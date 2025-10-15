"""
Quick Visualization Test

Test the hybrid visualizations on existing results.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

from trader_analysis.hybrid_visualizer import HybridVisualizer

def main():
    output_dir = '../outputs'
    
    # Load existing results
    print("Loading analysis results...")
    features = pd.read_csv(f"{output_dir}/complete_trader_analysis.csv")
    print(f"Loaded {len(features)} traders")
    
    # Initialize visualizer
    viz = HybridVisualizer(output_dir)
    
    # Generate visualizations
    print("\n1. Creating persona quality matrix...")
    viz.plot_persona_quality_matrix(
        features,
        save_path=f"{output_dir}/persona_quality_matrix.png"
    )
    plt.close('all')
    
    print("2. Creating follow-worthiness rankings...")
    viz.plot_follow_worthiness_rankings(
        features,
        top_n=30,
        save_path=f"{output_dir}/follow_worthiness_rankings.png"
    )
    plt.close('all')
    
    print("3. Creating persona characteristics radar...")
    viz.plot_persona_characteristics_radar(
        features,
        save_path=f"{output_dir}/persona_characteristics_radar.png"
    )
    plt.close('all')
    
    print("4. Creating confidence vs performance...")
    viz.plot_confidence_vs_performance(
        features,
        save_path=f"{output_dir}/confidence_vs_performance.png"
    )
    plt.close('all')
    
    print("5. Creating comprehensive dashboard...")
    viz.create_comprehensive_dashboard(
        features,
        save_path=f"{output_dir}/comprehensive_dashboard.png"
    )
    plt.close('all')
    
    print("\n✓ All visualizations created successfully!")
    print(f"✓ Saved to: {output_dir}/")

if __name__ == '__main__':
    main()
