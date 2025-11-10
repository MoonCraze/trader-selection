"""
FastAPI Application for Trader Analysis with Database Integration

Exposes RESTful endpoints for real-time trader analysis from MySQL database.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import FastAPI, HTTPException, Query, Path, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
import json
from pathlib import Path as FilePath
from pydantic import BaseModel, Field
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database service
from db_service import get_db_service

# Import analysis modules
from trader_analysis.hybrid_persona_system import HybridPersonaSystem
from trader_analysis.feature_engineering import FeatureEngineer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Trader Analysis API",
    description="Real-time trader analysis and copy-trading recommendations from database",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global cache for analysis results
analysis_cache = {
    'data': None,
    'timestamp': None,
    'is_processing': False
}

# Pydantic models for response validation
class TraderResponse(BaseModel):
    wallet_address: str
    token_address: Optional[str] = None
    gross_profit: Optional[float] = None
    realized_profit: Optional[float] = None
    realized_profit_percent: Optional[float] = None
    unrealized_profit: Optional[float] = None
    unrealized_profit_percent: Optional[float] = None
    win_rate: Optional[float] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    trade_volume: Optional[float] = None
    trades: Optional[int] = None
    avg_trade_size: Optional[float] = None
    is_bot: Optional[bool] = None
    persona: Optional[str] = None
    copy_trading_score: Optional[float] = None
    quality_score: Optional[float] = None
    risk_category: Optional[str] = None

class AnalysisSummary(BaseModel):
    total_traders: int
    non_bot_traders: int
    bot_traders: int
    avg_win_rate: float
    avg_trades: float
    avg_volume: float
    avg_profit: float
    total_profit: float
    total_volume: float
    analysis_available: bool
    last_analysis: Optional[str] = None

class PersonaStats(BaseModel):
    persona: str
    trader_count: int
    avg_copy_trading_score: float
    avg_quality_score: float
    avg_realized_profit: float
    avg_win_rate: float

class HealthCheck(BaseModel):
    status: str
    message: str
    database_connected: bool
    analysis_available: bool


# Helper functions
def prepare_trader_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare comprehensive feature set for trader analysis.
    Maps database columns to expected feature names.
    """
    logger.info(f"Preparing features for {len(df)} traders")
    
    # Filter bots
    if 'is_bot' in df.columns:
        original_count = len(df)
        df = df[df['is_bot'] == 0].copy()
        logger.info(f"Filtered {original_count - len(df)} bots, {len(df)} real traders remain")
    
    # Map database columns to expected feature names
    column_mapping = {
        'wallet_address': 'address',
        'gross_profit': 'total_pnl',
        'realized_profit': 'realized_pnl',
        'realized_profit_percent': 'roi',
        'win_rate': 'win_rate',
        'trade_volume': 'total_volume',
        'trades': 'total_trades',
        'avg_trade_size': 'avg_trade_size',
        'wins': 'wins',
        'losses': 'losses'
    }
    
    # Rename columns
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df[new_col] = df[old_col]
    
    # Calculate additional features
    df['profit_factor'] = np.where(
        df['losses'] > 0,
        df['wins'] / df['losses'],
        df['wins']
    )
    
    # Calculate loss_rate
    df['loss_rate'] = 100 - df['win_rate']
    
    # Calculate average profit per trade
    df['avg_profit'] = np.where(
        df['total_trades'] > 0,
        df['realized_pnl'] / df['total_trades'],
        0
    )
    
    # Handle missing values
    df = df.fillna(0)
    
    # Replace infinities
    df = df.replace([np.inf, -np.inf], 0)
    
    logger.info(f"Feature preparation complete: {len(df)} traders with {len(df.columns)} features")
    
    return df


def run_hybrid_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run hybrid persona classification and scoring on trader data.
    """
    logger.info("Starting hybrid analysis...")
    
    # Prepare features
    features_df = prepare_trader_features(df)
    
    if len(features_df) < 10:
        logger.warning(f"Only {len(features_df)} traders available. Need at least 10 for clustering.")
        return features_df
    
    # Initialize hybrid system
    hybrid_system = HybridPersonaSystem(random_state=42)
    
    # Run classification
    logger.info("Running hybrid classification...")
    results_df = hybrid_system.classify_traders(features_df)
    
    # Add classification results to features dataframe
    # The classify_traders method returns a dataframe with additional columns
    features_df = results_df.copy()
    
    # Rename columns to match our API expectations
    if 'persona_confidence' in features_df.columns:
        features_df['classification_confidence'] = features_df['persona_confidence']
    
    # Add copy trading score (weighted quality score)
    features_df['copy_trading_score'] = features_df['quality_score'] * 100  # Scale to 0-100
    
    # Add risk category based on various factors
    features_df['risk_category'] = features_df.apply(lambda row: classify_risk(row), axis=1)
    
    # Add classification method (all are domain-based in this system)
    features_df['classification_method'] = 'domain_rules'
    
    logger.info(f"Hybrid analysis complete. Classified {len(features_df)} traders")
    
    return features_df


def classify_risk(row: pd.Series) -> str:
    """Classify trader risk level"""
    if row['win_rate'] >= 60 and row['profit_factor'] >= 2.0:
        return 'low'
    elif row['win_rate'] >= 45 and row['profit_factor'] >= 1.5:
        return 'medium'
    elif row['win_rate'] >= 35:
        return 'medium-high'
    else:
        return 'high'


def get_or_run_analysis(force_refresh: bool = False) -> pd.DataFrame:
    """
    Get cached analysis or run new analysis if needed.
    """
    global analysis_cache
    
    # Check if we need to refresh
    if force_refresh or analysis_cache['data'] is None:
        if analysis_cache['is_processing']:
            raise HTTPException(status_code=503, detail="Analysis is already in progress")
        
        try:
            analysis_cache['is_processing'] = True
            logger.info("Running new analysis from database...")
            
            # Get data from database
            db_service = get_db_service()
            df = db_service.get_all_traders(exclude_bots=True)
            
            # Run analysis
            analyzed_df = run_hybrid_analysis(df)
            
            # Cache results
            analysis_cache['data'] = analyzed_df
            analysis_cache['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Analysis complete and cached at {analysis_cache['timestamp']}")
            
        finally:
            analysis_cache['is_processing'] = False
    
    return analysis_cache['data']


# API Endpoints

@app.get("/", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        db_service = get_db_service()
        database_connected = True
        analysis_available = analysis_cache['data'] is not None
        
        return {
            "status": "healthy",
            "message": "Trader Analysis API is running",
            "database_connected": database_connected,
            "analysis_available": analysis_available
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
            "database_connected": False,
            "analysis_available": False
        }


@app.get("/api/v1/stats", response_model=AnalysisSummary)
async def get_database_stats():
    """Get overall database statistics"""
    try:
        db_service = get_db_service()
        stats = db_service.get_database_stats()
        
        stats['analysis_available'] = analysis_cache['data'] is not None
        stats['last_analysis'] = analysis_cache['timestamp']
        
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/traders", response_model=List[TraderResponse])
async def get_all_traders(
    exclude_bots: bool = Query(True, description="Exclude bot accounts"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of traders to return"),
    offset: int = Query(0, ge=0, description="Number of traders to skip")
):
    """Get all traders from database"""
    try:
        db_service = get_db_service()
        df = db_service.get_all_traders(exclude_bots=exclude_bots)
        
        # Apply pagination
        df = df.iloc[offset:offset+limit]
        
        # Convert to dict records
        traders = df.to_dict('records')
        
        return traders
    except Exception as e:
        logger.error(f"Error getting traders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/traders/{wallet_address}", response_model=TraderResponse)
async def get_trader_by_address(
    wallet_address: str = Path(..., description="Trader's wallet address")
):
    """Get specific trader by wallet address"""
    try:
        db_service = get_db_service()
        trader = db_service.get_trader_by_address(wallet_address)
        
        if trader is None:
            raise HTTPException(status_code=404, detail=f"Trader {wallet_address} not found")
        
        return trader.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trader: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/traders/top/ranked")
async def get_top_traders(
    limit: int = Query(50, ge=1, le=500, description="Number of top traders to return"),
    sort_by: str = Query("realized_profit", description="Metric to sort by"),
    exclude_bots: bool = Query(True, description="Exclude bot accounts")
):
    """Get top traders sorted by specified metric"""
    try:
        db_service = get_db_service()
        df = db_service.get_top_traders(limit=limit, sort_by=sort_by, exclude_bots=exclude_bots)
        
        traders = df.to_dict('records')
        return traders
    except Exception as e:
        logger.error(f"Error getting top traders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/traders/filter")
async def filter_traders(
    min_win_rate: Optional[float] = Query(None, ge=0, le=100, description="Minimum win rate %"),
    min_trades: Optional[int] = Query(None, ge=0, description="Minimum number of trades"),
    min_volume: Optional[float] = Query(None, ge=0, description="Minimum trade volume"),
    min_profit: Optional[float] = Query(None, description="Minimum realized profit"),
    exclude_bots: bool = Query(True, description="Exclude bot accounts"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results")
):
    """Filter traders by various criteria"""
    try:
        db_service = get_db_service()
        df = db_service.get_traders_by_filter(
            min_win_rate=min_win_rate,
            min_trades=min_trades,
            min_volume=min_volume,
            min_profit=min_profit,
            exclude_bots=exclude_bots
        )
        
        # Apply limit
        df = df.head(limit)
        
        traders = df.to_dict('records')
        return traders
    except Exception as e:
        logger.error(f"Error filtering traders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analysis/run")
async def trigger_analysis(background_tasks: BackgroundTasks):
    """Trigger a new hybrid analysis run"""
    try:
        # Run analysis in foreground (can be moved to background if needed)
        df = get_or_run_analysis(force_refresh=True)
        
        return {
            "status": "success",
            "message": f"Analysis completed for {len(df)} traders",
            "timestamp": analysis_cache['timestamp'],
            "traders_analyzed": len(df)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analysis/results")
async def get_analysis_results(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    persona: Optional[str] = Query(None, description="Filter by persona"),
    min_copy_trading_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum copy trading score")
):
    """Get hybrid analysis results with optional filtering"""
    try:
        df = get_or_run_analysis()
        
        if df is None:
            raise HTTPException(status_code=404, detail="No analysis results available. Run analysis first.")
        
        # Apply filters
        filtered_df = df.copy()
        
        if persona:
            filtered_df = filtered_df[filtered_df['persona'] == persona]
        
        if min_copy_trading_score is not None:
            filtered_df = filtered_df[filtered_df['copy_trading_score'] >= min_copy_trading_score]
        
        # Sort by copy trading score
        filtered_df = filtered_df.sort_values('copy_trading_score', ascending=False)
        
        # Apply pagination
        filtered_df = filtered_df.iloc[offset:offset+limit]
        
        # Convert to records
        results = filtered_df.to_dict('records')
        
        return {
            "total_results": len(df),
            "filtered_results": len(filtered_df),
            "results": results,
            "analysis_timestamp": analysis_cache['timestamp']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analysis/personas")
async def get_persona_statistics():
    """Get statistics for each discovered persona"""
    try:
        df = get_or_run_analysis()
        
        if df is None:
            raise HTTPException(status_code=404, detail="No analysis results available. Run analysis first.")
        
        # Filter to only classified traders
        classified_df = df[df['persona'].notna() & (df['persona'] != 'Unclassified')]
        
        # Group by persona
        persona_stats = []
        for persona in classified_df['persona'].unique():
            persona_df = classified_df[classified_df['persona'] == persona]
            
            stats = {
                'persona': persona,
                'trader_count': len(persona_df),
                'avg_copy_trading_score': float(persona_df['copy_trading_score'].mean()),
                'avg_quality_score': float(persona_df['quality_score'].mean()),
                'avg_realized_profit': float(persona_df['realized_pnl'].mean()),
                'avg_win_rate': float(persona_df['win_rate'].mean()),
                'total_volume': float(persona_df['total_volume'].sum())
            }
            persona_stats.append(stats)
        
        # Sort by trader count
        persona_stats = sorted(persona_stats, key=lambda x: x['trader_count'], reverse=True)
        
        return {
            "total_personas": len(persona_stats),
            "total_classified_traders": len(classified_df),
            "personas": persona_stats,
            "analysis_timestamp": analysis_cache['timestamp']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting persona statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analysis/recommendations")
async def get_copy_trading_recommendations(
    min_score: float = Query(70, ge=0, le=100, description="Minimum copy trading score"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of recommendations")
):
    """Get top copy trading recommendations"""
    try:
        df = get_or_run_analysis()
        
        if df is None:
            raise HTTPException(status_code=404, detail="No analysis results available. Run analysis first.")
        
        # Filter by minimum score and validation
        recommendations = df[
            (df['copy_trading_score'] >= min_score) & 
            (df['validation_passed'] == True)
        ].copy()
        
        # Sort by copy trading score
        recommendations = recommendations.sort_values('copy_trading_score', ascending=False)
        
        # Limit results
        recommendations = recommendations.head(limit)
        
        # Select relevant columns
        columns = [
            'address', 'persona', 'copy_trading_score', 'quality_score',
            'realized_pnl', 'roi', 'win_rate', 'total_trades', 'total_volume',
            'risk_category', 'profit_factor'
        ]
        
        recommendations = recommendations[columns]
        
        return {
            "total_recommendations": len(recommendations),
            "min_score_threshold": min_score,
            "recommendations": recommendations.to_dict('records'),
            "analysis_timestamp": analysis_cache['timestamp']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    logger.info("Starting Trader Analysis API...")
    try:
        db_service = get_db_service()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("Shutting down Trader Analysis API...")
    try:
        db_service = get_db_service()
        db_service.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


if __name__ == "__main__":
    import uvicorn
    
    # Get API configuration from environment variables
    api_host = os.getenv('API_HOST', '0.0.0.0')
    api_port = int(os.getenv('API_PORT', '8000'))
    
    logger.info(f"Starting API server on {api_host}:{api_port}")
    uvicorn.run(app, host=api_host, port=api_port)
