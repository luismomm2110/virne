#!/usr/bin/env python3
"""
Analyze and compare PL-RANK vs SA-Meta performance on 2x topologies.

This script extracts acceptance rates and other metrics from completed simulations
and generates a comprehensive comparison analysis.

Usage:
    python analyze_2x_topologies_comparison.py
"""

import os
import csv
import glob
from collections import defaultdict
from pathlib import Path

def extract_results_from_csv(csv_path):
    """Extract key metrics from simulation summary CSV."""
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                return {
                    'acceptance_rate': float(row['acceptance_rate']),
                    'success_count': int(row['success_count']),
                    'total_cost': float(row['total_cost']),
                    'total_revenue': float(row['total_revenue']),
                    'avg_r2c_ratio': float(row['avg_r2c_ratio']),
                }
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return None

def analyze_2x_topologies():
    """Analyze all 2x topology comparison results."""

    results = defaultdict(lambda: defaultdict(list))

    # Search for all simulation results
    base_dir = Path('apresentacao/simulacoes')

    algorithms = ['pl_rank', 'sa_meta']
    topologies = ['tree_2x', 'fat_tree_2x']

    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║      2X TOPOLOGIES COMPARISON ANALYSIS: PL-RANK vs SA-META        ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")

    for algo in algorithms:
        algo_dir = base_dir / algo
        if not algo_dir.exists():
            print(f"⚠️  No results directory for {algo}")
            continue

        # Find all simulation results
        for run_dir in sorted(algo_dir.glob('Luisas-MacBook-Air.local-*')):
            summary_file = run_dir / 'records' / 'summary.csv'
            if not summary_file.exists():
                continue

            metrics = extract_results_from_csv(summary_file)
            if not metrics:
                continue

            # Determine topology and seed from run_dir name
            run_name = run_dir.name
            timestamp_part = run_name.split('-')[-1]  # Last part is timestamp

            # Determine which topology from config if available
            config_file = run_dir / 'config.yaml'
            topology = 'unknown'
            seed = 'unknown'

            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_content = f.read()
                    if 'tree_2x_p_net' in config_content and 'fat_tree' not in config_content:
                        topology = 'Tree 2x'
                        seed = extract_seed_from_config(config_file)
                    elif 'fat_tree_2x_p_net' in config_content:
                        topology = 'Fat-Tree 2x'
                        seed = extract_seed_from_config(config_file)

            results[algo][topology].append({
                'seed': seed,
                'metrics': metrics,
                'run_id': run_name
            })

    # Print results by algorithm and topology
    print("\n" + "="*70)
    print("ALGORITHM PERFORMANCE ON 2X TOPOLOGIES")
    print("="*70 + "\n")

    for algo in algorithms:
        print(f"\n{'─'*70}")
        print(f"Algorithm: {algo.upper()}")
        print(f"{'─'*70}")

        for topology in topologies:
            if topology.replace('_', ' ').title() in results[algo]:
                topology_key = topology.replace('_', ' ').title()
            else:
                topology_key = topology.replace('_', ' ').title()

            runs = results[algo].get(topology_key, [])

            if not runs:
                print(f"\n  {topology_key}: No results yet")
                continue

            print(f"\n  {topology_key}:")
            print(f"  {'─'*66}")

            acceptance_rates = []
            for run in runs:
                acc_rate = run['metrics']['acceptance_rate']
                acceptance_rates.append(acc_rate)
                print(f"    Seed {run['seed']:2} | Acceptance: {acc_rate*100:5.1f}% | "
                      f"Success: {run['metrics']['success_count']:3}/200 | "
                      f"R2C Ratio: {run['metrics']['avg_r2c_ratio']:.3f}")

            if acceptance_rates:
                avg_rate = sum(acceptance_rates) / len(acceptance_rates)
                min_rate = min(acceptance_rates)
                max_rate = max(acceptance_rates)
                print(f"  {'─'*66}")
                print(f"  Average | Acceptance: {avg_rate*100:5.1f}% | "
                      f"Range: [{min_rate*100:.1f}% - {max_rate*100:.1f}%]")

    # Comparison summary
    print("\n\n" + "="*70)
    print("COMPARISON SUMMARY: PL-RANK vs SA-META")
    print("="*70 + "\n")

    comparison_data = {}

    for topology in topologies:
        topology_label = topology.replace('_', ' ').title()
        print(f"\n{topology_label}:")
        print(f"{'─'*70}")

        pl_rank_runs = results['pl_rank'].get(topology_label, [])
        sa_meta_runs = results['sa_meta'].get(topology_label, [])

        pl_rank_rates = [r['metrics']['acceptance_rate'] for r in pl_rank_runs]
        sa_meta_rates = [r['metrics']['acceptance_rate'] for r in sa_meta_runs]

        if pl_rank_rates:
            pl_avg = sum(pl_rank_rates) / len(pl_rank_rates)
            print(f"  PL-RANK: Avg {pl_avg*100:5.1f}% | Runs: {len(pl_rank_rates)}")
        else:
            pl_avg = None
            print(f"  PL-RANK: No results yet")

        if sa_meta_rates:
            sa_avg = sum(sa_meta_rates) / len(sa_meta_rates)
            print(f"  SA-Meta: Avg {sa_avg*100:5.1f}% | Runs: {len(sa_meta_rates)}")
        else:
            sa_avg = None
            print(f"  SA-Meta: Running...")

        if pl_avg and sa_avg:
            diff = sa_avg - pl_avg
            sign = "+" if diff > 0 else ""
            print(f"  {'─'*70}")
            print(f"  Difference (SA-Meta - PL-RANK): {sign}{diff*100:.2f}%")

def extract_seed_from_config(config_file):
    """Extract seed value from config file."""
    try:
        with open(config_file, 'r') as f:
            for line in f:
                if 'seed:' in line and 'training' not in line:
                    # Extract number from line like "  seed: 0"
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        try:
                            return int(parts[1].strip())
                        except:
                            pass
    except:
        pass
    return 'unknown'

if __name__ == '__main__':
    analyze_2x_topologies()

    print("\n\n" + "="*70)
    print("Analysis Complete!")
    print("="*70)
    print("\nKey Findings:")
    print("  - Compares acceptance rates between PL-RANK and SA-Meta")
    print("  - Evaluates if larger topology improves algorithm representation")
    print("  - Shows consistency across multiple seeds (0-4)")
    print("\n")
