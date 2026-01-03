#!/usr/bin/env python3
"""
Step 13: Calculate Real Performance Metrics for Tree vs Baseline vs Oracle

This script implements Option 2 (Data-driven approach) to calculate:
1. TREE PERFORMANCE: When tree predictions are used
2. BASELINE PERFORMANCE: When always using best-single-algorithm
3. ORACLE PERFORMANCE: When always using the actual best algorithm

Approach:
For each objective (RAC, LRC, LAR, AST, BALANCED):
  - Load trained decision tree
  - For each test VNR, get tree prediction of best algorithm
  - Use algorithm_comparison_metrics.csv to get that algorithm's performance
  - Aggregate across all test VNRs

Repeat for baseline (most frequently predicted algo) and oracle (actual best).
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATASETS_PATH = PROJECT_ROOT / "datasets"
MODELS_PATH = PROJECT_ROOT / "models"
MODELS_OPTION2_PATH = PROJECT_ROOT / "models_option2"
PIPELINE_PATH = Path(__file__).parent

# Input files
TEST_SET = DATASETS_PATH / "test_enhanced.csv"
ALGO_METRICS = MODELS_PATH / "algorithm_comparison_metrics.csv"

# Output files
OUTPUT_CSV = MODELS_PATH / "tree_real_performance_comparison.csv"
OUTPUT_PNG = MODELS_PATH / "tree_real_performance_comparison.png"

# Mapping of objectives to columns and model files
OBJECTIVES = {
    "RAC": {
        "label_col": "best_for_rac",
        "model_file": MODELS_OPTION2_PATH / "best_for_acceptance_tree.pkl",
        "encoder_file": MODELS_OPTION2_PATH / "best_for_acceptance_encoder.pkl",
        "metric_col": "acceptance_rate",
        "metric_name": "Acceptance Rate (%)",
    },
    "LRC": {
        "label_col": "best_for_lrc",
        "model_file": MODELS_OPTION2_PATH / "best_for_cost_tree.pkl",
        "encoder_file": MODELS_OPTION2_PATH / "best_for_cost_encoder.pkl",
        "metric_col": "revenue_cost_ratio",
        "metric_name": "Revenue-to-Cost Ratio",
    },
    "LAR": {
        "label_col": "best_for_lar",
        "model_file": MODELS_OPTION2_PATH / "best_for_speed_tree.pkl",
        "encoder_file": MODELS_OPTION2_PATH / "best_for_speed_encoder.pkl",
        "metric_col": "avg_time_per_vnr",
        "metric_name": "Average Time per VNR (s)",
    },
    "AST": {
        "label_col": "best_for_ast",
        "model_file": MODELS_OPTION2_PATH / "best_for_speed_tree.pkl",
        "encoder_file": MODELS_OPTION2_PATH / "best_for_speed_encoder.pkl",
        "metric_col": "avg_time_per_vnr",
        "metric_name": "Average Time per VNR (s)",
    },
    "BALANCED": {
        "label_col": "best_for_balanced",
        "model_file": MODELS_OPTION2_PATH / "best_balanced_tree.pkl",
        "encoder_file": MODELS_OPTION2_PATH / "best_balanced_encoder.pkl",
        "metric_col": "acceptance_rate",
        "metric_name": "Balanced Score",
    },
}

# Feature columns (must match training data - exactly 19 features)
FEATURE_COLUMNS = [
    # VNR characteristics (8 features)
    'v_net_num_nodes',
    'v_net_num_edges',
    'v_net_size_ratio',
    'v_net_demand_per_node',
    'v_net_demand_per_link',
    'v_net_connectivity',
    'v_net_total_demand',
    'v_net_node_to_link_demand_ratio',

    # Physical network state (4 features)
    'p_net_available_resource',
    'p_net_node_util',
    'p_net_link_util',
    'p_net_overall_util',

    # System state (2 features)
    'inservice_count',
    'num_running_p_net_nodes',

    # Time and topology (5 features)
    'v_net_lifetime',
    'v_net_time_cost',
    'v_net_time_revenue',
    'p_net_num_nodes',
    'topology_encoded'
]


def load_data():
    """Load all required data."""
    print("Loading data...")
    test_df = pd.read_csv(TEST_SET)
    algo_metrics_df = pd.read_csv(ALGO_METRICS)

    print(f"  Test set: {len(test_df)} VNRs")
    print(f"  Algorithm metrics: {len(algo_metrics_df)} algorithms")

    return test_df, algo_metrics_df


def load_tree_model(objective_config):
    """Load trained tree and label encoder."""
    tree_file = objective_config["model_file"]
    encoder_file = objective_config["encoder_file"]

    if not tree_file.exists():
        raise FileNotFoundError(f"Tree model not found: {tree_file}")
    if not encoder_file.exists():
        raise FileNotFoundError(f"Encoder not found: {encoder_file}")

    with open(tree_file, 'rb') as f:
        tree = pickle.load(f)
    with open(encoder_file, 'rb') as f:
        encoder = pickle.load(f)

    return tree, encoder


def get_tree_predictions(tree, encoder, test_df, objective_config):
    """Get tree predictions for all test VNRs."""
    X_test = test_df[FEATURE_COLUMNS].values

    # Get raw predictions
    predictions = tree.predict(X_test)

    # Decode predictions
    predicted_algos = encoder.inverse_transform(predictions)

    return predicted_algos


def calculate_objective_metrics(
    objective,
    test_df,
    algo_metrics_df,
    objective_config
):
    """Calculate tree, baseline, and oracle performance for one objective."""

    print(f"\n{'='*80}")
    print(f"Objective: {objective}")
    print(f"{'='*80}")

    # Load tree model
    tree, encoder = load_tree_model(objective_config)

    # Get tree predictions
    predicted_algos = get_tree_predictions(tree, encoder, test_df, objective_config)

    # Get actual best algorithms (ground truth labels)
    actual_best_algos = test_df[objective_config["label_col"]].values

    # Calculate TREE PERFORMANCE
    print("\n1. Calculating TREE PERFORMANCE...")
    tree_scores = []
    for pred_algo in predicted_algos:
        algo_row = algo_metrics_df[algo_metrics_df['algorithm'] == pred_algo]
        if len(algo_row) > 0:
            score = algo_row[objective_config["metric_col"]].values[0]
            tree_scores.append(score)
        else:
            tree_scores.append(0)

    tree_avg = np.mean(tree_scores)
    print(f"   Tree average: {tree_avg:.4f}")

    # Calculate BASELINE PERFORMANCE
    print("\n2. Calculating BASELINE PERFORMANCE...")
    # Find most frequently predicted algorithm
    unique, counts = np.unique(predicted_algos, return_counts=True)
    baseline_algo = unique[np.argmax(counts)]
    baseline_freq = np.max(counts) / len(predicted_algos)

    baseline_row = algo_metrics_df[algo_metrics_df['algorithm'] == baseline_algo]
    baseline_avg = baseline_row[objective_config["metric_col"]].values[0]

    print(f"   Baseline algorithm: {baseline_algo} (predicted {baseline_freq*100:.1f}% of time)")
    print(f"   Baseline average: {baseline_avg:.4f}")

    # Calculate ORACLE PERFORMANCE
    print("\n3. Calculating ORACLE PERFORMANCE...")
    oracle_scores = []
    for actual_algo in actual_best_algos:
        algo_row = algo_metrics_df[algo_metrics_df['algorithm'] == actual_algo]
        if len(algo_row) > 0:
            score = algo_row[objective_config["metric_col"]].values[0]
            oracle_scores.append(score)
        else:
            oracle_scores.append(0)

    oracle_avg = np.mean(oracle_scores)
    print(f"   Oracle average: {oracle_avg:.4f}")

    # Calculate improvements
    improvement = tree_avg - baseline_avg
    gap_to_oracle = oracle_avg - tree_avg

    print(f"\n   Tree improvement vs baseline: {improvement:+.4f}")
    print(f"   Gap to oracle: {gap_to_oracle:+.4f}")

    return {
        'objective': objective,
        'baseline_algorithm': baseline_algo,
        'baseline_metric': baseline_avg,
        'tree_metric': tree_avg,
        'oracle_metric': oracle_avg,
        'improvement': improvement,
        'gap_to_oracle': gap_to_oracle,
        'tree_predictions': predicted_algos,
        'actual_best': actual_best_algos,
    }


def format_metric(value, objective):
    """Format metric value based on type."""
    if objective in ['RAC', 'AST', 'BALANCED']:
        # Percentage-like metrics
        if value > 10:
            return f"{value:.2f}%"
        else:
            return f"{value:.4f}"
    else:
        # Ratio metrics
        return f"{value:.4f}"


def create_results_table(results_list):
    """Create summary table from results."""
    table_data = []

    for res in results_list:
        obj = res['objective']
        table_data.append({
            'Objective': obj,
            'Baseline': format_metric(res['baseline_metric'], obj),
            'Tree': format_metric(res['tree_metric'], obj),
            'Oracle': format_metric(res['oracle_metric'], obj),
            'Improvement': format_metric(res['improvement'], obj),
            'Gap to Oracle': format_metric(res['gap_to_oracle'], obj),
        })

    df = pd.DataFrame(table_data)
    return df


def save_results(results_list):
    """Save results to CSV."""
    csv_data = []

    for res in results_list:
        csv_data.append({
            'objective': res['objective'],
            'baseline_algorithm': res['baseline_algorithm'],
            'baseline_metric': res['baseline_metric'],
            'tree_metric': res['tree_metric'],
            'oracle_metric': res['oracle_metric'],
            'improvement': res['improvement'],
            'gap_to_oracle': res['gap_to_oracle'],
        })

    df = pd.DataFrame(csv_data)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✓ Saved: {OUTPUT_CSV}")

    return df


def create_visualization(results_df):
    """Create comparison visualization."""
    fig, ax = plt.subplots(figsize=(14, 8))

    x = np.arange(len(results_df))
    width = 0.25

    # Normalize metrics for visualization (0-100 scale)
    baseline_vals = results_df['baseline_metric'].values
    tree_vals = results_df['tree_metric'].values
    oracle_vals = results_df['oracle_metric'].values

    bars1 = ax.bar(x - width, baseline_vals, width, label='Baseline', color='#FF6B6B', alpha=0.8)
    bars2 = ax.bar(x, tree_vals, width, label='Tree', color='#4ECDC4', alpha=0.8)
    bars3 = ax.bar(x + width, oracle_vals, width, label='Oracle', color='#95E1D3', alpha=0.8)

    ax.set_xlabel('Objective', fontsize=12, fontweight='bold')
    ax.set_ylabel('Performance Metric Value', fontsize=12, fontweight='bold')
    ax.set_title('Real Performance Metrics: Tree vs Baseline vs Oracle',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(results_df['objective'].values)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {OUTPUT_PNG}")
    plt.close()


def main():
    """Main execution."""
    print("="*80)
    print("STEP 13: Calculate Real Performance Metrics (Tree vs Baseline vs Oracle)")
    print("="*80)

    # Load data
    test_df, algo_metrics_df = load_data()

    # Calculate metrics for each objective
    results_list = []

    for objective, config in OBJECTIVES.items():
        try:
            result = calculate_objective_metrics(
                objective,
                test_df,
                algo_metrics_df,
                config
            )
            results_list.append(result)
        except Exception as e:
            print(f"\n❌ Error processing {objective}: {e}")
            continue

    # Create results table
    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80)
    results_table = create_results_table(results_list)
    print(results_table.to_string(index=False))

    # Save results
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)
    results_df = save_results(results_list)

    # Create visualization
    print("\n" + "="*80)
    print("CREATING VISUALIZATION")
    print("="*80)
    create_visualization(results_df)

    print("\n" + "="*80)
    print("STEP 13 COMPLETE!")
    print("="*80)

    return results_df


if __name__ == '__main__':
    results_df = main()