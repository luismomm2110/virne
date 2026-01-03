#!/usr/bin/env python3
"""
Step 5: Evaluate Real Performance Improvement for Balanced Models

This script calculates the REAL PERFORMANCE improvement when using tree predictions
vs baseline (fixed algorithm) vs oracle (optimal algorithm).

For each objective (RAC, LRC, LAR):
1. TREE PERFORMANCE: Performance when using tree predictions
2. BASELINE PERFORMANCE: Performance when always using the most frequent optimal algorithm
3. ORACLE PERFORMANCE: Performance when always using the actual best algorithm

Approach:
- Load balanced decision tree models
- For each test VNR, get tree prediction
- Look up algorithm performance from algorithm_comparison_metrics.csv
- Compare aggregated performance
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import top_k_accuracy_score

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATASETS_PATH = PROJECT_ROOT / "datasets"
MODELS_PATH = PROJECT_ROOT / "models"
PIPELINE_PATH = Path(__file__).parent

# Input files
TEST_SET = DATASETS_PATH / "test.csv"
VNR_FEATURES = DATASETS_PATH / "vnr_features.csv"  # Full dataset with seed/v_net_id
VNR_RAW_DATA = DATASETS_PATH / "vnr_raw_data.csv"  # Individual VNR results per algorithm
ALGO_METRICS = MODELS_PATH / "algorithm_comparison_metrics.csv"
BALANCED_MODELS = MODELS_PATH / "decision_trees_balanced.pkl"
LABEL_ENCODER = MODELS_PATH / "algorithm_label_encoder.pkl"

# Output files
OUTPUT_CSV = MODELS_PATH / "balanced_performance_improvement.csv"
OUTPUT_JSON = MODELS_PATH / "balanced_performance_improvement.json"
OUTPUT_PNG = MODELS_PATH / "balanced_performance_improvement.png"

# Mapping of objectives to columns and metrics
OBJECTIVES = {
    "RAC": {
        "label_col": "best_for_rac",
        "metric_col": "acceptance_rate",
        "metric_name": "Acceptance Rate (%)",
        "higher_is_better": True,
    },
    "LRC": {
        "label_col": "best_for_lrc",
        "metric_col": "revenue_cost_ratio",
        "metric_name": "Revenue-to-Cost Ratio",
        "higher_is_better": True,
    },
    "LAR": {
        "label_col": "best_for_lar",
        "metric_col": "avg_revenue",  # Note: LAR is typically avg revenue per VNR
        "metric_name": "Average Revenue per VNR",
        "higher_is_better": True,
    },
}

# Note: For LAR, we might need to calculate from total_revenue / num_records
# Let's check if avg_revenue exists, otherwise calculate it


def load_data():
    """Load all required data."""
    print("Loading data...")
    test_df = pd.read_csv(TEST_SET)
    
    # Load full dataset with identifiers (has seed, v_net_id, topology)
    print("  Loading full dataset with identifiers...")
    vnr_features_df = pd.read_csv(VNR_FEATURES)
    
    # Load individual VNR results (this has actual performance per VNR per algorithm)
    print("  Loading individual VNR results...")
    vnr_raw_df = pd.read_csv(VNR_RAW_DATA)
    
    # Merge test_df with vnr_features_df to get seed and v_net_id
    # Use feature columns that should be unique per VNR to match
    # Match on features that uniquely identify a VNR (but without algorithm-specific columns)
    print("  Matching test.csv with vnr_features.csv to get identifiers...")
    
    # Features that uniquely identify a VNR (excluding algorithm-dependent and temporal features)
    matching_features = [
        'v_net_num_nodes', 'v_net_num_edges', 'v_net_lifetime',
        'v_net_demand', 'v_net_node_demand', 'v_net_link_demand',
        'p_net_available_resource', 'p_net_node_available_resource',
        'p_net_link_available_resource', 'inservice_count', 'num_running_p_net_nodes',
        'v_net_size_ratio', 'v_net_demand_per_node', 'v_net_demand_per_link',
        'v_net_connectivity', 'v_net_total_demand', 'v_net_node_to_link_demand_ratio'
    ]
    
    # Filter to only matching features that exist in both dataframes
    matching_features = [f for f in matching_features if f in test_df.columns and f in vnr_features_df.columns]
    
    # For each row in test_df, find matching row in vnr_features_df
    # Since there are multiple rows per VNR (one per algorithm) in vnr_features_df,
    # we'll take the first match after grouping by VNR identifiers
    vnr_features_unique = vnr_features_df.groupby(['topology', 'seed', 'v_net_id']).first().reset_index()
    
    # Merge on matching features
    test_df_with_ids = test_df.merge(
        vnr_features_unique[['topology', 'seed', 'v_net_id'] + matching_features],
        on=matching_features,
        how='left',
        suffixes=('', '_match')
    )
    
    # If merge didn't work well, try a simpler approach: match based on feature similarity
    matched_count = test_df_with_ids['seed'].notna().sum()
    print(f"  Matched {matched_count}/{len(test_df)} VNRs using feature matching")
    
    if matched_count < len(test_df) * 0.9:
        print("  ⚠️  Warning: Low match rate. Using vnr_features_df directly for test split...")
        # Alternative: use vnr_features_df and filter to test split indices
        # This assumes test.csv has same order as vnr_features_df was split
        if len(test_df) == len(vnr_features_unique):
            print("  → Using positional matching (assuming same order)")
            test_df_with_ids = test_df.copy()
            test_df_with_ids['topology'] = vnr_features_unique['topology'].values[:len(test_df)]
            test_df_with_ids['seed'] = vnr_features_unique['seed'].values[:len(test_df)]
            test_df_with_ids['v_net_id'] = vnr_features_unique['v_net_id'].values[:len(test_df)]
        else:
            # Last resort: try to match using fewer features
            print("  → Trying simplified matching...")
            simple_features = ['v_net_num_nodes', 'v_net_num_edges', 'v_net_lifetime']
            simple_features = [f for f in simple_features if f in test_df.columns and f in vnr_features_unique.columns]
            test_df_with_ids = test_df.merge(
                vnr_features_unique[['topology', 'seed', 'v_net_id'] + simple_features],
                on=simple_features,
                how='left'
            )
            matched_count = test_df_with_ids['seed'].notna().sum()
            print(f"  Matched {matched_count}/{len(test_df)} VNRs with simplified matching")
    
    # Ensure topology_name column
    if 'topology' in test_df_with_ids.columns:
        test_df_with_ids['topology_name'] = test_df_with_ids['topology']
    elif 'topology_encoded' in test_df_with_ids.columns:
        topology_map = {0: 'tree', 1: 'fat_tree', 2: 'waxman_16'}
        test_df_with_ids['topology_name'] = test_df_with_ids['topology_encoded'].map(topology_map).fillna('unknown')
    else:
        test_df_with_ids['topology_name'] = 'unknown'
    
    algo_metrics_df = pd.read_csv(ALGO_METRICS)
    
    # Calculate avg_revenue if it doesn't exist (for LAR)
    if 'avg_revenue' not in algo_metrics_df.columns and 'total_revenue' in algo_metrics_df.columns:
        algo_metrics_df['avg_revenue'] = algo_metrics_df['total_revenue'] / algo_metrics_df['num_records']

    print(f"  Test set: {len(test_df_with_ids)} VNRs")
    print(f"  VNR raw data: {len(vnr_raw_df)} records (multiple algorithms per VNR)")
    print(f"  Algorithm metrics: {len(algo_metrics_df)} algorithms")
    print(f"  VNRs with valid identifiers: {test_df_with_ids['seed'].notna().sum()}")

    return test_df_with_ids, vnr_raw_df, algo_metrics_df


def load_balanced_models():
    """Load balanced decision trees and label encoder."""
    print("Loading balanced models...")
    
    if not BALANCED_MODELS.exists():
        raise FileNotFoundError(f"Balanced models not found: {BALANCED_MODELS}")
    if not LABEL_ENCODER.exists():
        raise FileNotFoundError(f"Label encoder not found: {LABEL_ENCODER}")

    with open(BALANCED_MODELS, 'rb') as f:
        models = pickle.load(f)
    
    with open(LABEL_ENCODER, 'rb') as f:
        label_encoder = pickle.load(f)

    print(f"  Loaded models for: {list(models.keys())}")
    return models, label_encoder


def get_features_for_model(model, test_df):
    """Extract and prepare features matching the model's expectations."""
    # Get feature names from model if available
    if hasattr(model, 'feature_names_in_'):
        expected_features = list(model.feature_names_in_)
    else:
        # Fallback: use common features
        expected_features = [
            'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
            'v_net_demand_per_node', 'v_net_demand_per_link', 'v_net_connectivity',
            'v_net_total_demand', 'v_net_node_to_link_demand_ratio', 'v_net_lifetime',
            'p_net_available_resource', 'p_net_node_util', 'p_net_link_util',
            'p_net_overall_util', 'inservice_count', 'num_running_p_net_nodes',
            'topology_encoded', 'network_stress_index', 'problem_complexity',
            'resource_bottleneck_ratio', 'vnr_size_category', 'cpu_intensive_flag',
            'bandwidth_intensive_flag', 'utilization_pressure', 'resource_efficiency'
        ]
    
    # Add missing features with default value 0
    for feat in expected_features:
        if feat not in test_df.columns:
            test_df[feat] = 0.0
    
    # Select only expected features
    X_test = test_df[[f for f in expected_features if f in test_df.columns]]
    
    return X_test


def calculate_baseline_algorithm(test_df, objective_config):
    """Calculate baseline algorithm (most frequently optimal)."""
    label_col = objective_config["label_col"]
    if label_col not in test_df.columns:
        return None
    
    algo_counts = test_df[label_col].value_counts()
    if len(algo_counts) == 0:
        return None
    
    baseline_algo = algo_counts.index[0]
    baseline_freq = algo_counts.iloc[0] / len(test_df)
    
    return baseline_algo, baseline_freq


def calculate_best_global_algorithm(algo_metrics_df, objective_config):
    """Calculate best global algorithm (highest average performance)."""
    metric_col = objective_config["metric_col"]
    
    if metric_col not in algo_metrics_df.columns:
        return None
    
    # Find algorithm with highest metric value
    best_idx = algo_metrics_df[metric_col].idxmax()
    best_algo = algo_metrics_df.loc[best_idx, 'algorithm']
    best_value = algo_metrics_df.loc[best_idx, metric_col]
    
    return best_algo, best_value


def get_vnr_result(vnr_raw_df, topology, seed, v_net_id, algorithm):
    """Get individual VNR result for a specific algorithm."""
    # Try to match by topology, seed, v_net_id, and algorithm
    matches = vnr_raw_df[
        (vnr_raw_df['topology'] == topology) &
        (vnr_raw_df['seed'] == seed) &
        (vnr_raw_df['v_net_id'] == v_net_id) &
        (vnr_raw_df['algorithm'] == algorithm)
    ]
    
    if len(matches) > 0:
        # Return first match (should be unique)
        return matches.iloc[0]
    return None


def calculate_metric_from_result(result_row, objective):
    """Calculate objective metric from individual VNR result."""
    if result_row is None:
        return 0.0
    
    if objective == 'RAC':
        # Acceptance rate: 1 if success, 0 otherwise (will be averaged)
        return 1.0 if result_row.get('success', False) else 0.0
    elif objective == 'LRC':
        # Revenue-to-cost ratio
        revenue = float(result_row.get('v_net_revenue', 0) or 0)
        cost = float(result_row.get('v_net_cost', 0) or 0)
        if cost > 0:
            return revenue / cost
        return 0.0
    elif objective == 'LAR':
        # Average revenue (revenue per VNR)
        revenue = float(result_row.get('v_net_revenue', 0) or 0)
        return revenue
    else:
        return 0.0


def calculate_objective_performance(
    objective,
    test_df,
    vnr_raw_df,
    algo_metrics_df,
    objective_config,
    models,
    label_encoder
):
    """Calculate tree, baseline, and oracle performance using INDIVIDUAL VNR results."""
    
    obj_key = objective.lower()
    label_col = objective_config["label_col"]
    
    print(f"\n{'='*80}")
    print(f"Objective: {objective}")
    print(f"{'='*80}")
    
    # Check if model exists
    if obj_key not in models:
        print(f"  ⚠️  Model '{obj_key}' not found, skipping...")
        return None
    
    # Load model
    model = models[obj_key]
    
    # Prepare features
    X_test = get_features_for_model(model, test_df.copy())
    
    # Get tree predictions
    print("\n1. Making tree predictions...")
    y_pred_encoded = model.predict(X_test)
    y_pred = label_encoder.inverse_transform(y_pred_encoded)
    test_df['predicted_algo'] = y_pred
    
    # Get actual best algorithms (oracle)
    if label_col not in test_df.columns:
        print(f"  ⚠️  Column '{label_col}' not found in test data, skipping...")
        return None
    
    # Filter to rows where we have both prediction and actual best
    valid_mask = test_df[label_col].notna()
    test_df_valid = test_df[valid_mask].copy()
    
    print(f"   Valid predictions: {len(test_df_valid)}/{len(test_df)}")
    
    # Ensure we have required columns for matching
    required_cols = ['topology_name', 'seed', 'v_net_id']
    missing_cols = [c for c in required_cols if c not in test_df_valid.columns]
    if missing_cols:
        print(f"  ⚠️  Missing required columns: {missing_cols}")
        print(f"  Available columns: {list(test_df_valid.columns)}")
        return None
    
    # Calculate BASELINE PERFORMANCE (using individual VNR results)
    print("\n2. Calculating BASELINE PERFORMANCE (individual VNR results)...")
    baseline_algo, baseline_freq = calculate_baseline_algorithm(test_df, objective_config)
    
    if baseline_algo is None:
        print("  ⚠️  Cannot calculate baseline, skipping...")
        return None
    
    print(f"   Baseline algorithm (most frequent optimal): {baseline_algo} (optimal in {baseline_freq*100:.1f}% of cases)")
    
    # Also calculate best global algorithm
    best_global_algo, best_global_value = calculate_best_global_algorithm(algo_metrics_df, objective_config)
    print(f"   Best global algorithm (highest avg performance): {best_global_algo} (avg: {best_global_value:.4f})")
    
    # Calculate baseline (most frequent optimal)
    baseline_scores = []
    baseline_matched = 0
    
    for idx, row in test_df_valid.iterrows():
        topology = row['topology_name']
        seed = row.get('seed', -1)
        vnr_id = row.get('v_net_id', -1)
        
        if pd.isna(seed) or pd.isna(vnr_id) or topology == 'unknown':
            continue
        
        result = get_vnr_result(vnr_raw_df, topology, int(seed), int(vnr_id), baseline_algo)
        if result is not None:
            score = calculate_metric_from_result(result, objective)
            baseline_scores.append(score)
            baseline_matched += 1
    
    if len(baseline_scores) == 0:
        print("  ⚠️  No baseline matches found in VNR raw data")
        return None
    
    baseline_avg = np.mean(baseline_scores)
    print(f"   Baseline (most frequent optimal) performance: {baseline_avg:.4f} (matched {baseline_matched}/{len(test_df_valid)} VNRs)")
    
    # Calculate best global algorithm performance
    if best_global_algo and best_global_algo != baseline_algo:
        best_global_scores = []
        best_global_matched = 0
        
        for idx, row in test_df_valid.iterrows():
            topology = row['topology_name']
            seed = row.get('seed', -1)
            vnr_id = row.get('v_net_id', -1)
            
            if pd.isna(seed) or pd.isna(vnr_id) or topology == 'unknown':
                continue
            
            result = get_vnr_result(vnr_raw_df, topology, int(seed), int(vnr_id), best_global_algo)
            if result is not None:
                score = calculate_metric_from_result(result, objective)
                best_global_scores.append(score)
                best_global_matched += 1
        
        if len(best_global_scores) > 0:
            best_global_avg = np.mean(best_global_scores)
            print(f"   Best global algorithm performance: {best_global_avg:.4f} (matched {best_global_matched}/{len(test_df_valid)} VNRs)")
        else:
            best_global_avg = None
            best_global_algo = None
    else:
        best_global_avg = baseline_avg
        best_global_algo = baseline_algo
        print(f"   Best global algorithm is same as baseline: {baseline_algo}")
    
    # Calculate TREE PERFORMANCE (using individual VNR results)
    print("\n3. Calculating TREE PERFORMANCE (individual VNR results)...")
    tree_scores = []
    tree_matched = 0
    
    for idx, row in test_df_valid.iterrows():
        topology = row['topology_name']
        seed = row.get('seed', -1)
        vnr_id = row.get('v_net_id', -1)
        pred_algo = row['predicted_algo']
        
        if pd.isna(seed) or pd.isna(vnr_id) or topology == 'unknown':
            continue
        
        result = get_vnr_result(vnr_raw_df, topology, int(seed), int(vnr_id), pred_algo)
        if result is not None:
            score = calculate_metric_from_result(result, objective)
            tree_scores.append(score)
            tree_matched += 1
    
    if len(tree_scores) == 0:
        print("  ⚠️  No tree matches found in VNR raw data")
        return None
    
    tree_avg = np.mean(tree_scores)
    print(f"   Tree average performance: {tree_avg:.4f} (matched {tree_matched}/{len(test_df_valid)} VNRs)")
    
    # Calculate ORACLE PERFORMANCE (using individual VNR results)
    print("\n4. Calculating ORACLE PERFORMANCE (individual VNR results)...")
    oracle_scores = []
    oracle_matched = 0
    
    for idx, row in test_df_valid.iterrows():
        topology = row['topology_name']
        seed = row.get('seed', -1)
        vnr_id = row.get('v_net_id', -1)
        oracle_algo = row[label_col]
        
        if pd.isna(seed) or pd.isna(vnr_id) or topology == 'unknown' or pd.isna(oracle_algo):
            continue
        
        result = get_vnr_result(vnr_raw_df, topology, int(seed), int(vnr_id), oracle_algo)
        if result is not None:
            score = calculate_metric_from_result(result, objective)
            oracle_scores.append(score)
            oracle_matched += 1
    
    if len(oracle_scores) == 0:
        print("  ⚠️  No oracle matches found in VNR raw data")
        return None
    
    oracle_avg = np.mean(oracle_scores)
    print(f"   Oracle average performance: {oracle_avg:.4f} (matched {oracle_matched}/{len(test_df_valid)} VNRs)")
    
    # Calculate improvements
    improvement_vs_baseline = tree_avg - baseline_avg
    improvement_pct = (improvement_vs_baseline / baseline_avg * 100) if baseline_avg > 0 else 0
    gap_to_oracle = oracle_avg - tree_avg
    gap_pct = (gap_to_oracle / oracle_avg * 100) if oracle_avg > 0 else 0
    
    # Compare with best global algorithm if different
    if best_global_avg is not None and best_global_algo != baseline_algo:
        improvement_vs_best_global = tree_avg - best_global_avg
        improvement_vs_best_global_pct = (improvement_vs_best_global / best_global_avg * 100) if best_global_avg > 0 else 0
        print(f"\n   Results (using INDIVIDUAL VNR values):")
        print(f"   Tree vs baseline (most frequent): {improvement_vs_baseline:+.4f} ({improvement_pct:+.2f}%)")
        print(f"   Tree vs best global algorithm ({best_global_algo}): {improvement_vs_best_global:+.4f} ({improvement_vs_best_global_pct:+.2f}%)")
        print(f"   Gap to oracle: {gap_to_oracle:+.4f} ({gap_pct:+.2f}%)")
    else:
        print(f"\n   Results (using INDIVIDUAL VNR values):")
        print(f"   Tree improvement vs baseline: {improvement_vs_baseline:+.4f} ({improvement_pct:+.2f}%)")
        print(f"   Gap to oracle: {gap_to_oracle:+.4f} ({gap_pct:+.2f}%)")
        improvement_vs_best_global = None
        improvement_vs_best_global_pct = None
    
    result = {
        'objective': objective,
        'baseline_algorithm': baseline_algo,
        'baseline_frequency': baseline_freq,
        'baseline_metric': float(baseline_avg),
        'best_global_algorithm': best_global_algo if best_global_algo else None,
        'best_global_metric': float(best_global_avg) if best_global_avg else None,
        'tree_metric': float(tree_avg),
        'oracle_metric': float(oracle_avg),
        'improvement_vs_baseline': float(improvement_vs_baseline),
        'improvement_pct': float(improvement_pct),
        'improvement_vs_best_global': float(improvement_vs_best_global) if improvement_vs_best_global is not None else None,
        'improvement_vs_best_global_pct': float(improvement_vs_best_global_pct) if improvement_vs_best_global_pct is not None else None,
        'gap_to_oracle': float(gap_to_oracle),
        'gap_pct': float(gap_pct),
        'baseline_matched': baseline_matched,
        'tree_matched': tree_matched,
        'oracle_matched': oracle_matched,
    }
    
    return result


def create_visualization(results_list, output_file):
    """Create comparison visualization."""
    if not results_list:
        print("  ⚠️  No results to visualize")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    objectives = [r['objective'] for r in results_list]
    baseline_vals = [r['baseline_metric'] for r in results_list]
    tree_vals = [r['tree_metric'] for r in results_list]
    oracle_vals = [r['oracle_metric'] for r in results_list]
    
    x = np.arange(len(objectives))
    width = 0.25
    
    bars1 = ax.bar(x - width, baseline_vals, width, label='Baseline (Fixed Algo)', color='#FF6B6B', alpha=0.8)
    bars2 = ax.bar(x, tree_vals, width, label='Tree Predictions', color='#4ECDC4', alpha=0.8)
    bars3 = ax.bar(x + width, oracle_vals, width, label='Oracle (Optimal)', color='#95E1D3', alpha=0.8)
    
    ax.set_xlabel('Objective', fontsize=12, fontweight='bold')
    ax.set_ylabel('Performance Metric Value', fontsize=12, fontweight='bold')
    ax.set_title('Real Performance: Tree vs Baseline vs Oracle (Balanced Models)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(objectives)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved visualization: {output_file}")
    plt.close()


def save_results(results_list):
    """Save results to CSV and JSON."""
    if not results_list:
        print("  ⚠️  No results to save")
        return
    
    # Save CSV
    df = pd.DataFrame(results_list)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✓ Saved CSV: {OUTPUT_CSV}")
    
    # Save JSON
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results_list, f, indent=2)
    print(f"✓ Saved JSON: {OUTPUT_JSON}")


def print_summary_table(results_list):
    """Print formatted summary table."""
    if not results_list:
        return
    
    print("\n" + "="*80)
    print("SUMMARY: Real Performance Improvement")
    print("="*80)
    
    print(f"\n{'Objective':<12} {'Baseline':<12} {'Tree':<12} {'Oracle':<12} {'Improvement':<15} {'Gap to Oracle':<15}")
    print("-" * 80)
    
    for r in results_list:
        obj = r['objective']
        baseline = r['baseline_metric']
        tree = r['tree_metric']
        oracle = r['oracle_metric']
        improvement = r['improvement_vs_baseline']
        gap = r['gap_to_oracle']
        
        print(f"{obj:<12} {baseline:>11.2f} {tree:>11.2f} {oracle:>11.2f} {improvement:>+14.2f} {gap:>+14.2f}")
    
    print("\nImprovement = Tree - Baseline (higher is better)")
    print("Gap to Oracle = Oracle - Tree (lower is better)")


def main():
    """Main execution."""
    print("="*80)
    print("STEP 5: Evaluate Real Performance Improvement (Balanced Models)")
    print("="*80)
    
    # Load data
    test_df, vnr_raw_df, algo_metrics_df = load_data()
    
    # Load models
    models, label_encoder = load_balanced_models()
    
    # Calculate performance for each objective
    results_list = []
    
    for objective, config in OBJECTIVES.items():
        try:
            result = calculate_objective_performance(
                objective,
                test_df,
                vnr_raw_df,
                algo_metrics_df,
                config,
                models,
                label_encoder
            )
            if result:
                results_list.append(result)
        except Exception as e:
            print(f"\n❌ Error processing {objective}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Print summary
    print_summary_table(results_list)
    
    # Save results
    if results_list:
        save_results(results_list)
        create_visualization(results_list, OUTPUT_PNG)
    
    print("\n" + "="*80)
    print("✅ EVALUATION COMPLETE!")
    print("="*80)
    
    return results_list


if __name__ == '__main__':
    results = main()

