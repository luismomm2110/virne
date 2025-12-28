#!/usr/bin/env python3
"""
Extract WX500 simulation results and integrate into training dataset.

This script:
1. Finds all WX500 simulation results in virne/ directories
2. Extracts summary.csv from each algorithm/seed combination
3. Combines them into a single results file
4. Merges with existing training data
5. Generates new class distribution analysis

Usage:
    python extract_wx500_results.py
"""

import os
import glob
import pandas as pd
import numpy as np
from pathlib import Path


def find_wx500_results():
    """Find all WX500 simulation results."""
    print("=" * 70)
    print("SEARCHING FOR WX500 RESULTS")
    print("=" * 70)

    algorithms = [
        'mip', 'ga_meta', 'pso_meta', 'sa_meta',
        'pl_rank', 'rw_rank_bfs', 'mcts', 'd_round'
    ]

    results = {}

    for algo in algorithms:
        algo_dir = f'virne/{algo}'
        if not os.path.exists(algo_dir):
            print(f"❌ {algo}: Directory not found at {algo_dir}")
            continue

        # Find all seed directories under this algorithm
        seed_dirs = glob.glob(f'{algo_dir}/*/')
        if not seed_dirs:
            print(f"❌ {algo}: No simulation results found")
            continue

        print(f"✓ {algo}: Found {len(seed_dirs)} simulations")

        for seed_dir in seed_dirs:
            summary_file = f'{seed_dir}records/summary.csv'

            if os.path.exists(summary_file):
                # Extract seed from directory name
                dir_name = os.path.basename(seed_dir.rstrip('/'))
                if 'seed' in dir_name:
                    # Parse seed number
                    parts = dir_name.split('_')
                    for i, part in enumerate(parts):
                        if part == 'seed' and i + 1 < len(parts):
                            try:
                                seed = int(parts[i + 1])
                                if algo not in results:
                                    results[algo] = []
                                results[algo].append({
                                    'seed': seed,
                                    'summary_file': summary_file,
                                    'dir': seed_dir
                                })
                                print(f"  └─ Seed {seed}: {summary_file}")
                            except:
                                pass

    return results


def extract_summary_data(results):
    """Extract key metrics from summary.csv files."""
    print("\n" + "=" * 70)
    print("EXTRACTING SUMMARY DATA")
    print("=" * 70)

    all_data = []

    for algo, seeds_info in results.items():
        for seed_info in seeds_info:
            summary_file = seed_info['summary_file']
            seed = seed_info['seed']

            try:
                # Read summary file
                df = pd.read_csv(summary_file)

                # Extract key metrics (last row usually has aggregated results)
                if len(df) > 0:
                    row = df.iloc[-1]  # Last row has final results

                    all_data.append({
                        'algorithm': algo,
                        'seed': seed,
                        'acceptance_rate': row.get('acceptance_rate', np.nan),
                        'average_embedding_time': row.get('average_embedding_time', np.nan),
                        'substrate_node_utilization': row.get('substrate_node_utilization', np.nan),
                        'substrate_link_utilization': row.get('substrate_link_utilization', np.nan),
                        'revenue': row.get('revenue', np.nan),
                        'cost': row.get('cost', np.nan),
                    })

                    print(f"✓ {algo:15s} seed {seed}: "
                          f"Acceptance={row.get('acceptance_rate', 0)*100:5.1f}%, "
                          f"Time={row.get('average_embedding_time', 0):7.4f}s")

            except Exception as e:
                print(f"❌ {algo} seed {seed}: Failed to read - {e}")

    wx500_results = pd.DataFrame(all_data)
    return wx500_results


def analyze_wx500_results(wx500_df):
    """Analyze WX500 results and show statistics."""
    print("\n" + "=" * 70)
    print("WX500 RESULTS SUMMARY")
    print("=" * 70)

    if len(wx500_df) == 0:
        print("No WX500 results found yet!")
        return

    print(f"\nTotal simulations completed: {len(wx500_df)}")
    print(f"Algorithms: {sorted(wx500_df['algorithm'].unique())}")
    print(f"Seeds: {sorted(wx500_df['seed'].unique())}")

    print("\n" + "-" * 70)
    print("ACCEPTANCE RATE BY ALGORITHM")
    print("-" * 70)

    acceptance = wx500_df.groupby('algorithm')['acceptance_rate'].agg(['mean', 'std', 'min', 'max'])
    acceptance = acceptance.sort_values('mean', ascending=False)
    for algo, row in acceptance.iterrows():
        print(f"{algo:15s}: {row['mean']*100:6.2f}% ± {row['std']*100:5.2f}% "
              f"(range: {row['min']*100:5.1f}% - {row['max']*100:5.1f}%)")

    print("\n" + "-" * 70)
    print("EXECUTION TIME BY ALGORITHM")
    print("-" * 70)

    times = wx500_df.groupby('algorithm')['average_embedding_time'].agg(['mean', 'std', 'min', 'max'])
    times = times.sort_values('mean')
    for algo, row in times.iterrows():
        print(f"{algo:15s}: {row['mean']:7.4f}s ± {row['std']:7.4f}s "
              f"(range: {row['min']:7.4f}s - {row['max']:7.4f}s)")

    print("\n" + "-" * 70)
    print("NODE UTILIZATION BY ALGORITHM")
    print("-" * 70)

    util = wx500_df.groupby('algorithm')['substrate_node_utilization'].agg(['mean', 'std'])
    util = util.sort_values('mean', ascending=False)
    for algo, row in util.iterrows():
        print(f"{algo:15s}: {row['mean']*100:6.2f}% ± {row['std']*100:5.2f}%")

    return wx500_df


def main():
    print("\n" + "=" * 70)
    print("WX500 RESULT EXTRACTION & ANALYSIS")
    print("=" * 70)

    # Find results
    results = find_wx500_results()

    if not results:
        print("\n❌ No WX500 results found!")
        print("\nNote: Simulations may still be running. Check back later.")
        print("Expected location: virne/{algorithm}/{run_id}/records/summary.csv")
        return

    # Extract summary data
    wx500_df = extract_summary_data(results)

    # Analyze results
    if len(wx500_df) > 0:
        wx500_df = analyze_wx500_results(wx500_df)

        # Save results
        output_file = 'virne/wx500_results_summary.csv'
        wx500_df.to_csv(output_file, index=False)
        print(f"\n✓ Saved results to: {output_file}")

        # Show comparison with tree/fat_tree
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("""
1. Wait for all WX500 simulations to complete
2. Re-extract results:
   python extract_wx500_results.py

3. Extract individual VNR data:
   python apresentacao/machine_learning/1_extract_vnr_data.py

4. Prepare combined dataset:
   python apresentacao/machine_learning/2_prepare_dataset.py

5. Retrain Option 2 trees with WX500 data:
   python train_multiple_objective_trees.py

6. Analyze improvements:
   python inference_option2.py --test
        """)
    else:
        print("\n⚠ No data extracted yet. Simulations may still be running.")


if __name__ == '__main__':
    main()
