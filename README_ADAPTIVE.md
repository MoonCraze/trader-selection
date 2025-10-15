# Intelligent Data-Driven Trader Selection Framework

**Version 2.0** - Adaptive Persona Discovery System

A sophisticated, research-grade framework for discovering and analyzing trader personas using unsupervised machine learning. This system replaces traditional rule-based classification with intelligent pattern discovery that learns directly from trading behavior data.

## Overview

This framework implements an **Intelligent Data-Driven Persona System** that:

- **Discovers personas organically** from trading data without predefined rules
- **Automatically determines** the optimal number of trader archetypes
- **Generates interpretable names** for discovered personas based on statistical profiles
- **Provides probabilistic membership** scores instead of binary classification
- **Tracks temporal evolution** of traders across personas over time
- **Identifies career paths** and common progression patterns

## Key Features

### 1. **Adaptive Persona Discovery**
- Unsupervised clustering with multiple algorithms (K-Means, Hierarchical, DBSCAN)
- Automatic optimal cluster selection using gap statistics and silhouette analysis
- Statistical profiling and automated persona naming
- Discriminative feature analysis to identify what distinguishes each persona

### 2. **Temporal Evolution Tracking**
- Transition probability matrices between personas
- Career path analysis and common progression patterns
- Trader trajectory modeling and prediction
- Lifecycle stage detection (Early, Growth, Mature, Decline)

### 3. **Probabilistic Classification**
- Soft membership assignments (e.g., 70% Persona A, 30% Persona B)
- Confidence scores for all assignments
- Mixed persona identification for traders with hybrid characteristics

### 4. **Continuous Learning**
- Adaptive system that evolves with new data
- Drift detection for emerging trader behaviors
- Stability metrics and validation

## System Architecture

```
traders_202510140811.csv
        ↓
┌───────────────────────┐
│  Feature Engineering  │
│  - Trading metrics    │
│  - Risk indicators    │
│  - Activity patterns  │
└───────────────────────┘
        ↓
┌───────────────────────┐
│ Adaptive Clustering   │
│  - Auto-optimal K     │
│  - Multiple algorithms│
│  - Validation metrics │
└───────────────────────┘
        ↓
┌───────────────────────┐
│  Persona Profiling    │
│  - Statistical analysis│
│  - Automated naming   │
│  - Feature importance │
└───────────────────────┘
        ↓
┌───────────────────────┐
│ Temporal Evolution    │
│  - Transition tracking│
│  - Career paths       │
│  - Lifecycle stages   │
└───────────────────────┘
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd trader-selection

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run adaptive persona discovery
python examples/complete_adaptive_analysis.py

# Run temporal evolution analysis
python examples/temporal_evolution_demo.py
```

### Python API

```python
from trader_analysis import AdaptivePersonaLearner, TemporalEvolutionTracker

# Load your data
import pandas as pd
traders = pd.read_csv('data/traders_202510140811.csv')

# Discover personas adaptively
learner = AdaptivePersonaLearner(min_clusters=3, max_clusters=10)
learner.fit(traders, algorithm='kmeans', auto_k=True)

# Assign personas with confidence scores
traders = learner.assign_personas(traders)

# Get persona profiles
profiles = learner.get_persona_profiles()
names = learner.get_persona_names()

# Predict persona for new traders
probabilities = learner.predict_persona(new_traders, return_probabilities=True)

# Track evolution (with historical data)
tracker = TemporalEvolutionTracker()
transition_matrix = tracker.calculate_transition_matrix(historical_data)
career_paths = tracker.identify_career_paths(historical_data)
```

## Project Structure

```
trader-selection/
├── data/
│   └── traders_202510140811.csv      # Source data
├── src/
│   └── trader_analysis/
│       ├── adaptive_personas.py       # Adaptive persona learning
│       ├── temporal_evolution.py      # Evolution tracking
│       ├── clustering.py              # Enhanced clustering
│       ├── feature_engineering.py     # Feature creation
│       ├── evaluation.py              # Statistical validation
│       └── visualization.py           # Plotting utilities
├── examples/
│   ├── complete_adaptive_analysis.py  # Main analysis pipeline
│   └── temporal_evolution_demo.py     # Evolution tracking demo
├── outputs/                           # Analysis results
└── requirements.txt                   # Dependencies
```

## Key Differences from Traditional Systems

| Traditional Rule-Based | Adaptive Data-Driven |
|------------------------|----------------------|
| Fixed predefined personas | Dynamic discovery from data |
| Manual threshold tuning | Auto-optimal clustering |
| Binary membership | Probabilistic membership |
| Static over time | Evolves with market changes |
| Limited to expected patterns | Discovers unexpected behaviors |
| Separate clustering & personas | Integrated approach |

## Methodology

### Unsupervised Pattern Discovery
1. **Multi-Algorithm Clustering**: Tests K-Means, Hierarchical, and DBSCAN
2. **Optimal Cluster Selection**: 
   - Silhouette analysis
   - Gap statistics
   - Davies-Bouldin index
   - Calinski-Harabasz score
3. **Stability Validation**: Cross-validation to ensure robust clusters

### Persona Interpretation
1. **Statistical Profiling**: Calculate mean, median, std for all features per cluster
2. **Discriminative Analysis**: F-ratio to identify features that best separate personas
3. **Automated Naming**: Rule-based naming from dominant characteristics
4. **Confidence Scoring**: Distance-based probability of membership

### Temporal Tracking
1. **Transition Matrix**: Markov chain of persona transitions
2. **Career Paths**: Sequence mining for common progressions
3. **Lifecycle Detection**: Activity trend analysis
4. **Stability Metrics**: Entropy and transition frequency

## Output Files

After running the analysis, you'll find:

- `traders_with_personas.csv` - Complete trader data with persona assignments
- `persona_statistics.csv` - Aggregated statistics per persona
- `discriminative_features.csv` - Feature importance rankings
- `top_traders_<persona>.csv` - Top performers in each persona
- `persona_clusters_pca.png` - PCA visualization
- `persona_clusters_tsne.png` - t-SNE visualization
- `persona_distribution.png` - Persona size distribution
- `performance_by_persona.png` - Performance comparisons
- `analysis_summary.json` - Complete analysis metadata

## Advanced Features

### Custom Feature Engineering

```python
# Add custom features before clustering
traders['custom_metric'] = traders['wins'] / (traders['losses'] + 1)
feature_columns.append('custom_metric')

learner.fit(traders, feature_names=feature_columns)
```

### Dimensionality Reduction

```python
# Visualize in 2D using PCA, t-SNE, or UMAP
features_2d = learner.reduce_dimensions(traders, method='umap')
```

### Mixed Persona Analysis

```python
# Find traders with mixed characteristics
mixed = traders[traders['persona_confidence'] < 0.7]
print(mixed[['address', 'persona', 'persona_confidence']])
```

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{trader_selection_framework,
  title={Intelligent Data-Driven Trader Selection Framework},
  author={MoonCraze},
  year={2025},
  version={2.0}
}
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License.

## 🔗 Links

- **Documentation**: See inline code documentation
- **Examples**: Check the `examples/` directory
- **Issues**: Report bugs or request features via GitHub Issues

---

**Built with care for the crypto trading community**
