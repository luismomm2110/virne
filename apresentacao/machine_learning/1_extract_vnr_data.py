#!/usr/bin/env python3
"""
Step 1: Extract VNR-level data from simulation results.

Input:  apresentacao/simulacoes/*/records/temp-*.csv
Output: datasets/vnr_raw_data.csv (~14,000 records)
"""

import pandas as pd
import glob
import os
import yaml
from pathlib import Path


def get_topology_from_config(csv_file_path):
    """Read topology from config.yaml. Fails fast if config not found or invalid."""
    csv_path = Path(csv_file_path)
    config_path = csv_path.parent.parent / 'config.yaml'

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            topo_type = config['p_net_setting']['topology']['type']
            return topo_type
    except (KeyError, TypeError, yaml.YAMLError) as e:
        raise ValueError(f"Cannot read topology from {config_path}: {e}")


def get_seed_from_config(csv_file_path):
    """Read seed from config.yaml (stored in config['experiment']['seed'])."""
    csv_path = Path(csv_file_path)
    config_path = csv_path.parent.parent / 'config.yaml'

    if not config_path.exists():
        return 0  # Default to 0 if config not found

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            # Seed is stored in config['experiment']['seed']
            seed = config.get('experiment', {}).get('seed', 0)
            return seed if seed is not None else 0
    except (KeyError, TypeError, yaml.YAMLError):
        return 0  # Default to 0 on any error


def get_solving_time_from_summary(csv_file_path):
    """
    Read solving time from summary.csv.
    Solving time = clock_running_time / success_count
    If no summary found or success_count is 0, default to 15 minutes (900 seconds).
    """
    csv_path = Path(csv_file_path)
    summary_path = csv_path.parent.parent / 'summary.csv'

    if not summary_path.exists():
        # Default to 15 minutes (900 seconds) if no summary found
        return 900.0

    try:
        summary_df = pd.read_csv(summary_path)
        if len(summary_df) > 0:
            row = summary_df.iloc[0]
            clock_time = row.get('clock_running_time', 900.0)
            success_count = row.get('success_count', 1)

            # Avoid division by zero
            if success_count > 0:
                return clock_time / success_count
            else:
                return 900.0  # Default to 15 minutes
    except Exception:
        pass

    # Default to 15 minutes if any error
    return 900.0


def extract_vnr_data():
    """Extract VNR-level features and outcomes from all simulation runs."""

    all_records = []

    algorithms = ['ga_meta', 'mip', 'mcts', 'sa_meta', 'pso_meta', 'pl_rank', 'rw_rank_bfs', 'd_round']

    # Average time per VNR for each algorithm (from summary analysis)
    # These are empirical averages from the simulations

    print("Extracting VNR data from simulations...")
    print(f"Looking for {len(algorithms)} algorithms")
    print()

    for algo in algorithms:
        # Pattern to find all CSV files in records/ (recursive search)
        # Supports both temp-*.csv and algorithm-timestamp.csv formats
        pattern = f"../simulacoes/{algo}/**/records/*.csv"
        files = glob.glob(pattern, recursive=True)

        if not files:
            print(f"  ⚠️  No files found for {algo}")
            continue

        print(f"  Processing {algo}: found {len(files)} record files")

        for temp_file in files:
            try:
                df = pd.read_csv(temp_file)

                # Filter only arrival events (event_type == 1)
                arrivals = df[df['event_type'] == 1].copy()

                if len(arrivals) == 0:
                    continue

                # Determine topology from config.yaml
                try:
                    detected_topo = get_topology_from_config(temp_file)
                except (FileNotFoundError, ValueError) as e:
                    print(f"    ✗ Cannot process {temp_file}: {e}")
                    continue

                # Determine seed from config.yaml
                seed = get_seed_from_config(temp_file)

                # Extract features for each VNR
                for idx, row in arrivals.iterrows():
                    record = {
                        # Metadata
                        'algorithm': algo,
                        'topology': detected_topo,
                        'seed': seed,
                        'v_net_id': row['v_net_id'],

                        # VNR characteristics
                        'v_net_num_nodes': row['v_net_num_nodes'],
                        'v_net_num_edges': row['v_net_num_egdes'],  # Note: typo in original data
                        'v_net_lifetime': row['v_net_lifetime'],
                        'v_net_arrival_time': row['v_net_arrival_time'],

                        # VNR demands
                        'v_net_demand': row['v_net_demand'],
                        'v_net_node_demand': row['v_net_node_demand'],
                        'v_net_link_demand': row['v_net_link_demand'],

                        # Physical network state
                        'p_net_available_resource': row['p_net_available_resource'],
                        'p_net_node_available_resource': row['p_net_node_available_resource'],
                        'p_net_link_available_resource': row['p_net_link_available_resource'],
                        'p_net_node_resource_utilization': row['p_net_node_resource_utilization'],
                        'p_net_link_resource_utilization': row['p_net_link_resource_utilization'],

                        # System state
                        'inservice_count': row['inservice_count'],
                        'num_running_p_net_nodes': row['num_running_p_net_nodes'],

                        # Solving effort (number of solver interactions)
                        'num_interactions': row.get('num_interactions', 0),

                        # Outcomes
                        'success': row['result'],
                        'v_net_r2c_ratio': row.get('v_net_r2c_ratio', None),
                        'v_net_revenue': row.get('v_net_revenue', None),
                        'v_net_cost': row.get('v_net_cost', None),
                        'v_net_time_cost': row.get('v_net_time_cost', 0.0),
                        'v_net_time_revenue': row.get('v_net_time_revenue', None),
                    }

                    all_records.append(record)

            except Exception as e:
                print(f"    ✗ Error reading {temp_file}: {e}")
                continue

    # Create DataFrame
    if len(all_records) == 0:
        print("\n❌ ERROR: No VNR data extracted!")
        print("   Check that simulations have been run and saved to apresentacao/simulacoes/")
        return pd.DataFrame()

    df = pd.DataFrame(all_records)

    print(f"\n{'='*80}")
    print(f"Total VNRs extracted: {len(df)}")
    print(f"Algorithms: {df['algorithm'].nunique()} ({df['algorithm'].unique().tolist()})")
    print(f"Topologies: {df['topology'].nunique()} ({df['topology'].unique().tolist()})")
    print(f"Seeds: {df['seed'].nunique()} ({sorted(df['seed'].unique())})")
    print(f"\nRecords per algorithm:")
    print(df['algorithm'].value_counts().sort_index())
    print(f"\nSuccess rate per algorithm:")
    print(df.groupby('algorithm')['success'].mean().sort_values(ascending=False))
    print(f"{'='*80}\n")

    return df


def save_dataset(df, output_path='datasets/vnr_raw_data.csv'):
    """Save extracted data to CSV."""
    if len(df) == 0:
        print("❌ No data to save!")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✓ Saved to: {output_path}")
    print(f"  Shape: {df.shape}")
    print(f"  Size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")


if __name__ == '__main__':
    # Extract data
    df = extract_vnr_data()

    if len(df) > 0:
        # Save to CSV
        save_dataset(df)

        # Basic statistics
        print("\n" + "="*80)
        print("BASIC STATISTICS")
        print("="*80)
        print(df.describe())
    else:
        print("\n❌ Extraction failed. Please check simulation data.")
