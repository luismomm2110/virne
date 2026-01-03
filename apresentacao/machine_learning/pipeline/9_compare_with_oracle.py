#!/usr/bin/env python3
"""
Step 9: Compare XGBoost selector predictions with Oracle (optimal algorithm).

For each VNR, this determines:
1. Which algorithm XGBoost selected
2. Which algorithm is actually the best (oracle)
3. Whether XGBoost made the correct choice
"""

import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


def load_data():
    """Load model, predictions, and full data."""

    print("Loading data...")

    # Load model and encoder
    with open('../models/xgb_best_overall_model.pkl', 'rb') as f:
        model = pickle.load(f)

    with open('../models/xgb_best_overall_model_label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)

    # Load test data (original features before predictions)
    test_df = pd.read_csv('../datasets/test.csv')

    # Load predictions we just made
    predictions = pd.read_csv('../results/vnr_predictions.csv')

    # Load full data with all algorithm results
    full_df = pd.read_csv('../datasets/vnr_features.csv')

    print(f"  Model classes: {label_encoder.classes_}")
    print(f"  Test data: {len(test_df)} rows")
    print(f"  Predictions: {len(predictions)} VNRs")
    print(f"  Full data: {len(full_df)} records")

    return model, label_encoder, test_df, predictions, full_df


def engineer_features(df):
    """Compute engineered features."""
    df = df.copy()

    df['network_stress_index'] = (df['p_net_node_util'] + df['p_net_link_util']) / 2
    df['problem_complexity'] = df['v_net_connectivity'] * df['v_net_total_demand']
    df['resource_bottleneck_ratio'] = (
        df['v_net_demand_per_node'] / (df['v_net_demand_per_link'] + 1e-6)
    )
    df['vnr_size_category'] = pd.cut(
        df['v_net_num_nodes'],
        bins=[0, 4, 7, 15],
        labels=[0, 1, 2],
        ordered=False
    ).astype(int)
    df['cpu_intensive_flag'] = (
        df['v_net_demand_per_node'] > df['v_net_demand_per_link']
    ).astype(int)
    df['bandwidth_intensive_flag'] = (
        df['v_net_demand_per_link'] > df['v_net_demand_per_node']
    ).astype(int)
    df['utilization_pressure'] = df['p_net_node_util'] * df['p_net_link_util']
    df['resource_efficiency'] = (
        df['p_net_available_resource'] / (df['v_net_total_demand'] + 1e-6)
    )

    return df


def get_oracle_algorithm(row_idx, test_df, full_df, trained_algos):
    """
    Determine the oracle (best) algorithm for a VNR.

    Oracle picks the algorithm that succeeds with the best metrics.
    """

    # Get the test row
    test_row = test_df.iloc[row_idx]

    # Map topology_encoded to actual topology name
    topology_map = {0: 'tree', 1: 'fat_tree'}
    test_topology = topology_map.get(test_row.get('topology_encoded', 0), 'unknown')

    # Match features to find corresponding VNR in full_df
    # Key criteria: same topology + same VNR characteristics

    features_to_match = ['v_net_num_nodes', 'v_net_demand', 'v_net_lifetime']

    # Strategy 1: Exact match on key features with same topology
    mask = full_df['topology'] == test_topology
    for feat in features_to_match:
        if feat in full_df.columns and feat in test_row.index:
            # Allow small tolerance for floating point
            mask &= (np.abs(full_df[feat] - test_row[feat]) < 1)

    matching_rows = full_df[mask].copy()

    if len(matching_rows) == 0:
        # Strategy 2: Fuzzy match - within 5% tolerance
        mask = full_df['topology'] == test_topology
        for feat in features_to_match:
            if feat in full_df.columns and feat in test_row.index:
                tolerance = abs(test_row[feat]) * 0.05 + 1
                mask &= (np.abs(full_df[feat] - test_row[feat]) <= tolerance)

        matching_rows = full_df[mask].copy()

    if len(matching_rows) == 0:
        return None, None, None

    # Filter to only trained algorithms
    matching_rows = matching_rows[matching_rows['algorithm'].isin(trained_algos)]

    if len(matching_rows) == 0:
        return None, None, None

    # Group by unique VNR if possible
    if all(col in matching_rows.columns for col in ['seed', 'v_net_id']):
        # Get the VNR (all matching rows should be for same VNR, but ensure it)
        vnr_set = matching_rows[['seed', 'v_net_id']].drop_duplicates()
        if len(vnr_set) > 1:
            # Multiple VNRs matched - pick the first one
            vnr = vnr_set.iloc[0]
            matching_rows = matching_rows[
                (matching_rows['seed'] == vnr['seed']) &
                (matching_rows['v_net_id'] == vnr['v_net_id'])
            ]

    # Check for success
    if 'success' in matching_rows.columns:
        successful = matching_rows[matching_rows['success'] == True]
    else:
        successful = matching_rows

    if len(successful) > 0:
        # Pick algorithm with best revenue
        if 'v_net_revenue' in successful.columns:
            best_idx = successful['v_net_revenue'].idxmax()
        else:
            best_idx = successful.index[0]

        best_row = successful.loc[best_idx]
        oracle_algo = best_row['algorithm']
        oracle_success = True
        oracle_time = best_row.get('solving_time', np.nan)
    else:
        # No successful algorithm - oracle also fails
        oracle_algo = None
        oracle_success = False
        oracle_time = np.nan

    return oracle_algo, oracle_success, oracle_time


def compare_with_oracle(test_df, predictions, full_df, label_encoder):
    """
    Compare XGBoost predictions with oracle for each VNR.
    """

    print("\nComparing XGBoost predictions with Oracle...")

    trained_algos = set(label_encoder.classes_)
    results = []

    for idx, pred in predictions.iterrows():
        # Get oracle algorithm
        oracle_algo, oracle_success, oracle_time = get_oracle_algorithm(idx, test_df, full_df, trained_algos)

        # Check if XGBoost made correct choice
        xgb_algo = pred['predicted_algorithm']
        correct = (xgb_algo == oracle_algo) if oracle_algo else False

        results.append({
            'vnr_index': pred['vnr_index'],
            'xgb_algorithm': xgb_algo,
            'oracle_algorithm': oracle_algo,
            'correct_prediction': correct,
            'oracle_success': oracle_success,
            'v_net_num_nodes': pred['v_net_num_nodes'],
            'v_net_total_demand': pred['v_net_total_demand'],
            'p_net_overall_util': pred['p_net_overall_util'],
            'system_load': pred['system_load'],
        })

        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1} VNRs...")

    return pd.DataFrame(results)


def print_comparison_summary(comparison_df, label_encoder):
    """Print summary statistics."""

    print("\n" + "="*100)
    print("XGBOOST VS ORACLE COMPARISON SUMMARY")
    print("="*100)

    total = len(comparison_df)
    correct = comparison_df['correct_prediction'].sum()
    accuracy = correct / total if total > 0 else 0

    print(f"\nOverall Accuracy (match with oracle): {accuracy:.2%} ({correct}/{total})")

    # Count by XGBoost selection
    print("\n" + "-"*100)
    print("XGBoost Algorithm Selections:")
    print("-"*100)
    for algo in label_encoder.classes_:
        count = (comparison_df['xgb_algorithm'] == algo).sum()
        pct = count / total if total > 0 else 0
        print(f"  {algo:15s}: {count:3d} selections ({pct:5.1f}%)")

    # Count by Oracle algorithm
    print("\n" + "-"*100)
    print("Oracle (Optimal) Algorithm Distribution:")
    print("-"*100)
    for algo in label_encoder.classes_:
        count = (comparison_df['oracle_algorithm'] == algo).sum()
        pct = count / total if total > 0 else 0
        print(f"  {algo:15s}: {count:3d} times optimal ({pct:5.1f}%)")

    # Confusion matrix
    print("\n" + "-"*100)
    print("Confusion Matrix: XGBoost vs Oracle")
    print("-"*100)

    algos = sorted(label_encoder.classes_)
    print("\n" + " " * 15 + "ORACLE ALGORITHM")
    print(" " * 5 + "XGBOOST" + " " * 5 + " | " + " | ".join(f"{a:8s}" for a in algos) + " |")
    print("-" * 90)

    for xgb_algo in algos:
        row_str = f"{xgb_algo:8s} |"
        for oracle_algo in algos:
            count = len(comparison_df[(comparison_df['xgb_algorithm'] == xgb_algo) &
                                       (comparison_df['oracle_algorithm'] == oracle_algo)])
            row_str += f" {count:8d} |"
        print(row_str)

    # Accuracy per algorithm
    print("\n" + "-"*100)
    print("Accuracy when XGBoost selects each algorithm:")
    print("-"*100)
    for algo in algos:
        algo_df = comparison_df[comparison_df['xgb_algorithm'] == algo]
        if len(algo_df) > 0:
            acc = algo_df['correct_prediction'].sum() / len(algo_df)
            print(f"  {algo:15s}: {acc:.2%} ({algo_df['correct_prediction'].sum()}/{len(algo_df)})")


def save_comparison_csv(comparison_df, output_path='../results/xgboost_vs_oracle.csv'):
    """Save comparison results to CSV."""

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    comparison_df.to_csv(output_path, index=False)
    print(f"\n✓ Comparison saved: {output_path}")


def plot_comparison(comparison_df, label_encoder, output_dir='results'):
    """Create visualization comparing XGBoost with Oracle."""

    os.makedirs(output_dir, exist_ok=True)

    # Figure 1: Confusion matrix heatmap
    fig, ax = plt.subplots(figsize=(10, 8))

    algos = sorted(label_encoder.classes_)
    confusion = np.zeros((len(algos), len(algos)))

    for i, xgb_algo in enumerate(algos):
        for j, oracle_algo in enumerate(algos):
            count = len(comparison_df[(comparison_df['xgb_algorithm'] == xgb_algo) &
                                       (comparison_df['oracle_algorithm'] == oracle_algo)])
            confusion[i, j] = count

    sns.heatmap(confusion, annot=True, fmt='.0f', cmap='YlOrRd',
                xticklabels=algos, yticklabels=algos, ax=ax, cbar_kws={'label': 'Count'})
    ax.set_xlabel('Oracle Algorithm (Optimal)', fontsize=12, fontweight='bold')
    ax.set_ylabel('XGBoost Selection', fontsize=12, fontweight='bold')
    ax.set_title('Confusion Matrix: XGBoost vs Oracle', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/xgboost_vs_oracle_confusion.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir}/xgboost_vs_oracle_confusion.png")
    plt.close()

    # Figure 2: Accuracy per algorithm
    fig, ax = plt.subplots(figsize=(10, 6))

    accuracies = []
    for algo in algos:
        algo_df = comparison_df[comparison_df['xgb_algorithm'] == algo]
        if len(algo_df) > 0:
            acc = algo_df['correct_prediction'].sum() / len(algo_df)
        else:
            acc = 0
        accuracies.append(acc)

    colors = ['#2ecc71' if acc > 0.5 else '#e74c3c' for acc in accuracies]
    bars = ax.bar(algos, accuracies, color=colors, edgecolor='black', linewidth=1.5)

    ax.set_ylabel('Accuracy (fraction correct)', fontsize=12, fontweight='bold')
    ax.set_title('Prediction Accuracy per Algorithm', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.02,
                f'{acc:.1%}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/xgboost_prediction_accuracy.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir}/xgboost_prediction_accuracy.png")
    plt.close()

    # Figure 3: Distribution comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    xgb_counts = comparison_df['xgb_algorithm'].value_counts().reindex(algos, fill_value=0)
    oracle_counts = comparison_df['oracle_algorithm'].value_counts().reindex(algos, fill_value=0)

    x = np.arange(len(algos))
    width = 0.35

    bars1 = ax1.bar(x - width/2, xgb_counts, width, label='XGBoost Selected', color='#3498db', edgecolor='black')
    bars2 = ax1.bar(x + width/2, oracle_counts, width, label='Oracle Optimal', color='#e74c3c', edgecolor='black')

    ax1.set_ylabel('Number of VNRs', fontsize=12, fontweight='bold')
    ax1.set_title('Algorithm Selection Distribution', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(algos)
    ax1.legend(fontsize=11)
    ax1.grid(axis='y', alpha=0.3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)

    # Percentage comparison
    xgb_pct = (xgb_counts / len(comparison_df) * 100).values
    oracle_pct = (oracle_counts / len(comparison_df) * 100).values

    x2 = np.arange(len(algos))
    bars3 = ax2.bar(x2 - width/2, xgb_pct, width, label='XGBoost Selected', color='#3498db', edgecolor='black')
    bars4 = ax2.bar(x2 + width/2, oracle_pct, width, label='Oracle Optimal', color='#e74c3c', edgecolor='black')

    ax2.set_ylabel('Percentage of VNRs (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Algorithm Selection Distribution (Percentage)', fontsize=14, fontweight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(algos)
    ax2.legend(fontsize=11)
    ax2.grid(axis='y', alpha=0.3)

    # Add value labels
    for bars in [bars3, bars4]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/algorithm_distribution_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir}/algorithm_distribution_comparison.png")
    plt.close()


def main():
    """Main execution."""

    # Load data
    model, label_encoder, test_df, predictions, full_df = load_data()

    # Compare with oracle
    comparison_df = compare_with_oracle(test_df, predictions, full_df, label_encoder)

    # Print summary
    print_comparison_summary(comparison_df, label_encoder)

    # Save and visualize
    print("\n" + "="*100)
    print("SAVING RESULTS")
    print("="*100)

    save_comparison_csv(comparison_df)
    plot_comparison(comparison_df, label_encoder)

    print("\n" + "="*100)
    print("COMPARISON COMPLETE!")
    print("="*100)
    print("\nGenerated files:")
    print("  - results/xgboost_vs_oracle.csv")
    print("  - results/xgboost_vs_oracle_confusion.png")
    print("  - results/xgboost_prediction_accuracy.png")
    print("  - results/algorithm_distribution_comparison.png")


if __name__ == '__main__':
    main()