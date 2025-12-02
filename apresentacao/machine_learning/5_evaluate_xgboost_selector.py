#!/usr/bin/env python3
"""
Step 5: Evaluate XGBoost selector vs baseline algorithms.

Simulates online scenario using test data to compare:
- XGBoost dynamic selector
- Fixed algorithm baselines (GA, MIP, MCTS, etc.)
"""

import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def load_model_and_data():
    """Load trained model and test data with all algorithm runs."""

    print("Loading model and data...")

    # Load model
    with open('models/xgb_best_overall_model.pkl', 'rb') as f:
        model = pickle.load(f)

    # Load label encoder
    with open('models/xgb_best_overall_model_label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)

    # Load test split indices and full featured dataset
    # vnr_features.csv has all algorithm runs with features and labels
    full_df = pd.read_csv('datasets/vnr_features.csv')
    test_indices = pd.read_csv('datasets/test.csv')

    # Get test VNR identifiers (topology, seed, v_net_id)
    test_vnr_ids = set(zip(
        test_indices['topology'],
        test_indices['seed'],
        test_indices['v_net_id']
    ))

    # Filter full_df to get all algorithm runs for test VNRs
    test_with_algos = full_df[
        full_df.apply(lambda row: (row['topology'], row['seed'], row['v_net_id']) in test_vnr_ids, axis=1)
    ].copy()

    print(f"  Model classes: {label_encoder.classes_}")
    print(f"  Test data: {len(test_with_algos)} records (all algorithm runs)")
    print(f"  Unique VNRs: {test_with_algos.groupby(['topology', 'seed', 'v_net_id']).ngroups}")

    return model, label_encoder, test_with_algos


def extract_features(df):
    """Extract feature columns used by the model."""

    feature_cols = [
        'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
        'v_net_demand_per_node', 'v_net_demand_per_link', 'v_net_connectivity',
        'v_net_total_demand', 'v_net_node_to_link_demand_ratio', 'v_net_lifetime',
        'p_net_available_resource', 'p_net_node_util', 'p_net_link_util',
        'p_net_overall_util', 'inservice_count', 'system_load',
        'num_running_p_net_nodes', 'solving_time', 'topology_encoded'
    ]

    return df[feature_cols]


def simulate_online(model, label_encoder, test_df):
    """
    Simulate online VNE with XGBoost selector.

    For each VNR in test set:
    1. XGBoost predicts best algorithm
    2. Check if that algorithm would succeed
    3. Track metrics
    """

    print("\nSimulating online scenario...")

    # Remove duplicates: keep only one record per (topology, seed, v_net_id, algorithm)
    # This handles cases where same algorithm ran multiple times on same VNR
    test_df_unique = test_df.groupby(['topology', 'seed', 'v_net_id', 'algorithm']).first().reset_index()

    print(f"  After deduplication: {len(test_df_unique)} records")

    # Group by unique VNR (topology, seed, v_net_id)
    vnr_groups = test_df_unique.groupby(['topology', 'seed', 'v_net_id'])

    results = {
        'xgboost_selector': {'accepted': 0, 'rejected': 0, 'total_time': 0.0, 'revenue': 0.0},
        'baselines': {}
    }

    # Initialize baseline counters for each algorithm
    for algo in label_encoder.classes_:
        results['baselines'][algo] = {'accepted': 0, 'rejected': 0, 'total_time': 0.0, 'revenue': 0.0}

    # Process each VNR
    for vnr_id, group in vnr_groups:
        # Get features for this VNR (use first row since features are same across algorithms)
        first_row = group.iloc[0]
        features = extract_features(pd.DataFrame([first_row]))

        # XGBoost predicts best algorithm
        pred_encoded = model.predict(features)[0]
        pred_algo = label_encoder.inverse_transform([pred_encoded])[0]

        # Check if predicted algorithm succeeds
        pred_row = group[group['algorithm'] == pred_algo]

        if len(pred_row) > 0:
            pred_row = pred_row.iloc[0]
            if pred_row['success']:
                results['xgboost_selector']['accepted'] += 1
                results['xgboost_selector']['revenue'] += pred_row['v_net_revenue']
            else:
                results['xgboost_selector']['rejected'] += 1
            results['xgboost_selector']['total_time'] += pred_row['solving_time']
        else:
            # Algorithm not in test data for this VNR - count as rejected
            results['xgboost_selector']['rejected'] += 1

        # Track baselines (each algorithm applied to all VNRs)
        for idx, row in group.iterrows():
            algo = row['algorithm']
            # Each baseline algorithm gets exactly ONE attempt per VNR
            if row['success']:
                results['baselines'][algo]['accepted'] += 1
                results['baselines'][algo]['revenue'] += row['v_net_revenue']
            else:
                results['baselines'][algo]['rejected'] += 1
            results['baselines'][algo]['total_time'] += row['solving_time']

    # Calculate metrics
    total_vnrs = len(vnr_groups)

    # XGBoost metrics
    xgb_results = results['xgboost_selector']
    xgb_results['acceptance_rate'] = xgb_results['accepted'] / total_vnrs
    xgb_results['avg_time'] = xgb_results['total_time'] / total_vnrs
    xgb_results['avg_revenue'] = xgb_results['revenue'] / total_vnrs

    # Baseline metrics
    for algo, baseline in results['baselines'].items():
        baseline['acceptance_rate'] = baseline['accepted'] / total_vnrs
        baseline['avg_time'] = baseline['total_time'] / total_vnrs
        baseline['avg_revenue'] = baseline['revenue'] / total_vnrs

    return results, total_vnrs


def print_results(results, total_vnrs):
    """Print comparison results."""

    print("\n" + "="*80)
    print("ONLINE SIMULATION RESULTS")
    print("="*80)
    print(f"\nTotal VNRs tested: {total_vnrs}")

    # XGBoost
    xgb = results['xgboost_selector']
    print(f"\n{'XGBoost Selector':<20s}")
    print(f"  Acceptance Rate:  {xgb['acceptance_rate']:.4f} ({xgb['accepted']}/{total_vnrs})")
    print(f"  Avg Time per VNR: {xgb['avg_time']:.4f}s")
    print(f"  Avg Revenue:      {xgb['avg_revenue']:.2f}")
    print(f"  Total Revenue:    {xgb['revenue']:.2f}")

    # Baselines
    print(f"\n{'Baseline Algorithms':<20s}")
    for algo, baseline in sorted(results['baselines'].items(), key=lambda x: x[1]['acceptance_rate'], reverse=True):
        print(f"\n  {algo:<15s}")
        print(f"    Acceptance Rate:  {baseline['acceptance_rate']:.4f} ({baseline['accepted']}/{total_vnrs})")
        print(f"    Avg Time per VNR: {baseline['avg_time']:.4f}s")
        print(f"    Avg Revenue:      {baseline['avg_revenue']:.2f}")

    # Comparison
    print(f"\n{'='*80}")
    print("COMPARISON TO BEST BASELINE")
    print("="*80)

    best_baseline_acc = max([b['acceptance_rate'] for b in results['baselines'].values()])
    best_baseline_rev = max([b['revenue'] for b in results['baselines'].values()])

    print(f"  XGBoost vs Best Acceptance: {xgb['acceptance_rate']/best_baseline_acc:.2%}")
    print(f"  XGBoost vs Best Revenue:    {xgb['revenue']/best_baseline_rev:.2%}")


def plot_comparison(results, output_path='results/online_comparison.png'):
    """Plot comparison charts."""

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Prepare data
    algos = ['XGBoost'] + list(results['baselines'].keys())

    acceptance_rates = [results['xgboost_selector']['acceptance_rate']] + \
                      [results['baselines'][a]['acceptance_rate'] for a in results['baselines'].keys()]

    avg_times = [results['xgboost_selector']['avg_time']] + \
               [results['baselines'][a]['avg_time'] for a in results['baselines'].keys()]

    total_revenues = [results['xgboost_selector']['revenue']] + \
                    [results['baselines'][a]['revenue'] for a in results['baselines'].keys()]

    # Colors
    colors = ['#2ecc71'] + ['#95a5a6'] * len(results['baselines'])

    # Plot 1: Acceptance Rate
    ax1 = axes[0]
    bars1 = ax1.bar(range(len(algos)), acceptance_rates, color=colors)
    ax1.set_xticks(range(len(algos)))
    ax1.set_xticklabels(algos, rotation=45, ha='right')
    ax1.set_ylabel('Acceptance Rate')
    ax1.set_title('Acceptance Rate Comparison', fontweight='bold')
    ax1.set_ylim(0, max(acceptance_rates) * 1.2)
    ax1.grid(True, alpha=0.3, axis='y')

    # Add values on bars
    for i, (bar, val) in enumerate(zip(bars1, acceptance_rates)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)

    # Plot 2: Average Time
    ax2 = axes[1]
    bars2 = ax2.bar(range(len(algos)), avg_times, color=colors)
    ax2.set_xticks(range(len(algos)))
    ax2.set_xticklabels(algos, rotation=45, ha='right')
    ax2.set_ylabel('Average Time (seconds)')
    ax2.set_title('Average Time per VNR', fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    # Plot 3: Total Revenue
    ax3 = axes[2]
    bars3 = ax3.bar(range(len(algos)), total_revenues, color=colors)
    ax3.set_xticks(range(len(algos)))
    ax3.set_xticklabels(algos, rotation=45, ha='right')
    ax3.set_ylabel('Total Revenue')
    ax3.set_title('Total Revenue Comparison', fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Comparison plot saved: {output_path}")
    plt.close()


if __name__ == '__main__':
    # Load model and data
    model, label_encoder, test_df = load_model_and_data()

    # Simulate online
    results, total_vnrs = simulate_online(model, label_encoder, test_df)

    # Print results
    print_results(results, total_vnrs)

    # Plot comparison
    plot_comparison(results)

    print("\n" + "="*80)
    print("EVALUATION COMPLETE!")
    print("="*80)
