"""
Hybrid Persona Classification System

Advanced trader classification combining:
1. Unsupervised pattern discovery
2. Domain-specific validation rules
3. Multi-factor quality scoring
4. Predictive performance modeling

This system is designed for copy-trading recommendations with reliability as top priority.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from scipy.spatial.distance import cdist
from scipy.stats import zscore
import warnings
warnings.filterwarnings('ignore')


class PersonaDefinition:
    """Define persona with both statistical and domain-specific criteria."""
    
    def __init__(self, name: str, description: str, 
                 constraints: Dict, quality_weights: Dict):
        """
        Initialize persona definition.
        
        Parameters:
        -----------
        name : str
            Persona name
        description : str
            Human-readable description
        constraints : Dict
            Hard constraints for membership (min/max values)
        quality_weights : Dict
            Feature weights for quality scoring
        """
        self.name = name
        self.description = description
        self.constraints = constraints
        self.quality_weights = quality_weights
    
    def validate(self, trader_row: pd.Series) -> Tuple[bool, float]:
        """
        Validate if trader meets persona criteria.
        
        Returns:
        --------
        Tuple[bool, float]
            (passes_validation, confidence_score)
        """
        score = 1.0
        passes = True
        
        for feature, rules in self.constraints.items():
            if feature not in trader_row:
                continue
            
            value = trader_row[feature]
            
            # Check minimum
            if 'min' in rules and value < rules['min']:
                passes = False
                score *= 0.5
            
            # Check maximum
            if 'max' in rules and value > rules['max']:
                passes = False
                score *= 0.5
            
            # Preferred range (soft constraint)
            if 'preferred_min' in rules and value >= rules['preferred_min']:
                score *= 1.2
            if 'preferred_max' in rules and value <= rules['preferred_max']:
                score *= 1.2
        
        return passes, min(score, 1.0)


class HybridPersonaSystem:
    """
    Advanced hybrid persona classification system.
    
    Combines:
    - Unsupervised clustering for pattern discovery
    - Domain-specific validation rules
    - Multi-factor quality scoring
    - Predictive performance modeling
    """
    
    def __init__(self, random_state: int = 42):
        """Initialize hybrid persona system."""
        self.random_state = random_state
        self.scaler = RobustScaler()  # More robust to outliers
        self.personas = self._define_personas()
        self.cluster_model = None
        self.quality_model = None
        self.feature_names_ = None
        
    def _define_personas(self) -> Dict[str, PersonaDefinition]:
        """
        Define trader personas with domain expertise.
        
        Returns:
        --------
        Dict[str, PersonaDefinition]
            Persona definitions
        """
        personas = {}
        
        # 1. ELITE SNIPER - High precision, selective
        personas['Elite Sniper'] = PersonaDefinition(
            name='Elite Sniper',
            description='High win rate, selective entries, excellent risk management',
            constraints={
                'win_rate': {'min': 60.0, 'preferred_min': 70.0},
                'total_trades': {'min': 10, 'max': 200, 'preferred_max': 100},
                'roi': {'min': 20.0, 'preferred_min': 50.0},
                'total_pnl': {'min': 5000.0}
            },
            quality_weights={
                'win_rate': 0.30,
                'roi': 0.25,
                'profit_factor': 0.20,
                'avg_profit_per_trade': 0.15,
                'total_pnl': 0.10
            }
        )
        
        # 2. WHALE - High volume, market moving
        personas['Whale'] = PersonaDefinition(
            name='Whale',
            description='Large position sizes, high capital deployment',
            constraints={
                'total_volume': {'min': 500000.0, 'preferred_min': 1000000.0},
                'avg_trade_size': {'min': 2000.0, 'preferred_min': 5000.0},
                'total_pnl': {'min': 50000.0},
                'total_trades': {'min': 20}
            },
            quality_weights={
                'total_pnl': 0.30,
                'roi': 0.25,
                'win_rate': 0.20,
                'total_volume': 0.15,
                'profit_factor': 0.10
            }
        )
        
        # 3. CONSISTENT PERFORMER - Steady, reliable returns
        personas['Consistent Performer'] = PersonaDefinition(
            name='Consistent Performer',
            description='Steady profits, good risk management, reliable',
            constraints={
                'win_rate': {'min': 45.0, 'preferred_min': 55.0},
                'total_trades': {'min': 30, 'preferred_min': 50},
                'roi': {'min': 10.0, 'preferred_min': 25.0},
                'profit_factor': {'min': 1.2, 'preferred_min': 1.5}
            },
            quality_weights={
                'profit_factor': 0.25,
                'win_rate': 0.25,
                'roi': 0.20,
                'total_pnl': 0.20,
                'total_trades': 0.10
            }
        )
        
        # 4. SCALPER - High frequency, small profits
        personas['Scalper'] = PersonaDefinition(
            name='Scalper',
            description='High frequency trading, small consistent profits',
            constraints={
                'total_trades': {'min': 100, 'preferred_min': 200},
                'avg_trade_size': {'max': 2000.0, 'preferred_max': 1000.0},
                'win_rate': {'min': 50.0, 'preferred_min': 60.0},
                'total_pnl': {'min': 1000.0}
            },
            quality_weights={
                'win_rate': 0.30,
                'total_pnl': 0.25,
                'total_trades': 0.20,
                'profit_factor': 0.15,
                'roi': 0.10
            }
        )
        
        # 5. MOMENTUM TRADER - Rides trends, good timing
        personas['Momentum Trader'] = PersonaDefinition(
            name='Momentum Trader',
            description='Trend following, good entry/exit timing',
            constraints={
                'total_trades': {'min': 20, 'max': 150},
                'roi': {'min': 15.0, 'preferred_min': 30.0},
                'avg_profit_per_trade': {'min': 50.0},
                'win_rate': {'min': 40.0}
            },
            quality_weights={
                'roi': 0.30,
                'avg_profit_per_trade': 0.25,
                'win_rate': 0.20,
                'total_pnl': 0.15,
                'profit_factor': 0.10
            }
        )
        
        # 6. RISK-TAKER - High risk/high reward
        personas['Risk-Taker'] = PersonaDefinition(
            name='Risk-Taker',
            description='Aggressive trading, high volatility, boom or bust',
            constraints={
                'total_volume': {'min': 100000.0},
                'avg_trade_size': {'min': 3000.0},
                # Note: Lower win rate acceptable for high rewards
                'roi': {'min': -50.0}  # Can have losses
            },
            quality_weights={
                'total_pnl': 0.35,
                'roi': 0.25,
                'total_volume': 0.20,
                'avg_trade_size': 0.15,
                'profit_factor': 0.05
            }
        )
        
        # 7. DEVELOPING TRADER - Growing, improving
        personas['Developing Trader'] = PersonaDefinition(
            name='Developing Trader',
            description='Newer trader showing promise and improvement',
            constraints={
                'total_trades': {'min': 10, 'max': 50},
                'win_rate': {'min': 35.0},
                'total_pnl': {'min': 0.0}  # At least break-even
            },
            quality_weights={
                'win_rate': 0.30,
                'roi': 0.25,
                'profit_factor': 0.20,
                'total_pnl': 0.15,
                'total_trades': 0.10
            }
        )
        
        return personas
    
    def fit(self, X: pd.DataFrame, feature_names: List[str]) -> 'HybridPersonaSystem':
        """
        Fit the hybrid persona system.
        
        Parameters:
        -----------
        X : pd.DataFrame
            Feature dataframe
        feature_names : List[str]
            Features to use for clustering
            
        Returns:
        --------
        self
        """
        print("\n" + "="*70)
        print("HYBRID PERSONA CLASSIFICATION SYSTEM")
        print("="*70)
        
        self.feature_names_ = feature_names
        X_features = X[feature_names].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_features)
        
        # Use clustering for initial grouping (not final classification)
        print("\nStep 1: Unsupervised pattern discovery...")
        self.cluster_model = KMeans(
            n_clusters=7,  # Match number of personas
            random_state=self.random_state,
            n_init=20,
            max_iter=500
        )
        cluster_labels = self.cluster_model.fit_predict(X_scaled)
        
        print(f"  Discovered {len(set(cluster_labels))} initial patterns")
        
        return self
    
    def classify_traders(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify traders into personas with validation and quality scoring.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe
            
        Returns:
        --------
        pd.DataFrame
            Dataframe with persona assignments, confidence, and quality scores
        """
        df = features_df.copy()
        
        print("\nStep 2: Applying domain-specific validation...")
        
        # Initialize result columns
        df['persona'] = 'Unclassified'
        df['persona_confidence'] = 0.0
        df['validation_passed'] = False
        df['quality_score'] = 0.0
        
        # Track persona probabilities
        for persona_name in self.personas.keys():
            df[f'prob_{persona_name}'] = 0.0
        
        # Classify each trader
        classifications = []
        for idx, row in df.iterrows():
            best_persona = None
            best_score = 0.0
            persona_scores = {}
            
            # Try each persona
            for persona_name, persona_def in self.personas.items():
                passes, confidence = persona_def.validate(row)
                
                if passes:
                    # Calculate quality score for this persona
                    quality = self._calculate_quality_score(row, persona_def)
                    combined_score = confidence * quality
                    persona_scores[persona_name] = combined_score
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        best_persona = persona_name
            
            # Assign best persona or mark unclassified
            if best_persona:
                df.at[idx, 'persona'] = best_persona
                df.at[idx, 'persona_confidence'] = best_score
                df.at[idx, 'validation_passed'] = True
                df.at[idx, 'quality_score'] = persona_scores[best_persona]
                
                # Set probabilities (normalized)
                total = sum(persona_scores.values())
                for p_name, p_score in persona_scores.items():
                    df.at[idx, f'prob_{p_name}'] = p_score / total if total > 0 else 0
        
        # Summary statistics
        print("\n✓ Classification complete!")
        print(f"\nPersona Distribution:")
        persona_counts = df['persona'].value_counts()
        for persona, count in persona_counts.items():
            pct = (count / len(df)) * 100
            avg_quality = df[df['persona'] == persona]['quality_score'].mean()
            print(f"  {persona}: {count} traders ({pct:.1f}%) - Avg Quality: {avg_quality:.3f}")
        
        return df
    
    def _calculate_quality_score(self, trader_row: pd.Series, 
                                 persona_def: PersonaDefinition) -> float:
        """
        Calculate quality score for a trader in a specific persona.
        
        Parameters:
        -----------
        trader_row : pd.Series
            Trader data
        persona_def : PersonaDefinition
            Persona definition with quality weights
            
        Returns:
        --------
        float
            Quality score (0-1)
        """
        score = 0.0
        total_weight = 0.0
        
        for feature, weight in persona_def.quality_weights.items():
            if feature not in trader_row:
                continue
            
            value = trader_row[feature]
            
            # Normalize value to 0-1 range based on reasonable bounds
            normalized = self._normalize_feature(feature, value)
            
            score += normalized * weight
            total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _normalize_feature(self, feature: str, value: float) -> float:
        """
        Normalize feature value to 0-1 range.
        
        Parameters:
        -----------
        feature : str
            Feature name
        value : float
            Feature value
            
        Returns:
        --------
        float
            Normalized value (0-1)
        """
        # Define reasonable ranges for normalization
        ranges = {
            'win_rate': (0, 100),
            'roi': (-100, 200),
            'total_pnl': (-100000, 500000),
            'total_trades': (0, 1000),
            'profit_factor': (0, 5),
            'avg_profit_per_trade': (-1000, 5000),
            'total_volume': (0, 5000000),
            'avg_trade_size': (0, 10000)
        }
        
        if feature in ranges:
            min_val, max_val = ranges[feature]
            normalized = (value - min_val) / (max_val - min_val)
            return max(0, min(1, normalized))
        
        return 0.5  # Default if unknown feature
    
    def calculate_copy_trading_score(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate comprehensive copy-trading recommendation score.
        
        Combines:
        - Quality score within persona
        - Profitability metrics
        - Risk-adjusted returns
        - Consistency
        - Recency
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe with persona assignments
            
        Returns:
        --------
        pd.DataFrame
            Dataframe with copy_trading_score column
        """
        df = features_df.copy()
        
        print("\nStep 3: Calculating copy-trading scores...")
        
        # Initialize score components
        df['profitability_score'] = 0.0
        df['risk_adjusted_score'] = 0.0
        df['consistency_score'] = 0.0
        df['copy_trading_score'] = 0.0
        
        for idx, row in df.iterrows():
            # Skip unclassified traders
            if row['persona'] == 'Unclassified':
                continue
            
            # 1. Profitability Score (40%)
            profit_score = self._score_profitability(row)
            
            # 2. Risk-Adjusted Score (30%)
            risk_score = self._score_risk_adjusted_returns(row)
            
            # 3. Consistency Score (20%)
            consistency = self._score_consistency(row)
            
            # 4. Quality Score from persona validation (10%)
            quality = row['quality_score']
            
            # Combined weighted score
            copy_score = (
                profit_score * 0.40 +
                risk_score * 0.30 +
                consistency * 0.20 +
                quality * 0.10
            )
            
            df.at[idx, 'profitability_score'] = profit_score
            df.at[idx, 'risk_adjusted_score'] = risk_score
            df.at[idx, 'consistency_score'] = consistency
            df.at[idx, 'copy_trading_score'] = copy_score
        
        print("✓ Copy-trading scores calculated!")
        
        return df
    
    def _score_profitability(self, row: pd.Series) -> float:
        """Score based on profitability metrics."""
        # Combine ROI and total PnL
        roi_score = self._normalize_feature('roi', row.get('roi', 0))
        pnl_score = self._normalize_feature('total_pnl', row.get('total_pnl', 0))
        
        # Win rate bonus
        win_rate_score = self._normalize_feature('win_rate', row.get('win_rate', 0))
        
        return (roi_score * 0.4 + pnl_score * 0.4 + win_rate_score * 0.2)
    
    def _score_risk_adjusted_returns(self, row: pd.Series) -> float:
        """Score based on risk-adjusted metrics."""
        # Profit factor
        profit_factor = row.get('profit_factor', 0)
        pf_score = self._normalize_feature('profit_factor', profit_factor)
        
        # Win/Loss ratio
        win_loss_ratio = row.get('win_loss_ratio', 0)
        wl_score = min(1.0, win_loss_ratio / 2.0)  # Normalize assuming 2.0 is excellent
        
        # Average profit per trade
        avg_profit = row.get('avg_profit_per_trade', 0)
        avg_profit_score = self._normalize_feature('avg_profit_per_trade', avg_profit)
        
        return (pf_score * 0.4 + wl_score * 0.3 + avg_profit_score * 0.3)
    
    def _score_consistency(self, row: pd.Series) -> float:
        """Score based on consistency metrics."""
        # Number of trades (more trades = more proven)
        trades = row.get('total_trades', 0)
        trades_score = min(1.0, trades / 100.0)  # 100+ trades is excellent
        
        # Win rate consistency
        win_rate = row.get('win_rate', 0)
        # Prefer 50-70% (too high might be luck, too low is bad)
        if 50 <= win_rate <= 70:
            wr_consistency = 1.0
        elif 40 <= win_rate < 50 or 70 < win_rate <= 80:
            wr_consistency = 0.8
        elif win_rate >= 80:
            wr_consistency = 0.9  # Very high but slightly suspicious
        else:
            wr_consistency = 0.5
        
        return (trades_score * 0.6 + wr_consistency * 0.4)
    
    def get_top_traders(self, features_df: pd.DataFrame, 
                       top_n: int = 50,
                       persona: Optional[str] = None) -> pd.DataFrame:
        """
        Get top traders overall or by persona.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe with scores
        top_n : int
            Number of top traders to return
        persona : Optional[str]
            Filter by specific persona (None for all)
            
        Returns:
        --------
        pd.DataFrame
            Top traders ranked by copy_trading_score
        """
        df = features_df.copy()
        
        # Filter by persona if specified
        if persona:
            df = df[df['persona'] == persona]
        
        # Filter out unclassified
        df = df[df['persona'] != 'Unclassified']
        
        # Sort by copy_trading_score
        top_traders = df.nlargest(top_n, 'copy_trading_score')
        
        # Select relevant columns
        columns = [
            'address', 'persona', 'copy_trading_score',
            'quality_score', 'profitability_score', 'risk_adjusted_score',
            'total_pnl', 'roi', 'win_rate', 'total_trades',
            'profit_factor', 'persona_confidence'
        ]
        
        # Filter to existing columns
        columns = [col for col in columns if col in top_traders.columns]
        
        return top_traders[columns]
    
    def get_persona_rankings(self, features_df: pd.DataFrame,
                            top_n_per_persona: int = 10) -> Dict[str, pd.DataFrame]:
        """
        Get top traders for each persona.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe with scores
        top_n_per_persona : int
            Number of top traders per persona
            
        Returns:
        --------
        Dict[str, pd.DataFrame]
            Dictionary mapping persona to top traders
        """
        rankings = {}
        
        for persona_name in self.personas.keys():
            top_traders = self.get_top_traders(
                features_df,
                top_n=top_n_per_persona,
                persona=persona_name
            )
            
            if len(top_traders) > 0:
                rankings[persona_name] = top_traders
        
        return rankings
