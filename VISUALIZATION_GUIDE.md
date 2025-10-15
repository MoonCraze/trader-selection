# Visualization Guide - Hybrid Persona System

## Overview

The hybrid persona system includes comprehensive visualization capabilities to help understand and validate trader classifications, rankings, and quality metrics.

## Visualization Modules

### 1. HybridVisualizer (hybrid_visualizer.py)

Advanced visualizations specifically designed for the hybrid persona classification system.

#### Key Visualizations:

#### A. **Persona Quality Matrix** (`plot_persona_quality_matrix`)
Four-panel visualization showing:
- **Confidence Distribution by Persona**: Box plots showing how confident each persona assignment is
- **Validation Pass Rate**: Bar chart showing what percentage of each persona passes validation rules
- **Persona Size vs Confidence**: Scatter plot revealing if larger personas have better confidence
- **Overall Confidence Distribution**: Pie chart showing high/medium/low confidence splits

**Use Case**: Quality assurance - ensures personas are well-separated and confidently assigned

#### B. **Follow-Worthiness Rankings** (`plot_follow_worthiness_rankings`)
Four-panel analysis of trader rankings:
- **Top 30 Overall Rankings**: Horizontal bar chart with color-coded personas
- **Score Component Breakdown**: Stacked bars showing profitability, consistency, risk, activity contributions
- **Persona-wise Performance**: Comparison of top and average scores per persona
- **Score Distribution by Persona**: Box plots showing score ranges

**Use Case**: Identifying best traders overall and within each persona type

#### C. **Persona Characteristics Radar Charts** (`plot_persona_characteristics_radar`)
Multi-panel radar/spider charts showing:
- One radar per persona
- 5 key metrics: win_rate, roi, total_trades, confidence, follow_score
- Normalized to 0-1 scale for comparison

**Use Case**: Understanding what makes each persona unique - visual fingerprints

#### D. **Confidence vs Performance Analysis** (`plot_confidence_vs_performance`)
Four-panel correlation analysis:
- **Confidence vs Total PnL**: Are high-confidence classifications more profitable?
- **Confidence vs Win Rate**: Does confidence correlate with success rate?
- **Confidence vs Follow Score**: Do we rank high-confidence traders higher?
- **Performance by Confidence Category**: Average scores for low/medium/high confidence

**Use Case**: Validation that confidence scores are meaningful predictors

#### E. **Comprehensive Dashboard** (`create_comprehensive_dashboard`)
All-in-one dashboard with 11 panels:
- **Row 1**: Persona counts, average confidence, confidence pie, follow score distribution
- **Row 2**: Top 20 traders by follow score (full-width)
- **Row 3**: Win rate, ROI, PnL by persona, trades distribution
- **Row 4**: Follow score by persona (box plots), confidence vs performance scatter

**Use Case**: Executive summary - print this for reports/presentations

### 2. Standard Visualizer (visualization.py)

Traditional analysis visualizations:

#### Key Visualizations:

- **Cluster Scatter** (`plot_cluster_scatter`): 2D PCA/t-SNE projections
- **Persona Distribution** (`plot_persona_distribution`): Bar + pie charts
- **Performance by Persona** (`plot_performance_by_persona`): Box plots of any metric
- **Feature Importance** (`plot_feature_importance`): Horizontal bar chart
- **Correlation Matrix** (`plot_correlation_matrix`): Heatmap
- **Metric Distributions** (`plot_metric_distributions`): Histograms
- **Top Traders** (`plot_top_traders`): Ranked bar chart
- **Summary Dashboard** (`create_summary_dashboard`): 3x3 grid overview

## Usage Examples

### Quick Start - Generate All Visualizations

```python
from trader_analysis.hybrid_visualizer import HybridVisualizer
import pandas as pd

# Load your classified traders
features = pd.read_csv('outputs/complete_trader_analysis.csv')

# Initialize visualizer
viz = HybridVisualizer('outputs')

# Generate all key visualizations
viz.plot_persona_quality_matrix(features, save_path='outputs/quality.png')
viz.plot_follow_worthiness_rankings(features, save_path='outputs/rankings.png')
viz.plot_persona_characteristics_radar(features, save_path='outputs/radar.png')
viz.plot_confidence_vs_performance(features, save_path='outputs/confidence.png')
viz.create_comprehensive_dashboard(features, save_path='outputs/dashboard.png')
```

### Customization Examples

#### Show Top 50 Traders Instead of 30
```python
viz.plot_follow_worthiness_rankings(
    features,
    top_n=50,  # Increase from default 30
    save_path='outputs/top_50_rankings.png'
)
```

#### Focus on Specific Personas
```python
# Filter to Elite Snipers only
elite_snipers = features[features['persona'] == 'Elite Sniper']

viz.plot_confidence_vs_performance(
    elite_snipers,
    save_path='outputs/elite_sniper_analysis.png'
)
```

#### Integrate with Analysis Pipeline
```python
def run_complete_analysis_with_viz(data_path, output_dir):
    # Step 1: Run hybrid classification
    system = HybridPersonaSystem()
    features = system.classify_and_rank(data_path)
    
    # Step 2: Generate visualizations
    viz = HybridVisualizer(output_dir)
    
    viz.plot_persona_quality_matrix(features, 
        save_path=f"{output_dir}/quality_check.png")
    
    viz.plot_follow_worthiness_rankings(features,
        save_path=f"{output_dir}/rankings.png")
    
    viz.create_comprehensive_dashboard(features,
        save_path=f"{output_dir}/dashboard.png")
    
    return features
```

## Output Files

When running the full hybrid analysis pipeline, these PNG files are generated:

### Quality & Validation
- `persona_quality_matrix.png` - 4-panel quality assessment
- `confidence_vs_performance.png` - Confidence validation

### Rankings & Performance
- `follow_worthiness_rankings.png` - Top trader rankings with breakdowns
- `comprehensive_dashboard.png` - All-in-one executive summary

### Persona Profiles
- `persona_characteristics_radar.png` - Radar charts per persona
- `persona_distribution.png` - Distribution bar + pie charts
- `performance_by_persona.png` - Box plots of PnL by persona

### Additional
- `cluster_visualization_pca.png` - 2D PCA projection (if enabled)
- `cluster_visualization_tsne.png` - 2D t-SNE projection (if enabled)

## Interpretation Guide

### How to Read Each Visualization

#### 1. Persona Quality Matrix
- **Good Signs**:
  - Confidence boxes mostly above 0.7
  - Validation pass rates > 90%
  - Large personas (500+) still have high confidence
- **Red Flags**:
  - Wide confidence distributions (lots of uncertainty)
  - Validation pass rates < 70%
  - Tiny personas (<10 traders) might be outliers

#### 2. Follow-Worthiness Rankings
- **What to Look For**:
  - Diverse personas in top 20 (not all one type)
  - Score components balanced (not 100% from one factor)
  - Clear separation between top and average performers
- **Actions**:
  - Copy-trade the top 10-20
  - Focus on personas with high average scores
  - Investigate low-scoring personas for improvement

#### 3. Radar Charts
- **Reading**:
  - Larger area = stronger overall characteristics
  - Spikes = extreme specialization
  - Balanced pentagon = well-rounded trader type
- **Comparisons**:
  - "Elite Sniper" should spike on win_rate
  - "Whale" should spike on total_trades/volume
  - "Consistent Performer" should be balanced

#### 4. Confidence vs Performance
- **Ideal Relationship**:
  - Positive correlation (upward trend line)
  - High-confidence traders cluster at top-right
  - Few low-confidence/high-performance outliers
- **If No Correlation**:
  - May need to adjust confidence formula
  - Could indicate overfitting or noise

#### 5. Comprehensive Dashboard
- **Quick Checks**:
  - Top row: Overall statistics
  - Middle row: Top traders list (ready to copy-trade)
  - Bottom rows: Distribution quality
- **Decision Making**:
  - Print for stakeholder meetings
  - Include in reports/presentations
  - Use as daily monitoring dashboard

## Best Practices

### 1. Generate After Every Analysis
Always create visualizations after running classification:
```python
# Bad
features = classify_traders(data)
features.to_csv('results.csv')

# Good
features = classify_traders(data)
features.to_csv('results.csv')
viz = HybridVisualizer('outputs')
viz.create_comprehensive_dashboard(features, save_path='outputs/dashboard.png')
```

### 2. Version Your Visualizations
Include timestamps in filenames:
```python
from datetime import datetime
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
save_path = f"outputs/dashboard_{timestamp}.png"
```

### 3. Compare Over Time
Keep historical dashboards to track changes:
```
outputs/
  dashboard_20250114.png
  dashboard_20250115.png  # Compare to see persona drift
  dashboard_20250116.png
```

### 4. Customize for Your Audience
- **For Technical Teams**: Show quality matrix, confidence analysis
- **For Business**: Show rankings, comprehensive dashboard
- **For Traders**: Show radar charts, top performers

## Troubleshooting

### Common Issues

#### "Figure too small to read"
```python
# Increase DPI
viz.create_comprehensive_dashboard(features, save_path='outputs/big_dashboard.png')
# Then manually edit hybrid_visualizer.py to increase figsize
```

#### "Too many personas for radar chart"
```python
# Filter to top personas only
top_personas = features['persona'].value_counts().head(6).index
filtered = features[features['persona'].isin(top_personas)]
viz.plot_persona_characteristics_radar(filtered)
```

#### "Visualization generation is slow"
```python
# Use matplotlib Agg backend (no display window)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

## Advanced Customization

### Change Color Schemes
Edit `hybrid_visualizer.py`:
```python
# Line ~15
sns.set_palette("Set2")  # Change from "husl"
```

### Add Custom Metrics to Radar
Edit `plot_persona_characteristics_radar` method:
```python
# Add your custom metric
metrics = ['win_rate', 'roi', 'total_trades', 'confidence', 
           'follow_score', 'custom_metric']  # Add here
```

### Create Custom Visualizations
```python
class MyCustomVisualizer(HybridVisualizer):
    def plot_my_special_analysis(self, features_df):
        fig, ax = plt.subplots(figsize=(12, 8))
        # Your custom plotting code
        plt.savefig('outputs/my_custom_plot.png', dpi=300)
```

## Integration with Reports

### Export to PowerPoint
```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()

# Add dashboard slide
slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
slide.shapes.add_picture('outputs/comprehensive_dashboard.png',
                        Inches(0.5), Inches(1), width=Inches(9))

prs.save('trader_analysis_report.pptx')
```

### Create PDF Report
```python
from matplotlib.backends.backend_pdf import PdfPages

with PdfPages('trader_analysis_report.pdf') as pdf:
    # Generate all visualizations
    viz.plot_persona_quality_matrix(features)
    pdf.savefig()
    plt.close()
    
    viz.plot_follow_worthiness_rankings(features)
    pdf.savefig()
    plt.close()
    
    # Add metadata
    d = pdf.infodict()
    d['Title'] = 'Trader Analysis Report'
    d['Author'] = 'Hybrid Persona System'
    d['CreationDate'] = datetime.now()
```

---

## Quick Reference

| Visualization | Best For | Key Insight |
|--------------|----------|-------------|
| Quality Matrix | Validation | Are personas well-defined? |
| Rankings | Decision Making | Who to follow? |
| Radar Charts | Understanding | What makes each persona unique? |
| Confidence vs Performance | Validation | Is confidence meaningful? |
| Dashboard | Overview | Everything at a glance |

**Remember**: Visualizations are not just pretty pictures - they're validation tools, decision aids, and communication devices. Use them actively!
