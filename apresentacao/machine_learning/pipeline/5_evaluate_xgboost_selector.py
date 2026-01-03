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
    with open('../models/xgb_best_overall_model.pkl', 'rb') as f:
        model = pickle.load(f)

    # Load label encoder
    with open('../models/xgb_best_overall_model_label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)

    # Load full featured dataset with all algorithm runs and identifiers
    full_df = pd.read_csv('../datasets/vnr_features.csv')

    # Load test split indices (may or may not have identifying columns)
    test_indices_df = pd.read_csv('../datasets/test.csv')

    # Get test VNR identifiers if they exist in test.csv, otherwise use row indices
    if 'topology' in test_indices_df.columns and 'seed' in test_indices_df.columns and 'v_net_id' in test_indices_df.columns:
        test_vnr_ids = set(zip(
            test_indices_df['topology'],
            test_indices_df['seed'],
            test_indices_df['v_net_id']
        ))
        # Filter full_df to get all algorithm runs for test VNRs
        test_with_algos = full_df[
            full_df.apply(lambda row: (row['topology'], row['seed'], row['v_net_id']) in test_vnr_ids, axis=1)
        ].copy()
    else:
        # If test.csv doesn't have identifiers, assume it's just feature vectors
        # Use the order to identify which rows were in the test set
        # We'll need to work with the full_df directly and use a reasonable split
        print("  Warning: test.csv doesn't have topology/seed/v_net_id columns")
        print("  Using full vnr_features.csv for evaluation")
        test_with_algos = full_df.copy()

    print(f"  Model classes: {label_encoder.classes_}")
    print(f"  Test data: {len(test_with_algos)} records (all algorithm runs)")
    print(f"  Unique VNRs: {test_with_algos.groupby(['topology', 'seed', 'v_net_id']).ngroups}")

    return model, label_encoder, test_with_algos


def engineer_features(df):
    """Compute engineered features like train.csv had."""
    df = df.copy()

    # Network Stress Index
    df['network_stress_index'] = (df['p_net_node_util'] + df['p_net_link_util']) / 2

    # Problem Complexity Score
    df['problem_complexity'] = df['v_net_connectivity'] * df['v_net_total_demand']

    # Resource Bottleneck Ratio
    df['resource_bottleneck_ratio'] = (
        df['v_net_demand_per_node'] / (df['v_net_demand_per_link'] + 1e-6)
    )

    # VNR Size Category
    df['vnr_size_category'] = pd.cut(
        df['v_net_num_nodes'],
        bins=[0, 4, 7, 15],
        labels=[0, 1, 2],
        ordered=False
    ).astype(int)

    # CPU Intensive Flag
    df['cpu_intensive_flag'] = (
        df['v_net_demand_per_node'] > df['v_net_demand_per_link']
    ).astype(int)

    # Bandwidth Intensive Flag
    df['bandwidth_intensive_flag'] = (
        df['v_net_demand_per_link'] > df['v_net_demand_per_node']
    ).astype(int)

    # Utilization Pressure
    df['utilization_pressure'] = df['p_net_node_util'] * df['p_net_link_util']

    # Resource Efficiency Metric
    df['resource_efficiency'] = (
        df['p_net_available_resource'] / (df['v_net_total_demand'] + 1e-6)
    )

    return df


def extract_features(df):
    """Extract feature columns used by the model.

    Model was trained on simplified features (after 2_prepare_dataset.py preprocessing).
    So we need to use the exact feature names and order from train.csv.
    NOTE: solving_time is removed because you don't know it before choosing the algorithm.
    """

    # First engineer the computed features
    df = engineer_features(df)

    # These are the EXACT features the model was trained on (from train.csv)
    # Order matters! This is the order XGBoost expects
    # NOTE: solving_time REMOVED (data leakage - not available at decision time)
    feature_cols = [
        'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
        'v_net_demand_per_node', 'v_net_demand_per_link', 'v_net_connectivity',
        'v_net_total_demand', 'v_net_node_to_link_demand_ratio', 'v_net_lifetime',
        'p_net_available_resource', 'p_net_node_util', 'p_net_link_util',
        'p_net_overall_util', 'inservice_count', 'system_load',
        'num_running_p_net_nodes', 'topology_encoded',
        'network_stress_index', 'problem_complexity', 'resource_bottleneck_ratio',
        'vnr_size_category', 'cpu_intensive_flag', 'bandwidth_intensive_flag',
        'utilization_pressure', 'resource_efficiency'
    ]

    return df[feature_cols]


def simulate_online(model, label_encoder, test_df):
    """
    Simulate online VNE with XGBoost selector.

    For each VNR in test set:
    1. XGBoost predicts best algorithm
    2. Check if that algorithm would succeed
    3. Track metrics
    4. Also compute oracle (optimal) performance
    """

    print("\nSimulating online scenario...")

    # Remove duplicates: keep only one record per (topology, seed, v_net_id, algorithm)
    # This handles cases where same algorithm ran multiple times on same VNR
    test_df_unique = test_df.groupby(['topology', 'seed', 'v_net_id', 'algorithm']).first().reset_index()

    print(f"  After deduplication: {len(test_df_unique)} records")

    # Group by unique VNR (topology, seed, v_net_id)
    vnr_groups = test_df_unique.groupby(['topology', 'seed', 'v_net_id'])

    results = {
        'oracle': {'accepted': 0, 'rejected': 0, 'total_time': 0.0, 'revenue': 0.0},
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

        # === ORACLE: Find best possible outcome for this VNR ===
        # Oracle picks the algorithm that succeeds with highest revenue (if any succeed)
        group_trained_algos = group[group['algorithm'].isin(label_encoder.classes_)]
        accepted_trained = group_trained_algos[group_trained_algos['success'] == True]

        if len(accepted_trained) > 0:
            # Pick the accepted algorithm with highest revenue
            oracle_idx = accepted_trained['v_net_revenue'].idxmax()
            oracle_row = group.loc[oracle_idx]
            results['oracle']['accepted'] += 1
            results['oracle']['revenue'] += oracle_row['v_net_revenue']
            # Only track solving_time if column exists
            if 'solving_time' in oracle_row.index:
                results['oracle']['total_time'] += oracle_row['solving_time']
        else:
            # No algorithm accepted - oracle also fails
            results['oracle']['rejected'] += 1

        # === XGBoost SELECTOR ===
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
            # Only track solving_time if column exists
            if 'solving_time' in pred_row.index:
                results['xgboost_selector']['total_time'] += pred_row['solving_time']
        else:
            # Algorithm not in test data for this VNR - count as rejected
            results['xgboost_selector']['rejected'] += 1

        # === BASELINES: Track each algorithm ===
        # Track baselines (only for algorithms the model was trained on)
        for idx, row in group.iterrows():
            algo = row['algorithm']
            # Skip algorithms not in training set (they weren't tested during training)
            if algo not in label_encoder.classes_:
                continue
            # Each baseline algorithm gets exactly ONE attempt per VNR
            if row['success']:
                results['baselines'][algo]['accepted'] += 1
                results['baselines'][algo]['revenue'] += row['v_net_revenue']
            else:
                results['baselines'][algo]['rejected'] += 1
            # Only track solving_time if column exists
            if 'solving_time' in row.index:
                results['baselines'][algo]['total_time'] += row['solving_time']

    # Calculate metrics
    total_vnrs = len(vnr_groups)

    # Oracle metrics
    oracle_results = results['oracle']
    oracle_results['acceptance_rate'] = oracle_results['accepted'] / total_vnrs
    oracle_results['avg_time'] = oracle_results['total_time'] / total_vnrs
    oracle_results['avg_revenue'] = oracle_results['revenue'] / total_vnrs

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

    # Oracle
    oracle = results['oracle']
    print(f"\n{'Oracle (Optimal)':<20s}")
    print(f"  Acceptance Rate:  {oracle['acceptance_rate']:.4f} ({oracle['accepted']}/{total_vnrs})")
    print(f"  Avg Time per VNR: {oracle['avg_time']:.4f}s")
    print(f"  Avg Revenue:      {oracle['avg_revenue']:.2f}")
    print(f"  Total Revenue:    {oracle['revenue']:.2f}")

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
    print("COMPARISON TO ORACLE AND BEST BASELINE")
    print("="*80)

    best_baseline_acc = max([b['acceptance_rate'] for b in results['baselines'].values()])
    best_baseline_rev = max([b['revenue'] for b in results['baselines'].values()])

    print(f"\n  XGBoost vs Oracle Acceptance:       {xgb['acceptance_rate']/oracle['acceptance_rate']:.2%}")
    print(f"  XGBoost vs Oracle Revenue:          {xgb['revenue']/oracle['revenue']:.2%}")
    print(f"  XGBoost vs Best Baseline Acceptance: {xgb['acceptance_rate']/best_baseline_acc:.2%}")
    print(f"  XGBoost vs Best Baseline Revenue:    {xgb['revenue']/best_baseline_rev:.2%}")


def plot_comparison(results, output_path='../results/online_comparison.png'):
    """Plot comparison charts including oracle."""

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Prepare data with oracle first
    algos = ['Oracle'] + ['XGBoost'] + list(results['baselines'].keys())

    acceptance_rates = [results['oracle']['acceptance_rate'],
                       results['xgboost_selector']['acceptance_rate']] + \
                      [results['baselines'][a]['acceptance_rate'] for a in results['baselines'].keys()]

    avg_times = [results['oracle']['avg_time'],
                results['xgboost_selector']['avg_time']] + \
               [results['baselines'][a]['avg_time'] for a in results['baselines'].keys()]

    total_revenues = [results['oracle']['revenue'],
                     results['xgboost_selector']['revenue']] + \
                    [results['baselines'][a]['revenue'] for a in results['baselines'].keys()]

    # Colors: Oracle in green, XGBoost in gold, baselines in gray
    colors = ['#27ae60'] + ['#f39c12'] + ['#95a5a6'] * len(results['baselines'])

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
