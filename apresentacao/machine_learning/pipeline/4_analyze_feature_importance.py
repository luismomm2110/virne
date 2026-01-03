#!/usr/bin/env python3
"""
Step 4: Analyze and visualize feature importance from trained XGBoost model.
"""

import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    """Analyze and visualize feature importance."""

    print("Loading trained model...")
    with open('../models/xgb_best_overall_model.pkl', 'rb') as f:
        model = pickle.load(f)

    # Define features (must match training)
    feature_cols = [
        # VNR characteristics
        'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
        'v_net_demand_per_node', 'v_net_demand_per_link', 'v_net_connectivity',
        'v_net_total_demand', 'v_net_node_to_link_demand_ratio', 'v_net_lifetime',

        # Physical network state
        'p_net_available_resource', 'p_net_node_util', 'p_net_link_util',
        'p_net_overall_util',

        # System state
        'inservice_count', 'system_load',
        'num_running_p_net_nodes',

        # Algorithm characteristics (computational effort)
        'solving_time',

        # Topology
        'topology_encoded',

        # Engineered features for better discrimination
        'network_stress_index',
        'problem_complexity',
        'resource_bottleneck_ratio',
        'vnr_size_category',
        'cpu_intensive_flag',
        'bandwidth_intensive_flag',
        'utilization_pressure',
        'resource_efficiency'
    ]

    # Get feature importance
    feature_importance = model.get_booster().get_score(importance_type='weight')

    # Create dataframe
    importance_df = pd.DataFrame(
        list(feature_importance.items()),
        columns=['Feature', 'Importance']
    ).sort_values('Importance', ascending=False)

    # Add features with 0 importance
    all_features = set(feature_cols)
    missing_features = all_features - set(importance_df['Feature'])
    for feat in missing_features:
        new_row = pd.DataFrame({'Feature': [feat], 'Importance': [0]})
        importance_df = pd.concat([importance_df, new_row], ignore_index=True)

    # Reorder to match feature_cols order
    importance_df['Feature'] = pd.Categorical(importance_df['Feature'], categories=feature_cols, ordered=True)
    importance_df = importance_df.sort_values('Feature').reset_index(drop=True)
    importance_df['Feature'] = importance_df['Feature'].astype(str)

    print("\n" + "="*80)
    print("FEATURE IMPORTANCE ANALYSIS")
    print("="*80)
    print("\nFeature Importance (XGBoost - Weight-based):")
    print("-" * 80)

    # Print as formatted table
    for idx, row in importance_df.iterrows():
        print(f"  {idx+1:2d}. {row['Feature']:40s} {row['Importance']:8.1f}")

    # Save to text file
    with open('../results/feature_importance.txt', 'w') as f:
        f.write("Feature Importance (XGBoost)\n")
        f.write("="*60 + "\n\n")
        for idx, row in importance_df.iterrows():
            f.write(f"  {idx+1:2d}. {row['Feature']:40s} {row['Importance']:8.1f}\n")

    print(f"\n✓ Saved: results/feature_importance.txt")

    # Statistics
    print("\n" + "="*80)
    print("IMPORTANCE STATISTICS")
    print("="*80)
    total_importance = importance_df['Importance'].sum()
    print(f"  Total Importance Score: {total_importance:.1f}")
    print(f"  Average per Feature: {importance_df['Importance'].mean():.2f}")
    print(f"  Features with non-zero importance: {(importance_df['Importance'] > 0).sum()}")
    print(f"  Features with zero importance: {(importance_df['Importance'] == 0).sum()}")

    # Top features
    print(f"\n  Top 5 Most Important Features:")
    for idx, row in importance_df.head(5).iterrows():
        pct = (row['Importance'] / total_importance * 100) if total_importance > 0 else 0
        print(f"    {idx+1}. {row['Feature']:40s} {row['Importance']:8.1f} ({pct:5.1f}%)")

    # Visualization 1: Horizontal bar chart
    plt.figure(figsize=(12, 10))

    # Color bars based on importance
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(importance_df)))
    colors = [colors[i] if importance_df.iloc[i]['Importance'] > 0 else '#cccccc'
              for i in range(len(importance_df))]

    plt.barh(range(len(importance_df)), importance_df['Importance'], color=colors, edgecolor='black', linewidth=0.5)
    plt.yticks(range(len(importance_df)), importance_df['Feature'], fontsize=10)
    plt.xlabel('Importance Score (Weight-based)', fontsize=12, fontweight='bold')
    plt.title('XGBoost Feature Importance for Algorithm Selection', fontsize=14, fontweight='bold')
    plt.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, val in enumerate(importance_df['Importance']):
        if val > 0:
            plt.text(val + max(importance_df['Importance']) * 0.01, i, f'{val:.1f}',
                    va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('../results/feature_importance.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: results/feature_importance.png")
    plt.close()

    # Visualization 2: Top features only
    top_n = 10
    top_features = importance_df.head(top_n)

    plt.figure(figsize=(10, 6))
    colors_top = plt.cm.viridis(np.linspace(0, 1, len(top_features)))
    plt.barh(range(len(top_features)), top_features['Importance'], color=colors_top, edgecolor='black', linewidth=1)
    plt.yticks(range(len(top_features)), top_features['Feature'], fontsize=11)
    plt.xlabel('Importance Score', fontsize=12, fontweight='bold')
    plt.title(f'Top {top_n} Most Important Features', fontsize=14, fontweight='bold')
    plt.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, val in enumerate(top_features['Importance']):
        if val > 0:
            plt.text(val + max(top_features['Importance']) * 0.02, i, f'{val:.1f}',
                    va='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig('../results/feature_importance_top10.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: results/feature_importance_top10.png")
    plt.close()

    # Visualization 3: Pie chart of top features
    if total_importance > 0:
        # Group features into "Top N" and "Others"
        top_k = 5
        top_k_features = importance_df.head(top_k)
        others_importance = importance_df.iloc[top_k:]['Importance'].sum()

        pie_data = list(top_k_features['Importance']) + [others_importance]
        pie_labels = list(top_k_features['Feature']) + [f'Others ({len(importance_df) - top_k} features)']
        colors_pie = plt.cm.Set3(np.linspace(0, 1, len(pie_data)))

        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(pie_data, labels=pie_labels, autopct='%1.1f%%',
                                            colors=colors_pie, startangle=90, textprops={'fontsize': 11})
        ax.set_title('Feature Importance Distribution', fontsize=14, fontweight='bold')

        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')

        plt.tight_layout()
        plt.savefig('../results/feature_importance_pie.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: results/feature_importance_pie.png")
        plt.close()

    # Visualization 4: Feature categories
    feature_categories = {
        'VNR Characteristics': [
            'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
            'v_net_demand_per_node', 'v_net_demand_per_link', 'v_net_connectivity',
            'v_net_total_demand', 'v_net_node_to_link_demand_ratio', 'v_net_lifetime'
        ],
        'Physical Network State': [
            'p_net_available_resource', 'p_net_node_util', 'p_net_link_util', 'p_net_overall_util'
        ],
        'System Load': [
            'inservice_count', 'system_load', 'num_running_p_net_nodes'
        ],
        'Algorithm & Topology': [
            'solving_time', 'topology_encoded'
        ],
        'Engineered Features': [
            'network_stress_index', 'problem_complexity', 'resource_bottleneck_ratio',
            'vnr_size_category', 'cpu_intensive_flag', 'bandwidth_intensive_flag',
            'utilization_pressure', 'resource_efficiency'
        ]
    }

    category_importance = {}
    for category, features in feature_categories.items():
        cat_importance = importance_df[importance_df['Feature'].isin(features)]['Importance'].sum()
        category_importance[category] = cat_importance

    print(f"\n" + "="*80)
    print("IMPORTANCE BY FEATURE CATEGORY")
    print("="*80)
    for category, importance in sorted(category_importance.items(), key=lambda x: x[1], reverse=True):
        pct = (importance / total_importance * 100) if total_importance > 0 else 0
        print(f"  {category:30s} {importance:8.1f} ({pct:5.1f}%)")

    # Visualization 5: Category importance
    fig, ax = plt.subplots(figsize=(10, 6))
    categories = list(category_importance.keys())
    values = list(category_importance.values())
    colors_cat = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']

    bars = ax.bar(categories, values, color=colors_cat, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Importance Score', fontsize=12, fontweight='bold')
    ax.set_title('Feature Importance by Category', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{val:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    plt.savefig('../results/feature_importance_by_category.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: results/feature_importance_by_category.png")
    plt.close()

    print(f"\n" + "="*80)
    print("FEATURE IMPORTANCE ANALYSIS COMPLETE!")
    print("="*80)
    print("\nGenerated files:")
    print("  - results/feature_importance.txt")
    print("  - results/feature_importance.png")
    print("  - results/feature_importance_top10.png")
    print("  - results/feature_importance_pie.png")
    print("  - results/feature_importance_by_category.png")


if __name__ == '__main__':
    main()