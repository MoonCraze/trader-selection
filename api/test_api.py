"""
Test script for Trader Analysis API

Run this after starting the API server to verify all endpoints work correctly.
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")


def test_endpoint(name: str, endpoint: str, params: Dict = None) -> Any:
    """Test an API endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n[TEST] {name}")
        print(f"[URL] {url}")
        if params:
            print(f"[PARAMS] {params}")
        
        response = requests.get(url, params=params, timeout=TIMEOUT)
        
        print(f"[STATUS] {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] ✓")
            
            # Print summary of response
            if isinstance(data, dict):
                if 'count' in data:
                    print(f"[RESULT] Found {data['count']} items")
                if 'traders' in data and len(data['traders']) > 0:
                    print(f"[SAMPLE] First trader: {data['traders'][0].get('address', 'N/A')}")
            
            return data
        else:
            print(f"[ERROR] ✗ {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] ✗ Cannot connect to API. Is the server running?")
        return None
    except Exception as e:
        print(f"[ERROR] ✗ {str(e)}")
        return None


def main():
    """Run all API tests"""
    print_section("TRADER ANALYSIS API TEST SUITE")
    
    # Test 1: Root endpoint
    print_section("Test 1: Root Endpoint")
    test_endpoint("Root", "/")
    
    # Test 2: Health check
    print_section("Test 2: Health Check")
    health = test_endpoint("Health Check", "/health")
    if health and not health.get('data_available'):
        print("\n⚠️  WARNING: Analysis data not available. Run the analysis first!")
        print("   Command: cd examples && python run_hybrid_analysis.py")
        return
    
    # Test 3: Analysis summary
    print_section("Test 3: Analysis Summary")
    summary = test_endpoint("Summary", "/api/summary")
    
    # Test 4: Top traders
    print_section("Test 4: Top Traders")
    test_endpoint("Top 10 Traders", "/api/traders/top", {"limit": 10})
    test_endpoint("Top 5 with min score", "/api/traders/top", {"limit": 5, "min_score": 0.7})
    
    # Test 5: Personas
    print_section("Test 5: Personas")
    personas = test_endpoint("All Personas", "/api/personas")
    
    if personas and personas.get('personas'):
        # Test persona-specific endpoint with first persona
        first_persona = personas['personas'][0]['persona']
        test_endpoint(
            f"Top traders for {first_persona}", 
            f"/api/personas/{first_persona}/top",
            {"limit": 5}
        )
    
    # Test 6: High-confidence traders
    print_section("Test 6: High-Confidence Recommendations")
    test_endpoint("High-confidence traders", "/api/traders/high-confidence")
    
    # Test 7: Risk categories
    print_section("Test 7: Risk Categories")
    for risk in ['low', 'medium', 'medium-high']:
        test_endpoint(f"{risk.title()} risk traders", f"/api/traders/by-risk/{risk}", {"limit": 5})
    
    # Test 8: Search functionality
    print_section("Test 8: Search & Filter")
    test_endpoint(
        "Search validated traders", 
        "/api/traders/search",
        {"validated_only": True, "min_trades": 50, "limit": 10}
    )
    
    # Test 9: Statistics
    print_section("Test 9: Statistics")
    test_endpoint("Overview statistics", "/api/stats/overview")
    test_endpoint("Persona statistics", "/api/stats/personas")
    
    # Test 10: Specific trader lookup
    print_section("Test 10: Specific Trader Lookup")
    if summary:
        top_trader_address = summary.get('top_trader_address')
        if top_trader_address:
            test_endpoint(
                "Top trader details", 
                f"/api/traders/{top_trader_address}"
            )
    
    # Final summary
    print_section("TEST SUITE COMPLETE")
    print("\n✅ All tests completed!")
    print(f"\n📚 View interactive docs at: {BASE_URL}/docs")
    print(f"📖 View ReDoc at: {BASE_URL}/redoc")


if __name__ == "__main__":
    main()
