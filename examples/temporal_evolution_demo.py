"""
Temporal Evolution Analysis Example

Demonstrates persona evolution tracking over time.
Shows how traders transition between personas and identifies career paths.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from trader_analysis import TemporalEvolutionTracker


def simulate_temporal_data(features_df: pd.DataFrame, n_timepoints: int = 5) -> pd.DataFrame:
    """
    Simulate temporal persona data for demonstration.
    
    In a real scenario, this would come from historical snapshots.
    
    Parameters:
    -----------
    features_df : pd.DataFrame
        Current feature dataframe with personas
    n_timepoints : int
        Number of historical timepoints to simulate
        
    Returns:
    --------
    pd.DataFrame
        Temporal persona data
    """
    temporal_data = []
    
    # Create timestamps
    current_date = datetime.now()
    
    for i in range(n_timepoints):
        # Go back in time
        timestamp = current_date - timedelta(days=30 * (n_timepoints - i))
        
        for _, row in features_df.iterrows():
            # Simulate some persona changes (20% chance of change per period)
            if i > 0 and np.random.random() < 0.2:
                # Random persona change
                available_personas = features_df['persona'].unique()
                new_persona = np.random.choice(available_personas)
            else:
                new_persona = row['persona']
            
            temporal_data.append({
                'wallet_address': row['address'],
                'timestamp': timestamp,
                'persona': new_persona,
                'total_pnl': row['total_pnl'] * (0.7 + i * 0.1),  # Simulate growth
                'win_rate': row['win_rate'],
                'total_trades': row['total_trades'] * (i + 1) // n_timepoints
            })
    
    return pd.DataFrame(temporal_data)


def run_temporal_analysis(features_path: str):
    """
    Run temporal evolution analysis.
    
    Parameters:
    -----------
    features_path : str
        Path to features CSV with personas
    """
    print("="*70)
    print("TEMPORAL EVOLUTION ANALYSIS")
    print("="*70)
    
    # Load features with personas
    features = pd.read_csv(features_path)
    print(f"\nLoaded {len(features)} traders with assigned personas")
    
    if 'persona' not in features.columns:
        print("ERROR: Personas not found. Run complete_adaptive_analysis.py first.")
        return
    
    # Simulate temporal data (in production, use real historical data)
    print("\nSimulating temporal persona data...")
    temporal_data = simulate_temporal_data(features, n_timepoints=6)
    print(f"Created {len(temporal_data)} temporal observations")
    
    # Initialize tracker
    tracker = TemporalEvolutionTracker(time_window_days=45)
    
    # =========================================================================
    # Transition Matrix
    # =========================================================================
    print("\n" + "="*70)
    print("TRANSITION PROBABILITY MATRIX")
    print("="*70)
    
    transition_matrix = tracker.calculate_transition_matrix(
        temporal_data,
        persona_column='persona',
        timestamp_column='timestamp',
        trader_id_column='wallet_address'
    )
    
    # =========================================================================
    # Career Paths
    # =========================================================================
    print("\n" + "="*70)
    print("CAREER PATH ANALYSIS")
    print("="*70)
    
    career_paths = tracker.identify_career_paths(
        temporal_data,
        persona_column='persona',
        timestamp_column='timestamp',
        trader_id_column='wallet_address',
        min_path_frequency=2
    )
    
    # =========================================================================
    # Lifecycle Stages
    # =========================================================================
    print("\n" + "="*70)
    print("LIFECYCLE STAGE DETECTION")
    print("="*70)
    
    lifecycle_stages = tracker.detect_lifecycle_stage(
        temporal_data,
        trader_id_column='wallet_address',
        timestamp_column='timestamp',
        activity_column='total_trades'
    )
    
    # =========================================================================
    # Persona Stability
    # =========================================================================
    print("\n" + "="*70)
    print("PERSONA STABILITY ANALYSIS")
    print("="*70)
    
    stability = tracker.calculate_persona_stability(
        temporal_data,
        persona_column='persona',
        timestamp_column='timestamp',
        trader_id_column='wallet_address'
    )
    
    print("\nMost Stable Traders:")
    print(stability.nlargest(10, 'stability_score')[
        ['wallet_address', 'dominant_persona', 'stability_score', 'num_transitions']
    ].to_string())
    
    print("\nMost Volatile Traders:")
    print(stability.nsmallest(10, 'stability_score')[
        ['wallet_address', 'dominant_persona', 'stability_score', 'num_transitions']
    ].to_string())
    
    # =========================================================================
    # Predictions
    # =========================================================================
    print("\n" + "="*70)
    print("NEXT PERSONA PREDICTIONS")
    print("="*70)
    
    # Get summary
    summary = tracker.get_transition_summary()
    
    print(f"\nMost Stable Persona: {summary['most_stable_persona']}")
    print(f"  (Self-transition probability: {summary['stability_score']:.2%})")
    
    print(f"\nMost Volatile Persona: {summary['most_volatile_persona']}")
    print(f"  (Volatility score: {summary['volatility_score']:.2%})")
    
    print(f"\nTop 5 Most Common Transitions:")
    for from_p, to_p, prob in summary['common_transitions'][:5]:
        print(f"  {from_p} → {to_p}: {prob:.2%}")
    
    # Example predictions
    personas = features['persona'].unique()[:3]
    print(f"\nPredicted Next Personas:")
    for persona in personas:
        try:
            predictions = tracker.predict_next_persona(persona, confidence_threshold=0.15)
            print(f"\n  Current: {persona}")
            for next_persona, prob in predictions[:3]:
                print(f"    → {next_persona}: {prob:.2%}")
        except:
            pass
    
    print("\n" + "="*70)
    print("TEMPORAL ANALYSIS COMPLETE")
    print("="*70)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run temporal evolution analysis'
    )
    parser.add_argument(
        '--features',
        type=str,
        default='../outputs/traders_with_personas.csv',
        help='Path to features CSV with personas'
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.features):
        print(f"ERROR: File not found: {args.features}")
        print("Please run complete_adaptive_analysis.py first.")
    else:
        run_temporal_analysis(args.features)
