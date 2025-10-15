# Quick Start Guide

Get started with the Trader Selection Framework in minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/MoonCraze/trader-selection.git
cd trader-selection

# Install dependencies
pip install -r requirements.txt
```

## 5-Minute Tutorial

### Step 2: Run Complete Analysis

```bash
python complete_analysis_pipeline.py
```

This runs the entire pipeline and generates:
- Feature engineering
- Clustering analysis
- Persona assignment (rule-based)
- **ML-based persona prediction** (NEW)
- Binary high-potential trader prediction
- Statistical validation
- Visualizations and reports

Results are saved to `outputs/` directory.

### Step 2b: Run Persona Prediction Demo

```bash
python persona_prediction_demo.py
```

This demonstrates the new multi-class persona prediction capability:
- Trains ML models to predict trader personas
- Achieves strong accuracy on 8-class classification
- Shows feature importance for persona prediction
- Compares ML predictions with rule-based assignment

### Step 3: View Results

Check these key output files:
- `outputs/high_potential_traders.csv` - Identified high-potential traders
- **`outputs/persona_predictions.csv`** - ML-predicted personas with probabilities (NEW)
- **`outputs/persona_prediction_feature_importance.csv`** - Features for persona prediction (NEW)
- `outputs/top_20_traders.csv` - Top 20 ranked traders
- `outputs/persona_statistics.csv` - Performance by persona
- `outputs/summary_dashboard.png` - Visual summary
- `outputs/complete_analysis_results.csv` - Full results

## Custom Analysis

### Analyze Your Own Data

Create a CSV file with required columns:
```
address,timestamp,pnl,volume,entry_price,exit_price,capital_deployed
```

Then run:
```bash
python complete_analysis_pipeline.py --data /path/to/your/data.csv --output /path/to/outputs
```

### Python API

```python
import pandas as pd
from trader_analysis import FeatureEngineer, PersonaAssigner

# Load your data
df = pd.read_csv('your_transactions.csv')

# Engineer features
engineer = FeatureEngineer(recency_decay=0.1)
features = engineer.engineer_features(df)

# Assign personas
assigner = PersonaAssigner()
features = assigner.assign_personas(features)

# View results
print(features[['address', 'persona', 'weighted_pnl', 'roi', 'win_rate']].head())
```

## Understanding the Output

### Personas

- **The Whale**: High-volume traders with significant market presence
- **The Sniper**: High win rate (>60%), selective entries, excellent timing
- **The Scalper**: High-frequency trading, many small profits
- **The HODLer**: Patient, long-term positions, infrequent trading
- **The Risk Taker**: Aggressive, high volatility, boom-or-bust
- **The Consistent**: Steady, reliable performance, moderate risk
- **The Newcomer**: Recently active, establishing track record
- **The Inactive**: Dormant, no recent activity (90+ days)

### Key Metrics

- **Weighted PNL**: Recent performance weighted more heavily
- **ROI**: Return on investment
- **Win Rate**: Percentage of profitable trades
- **Sharpe Ratio**: Risk-adjusted return (higher is better)
- **High Potential Score**: Probability of being high-performing (0-1)

### Interpreting Results

1. **High Potential Score > 0.7**: Strong candidate
2. **High Potential Score 0.5-0.7**: Moderate candidate
3. **High Potential Score < 0.5**: Lower probability

Combine with:
- Recent activity (days_since_last_trade < 30)
- Minimum track record (total_trades > 10)
- Positive ROI
- Persona fit for your strategy

## Jupyter Notebook

For interactive analysis:

```bash
jupyter notebook notebooks/example_analysis.ipynb
```

## Common Use Cases

### 1. Find Top Performing Whales

```python
whales = features[features['persona'] == 'The Whale']
top_whales = whales.nlargest(10, 'weighted_pnl')
```

### 2. Identify Consistent Low-Risk Traders

```python
consistent = features[
    (features['persona'] == 'The Consistent') &
    (features['volatility'] < features['volatility'].quantile(0.5)) &
    (features['win_rate'] > 0.5)
]
```

### 3. Find High-Win-Rate Snipers

```python
snipers = features[
    (features['persona'] == 'The Sniper') &
    (features['win_rate'] > 0.65) &
    (features['high_potential_score'] > 0.7)
]
```

### 4. Build Diversified Portfolio

```python
# Select top traders from each persona
portfolio = []
for persona in features['persona'].unique():
    if persona not in ['The Inactive', 'The Newcomer']:
        top_5 = features[features['persona'] == persona].nlargest(5, 'high_potential_score')
        portfolio.append(top_5)

portfolio_df = pd.concat(portfolio)
```

## Customization

### Adjust Recency Weighting

```python
# More emphasis on recent trades
engineer = FeatureEngineer(recency_decay=0.2)

# Less emphasis on recent trades
engineer = FeatureEngineer(recency_decay=0.05)
```

### Change High-Potential Threshold

```python
# Top 10% instead of top 20%
target = predictor.create_target_labels(features, top_percentile=0.10)

# Top 30%
target = predictor.create_target_labels(features, top_percentile=0.30)
```

### Modify Minimum Requirements

```python
target = predictor.create_target_labels(
    features,
    top_percentile=0.2,
    min_trades=20,  # Require more trades
)
```

## Troubleshooting

### Issue: Not enough high-potential traders

**Solution**: Lower the threshold or percentile
```python
target = predictor.create_target_labels(features, top_percentile=0.3)
```

### Issue: Too many inactive traders

**Solution**: Filter before analysis
```python
df_active = df[df.groupby('address')['timestamp'].transform('max') > recent_date]
```

### Issue: Personas not diverse

**Solution**: Check your data distribution and minimum trade requirements

## Next Steps

1. Read the [Methodology](METHODOLOGY.md) for detailed explanations
2. Explore the [API documentation](README.md#python-api-usage)
3. Customize parameters for your use case
4. Backtest on historical data
5. Monitor performance of selected traders

## Support

- GitHub Issues: Report bugs or request features
- Documentation: See README.md and METHODOLOGY.md
- Examples: Check `examples/` directory

---

Happy trading! 🚀
