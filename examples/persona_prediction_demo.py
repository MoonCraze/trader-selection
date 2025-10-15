"""
Persona Prediction Demo

Demonstrates the new multi-class persona prediction capability.
This script shows how to train a model to predict trader personas
based on trading behavior features.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import numpy as np
from trader_analysis import FeatureEngineer, HighPotentialPredictor


def run_persona_prediction_demo(data_path: str = '../data/traders_202510140811.csv'):
    """
    Run a simple demonstration of persona prediction.
    
    Parameters:
    -----------
    data_path : str
        Path to transaction data CSV with true_archetype labels
    """
    print("="*70)
    print("PERSONA PREDICTION DEMONSTRATION")
    print("="*70)
    
    # Load data
    print("\n1. Loading transaction data...")
    df = pd.read_csv(data_path)
    print(f"   Loaded {len(df)} transactions from {df['address'].nunique()} addresses")
    
    # Check for true labels
    if 'true_archetype' not in df.columns:
        print("\n   ERROR: No 'true_archetype' column found!")
        return
    
    # Feature engineering
    print("\n2. Engineering features...")
    engineer = FeatureEngineer(recency_decay=0.1)
    features = engineer.engineer_features(df)
    print(f"   Created {len(engineer.get_feature_names())} features")
    
    # Add true labels to features
    df_labels = df[['address', 'true_archetype']].drop_duplicates('address')
    features = features.merge(df_labels, on='address', how='left')
    features = features[features['true_archetype'].notna()]
    
    print(f"\n   Personas in dataset:")
    for persona, count in features['true_archetype'].value_counts().items():
        pct = count / len(features) * 100
        print(f"   - {persona}: {count} traders ({pct:.1f}%)")
    
    # Initialize predictor for persona classification
    print("\n3. Training persona prediction model...")
    predictor = HighPotentialPredictor(
        random_state=42, 
        use_smote=True, 
        prediction_type='persona'
    )
    
    # Create persona target labels
    target = predictor.create_persona_target_labels(features)
    
    # Prepare data
    features_for_training = features.drop(['true_archetype'], axis=1, errors='ignore')
    X_train, X_test, y_train, y_test = predictor.prepare_data(
        features_for_training,
        target,
        test_size=0.2
    )
    
    # Train model
    predictor.train_ensemble(X_train, y_train)
    
    # Evaluate
    print("\n4. Evaluating model performance...")
    metrics = predictor.evaluate(X_test, y_test)
    
    # Feature importance
    print("\n5. Most important features for persona prediction:")
    importance_df = predictor.get_feature_importance()
    print(importance_df.head(10).to_string(index=False))
    
    # Make predictions on test set
    print("\n6. Example predictions:")
    print("-" * 70)
    
    # Get predictions and probabilities for first 5 examples
    num_examples = min(5, len(X_test))
    X_sample = X_test[:num_examples]
    y_sample = y_test[:num_examples]
    
    predictions = predictor.predict(X_sample)
    probabilities = predictor.predict_proba_ensemble(X_sample)
    
    # Show examples
    for i in range(num_examples):
        true_label = y_sample[i]
        pred_label = predictions[i]
        
        # Validate indices are within range
        if true_label < 0 or true_label >= len(predictor.persona_labels_):
            print(f"? Invalid true label index: {true_label}")
            continue
        if pred_label < 0 or pred_label >= len(predictor.persona_labels_):
            print(f"? Invalid predicted label index: {pred_label}")
            continue
            
        true_persona = predictor.persona_labels_[true_label]
        pred_persona = predictor.persona_labels_[pred_label]
        confidence = probabilities[i, pred_label]
        
        match = "✓" if true_label == pred_label else "✗"
        print(f"{match} True: {true_persona:15s} | Predicted: {pred_persona:15s} (confidence: {confidence:.2%})")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("- Multi-class classification can predict trader personas from behavior")
    print(f"- Model achieved {metrics['accuracy']:.1%} accuracy on test set")
    print("- Most important features:", ', '.join(importance_df['feature'].head(3).tolist()))
    print("\nTo use in production:")
    print("  1. Train on larger, more diverse dataset")
    print("  2. Regularly retrain as market conditions change")
    print("  3. Use predictions to supplement or replace rule-based assignment")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Demonstrate persona prediction')
    parser.add_argument('--data', default='..data/traders_202510140811.csv',
                       help='Path to transaction data CSV')
    args = parser.parse_args()
    
    run_persona_prediction_demo(args.data)
