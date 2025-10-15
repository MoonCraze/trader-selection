"""
Complete Analysis Pipeline

End-to-end demonstration of the trader selection framework.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import numpy as np
from trader_analysis import (
    FeatureEngineer,
    TraderSegmentation,
    HighPotentialPredictor,
    PersonaAssigner,
    ModelEvaluator
)
from trader_analysis.visualization import Visualizer


def run_complete_analysis(data_path: str, output_dir: str = '../outputs'):
    """
    Run complete trader analysis pipeline.
    
    Parameters:
    -----------
    data_path : str
        Path to transaction data CSV
    output_dir : str
        Directory to save outputs
    """
    print("="*70)
    print("TRADER SELECTION FRAMEWORK - COMPLETE ANALYSIS PIPELINE")
    print("="*70)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # =========================================================================
    # STEP 1: Load Data
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 1: Loading Transaction Data")
    print("="*70)
    
    df = pd.read_csv(data_path)
    print(f"\nLoaded {len(df)} transactions from {df['address'].nunique()} unique addresses")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # =========================================================================
    # STEP 2: Feature Engineering
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 2: Feature Engineering")
    print("="*70)
    
    engineer = FeatureEngineer(recency_decay=0.1)
    features = engineer.engineer_features(df)
    
    print(f"\nFeature Matrix Shape: {features.shape}")
    print(f"Features: {', '.join(engineer.get_feature_names()[:10])}...")
    
    # Save features
    features.to_csv(f"{output_dir}/engineered_features.csv", index=False)
    print(f"\nFeatures saved to: {output_dir}/engineered_features.csv")
    
    # =========================================================================
    # STEP 3: Clustering Analysis
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 3: Clustering Analysis")
    print("="*70)
    
    # Prepare features for clustering
    feature_cols = [col for col in features.columns if col != 'address']
    X = features[feature_cols].values
    
    # K-Means clustering
    clusterer = TraderSegmentation(random_state=42)
    clusterer.fit_kmeans(X, optimize_k=True)
    
    # Evaluate clustering
    clustering_metrics = clusterer.evaluate_clustering(X)
    
    # Get cluster statistics
    features['cluster'] = clusterer.labels_
    cluster_stats = clusterer.get_cluster_statistics(features)
    print("\nCluster Statistics:")
    print(cluster_stats[['cluster_id', 'size', 'percentage', 'mean_total_pnl', 'mean_win_rate']].to_string())
    
    cluster_stats.to_csv(f"{output_dir}/cluster_statistics.csv", index=False)
    
    # Visualize clusters
    visualizer = Visualizer(output_dir)
    features_2d = clusterer.reduce_dimensions_for_visualization(X)
    visualizer.plot_cluster_scatter(
        features_2d, 
        clusterer.labels_,
        save_path=f"{output_dir}/cluster_visualization.png"
    )
    
    # =========================================================================
    # STEP 4: Persona Assignment
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 4: Persona Assignment")
    print("="*70)
    
    persona_assigner = PersonaAssigner()
    features = persona_assigner.assign_personas(features)
    
    # Get persona statistics
    persona_stats = persona_assigner.get_persona_statistics(features)
    print("\nPersona Performance Statistics:")
    print(persona_stats.to_string())
    
    persona_stats.to_csv(f"{output_dir}/persona_statistics.csv", index=False)
    
    # Visualize personas
    visualizer.plot_persona_distribution(features, save_path=f"{output_dir}/persona_distribution.png")
    visualizer.plot_performance_by_persona(
        features, 
        metric='total_pnl',
        save_path=f"{output_dir}/performance_by_persona.png"
    )
    
    # Get top traders by persona
    top_traders = persona_assigner.get_top_traders_by_persona(features, top_n=5)
    print("\nTop 5 Traders per Persona:")
    for persona, traders_df in top_traders.items():
        if len(traders_df) > 0:
            print(f"\n{persona}:")
            print(traders_df[['address', 'weighted_pnl', 'roi', 'win_rate']].to_string())
    
    # =========================================================================
    # STEP 5: Predictive Modeling - Persona Type Prediction
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 5A: Predictive Modeling - Persona Type Prediction")
    print("="*70)
    
    # Check if we have true archetype labels (from sample data)
    if 'true_archetype' in df.columns:
        print("\nDetected true archetype labels in data. Training persona predictor...")
        
        # Create persona-based features with true labels
        df_with_labels = df.copy()
        features_with_labels = features.merge(
            df_with_labels[['address', 'true_archetype']].drop_duplicates('address'),
            on='address',
            how='left'
        )
        
        # Only use samples with labels
        features_with_labels = features_with_labels[features_with_labels['true_archetype'].notna()]
        
        if len(features_with_labels) > 0:
            persona_predictor = HighPotentialPredictor(random_state=42, use_smote=True, prediction_type='persona')
            
            # Create persona target labels
            persona_target = persona_predictor.create_persona_target_labels(
                features_with_labels,
                persona_column='true_archetype'
            )
            
            # Prepare data (exclude persona columns and true labels)
            features_for_persona_pred = features_with_labels.drop(
                ['persona', 'persona_confidence', 'persona_description', 'cluster', 'true_archetype'], 
                axis=1, errors='ignore'
            )
            
            X_train_p, X_test_p, y_train_p, y_test_p = persona_predictor.prepare_data(
                features_for_persona_pred,
                persona_target,
                test_size=0.2
            )
            
            # Train ensemble for persona prediction
            persona_predictor.train_ensemble(X_train_p, y_train_p)
            
            # Evaluate
            persona_metrics = persona_predictor.evaluate(X_test_p, y_test_p)
            
            # Feature importance for persona prediction
            persona_importance_df = persona_predictor.get_feature_importance()
            print("\nTop 10 Most Important Features for Persona Prediction:")
            print(persona_importance_df.head(10).to_string())
            
            persona_importance_df.to_csv(f"{output_dir}/persona_prediction_feature_importance.csv", index=False)
            visualizer.plot_feature_importance(
                persona_importance_df,
                top_n=15,
                save_path=f"{output_dir}/persona_prediction_feature_importance.png"
            )
            
            # Predict personas on all data
            features_for_all_pred = features.drop(
                ['persona', 'persona_confidence', 'persona_description', 'cluster'], 
                axis=1, errors='ignore'
            )
            X_all_p = features_for_all_pred[[col for col in features_for_all_pred.columns if col != 'address']].values
            X_all_p_scaled = persona_predictor.scaler.transform(X_all_p)
            
            # Get predictions
            predicted_persona_idx = persona_predictor.predict(X_all_p_scaled)
            predicted_persona_proba = persona_predictor.predict_proba_ensemble(X_all_p_scaled)
            
            # Map back to persona names
            predicted_personas = [persona_predictor.persona_labels_[idx] for idx in predicted_persona_idx]
            predicted_persona_confidence = np.max(predicted_persona_proba, axis=1)
            
            features['predicted_persona'] = predicted_personas
            features['predicted_persona_confidence'] = predicted_persona_confidence
            
            # Get probability for each persona class
            for i, persona_name in enumerate(persona_predictor.persona_labels_):
                features[f'persona_prob_{persona_name}'] = predicted_persona_proba[:, i]
            
            print(f"\nPersona Prediction Summary:")
            pred_persona_counts = pd.Series(predicted_personas).value_counts()
            for persona, count in pred_persona_counts.items():
                pct = count / len(predicted_personas) * 100
                print(f"  {persona}: {count} traders ({pct:.1f}%)")
            
            # Save predictions
            persona_predictions = features[['address', 'predicted_persona', 'predicted_persona_confidence'] + 
                                          [col for col in features.columns if col.startswith('persona_prob_')]]
            persona_predictions.to_csv(f"{output_dir}/persona_predictions.csv", index=False)
            print(f"\nPersona predictions saved to: {output_dir}/persona_predictions.csv")
            
            # Compare predicted vs rule-based personas
            if 'persona' in features.columns:
                comparison = pd.DataFrame({
                    'address': features['address'],
                    'rule_based_persona': features['persona'],
                    'predicted_persona': features['predicted_persona'],
                    'rule_based_confidence': features['persona_confidence'],
                    'predicted_confidence': features['predicted_persona_confidence']
                })
                
                # Calculate agreement
                agreement = (comparison['rule_based_persona'] == comparison['predicted_persona']).sum()
                agreement_pct = agreement / len(comparison) * 100
                print(f"\nRule-based vs ML Prediction Agreement: {agreement_pct:.1f}%")
                
                comparison.to_csv(f"{output_dir}/persona_comparison.csv", index=False)
    else:
        print("\nNo true archetype labels found in data. Skipping persona prediction.")
    
    # =========================================================================
    # STEP 5B: Binary High-Potential Prediction (Original Method)
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 5B: Predictive Modeling for High-Potential Traders")
    print("="*70)
    
    predictor = HighPotentialPredictor(random_state=42, use_smote=True)
    
    # Create target labels
    target = predictor.create_target_labels(
        features,
        top_percentile=0.2,
        min_trades=10
    )
    
    # Prepare data (exclude persona columns)
    cols_to_drop = ['persona', 'persona_confidence', 'persona_description', 'cluster', 
                    'predicted_persona', 'predicted_persona_confidence', 'true_archetype']
    cols_to_drop += [col for col in features.columns if col.startswith('persona_prob_')]
    features_for_prediction = features.drop(cols_to_drop, axis=1, errors='ignore')
    X_train, X_test, y_train, y_test = predictor.prepare_data(
        features_for_prediction,
        target,
        test_size=0.2
    )
    
    # Train ensemble
    predictor.train_ensemble(X_train, y_train)
    
    # Evaluate
    prediction_metrics = predictor.evaluate(X_test, y_test)
    
    # Feature importance
    importance_df = predictor.get_feature_importance()
    print("\nTop 10 Most Important Features:")
    print(importance_df.head(10).to_string())
    
    importance_df.to_csv(f"{output_dir}/feature_importance.csv", index=False)
    visualizer.plot_feature_importance(
        importance_df,
        top_n=15,
        save_path=f"{output_dir}/feature_importance.png"
    )
    
    # Predict on all data
    cols_to_drop = ['persona', 'persona_confidence', 'persona_description', 'cluster',
                    'predicted_persona', 'predicted_persona_confidence', 'true_archetype']
    cols_to_drop += [col for col in features.columns if col.startswith('persona_prob_')]
    features_for_prediction = features.drop(cols_to_drop, axis=1, errors='ignore')
    X_all = features_for_prediction[[col for col in features_for_prediction.columns if col != 'address']].values
    X_all_scaled = predictor.scaler.transform(X_all)
    high_potential_proba = predictor.predict_proba_ensemble(X_all_scaled)[:, 1]
    features['high_potential_score'] = high_potential_proba
    features['high_potential'] = predictor.predict(X_all_scaled)
    
    # =========================================================================
    # STEP 6: Statistical Validation
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 6: Statistical Validation")
    print("="*70)
    
    evaluator = ModelEvaluator(confidence_level=0.95)
    
    # Compare personas statistically
    persona_comparison = evaluator.compare_personas(features, metric='total_pnl')
    persona_comparison.to_csv(f"{output_dir}/persona_comparison.csv", index=False)
    
    # Confidence intervals
    confidence_intervals = evaluator.calculate_confidence_intervals(features, metric='total_pnl')
    print("\nConfidence Intervals for Total PNL by Persona:")
    print(confidence_intervals[['persona', 'mean', 'ci_lower', 'ci_upper']].to_string())
    
    # Correlation analysis
    correlation_matrix = evaluator.perform_feature_correlation_analysis(features)
    visualizer.plot_correlation_matrix(
        correlation_matrix,
        save_path=f"{output_dir}/correlation_matrix.png"
    )
    
    # =========================================================================
    # STEP 7: Select High-Potential Traders
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 7: Final Selection of High-Potential Traders")
    print("="*70)
    
    # Select high-potential traders
    high_potential_traders = features[features['high_potential'] == 1].copy()
    high_potential_traders = high_potential_traders.sort_values('high_potential_score', ascending=False)
    
    print(f"\nIdentified {len(high_potential_traders)} high-potential traders")
    
    # Portfolio metrics
    portfolio_metrics = evaluator.calculate_portfolio_metrics(high_potential_traders)
    
    # Save high-potential traders
    high_potential_traders.to_csv(f"{output_dir}/high_potential_traders.csv", index=False)
    print(f"\nHigh-potential traders saved to: {output_dir}/high_potential_traders.csv")
    
    # Top 20 traders
    print("\nTop 20 High-Potential Traders:")
    top_20 = high_potential_traders.head(20)[
        ['address', 'persona', 'high_potential_score', 'weighted_pnl', 
         'roi', 'win_rate', 'sharpe_ratio', 'total_trades']
    ]
    print(top_20.to_string())
    
    top_20.to_csv(f"{output_dir}/top_20_traders.csv", index=False)
    
    # =========================================================================
    # STEP 8: Generate Comprehensive Report
    # =========================================================================
    print("\n" + "="*70)
    print("STEP 8: Generate Comprehensive Report")
    print("="*70)
    
    report = evaluator.generate_evaluation_report(
        features,
        clustering_metrics,
        prediction_metrics
    )
    
    # Create summary dashboard
    visualizer.create_summary_dashboard(
        features,
        save_path=f"{output_dir}/summary_dashboard.png"
    )
    
    # Save all features with analysis results
    features.to_csv(f"{output_dir}/complete_analysis_results.csv", index=False)
    print(f"\nComplete analysis results saved to: {output_dir}/complete_analysis_results.csv")
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE - SUMMARY")
    print("="*70)
    print(f"\nTotal Wallets Analyzed: {len(features)}")
    print(f"Total Transactions: {len(df)}")
    print(f"Clusters Identified: {len(features['cluster'].unique())}")
    print(f"Personas Assigned: {len(features['persona'].unique())}")
    print(f"High-Potential Traders: {len(high_potential_traders)}")
    print(f"\nPersona Breakdown of High-Potential Traders:")
    hp_persona_dist = high_potential_traders['persona'].value_counts()
    for persona, count in hp_persona_dist.items():
        print(f"  {persona}: {count} traders")
    
    print(f"\nAll outputs saved to: {output_dir}/")
    print("="*70)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run complete trader analysis pipeline')
    parser.add_argument(
        '--data',
        type=str,
        default='../data/traders_202510140811.csv',
        help='Path to transaction data CSV'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='../outputs',
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    # Run analysis
    run_complete_analysis(args.data, args.output)
