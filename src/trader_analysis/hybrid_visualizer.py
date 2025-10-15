"""
Hybrid Persona System Visualizations

Advanced visualization tools specifically for the hybrid persona classification system.
Includes confidence analysis, persona quality metrics, and ranking visualizations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set professional style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


class HybridVisualizer:
    """
    Advanced visualization toolkit for hybrid persona system.
    
    Provides comprehensive visualizations for:
    - Persona quality and validation
    - Confidence score distributions
    - Copy-Trading Worthiness rankings
    - Performance comparisons
    - Temporal evolution
    """
    
    def __init__(self, output_dir: str = './outputs'):
        """
        Initialize HybridVisualizer.
        
        Parameters:
        -----------
        output_dir : str
            Directory to save plots
        """
        self.output_dir = output_dir
        
    def plot_persona_quality_matrix(self, 
                                    features_df: pd.DataFrame,
                                    save_path: Optional[str] = None):
        """
        Plot quality matrix showing persona validation status.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe with persona assignments
        save_path : Optional[str]
            Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Quality score distribution by persona
        ax1 = axes[0, 0]
        personas = sorted(features_df['persona'].unique())
        quality_data = [features_df[features_df['persona'] == p]['quality_score'].values 
                       for p in personas]
        
        bp1 = ax1.boxplot(quality_data, labels=personas, patch_artist=True)
        colors = plt.cm.viridis(np.linspace(0, 1, len(personas)))
        for patch, color in zip(bp1['boxes'], colors):
            patch.set_facecolor(color)
        ax1.set_xticklabels(personas, rotation=45, ha='right')
        ax1.set_ylabel('Quality Score')
        ax1.set_title('Quality Score Distribution by Persona')
        ax1.axhline(y=0.7, color='r', linestyle='--', label='High Quality Threshold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Validation pass rate
        ax2 = axes[0, 1]
        if 'validation_passed' in features_df.columns:
            validation_rates = []
            for persona in personas:
                persona_data = features_df[features_df['persona'] == persona]
                pass_rate = (persona_data['validation_passed'].sum() / len(persona_data)) * 100
                validation_rates.append(pass_rate)
            
            bars = ax2.bar(range(len(personas)), validation_rates, color=colors)
            ax2.set_xticks(range(len(personas)))
            ax2.set_xticklabels(personas, rotation=45, ha='right')
            ax2.set_ylabel('Validation Pass Rate (%)')
            ax2.set_title('Persona Validation Quality')
            ax2.axhline(y=90, color='g', linestyle='--', label='Target 90%')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, (bar, rate) in enumerate(zip(bars, validation_rates)):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{rate:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # 3. Persona size vs average quality
        ax3 = axes[1, 0]
        persona_stats = []
        for persona in personas:
            persona_data = features_df[features_df['persona'] == persona]
            persona_stats.append({
                'persona': persona,
                'size': len(persona_data),
                'avg_quality': persona_data['quality_score'].mean()
            })
        stats_df = pd.DataFrame(persona_stats)
        
        scatter = ax3.scatter(stats_df['size'], stats_df['avg_quality'], 
                            s=stats_df['size']*2, alpha=0.6, c=range(len(personas)), 
                            cmap='viridis')
        for idx, row in stats_df.iterrows():
            ax3.annotate(row['persona'], (row['size'], row['avg_quality']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        ax3.set_xlabel('Persona Size (# traders)')
        ax3.set_ylabel('Average Quality Score')
        ax3.set_title('Persona Size vs Quality')
        ax3.grid(True, alpha=0.3)
        
        # 4. High vs Low quality traders
        ax4 = axes[1, 1]
        high_qual = (features_df['quality_score'] >= 0.7).sum()
        medium_qual = ((features_df['quality_score'] >= 0.4) & 
                      (features_df['quality_score'] < 0.7)).sum()
        low_qual = (features_df['quality_score'] < 0.4).sum()
        
        qual_categories = ['High\n(≥0.7)', 'Medium\n(0.4-0.7)', 'Low\n(<0.4)']
        qual_counts = [high_qual, medium_qual, low_qual]
        qual_colors = ['green', 'orange', 'red']
        
        wedges, texts, autotexts = ax4.pie(qual_counts, labels=qual_categories, 
                                           autopct='%1.1f%%', colors=qual_colors,
                                           startangle=90)
        ax4.set_title('Overall Quality Distribution')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_follow_worthiness_rankings(self,
                                       features_df: pd.DataFrame,
                                       top_n: int = 30,
                                       save_path: Optional[str] = None):
        """
        Plot Copy-Trading Worthiness rankings with detailed breakdown.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe with Copy-Trading Scores
        top_n : int
            Number of top traders to show
        save_path : Optional[str]
            Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))
        
        # Sort by Copy-Trading Score
        top_traders = features_df.nlargest(top_n, 'copy_trading_score')
        
        # 1. Overall rankings
        ax1 = axes[0, 0]
        colors_persona = [plt.cm.tab10(i % 10) for i in pd.Categorical(top_traders['persona']).codes]
        bars = ax1.barh(range(len(top_traders)), top_traders['copy_trading_score'].values, 
                       color=colors_persona, alpha=0.7)
        ax1.set_yticks(range(len(top_traders)))
        ax1.set_yticklabels([f"{i+1}. {addr[:8]}..." 
                            for i, addr in enumerate(top_traders['address'].values)],
                           fontsize=8)
        ax1.set_xlabel('Copy-Trading Score')
        ax1.set_title(f'Top {top_n} Traders by Copy-Trading Worthiness Score')
        ax1.invert_yaxis()
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Add persona legend
        from matplotlib.patches import Patch
        personas_in_top = top_traders['persona'].unique()
        legend_elements = [Patch(facecolor=plt.cm.tab10(i % 10), label=p) 
                          for i, p in enumerate(personas_in_top)]
        ax1.legend(handles=legend_elements, loc='lower right', fontsize=8)
        
        # 2. Score components breakdown (for top 10)
        ax2 = axes[0, 1]
        top_10 = top_traders.head(10)
        
        # Stack plot of score components
        score_components = []
        if 'profitability_score' in top_10.columns:
            score_components.append(('Profitability', top_10['profitability_score'].values))
        if 'consistency_score' in top_10.columns:
            score_components.append(('Consistency', top_10['consistency_score'].values))
        if 'risk_score' in top_10.columns:
            score_components.append(('Risk-Adjusted', top_10['risk_score'].values))
        if 'activity_score' in top_10.columns:
            score_components.append(('Activity', top_10['activity_score'].values))
        
        if score_components:
            x = range(len(top_10))
            bottom = np.zeros(len(top_10))
            
            for label, values in score_components:
                ax2.barh(x, values, left=bottom, label=label, alpha=0.8)
                bottom += values
            
            ax2.set_yticks(range(len(top_10)))
            ax2.set_yticklabels([f"{addr[:8]}..." for addr in top_10['address'].values],
                               fontsize=8)
            ax2.set_xlabel('Score Components')
            ax2.set_title('Top 10 Traders - Score Breakdown')
            ax2.legend(loc='lower right', fontsize=8)
            ax2.invert_yaxis()
            ax2.grid(True, alpha=0.3, axis='x')
        
        # 3. Persona-wise rankings
        ax3 = axes[1, 0]
        personas = features_df['persona'].unique()
        persona_top_scores = []
        
        for persona in personas:
            persona_data = features_df[features_df['persona'] == persona]
            if len(persona_data) > 0:
                top_score = persona_data['copy_trading_score'].max()
                avg_score = persona_data['copy_trading_score'].mean()
                persona_top_scores.append({
                    'persona': persona,
                    'top_score': top_score,
                    'avg_score': avg_score,
                    'count': len(persona_data)
                })
        
        persona_scores_df = pd.DataFrame(persona_top_scores).sort_values('top_score', ascending=False)
        
        x = range(len(persona_scores_df))
        width = 0.35
        
        ax3.bar([i - width/2 for i in x], persona_scores_df['top_score'], width, 
               label='Top Score', alpha=0.8)
        ax3.bar([i + width/2 for i in x], persona_scores_df['avg_score'], width,
               label='Avg Score', alpha=0.8)
        
        ax3.set_xticks(x)
        ax3.set_xticklabels(persona_scores_df['persona'], rotation=45, ha='right')
        ax3.set_ylabel('Copy-Trading Score')
        ax3.set_title('Persona Performance Comparison')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Score distribution by persona
        ax4 = axes[1, 1]
        score_by_persona = [features_df[features_df['persona'] == p]['copy_trading_score'].values
                           for p in sorted(personas)]
        
        bp = ax4.boxplot(score_by_persona, labels=sorted(personas), patch_artist=True)
        colors = plt.cm.viridis(np.linspace(0, 1, len(personas)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax4.set_xticklabels(sorted(personas), rotation=45, ha='right')
        ax4.set_ylabel('Copy-Trading Score')
        ax4.set_title('Copy-Trading Score Distribution by Persona')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_persona_characteristics_radar(self,
                                          features_df: pd.DataFrame,
                                          save_path: Optional[str] = None):
        """
        Create radar charts showing persona characteristics.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe
        save_path : Optional[str]
            Path to save figure
        """
        personas = sorted(features_df['persona'].unique())
        n_personas = len(personas)
        
        # Calculate grid size
        n_cols = min(3, n_personas)
        n_rows = (n_personas + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6*n_cols, 6*n_rows),
                                subplot_kw=dict(projection='polar'))
        
        if n_personas == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        # Metrics for radar chart
        metrics = ['win_rate', 'roi', 'total_trades', 'quality_score', 'copy_trading_score']
        
        for idx, persona in enumerate(personas):
            ax = axes[idx]
            persona_data = features_df[features_df['persona'] == persona]
            
            # Normalize metrics to 0-1 scale
            values = []
            for metric in metrics:
                if metric in persona_data.columns:
                    val = persona_data[metric].mean()
                    # Normalize to 0-1 (simple min-max across all data)
                    min_val = features_df[metric].min()
                    max_val = features_df[metric].max()
                    normalized = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
                    values.append(normalized)
                else:
                    values.append(0)
            
            # Close the plot
            values += values[:1]
            
            # Angles for radar
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            angles += angles[:1]
            
            # Plot
            ax.plot(angles, values, 'o-', linewidth=2, label=persona)
            ax.fill(angles, values, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics], fontsize=8)
            ax.set_ylim(0, 1)
            ax.set_title(f'{persona}\n({len(persona_data)} traders)', fontsize=10, pad=20)
            ax.grid(True)
        
        # Hide unused subplots
        for idx in range(n_personas, len(axes)):
            axes[idx].axis('off')
        
        plt.suptitle('Persona Characteristic Profiles (Radar Charts)', 
                    fontsize=14, y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_confidence_vs_performance(self,
                                      features_df: pd.DataFrame,
                                      save_path: Optional[str] = None):
        """
        Plot relationship between quality score and performance metrics.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe
        save_path : Optional[str]
            Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Quality vs Total PnL
        ax1 = axes[0, 0]
        scatter1 = ax1.scatter(features_df['quality_score'], features_df['total_pnl'],
                              c=pd.Categorical(features_df['persona']).codes,
                              cmap='tab10', alpha=0.6, s=50)
        ax1.set_xlabel('Quality Score')
        ax1.set_ylabel('Total PnL')
        ax1.set_title('Quality vs Total PnL')
        ax1.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(features_df['quality_score'], features_df['total_pnl'], 1)
        p = np.poly1d(z)
        ax1.plot(features_df['quality_score'].sort_values(), 
                p(features_df['quality_score'].sort_values()),
                "r--", alpha=0.5, label='Trend')
        ax1.legend()
        
        # 2. Quality vs Win Rate
        ax2 = axes[0, 1]
        scatter2 = ax2.scatter(features_df['quality_score'], features_df['win_rate'],
                              c=pd.Categorical(features_df['persona']).codes,
                              cmap='tab10', alpha=0.6, s=50)
        ax2.set_xlabel('Quality Score')
        ax2.set_ylabel('Win Rate')
        ax2.set_title('Quality vs Win Rate')
        ax2.grid(True, alpha=0.3)
        
        # 3. Quality vs Copy-Trading Score
        ax3 = axes[1, 0]
        scatter3 = ax3.scatter(features_df['quality_score'], features_df['copy_trading_score'],
                              c=pd.Categorical(features_df['persona']).codes,
                              cmap='tab10', alpha=0.6, s=50)
        ax3.set_xlabel('Quality Score')
        ax3.set_ylabel('Copy-Trading Score')
        ax3.set_title('Quality vs Copy-Trading Score')
        ax3.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(features_df['quality_score'], features_df['copy_trading_score'], 1)
        p = np.poly1d(z)
        ax3.plot(features_df['quality_score'].sort_values(),
                p(features_df['quality_score'].sort_values()),
                "r--", alpha=0.5, label='Trend')
        ax3.legend()
        
        # 4. Performance by quality category
        ax4 = axes[1, 1]
        
        # Categorize quality
        features_df['qual_category'] = pd.cut(features_df['quality_score'],
                                             bins=[0, 0.4, 0.7, 1.0],
                                             labels=['Low', 'Medium', 'High'])
        
        qual_performance = features_df.groupby('qual_category')['copy_trading_score'].mean()
        
        bars = ax4.bar(range(len(qual_performance)), qual_performance.values,
                      color=['red', 'orange', 'green'], alpha=0.7)
        ax4.set_xticks(range(len(qual_performance)))
        ax4.set_xticklabels(qual_performance.index)
        ax4.set_ylabel('Average Copy-Trading Score')
        ax4.set_title('Average Performance by Quality Category')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def create_comprehensive_dashboard(self,
                                      features_df: pd.DataFrame,
                                      save_path: Optional[str] = None):
        """
        Create comprehensive dashboard with all key metrics.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe with all analysis results
        save_path : Optional[str]
            Path to save figure
        """
        fig = plt.figure(figsize=(20, 14))
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # Row 1: Summary Stats
        # 1.1 Total traders by persona
        ax1 = fig.add_subplot(gs[0, 0])
        persona_counts = features_df['persona'].value_counts()
        ax1.bar(range(len(persona_counts)), persona_counts.values,
               color=plt.cm.viridis(np.linspace(0, 1, len(persona_counts))))
        ax1.set_xticks(range(len(persona_counts)))
        ax1.set_xticklabels(persona_counts.index, rotation=45, ha='right', fontsize=8)
        ax1.set_title('Traders by Persona', fontsize=10)
        ax1.set_ylabel('Count')
        
        # 1.2 Average quality score by persona
        ax2 = fig.add_subplot(gs[0, 1])
        avg_conf = features_df.groupby('persona')['quality_score'].mean().sort_values(ascending=False)
        ax2.barh(range(len(avg_conf)), avg_conf.values,
                color=plt.cm.viridis(np.linspace(0, 1, len(avg_conf))))
        ax2.set_yticks(range(len(avg_conf)))
        ax2.set_yticklabels(avg_conf.index, fontsize=8)
        ax2.set_title('Avg Quality Score by Persona', fontsize=10)
        ax2.set_xlabel('Quality Score')
        ax2.invert_yaxis()
        
        # 1.3 Quality score distribution
        ax3 = fig.add_subplot(gs[0, 2])
        high_conf = (features_df['quality_score'] >= 0.7).sum()
        medium_conf = ((features_df['quality_score'] >= 0.4) & 
                      (features_df['quality_score'] < 0.7)).sum()
        low_conf = (features_df['quality_score'] < 0.4).sum()
        ax3.pie([high_conf, medium_conf, low_conf],
               labels=['High (≥0.7)', 'Medium', 'Low (<0.4)'],
               autopct='%1.1f%%', colors=['green', 'orange', 'red'],
               startangle=90)
        ax3.set_title('Quality Score Distribution', fontsize=10)
        
        # 1.4 Copy-Trading Score distribution
        ax4 = fig.add_subplot(gs[0, 3])
        ax4.hist(features_df['copy_trading_score'], bins=50, alpha=0.7, edgecolor='black')
        ax4.set_title('Copy-Trading Score Distribution', fontsize=10)
        ax4.set_xlabel('Copy-Trading Score')
        ax4.set_ylabel('Frequency')
        
        # Row 2: Top Performers
        # 2.1-2.4 Top 20 traders
        ax5 = fig.add_subplot(gs[1, :])
        top_20 = features_df.nlargest(20, 'copy_trading_score')
        colors = [plt.cm.tab10(i % 10) for i in pd.Categorical(top_20['persona']).codes]
        ax5.barh(range(len(top_20)), top_20['copy_trading_score'].values,
                color=colors, alpha=0.7)
        ax5.set_yticks(range(len(top_20)))
        ax5.set_yticklabels([f"{i+1}. {addr[:10]}..." 
                            for i, addr in enumerate(top_20['address'].values)],
                           fontsize=8)
        ax5.set_xlabel('Copy-Trading Score')
        ax5.set_title('Top 20 Traders by Copy-Trading Worthiness', fontsize=12, fontweight='bold')
        ax5.invert_yaxis()
        ax5.grid(True, alpha=0.3, axis='x')
        
        # Row 3: Performance Metrics
        # 3.1 Win rate distribution
        ax6 = fig.add_subplot(gs[2, 0])
        ax6.hist(features_df['win_rate'], bins=50, alpha=0.7, edgecolor='black')
        ax6.set_title('Win Rate Distribution', fontsize=10)
        ax6.set_xlabel('Win Rate')
        
        # 3.2 ROI distribution
        ax7 = fig.add_subplot(gs[2, 1])
        ax7.hist(features_df['roi'].clip(-100, 500), bins=50, alpha=0.7, edgecolor='black')
        ax7.set_title('ROI Distribution', fontsize=10)
        ax7.set_xlabel('ROI (%)')
        
        # 3.3 Total PnL by persona
        ax8 = fig.add_subplot(gs[2, 2])
        pnl_by_persona = [features_df[features_df['persona'] == p]['total_pnl'].values
                         for p in sorted(persona_counts.index)]
        bp = ax8.boxplot(pnl_by_persona, labels=sorted(persona_counts.index), patch_artist=True)
        for patch, color in zip(bp['boxes'], plt.cm.viridis(np.linspace(0, 1, len(pnl_by_persona)))):
            patch.set_facecolor(color)
        ax8.set_xticklabels(sorted(persona_counts.index), rotation=45, ha='right', fontsize=8)
        ax8.set_title('Total PnL by Persona', fontsize=10)
        ax8.set_ylabel('Total PnL')
        
        # 3.4 Trades distribution
        ax9 = fig.add_subplot(gs[2, 3])
        ax9.hist(features_df['total_trades'], bins=50, alpha=0.7, edgecolor='black')
        ax9.set_title('Total Trades Distribution', fontsize=10)
        ax9.set_xlabel('Total Trades')
        
        # Row 4: Persona Quality
        # 4.1 Copy-Trading Score by persona
        ax10 = fig.add_subplot(gs[3, 0:2])
        score_by_persona = [features_df[features_df['persona'] == p]['copy_trading_score'].values
                           for p in sorted(persona_counts.index)]
        bp2 = ax10.boxplot(score_by_persona, labels=sorted(persona_counts.index), 
                          patch_artist=True, vert=False)
        for patch, color in zip(bp2['boxes'], plt.cm.viridis(np.linspace(0, 1, len(score_by_persona)))):
            patch.set_facecolor(color)
        ax10.set_yticklabels(sorted(persona_counts.index), fontsize=8)
        ax10.set_title('Copy-Trading Score by Persona', fontsize=10)
        ax10.set_xlabel('Copy-Trading Score')
        ax10.grid(True, alpha=0.3, axis='x')
        
        # 4.2 Quality score vs Performance scatter
        ax11 = fig.add_subplot(gs[3, 2:])
        scatter = ax11.scatter(features_df['quality_score'], features_df['copy_trading_score'],
                             c=pd.Categorical(features_df['persona']).codes,
                             cmap='tab10', alpha=0.5, s=30)
        ax11.set_xlabel('Quality Score')
        ax11.set_ylabel('Copy-Trading Score')
        ax11.set_title('Quality Score vs Copy-Trading Worthiness', fontsize=10)
        ax11.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(features_df['quality_score'], features_df['copy_trading_score'], 1)
        p = np.poly1d(z)
        ax11.plot(features_df['quality_score'].sort_values(),
                 p(features_df['quality_score'].sort_values()),
                 "r--", alpha=0.5, linewidth=2)
        
        plt.suptitle('Hybrid Persona System - Comprehensive Analysis Dashboard',
                    fontsize=16, fontweight='bold', y=0.995)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


