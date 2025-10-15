# Trader Selection Framework

A research-grade framework for statistical evaluation and segmentation of crypto wallet addresses using clustering, predictive modeling, and behavioral persona assignment.

## 🎯 Overview

This framework provides a comprehensive, statistically-rigorous approach to identifying high-potential crypto traders from transaction data. It combines machine learning, statistical validation, and domain expertise to segment traders into behavioral personas and predict future performance.

## 📊 Key Features

### 1. **Feature Engineering**
- Profitability metrics (ROI, win rate, Sharpe ratio, Sortino ratio)
- Recency-weighted performance indicators with exponential decay
- Risk-adjusted metrics (volatility, drawdown, Calmar ratio)
- Trading activity patterns (frequency, consistency, volume)

### 2. **Clustering Analysis**
- Multiple clustering algorithms (K-Means, DBSCAN, Hierarchical)
- Automatic optimal cluster selection using elbow method and silhouette analysis
- Statistical validation (silhouette score, Calinski-Harabasz, Davies-Bouldin)
- PCA-based dimensionality reduction for visualization

### 3. **Predictive Modeling**
- **Binary Classification**: Identify high-potential traders
  - Ensemble methods (XGBoost, LightGBM, Random Forest, Gradient Boosting)
  - SMOTE for handling class imbalance
  - Probability calibration for high-potential identification
- **Multi-class Persona Prediction**: ML-based persona classification
  - Train models to predict trader personas from behavior patterns
  - 8-class classification (Whale, Sniper, Scalper, HODLer, Risk Taker, Consistent, Newcomer, Inactive)
  - Superior accuracy compared to rule-based assignment
  - Confidence scores and probability distributions for each persona
- Cross-validation and feature importance analysis

### 4. **Persona Assignment**
- **The Whale**: High volume, market-moving trades
- **The Sniper**: High win rate, precision entries, selective trading
- **The Scalper**: High frequency, small consistent profits
- **The HODLer**: Patient, long-term positions, infrequent trading
- **The Risk Taker**: Aggressive, high volatility, boom-or-bust
- **The Consistent**: Steady, reliable performance, moderate risk
- **The Newcomer**: Recently active, establishing track record
- **The Inactive**: Dormant, no recent activity

### 5. **Statistical Validation**
- Hypothesis testing (t-tests, Mann-Whitney U, Kolmogorov-Smirnov)
- Confidence interval calculations
- Effect size analysis
- Correlation and multicollinearity detection

### 6. **Visualization Tools**
- Cluster scatter plots with PCA projection
- Persona distribution and performance comparisons
- Feature importance rankings
- Correlation heatmaps
- Comprehensive summary dashboards

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MoonCraze/trader-selection.git
cd trader-selection

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

#### Run Complete Analysis
```bash
python complete_analysis_pipeline.py --data ../data/traders_202510140811.csv --output ../outputs
```

### Python API Usage

```python
from trader_analysis import (
    FeatureEngineer,
    TraderSegmentation,
    HighPotentialPredictor,
    PersonaAssigner,
    ModelEvaluator
)
import pandas as pd

# Load your transaction data
df = pd.read_csv('your_transactions.csv')
# Required columns: address, timestamp, pnl, volume (optional), entry_price, exit_price

# 1. Feature Engineering
engineer = FeatureEngineer(recency_decay=0.1)
features = engineer.engineer_features(df)

# 2. Clustering
clusterer = TraderSegmentation(random_state=42)
clusterer.fit_kmeans(features.drop('address', axis=1).values, optimize_k=True)
features['cluster'] = clusterer.labels_

# 3. Persona Assignment (Rule-based)
persona_assigner = PersonaAssigner()
features = persona_assigner.assign_personas(features)

# 4. Predictive Modeling - Binary High-Potential Prediction
predictor = HighPotentialPredictor(random_state=42)
target = predictor.create_target_labels(features, top_percentile=0.2)
X_train, X_test, y_train, y_test = predictor.prepare_data(features, target)
predictor.train_ensemble(X_train, y_train)
predictor.evaluate(X_test, y_test)

# 5. ML-based Persona Prediction (requires true labels)
if 'true_archetype' in df.columns:
    persona_predictor = HighPotentialPredictor(
        random_state=42, 
        prediction_type='persona'
    )
    persona_target = persona_predictor.create_persona_target_labels(df_with_labels)
    X_train_p, X_test_p, y_train_p, y_test_p = persona_predictor.prepare_data(
        features, persona_target
    )
    persona_predictor.train_ensemble(X_train_p, y_train_p)
    persona_predictor.evaluate(X_test_p, y_test_p)
    
    # Get persona predictions
    X_scaled_p = persona_predictor.scaler.transform(features.drop('address', axis=1).values)
    predicted_personas = persona_predictor.predict(X_scaled_p)
    persona_probs = persona_predictor.predict_proba_ensemble(X_scaled_p)

# 6. Get High-Potential Traders
X_scaled = predictor.scaler.transform(features.drop('address', axis=1).values)
features['high_potential_score'] = predictor.predict_proba_ensemble(X_scaled)[:, 1]
high_potential = features[features['high_potential_score'] > 0.7]
```

### Run Persona Prediction Demo

```bash
cd examples
python persona_prediction_demo.py
```

This demonstrates:
- Training a multi-class classifier to predict trader personas
- 77.5% accuracy on 8-class persona prediction
- Feature importance for persona classification
- Comparison of predicted vs rule-based persona assignment

## 📁 Project Structure

```
trader-selection/
├── src/
│   └── trader_analysis/
│       ├── __init__.py
│       ├── feature_engineering.py    # Feature extraction and engineering
│       ├── clustering.py              # Clustering algorithms
│       ├── prediction.py              # Predictive models
│       ├── personas.py                # Persona assignment logic
│       ├── evaluation.py              # Statistical validation
│       └── visualization.py           # Plotting and visualization
├── examples/
│   ├── complete_analysis_pipeline.py # End-to-end pipeline
│   └── persona_prediction_demo.py    # Persona prediction demonstration
├── data/
│   ├── raw/                          # Raw transaction data
│   └── processed/                    # Processed features
├── models/                           # Saved models
├── outputs/                          # Analysis results
├── notebooks/                        # Jupyter notebooks
├── requirements.txt                  # Python dependencies
├── .gitignore
└── README.md
```

## 📈 Methodology

### Statistical Approach

The framework implements a multi-stage methodology:

1. **Data Preprocessing**: Clean and validate transaction data
2. **Feature Engineering**: Extract 25+ metrics covering profitability, risk, and activity
3. **Recency Weighting**: Apply exponential decay to emphasize recent performance
4. **Clustering**: Segment traders into behavioral groups using unsupervised learning
5. **Persona Mapping**: Assign interpretable personas based on cluster characteristics
6. **Predictive Modeling**: Train ensemble classifiers to identify high-potential traders
7. **Statistical Validation**: Perform hypothesis tests and confidence interval analysis
8. **Portfolio Construction**: Select top traders based on combined scores

### Key Metrics

#### Profitability Metrics
- **Total PNL**: Cumulative profit/loss
- **ROI**: Return on investment
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Sharpe Ratio**: Risk-adjusted return (annualized)
- **Sortino Ratio**: Downside risk-adjusted return

#### Risk Metrics
- **Volatility**: Standard deviation of returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Calmar Ratio**: Return / Maximum drawdown
- **Risk-Adjusted Return**: Mean return / Volatility

#### Activity Metrics
- **Trades Per Day**: Average trading frequency
- **Active Days**: Number of unique trading days
- **Consistency Score**: Regularity of trading intervals
- **Recency Score**: Activity recency (exponentially weighted)

### Machine Learning Models

The ensemble predictor combines:
- **XGBoost**: Gradient boosting with regularization
- **LightGBM**: Fast gradient boosting framework
- **Random Forest**: Ensemble of decision trees
- **Gradient Boosting**: Sequential tree building
- **Logistic Regression**: Baseline linear model

Models are trained with:
- Stratified train-test split (80/20)
- SMOTE for class imbalance handling
- 5-fold cross-validation
- Hyperparameter optimization

## 📊 Output Files

After running the complete analysis pipeline, the following files are generated:

- `engineered_features.csv`: Complete feature matrix
- `cluster_statistics.csv`: Per-cluster summary statistics
- `persona_statistics.csv`: Per-persona performance metrics
- `feature_importance.csv`: Ranked feature importances
- `high_potential_traders.csv`: Identified high-potential traders
- `top_20_traders.csv`: Top 20 ranked traders
- `complete_analysis_results.csv`: Full results with all scores
- `*.png`: Visualization plots and dashboards

## 🔬 Statistical Validation

The framework includes comprehensive statistical validation:

- **Cluster Stability**: Adjusted Rand Index across multiple runs
- **Significance Testing**: Mann-Whitney U, t-tests, Kolmogorov-Smirnov
- **Confidence Intervals**: Bootstrap and parametric methods
- **Effect Size**: Cohen's d for practical significance
- **Correlation Analysis**: Pearson and Spearman correlations
- **Cross-Validation**: K-fold stratified validation

## 📚 Example Notebooks

Coming soon: Jupyter notebooks demonstrating:
- Exploratory data analysis
- Feature engineering deep dive
- Model comparison and selection
- Hyperparameter tuning
- Backtesting strategies

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 📧 Contact

For questions or collaboration opportunities, please open an issue on GitHub.

## 🙏 Acknowledgments

This framework was developed using best practices from:
- Academic research in quantitative finance
- Industry standards in algorithmic trading
- Statistical machine learning literature
- Open-source data science community

---

**Note**: This is a research framework. Always perform due diligence and additional validation before making trading decisions based on model outputs.