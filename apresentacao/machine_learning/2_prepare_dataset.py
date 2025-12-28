#!/usr/bin/env python3
"""
Step 2: Feature engineering and label creation.

Input:  datasets/vnr_raw_data.csv
Output: datasets/vnr_features.csv (with engineered features and labels)
"""

import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path

# Cache for solving times to avoid repeated file reads
_solving_time_cache = {}


def get_solving_time_from_summary(algorithm, topology, seed):
    """
    Get solving time from summary.csv of the matching simulation run.
    Solving time = clock_running_time / success_count
    If no summary found or success_count is 0, default to 900 seconds (15 minutes).
    Uses caching to avoid repeated file reads.
    """
    # Check cache first
    cache_key = (algorithm, seed)
    if cache_key in _solving_time_cache:
        return _solving_time_cache[cache_key]

    # Build pattern to find matching simulation folder
    pattern = f"../simulacoes/{algorithm}/**/summary.csv"
    files = glob.glob(pattern, recursive=True)

    for summary_file in files:
        try:
            summary_df = pd.read_csv(summary_file)
            if len(summary_df) > 0:
                row = summary_df.iloc[0]
                # Check if seed matches (if seed column exists)
                if 'seed' in summary_df.columns:
                    if row['seed'] != seed:
                        continue

                clock_time = row.get('clock_running_time', 900.0)
                success_count = row.get('success_count', 1)

                # Avoid division by zero
                if success_count > 0:
                    solving_time = clock_time / success_count
                    _solving_time_cache[cache_key] = solving_time
                    return solving_time
        except Exception:
            pass

    # Default to 15 minutes (900 seconds) if not found
    _solving_time_cache[cache_key] = 900.0
    return 900.0


def create_features(df):
    """Engineer features from raw VNR data."""

    print("Creating engineered features...")

    # Solving time: average clock running time per VNR
    # Get from summary.csv: clock_running_time / success_count
    print("  Computing solving time from simulation summaries...")
    df['solving_time'] = df.apply(
        lambda row: get_solving_time_from_summary(row['algorithm'], row['topology'], row['seed']),
        axis=1
    )

    # Physical network sizes (hardcoded for each topology)
    # Tree: 15 switches + 16 hosts = 31 nodes
    # Fat-Tree k=4: 20 nodes (4 core + 8 aggregation + 8 edge switches)
    # Waxman_16: 16 nodes (Waxman-generated topology)
    df['p_net_num_nodes'] = df['topology'].map({'tree': 31, 'fat_tree': 20, 'waxman_16': 16})

    # VNR size features
    df['v_net_size_ratio'] = df['v_net_num_nodes'] / df['p_net_num_nodes']
    df['v_net_demand_per_node'] = df['v_net_node_demand'] / df['v_net_num_nodes']
    df['v_net_demand_per_link'] = df['v_net_link_demand'] / (df['v_net_num_edges'] + 1e-9)  # Avoid div by 0

    # VNR connectivity (density)
    max_edges = df['v_net_num_nodes'] * (df['v_net_num_nodes'] - 1) / 2
    df['v_net_connectivity'] = df['v_net_num_edges'] / (max_edges + 1e-9)

    # Resource intensity
    df['v_net_total_demand'] = df['v_net_node_demand'] + df['v_net_link_demand']
    df['v_net_node_to_link_demand_ratio'] = df['v_net_node_demand'] / (df['v_net_link_demand'] + 1e-9)

    # Physical network utilization
    df['p_net_overall_util'] = 1 - (df['p_net_available_resource'] / 10457)  # Initial total resource
    df['p_net_node_util'] = df['p_net_node_resource_utilization']
    df['p_net_link_util'] = df['p_net_link_resource_utilization']

    # System load
    max_inservice = df['inservice_count'].max()
    df['system_load'] = df['inservice_count'] / (max_inservice + 1e-9)


    # Categorical encoding (NOW WITH WAXMAN_16 SUPPORT!)
    df['topology_encoded'] = df['topology'].map({'tree': 0, 'fat_tree': 1, 'waxman_16': 2})

    print(f"  ✓ Created {df.shape[1]} total features")

    return df


def compute_algorithm_cost(row, df_stats):
    """
    Multi-objective cost function for algorithm selection (R2C-Heavy).
    Lower cost = better algorithm for this state.

    Cost = w1 * success_penalty + w2 * time_metric + w3 * (1 - r2c_metric)

    Weights (priorities):
      w1 = 0.20 (Success - maximize acceptance)
      w2 = 0.20 (Speed - minimize wall-clock time)
      w3 = 0.60 (R2C Profitability - maximize revenue/cost ratio)

    Three objectives:
      1. Success: Did the embedding work?
      2. Time: How long did it take (real CPU time from clock_running_time)?
      3. Profitability: Revenue to Cost ratio (higher R2C = more profitable)

    Args:
        row: Single row from dataframe (one algorithm's result on one VNR)
        df_stats: Dict with normalization constants {max_clock_time, max_r2c}

    Returns:
        float: Cost score (0 to 1, lower is better)
    """
    w1, w2, w3 = 0.20, 0.20, 0.60

    # Component 1: Success penalty
    # If embedding succeeded: cost = 0 (no penalty)
    # If embedding failed: cost = 1 (maximum penalty)
    success_penalty = 0.0 if row['success'] else 1.0

    # Component 2: Time metric (normalized clock_running_time / success_count)
    # Real wall-clock time in seconds (from summary.csv)
    # Lower time = faster = better
    # Normalized to [0, 1] where 1 = slowest algorithm
    max_clock_time = df_stats['max_clock_time']
    if max_clock_time > 0 and pd.notna(row['clock_time_per_vnr']):
        time_metric = row['clock_time_per_vnr'] / max_clock_time
    else:
        time_metric = 0.0

    # Component 3: R2C metric (Revenue to Cost ratio)
    # R2C = v_net_revenue / v_net_cost
    # Higher R2C = more profitable = better
    # We want to maximize R2C, so we use (1 - normalized_r2c) to minimize
    max_r2c = df_stats['max_r2c']
    if max_r2c > 0 and pd.notna(row['v_net_r2c_ratio']):
        # Normalize R2C to [0, 1] range
        normalized_r2c = row['v_net_r2c_ratio'] / max_r2c
        # For cost function: lower is better, so we invert it (1 - r2c)
        # High R2C → low cost, Low R2C → high cost
        r2c_metric = 1.0 - min(normalized_r2c, 1.0)
    else:
        r2c_metric = 0.5  # Default to neutral if R2C unavailable

    # Combine into single cost function (lower = better)
    cost = (
        w1 * success_penalty +      # Penalize failures (30%)
        w2 * time_metric +          # Penalize slow algorithms (25%)
        w3 * r2c_metric             # Penalize low profitability (45%)
    )

    return cost


def create_labels(df):
    """
    For each unique VNR (identified by topology, seed, v_net_id),
    determine the best algorithm for EACH of 5 objectives:

    1. RAC (Request Acceptance Rate) - Maximize acceptance
    2. LRC (Long-Term Revenue-to-Cost) - Maximize cost-efficiency
    3. LAR (Long-Term Average Revenue) - Maximize revenue
    4. AST (Average Solving Time) - Minimize solving time
    5. BALANCED (Composite) - Maximize (0.8*revenue - 0.2*time) [only if accepted]

    This multi-objective approach allows switching objectives at runtime.
    """

    print("\nCreating multi-objective labels (RAC, LRC, LAR, AST, BALANCED)...")

    # Group by VNR instance (same VNR tested with different algorithms)
    vnr_groups = df.groupby(['topology', 'seed', 'v_net_id'])

    labels_list = []

    for (topo, seed, vnr_id), group in vnr_groups:
        # FIX: When there are multiple events per algorithm (from raw data),
        # we need to aggregate by algorithm FIRST to get one row per algorithm
        # This fixes num_algos_accepted which should count algorithms (1-8), not events (1-220)

        # Aggregate multiple events per algorithm (take first event per algo)
        group_per_algo = group.groupby('algorithm').first().reset_index()

        # For each objective, find the best algorithm

        # Objective 1: RAC - Request Acceptance Rate (maximize success)
        accepted = group_per_algo[group_per_algo['success'] == True]
        if len(accepted) > 0:
            # All accepted ones are equally good for RAC, pick first
            best_for_rac = accepted.iloc[0]['algorithm']
        else:
            best_for_rac = None

        # Objective 2: LRC - Long-Term Revenue-to-Cost (maximize r2c_ratio)
        valid_r2c = group_per_algo[group_per_algo['v_net_r2c_ratio'].notna()]
        if len(valid_r2c) > 0:
            best_lrc_idx = valid_r2c['v_net_r2c_ratio'].idxmax()
            best_for_lrc = valid_r2c.loc[best_lrc_idx, 'algorithm']
        else:
            best_for_lrc = None

        # Objective 3: LAR - Long-Term Average Revenue (maximize revenue)
        valid_revenue = group_per_algo[group_per_algo['v_net_revenue'].notna()]
        if len(valid_revenue) > 0:
            best_lar_idx = valid_revenue['v_net_revenue'].idxmax()
            best_for_lar = valid_revenue.loc[best_lar_idx, 'algorithm']
        else:
            best_for_lar = None

        # Objective 4: AST - Average Solving Time (minimize time)
        # Use solving_time if available, otherwise use clock_time_per_vnr
        time_column = 'solving_time' if 'solving_time' in group_per_algo.columns else 'clock_time_per_vnr'
        valid_time = group_per_algo[group_per_algo[time_column].notna()]
        if len(valid_time) > 0:
            best_ast_idx = valid_time[time_column].idxmin()
            best_for_ast = valid_time.loc[best_ast_idx, 'algorithm']
        else:
            best_for_ast = None

        # Objective 5: BALANCED - Composite objective
        # ONLY for accepted VNRs (success == True)
        # score = 0.8 * v_net_revenue - 0.2 * solving_time
        # Maximize revenue, minimize time
        # If not accepted: score = 0 (disqualified)
        valid_balanced = group_per_algo[
            (group_per_algo['success'] == True) &  # MUST be accepted
            (group_per_algo['v_net_revenue'].notna()) &
            (group_per_algo[time_column].notna())
        ].copy()
        if len(valid_balanced) > 0:
            valid_balanced['balanced_score'] = (
                0.8 * valid_balanced['v_net_revenue'] -
                0.2 * valid_balanced[time_column]
            )
            best_balanced_idx = valid_balanced['balanced_score'].idxmax()
            best_for_balanced = valid_balanced.loc[best_balanced_idx, 'algorithm']
        else:
            best_for_balanced = None

        # Assign labels to all rows in this group
        for idx in group.index:
            labels_list.append({
                'index': idx,
                'best_for_rac': best_for_rac,           # Request Acceptance Rate
                'best_for_lrc': best_for_lrc,           # Long-Term Revenue-to-Cost
                'best_for_lar': best_for_lar,           # Long-Term Average Revenue
                'best_for_ast': best_for_ast,           # Average Solving Time
                'best_for_balanced': best_for_balanced, # Composite: 0.8*revenue - 0.2*time (only if accepted)
                'num_algos_accepted': len(accepted)
            })

    # Join labels back to main dataframe
    labels_df = pd.DataFrame(labels_list).set_index('index')
    df = df.join(labels_df)

    # Statistics
    total_vnrs = vnr_groups.ngroups
    num_algos = df['algorithm'].nunique()

    print(f"\n  Label creation results:")
    print(f"    Total unique VNRs: {total_vnrs}")
    print(f"    Avg algos per VNR: {len(df) / total_vnrs:.1f}")

    print(f"\n  📊 RAC (Request Acceptance Rate) - which algo maximizes acceptance?")
    rac_counts = df['best_for_rac'].value_counts()
    for algo, count in rac_counts.items():
        pct = (count / total_vnrs) * 100
        print(f"    {algo:15s}: {count:6d} VNRs ({pct:5.1f}%)")
    print(f"    (No acceptable algo: {df['best_for_rac'].isna().sum() // num_algos})")

    print(f"\n  💰 LRC (Revenue-to-Cost) - which algo maximizes profitability?")
    lrc_counts = df['best_for_lrc'].value_counts()
    for algo, count in lrc_counts.items():
        pct = (count / total_vnrs) * 100
        print(f"    {algo:15s}: {count:6d} VNRs ({pct:5.1f}%)")
    print(f"    (Missing R2C data: {df['best_for_lrc'].isna().sum() // num_algos})")

    print(f"\n  💵 LAR (Average Revenue) - which algo maximizes revenue?")
    lar_counts = df['best_for_lar'].value_counts()
    for algo, count in lar_counts.items():
        pct = (count / total_vnrs) * 100
        print(f"    {algo:15s}: {count:6d} VNRs ({pct:5.1f}%)")
    print(f"    (Missing revenue data: {df['best_for_lar'].isna().sum() // num_algos})")

    print(f"\n  ⚡ AST (Average Solving Time) - which algo is fastest?")
    ast_counts = df['best_for_ast'].value_counts()
    for algo, count in ast_counts.items():
        pct = (count / total_vnrs) * 100
        print(f"    {algo:15s}: {count:6d} VNRs ({pct:5.1f}%)")
    print(f"    (Missing time data: {df['best_for_ast'].isna().sum() // num_algos})")

    print(f"\n  ⚖️  BALANCED (Composite: 0.8*revenue - 0.2*time) - which algo balances profit & speed?")
    balanced_counts = df['best_for_balanced'].value_counts()
    for algo, count in balanced_counts.items():
        pct = (count / total_vnrs) * 100
        print(f"    {algo:15s}: {count:6d} VNRs ({pct:5.1f}%)")
    print(f"    (Not accepted or missing data: {df['best_for_balanced'].isna().sum() // num_algos})")

    return df




def remove_unnecessary_columns(df):
    """Remove metadata and data-leakage columns (but keep the 4 objective labels!)."""

    columns_to_remove = [
        'seed',                  # Metadata, not a VNR feature
        'v_net_id',              # Pure ID, no predictive value
        'topology',              # Use topology_encoded instead
        'v_net_arrival_time',    # Data leakage - temporal info not available at decision time
        'algorithm',             # Data leakage - result of algorithm execution
        'success',               # Data leakage - result of algorithm execution
        'v_net_r2c_ratio',       # Data leakage - result of algorithm execution
        'v_net_revenue',         # Data leakage - result of algorithm execution
        'v_net_cost',            # Data leakage - result of algorithm execution
        'clock_time_per_vnr',    # Data leakage - solving time result
        'num_interactions',      # Data leakage - result of algorithm execution
        'event_time'             # Data leakage - temporal info
    ]

    # Only remove columns that exist
    cols_to_remove = [col for col in columns_to_remove if col in df.columns]

    if cols_to_remove:
        print(f"\nRemoving data-leakage columns: {cols_to_remove}")
        df = df.drop(columns=cols_to_remove)

    # Make sure the 5 objective labels are preserved!
    required_labels = ['best_for_rac', 'best_for_lrc', 'best_for_lar', 'best_for_ast', 'best_for_balanced']
    missing_labels = [label for label in required_labels if label not in df.columns]
    if missing_labels:
        print(f"  ⚠️  WARNING: Missing objective labels: {missing_labels}")

    return df


def save_datasets(train_df, val_df, test_df, output_dir='datasets'):
    """Save train/val/test splits."""

    os.makedirs(output_dir, exist_ok=True)

    train_df.to_csv(f'{output_dir}/train.csv', index=False)
    val_df.to_csv(f'{output_dir}/val.csv', index=False)
    test_df.to_csv(f'{output_dir}/test.csv', index=False)

    print(f"\n✓ Saved datasets to {output_dir}/")
    print(f"  train.csv: {train_df.shape}")
    print(f"  val.csv:   {val_df.shape}")
    print(f"  test.csv:  {test_df.shape}")


def assign_algorithm_specific_solving_times(df):
    """
    Assign algorithm-specific solving times to each row.

    Problem: Original solving_time was constant for all rows (2.367834s),
    preventing the model from learning algorithm characteristics.

    Solution: Compute average solving time PER ALGORITHM (not per best_overall label).
    This avoids data leakage where solving_time would reveal the target variable.
    """
    print("\nAssigning algorithm-specific solving times...")

    # Compute average solving time per algorithm from raw data
    # This is the ALGORITHM that was used in the simulation, not the best_overall label
    algo_solving_times = df.groupby('algorithm')['solving_time'].mean()

    print("  Algorithm-specific solving times:")
    for algo, solving_time in sorted(algo_solving_times.items(), key=lambda x: x[1], reverse=True):
        print(f"    {algo:15s}: {solving_time:.6f} seconds")

    # Map each row's ALGORITHM (not best_overall) to its solving time
    # This represents the computational cost of each algorithm in general
    df['solving_time'] = df['algorithm'].map(algo_solving_times)

    # Verify we have values
    print(f"\n  Unique solving_time values after assignment: {df['solving_time'].nunique()}")
    print(f"  Solving time range: {df['solving_time'].min():.6f} - {df['solving_time'].max():.6f}")

    return df


def engineer_features(df):
    """Add engineered features to improve algorithm discrimination."""

    print("\n🔧 Engineering new features...")

    # 1. Network Stress Index
    # Combines node and link utilization - shows how stressed the physical network is
    df['network_stress_index'] = (df['p_net_node_util'] + df['p_net_link_util']) / 2

    # 2. Problem Complexity Score
    # Higher = more complex problem requiring better algorithms
    df['problem_complexity'] = df['v_net_connectivity'] * df['v_net_total_demand']

    # 3. Resource Bottleneck Type
    # Ratio shows whether problem is CPU-bound or Bandwidth-bound
    df['resource_bottleneck_ratio'] = (
        df['v_net_demand_per_node'] / (df['v_net_demand_per_link'] + 1e-6)
    )

    # 4. VNR Size Category (encoded)
    # Larger networks need more sophisticated algorithms
    df['vnr_size_category'] = pd.cut(
        df['v_net_num_nodes'],
        bins=[0, 4, 7, 15],
        labels=[0, 1, 2],  # small, medium, large
        ordered=False
    ).astype(int)

    # 5. CPU Intensive Flag
    # True if node demand is much higher than link demand
    df['cpu_intensive_flag'] = (
        df['v_net_demand_per_node'] > df['v_net_demand_per_link']
    ).astype(int)

    # 6. Bandwidth Intensive Flag
    # True if link demand is much higher than node demand
    df['bandwidth_intensive_flag'] = (
        df['v_net_demand_per_link'] > df['v_net_demand_per_node']
    ).astype(int)

    # 7. Utilization Pressure
    # Shows how congested the network is
    df['utilization_pressure'] = df['p_net_node_util'] * df['p_net_link_util']

    # 8. Resource Efficiency Metric
    # How efficiently can we fit this VNR given current network state
    df['resource_efficiency'] = (
        df['p_net_available_resource'] / (df['v_net_total_demand'] + 1e-6)
    )

    print("  ✓ network_stress_index")
    print("  ✓ problem_complexity")
    print("  ✓ resource_bottleneck_ratio")
    print("  ✓ vnr_size_category")
    print("  ✓ cpu_intensive_flag")
    print("  ✓ bandwidth_intensive_flag")
    print("  ✓ utilization_pressure")
    print("  ✓ resource_efficiency")

    return df


def fix_dataset(df):
    """
    Fix dataset: Create one row per VNR (not per algorithm run).
    Remove data leakage columns.
    Assign algorithm-specific solving times.
    Add engineered features.
    """
    print("\nFixing dataset (one row per VNR)...")
    print(f"Original dataset: {len(df)} rows")
    print(f"Unique VNRs: {df.groupby(['topology', 'seed', 'v_net_id']).ngroups}")

    # Group by unique VNR and keep only one row per VNR
    # Take the first occurrence (they all have same VNR features, different only in algorithm/success/solving_time)
    vnr_unique = df.groupby(['topology', 'seed', 'v_net_id']).first().reset_index()

    # Remove columns that are results of algorithm execution (data leakage)
    # NOTE: solving_time is NOW REMOVED because you don't know it before choosing the algorithm!
    # Even though it's "average per algorithm", it still reveals which algorithm you chose.
    columns_to_remove = ['algorithm', 'success', 'v_net_r2c_ratio',
                         'v_net_revenue', 'v_net_cost', 'num_interactions', 'event_time',
                         'solving_time']

    # Keep only columns that are known BEFORE running any algorithm
    features_to_keep = [col for col in vnr_unique.columns if col not in columns_to_remove]

    vnr_clean = vnr_unique[features_to_keep].copy()

    print(f"\nCleaned dataset: {len(vnr_clean)} rows")
    print(f"Features before engineering: {len(vnr_clean.columns)}")

    # Engineer new features
    vnr_clean = engineer_features(vnr_clean)

    print(f"Features after engineering: {len(vnr_clean.columns)}")
    print(f"\nTarget distribution:")
    # Check which label columns exist
    label_cols = ['best_for_rac', 'best_for_lrc', 'best_for_lar', 'best_for_ast', 'best_for_balanced']
    for label_col in label_cols:
        if label_col in vnr_clean.columns:
            print(f"\n{label_col}:")
            print(vnr_clean[label_col].value_counts())

    # Save cleaned dataset
    vnr_clean.to_csv('datasets/vnr_clean.csv', index=False)
    print(f"\n✓ Saved: datasets/vnr_clean.csv")

    return vnr_clean


def add_real_clock_times(df):
    """
    Add real wall-clock execution time from summary.csv files.
    Maps clock_running_time / success_count to each (algorithm, seed) pair.
    """
    import glob
    from collections import defaultdict

    print("\nAdding real clock times from summary.csv files...")

    # Extract clock_running_time per (algorithm, seed)
    algo_seed_times = defaultdict(list)
    summary_files = glob.glob('../simulacoes/**/summary.csv', recursive=True)

    for summary_file in summary_files:
        try:
            df_sum = pd.read_csv(summary_file)
            if 'solver_name' in df_sum.columns and 'seed' in df_sum.columns and 'clock_running_time' in df_sum.columns:
                algo = df_sum['solver_name'].iloc[0]
                seed = int(df_sum['seed'].iloc[0])
                clock_time = df_sum['clock_running_time'].iloc[0]
                success_count = df_sum.get('success_count', [1]).iloc[0] if 'success_count' in df_sum.columns else 1

                if success_count > 0 and clock_time >= 0:
                    time_per_vnr = clock_time / 1000.0  # 1000 VNRs per simulation
                    algo_seed_times[(algo, seed)].append(time_per_vnr)
        except:
            pass

    # Average time per (algorithm, seed)
    time_lookup = {}
    for (algo, seed), times in algo_seed_times.items():
        time_lookup[(algo, seed)] = np.mean(times)

    # Map to dataframe
    df['clock_time_per_vnr'] = df.apply(
        lambda row: time_lookup.get((row['algorithm'], row['seed']), np.nan),
        axis=1
    )

    # Fill NaNs with algorithm average
    for algo in df['algorithm'].unique():
        algo_times = [v for (a, s), v in time_lookup.items() if a == algo]
        if algo_times:
            avg_time = np.mean(algo_times)
            df.loc[(df['algorithm'] == algo) & (df['clock_time_per_vnr'].isna()), 'clock_time_per_vnr'] = avg_time

    print(f"  ✓ Added clock_time_per_vnr for {len(time_lookup)} algorithm-seed pairs")
    print(f"  ✓ Filled missing values with algorithm averages")

    return df


if __name__ == '__main__':
    # Load raw data from all topologies
    print("Loading raw VNR data from all topologies...")

    dfs = []

    # Load Tree topology
    if os.path.exists('datasets/vnr_raw_data.csv'):
        df_tree = pd.read_csv('datasets/vnr_raw_data.csv')
        print(f"  ✓ Tree topology: {len(df_tree)} records")
        dfs.append(df_tree)

    # Load Fat-Tree topology (should already be in vnr_raw_data.csv)
    # (Fat-Tree data is combined with Tree in the main vnr_raw_data.csv)

    # Load Waxman_16 topology
    if os.path.exists('datasets/waxman_16_raw_data.csv'):
        df_waxman = pd.read_csv('datasets/waxman_16_raw_data.csv')
        print(f"  ✓ Waxman_16 topology: {len(df_waxman)} records")
        dfs.append(df_waxman)
    else:
        print(f"  ✗ Waxman_16 data not found at datasets/waxman_16_raw_data.csv")

    # Combine all topologies
    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        print(f"\nTotal records combined: {len(df)}")
        print(f"Topologies: {sorted(df['topology'].unique())}\n")
    else:
        print("ERROR: No data files found!")
        exit(1)

    # Add real clock times
    df = add_real_clock_times(df)

    # Feature engineering
    df = create_features(df)

    # Create labels
    df = create_labels(df)

    # Remove solving_time BEFORE saving vnr_features.csv
    # Reason: solving_time is a data leakage feature (you don't know it before choosing algorithm)
    if 'solving_time' in df.columns:
        df = df.drop(columns=['solving_time'])
        print("  ✓ Removed solving_time (data leakage)")

    # Save full dataset with features (WITHOUT solving_time)
    df.to_csv('datasets/vnr_features.csv', index=False)
    print(f"\n✓ Saved full dataset with features: datasets/vnr_features.csv")

    # NOTE: Removed call to assign_algorithm_specific_solving_times()
    # (We removed solving_time entirely, so no need to assign it)

    # Fix dataset: one row per VNR, remove data leakage
    vnr_clean = fix_dataset(df)

    # Remove rows where no algorithm succeeded for RAC objective
    vnr_clean = vnr_clean[vnr_clean['best_for_rac'].notna()].copy()

    # Remove rare classes (< 10 samples) for stratified split stability
    from sklearn.model_selection import train_test_split

    print(f"\nRemoving rare algorithm classes (< 10 samples) for split stability...")
    class_counts = vnr_clean['best_for_rac'].value_counts()
    rare_classes = class_counts[class_counts < 10].index.tolist()

    if rare_classes:
        print(f"  Removing classes: {rare_classes}")
        vnr_clean = vnr_clean[~vnr_clean['best_for_rac'].isin(rare_classes)].copy()
        print(f"  Remaining VNRs: {len(vnr_clean)}")

    print(f"\nSplitting data into train/val/test with stratification...")

    # First split: 70/30 for train / (val+test)
    # Stratify by target class to ensure balanced distribution
    train_df, val_test_df = train_test_split(
        vnr_clean, test_size=0.3, random_state=42, stratify=vnr_clean['best_for_rac']
    )

    # Second split: 50/50 of val_test for val / test (results in 70/15/15 overall)
    # Stratify by target class in the val_test subset
    val_df, test_df = train_test_split(
        val_test_df, test_size=0.5, random_state=42, stratify=val_test_df['best_for_rac']
    )

    print(f"\nSplit:")
    print(f"  Train: {len(train_df)} VNRs ({len(train_df)/len(vnr_clean)*100:.1f}%)")
    print(f"  Val:   {len(val_df)} VNRs ({len(val_df)/len(vnr_clean)*100:.1f}%)")
    print(f"  Test:  {len(test_df)} VNRs ({len(test_df)/len(vnr_clean)*100:.1f}%)")

    # Remove unnecessary columns before saving
    train_df = remove_unnecessary_columns(train_df)
    val_df = remove_unnecessary_columns(val_df)
    test_df = remove_unnecessary_columns(test_df)

    # Save splits
    save_datasets(train_df, val_df, test_df)

    print(f"\nTrain distribution (best_for_rac):")
    print(train_df['best_for_rac'].value_counts())
    print(f"\nVal distribution (best_for_rac):")
    print(val_df['best_for_rac'].value_counts())
    print(f"\nTest distribution (best_for_rac):")
    print(test_df['best_for_rac'].value_counts())

    print("\n" + "="*80)
    print("Dataset preparation complete!")
    print("="*80)
