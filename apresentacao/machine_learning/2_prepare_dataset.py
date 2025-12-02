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

    # Physical network sizes (hardcoded for tree topology)
    # Tree: 15 switches + 16 hosts = 31 nodes
    # Fat-Tree k=4: 20 nodes (4 core + 8 aggregation + 8 edge switches)
    df['p_net_num_nodes'] = df['topology'].map({'tree': 31, 'fat_tree': 20})

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


    # Categorical encoding
    df['topology_encoded'] = df['topology'].map({'tree': 0, 'fat_tree': 1})

    print(f"  ✓ Created {df.shape[1]} total features")

    return df


def create_labels(df):
    """
    For each unique VNR (identified by topology, seed, v_net_id),
    determine the best algorithm based on different criteria.
    """

    print("\nCreating labels (best algorithm per VNR)...")

    # Group by VNR instance (same VNR tested with different algorithms)
    vnr_groups = df.groupby(['topology', 'seed', 'v_net_id'])

    labels_list = []

    for (topo, seed, vnr_id), group in vnr_groups:
        # Separate accepted and rejected
        accepted = group[group['success'] == True]
        rejected = group[group['success'] == False]

        # Label 1: Best for acceptance (prioritize acceptance, then speed)
        if len(accepted) > 0:
            best_for_acceptance = accepted.loc[accepted['solving_time'].idxmin(), 'algorithm']
        else:
            best_for_acceptance = group.iloc[0]['algorithm']  # No one accepted

        # Label 2: Best for time (fastest among those that accepted)
        if len(accepted) > 0:
            best_for_time = accepted.loc[accepted['solving_time'].idxmin(), 'algorithm']
        else:
            best_for_time = group.iloc[0]['algorithm']

        # Label 3: Best for Acceptance + Revenue + Speed
        # Priority 1: Accept the VNR (most important)
        # Priority 2: Maximize revenue (economic benefit)
        # Priority 3: Minimize time (operational efficiency)
        if len(accepted) > 0:
            accepted_copy = accepted.copy()

            # Among accepted, pick the one with highest revenue
            # If tie, pick fastest
            best_idx = accepted_copy['v_net_revenue'].idxmax()

            # Check for ties in revenue
            max_revenue = accepted_copy['v_net_revenue'].max()
            tied = accepted_copy[accepted_copy['v_net_revenue'] == max_revenue]

            if len(tied) > 1:
                # Break tie with solving time (faster is better)
                best_idx = tied['solving_time'].idxmin()

            best_overall = accepted_copy.loc[best_idx, 'algorithm']
        else:
            # No one accepted - doesn't matter for training
            best_overall = group.iloc[0]['algorithm']

        # Assign labels to all rows in this group
        for idx in group.index:
            labels_list.append({
                'index': idx,
                'best_for_acceptance': best_for_acceptance,
                'best_for_time': best_for_time,
                'best_overall': best_overall,
                'num_algos_accepted': len(accepted),
                'num_algos_rejected': len(rejected)
            })

    # Join labels back to main dataframe
    labels_df = pd.DataFrame(labels_list).set_index('index')
    df = df.join(labels_df)

    # Statistics
    print(f"  Total unique VNRs: {vnr_groups.ngroups}")
    print(f"  VNRs accepted by at least 1 algo: {df['best_for_acceptance'].notna().sum() // 7}")  # Divide by num algos
    print(f"  VNRs rejected by all algos: {df['best_for_acceptance'].isna().sum() // 7}")

    print("\n  Best algorithm distribution (best_overall):")
    print(df['best_overall'].value_counts())

    return df




def remove_unnecessary_columns(df):
    """Remove metadata and redundant label columns."""

    columns_to_remove = [
        'seed',                  # Metadata, not a VNR feature
        'v_net_id',              # Pure ID, no predictive value
        'topology',              # Use topology_encoded instead
        'best_for_acceptance',   # Redundant label (use best_overall)
        'best_for_time',         # Redundant label (use best_overall)
        'num_algos_accepted',    # Derived from best_overall
        'num_algos_rejected'     # Derived from best_overall
    ]

    # Only remove columns that exist
    cols_to_remove = [col for col in columns_to_remove if col in df.columns]

    if cols_to_remove:
        print(f"\nRemoving unnecessary columns: {cols_to_remove}")
        df = df.drop(columns=cols_to_remove)

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


def fix_dataset(df):
    """
    Fix dataset: Create one row per VNR (not per algorithm run).
    Remove data leakage columns.
    Assign algorithm-specific solving times.
    """
    print("\nFixing dataset (one row per VNR)...")
    print(f"Original dataset: {len(df)} rows")
    print(f"Unique VNRs: {df.groupby(['topology', 'seed', 'v_net_id']).ngroups}")

    # Group by unique VNR and keep only one row per VNR
    # Take the first occurrence (they all have same VNR features, different only in algorithm/success/solving_time)
    vnr_unique = df.groupby(['topology', 'seed', 'v_net_id']).first().reset_index()

    # Remove columns that are results of algorithm execution (data leakage)
    # Note: solving_time is kept because it's computed from summary.csv (avg time per VNR),
    # not an outcome of a specific algorithm run
    columns_to_remove = ['algorithm', 'success', 'v_net_r2c_ratio',
                         'v_net_revenue', 'v_net_cost', 'num_interactions', 'event_time']

    # Keep only columns that are known BEFORE running any algorithm
    features_to_keep = [col for col in vnr_unique.columns if col not in columns_to_remove]

    vnr_clean = vnr_unique[features_to_keep].copy()

    print(f"\nCleaned dataset: {len(vnr_clean)} rows")
    print(f"Features: {len(vnr_clean.columns)}")
    print(f"\nTarget distribution:")
    print(vnr_clean['best_overall'].value_counts())

    # Save cleaned dataset
    vnr_clean.to_csv('datasets/vnr_clean.csv', index=False)
    print(f"\n✓ Saved: datasets/vnr_clean.csv")

    return vnr_clean


if __name__ == '__main__':
    # Load raw data
    print("Loading raw VNR data...")
    df = pd.read_csv('datasets/vnr_raw_data.csv')
    print(f"Loaded {len(df)} records\n")

    # Feature engineering
    df = create_features(df)

    # Create labels
    df = create_labels(df)

    # Save full dataset with features
    df.to_csv('datasets/vnr_features.csv', index=False)
    print(f"\n✓ Saved full dataset with features: datasets/vnr_features.csv")

    # Assign algorithm-specific solving times (BEFORE splitting)
    # This ensures each algorithm gets its characteristic solving time
    df = assign_algorithm_specific_solving_times(df)

    # Fix dataset: one row per VNR, remove data leakage
    vnr_clean = fix_dataset(df)

    # Remove rows where no algorithm succeeded
    vnr_clean = vnr_clean[vnr_clean['best_overall'].notna()].copy()

    # Split into train/val/test
    from sklearn.model_selection import train_test_split

    print(f"\nSplitting data into train/val/test with stratification...")

    # First split: 70/30 for train / (val+test)
    # Stratify by target class to ensure balanced distribution
    train_df, val_test_df = train_test_split(
        vnr_clean, test_size=0.3, random_state=42, stratify=vnr_clean['best_overall']
    )

    # Second split: 50/50 of val_test for val / test (results in 70/15/15 overall)
    # Stratify by target class in the val_test subset
    val_df, test_df = train_test_split(
        val_test_df, test_size=0.5, random_state=42, stratify=val_test_df['best_overall']
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

    print(f"\nTrain distribution:")
    print(train_df['best_overall'].value_counts())
    print(f"\nVal distribution:")
    print(val_df['best_overall'].value_counts())
    print(f"\nTest distribution:")
    print(test_df['best_overall'].value_counts())

    print("\n" + "="*80)
    print("Dataset preparation complete!")
    print("="*80)
