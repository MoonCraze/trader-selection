"""
FastAPI Application for Trader Analysis Results

Exposes RESTful endpoints for accessing hybrid trader analysis results.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import pandas as pd
import json
from pathlib import Path as FilePath
from pydantic import BaseModel, Field

# Initialize FastAPI app
app = FastAPI(
    title="Trader Analysis API",
    description="API for accessing hybrid trader analysis and copy-trading recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OUTPUTS_DIR = FilePath(__file__).parent.parent / "outputs"

# Pydantic models for response validation
class TraderResponse(BaseModel):
    address: str
    persona: Optional[str] = None
    copy_trading_score: Optional[float] = None
    quality_score: Optional[float] = None
    total_pnl: Optional[float] = None
    realized_pnl: Optional[float] = None
    roi: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: Optional[int] = None
    total_volume: Optional[float] = None
    profit_factor: Optional[float] = None
    risk_category: Optional[str] = None
    validation_passed: Optional[bool] = None

class AnalysisSummary(BaseModel):
    total_traders_analyzed: int
    classified_traders: int
    unclassified_traders: int
    high_confidence_count: int
    personas_discovered: int
    avg_copy_trading_score: float
    top_trader_address: Optional[str]
    top_trader_score: float

class PersonaStats(BaseModel):
    persona: str
    trader_count: int
    avg_copy_trading_score: float
    avg_quality_score: float
    avg_total_pnl: float
    avg_win_rate: float

class HealthCheck(BaseModel):
    status: str
    message: str
    data_available: bool


# Helper functions
def load_complete_analysis() -> pd.DataFrame:
    """Load complete trader analysis data"""
    file_path = OUTPUTS_DIR / "complete_trader_analysis.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Analysis data not found. Please run the analysis first.")
    return pd.read_csv(file_path)


def load_summary() -> dict:
    """Load analysis summary"""
    file_path = OUTPUTS_DIR / "analysis_summary_hybrid.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Summary not found. Please run the analysis first.")
    with open(file_path, 'r') as f:
        return json.load(f)


def load_persona_file(persona: str, top_n: int = 10) -> pd.DataFrame:
    """Load persona-specific ranking file"""
    filename = f"top_{top_n}_{persona.replace(' ', '_')}.csv"
    file_path = OUTPUTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Persona file not found: {filename}")
    return pd.read_csv(file_path)


def dataframe_to_dict_list(df: pd.DataFrame) -> List[Dict]:
    """Convert DataFrame to list of dictionaries with NaN handling"""
    return df.replace({pd.NA: None, float('nan'): None}).to_dict('records')


# API Endpoints

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Trader Analysis API",
        "version": "1.0.0",
        "description": "API for accessing hybrid trader analysis results",
        "endpoints": {
            "health": "/health",
            "summary": "/api/summary",
            "top_traders": "/api/traders/top",
            "trader_by_address": "/api/traders/{address}",
            "personas": "/api/personas",
            "high_confidence": "/api/traders/high-confidence",
            "risk_categories": "/api/traders/by-risk/{category}"
        }
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    data_available = (OUTPUTS_DIR / "complete_trader_analysis.csv").exists()
    return {
        "status": "healthy" if data_available else "warning",
        "message": "API is running" if data_available else "API is running but analysis data not found",
        "data_available": data_available
    }


@app.get("/api/summary", response_model=AnalysisSummary, tags=["Analysis"])
async def get_analysis_summary():
    """
    Get overall analysis summary
    
    Returns high-level statistics about the analysis including:
    - Total traders analyzed
    - Classification statistics
    - Average scores
    - Top trader information
    """
    summary = load_summary()
    return summary


@app.get("/api/traders/top", tags=["Traders"])
async def get_top_traders(
    limit: int = Query(50, ge=1, le=500, description="Number of top traders to return"),
    min_score: Optional[float] = Query(None, ge=0, le=1, description="Minimum copy trading score")
):
    """
    Get top traders by copy-trading score
    
    Parameters:
    - limit: Number of traders to return (default: 50, max: 500)
    - min_score: Optional minimum copy trading score filter
    """
    df = load_complete_analysis()
    
    # Filter by score if provided
    if min_score is not None:
        df = df[df['copy_trading_score'] >= min_score]
    
    # Sort and limit
    top_traders = df.nlargest(limit, 'copy_trading_score')
    
    return {
        "count": len(top_traders),
        "traders": dataframe_to_dict_list(top_traders)
    }


@app.get("/api/traders/{address}", tags=["Traders"])
async def get_trader_by_address(
    address: str = Path(..., description="Wallet address of the trader")
):
    """
    Get detailed information for a specific trader by wallet address
    """
    df = load_complete_analysis()
    trader = df[df['address'] == address]
    
    if len(trader) == 0:
        raise HTTPException(status_code=404, detail=f"Trader with address {address} not found")
    
    return dataframe_to_dict_list(trader)[0]


@app.get("/api/traders/search", tags=["Traders"])
async def search_traders(
    persona: Optional[str] = Query(None, description="Filter by persona type"),
    min_score: Optional[float] = Query(None, ge=0, le=1, description="Minimum copy trading score"),
    min_trades: Optional[int] = Query(None, ge=0, description="Minimum number of trades"),
    min_win_rate: Optional[float] = Query(None, ge=0, le=100, description="Minimum win rate percentage"),
    validated_only: bool = Query(False, description="Return only validated traders"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return")
):
    """
    Search and filter traders by multiple criteria
    """
    df = load_complete_analysis()
    
    # Apply filters
    if persona:
        df = df[df['persona'] == persona]
    
    if min_score is not None:
        df = df[df['copy_trading_score'] >= min_score]
    
    if min_trades is not None:
        df = df[df['total_trades'] >= min_trades]
    
    if min_win_rate is not None:
        df = df[df['win_rate'] >= min_win_rate]
    
    if validated_only:
        df = df[df['validation_passed'] == True]
    
    # Sort by score and limit
    df = df.nlargest(limit, 'copy_trading_score')
    
    return {
        "count": len(df),
        "filters": {
            "persona": persona,
            "min_score": min_score,
            "min_trades": min_trades,
            "min_win_rate": min_win_rate,
            "validated_only": validated_only
        },
        "traders": dataframe_to_dict_list(df)
    }


@app.get("/api/personas", tags=["Personas"])
async def get_all_personas():
    """
    Get list of all discovered personas with statistics
    """
    df = load_complete_analysis()
    
    # Calculate statistics per persona
    persona_stats = df[df['persona'] != 'Unclassified'].groupby('persona').agg({
        'address': 'count',
        'copy_trading_score': 'mean',
        'quality_score': 'mean',
        'total_pnl': 'mean',
        'win_rate': 'mean'
    }).reset_index()
    
    persona_stats.columns = ['persona', 'trader_count', 'avg_copy_trading_score', 
                             'avg_quality_score', 'avg_total_pnl', 'avg_win_rate']
    
    return {
        "count": len(persona_stats),
        "personas": dataframe_to_dict_list(persona_stats)
    }


@app.get("/api/personas/{persona_name}/top", tags=["Personas"])
async def get_top_traders_by_persona(
    persona_name: str = Path(..., description="Name of the persona"),
    limit: int = Query(10, ge=1, le=100, description="Number of top traders to return")
):
    """
    Get top traders for a specific persona
    """
    df = load_complete_analysis()
    
    # Filter by persona
    persona_traders = df[df['persona'] == persona_name]
    
    if len(persona_traders) == 0:
        raise HTTPException(status_code=404, detail=f"Persona '{persona_name}' not found")
    
    # Get top traders
    top_traders = persona_traders.nlargest(limit, 'copy_trading_score')
    
    return {
        "persona": persona_name,
        "count": len(top_traders),
        "traders": dataframe_to_dict_list(top_traders)
    }


@app.get("/api/traders/high-confidence", tags=["Traders"])
async def get_high_confidence_traders(
    min_score: float = Query(0.6, ge=0, le=1, description="Minimum copy trading score"),
    min_trades: int = Query(20, ge=0, description="Minimum number of trades")
):
    """
    Get high-confidence copy-trading recommendations
    
    Returns traders that meet high-quality criteria:
    - High copy-trading score
    - Passed validation
    - Sufficient trading history
    """
    file_path = OUTPUTS_DIR / "high_confidence_recommendations.csv"
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        
        # Apply additional filters if provided
        df = df[(df['copy_trading_score'] >= min_score) & (df['total_trades'] >= min_trades)]
        
        return {
            "count": len(df),
            "criteria": {
                "min_score": min_score,
                "min_trades": min_trades,
                "validation_required": True
            },
            "traders": dataframe_to_dict_list(df)
        }
    else:
        # Fallback to calculating from complete data
        df = load_complete_analysis()
        
        high_confidence = df[
            (df['persona'] != 'Unclassified') &
            (df['copy_trading_score'] >= min_score) &
            (df['validation_passed'] == True) &
            (df['total_trades'] >= min_trades)
        ].sort_values('copy_trading_score', ascending=False)
        
        return {
            "count": len(high_confidence),
            "criteria": {
                "min_score": min_score,
                "min_trades": min_trades,
                "validation_required": True
            },
            "traders": dataframe_to_dict_list(high_confidence)
        }


@app.get("/api/traders/by-risk/{category}", tags=["Risk"])
async def get_traders_by_risk_category(
    category: str = Path(..., description="Risk category: low, medium, medium-high, or high"),
    limit: int = Query(10, ge=1, le=100, description="Number of traders to return")
):
    """
    Get top traders by risk category
    
    Risk categories:
    - low: Elite Sniper traders (precision, low risk)
    - medium: Consistent Performer, Scalper traders
    - medium-high: Whale, Momentum Trader
    - high: Risk-Taker and other high-risk traders
    """
    # Normalize category name
    category_map = {
        'low': 'Low Risk',
        'medium': 'Medium Risk',
        'medium-high': 'Medium-High Risk',
        'high': 'High Risk'
    }
    
    if category.lower() not in category_map:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid risk category. Must be one of: {', '.join(category_map.keys())}"
        )
    
    risk_category = category_map[category.lower()]
    
    # Try to load from file first
    filename = f"top_10_{risk_category.replace(' ', '_').lower()}.csv"
    file_path = OUTPUTS_DIR / filename
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        df = df.head(limit)
    else:
        # Fallback to calculating from complete data
        df = load_complete_analysis()
        
        if 'risk_category' in df.columns:
            df = df[df['risk_category'] == risk_category]
            df = df.nlargest(limit, 'copy_trading_score')
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Risk category data not available. Please run the analysis with risk categorization."
            )
    
    return {
        "risk_category": risk_category,
        "count": len(df),
        "traders": dataframe_to_dict_list(df)
    }


@app.get("/api/stats/overview", tags=["Statistics"])
async def get_overview_statistics():
    """
    Get comprehensive overview statistics
    """
    df = load_complete_analysis()
    summary = load_summary()
    
    # Calculate additional statistics
    classified = df[df['persona'] != 'Unclassified']
    
    persona_distribution = classified.groupby('persona').size().to_dict()
    
    stats = {
        "summary": summary,
        "persona_distribution": persona_distribution,
        "score_statistics": {
            "mean": float(classified['copy_trading_score'].mean()),
            "median": float(classified['copy_trading_score'].median()),
            "std": float(classified['copy_trading_score'].std()),
            "min": float(classified['copy_trading_score'].min()),
            "max": float(classified['copy_trading_score'].max())
        },
        "performance_statistics": {
            "avg_pnl": float(classified['total_pnl'].mean()),
            "avg_roi": float(classified['roi'].mean()),
            "avg_win_rate": float(classified['win_rate'].mean()),
            "avg_trades": float(classified['total_trades'].mean())
        }
    }
    
    return stats


@app.get("/api/stats/personas", tags=["Statistics"])
async def get_persona_statistics():
    """
    Get detailed statistics for each persona
    """
    file_path = OUTPUTS_DIR / "persona_quality_statistics.csv"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Persona statistics not found")
    
    df = pd.read_csv(file_path)
    return {
        "count": len(df),
        "statistics": dataframe_to_dict_list(df)
    }


@app.get("/api/exports/all-traders", tags=["Export"])
async def export_all_traders():
    """
    Export complete trader analysis data (WARNING: Large response)
    """
    df = load_complete_analysis()
    
    return {
        "count": len(df),
        "warning": "This endpoint returns all trader data and may be large",
        "traders": dataframe_to_dict_list(df)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
