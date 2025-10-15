"""
Complete Adaptive Analysis Pipeline

Demonstrates the intelligent data-driven persona discovery system.
Uses only traders_202510140811.csv and discovers personas organically from data.

This replaces rule-based persona assignment with:
- Unsupervised pattern discovery
- Automatic optimal clustering
- Statistical persona profiling
- Probabilistic membership
- Temporal evolution tracking
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import numpy as np
from trader_analysis import (
    AdaptivePersonaLearner,
    TemporalEvolutionTracker,
    TraderSegmentation,
    ModelEvaluator
)
from trader_analysis.visualization import Visualizer


def prepare_features_from_raw_data(data_path: str) -> pd.DataFrame:
    """
    Prepare feature set from raw trader data.
    
    Parameters:
    -----------
    data_path : str
        Path to traders CSV file
        
    Returns:
    --------
    pd.DataFrame
        Feature dataframe ready for analysis
    """
    print("="*70)
    print("DATA PREPARATION")
    print("="*70)
    
    # Load data
    df = pd.read_csv(data_path)
    print(f"\nLoaded {len(df)} traders from {data_path}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Clean data
    # Remove bots if column exists
    if 'is_bot' in df.columns:
        original_count = len(df)
        df = df[df['is_bot'] == 0]
        print(f"Filtered out {original_count - len(df)} bots")
    
    # Handle missing values
    df = df.fillna(0)
    
    # Create feature set
    features = df.copy()
    
    # Rename columns for consistency
    column_mapping = {
        'wallet_address': 'address',
        'gross_profit': 'total_pnl',
        'realized_profit': 'realized_pnl',
        'realized_profit_percent': 'roi',
        'unrealized_profit': 'unrealized_pnl',
        'unrealized_profit_percent': 'unrealized_roi',
        'trades': 'total_trades',
        'trade_volume': 'total_volume'
    }
    
    features = features.rename(columns=column_mapping)
    
    # Create additional features
    features['avg_profit_per_trade'] = features['realized_pnl'] / features['total_trades'].replace(0, 1)
    features['loss_rate'] = features['losses'] / features['total_trades'].replace(0, 1)
    features['win_loss_ratio'] = features['wins'] / features['losses'].replace(0, 1)
    
    # Risk metrics
    features['profit_factor'] = (
        features['total_pnl'] / abs(features['losses'].replace(0, 1))
    )
    
    # Replace infinities
    features = features.replace([np.inf, -np.inf], 0)
    
    print(f"\n✓ Created feature set with {features.shape[1]} columns for {features.shape[0]} traders")
    
    return features


def run_adaptive_analysis(data_path: str, output_dir: str = '../outputs'):
    """
    Run complete adaptive persona analysis pipeline.
    
    Parameters:
    -----------
    data_path : str
        Path to traders CSV file
    output_dir : str
        Directory to save outputs
    """
    print("="*70)
    print("INTELLIGENT DATA-DRIVEN PERSONA DISCOVERY SYSTEM")
    print("="*70)
    print(f"\nData Source: {data_path}")
    print(f"Output Directory: {output_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # =========================================================================
    # STEP 1: Prepare Features
    # =========================================================================
    features = prepare_features_from_raw_data(data_path)
    
    # Save prepared features
    features.to_csv(f"{output_dir}/prepared_features.csv", index=False)
    
    # =========================================================================
    # STEP 2: Adaptive Persona Discovery
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 2: ADAPTIVE PERSONA DISCOVERY")
    print("="*70)
    
    # Select features for clustering (exclude identifiers)
    feature_columns = [
        'total_pnl', 'realized_pnl', 'unrealized_pnl',
        'roi', 'unrealized_roi',
        'win_rate', 'wins', 'losses', 'loss_rate', 'win_loss_ratio',
        'total_volume', 'total_trades', 'avg_trade_size',
        'avg_profit_per_trade', 'profit_factor'
    ]
    
    # Filter to existing columns
    feature_columns = [col for col in feature_columns if col in features.columns]
    
    print(f"\nUsing {len(feature_columns)} features for persona discovery:")
    print(f"  {', '.join(feature_columns)}")
    
    # Initialize adaptive persona learner
    persona_learner = AdaptivePersonaLearner(
        random_state=42,
        min_clusters=3,
        max_clusters=10
    )
    
    # Fit the model (auto-discovers optimal number of personas)
    persona_learner.fit(
        features,
        feature_names=feature_columns,
        algorithm='kmeans',
        auto_k=True
    )
    
    # Assign personas to all traders
    features = persona_learner.assign_personas(features)
    
    # =========================================================================
    # STEP 3: Persona Analysis & Interpretation
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 3: PERSONA ANALYSIS & INTERPRETATION")
    print("="*70)
    
    # Get persona statistics
    persona_stats = persona_learner.get_persona_statistics(features)
    print("\nPersona Statistics:")
    print(persona_stats[['persona', 'count', 'percentage', 
                         'mean_total_pnl', 'mean_win_rate', 'mean_total_trades']].to_string())
    
    persona_stats.to_csv(f"{output_dir}/persona_statistics.csv", index=False)
    
    # Get discriminative features
    discriminative_features = persona_learner.get_discriminative_features(top_n=15)
    print("\nTop 15 Most Discriminative Features:")
    print(discriminative_features[['feature', 'importance']].to_string())
    
    discriminative_features.to_csv(f"{output_dir}/discriminative_features.csv", index=False)
    
    # Get detailed persona profiles
    persona_profiles = persona_learner.get_persona_profiles()
    print("\nDetailed Persona Profiles:")
    for i, profile in enumerate(persona_profiles):
        persona_name = persona_learner.get_persona_names()[i]
        print(f"\n{persona_name}:")
        print(f"  Size: {profile['size']} traders ({profile['percentage']:.1f}%)")
        
        # Show top 3 distinguishing characteristics
        stats = profile['statistics']
        if 'total_pnl' in stats:
            print(f"  Avg Total PnL: ${stats['total_pnl']['mean']:,.2f}")
        if 'win_rate' in stats:
            print(f"  Avg Win Rate: {stats['win_rate']['mean']:.2%}")
        if 'total_trades' in stats:
            print(f"  Avg Trades: {stats['total_trades']['mean']:.1f}")
    
    # =========================================================================
    # STEP 4: Visualization
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 4: VISUALIZATION")
    print("="*70)
    
    visualizer = Visualizer(output_dir)
    
    # PCA visualization
    print("\nGenerating PCA visualization...")
    features_2d_pca = persona_learner.reduce_dimensions(features, method='pca', n_components=2)
    visualizer.plot_cluster_scatter(
        features_2d_pca,
        features['persona_id'].values,
        save_path=f"{output_dir}/persona_clusters_pca.png",
        title="Adaptive Personas (PCA)"
    )
    
    # t-SNE visualization
    print("Generating t-SNE visualization...")
    features_2d_tsne = persona_learner.reduce_dimensions(features, method='tsne', n_components=2)
    visualizer.plot_cluster_scatter(
        features_2d_tsne,
        features['persona_id'].values,
        save_path=f"{output_dir}/persona_clusters_tsne.png",
        title="Adaptive Personas (t-SNE)"
    )
    
    # Persona distribution
    print("Generating persona distribution plot...")
    visualizer.plot_persona_distribution(
        features,
        save_path=f"{output_dir}/persona_distribution.png"
    )
    
    # Performance by persona
    print("Generating performance comparison...")
    visualizer.plot_performance_by_persona(
        features,
        metric='total_pnl',
        save_path=f"{output_dir}/performance_by_persona.png"
    )
    
    # =========================================================================
    # STEP 5: Probabilistic Membership Analysis
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 5: PROBABILISTIC MEMBERSHIP ANALYSIS")
    print("="*70)
    
    # Find traders with mixed persona characteristics
    mixed_personas = features[features['persona_confidence'] < 0.7].copy()
    mixed_personas = mixed_personas.sort_values('persona_confidence')
    
    print(f"\nFound {len(mixed_personas)} traders with mixed persona characteristics (confidence < 0.7)")
    
    if len(mixed_personas) > 0:
        print("\nTop 10 Most Mixed Traders:")
        prob_cols = [col for col in features.columns if col.startswith('prob_')]
        display_cols = ['address', 'persona', 'persona_confidence'] + prob_cols[:3]
        print(mixed_personas.head(10)[display_cols].to_string())
        
        mixed_personas.to_csv(f"{output_dir}/mixed_persona_traders.csv", index=False)
    
    # =========================================================================
    # STEP 6: Top Traders by Persona
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 6: TOP TRADERS BY PERSONA")
    print("="*70)
    
    persona_names = persona_learner.get_persona_names()
    
    for persona_name in persona_names:
        persona_traders = features[features['persona'] == persona_name]
        
        if len(persona_traders) > 0:
            # Sort by total PnL
            top_traders = persona_traders.nlargest(10, 'total_pnl')
            
            print(f"\nTop 10 Traders in {persona_name}:")
            print(top_traders[['address', 'total_pnl', 'roi', 'win_rate', 
                              'total_trades', 'persona_confidence']].to_string())
            
            # Save to file
            top_traders.to_csv(
                f"{output_dir}/top_traders_{persona_name.replace(' ', '_').replace('/', '-')}.csv",
                index=False
            )
    
    # =========================================================================
    # STEP 7: Clustering Validation
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 7: CLUSTERING VALIDATION")
    print("="*70)
    
    # Use enhanced TraderSegmentation for additional validation
    clusterer = TraderSegmentation(random_state=42)
    
    X_features = features[feature_columns].values
    clusterer.fit_kmeans(X_features, optimize_k=False)
    clusterer.n_clusters = len(persona_names)
    
    # Evaluate clustering quality
    print("\nClustering Quality Metrics:")
    clustering_metrics = clusterer.evaluate_clustering(X_features)
    
    # Get probabilistic membership
    prob_membership = clusterer.get_probabilistic_membership(X_features)
    features['membership_entropy'] = -np.sum(
        prob_membership * np.log(prob_membership + 1e-10), axis=1
    )
    
    print(f"\nAverage Membership Entropy: {features['membership_entropy'].mean():.4f}")
    print(f"  (Lower entropy = more certain assignments)")
    
    # =========================================================================
    # STEP 8: Statistical Evaluation
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 8: STATISTICAL EVALUATION")
    print("="*70)
    
    evaluator = ModelEvaluator(confidence_level=0.95)
    
    # Compare personas statistically
    print("\nComparing personas statistically...")
    persona_comparison = evaluator.compare_personas(features, metric='total_pnl')
    
    # Confidence intervals
    confidence_intervals = evaluator.calculate_confidence_intervals(features, metric='total_pnl')
    print("\nConfidence Intervals (95%) for Total PnL by Persona:")
    print(confidence_intervals[['persona', 'mean', 'ci_lower', 'ci_upper']].to_string())
    
    confidence_intervals.to_csv(f"{output_dir}/confidence_intervals.csv", index=False)
    
    # =========================================================================
    # STEP 9: Save Complete Results
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 9: SAVING RESULTS")
    print("="*70)
    
    # Save complete feature set with personas
    features.to_csv(f"{output_dir}/traders_with_personas.csv", index=False)
    print(f"✓ Saved complete results to: {output_dir}/traders_with_personas.csv")
    
    # Create summary report
    summary = {
        'total_traders': len(features),
        'num_personas_discovered': len(persona_names),
        'persona_names': persona_names,
        'avg_persona_confidence': features['persona_confidence'].mean(),
        'features_used': feature_columns,
        'clustering_metrics': clustering_metrics
    }
    
    # Save summary as JSON
    import json
    with open(f"{output_dir}/analysis_summary.json", 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"✓ Saved analysis summary to: {output_dir}/analysis_summary.json")
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE - SUMMARY")
    print("="*70)
    
    print(f"\n📊 Total Traders Analyzed: {len(features)}")
    print(f"🎯 Personas Discovered: {len(persona_names)}")
    print(f"✨ Average Persona Confidence: {features['persona_confidence'].mean():.2%}")
    
    print(f"\n📈 Persona Distribution:")
    for persona_name in persona_names:
        count = (features['persona'] == persona_name).sum()
        pct = (count / len(features)) * 100
        avg_pnl = features[features['persona'] == persona_name]['total_pnl'].mean()
        print(f"  • {persona_name}: {count} traders ({pct:.1f}%) - Avg PnL: ${avg_pnl:,.2f}")
    
    print(f"\n💾 All results saved to: {output_dir}/")
    print(f"\n🎉 Adaptive persona discovery complete!")
    print("="*70)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run adaptive persona discovery analysis'
    )
    parser.add_argument(
        '--data',
        type=str,
        default='../data/traders_202510140811.csv',
        help='Path to traders CSV file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='../outputs',
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    # Run analysis
    run_adaptive_analysis(args.data, args.output)
