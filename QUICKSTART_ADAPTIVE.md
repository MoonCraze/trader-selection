# Quick Start Guide - Adaptive Persona System

## 🚀 5-Minute Quickstart

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Analysis
```bash
python examples/complete_adaptive_analysis.py
```

### Step 3: Check Results
Look in the `outputs/` folder for:
- `traders_with_personas.csv` - All traders with persona assignments
- Various PNG visualizations
- Statistical summaries

## 📊 What You Get

### Automatic Discovery
The system automatically:
- ✅ Discovers 3-10 trader personas from your data
- ✅ Names them based on behavior (e.g., "High-Volume Sniper")
- ✅ Assigns confidence scores (how certain the classification is)
- ✅ Identifies mixed personas (traders with hybrid characteristics)

### Key Outputs

#### 1. Trader Classifications
Each trader gets:
- **Persona name** (e.g., "Sniper", "Risk-Taker")
- **Confidence score** (0-100%)
- **Probability for each persona** (shows how mixed they are)

#### 2. Persona Profiles
For each discovered persona:
- Statistical summary (mean, median, std)
- Size and percentage of total
- Top distinguishing features

#### 3. Visualizations
- PCA plot showing cluster separation
- t-SNE plot for pattern visualization
- Distribution charts
- Performance comparisons

## 🎯 Understanding the Results

### High Confidence (>70%)
Trader clearly belongs to this persona. Strong, consistent behavioral pattern.

### Medium Confidence (40-70%)
Trader mostly fits this persona but shows some mixed characteristics.

### Low Confidence (<40%)
Trader has very mixed behavior, doesn't fit cleanly into one persona.

## 💡 Common Use Cases

### Find Top Performers by Type
```python
# Load results
traders = pd.read_csv('outputs/traders_with_personas.csv')

# Get top "Sniper" traders
snipers = traders[traders['persona'] == 'Sniper']
top_snipers = snipers.nlargest(10, 'total_pnl')
```

### Identify Mixed Personas
```python
# Find traders with uncertain classifications
mixed = traders[traders['persona_confidence'] < 0.7]
print(f"Found {len(mixed)} mixed persona traders")
```

### Compare Personas
```python
# Average performance by persona
persona_performance = traders.groupby('persona')['total_pnl'].mean()
print(persona_performance)
```

## 🔧 Customization

### Change Number of Personas
```python
learner = AdaptivePersonaLearner(
    min_clusters=3,   # Minimum personas to consider
    max_clusters=12   # Maximum personas to consider
)
```

### Use Different Features
```python
# Select specific features for clustering
custom_features = [
    'total_pnl', 'win_rate', 'total_trades',
    'roi', 'avg_trade_size'
]

learner.fit(traders, feature_names=custom_features)
```

### Change Visualization Method
```python
# Use UMAP instead of PCA
features_2d = learner.reduce_dimensions(
    traders, 
    method='umap',  # or 'pca', 'tsne'
    n_components=2
)
```

## 📈 Interpreting Outputs

### `persona_statistics.csv`
Shows aggregated stats per persona:
- `count`: Number of traders
- `percentage`: % of total traders
- `mean_*`: Average values for each metric

### `discriminative_features.csv`
Shows which features best distinguish personas:
- Higher `importance` = more useful for separating personas
- Top features are the most characteristic

### `traders_with_personas.csv`
Complete dataset with:
- Original data columns
- `persona`: Assigned persona name
- `persona_id`: Numeric cluster ID
- `persona_confidence`: How certain (0-1)
- `prob_<PersonaName>`: Probability for each persona

## ⚠️ Important Notes

### Data Requirements
- Minimum ~100 traders for meaningful clustering
- More traders = better persona discovery
- Bots are automatically filtered out

### Persona Names
- Automatically generated based on dominant characteristics
- May need manual interpretation for your specific context
- Check persona profiles for statistical details

### Confidence Scores
- Based on distance to cluster center
- Lower score = trader is between personas
- Use threshold of 0.7 for high-confidence classifications

## 🆘 Troubleshooting

### "Too few traders"
- Need at least 50-100 traders for meaningful clustering
- Reduce `min_clusters` parameter

### "All traders in one persona"
- Data may be too homogeneous
- Try different feature selections
- Check if bots were properly filtered

### "Persona names not meaningful"
- Check the statistical profiles in persona_statistics.csv
- Names are auto-generated, may need custom logic for your domain
- Use `persona_id` and create your own names

## 📚 Learn More

- See `README_ADAPTIVE.md` for detailed documentation
- Check `IMPLEMENTATION_SUMMARY_ADAPTIVE.md` for technical details
- Example code in `examples/complete_adaptive_analysis.py`

## 🤝 Getting Help

1. Check the output logs - they show the discovery process
2. Review persona_statistics.csv to understand each persona
3. Examine discriminative_features.csv to see what matters most
4. Look at visualizations to see cluster separation

---

**Ready to discover your traders' personas?**

```bash
python examples/complete_adaptive_analysis.py
```
