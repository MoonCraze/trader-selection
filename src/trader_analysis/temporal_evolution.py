"""
Temporal Evolution Tracking Module

Tracks how traders evolve across personas over time, analyzing career paths,
transition probabilities, and lifecycle stages.

Key Features:
- Transition probability matrices between personas
- Career path analysis and common progression patterns
- Trader trajectory modeling and prediction
- Lifecycle stage detection
- Temporal stability metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')


class TemporalEvolutionTracker:
    """
    Track and analyze how traders evolve across personas over time.
    
    This module provides insights into:
    - Which personas traders typically transition to/from
    - Common career progression paths
    - Lifecycle stages (early, growth, mature, decline)
    - Prediction of future persona changes
    """
    
    def __init__(self, time_window_days: int = 30):
        """
        Initialize TemporalEvolutionTracker.
        
        Parameters:
        -----------
        time_window_days : int
            Time window for calculating transitions (default: 30 days)
        """
        self.time_window_days = time_window_days
        self.transition_matrix_ = None
        self.career_paths_ = None
        self.lifecycle_stages_ = None
        self.persona_names_ = None
        
    def calculate_transition_matrix(self, historical_personas: pd.DataFrame,
                                   persona_column: str = 'persona',
                                   timestamp_column: str = 'timestamp',
                                   trader_id_column: str = 'wallet_address') -> pd.DataFrame:
        """
        Calculate transition probability matrix between personas.
        
        Parameters:
        -----------
        historical_personas : pd.DataFrame
            DataFrame with historical persona assignments over time
            Columns: [trader_id, timestamp, persona]
        persona_column : str
            Name of persona column
        timestamp_column : str
            Name of timestamp column
        trader_id_column : str
            Name of trader ID column
            
        Returns:
        --------
        pd.DataFrame
            Transition probability matrix
        """
        df = historical_personas.copy()
        df[timestamp_column] = pd.to_datetime(df[timestamp_column])
        df = df.sort_values([trader_id_column, timestamp_column])
        
        # Get unique personas
        self.persona_names_ = sorted(df[persona_column].unique())
        n_personas = len(self.persona_names_)
        
        # Initialize transition count matrix
        transition_counts = np.zeros((n_personas, n_personas))
        persona_to_idx = {p: i for i, p in enumerate(self.persona_names_)}
        
        # Count transitions
        for trader_id, group in df.groupby(trader_id_column):
            group = group.sort_values(timestamp_column)
            
            # Get consecutive persona pairs
            for i in range(len(group) - 1):
                from_persona = group.iloc[i][persona_column]
                to_persona = group.iloc[i + 1][persona_column]
                
                # Check if within time window
                time_diff = (group.iloc[i + 1][timestamp_column] - 
                           group.iloc[i][timestamp_column]).days
                
                if time_diff <= self.time_window_days:
                    from_idx = persona_to_idx[from_persona]
                    to_idx = persona_to_idx[to_persona]
                    transition_counts[from_idx, to_idx] += 1
        
        # Convert to probabilities
        row_sums = transition_counts.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        transition_probs = transition_counts / row_sums
        
        # Create DataFrame
        self.transition_matrix_ = pd.DataFrame(
            transition_probs,
            index=self.persona_names_,
            columns=self.persona_names_
        )
        
        print("\n✓ Transition Probability Matrix:")
        print(self.transition_matrix_.round(3))
        
        return self.transition_matrix_
    
    def identify_career_paths(self, historical_personas: pd.DataFrame,
                             persona_column: str = 'persona',
                             timestamp_column: str = 'timestamp',
                             trader_id_column: str = 'wallet_address',
                             min_path_frequency: int = 3) -> pd.DataFrame:
        """
        Identify common career progression paths across personas.
        
        Parameters:
        -----------
        historical_personas : pd.DataFrame
            DataFrame with historical persona assignments
        persona_column : str
            Name of persona column
        timestamp_column : str
            Name of timestamp column
        trader_id_column : str
            Name of trader ID column
        min_path_frequency : int
            Minimum number of traders to consider a path common
            
        Returns:
        --------
        pd.DataFrame
            Common career paths with frequency and success metrics
        """
        df = historical_personas.copy()
        df[timestamp_column] = pd.to_datetime(df[timestamp_column])
        df = df.sort_values([trader_id_column, timestamp_column])
        
        # Extract paths for each trader
        paths = []
        path_performance = defaultdict(list)
        
        for trader_id, group in df.groupby(trader_id_column):
            group = group.sort_values(timestamp_column)
            
            # Get persona sequence
            persona_sequence = group[persona_column].tolist()
            
            # Remove consecutive duplicates
            deduped_sequence = [persona_sequence[0]]
            for p in persona_sequence[1:]:
                if p != deduped_sequence[-1]:
                    deduped_sequence.append(p)
            
            # Create path string
            if len(deduped_sequence) > 1:
                path = ' → '.join(deduped_sequence)
                paths.append(path)
                
                # Track performance if available
                if 'realized_profit' in group.columns:
                    final_profit = group['realized_profit'].iloc[-1]
                    path_performance[path].append(final_profit)
        
        # Count path frequencies
        path_counts = Counter(paths)
        
        # Filter by minimum frequency
        common_paths = {path: count for path, count in path_counts.items() 
                       if count >= min_path_frequency}
        
        # Create results dataframe
        path_data = []
        for path, count in sorted(common_paths.items(), key=lambda x: x[1], reverse=True):
            path_info = {
                'career_path': path,
                'frequency': count,
                'percentage': (count / len(paths)) * 100,
                'avg_length': len(path.split(' → '))
            }
            
            # Add performance metrics if available
            if path in path_performance:
                perfs = path_performance[path]
                path_info['avg_final_profit'] = np.mean(perfs)
                path_info['median_final_profit'] = np.median(perfs)
                path_info['success_rate'] = (np.array(perfs) > 0).mean()
            
            path_data.append(path_info)
        
        self.career_paths_ = pd.DataFrame(path_data)
        
        print(f"\n✓ Identified {len(self.career_paths_)} common career paths")
        print("\nTop 10 Most Common Paths:")
        print(self.career_paths_.head(10)[['career_path', 'frequency', 'percentage']])
        
        return self.career_paths_
    
    def predict_next_persona(self, current_persona: str, 
                            confidence_threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        Predict likely next persona(s) given current persona.
        
        Parameters:
        -----------
        current_persona : str
            Current persona name
        confidence_threshold : float
            Minimum probability threshold for prediction
            
        Returns:
        --------
        List[Tuple[str, float]]
            List of (next_persona, probability) tuples
        """
        if self.transition_matrix_ is None:
            raise ValueError("Transition matrix not calculated. Call calculate_transition_matrix() first.")
        
        if current_persona not in self.transition_matrix_.index:
            raise ValueError(f"Unknown persona: {current_persona}")
        
        # Get transition probabilities
        probs = self.transition_matrix_.loc[current_persona]
        
        # Filter by threshold and sort
        predictions = [(persona, prob) for persona, prob in probs.items() 
                      if prob >= confidence_threshold]
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions
    
    def detect_lifecycle_stage(self, trader_history: pd.DataFrame,
                              trader_id_column: str = 'wallet_address',
                              timestamp_column: str = 'timestamp',
                              activity_column: str = 'trades') -> pd.DataFrame:
        """
        Detect lifecycle stage for each trader.
        
        Stages:
        - Early: New trader, establishing patterns
        - Growth: Increasing activity and skill
        - Mature: Stable, consistent performance
        - Decline: Decreasing activity or performance
        
        Parameters:
        -----------
        trader_history : pd.DataFrame
            Historical trading data per trader
        trader_id_column : str
            Name of trader ID column
        timestamp_column : str
            Name of timestamp column
        activity_column : str
            Column to measure activity level
            
        Returns:
        --------
        pd.DataFrame
            Trader lifecycle stages
        """
        df = trader_history.copy()
        df[timestamp_column] = pd.to_datetime(df[timestamp_column])
        
        lifecycle_data = []
        
        for trader_id, group in df.groupby(trader_id_column):
            group = group.sort_values(timestamp_column)
            
            # Calculate key metrics
            total_days = (group[timestamp_column].max() - group[timestamp_column].min()).days + 1
            total_activity = group[activity_column].sum() if activity_column in group.columns else len(group)
            
            # Split into periods
            n_periods = min(4, len(group))
            if n_periods < 2:
                stage = 'Early'
            else:
                period_size = len(group) // n_periods
                
                # Calculate activity trend
                period_activities = []
                for i in range(n_periods):
                    start_idx = i * period_size
                    end_idx = (i + 1) * period_size if i < n_periods - 1 else len(group)
                    period_data = group.iloc[start_idx:end_idx]
                    
                    if activity_column in period_data.columns:
                        period_activity = period_data[activity_column].sum()
                    else:
                        period_activity = len(period_data)
                    
                    period_activities.append(period_activity)
                
                # Determine trend
                if len(period_activities) >= 2:
                    recent_activity = np.mean(period_activities[-2:])
                    early_activity = np.mean(period_activities[:2])
                    
                    if total_days < 90:
                        stage = 'Early'
                    elif recent_activity > early_activity * 1.2:
                        stage = 'Growth'
                    elif recent_activity < early_activity * 0.6:
                        stage = 'Decline'
                    else:
                        stage = 'Mature'
                else:
                    stage = 'Early'
            
            lifecycle_data.append({
                trader_id_column: trader_id,
                'lifecycle_stage': stage,
                'total_days_active': total_days,
                'total_activity': total_activity,
                'activity_per_day': total_activity / total_days if total_days > 0 else 0
            })
        
        self.lifecycle_stages_ = pd.DataFrame(lifecycle_data)
        
        print("\n✓ Lifecycle Stage Distribution:")
        stage_dist = self.lifecycle_stages_['lifecycle_stage'].value_counts()
        for stage, count in stage_dist.items():
            pct = (count / len(self.lifecycle_stages_)) * 100
            print(f"  {stage}: {count} traders ({pct:.1f}%)")
        
        return self.lifecycle_stages_
    
    def calculate_persona_stability(self, historical_personas: pd.DataFrame,
                                    persona_column: str = 'persona',
                                    timestamp_column: str = 'timestamp',
                                    trader_id_column: str = 'wallet_address') -> pd.DataFrame:
        """
        Calculate how stable each trader's persona assignment is over time.
        
        Parameters:
        -----------
        historical_personas : pd.DataFrame
            DataFrame with historical persona assignments
        persona_column : str
            Name of persona column
        timestamp_column : str
            Name of timestamp column
        trader_id_column : str
            Name of trader ID column
            
        Returns:
        --------
        pd.DataFrame
            Stability metrics per trader
        """
        df = historical_personas.copy()
        df[timestamp_column] = pd.to_datetime(df[timestamp_column])
        df = df.sort_values([trader_id_column, timestamp_column])
        
        stability_data = []
        
        for trader_id, group in df.groupby(trader_id_column):
            group = group.sort_values(timestamp_column)
            
            # Calculate stability metrics
            personas = group[persona_column].tolist()
            
            # Most frequent persona
            persona_counts = Counter(personas)
            most_common_persona = persona_counts.most_common(1)[0][0]
            most_common_freq = persona_counts.most_common(1)[0][1]
            
            # Stability score (proportion of time in most common persona)
            stability_score = most_common_freq / len(personas)
            
            # Number of transitions
            n_transitions = sum(1 for i in range(len(personas) - 1) 
                              if personas[i] != personas[i + 1])
            
            # Transition rate
            transition_rate = n_transitions / (len(personas) - 1) if len(personas) > 1 else 0
            
            stability_data.append({
                trader_id_column: trader_id,
                'dominant_persona': most_common_persona,
                'stability_score': stability_score,
                'num_transitions': n_transitions,
                'transition_rate': transition_rate,
                'num_personas_visited': len(persona_counts)
            })
        
        stability_df = pd.DataFrame(stability_data)
        
        print(f"\n✓ Calculated persona stability for {len(stability_df)} traders")
        print(f"Average stability score: {stability_df['stability_score'].mean():.3f}")
        print(f"Average transitions: {stability_df['num_transitions'].mean():.1f}")
        
        return stability_df
    
    def get_transition_summary(self) -> Dict:
        """
        Get summary of transition patterns.
        
        Returns:
        --------
        Dict
            Summary statistics about persona transitions
        """
        if self.transition_matrix_ is None:
            raise ValueError("Transition matrix not calculated.")
        
        summary = {
            'num_personas': len(self.persona_names_),
            'most_stable_persona': None,
            'most_volatile_persona': None,
            'common_transitions': []
        }
        
        # Find most stable persona (highest self-transition probability)
        self_transitions = np.diag(self.transition_matrix_.values)
        most_stable_idx = np.argmax(self_transitions)
        summary['most_stable_persona'] = self.persona_names_[most_stable_idx]
        summary['stability_score'] = self_transitions[most_stable_idx]
        
        # Find most volatile persona (lowest self-transition probability)
        most_volatile_idx = np.argmin(self_transitions)
        summary['most_volatile_persona'] = self.persona_names_[most_volatile_idx]
        summary['volatility_score'] = 1 - self_transitions[most_volatile_idx]
        
        # Find most common transitions (excluding self-transitions)
        transitions = []
        for i, from_persona in enumerate(self.persona_names_):
            for j, to_persona in enumerate(self.persona_names_):
                if i != j:  # Exclude self-transitions
                    prob = self.transition_matrix_.iloc[i, j]
                    if prob > 0.1:  # Only include significant transitions
                        transitions.append((from_persona, to_persona, prob))
        
        transitions.sort(key=lambda x: x[2], reverse=True)
        summary['common_transitions'] = transitions[:10]
        
        return summary
