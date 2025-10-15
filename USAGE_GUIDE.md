# How to Use the Hybrid Persona System

This guide shows you how to use the Hybrid Persona Classification System to analyze traders and identify the best ones to follow for copy-trading.

---

## Quick Start (3 Steps)

### 1. Prepare Your Data

Place your trader data CSV in the `data/` directory. Required columns:
- `address` - Unique trader identifier
- `total_pnl` - Total profit/loss
- `roi` - Return on investment (%)
- `win_rate` - Win rate (%)
- `total_trades` - Number of trades
- Additional columns will be used if available

### 2. Run the Analysis

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run hybrid analysis
python examples/run_hybrid_analysis.py
```

That's it! The system will:
- Load and clean your data
- Engineer features
- Classify traders into personas
- Calculate copy-trading scores
- Generate rankings
- Create visualizations
- Save all outputs to `outputs/`

### 3. Review Results

Check these files in `outputs/`:
- `top_50_traders_overall.csv` - Start here! Top 50 traders ranked
- `high_confidence_recommendations.csv` - 17 best traders to copy
- `comprehensive_dashboard.png` - Visual overview
- Persona-specific files: `top_10_Elite_Sniper.csv`, etc.

---

## Understanding the Output

### Copy-Trading Score (0-1 Scale)

The main metric you should use for ranking. Higher = better.

**Score Components:**
- **0.8+**: Elite traders - Copy immediately
- **0.6-0.8**: High quality - Strongly recommended
- **0.4-0.6**: Good quality - Consider for diversification
- **0.2-0.4**: Average - Monitor before copying
- **<0.2**: Below average - Avoid

**Example:**
```
Trader: 12ezPHMd...6K9e
Persona: Whale
Copy-Trading Score: 0.814  ← This is excellent!
Win Rate: 66.67%
Total PnL: $4,786,997
```

### Personas Explained

| Persona | Description | Best For | Risk Level |
|---------|-------------|----------|------------|
| **Elite Sniper** | High win rate, selective | Conservative investors | Low |
| **Consistent Performer** | Stable returns | Balanced portfolios | Medium |
| **Scalper** | High frequency, good win rate | Active copy-trading | Medium |
| **Whale** | Massive volume | Aggressive growth | Medium-High |
| **Momentum Trader** | Trend following | Volatile markets | Medium-High |
| **Risk-Taker** | Large positions | High risk tolerance | High |
| **Developing Trader** | Improving metrics | Long-term potential | Variable |

### Quality Score vs Copy-Trading Score

- **Quality Score (0-1)**: How well the trader fits their persona's ideal profile
- **Copy-Trading Score (0-1)**: Overall recommendation for copy-trading (uses quality + persona multipliers)

Both are useful, but **Copy-Trading Score is the final ranking metric**.

---

## Common Use Cases

### Use Case 1: "I want the safest traders to copy"

```python
# Option A: Use the CSV files
import pandas as pd

# Load high-confidence recommendations
safe_traders = pd.read_csv('outputs/high_confidence_recommendations.csv')

# Filter for Elite Snipers only
elite = safe_traders[safe_traders['persona'] == 'Elite Sniper']

# Get top 5
top_5_safe = elite.nlargest(5, 'copy_trading_score')
print(top_5_safe[['address', 'copy_trading_score', 'win_rate', 'total_pnl']])
```

**Output File**: `outputs/top_10_low_risk.csv` (already created for you!)

### Use Case 2: "I want maximum profit potential"

```python
# Load overall top 50
aggressive = pd.read_csv('outputs/top_50_traders_overall.csv')

# Filter for high PnL
high_earners = aggressive[aggressive['total_pnl'] > 500000]

# Get top 10
top_10_profit = high_earners.nlargest(10, 'copy_trading_score')
```

**Recommended Personas**: Whale, Risk-Taker

### Use Case 3: "I want a balanced portfolio"

```python
# Mix of personas
portfolio = []

# 3 Elite Snipers (safety)
elites = pd.read_csv('outputs/top_10_Elite_Sniper.csv').head(3)
portfolio.append(elites)

# 3 Scalpers (frequency)
scalpers = pd.read_csv('outputs/top_10_Scalper.csv').head(3)
portfolio.append(scalpers)

# 2 Whales (growth)
whales = pd.read_csv('outputs/top_10_Whale.csv').head(2)
portfolio.append(whales)

# Combine
balanced_portfolio = pd.concat(portfolio)
```

### Use Case 4: "I want to analyze a specific trader"

```python
# Load complete analysis
all_traders = pd.read_csv('outputs/complete_trader_analysis.csv')

# Find trader by address
trader = all_traders[all_traders['address'] == '12ezPHMd...6K9e']

print(f"Persona: {trader['persona'].values[0]}")
print(f"Copy-Trading Score: {trader['copy_trading_score'].values[0]:.3f}")
print(f"Quality Score: {trader['quality_score'].values[0]:.3f}")
print(f"Win Rate: {trader['win_rate'].values[0]:.2f}%")
print(f"Total PnL: ${trader['total_pnl'].values[0]:,.2f}")
```

---

## Customizing the Analysis

### Adjust Scoring Weights

Edit `src/trader_analysis/hybrid_persona_system.py`:

```python
# Line ~600 in HybridPersonaSystem.calculate_copy_trading_scores()
def calculate_copy_trading_scores(self, features_df):
    # Change these weights (must sum to 1.0)
    profitability_weight = 0.40  # Default: 40%
    consistency_weight = 0.30    # Default: 30%
    risk_weight = 0.20           # Default: 20%
    activity_weight = 0.10       # Default: 10%
```

**Example**: Want to prioritize consistency over profitability?
```python
profitability_weight = 0.25  # Reduced from 0.40
consistency_weight = 0.45    # Increased from 0.30
risk_weight = 0.20           # Same
activity_weight = 0.10       # Same
```

### Change Persona Validation Rules

Edit `src/trader_analysis/hybrid_persona_system.py`:

```python
# Line ~100 in PersonaValidator class
def validate_elite_sniper(self, row):
    return (
        row['win_rate'] >= 0.60 and      # Increase to 0.70 for stricter
        row['total_trades'] <= 100 and   # Increase to 150 for more traders
        row['roi'] > 0 and
        row['total_pnl'] > 0 and
        row['profit_factor'] >= 1.5      # Increase to 2.0 for higher quality
    )
```

### Filter by Minimum Trades

```python
# When loading results
traders = pd.read_csv('outputs/top_50_traders_overall.csv')

# Only traders with 50+ trades
experienced = traders[traders['total_trades'] >= 50]
```

---

## Interpreting Visualizations

### 1. Comprehensive Dashboard (`comprehensive_dashboard.png`)

**What to Look For:**
- **Top-left**: How many traders in each persona?
- **Top-middle**: Which personas have highest quality?
- **Middle row**: Who are the top 20 traders? (Copy these!)
- **Bottom-left**: Are scores well-distributed by persona?
- **Bottom-right**: Is quality score correlated with performance?

**Good Signs:**
✅ Top traders span multiple personas (diversification)  
✅ Quality scores cluster high (>0.5)  
✅ Positive correlation in scatter plot  

**Red Flags:**
❌ All top traders from one persona (risky)  
❌ Wide score ranges within personas (inconsistency)  
❌ No correlation in scatter (scoring issues)

### 2. Copy-Trading Rankings (`follow_worthiness_rankings.png`)

**Panel 1 (Top-left)**: Top 30 traders bar chart
- **Use**: Quick visual ranking
- **Colors**: Each persona has different color
- **Action**: Copy top 5-10 traders

**Panel 2 (Top-right)**: Score component breakdown
- **Use**: Understand why traders ranked high
- **Colors**: Green=profitability, Blue=consistency, Orange=risk, Red=activity
- **Action**: Prefer balanced bars (all 4 components contributing)

**Panel 3 (Bottom-left)**: Persona comparison
- **Use**: Which personas perform best?
- **Dark bars**: Top traders in persona
- **Light bars**: Average traders in persona
- **Action**: Focus on personas with large gap

**Panel 4 (Bottom-right)**: Score distributions
- **Use**: Variability within personas
- **Tight boxes**: Consistent persona quality
- **Wide boxes**: High variability
- **Action**: Prefer personas with tight, high boxes

### 3. Persona Radar Charts (`persona_characteristics_radar.png`)

Each persona has a pentagon showing 5 metrics (0-1 scale):
- **win_rate**: Closer to edge = higher win rate
- **roi**: Closer to edge = better returns
- **total_trades**: Closer to edge = more active
- **quality_score**: Closer to edge = better fit to persona
- **copy_trading_score**: Closer to edge = better overall

**Reading Example:**
```
Elite Sniper radar:
- win_rate: 0.92 (near edge) ← Excellent!
- roi: 0.75 (far from edge) ← Moderate
- total_trades: 0.15 (close to center) ← Low volume
- quality_score: 0.55 (mid-range)
- copy_trading_score: 0.53 (mid-range)
```
**Interpretation**: Great win rate but low volume. Good for conservative copy-trading.

---

## Advanced Usage

### Run Analysis Programmatically

```python
from src.trader_analysis.hybrid_persona_system import HybridPersonaSystem
from src.trader_analysis.hybrid_visualizer import HybridVisualizer

# Initialize system
system = HybridPersonaSystem()

# Run classification
data_path = 'data/traders_202510140811.csv'
features = system.classify_and_rank(data_path)

# Generate visualizations
viz = HybridVisualizer('outputs')
viz.create_comprehensive_dashboard(features, save_path='outputs/dashboard.png')

# Get top 10 overall
top_10 = features.nlargest(10, 'copy_trading_score')
print(top_10[['address', 'persona', 'copy_trading_score']])
```

### Filter High-Quality Traders

```python
# Custom filtering
high_quality = features[
    (features['copy_trading_score'] >= 0.6) &
    (features['validation_passed'] == True) &
    (features['total_trades'] >= 20) &
    (features['win_rate'] >= 60)
]

print(f"Found {len(high_quality)} high-quality traders")
```

### Compare Two Traders

```python
def compare_traders(addr1, addr2, features_df):
    t1 = features_df[features_df['address'] == addr1].iloc[0]
    t2 = features_df[features_df['address'] == addr2].iloc[0]
    
    print(f"\nTrader 1: {addr1[:10]}...")
    print(f"  Persona: {t1['persona']}")
    print(f"  Copy-Trading Score: {t1['copy_trading_score']:.3f}")
    print(f"  Win Rate: {t1['win_rate']:.2f}%")
    print(f"  PnL: ${t1['total_pnl']:,.2f}")
    
    print(f"\nTrader 2: {addr2[:10]}...")
    print(f"  Persona: {t2['persona']}")
    print(f"  Copy-Trading Score: {t2['copy_trading_score']:.3f}")
    print(f"  Win Rate: {t2['win_rate']:.2f}%")
    print(f"  PnL: ${t2['total_pnl']:,.2f}")
    
    if t1['copy_trading_score'] > t2['copy_trading_score']:
        print(f"\n✓ Recommendation: Trader 1")
    else:
        print(f"\n✓ Recommendation: Trader 2")

# Usage
compare_traders('12ezPHMd...', 'CcLYwqv5...', features)
```

---

## Updating Your Data

### Add New Traders

1. Add new rows to your CSV file
2. Re-run the analysis:
   ```bash
   python examples/run_hybrid_analysis.py
   ```
3. Check if new traders appear in top rankings

### Weekly/Monthly Updates

```python
# Recommended: Keep historical snapshots
import shutil
from datetime import datetime

# Backup old results
timestamp = datetime.now().strftime('%Y%m%d')
shutil.copytree('outputs', f'outputs_backup_{timestamp}')

# Run new analysis
python examples/run_hybrid_analysis.py

# Compare changes
old = pd.read_csv(f'outputs_backup_{timestamp}/top_50_traders_overall.csv')
new = pd.read_csv('outputs/top_50_traders_overall.csv')

# Find new entries
new_traders = new[~new['address'].isin(old['address'])]
print(f"{len(new_traders)} new traders in top 50!")
```

---

## Troubleshooting

### Issue: "No high-confidence traders found"

**Solution**: Lower the threshold in `run_hybrid_analysis.py`:

```python
# Line ~250
high_confidence = features[
    (features['copy_trading_score'] >= 0.5) &  # Changed from 0.6
    (features['validation_passed'] == True) &
    (features['total_trades'] >= 10)  # Changed from 20
]
```

### Issue: "Too many unclassified traders"

**Reason**: They don't meet persona validation rules (e.g., low win rate, few trades)

**Solution**: Either:
1. Accept that only quality traders are classified (recommended)
2. Relax validation rules (see "Change Persona Validation Rules" above)

### Issue: "All traders are the same persona"

**Solution**: Increase number of clusters in `hybrid_persona_system.py`:

```python
# Line ~420
optimal_k = min(len(features_df) // 50, 10)  # Changed from //100
```

### Issue: "Visualizations are too small"

**Solution**: Increase DPI and figure size in visualization files:

```python
# In hybrid_visualizer.py
fig = plt.figure(figsize=(24, 20), dpi=150)  # Increase from (20, 16), dpi=100
```

---

## Best Practices

### ✅ DO:
- **Start with high-confidence recommendations** (17 traders in `high_confidence_recommendations.csv`)
- **Diversify across personas** (don't copy only one type)
- **Monitor actual performance** vs predicted scores
- **Update analysis regularly** (weekly/monthly)
- **Review visualizations** before making decisions
- **Set stop-losses** based on risk categories
- **Start small** then scale up successful traders

### ❌ DON'T:
- Copy traders with `validation_passed=False`
- Ignore risk categories
- Copy 100% from one trader
- Skip reviewing visualizations
- Use outdated data (>1 month old)
- Copy traders with <20 trades
- Ignore win rate (prefer >50%)

---

## Decision Framework

Use this flowchart to decide which traders to copy:

```
1. What's your risk tolerance?
   ├─ Low → Use top_10_low_risk.csv (Elite Snipers)
   ├─ Medium → Use top_10_medium_risk.csv (Scalpers, Consistent Performers)
   └─ High → Use top_10_medium-high_risk.csv (Whales, Momentum Traders)

2. Check copy_trading_score
   ├─ ≥0.8 → Copy immediately
   ├─ 0.6-0.8 → Strong candidate
   ├─ 0.4-0.6 → Consider for diversification
   └─ <0.4 → Skip

3. Verify validation_passed == True
   ├─ Yes → Proceed
   └─ No → Skip (doesn't meet quality standards)

4. Check total_trades
   ├─ ≥50 → Experienced
   ├─ 20-49 → Moderate experience
   └─ <20 → High variance, proceed with caution

5. Review win_rate
   ├─ ≥70% → Excellent
   ├─ 50-70% → Good
   └─ <50% → Only if high PnL justifies it

6. Make decision
   ├─ All checks pass → Add to copy-trading list
   └─ Any check fails → Skip or reduce allocation
```

---

## Example: Building a Copy-Trading Portfolio

```python
import pandas as pd

# Load recommendations
high_conf = pd.read_csv('outputs/high_confidence_recommendations.csv')

# Portfolio allocation
portfolio = {
    'conservative': [],  # 40% of capital
    'moderate': [],      # 40% of capital
    'aggressive': []     # 20% of capital
}

# Conservative: Top 3 Elite Snipers
elites = high_conf[high_conf['persona'] == 'Elite Sniper'].nlargest(3, 'copy_trading_score')
portfolio['conservative'] = elites['address'].tolist()

# Moderate: Top 3 Scalpers or Consistent Performers
moderate_personas = ['Scalper', 'Consistent Performer']
moderate = high_conf[high_conf['persona'].isin(moderate_personas)].nlargest(3, 'copy_trading_score')
portfolio['moderate'] = moderate['address'].tolist()

# Aggressive: Top 2 Whales
whales = high_conf[high_conf['persona'] == 'Whale'].nlargest(2, 'copy_trading_score')
portfolio['aggressive'] = whales['address'].tolist()

print("Copy-Trading Portfolio:")
print(f"Conservative (40%): {len(portfolio['conservative'])} traders")
print(f"Moderate (40%): {len(portfolio['moderate'])} traders")
print(f"Aggressive (20%): {len(portfolio['aggressive'])} traders")
print(f"\nTotal: {sum(len(v) for v in portfolio.values())} traders")
```

---

## Getting Help

- **Documentation**: See `METHODOLOGY.md` for technical details
- **Visualization Guide**: See `VISUALIZATION_GUIDE.md` for plot interpretation
- **Results Summary**: See `RESULTS_SUMMARY.md` for latest analysis
- **Quick Start**: See `QUICKSTART.md` for basic usage

---

**Remember**: Past performance doesn't guarantee future results. Always do your own research and start with small allocations when copy-trading!
