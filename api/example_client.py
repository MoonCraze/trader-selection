"""
Example client for Trader Analysis API

Demonstrates various ways to interact with the API and process results.
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
import json


class TraderAnalysisClient:
    """Client for interacting with Trader Analysis API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request to API"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health and data availability"""
        return self._get("/health")
    
    def get_summary(self) -> Dict:
        """Get analysis summary"""
        return self._get("/api/summary")
    
    def get_top_traders(self, limit: int = 50, min_score: Optional[float] = None) -> pd.DataFrame:
        """Get top traders as DataFrame"""
        params = {"limit": limit}
        if min_score:
            params["min_score"] = min_score
        
        data = self._get("/api/traders/top", params)
        return pd.DataFrame(data['traders'])
    
    def get_trader(self, address: str) -> Dict:
        """Get specific trader by address"""
        return self._get(f"/api/traders/{address}")
    
    def search_traders(
        self, 
        persona: Optional[str] = None,
        min_score: Optional[float] = None,
        min_trades: Optional[int] = None,
        min_win_rate: Optional[float] = None,
        validated_only: bool = False,
        limit: int = 100
    ) -> pd.DataFrame:
        """Search traders with filters"""
        params = {"limit": limit, "validated_only": validated_only}
        
        if persona:
            params["persona"] = persona
        if min_score:
            params["min_score"] = min_score
        if min_trades:
            params["min_trades"] = min_trades
        if min_win_rate:
            params["min_win_rate"] = min_win_rate
        
        data = self._get("/api/traders/search", params)
        return pd.DataFrame(data['traders'])
    
    def get_high_confidence_traders(
        self, 
        min_score: float = 0.6, 
        min_trades: int = 20
    ) -> pd.DataFrame:
        """Get high-confidence recommendations"""
        params = {"min_score": min_score, "min_trades": min_trades}
        data = self._get("/api/traders/high-confidence", params)
        return pd.DataFrame(data['traders'])
    
    def get_personas(self) -> pd.DataFrame:
        """Get all personas with statistics"""
        data = self._get("/api/personas")
        return pd.DataFrame(data['personas'])
    
    def get_persona_top_traders(self, persona: str, limit: int = 10) -> pd.DataFrame:
        """Get top traders for specific persona"""
        data = self._get(f"/api/personas/{persona}/top", {"limit": limit})
        return pd.DataFrame(data['traders'])
    
    def get_traders_by_risk(self, category: str, limit: int = 10) -> pd.DataFrame:
        """Get traders by risk category (low, medium, medium-high, high)"""
        data = self._get(f"/api/traders/by-risk/{category}", {"limit": limit})
        return pd.DataFrame(data['traders'])
    
    def get_overview_stats(self) -> Dict:
        """Get comprehensive overview statistics"""
        return self._get("/api/stats/overview")
    
    def get_persona_stats(self) -> pd.DataFrame:
        """Get detailed persona statistics"""
        data = self._get("/api/stats/personas")
        return pd.DataFrame(data['statistics'])


def example_basic_usage():
    """Example 1: Basic usage"""
    print("="*70)
    print("EXAMPLE 1: Basic Usage")
    print("="*70)
    
    # Initialize client
    client = TraderAnalysisClient()
    
    # Check health
    health = client.health_check()
    print(f"\nAPI Status: {health['status']}")
    print(f"Data Available: {health['data_available']}")
    
    # Get summary
    summary = client.get_summary()
    print(f"\nTotal Traders Analyzed: {summary['total_traders_analyzed']}")
    print(f"High Confidence Count: {summary['high_confidence_count']}")
    print(f"Top Trader: {summary['top_trader_address']}")
    
    # Get top 10 traders
    top_traders = client.get_top_traders(limit=10)
    print(f"\nTop 10 Traders:")
    print(top_traders[['address', 'persona', 'copy_trading_score', 'total_pnl', 'win_rate']])


def example_filtering():
    """Example 2: Advanced filtering"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Advanced Filtering")
    print("="*70)
    
    client = TraderAnalysisClient()
    
    # Find Elite Snipers with high win rate
    elite_traders = client.search_traders(
        persona="Elite Sniper",
        min_win_rate=70,
        min_trades=50,
        validated_only=True
    )
    
    print(f"\nFound {len(elite_traders)} Elite Snipers with 70+% win rate and 50+ trades")
    if len(elite_traders) > 0:
        print(elite_traders[['address', 'copy_trading_score', 'win_rate', 'total_trades']].head())


def example_high_confidence():
    """Example 3: High-confidence recommendations"""
    print("\n" + "="*70)
    print("EXAMPLE 3: High-Confidence Recommendations")
    print("="*70)
    
    client = TraderAnalysisClient()
    
    # Get high-confidence traders
    high_conf = client.get_high_confidence_traders(min_score=0.7, min_trades=30)
    
    print(f"\nFound {len(high_conf)} high-confidence traders (score >= 0.7, trades >= 30)")
    if len(high_conf) > 0:
        print("\nTop 5:")
        print(high_conf[['address', 'persona', 'copy_trading_score', 'roi', 'profit_factor']].head())


def example_risk_analysis():
    """Example 4: Risk-based selection"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Risk-Based Selection")
    print("="*70)
    
    client = TraderAnalysisClient()
    
    # Get traders by risk category
    for risk in ['low', 'medium', 'medium-high']:
        traders = client.get_traders_by_risk(risk, limit=5)
        
        print(f"\n{risk.upper()} Risk Traders (Top 5):")
        if len(traders) > 0:
            print(traders[['address', 'persona', 'copy_trading_score', 'total_pnl']].head())


def example_persona_analysis():
    """Example 5: Persona analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Persona Analysis")
    print("="*70)
    
    client = TraderAnalysisClient()
    
    # Get all personas
    personas = client.get_personas()
    
    print("\nAll Personas:")
    print(personas[['persona', 'trader_count', 'avg_copy_trading_score', 'avg_win_rate']])
    
    # Get top traders for each persona
    if len(personas) > 0:
        first_persona = personas.iloc[0]['persona']
        top_in_persona = client.get_persona_top_traders(first_persona, limit=5)
        
        print(f"\nTop 5 {first_persona} Traders:")
        print(top_in_persona[['address', 'copy_trading_score', 'total_pnl']])


def example_portfolio_building():
    """Example 6: Building a diversified portfolio"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Building a Diversified Portfolio")
    print("="*70)
    
    client = TraderAnalysisClient()
    
    portfolio = []
    
    # Strategy: Mix of risk levels with high-quality traders
    
    # 1. Get 2 low-risk traders
    low_risk = client.get_traders_by_risk('low', limit=2)
    portfolio.extend(low_risk.to_dict('records'))
    
    # 2. Get 3 medium-risk traders
    medium_risk = client.get_traders_by_risk('medium', limit=3)
    portfolio.extend(medium_risk.to_dict('records'))
    
    # 3. Get 1 medium-high risk trader for growth potential
    high_risk = client.get_traders_by_risk('medium-high', limit=1)
    portfolio.extend(high_risk.to_dict('records'))
    
    print(f"\nBuilt a diversified portfolio of {len(portfolio)} traders:")
    print("\nPortfolio Composition:")
    
    portfolio_df = pd.DataFrame(portfolio)
    print(portfolio_df[['address', 'persona', 'risk_category', 'copy_trading_score', 'roi']])
    
    # Portfolio statistics
    print(f"\nPortfolio Statistics:")
    print(f"  Average Copy-Trading Score: {portfolio_df['copy_trading_score'].mean():.3f}")
    print(f"  Average ROI: {portfolio_df['roi'].mean():.2f}%")
    print(f"  Average Win Rate: {portfolio_df['win_rate'].mean():.2f}%")


def example_statistics():
    """Example 7: Statistical analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Statistical Analysis")
    print("="*70)
    
    client = TraderAnalysisClient()
    
    # Get overview statistics
    stats = client.get_overview_stats()
    
    print("\nScore Statistics:")
    score_stats = stats['score_statistics']
    for key, value in score_stats.items():
        print(f"  {key.capitalize()}: {value:.3f}")
    
    print("\nPerformance Statistics:")
    perf_stats = stats['performance_statistics']
    for key, value in perf_stats.items():
        print(f"  {key}: {value:.2f}")
    
    # Get persona statistics
    persona_stats = client.get_persona_stats()
    print("\nPersona Statistics:")
    print(persona_stats)


def example_specific_trader():
    """Example 8: Detailed trader lookup"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Specific Trader Lookup")
    print("="*70)
    
    client = TraderAnalysisClient()
    
    # Get summary to find top trader
    summary = client.get_summary()
    top_address = summary['top_trader_address']
    
    # Get detailed information
    trader = client.get_trader(top_address)
    
    print(f"\nDetailed Information for Top Trader:")
    print(f"  Address: {trader['address']}")
    print(f"  Persona: {trader['persona']}")
    print(f"  Copy-Trading Score: {trader['copy_trading_score']:.3f}")
    print(f"  Quality Score: {trader['quality_score']:.3f}")
    print(f"  Total PNL: ${trader['total_pnl']:,.2f}")
    print(f"  ROI: {trader['roi']:.2f}%")
    print(f"  Win Rate: {trader['win_rate']:.2f}%")
    print(f"  Total Trades: {trader['total_trades']}")
    print(f"  Profit Factor: {trader['profit_factor']:.2f}")
    print(f"  Risk Category: {trader['risk_category']}")
    print(f"  Validation Passed: {trader['validation_passed']}")


def main():
    """Run all examples"""
    try:
        example_basic_usage()
        example_filtering()
        example_high_confidence()
        example_risk_analysis()
        example_persona_analysis()
        example_portfolio_building()
        example_statistics()
        example_specific_trader()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("   Make sure the API server is running:")
        print("   cd api && python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    main()
