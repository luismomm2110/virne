#!/usr/bin/env python3
"""
Step 11: Revenue-Time Optimization Cost Function

Objective: Maximize Revenue while Minimizing Time
Cost = -w1·revenue + w2·time

This is the opposite of Step 10 (Pareto efficiency).
- Maximize revenue → minimize (-revenue)
- Minimize time → minimize time

Usage:
    metrics_df = compute_metrics_per_algorithm(df, label_encoder)
    metrics_df = compute_revenue_time_cost(metrics_df, w1=0.6, w2=0.4)
"""

import pickle
import pandas as pd
import numpy as np


def compute_metrics_per_algorithm(df, label_encoder):
    """
    Compute aggregated metrics for each algorithm focusing on revenue and time.

    Returns: DataFrame with one row per algorithm
    """
    print("\nComputing metrics per algorithm...")

    metrics_list = []

    for algo in label_encoder.classes_:
        algo_df = df[df['algorithm'] == algo]

        if len(algo_df) == 0:
            continue

        # Total revenue from successful embeddings
        algo_df_success = algo_df[algo_df['success'] == True]
        if len(algo_df_success) > 0:
            total_revenue = algo_df_success['v_net_revenue'].sum()
            avg_revenue = algo_df_success['v_net_revenue'].mean()
        else:
            total_revenue = 0
            avg_revenue = 0

        # Time cost: computational cost proxy
        # Problem difficulty = VNR size * connectivity * demand / (1 + available_resources)
        problem_difficulty = (
            algo_df['v_net_size_ratio'] *
            algo_df['v_net_connectivity'] *
            algo_df['v_net_total_demand'] /
            (algo_df['p_net_available_resource'] + 1)
        )
        avg_time_cost = problem_difficulty.mean()

        # Acceptance rate
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
        print(f"    {row['algorithm']:15s}: rev=${row['avg_revenue']:8.2f}, "
              f"time={row['avg_time_cost']:8.4f}, acc={row['acceptance_rate']:.1%}")

    return metrics_df


def compute_revenue_time_cost(metrics_df, w1=0.6, w2=0.4):
    """
    Compute Revenue-Time optimized cost for each algorithm.

    Objective: Maximize Revenue × Minimize Time

    Cost = -w1·(revenue/max_revenue) + w2·(time/max_time)

    Lower cost = better (higher revenue, lower time)

    Args:
        metrics_df: DataFrame with metrics per algorithm
        w1: Weight for revenue (0-1), higher = prioritize revenue
        w2: Weight for time (0-1), higher = prioritize speed
            w1 + w2 = 1

    Returns:
        Updated DataFrame with cost columns
    """
    print(f"\nComputing Revenue-Time cost (w1={w1}, w2={w2})...")

    if w1 + w2 != 1.0:
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
    metrics_df['revenue_time_cost'] = (
        -w1 * metrics_df['revenue_norm'] +  # Maximize revenue
        w2 * metrics_df['time_norm']        # Minimize time
    )

    # Rank algorithms by cost (lower is better)
    metrics_df['rank'] = metrics_df['revenue_time_cost'].rank()

    return metrics_df


def print_revenue_time_results(metrics_df):
    """Print Revenue-Time optimization results."""
    print("\n" + "="*100)
    print("REVENUE-TIME OPTIMIZATION ANALYSIS")
    print("="*100)

    for idx, row in metrics_df.sort_values('revenue_time_cost').iterrows():
        print(f"\n{row['algorithm']:15s} (Rank: {int(row['rank'])})")
        print(f"  Total Revenue:            ${row['total_revenue']:12.2f}")
        print(f"  Avg Revenue/VNR:          ${row['avg_revenue']:12.2f}")
        print(f"  Avg Time Cost (problem):  {row['avg_time_cost']:12.4f}")
        print(f"  Acceptance Rate:          {row['acceptance_rate']:12.1%}")
        print(f"  Revenue-Time Cost:        {row['revenue_time_cost']:12.4f} (lower = better)")
        print(f"    - Revenue Contribution: -{row['revenue_norm']:12.4f} (maximized)")
        print(f"    - Time Contribution:    {row['time_norm']:12.4f} (minimized)")


def compute_objectives(metrics_df):
    """Compute objective values for each algorithm."""
    objectives = []
    for idx, row in metrics_df.iterrows():
        objectives.append({
            'algorithm': row['algorithm'],
            'revenue_maximized': row['avg_revenue'],
            'time_minimized': row['avg_time_cost'],
            'composite_cost': row['revenue_time_cost'],
            'rank': int(row['rank'])
        })
    return pd.DataFrame(objectives).sort_values('composite_cost')


if __name__ == '__main__':
    # Example usage
    print("Revenue-Time Cost Function Examples")
    print("="*100)

    # Hypothetical data
    example_data = {
        'algorithm': ['MIP', 'PL_RANK', 'GA_META', 'MCTS', 'SA_META', 'D_ROUND'],
        'avg_revenue': [450, 320, 290, 280, 270, 150],
        'avg_time_cost': [0.45, 0.28, 0.32, 0.35, 0.38, 0.52],
        'acceptance_rate': [0.65, 0.53, 0.50, 0.48, 0.46, 0.33],
        'total_revenue': [9000, 6400, 5800, 5600, 5400, 3000],
        'count': [1000, 1000, 1000, 1000, 1000, 1000]
    }

    df_example = pd.DataFrame(example_data)

    print("\nExample 1: Equal priority (w1=0.5, w2=0.5)")
    print("-" * 100)
    df1 = compute_revenue_time_cost(df_example, w1=0.5, w2=0.5)
    print_revenue_time_results(df1)

    print("\n\nExample 2: Prioritize revenue (w1=0.7, w2=0.3)")
    print("-" * 100)
    df2 = compute_revenue_time_cost(df_example, w1=0.7, w2=0.3)
    print_revenue_time_results(df2)

    print("\n\nExample 3: Prioritize speed (w1=0.3, w2=0.7)")
    print("-" * 100)
    df3 = compute_revenue_time_cost(df_example, w1=0.3, w2=0.7)
    print_revenue_time_results(df3)

    # Show objectives comparison
    print("\n\n" + "="*100)
    print("OBJECTIVES COMPARISON")
    print("="*100)
    objectives = compute_objectives(df_example)
    print(objectives.to_string(index=False))
