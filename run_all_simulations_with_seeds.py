#!/usr/bin/env python3
"""
Run all algorithm simulations with different seeds for fat_tree and tree topologies.
Generates data for XGBoost training and testing.
"""

import subprocess
import sys
from pathlib import Path

# Algorithms to test
algorithms = ['ga_meta', 'mip', 'mcts', 'sa_meta', 'pso_meta', 'pl_rank', 'rw_rank_bfs', 'd_round']

# Seeds for simulations (3 different seeds)
seeds = [0, 1, 2]

# Topologies
topologies = ['tree', 'fat_tree']

# Algorithm name mapping for script execution
algo_script_map = {
    'ga_meta': 'ga_meta',
    'mip': 'mip',
    'mcts': 'mcts',
    'sa_meta': 'sa_meta',
    'pso_meta': 'pso_meta',
    'pl_rank': 'pl_rank',
    'rw_rank_bfs': 'rw_rank_bfs',
    'd_round': 'd_round'
}

def run_simulation(algorithm, topology, seed):
    """Run a single simulation."""
    script_name = f"main_{topology}_{algo_script_map[algorithm]}.py"

    print(f"\n{'='*70}")
    print(f"Running: {algorithm} on {topology} with seed={seed}")
    print(f"Script: {script_name}")
    print(f"{'='*70}\n")

    # Check if script exists
    if not Path(script_name).exists():
        print(f"⚠️  WARNING: Script {script_name} not found. Skipping...")
        return False

    try:
        cmd = [
            'python3',
            script_name,
            f'experiment.seed={seed}'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )

        if result.returncode == 0:
            print(f"✅ SUCCESS: {algorithm} on {topology} with seed={seed}")
            return True
        else:
            print(f"❌ FAILED: {algorithm} on {topology} with seed={seed}")
            print(f"Error output:\n{result.stderr[-500:]}")  # Last 500 chars
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️  TIMEOUT: {algorithm} on {topology} with seed={seed} (>10 min)")
        return False
    except Exception as e:
        print(f"💥 ERROR: {algorithm} on {topology} with seed={seed}")
        print(f"Exception: {str(e)}")
        return False

def main():
    """Run all simulations."""
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║           Running All Algorithm Simulations with Seeds            ║
║                                                                   ║
║  Algorithms: {len(algorithms)}                                              ║
║  Topologies: {len(topologies)} (tree, fat_tree)                              ║
║  Seeds per topology: {len(seeds)}                                        ║
║  Total simulations: {len(algorithms) * len(topologies) * len(seeds)}                                  ║
╚═══════════════════════════════════════════════════════════════════╝
""")

    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }

    total = len(algorithms) * len(topologies) * len(seeds)
    current = 0

    for algorithm in algorithms:
        for topology in topologies:
            for seed in seeds:
                current += 1
                print(f"\n[{current}/{total}] Processing {algorithm} - {topology} - seed {seed}")

                success = run_simulation(algorithm, topology, seed)

                key = f"{algorithm}_{topology}_seed_{seed}"
                if success:
                    results['success'].append(key)
                else:
                    # Check if skipped or failed
                    script_name = f"main_{topology}_{algo_script_map[algorithm]}.py"
                    if not Path(script_name).exists():
                        results['skipped'].append(key)
                    else:
                        results['failed'].append(key)

    # Summary
    print(f"\n{'='*70}")
    print("SIMULATION SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successful: {len(results['success'])}/{total}")
    print(f"❌ Failed: {len(results['failed'])}/{total}")
    print(f"⚠️  Skipped: {len(results['skipped'])}/{total}")

    if results['failed']:
        print(f"\nFailed simulations:")
        for item in results['failed']:
            print(f"  - {item}")

    if results['skipped']:
        print(f"\nSkipped simulations (script not found):")
        for item in results['skipped']:
            print(f"  - {item}")

    print(f"\n{'='*70}")
    print("All simulations completed!")
    print(f"{'='*70}\n")

    return len(results['success'])

if __name__ == '__main__':
    success_count = main()
    sys.exit(0 if success_count > 0 else 1)