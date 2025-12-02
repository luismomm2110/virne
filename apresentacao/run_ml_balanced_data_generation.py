#!/usr/bin/env python3
"""
Run ML Balanced Data Generation - Option 2

Generate balanced training data for ML algorithm selector with:
- 8 scenarios × 2 topologies × 5 seeds × 8 algorithms = 640 simulation runs
- Perfect head-to-head comparison (all algorithms test same VNRs)
- Balanced algorithm distribution

Scenarios:
1. mip_favoring      - Low load, small VNRs
2. meta_favoring     - High demand, complex VNRs
3. balanced          - Standard workload
4. stress_test       - High load, large VNRs
5. sparse_congested  - Few heavy VNRs
6. tiny_optimal      - Very small VNRs
7. moderate_mixed    - Mixed demands
8. realtime          - Fast decisions needed

Expected output: ~38,400 records (2,400 unique VNRs × 2 topologies × 8 algorithms)
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Get the project root directory
PROJECT_ROOT = Path('/Users/luismomm/PycharmProjects/virne')

# 8 Scenarios - SKIPPING already completed: mip_favoring, meta_favoring
SCENARIOS = [
    'mip_favoring',
    'meta_favoring',
    'balanced',
    'stress_test',
    'sparse_congested',
    'tiny_optimal',
    'moderate_mixed',
    'realtime'
]

# 2 Topologies
TOPOLOGIES = ['tree', 'fat_tree']

# 5 Seeds for statistical significance
SEEDS = [0, 1, 2, 3, 4]

# 8 Algorithms
ALGORITHMS = ['ga_meta', 'mip', 'mcts', 'sa_meta', 'pso_meta', 'pl_rank', 'rw_rank_bfs', 'd_round']

# Algorithm to script name mapping
ALGO_SCRIPT_MAP = {
    'ga_meta': 'ga',
    'mip': 'mip',
    'mcts': 'mcts',
    'sa_meta': 'sa',
    'pso_meta': 'pso_meta',
    'pl_rank': 'pl_rank',
    'rw_rank_bfs': 'rw_rank_bfs',
    'd_round': 'd_round'
}


def run_simulation(algorithm, topology, scenario, seed):
    """Run a single simulation."""

    # Main script to execute
    script_name = f"main_{topology}_{ALGO_SCRIPT_MAP[algorithm]}.py"
    script_path = PROJECT_ROOT / 'apresentacao/algoritmos' / script_name

    # Config file in apresentacao/settings
    config_name = f"main_{topology}_ml_{scenario}"

    print(f"\n{'='*70}")
    print(f"Running: {algorithm} | {topology} | {scenario} | seed={seed}")
    print(f"Script:  {script_name}")
    print(f"Config:  {config_name}")
    print(f"{'='*70}\n")

    # Check if script exists
    if not script_path.exists():
        print(f"⚠️  WARNING: Script {script_path} not found. Skipping...")
        return 'skipped'

    try:
        # Run with Hydra config override
        cmd = [
            'python3',
            str(script_path),
            f'--config-path=../settings',
            f'--config-name={config_name}',
            f'solver.solver_name={algorithm}',
            f'experiment.seed={seed}'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=900,  # 15 minutes timeout per run
            cwd='/Users/luismomm/PycharmProjects/virne'  # Run from project root
        )

        if result.returncode == 0:
            print(f"✅ SUCCESS: {algorithm} | {topology} | {scenario} | seed={seed}")
            return 'success'
        else:
            print(f"❌ FAILED: {algorithm} | {topology} | {scenario} | seed={seed}")
            print(f"Error output (last 500 chars):\n{result.stderr[-500:]}")
            return 'failed'

    except subprocess.TimeoutExpired:
        print(f"⏱️  TIMEOUT: {algorithm} | {topology} | {scenario} | seed={seed} (>15 min)")
        return 'timeout'
    except Exception as e:
        print(f"💥 ERROR: {algorithm} | {topology} | {scenario} | seed={seed}")
        print(f"Exception: {str(e)}")
        return 'error'


def main():
    """Run all simulations."""

    start_time = datetime.now()

    total_runs = len(SCENARIOS) * len(TOPOLOGIES) * len(SEEDS) * len(ALGORITHMS)

    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║          ML Balanced Data Generation - Option 2                   ║
║                                                                   ║
║  Scenarios:  {len(SCENARIOS)} (mip_favoring, meta_favoring, ...)              ║
║  Topologies: {len(TOPOLOGIES)} (tree, fat_tree)                                  ║
║  Seeds:      {len(SEEDS)} (0-4)                                                ║
║  Algorithms: {len(ALGORITHMS)} (ga_meta, mip, mcts, ...)                         ║
║                                                                   ║
║  Total runs: {total_runs}                                                ║
║  Expected:   ~38,400 records (2,400 VNRs × 2 topos × 8 algos)    ║
╚═══════════════════════════════════════════════════════════════════╝
""")

    # Tracking
    results = {
        'success': [],
        'failed': [],
        'timeout': [],
        'skipped': [],
        'error': []
    }

    current = 0

    # Iterate through all combinations
    for scenario in SCENARIOS:
        for topology in TOPOLOGIES:
            for seed in SEEDS:
                # Skip balanced tree seed 0 (already completed)
                if scenario == 'balanced' and topology == 'tree' and seed == 0:
                    print(f"\n⏭️  SKIPPING balanced | tree | seed=0 (already completed)")
                    continue

                for algorithm in ALGORITHMS:
                    current += 1

                    print(f"\n[{current}/{total_runs}] Processing:")
                    print(f"  Scenario:  {scenario}")
                    print(f"  Topology:  {topology}")
                    print(f"  Seed:      {seed}")
                    print(f"  Algorithm: {algorithm}")

                    status = run_simulation(algorithm, topology, scenario, seed)

                    # Record result
                    key = f"{scenario}_{topology}_seed_{seed}_{algorithm}"
                    results[status].append(key)

    # Summary
    end_time = datetime.now()
    duration = end_time - start_time

    print(f"\n{'='*70}")
    print("SIMULATION SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successful: {len(results['success'])}/{total_runs}")
    print(f"❌ Failed:     {len(results['failed'])}/{total_runs}")
    print(f"⏱️  Timeout:    {len(results['timeout'])}/{total_runs}")
    print(f"⚠️  Skipped:    {len(results['skipped'])}/{total_runs}")
    print(f"💥 Error:      {len(results['error'])}/{total_runs}")
    print(f"\nTotal duration: {duration}")
    print(f"{'='*70}")

    if results['failed']:
        print(f"\nFailed simulations ({len(results['failed'])}):")
        for item in results['failed'][:10]:  # Show first 10
            print(f"  - {item}")
        if len(results['failed']) > 10:
            print(f"  ... and {len(results['failed']) - 10} more")

    if results['timeout']:
        print(f"\nTimeout simulations ({len(results['timeout'])}):")
        for item in results['timeout'][:10]:
            print(f"  - {item}")
        if len(results['timeout']) > 10:
            print(f"  ... and {len(results['timeout']) - 10} more")

    if results['skipped']:
        print(f"\nSkipped simulations ({len(results['skipped'])}):")
        for item in results['skipped'][:10]:
            print(f"  - {item}")
        if len(results['skipped']) > 10:
            print(f"  ... and {len(results['skipped']) - 10} more")

    print(f"\n{'='*70}")
    print("Data saved to: apresentacao/simulacoes/")
    print("Next steps:")
    print("  1. Run: apresentacao/machine_learning/1_extract_vnr_data.py")
    print("  2. Verify head-to-head comparison")
    print("  3. Check algorithm distribution balance")
    print(f"{'='*70}\n")

    return len(results['success'])


if __name__ == '__main__':
    success_count = main()
    sys.exit(0 if success_count > 0 else 1)
