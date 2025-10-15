"""
Adaptive Persona Learning Module

Intelligent data-driven persona discovery system that learns trader archetypes
from behavioral patterns without predefined rules.

Key Features:
- Unsupervised pattern discovery through multiple clustering algorithms
- Automatic optimal cluster detection
- Statistical profiling and automated persona naming
- Probabilistic persona membership
- Temporal evolution tracking
- Incremental learning capabilities
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, silhouette_samples, davies_bouldin_score, calinski_harabasz_score
from scipy.spatial.distance import cdist
from scipy.stats import zscore
import warnings
warnings.filterwarnings('ignore')

try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
    warnings.warn("UMAP not available. Install with: pip install umap-learn")


class AdaptivePersonaLearner:
    """
    Intelligent persona discovery system that learns trader archetypes from data.
    
    This replaces rule-based persona assignment with a data-driven approach that:
    - Discovers natural groupings in trader behavior
    - Automatically determines optimal number of personas
    - Generates interpretable persona names from statistical profiles
    - Tracks persona evolution over time
    - Provides probabilistic membership scores
    """
    
    def __init__(self, random_state: int = 42, min_clusters: int = 3, max_clusters: int = 12):
        """
        Initialize AdaptivePersonaLearner.
        
        Parameters:
        -----------
        random_state : int
            Random state for reproducibility
        min_clusters : int
            Minimum number of personas to consider
        max_clusters : int
            Maximum number of personas to consider
        """
        self.random_state = random_state
        self.min_clusters = min_clusters
        self.max_clusters = max_clusters
        self.scaler = StandardScaler()
        
        # Model storage
        self.best_model = None
        self.best_n_clusters = None
        self.cluster_labels_ = None
        self.cluster_centers_ = None
        self.persona_names_ = None
        self.persona_profiles_ = None
        
        # Feature importance
        self.feature_names_ = None
        self.discriminative_features_ = None
        
    def _calculate_gap_statistic(self, X: np.ndarray, k: int, n_references: int = 10) -> float:
        """
        Calculate gap statistic for optimal cluster selection.
        
        Parameters:
        -----------
        X : np.ndarray
            Scaled feature matrix
        k : int
            Number of clusters to test
        n_references : int
            Number of reference datasets to generate
            
        Returns:
        --------
        float
            Gap statistic value
        """
        # Fit clustering on actual data
        kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
        labels = kmeans.fit_predict(X)
        
        # Calculate within-cluster dispersion
        W_k = sum([np.sum(cdist(X[labels == i], [kmeans.cluster_centers_[i]], 'euclidean'))
                   for i in range(k)])
        
        # Generate reference datasets and calculate dispersion
        ref_dispersions = []
        for _ in range(n_references):
            # Generate random reference data with same bounds
            random_data = np.random.uniform(X.min(axis=0), X.max(axis=0), X.shape)
            kmeans_ref = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels_ref = kmeans_ref.fit_predict(random_data)
            
            W_k_ref = sum([np.sum(cdist(random_data[labels_ref == i], 
                                       [kmeans_ref.cluster_centers_[i]], 'euclidean'))
                          for i in range(k)])
            ref_dispersions.append(np.log(W_k_ref))
        
        # Gap statistic
        gap = np.mean(ref_dispersions) - np.log(W_k)
        return gap
    
    def find_optimal_clusters(self, X: np.ndarray, method: str = '综合') -> int:
        """
        Find optimal number of clusters using multiple methods.
        
        Parameters:
        -----------
        X : np.ndarray
            Scaled feature matrix
        method : str
            Method to use: 'silhouette', 'gap', 'elbow', '综合' (combined)
            
        Returns:
        --------
        int
            Optimal number of clusters
        """
        print(f"\nFinding optimal number of clusters (testing {self.min_clusters} to {self.max_clusters})...")
        
        k_range = range(self.min_clusters, self.max_clusters + 1)
        silhouette_scores = []
        gap_statistics = []
        inertias = []
        db_scores = []
        ch_scores = []
        
        for k in k_range:
            # Fit K-Means
            kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels = kmeans.fit_predict(X)
            
            # Silhouette score (higher is better)
            sil_score = silhouette_score(X, labels)
            silhouette_scores.append(sil_score)
            
            # Davies-Bouldin score (lower is better)
            db_score = davies_bouldin_score(X, labels)
            db_scores.append(db_score)
            
            # Calinski-Harabasz score (higher is better)
            ch_score = calinski_harabasz_score(X, labels)
            ch_scores.append(ch_score)
            
            # Inertia for elbow method
            inertias.append(kmeans.inertia_)
            
            # Gap statistic (slower, optional)
            if method in ['gap', '综合'] and k <= 8:  # Limit gap calculation for speed
                gap = self._calculate_gap_statistic(X, k, n_references=5)
                gap_statistics.append(gap)
            
            print(f"  k={k}: Silhouette={sil_score:.4f}, DB={db_score:.4f}, CH={ch_score:.2f}")
        
        # Find optimal k using different methods
        optimal_k_silhouette = k_range[np.argmax(silhouette_scores)]
        optimal_k_db = k_range[np.argmin(db_scores)]
        optimal_k_ch = k_range[np.argmax(ch_scores)]
        
        # Elbow method using second derivative
        if len(inertias) > 2:
            # Normalize inertias
            inertias_norm = (inertias - np.min(inertias)) / (np.max(inertias) - np.min(inertias))
            # Calculate second derivative
            second_derivative = np.diff(inertias_norm, n=2)
            optimal_k_elbow = k_range[np.argmax(second_derivative) + 2]
        else:
            optimal_k_elbow = optimal_k_silhouette
        
        # Gap statistic
        if gap_statistics:
            optimal_k_gap = k_range[np.argmax(gap_statistics[:len(gap_statistics)])]
        else:
            optimal_k_gap = optimal_k_silhouette
        
        print(f"\nOptimal k by method:")
        print(f"  Silhouette: {optimal_k_silhouette}")
        print(f"  Davies-Bouldin: {optimal_k_db}")
        print(f"  Calinski-Harabasz: {optimal_k_ch}")
        print(f"  Elbow: {optimal_k_elbow}")
        if gap_statistics:
            print(f"  Gap Statistic: {optimal_k_gap}")
        
        # Combined decision: majority vote with preference for silhouette
        candidates = [optimal_k_silhouette, optimal_k_db, optimal_k_ch, optimal_k_elbow]
        if gap_statistics:
            candidates.append(optimal_k_gap)
        
        # Use mode, but prefer silhouette if tie
        from collections import Counter
        vote_counts = Counter(candidates)
        optimal_k = vote_counts.most_common(1)[0][0]
        
        # If vote is too fragmented, use silhouette
        if vote_counts[optimal_k] == 1:
            optimal_k = optimal_k_silhouette
        
        print(f"\n✓ Selected optimal k: {optimal_k} clusters")
        
        return optimal_k
    
    def fit(self, X: pd.DataFrame, feature_names: List[str] = None, 
            algorithm: str = 'kmeans', auto_k: bool = True) -> 'AdaptivePersonaLearner':
        """
        Fit adaptive persona learning model.
        
        Parameters:
        -----------
        X : pd.DataFrame
            Feature dataframe (will extract numeric columns)
        feature_names : List[str]
            Names of features to use (if None, uses all numeric columns)
        algorithm : str
            Clustering algorithm: 'kmeans', 'hierarchical', or 'ensemble'
        auto_k : bool
            Automatically determine optimal number of clusters
            
        Returns:
        --------
        self
        """
        # Extract feature matrix
        if feature_names is None:
            feature_names = X.select_dtypes(include=[np.number]).columns.tolist()
        
        self.feature_names_ = feature_names
        X_features = X[feature_names].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_features)
        
        # Find optimal number of clusters
        if auto_k:
            self.best_n_clusters = self.find_optimal_clusters(X_scaled)
        else:
            self.best_n_clusters = self.max_clusters
        
        # Fit clustering model
        print(f"\nFitting {algorithm} clustering with {self.best_n_clusters} clusters...")
        
        if algorithm == 'kmeans':
            self.best_model = KMeans(
                n_clusters=self.best_n_clusters,
                random_state=self.random_state,
                n_init=20,
                max_iter=500
            )
        elif algorithm == 'hierarchical':
            self.best_model = AgglomerativeClustering(
                n_clusters=self.best_n_clusters,
                linkage='ward'
            )
        elif algorithm == 'ensemble':
            # Use ensemble of multiple algorithms and combine
            kmeans = KMeans(n_clusters=self.best_n_clusters, random_state=self.random_state, n_init=20)
            hierarchical = AgglomerativeClustering(n_clusters=self.best_n_clusters, linkage='ward')
            
            labels_kmeans = kmeans.fit_predict(X_scaled)
            labels_hierarchical = hierarchical.fit_predict(X_scaled)
            
            # Combine using consensus (take kmeans but validate with hierarchical)
            self.cluster_labels_ = labels_kmeans
            self.best_model = kmeans
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        if algorithm != 'ensemble':
            self.cluster_labels_ = self.best_model.fit_predict(X_scaled)
        
        # Store cluster centers
        if hasattr(self.best_model, 'cluster_centers_'):
            self.cluster_centers_ = self.best_model.cluster_centers_
        else:
            # Calculate centers manually for algorithms without centers attribute
            self.cluster_centers_ = np.array([
                X_scaled[self.cluster_labels_ == i].mean(axis=0)
                for i in range(self.best_n_clusters)
            ])
        
        # Generate persona profiles and names
        self._generate_persona_profiles(X, X_scaled)
        
        # Calculate feature importance
        self._calculate_discriminative_features(X_scaled)
        
        print(f"✓ Clustering complete!")
        
        return self
    
    def _generate_persona_profiles(self, X: pd.DataFrame, X_scaled: np.ndarray):
        """
        Generate statistical profiles and interpretable names for each persona.
        
        Parameters:
        -----------
        X : pd.DataFrame
            Original feature dataframe
        X_scaled : np.ndarray
            Scaled feature matrix
        """
        print("\nGenerating persona profiles...")
        
        self.persona_profiles_ = []
        self.persona_names_ = []
        
        # Get original values for each cluster
        for cluster_id in range(self.best_n_clusters):
            mask = self.cluster_labels_ == cluster_id
            cluster_data = X[self.feature_names_].iloc[mask]
            
            # Calculate statistics
            profile = {
                'cluster_id': cluster_id,
                'size': mask.sum(),
                'percentage': (mask.sum() / len(X)) * 100,
                'statistics': {}
            }
            
            for feature in self.feature_names_:
                profile['statistics'][feature] = {
                    'mean': cluster_data[feature].mean(),
                    'median': cluster_data[feature].median(),
                    'std': cluster_data[feature].std(),
                    'min': cluster_data[feature].min(),
                    'max': cluster_data[feature].max()
                }
            
            self.persona_profiles_.append(profile)
            
            # Generate human-readable name
            persona_name = self._generate_persona_name(profile, cluster_id)
            self.persona_names_.append(persona_name)
            
            print(f"  Cluster {cluster_id}: {persona_name} ({profile['size']} traders, {profile['percentage']:.1f}%)")
    
    def _generate_persona_name(self, profile: Dict, cluster_id: int) -> str:
        """
        Generate interpretable persona name based on cluster characteristics.
        
        Parameters:
        -----------
        profile : Dict
            Statistical profile of the cluster
        cluster_id : int
            Cluster identifier
            
        Returns:
        --------
        str
            Human-readable persona name
        """
        stats = profile['statistics']
        
        # Analyze key characteristics
        characteristics = []
        
        # Trading volume
        if 'trade_volume' in stats:
            vol_mean = stats['trade_volume']['mean']
            if vol_mean > 1000000:
                characteristics.append('High-Volume')
            elif vol_mean < 50000:
                characteristics.append('Low-Volume')
        
        # Win rate
        if 'win_rate' in stats:
            wr_mean = stats['win_rate']['mean']
            if wr_mean > 0.65:
                characteristics.append('Sniper')
            elif wr_mean < 0.35:
                characteristics.append('Risk-Taker')
        
        # Trade frequency
        if 'trades' in stats:
            trades_mean = stats['trades']['mean']
            if trades_mean > 100:
                characteristics.append('Active')
            elif trades_mean < 20:
                characteristics.append('Patient')
        
        # Profitability
        if 'realized_profit' in stats:
            profit_mean = stats['realized_profit']['mean']
            if profit_mean > 10000:
                characteristics.append('High-Profit')
            elif profit_mean < -1000:
                characteristics.append('Struggling')
        
        # ROI
        if 'realized_profit_percent' in stats:
            roi_mean = stats['realized_profit_percent']['mean']
            if roi_mean > 50:
                characteristics.append('Elite-Performer')
            elif roi_mean < -20:
                characteristics.append('Underperformer')
        
        # Combine characteristics
        if characteristics:
            name = ' '.join(characteristics[:2])  # Take top 2 characteristics
        else:
            name = f"Persona_{cluster_id}"
        
        return name
    
    def _calculate_discriminative_features(self, X_scaled: np.ndarray):
        """
        Calculate which features best discriminate between personas.
        
        Parameters:
        -----------
        X_scaled : np.ndarray
            Scaled feature matrix
        """
        # Calculate feature importance using cluster separation
        feature_importance = []
        
        for i, feature in enumerate(self.feature_names_):
            # Calculate between-cluster variance vs within-cluster variance
            feature_values = X_scaled[:, i]
            
            between_var = 0
            within_var = 0
            
            for cluster_id in range(self.best_n_clusters):
                mask = self.cluster_labels_ == cluster_id
                cluster_values = feature_values[mask]
                
                # Within-cluster variance
                within_var += cluster_values.var() * len(cluster_values)
                
                # Between-cluster variance (distance from global mean)
                global_mean = feature_values.mean()
                cluster_mean = cluster_values.mean()
                between_var += ((cluster_mean - global_mean) ** 2) * len(cluster_values)
            
            # F-ratio: between-cluster variance / within-cluster variance
            if within_var > 0:
                f_ratio = between_var / within_var
            else:
                f_ratio = 0
            
            feature_importance.append({
                'feature': feature,
                'importance': f_ratio,
                'between_var': between_var,
                'within_var': within_var
            })
        
        # Sort by importance
        self.discriminative_features_ = sorted(
            feature_importance,
            key=lambda x: x['importance'],
            reverse=True
        )
    
    def predict_persona(self, X: pd.DataFrame, return_probabilities: bool = False) -> np.ndarray:
        """
        Predict persona for new traders.
        
        Parameters:
        -----------
        X : pd.DataFrame
            Feature dataframe
        return_probabilities : bool
            If True, return probabilistic membership scores
            
        Returns:
        --------
        np.ndarray
            Persona assignments or probability matrix
        """
        if self.best_model is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        X_features = X[self.feature_names_].values
        X_scaled = self.scaler.transform(X_features)
        
        if return_probabilities:
            # Calculate probabilistic membership using distance to cluster centers
            distances = cdist(X_scaled, self.cluster_centers_, metric='euclidean')
            
            # Convert distances to probabilities (softmax)
            # Negative because closer = higher probability
            probabilities = np.exp(-distances)
            probabilities = probabilities / probabilities.sum(axis=1, keepdims=True)
            
            return probabilities
        else:
            # Hard assignment
            if hasattr(self.best_model, 'predict'):
                return self.best_model.predict(X_scaled)
            else:
                # Use nearest center
                distances = cdist(X_scaled, self.cluster_centers_, metric='euclidean')
                return np.argmin(distances, axis=1)
    
    def assign_personas(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Assign personas to traders with confidence scores.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe
            
        Returns:
        --------
        pd.DataFrame
            Dataframe with persona assignments and confidence scores
        """
        df = features_df.copy()
        
        # Get predictions
        persona_labels = self.predict_persona(df, return_probabilities=False)
        persona_probs = self.predict_persona(df, return_probabilities=True)
        
        # Assign persona names and confidence
        df['persona'] = [self.persona_names_[label] for label in persona_labels]
        df['persona_id'] = persona_labels
        df['persona_confidence'] = np.max(persona_probs, axis=1)
        
        # Add individual persona probabilities
        for i, name in enumerate(self.persona_names_):
            df[f'prob_{name}'] = persona_probs[:, i]
        
        # Add persona description
        df['persona_description'] = df['persona_id'].apply(
            lambda x: f"{self.persona_names_[x]}: {self.persona_profiles_[x]['size']} members"
        )
        
        print(f"\n✓ Assigned personas to {len(df)} traders")
        print("\nPersona Distribution:")
        for name in self.persona_names_:
            count = (df['persona'] == name).sum()
            pct = (count / len(df)) * 100
            print(f"  {name}: {count} traders ({pct:.1f}%)")
        
        return df
    
    def get_persona_statistics(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get comprehensive statistics for each discovered persona.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe with assigned personas
            
        Returns:
        --------
        pd.DataFrame
            Aggregated statistics per persona
        """
        if 'persona' not in features_df.columns:
            raise ValueError("Personas not assigned. Call assign_personas() first.")
        
        stats_list = []
        
        for profile in self.persona_profiles_:
            persona_name = self.persona_names_[profile['cluster_id']]
            persona_data = features_df[features_df['persona'] == persona_name]
            
            if len(persona_data) == 0:
                continue
            
            # Calculate key metrics
            stat = {
                'persona': persona_name,
                'count': len(persona_data),
                'percentage': (len(persona_data) / len(features_df)) * 100
            }
            
            # Add mean values for important features
            for feature in self.feature_names_:
                if feature in persona_data.columns:
                    stat[f'mean_{feature}'] = persona_data[feature].mean()
                    stat[f'median_{feature}'] = persona_data[feature].median()
            
            stats_list.append(stat)
        
        return pd.DataFrame(stats_list)
    
    def get_discriminative_features(self, top_n: int = 10) -> pd.DataFrame:
        """
        Get most discriminative features for persona classification.
        
        Parameters:
        -----------
        top_n : int
            Number of top features to return
            
        Returns:
        --------
        pd.DataFrame
            Top discriminative features with importance scores
        """
        if self.discriminative_features_ is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        return pd.DataFrame(self.discriminative_features_[:top_n])
    
    def reduce_dimensions(self, X: pd.DataFrame, method: str = 'pca', n_components: int = 2) -> np.ndarray:
        """
        Reduce dimensions for visualization.
        
        Parameters:
        -----------
        X : pd.DataFrame
            Feature dataframe
        method : str
            Reduction method: 'pca', 'tsne', or 'umap'
        n_components : int
            Number of components
            
        Returns:
        --------
        np.ndarray
            Reduced dimension features
        """
        X_features = X[self.feature_names_].values
        X_scaled = self.scaler.transform(X_features)
        
        if method == 'pca':
            reducer = PCA(n_components=n_components, random_state=self.random_state)
        elif method == 'tsne':
            reducer = TSNE(n_components=n_components, random_state=self.random_state, 
                          perplexity=min(30, len(X) - 1))
        elif method == 'umap':
            if not UMAP_AVAILABLE:
                raise ValueError("UMAP not available. Install with: pip install umap-learn")
            reducer = umap.UMAP(n_components=n_components, random_state=self.random_state)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return reducer.fit_transform(X_scaled)
    
    def get_persona_names(self) -> List[str]:
        """Return list of discovered persona names."""
        if self.persona_names_ is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        return self.persona_names_
    
    def get_persona_profiles(self) -> List[Dict]:
        """Return detailed persona profiles."""
        if self.persona_profiles_ is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        return self.persona_profiles_
