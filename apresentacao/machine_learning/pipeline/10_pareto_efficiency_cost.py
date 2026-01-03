#!/usr/bin/env python3
"""
Step 10: Revenue-Time Cost Function Optimization

Objective: Maximize Revenue while Minimizing Time

Using weighted cost function:
Cost = -w1·(revenue/max_revenue) + w2·(time/max_time)

Where:
- w1: Weight for revenue (higher = prioritize revenue)
- w2: Weight for time (higher = prioritize speed)
- w1 + w2 = 1

Lower cost = better (higher revenue, lower time)
"""

import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import Axes3D


def load_data():
    """Load trained model and evaluation data."""
    print("Loading model and data...")

    # Load model
    with open('../models/xgb_best_overall_model.pkl', 'rb') as f:
        model = pickle.load(f)

    # Load label encoder
    with open('../models/xgb_best_overall_model_label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)

    # Load full featured dataset
    full_df = pd.read_csv('../datasets/vnr_features.csv')

    print(f"  Loaded {len(full_df)} records")
    print(f"  Algorithms: {label_encoder.classes_}")

    return model, label_encoder, full_df


def compute_metrics_per_algorithm(df, label_encoder):
    """
    Compute aggregated metrics for each algorithm.

    Returns: DataFrame with one row per algorithm

    Focus: Revenue generation and Time efficiency
    """
    print("\nComputing metrics per algorithm...")

    metrics_list = []

    for algo in label_encoder.classes_:
        algo_df = df[df['algorithm'] == algo]

        if len(algo_df) == 0:
            continue

        # Revenue: Total and average from successful embeddings
        algo_df_success = algo_df[algo_df['success'] == True]
        if len(algo_df_success) > 0:
            total_revenue = algo_df_success['v_net_revenue'].sum()
            avg_revenue = algo_df_success['v_net_revenue'].mean()
        else:
            total_revenue = 0
            avg_revenue = 0

        # Time cost proxy: estimated from problem difficulty
        # Problem difficulty = VNR size * connectivity * demand / (1 + available_resources)
        problem_difficulty = (
            algo_df['v_net_size_ratio'] *
            algo_df['v_net_connectivity'] *
            algo_df['v_net_total_demand'] /
            (algo_df['p_net_available_resource'] + 1)
        )
        avg_time_cost = problem_difficulty.mean()

        # Acceptance rate (% of successful embeddings)
        acceptance_rate = (algo_df['success'].sum() / len(algo_df)) if len(algo_df) > 0 else 0

        metrics_list.append({
            'algorithm': algo,
            'total_revenue': total_revenue,
            'avg_revenue': avg_revenue,
            'avg_time_cost': avg_time_cost,
            'acceptance_rate': acceptance_rate,
            'count': len(algo_df)
        })

    metrics_df = pd.DataFrame(metrics_list)
    print(f"  Computed metrics for {len(metrics_df)} algorithms")
    print(f"\n  Algorithm Performance Summary:")
    for idx, row in metrics_df.iterrows():
        print(f"    {row['algorithm']:15s}: rev=${row['avg_revenue']:8.2f}, time={row['avg_time_cost']:8.4f}, acc={row['acceptance_rate']:.1%}")

    return metrics_df


def compute_pareto_cost(metrics_df, w1=0.6, w2=0.4):
    """
    Compute Revenue-Time optimized cost for each algorithm.

    Objective: Maximize Revenue × Minimize Time

    Cost = -w1·(revenue/max_revenue) + w2·(time/max_time)

    Lower cost = better (higher revenue, lower time)

    Args:
        w1: Weight for revenue (0-1), default 0.6 (prioritize revenue)
        w2: Weight for time (0-1), default 0.4 (prioritize speed)
            w1 + w2 = 1
    """
    print(f"\nComputing Revenue-Time cost (w1={w1}, w2={w2})...")

    if abs(w1 + w2 - 1.0) > 0.01:
        print(f"  WARNING: Weights don't sum to 1.0 ({w1} + {w2} = {w1 + w2})")
        print(f"  Normalizing...")
        total = w1 + w2
        w1 = w1 / total
        w2 = w2 / total

    metrics_df = metrics_df.copy()

    # Normalize each objective to [0, 1]
    # 1. Revenue: higher is better
    max_revenue = metrics_df['avg_revenue'].max()
    if max_revenue > 0:
        metrics_df['revenue_norm'] = metrics_df['avg_revenue'] / max_revenue
    else:
        metrics_df['revenue_norm'] = 0

    # 2. Time: lower is better
    max_time = metrics_df['avg_time_cost'].max()
    if max_time > 0:
        metrics_df['time_norm'] = metrics_df['avg_time_cost'] / max_time
    else:
        metrics_df['time_norm'] = 0

    # Compute weighted cost
    # Revenue benefit: -revenue_norm (negative because we want to maximize)
    # Time cost: +time_norm (positive because we want to minimize)
    metrics_df['pareto_cost'] = (
        -w1 * metrics_df['revenue_norm'] +  # Maximize revenue
        w2 * metrics_df['time_norm']        # Minimize time
    )

    # Rank algorithms by cost (lower is better)
    metrics_df['rank'] = metrics_df['pareto_cost'].rank()

    return metrics_df


def print_pareto_results(metrics_df):
    """Print Revenue-Time optimization results."""
    print("\n" + "="*100)
    print("REVENUE-TIME OPTIMIZATION COST ANALYSIS")
    print("="*100)

    for idx, row in metrics_df.sort_values('pareto_cost').iterrows():
        print(f"\n{row['algorithm']:15s} (Rank: {int(row['rank'])})")
        print(f"  Total Revenue:            ${row['total_revenue']:12.2f}")
        print(f"  Avg Revenue/VNR:          ${row['avg_revenue']:12.2f}")
        print(f"  Avg Time Cost (problem):  {row['avg_time_cost']:12.4f}")
        print(f"  Acceptance Rate:          {row['acceptance_rate']:12.1%}")
        print(f"  Revenue-Time Cost:        {row['pareto_cost']:12.4f} (lower = better)")
        print(f"    - Revenue Contribution: -{row['revenue_norm']:12.4f} (maximized)")
        print(f"    - Time Contribution:    {row['time_norm']:12.4f} (minimized)")


def plot_pareto_2d_scatter(metrics_df, output_path='../results/pareto_2d_scatter.png'):
    """
    Plot 2D scatter plots showing trade-offs between objectives.
    """
    print(f"\nPlotting 2D Pareto scatter plots...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Color by Pareto cost (lower = better = green)
    costs = metrics_df['pareto_cost'].values
    colors = plt.cm.RdYlGn_r(costs / costs.max())  # Red (high cost) to Green (low cost)

    # Plot 1: Acceptance Rate vs Computational Cost
    ax = axes[0, 0]
    scatter = ax.scatter(metrics_df['acceptance_rate'], metrics_df['avg_computational_cost'],
                        s=200, c=costs, cmap='RdYlGn_r', edgecolors='black', linewidth=1.5, alpha=0.7)
    for idx, row in metrics_df.iterrows():
        ax.annotate(row['algorithm'],
                   (row['acceptance_rate'], row['avg_computational_cost']),
                   fontsize=9, ha='center', va='center', fontweight='bold')
    ax.set_xlabel('Acceptance Rate', fontweight='bold')
    ax.set_ylabel('Avg Computational Cost (problem complexity)', fontweight='bold')
    ax.set_title('Acceptance vs Computational Cost Trade-off', fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Plot 2: Acceptance Rate vs Resource Efficiency
    ax = axes[0, 1]
    scatter = ax.scatter(metrics_df['acceptance_rate'], metrics_df['resource_efficiency'],
                        s=200, c=costs, cmap='RdYlGn_r', edgecolors='black', linewidth=1.5, alpha=0.7)
    for idx, row in metrics_df.iterrows():
        ax.annotate(row['algorithm'],
                   (row['acceptance_rate'], row['resource_efficiency']),
                   fontsize=9, ha='center', va='center', fontweight='bold')
    ax.set_xlabel('Acceptance Rate', fontweight='bold')
    ax.set_ylabel('Resource Efficiency', fontweight='bold')
    ax.set_title('Acceptance vs Efficiency Trade-off', fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Plot 3: Computational Cost vs Resource Efficiency
    ax = axes[1, 0]
    scatter = ax.scatter(metrics_df['avg_computational_cost'], metrics_df['resource_efficiency'],
                        s=200, c=costs, cmap='RdYlGn_r', edgecolors='black', linewidth=1.5, alpha=0.7)
    for idx, row in metrics_df.iterrows():
        ax.annotate(row['algorithm'],
                   (row['avg_computational_cost'], row['resource_efficiency']),
                   fontsize=9, ha='center', va='center', fontweight='bold')
    ax.set_xlabel('Avg Computational Cost (problem complexity)', fontweight='bold')
    ax.set_ylabel('Resource Efficiency', fontweight='bold')
    ax.set_title('Computational Cost vs Efficiency Trade-off', fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Plot 4: Pareto Cost Breakdown (stacked bar)
    ax = axes[1, 1]
    algos = metrics_df.sort_values('pareto_cost')['algorithm'].values
    indices = range(len(algos))

    acceptance_losses = metrics_df.sort_values('pareto_cost')['acceptance_loss'].values * 0.4
    time_costs = metrics_df.sort_values('pareto_cost')['time_cost'].values * 0.3
    efficiency_losses = metrics_df.sort_values('pareto_cost')['efficiency_loss'].values * 0.3

    ax.bar(indices, acceptance_losses, label='Acceptance Loss (w1=0.4)', color='#e74c3c', alpha=0.8)
    ax.bar(indices, time_costs, bottom=acceptance_losses, label='Time Cost (w2=0.3)', color='#f39c12', alpha=0.8)
    ax.bar(indices, efficiency_losses, bottom=acceptance_losses+time_costs, label='Efficiency Loss (w3=0.3)', color='#3498db', alpha=0.8)

    ax.set_xticks(indices)
    ax.set_xticklabels(algos, rotation=45, ha='right')
    ax.set_ylabel('Weighted Cost Contribution', fontweight='bold')
    ax.set_title('Pareto Cost Breakdown by Component', fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=axes, orientation='vertical', pad=0.02)
    cbar.set_label('Pareto Cost (lower = better)', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved to {output_path}")
    plt.close()


def plot_pareto_3d(metrics_df, output_path='../results/pareto_3d.png'):
    """
    Plot 3D scatter plot showing all three objectives simultaneously.
    """
    print(f"\nPlotting 3D Pareto surface...")

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    costs = metrics_df['pareto_cost'].values
    colors = plt.cm.RdYlGn_r(costs / costs.max())

    scatter = ax.scatter(metrics_df['acceptance_rate'],
                        metrics_df['avg_computational_cost'],
                        metrics_df['resource_efficiency'],
                        s=300, c=costs, cmap='RdYlGn_r',
                        edgecolors='black', linewidth=1.5, alpha=0.7)

    # Annotate each point
    for idx, row in metrics_df.iterrows():
        ax.text(row['acceptance_rate'],
               row['avg_computational_cost'],
               row['resource_efficiency'],
               f"  {row['algorithm']}", fontsize=9, fontweight='bold')

    ax.set_xlabel('Acceptance Rate', fontweight='bold', labelpad=10)
    ax.set_ylabel('Computational Cost (complexity)', fontweight='bold', labelpad=10)
    ax.set_zlabel('Resource Efficiency', fontweight='bold', labelpad=10)
    ax.set_title('3D Pareto Efficiency Surface\n(Acceptance × Cost × Efficiency)',
                fontweight='bold', pad=20)

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, pad=0.1, shrink=0.8)
    cbar.set_label('Pareto Cost', fontweight='bold')

    ax.view_init(elev=20, azim=45)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved to {output_path}")
    plt.close()


def plot_pareto_frontier(metrics_df, output_path='../results/pareto_frontier.png'):
    """
    Plot Pareto frontier: algorithms on the efficient frontier.
    An algorithm is on the frontier if you can't improve one objective
    without worsening another.
    """
    print(f"\nPlotting Pareto frontier...")

    # For 3 objectives, we'll show 2D projections of the frontier
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Compute Pareto frontier (simplified: just show top N algorithms)
    df_sorted = metrics_df.sort_values('pareto_cost')

    # Plot 1: Acceptance vs Computational Cost (with frontier)
    ax = axes[0]

    # Plot all points
    ax.scatter(metrics_df['acceptance_rate'], metrics_df['avg_computational_cost'],
              s=150, alpha=0.5, color='gray', label='All algorithms', zorder=2)

    # Highlight top performers
    top_performers = df_sorted.head(3)
    ax.scatter(top_performers['acceptance_rate'], top_performers['avg_computational_cost'],
              s=300, color='#27ae60', edgecolors='black', linewidth=2,
              label='Top 3 performers', zorder=3)

    # Annotate
    for idx, row in metrics_df.iterrows():
        color = '#27ae60' if row['algorithm'] in top_performers['algorithm'].values else '#7f8c8d'
        ax.annotate(row['algorithm'],
                   (row['acceptance_rate'], row['avg_computational_cost']),
                   fontsize=9, ha='center', va='bottom', color=color, fontweight='bold')

    ax.set_xlabel('Acceptance Rate', fontweight='bold')
    ax.set_ylabel('Computational Cost (problem complexity)', fontweight='bold')
    ax.set_title('Acceptance Rate vs Computational Cost\n(Top 3 in green)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Plot 2: Cost comparison radar/bar
    ax = axes[1]

    df_sorted_plot = df_sorted.copy()
    algos = df_sorted_plot['algorithm'].values
    costs = df_sorted_plot['pareto_cost'].values

    colors_bar = plt.cm.RdYlGn_r(costs / costs.max())
    bars = ax.barh(algos, costs, color=colors_bar, edgecolor='black', linewidth=1.5)

    # Add value labels
    for i, (bar, cost) in enumerate(zip(bars, costs)):
        ax.text(cost + 0.01, bar.get_y() + bar.get_height()/2, f'{cost:.4f}',
               va='center', fontweight='bold', fontsize=9)

    ax.set_xlabel('Pareto Cost (lower = better)', fontweight='bold')
    ax.set_title('Pareto Cost Ranking', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved to {output_path}")
    plt.close()


def plot_sensitivity_analysis(metrics_df, output_path='../results/pareto_sensitivity.png'):
    """
    Show how Pareto ranking changes with different weight combinations.
    """
    print(f"\nPlotting sensitivity analysis...")

    weight_configs = [
        {'name': 'Acceptance\nFirst (w1=0.6)', 'w1': 0.6, 'w2': 0.2, 'w3': 0.2},
        {'name': 'Balanced\n(w1=0.33)', 'w1': 0.33, 'w2': 0.33, 'w3': 0.34},
        {'name': 'Speed\nFirst (w2=0.6)', 'w1': 0.2, 'w2': 0.6, 'w3': 0.2},
        {'name': 'Efficiency\nFirst (w3=0.6)', 'w1': 0.2, 'w2': 0.2, 'w3': 0.6},
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for ax_idx, config in enumerate(weight_configs):
        ax = axes[ax_idx]

        df_temp = compute_pareto_cost(metrics_df,
                                     w1=config['w1'],
                                     w2=config['w2'],
                                     w3=config['w3'])

        df_sorted = df_temp.sort_values('pareto_cost')
        algos = df_sorted['algorithm'].values
        costs = df_sorted['pareto_cost'].values

        colors_bar = plt.cm.RdYlGn_r(costs / costs.max())
        bars = ax.barh(algos, costs, color=colors_bar, edgecolor='black', linewidth=1.5)

        # Add value labels
        for i, (bar, cost) in enumerate(zip(bars, costs)):
            ax.text(cost + 0.01, bar.get_y() + bar.get_height()/2, f'{cost:.3f}',
                   va='center', fontweight='bold', fontsize=8)

        ax.set_xlabel('Cost', fontweight='bold')
        ax.set_title(config['name'], fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved to {output_path}")
    plt.close()


def plot_radar_chart(metrics_df, output_path='../results/pareto_radar.png'):
    """
    Plot radar chart comparing all objectives for top algorithms.
    """
    print(f"\nPlotting radar chart...")

    from math import pi

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

    # Select top 4 algorithms by cost
    top_algos = metrics_df.sort_values('pareto_cost').head(4)

    # Normalize objectives to [0, 1] (higher = better)
    categories = ['Acceptance\nRate', 'Speed\n(1-norm_time)', 'Efficiency']
    num_vars = len(categories)

    angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
    angles += angles[:1]

    colors_list = ['#27ae60', '#f39c12', '#3498db', '#e74c3c']

    for algo_idx, (idx, row) in enumerate(top_algos.iterrows()):
        values = [
            row['acceptance_rate'],  # Already [0,1]
            1 - row['time_cost'],    # Lower time = better, so invert
            row['resource_efficiency'] / metrics_df['resource_efficiency'].max()  # Normalize
        ]
        values += values[:1]

        ax.plot(angles, values, 'o-', linewidth=2, label=row['algorithm'],
               color=colors_list[algo_idx], markersize=8)
        ax.fill(angles, values, alpha=0.15, color=colors_list[algo_idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10, framealpha=0.9)
    plt.title('Top 4 Algorithms: Multi-Objective Comparison\n(Radar Chart)',
             fontweight='bold', pad=20, fontsize=12)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved to {output_path}")
    plt.close()


def export_results_to_csv(metrics_df, output_path='../results/pareto_analysis.csv'):
    """Export detailed results to CSV."""
    print(f"\nExporting results to CSV...")

    # Select relevant columns
    export_df = metrics_df[[
        'algorithm', 'acceptance_rate', 'avg_computational_cost', 'resource_efficiency',
        'pareto_cost', 'acceptance_loss', 'time_cost', 'efficiency_loss', 'rank'
    ]].sort_values('pareto_cost')

    export_df.to_csv(output_path, index=False)
    print(f"  ✓ Saved to {output_path}")


if __name__ == '__main__':
    # Load data
    model, label_encoder, df = load_data()

    # Compute metrics
    metrics_df = compute_metrics_per_algorithm(df, label_encoder)

    # Compute Revenue-Time cost with default weights (prioritize revenue)
    metrics_df = compute_pareto_cost(metrics_df, w1=0.6, w2=0.4)

    # Print results
    print_pareto_results(metrics_df)

    print("\n" + "="*100)
    print("REVENUE-TIME OPTIMIZATION ANALYSIS COMPLETE!")
    print("="*100)
    print("\nObjective: Maximize Revenue while Minimizing Time")
    print("Cost Function: Cost = -w1·(revenue/max_revenue) + w2·(time/max_time)")
    print("Weights: w1=0.6 (revenue priority), w2=0.4 (time priority)")