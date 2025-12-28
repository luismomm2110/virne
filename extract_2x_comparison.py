#!/usr/bin/env python3
"""
Extract and compare PL-RANK vs SA-Meta performance on 2x topologies.

This script extracts acceptance rates and other metrics from completed simulations
and generates a comprehensive comparison analysis.
"""

import csv
from pathlib import Path
from collections import defaultdict


def extract_metrics_from_csv(csv_path):
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
                    'seed': int(row['seed']),
                    'p_net_dataset_dir': row['p_net_dataset_dir'],
                }
    except Exception as e:
        return None


def identify_topology(p_net_dir_string):
    """Identify topology from p_net_dataset_dir string."""
    if 'tree_2x' in p_net_dir_string and 'fat_tree' not in p_net_dir_string:
        return 'Tree 2x'
    elif 'fat_tree_2x' in p_net_dir_string:
        return 'Fat-Tree 2x'
    elif '64-' in p_net_dir_string and 'fat_tree' not in p_net_dir_string:
        return 'Tree 2x'  # 64 nodes = Tree 2x
    elif '32-fat_tree' in p_net_dir_string:
        return 'Fat-Tree 2x'  # 32 nodes = Fat-Tree 2x
    else:
        return 'Unknown'


def analyze_2x_topologies():
    """Analyze all 2x topology comparison results."""

    results = defaultdict(lambda: defaultdict(list))

    base_dir = Path('apresentacao/simulacoes')

    algorithms = ['pl_rank', 'sa_meta']

    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║      2X TOPOLOGIES COMPARISON: PL-RANK vs SA-META                 ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")

    # Collect all results
    for algo in algorithms:
        algo_dir = base_dir / algo
        if not algo_dir.exists():
            print(f"⚠️  No results directory for {algo}")
            continue

        # Find all recent simulation results (from Dec 21)
        for run_dir in sorted(algo_dir.glob('Luisas-MacBook-Air.local-2025122*')):
            summary_file = run_dir / 'summary.csv'
            if not summary_file.exists():
                continue

            metrics = extract_metrics_from_csv(summary_file)
            if not metrics:
                continue

            topology = identify_topology(metrics['p_net_dataset_dir'])
            seed = metrics['seed']

            results[algo][topology].append({
                'seed': seed,
                'metrics': metrics,
                'run_id': run_dir.name
            })

    # Print results by algorithm and topology
    print("\n" + "="*70)
    print("ALGORITHM PERFORMANCE ON 2X TOPOLOGIES")
    print("="*70 + "\n")

    for algo in algorithms:
        print(f"\n{'─'*70}")
        print(f"Algorithm: {algo.upper()}")
        print(f"{'─'*70}")

        for topology in ['Tree 2x', 'Fat-Tree 2x']:
            runs = results[algo].get(topology, [])

            if not runs:
                print(f"\n  {topology}: No results yet")
                continue

            # Sort by seed
            runs = sorted(runs, key=lambda r: r['seed'])

            print(f"\n  {topology}:")
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

    for topology in ['Tree 2x', 'Fat-Tree 2x']:
        print(f"\n{topology}:")
        print(f"{'─'*70}")

        pl_rank_runs = results['pl_rank'].get(topology, [])
        sa_meta_runs = results['sa_meta'].get(topology, [])

        pl_rank_rates = [r['metrics']['acceptance_rate'] for r in pl_rank_runs]
        sa_meta_rates = [r['metrics']['acceptance_rate'] for r in sa_meta_runs]

        pl_avg = None
        sa_avg = None

        if pl_rank_rates:
            pl_avg = sum(pl_rank_rates) / len(pl_rank_rates)
            print(f"  PL-RANK: Avg {pl_avg*100:5.1f}% | Runs: {len(pl_rank_rates)} | "
                  f"Range: {min(pl_rank_rates)*100:.1f}% - {max(pl_rank_rates)*100:.1f}%")
        else:
            print(f"  PL-RANK: No results found")

        if sa_meta_rates:
            sa_avg = sum(sa_meta_rates) / len(sa_meta_rates)
            print(f"  SA-Meta: Avg {sa_avg*100:5.1f}% | Runs: {len(sa_meta_rates)} | "
                  f"Range: {min(sa_meta_rates)*100:.1f}% - {max(sa_meta_rates)*100:.1f}%")
        else:
            print(f"  SA-Meta: No results found")

        if pl_avg and sa_avg:
            diff = sa_avg - pl_avg
            sign = "+" if diff > 0 else ""
            pct_diff = (diff / pl_avg * 100) if pl_avg != 0 else 0
            print(f"  {'─'*70}")
            print(f"  Difference (SA-Meta - PL-RANK): {sign}{diff*100:.2f}% "
                  f"({sign}{pct_diff:.1f}% relative)")

            if sa_avg > pl_avg:
                print(f"  → SA-Meta performs BETTER on {topology} (larger topology helps!)")
            elif sa_avg < pl_avg:
                print(f"  → SA-Meta performs WORSE on {topology}")
            else:
                print(f"  → Performance is equivalent")

    # Overall hypothesis testing
    print("\n\n" + "="*70)
    print("HYPOTHESIS TEST: Larger Topology Improves Algorithm Diversity")
    print("="*70 + "\n")

    tree_2x_results = {
        'pl_rank': [r['metrics']['acceptance_rate'] for r in results['pl_rank'].get('Tree 2x', [])],
        'sa_meta': [r['metrics']['acceptance_rate'] for r in results['sa_meta'].get('Tree 2x', [])]
    }

    fat_tree_2x_results = {
        'pl_rank': [r['metrics']['acceptance_rate'] for r in results['pl_rank'].get('Fat-Tree 2x', [])],
        'sa_meta': [r['metrics']['acceptance_rate'] for r in results['sa_meta'].get('Fat-Tree 2x', [])]
    }

    if tree_2x_results['sa_meta'] and fat_tree_2x_results['sa_meta']:
        tree_sa_avg = sum(tree_2x_results['sa_meta']) / len(tree_2x_results['sa_meta'])
        fat_tree_sa_avg = sum(fat_tree_2x_results['sa_meta']) / len(fat_tree_2x_results['sa_meta'])

        print("SA-Meta Performance on 2x Topologies:")
        print(f"  Tree 2x (64 nodes):      {tree_sa_avg*100:.1f}%")
        print(f"  Fat-Tree 2x (32 nodes):  {fat_tree_sa_avg*100:.1f}%")

        tree_pl_avg = sum(tree_2x_results['pl_rank']) / len(tree_2x_results['pl_rank']) if tree_2x_results['pl_rank'] else None
        fat_tree_pl_avg = sum(fat_tree_2x_results['pl_rank']) / len(fat_tree_2x_results['pl_rank']) if fat_tree_2x_results['pl_rank'] else None

        print("\nPL-RANK Performance on 2x Topologies:")
        if tree_pl_avg:
            print(f"  Tree 2x (64 nodes):      {tree_pl_avg*100:.1f}%")
        else:
            print(f"  Tree 2x (64 nodes):      No data")

        if fat_tree_pl_avg:
            print(f"  Fat-Tree 2x (32 nodes):  {fat_tree_pl_avg*100:.1f}%")
        else:
            print(f"  Fat-Tree 2x (32 nodes):  No data")


if __name__ == '__main__':
    analyze_2x_topologies()

    print("\n\n" + "="*70)
    print("Analysis Complete!")
    print("="*70 + "\n")
