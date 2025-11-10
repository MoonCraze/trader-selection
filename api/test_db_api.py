"""
Simple Test Client for Database API

Quick test of all main endpoints.
"""

import requests

BASE_URL = "http://localhost:8000"

print("Testing Trader Analysis API\n")

# 1. Health
print("1. Health Check:")
r = requests.get(f"{BASE_URL}/")
print(f"   {r.json()}\n")

# 2. Stats
print("2. Database Stats:")
r = requests.get(f"{BASE_URL}/api/v1/stats")
stats = r.json()
print(f"   Total: {stats['total_traders']}, Non-Bot: {stats['non_bot_traders']}\n")

# 3. Top Traders
print("3. Top 3 Traders:")
r = requests.get(f"{BASE_URL}/api/v1/traders/top/ranked?limit=3")
for t in r.json()[:3]:
    print(f"   {t['wallet_address']}: ${t['realized_profit']:.2f}")
print()

# 4. Run Analysis
print("4. Running Analysis...")
r = requests.post(f"{BASE_URL}/api/v1/analysis/run")
print(f"   {r.json()['message']}\n")

# 5. Personas
print("5. Persona Stats:")
r = requests.get(f"{BASE_URL}/api/v1/analysis/personas")
personas = r.json()
for p in personas['personas'][:3]:
    print(f"   {p['persona']}: {p['trader_count']} traders, score: {p['avg_copy_trading_score']:.2f}")
print()

# 6. Recommendations
print("6. Top 3 Recommendations:")
r = requests.get(f"{BASE_URL}/api/v1/analysis/recommendations?min_score=50&limit=3")
for rec in r.json()['recommendations']:
    print(f"   {rec['address'][:20]}... - {rec['persona']} - Score: {rec['copy_trading_score']:.2f}")

print("\n✓ All tests passed!")
