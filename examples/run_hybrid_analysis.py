"""
Advanced Hybrid Analysis Pipeline

Production-grade trader analysis and ranking system for copy-trading recommendations.

Features:
- Hybrid classification (unsupervised + domain rules)
- Multi-factor quality scoring
- Risk-adjusted performance metrics
- Group-wise and overall rankings
- Validation and quality assurance
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import numpy as np
from trader_analysis.hybrid_persona_system import HybridPersonaSystem
from trader_analysis.evaluation import ModelEvaluator
from trader_analysis.visualization import Visualizer
from trader_analysis.hybrid_visualizer import HybridVisualizer


def prepare_trader_features(data_path: str) -> pd.DataFrame:
    """
    Prepare comprehensive feature set for trader analysis.
    
    Parameters:
    -----------
    data_path : str
        Path to traders CSV file
        
    Returns:
    --------
    pd.DataFrame
        Feature dataframe with all metrics
    """
    print("="*70)
    print("ADVANCED TRADER ANALYSIS & RANKING SYSTEM")
    print("="*70)
    print(f"\nData Source: {data_path}\n")
    
    # Load data
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} traders")
    
    # Filter bots
    if 'is_bot' in df.columns:
        original_count = len(df)
        df = df[df['is_bot'] == 0]
        print(f"Filtered out {original_count - len(df)} bots")
    
    # Handle missing values
    df = df.fillna(0)
    
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
    
    df = df.rename(columns=column_mapping)
    
    # Create derived features
    print("\nEngineering features...")
    
    # Profitability metrics
    df['avg_profit_per_trade'] = df['realized_pnl'] / df['total_trades'].replace(0, 1)
    df['loss_rate'] = df['losses'] / df['total_trades'].replace(0, 1)
    df['win_loss_ratio'] = df['wins'] / df['losses'].replace(0, 1)
    
    # Risk metrics
    df['profit_factor'] = np.where(
        df['losses'] > 0,
        df['wins'] / df['losses'],
        df['wins']  # If no losses, use wins count
    )
    
    # Handle edge cases where win_rate might be percentage-like values
    # Normalize to 0-100 range
    df['win_rate'] = df['win_rate'].clip(0, 100)
    
    # Volume metrics
    df['volume_per_trade'] = df['total_volume'] / df['total_trades'].replace(0, 1)
    
    # Replace infinities
    df = df.replace([np.inf, -np.inf], 0)
    
    # Ensure all numeric
    numeric_cols = ['total_pnl', 'realized_pnl', 'unrealized_pnl', 'roi', 'unrealized_roi',
                    'win_rate', 'wins', 'losses', 'total_volume', 'total_trades',
                    'avg_trade_size', 'avg_profit_per_trade', 'loss_rate',
                    'win_loss_ratio', 'profit_factor', 'volume_per_trade']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    print(f"[OK] Prepared {df.shape[1]} features for {df.shape[0]} traders\n")
    
    return df


def run_hybrid_analysis(data_path: str, output_dir: str = '../outputs'):
    """
    Run complete hybrid trader analysis and ranking.
    
    Parameters:
    -----------
    data_path : str
        Path to traders CSV file
    output_dir : str
        Directory to save outputs
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # =========================================================================
    # STEP 1: Prepare Data
    # =========================================================================
    features = prepare_trader_features(data_path)
    
    # Save prepared features
    features.to_csv(f"{output_dir}/prepared_features_hybrid.csv", index=False)
    
    # =========================================================================
    # STEP 2: Initialize Hybrid System
    # =========================================================================
    print("="*70)
    print("HYBRID PERSONA CLASSIFICATION")
    print("="*70)
    
    # Feature columns for classification
    feature_columns = [
        'total_pnl', 'realized_pnl', 'roi',
        'win_rate', 'wins', 'losses',
        'total_volume', 'total_trades', 'avg_trade_size',
        'avg_profit_per_trade', 'profit_factor', 'win_loss_ratio'
    ]
    
    # Filter to existing columns
    feature_columns = [col for col in feature_columns if col in features.columns]
    
    # Initialize system
    hybrid_system = HybridPersonaSystem(random_state=42)
    
    # Fit (learns patterns)
    hybrid_system.fit(features, feature_columns)
    
    # =========================================================================
    # STEP 3: Classify Traders
    # =========================================================================
    features = hybrid_system.classify_traders(features)
    
    # =========================================================================
    # STEP 4: Calculate Copy-Trading Scores
    # =========================================================================
    print("\n" + "="*70)
    print("COPY-TRADING SCORE CALCULATION")
    print("="*70)
    
    features = hybrid_system.calculate_copy_trading_score(features)
    
    # =========================================================================
    # STEP 5: Overall Rankings
    # =========================================================================
    print("\n" + "="*70)
    print("TOP TRADERS - OVERALL RANKINGS")
    print("="*70)
    
    top_50 = hybrid_system.get_top_traders(features, top_n=50)
    
    print(f"\nTop 50 Traders Across All Personas:")
    print(top_50[['address', 'persona', 'copy_trading_score', 'total_pnl', 
                   'roi', 'win_rate', 'total_trades']].head(20).to_string())
    
    # Save overall rankings
    top_50.to_csv(f"{output_dir}/top_50_traders_overall.csv", index=False)
    print(f"\n[OK] Saved top 50 traders to: {output_dir}/top_50_traders_overall.csv")
    
    # =========================================================================
    # STEP 6: Persona-Specific Rankings
    # =========================================================================
    print("\n" + "="*70)
    print("TOP TRADERS BY PERSONA")
    print("="*70)
    
    persona_rankings = hybrid_system.get_persona_rankings(features, top_n_per_persona=10)
    
    for persona_name, top_traders in persona_rankings.items():
        if len(top_traders) > 0:
            print(f"\n{'='*70}")
            print(f"{persona_name.upper()} - Top 10 Traders")
            print(f"{'='*70}")
            print(top_traders[['address', 'copy_trading_score', 'total_pnl',
                              'roi', 'win_rate', 'total_trades']].to_string())
            
            # Save persona rankings
            filename = f"{output_dir}/top_10_{persona_name.replace(' ', '_')}.csv"
            top_traders.to_csv(filename, index=False)
            print(f"\n[OK] Saved to: {filename}")
    
    # =========================================================================
    # STEP 7: Quality Analysis
    # =========================================================================
    print("\n" + "="*70)
    print("QUALITY ANALYSIS")
    print("="*70)
    
    # Persona quality statistics
    persona_stats = features[features['persona'] != 'Unclassified'].groupby('persona').agg({
        'copy_trading_score': ['mean', 'median', 'std', 'min', 'max'],
        'quality_score': ['mean', 'median'],
        'profitability_score': 'mean',
        'risk_adjusted_score': 'mean',
        'consistency_score': 'mean',
        'total_pnl': 'mean',
        'win_rate': 'mean',
        'address': 'count'
    }).round(3)
    
    persona_stats.columns = ['_'.join(col).strip() for col in persona_stats.columns.values]
    persona_stats = persona_stats.rename(columns={'address_count': 'trader_count'})
    
    print("\nPersona Quality Statistics:")
    print(persona_stats.to_string())
    
    persona_stats.to_csv(f"{output_dir}/persona_quality_statistics.csv")
    
    # =========================================================================
    # STEP 8: High-Confidence Recommendations
    # =========================================================================
    print("\n" + "="*70)
    print("HIGH-CONFIDENCE COPY-TRADING RECOMMENDATIONS")
    print("="*70)
    
    # Filter for high-quality traders
    high_confidence = features[
        (features['persona'] != 'Unclassified') &
        (features['copy_trading_score'] >= 0.6) &
        (features['validation_passed'] == True) &
        (features['total_trades'] >= 20)  # Minimum track record
    ].copy()
    
    high_confidence = high_confidence.sort_values('copy_trading_score', ascending=False)
    
    print(f"\nFound {len(high_confidence)} high-confidence traders")
    print(f"  (Score >= 0.6, Validation passed, 20+ trades)\n")
    
    if len(high_confidence) > 0:
        print("Top 20 High-Confidence Recommendations:")
        print(high_confidence[['address', 'persona', 'copy_trading_score',
                               'quality_score', 'total_pnl', 'roi', 'win_rate',
                               'total_trades', 'profit_factor']].head(20).to_string())
        
        high_confidence.to_csv(f"{output_dir}/high_confidence_recommendations.csv", index=False)
        print(f"\n[OK] Saved high-confidence traders to: {output_dir}/high_confidence_recommendations.csv")
    
    # =========================================================================
    # STEP 9: Risk Categories
    # =========================================================================
    print("\n" + "="*70)
    print("RISK-CATEGORIZED RECOMMENDATIONS")
    print("="*70)
    
    # Categorize by risk profile
    def categorize_risk(row):
        if row['persona'] == 'Elite Sniper':
            return 'Low Risk'
        elif row['persona'] in ['Consistent Performer', 'Scalper']:
            return 'Medium Risk'
        elif row['persona'] in ['Whale', 'Momentum Trader']:
            return 'Medium-High Risk'
        else:
            return 'High Risk'
    
    features['risk_category'] = features.apply(categorize_risk, axis=1)
    
    # Top traders by risk category
    for risk_cat in ['Low Risk', 'Medium Risk', 'Medium-High Risk']:
        risk_traders = features[
            (features['risk_category'] == risk_cat) &
            (features['validation_passed'] == True)
        ].nlargest(10, 'copy_trading_score')
        
        if len(risk_traders) > 0:
            print(f"\n{risk_cat} - Top 10:")
            print(risk_traders[['address', 'persona', 'copy_trading_score',
                               'total_pnl', 'roi', 'win_rate']].to_string())
            
            filename = f"{output_dir}/top_10_{risk_cat.replace(' ', '_').lower()}.csv"
            risk_traders.to_csv(filename, index=False)
    
    # =========================================================================
    # STEP 10: Generate Advanced Visualizations
    # =========================================================================
    print("\n" + "="*70)
    print("GENERATING ADVANCED VISUALIZATIONS")
    print("="*70)
    
    # Initialize visualizers
    visualizer = Visualizer(output_dir)
    hybrid_viz = HybridVisualizer(output_dir)
    
    # 1. Persona quality matrix
    print("\n1. Creating persona quality matrix...")
    hybrid_viz.plot_persona_quality_matrix(
        features,
        save_path=f"{output_dir}/persona_quality_matrix.png"
    )
    
    # 2. Follow-worthiness rankings
    print("2. Creating follow-worthiness rankings...")
    hybrid_viz.plot_follow_worthiness_rankings(
        features,
        top_n=30,
        save_path=f"{output_dir}/follow_worthiness_rankings.png"
    )
    
    # 3. Persona characteristics radar charts
    print("3. Creating persona characteristic radar charts...")
    hybrid_viz.plot_persona_characteristics_radar(
        features,
        save_path=f"{output_dir}/persona_characteristics_radar.png"
    )
    
    # 4. Confidence vs performance analysis
    print("4. Creating confidence vs performance analysis...")
    hybrid_viz.plot_confidence_vs_performance(
        features,
        save_path=f"{output_dir}/confidence_vs_performance.png"
    )
    
    # 5. Comprehensive dashboard
    print("5. Creating comprehensive dashboard...")
    hybrid_viz.create_comprehensive_dashboard(
        features,
        save_path=f"{output_dir}/comprehensive_dashboard.png"
    )
    
    # 6. Traditional visualizations
    print("6. Creating traditional visualizations...")
    visualizer.plot_persona_distribution(
        features,
        save_path=f"{output_dir}/persona_distribution.png"
    )
    
    visualizer.plot_performance_by_persona(
        features,
        metric='total_pnl',
        save_path=f"{output_dir}/performance_by_persona.png"
    )
    
    print("\n[OK] All visualizations generated successfully!")
    
    # =========================================================================
    # STEP 11: Save Complete Results
    # =========================================================================
    print("\n" + "="*70)
    print("SAVING COMPLETE RESULTS")
    print("="*70)
    
    # Save all features with classifications and scores
    features.to_csv(f"{output_dir}/complete_trader_analysis.csv", index=False)
    print(f"\n[OK] Complete analysis saved to: {output_dir}/complete_trader_analysis.csv")
    
    # Create summary report
    summary = {
        'total_traders_analyzed': len(features),
        'classified_traders': len(features[features['persona'] != 'Unclassified']),
        'unclassified_traders': len(features[features['persona'] == 'Unclassified']),
        'high_confidence_count': len(high_confidence),
        'personas_discovered': features[features['persona'] != 'Unclassified']['persona'].nunique(),
        'avg_copy_trading_score': features[features['persona'] != 'Unclassified']['copy_trading_score'].mean(),
        'top_trader_address': top_50.iloc[0]['address'] if len(top_50) > 0 else None,
        'top_trader_score': top_50.iloc[0]['copy_trading_score'] if len(top_50) > 0 else 0
    }
    
    # Save summary
    import json
    with open(f"{output_dir}/analysis_summary_hybrid.json", 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"[OK] Summary saved to: {output_dir}/analysis_summary_hybrid.json")
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE - FINAL SUMMARY")
    print("="*70)
    
    print(f"\n[STATS] Total Traders: {summary['total_traders_analyzed']}")
    print(f"[STATS] Successfully Classified: {summary['classified_traders']} ({summary['classified_traders']/summary['total_traders_analyzed']*100:.1f}%)")
    print(f"[STATS] Unclassified: {summary['unclassified_traders']} ({summary['unclassified_traders']/summary['total_traders_analyzed']*100:.1f}%)")
    print(f"[STATS] High-Confidence Recommendations: {summary['high_confidence_count']}")
    print(f"[STATS] Average Copy-Trading Score: {summary['avg_copy_trading_score']:.3f}")
    
    print(f"\n[PERSONAS] Persona Distribution:")
    persona_dist = features[features['persona'] != 'Unclassified']['persona'].value_counts()
    for persona, count in persona_dist.items():
        pct = (count / summary['classified_traders']) * 100
        avg_score = features[features['persona'] == persona]['copy_trading_score'].mean()
        print(f"  - {persona}: {count} traders ({pct:.1f}%) - Avg Score: {avg_score:.3f}")
    
    print(f"\n[TOP] Top Trader: {summary['top_trader_address']}")
    print(f"[TOP] Copy-Trading Score: {summary['top_trader_score']:.3f}")
    
    print(f"\n💾 All results saved to: {output_dir}/")
    print("\n🎉 Hybrid analysis complete!")
    print("="*70)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run hybrid trader analysis and ranking'
    )
    parser.add_argument(
        '--data',
        type=str,
        default='data/traders_202510140811.csv',
        help='Path to traders CSV file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='outputs',
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    # Run analysis
    run_hybrid_analysis(args.data, args.output)
