#!/usr/bin/env python3
"""
Analyze Waxman 16-node topology results across all 7 algorithms
Compares performance metrics including acceptance rate, R2C ratio, and resource efficiency
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import json

# Configuration
RESULTS_DIR = Path("/Users/luismomm/PycharmProjects/virne/apresentacao/simulacoes")
ALGORITHMS = ['pl_rank', 'sa_meta', 'ga_meta', 'mcts', 'rw_rank_bfs', 'mip', 'd_round']
TOPOLOGY_FILTER = '16-waxman'
OUTPUT_DIR = RESULTS_DIR / "waxman_16_analysis"

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("WAXMAN 16-NODE TOPOLOGY - ALL ALGORITHMS ANALYSIS")
print("=" * 80)
print()

# Collect results for each algorithm
all_results = []

for algo in ALGORITHMS:
    algo_dir = RESULTS_DIR / algo

    if not algo_dir.exists():
        print(f"⚠️  Algorithm directory not found: {algo}")
        continue

    # Find all summary.csv files for this algorithm
    summary_files = list(algo_dir.glob("*summary.csv"))

    # Filter for Waxman 16 topology
    waxman_files = []
    for f in summary_files:
        try:
            # Read just enough to check the topology
            df = pd.read_csv(f, nrows=1)
            if TOPOLOGY_FILTER in str(df.iloc[0].get('p_net_dataset_dir', '')):
                waxman_files.append(f)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            continue

    print(f"Algorithm: {algo.upper()}")
    print(f"  Found {len(waxman_files)} runs for {TOPOLOGY_FILTER}")

    if len(waxman_files) == 0:
        print(f"  ⚠️  No results yet")
        continue

    # Read and aggregate results
    algo_results = []
    for f in waxman_files:
        try:
            df = pd.read_csv(f)
            for _, row in df.iterrows():
                algo_results.append({
                    'algorithm': algo,
                    'seed': row.get('seed', -1),
                    'acceptance_rate': float(row.get('acceptance_rate', 0)),
                    'r2c_ratio': float(row.get('avg_r2c_ratio', 0)),
                    'success_count': int(row.get('success_count', 0)),
                    'total_simulation_time': float(row.get('total_simulation_time', 0)),
                    'run_id': row.get('run_id', ''),
                })
        except Exception as e:
            print(f"  Error processing {f.name}: {e}")
            continue

    all_results.extend(algo_results)

    if algo_results:
        df_algo = pd.DataFrame(algo_results)

        print(f"  Acceptance Rate: {df_algo['acceptance_rate'].mean():.1%} (σ: {df_algo['acceptance_rate'].std():.2%})")
        print(f"  R2C Ratio:       {df_algo['r2c_ratio'].mean():.4f} (σ: {df_algo['r2c_ratio'].std():.4f})")
        print(f"  Avg Sim Time:    {df_algo['total_simulation_time'].mean():.1f}s")
        print(f"  Seeds: {sorted(df_algo['seed'].unique())}")
    print()

# Create comprehensive comparison table
if all_results:
    df_all = pd.DataFrame(all_results)

    # Aggregate by algorithm
    comparison = []
    for algo in ALGORITHMS:
        algo_data = df_all[df_all['algorithm'] == algo]
        if len(algo_data) > 0:
            comparison.append({
                'Algorithm': algo.upper(),
                'Runs': len(algo_data),
                'Avg Acceptance Rate': f"{algo_data['acceptance_rate'].mean():.1%}",
                'Min Acceptance': f"{algo_data['acceptance_rate'].min():.1%}",
                'Max Acceptance': f"{algo_data['acceptance_rate'].max():.1%}",
                'Std Dev': f"{algo_data['acceptance_rate'].std():.2%}",
                'Avg R2C': f"{algo_data['r2c_ratio'].mean():.4f}",
                'Avg Sim Time': f"{algo_data['total_simulation_time'].mean():.1f}s",
            })

    df_comparison = pd.DataFrame(comparison)

    print()
    print("=" * 120)
    print("COMPREHENSIVE COMPARISON TABLE")
    print("=" * 120)
    print(df_comparison.to_string(index=False))
    print()

    # Save to CSV
    csv_path = OUTPUT_DIR / "waxman_16_comparison.csv"
    df_comparison.to_csv(csv_path, index=False)
    print(f"✓ Comparison saved to: {csv_path}")

    # Save detailed results
    detailed_path = OUTPUT_DIR / "waxman_16_detailed_results.csv"
    df_all.to_csv(detailed_path, index=False)
    print(f"✓ Detailed results saved to: {detailed_path}")

    # Rank algorithms by acceptance rate
    print()
    print("=" * 80)
    print("ALGORITHM RANKING (by Acceptance Rate)")
    print("=" * 80)

    ranking = []
    for idx, row in df_comparison.iterrows():
        acc_rate = float(row['Avg Acceptance Rate'].rstrip('%')) / 100
        ranking.append((row['Algorithm'], acc_rate, row['Runs']))

    ranking.sort(key=lambda x: x[1], reverse=True)

    for rank, (algo, acc_rate, runs) in enumerate(ranking, 1):
        print(f"{rank}. {algo:<15} - {acc_rate:.1%} acceptance rate ({runs} runs)")

    print()
    print("=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)

    best_algo = ranking[0]
    worst_algo = ranking[-1]

    print(f"✓ Best Performer:  {best_algo[0]} with {best_algo[1]:.1%} acceptance rate")
    print(f"✗ Worst Performer: {worst_algo[0]} with {worst_algo[1]:.1%} acceptance rate")
    print(f"  Improvement: {(best_algo[1] - worst_algo[1]):.1%} absolute difference")

    # Check if all algorithms have completed
    completed_algos = df_comparison['Runs'].sum()
    expected_runs = len(ALGORITHMS) * 5  # 5 seeds per algorithm

    print()
    print(f"Campaign Progress: {completed_algos}/{expected_runs} simulations completed")
    print(f"Status: {100 * completed_algos / expected_runs:.1f}% complete")

    if completed_algos < expected_runs:
        print()
        print("Algorithms pending completion:")
        for algo in ALGORITHMS:
            algo_data = df_all[df_all['algorithm'] == algo]
            runs = len(algo_data)
            if runs < 5:
                print(f"  - {algo.upper()}: {runs}/5 runs")

print()
print("Analysis complete!")
