#!/usr/bin/env python3
"""
Calculate TRUE Oracle Performance for VNE Algorithm Selection.

The Oracle answers: "If we ALWAYS selected the best_for_rac algorithm for each VNR,
what would be the actual acceptance rate?"

This requires:
1. Loading individual VNR results from simulation records
2. For each VNR in test set, finding its best_for_* algorithm
3. Looking up if that algorithm successfully embedded that VNR
4. Calculating the aggregated acceptance rate

This fixes the bug in visualize_model_oracle_algorithms_fixed_v2.py where Oracle
was calculating MEAN of algorithm averages (wrong) instead of actual per-VNR results.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob
import json
from collections import defaultdict

# ============================================================================
# Step 1: Load test dataset and simulation records
# ============================================================================

print("=" * 80)
print("CALCULATING TRUE ORACLE PERFORMANCE")
print("=" * 80)

# Load test data
test_file = Path(__file__).parent / "datasets" / "test_enhanced.csv"
test_data = pd.read_csv(test_file)
print(f"\n✓ Loaded test data: {len(test_data)} rows")

# Map topology encoding back
topology_map = {0: 'tree', 1: 'fat_tree', 2: 'waxman_16'}
test_data['topology_name'] = test_data['topology_encoded'].map(topology_map)

# ============================================================================
# Step 2: Load individual VNR results from simulation records
# ============================================================================

print("\n📂 Loading individual VNR results from simulation records...")

# Structure: {(topology, algorithm, seed, v_net_id): {'success': bool, 'v_net_revenue': float, etc}}
vnr_results = {}

# Find all records files
record_files = glob.glob(
    '/Users/luismomm/PycharmProjects/virne/virne/**/records/*.csv',
    recursive=True
)

print(f"  Found {len(record_files)} record files")

for record_file in record_files:
    try:
        # Extract algorithm name and seed from path
        # Path format: virne/{algorithm}/{experiment_dir}/records/{algo}-{experiment_name}-{seed}.csv
        parts = record_file.split('/')
        algorithm = parts[-3]  # virne/{algorithm}/...

        # Load the records file
        df = pd.read_csv(record_file)

        # Extract key columns: topology should be in experiment name or we need to infer
        # Actually, topology isn't in the records - we need to infer from algorithm/seed pattern

        for idx, row in df.iterrows():
            try:
                v_net_id = int(row.get('v_net_id', -1))
                result = row.get('result', False)

                # Try to extract topology from path
                if 'tree' in record_file and 'fat_tree' not in record_file:
                    topology = 'tree'
                elif 'fat_tree' in record_file:
                    topology = 'fat_tree'
                elif 'waxman_16' in record_file or 'wx' in record_file:
                    topology = 'waxman_16'
                else:
                    continue  # Skip if we can't determine topology

                # Try to extract seed (it's in the experiment name in the path)
                # Format: name-{seed}/ or name_seed_{seed}/
                seed = -1
                for part in parts:
                    if 'seed_' in part:
                        try:
                            seed = int(part.split('seed_')[1].split('/')[0])
                            break
                        except:
                            pass

                if seed == -1:
                    continue

                key = (topology, algorithm, seed, v_net_id)
                vnr_results[key] = {
                    'success': bool(result),
                    'v_net_revenue': float(row.get('v_net_revenue', 0)) if pd.notna(row.get('v_net_revenue')) else 0,
                    'v_net_cost': float(row.get('v_net_cost', 0)) if pd.notna(row.get('v_net_cost')) else 0,
                    'solving_time': float(row.get('solving_time', 0)) if pd.notna(row.get('solving_time')) else 0,
                }

            except Exception as e:
                continue

    except Exception as e:
        continue

print(f"  ✓ Loaded {len(vnr_results)} individual VNR results")

# ============================================================================
# Step 3: Calculate Oracle Performance
# ============================================================================

print("\n🎯 Calculating Oracle Performance by Objective...\n")

objectives = ['rac', 'lrc', 'lar', 'ast', 'balanced']
objective_labels = {
    'rac': 'Taxa de Aceitação (RAC) %',
    'lrc': 'Razão Receita-para-Custo (LRC)',
    'lar': 'Receita Média (LAR)',
    'ast': 'Tempo Médio (AST) segundos',
    'balanced': 'Objetivo Balanceado'
}

topologies = ['tree', 'fat_tree', 'waxman_16']

oracle_results = {}

for objective in objectives:
    print(f"{'='*60}")
    print(f"Objective: {objective.upper()}")
    print(f"{'='*60}")

    oracle_results[objective] = {}
    best_col = f'best_for_{objective}'

    for topology in topologies:
        # Filter test data for this topology
        topo_test = test_data[test_data['topology_name'] == topology].copy()

        if len(topo_test) == 0:
            print(f"  {topology:12s}: No test data")
            continue

        # Simulate Oracle: for each VNR, try to use best_for_* algorithm
        oracle_successes = 0
        oracle_revenues = []
        oracle_costs = []
        oracle_times = []
        oracle_r2c_ratios = []

        found_results = 0
        not_found = 0
        no_best_algo = 0

        for idx, row in topo_test.iterrows():
            best_algo = row[best_col]

            # Skip if no best algorithm assigned (shouldn't happen for RAC, but might for others)
            if pd.isna(best_algo):
                no_best_algo += 1
                continue

            # Try to find this VNR's result for the best_for_* algorithm
            # Problem: v_net_id might not be stored consistently
            # We'll try to match by finding the result in vnr_results

            # Try different seed values since we don't know the exact seed used in training
            found = False
            for seed in range(0, 5):  # Try seeds 0-4
                key = (topology, best_algo, seed, int(row.get('v_net_id', -1)))

                if key in vnr_results:
                    result = vnr_results[key]

                    if result['success']:
                        oracle_successes += 1
                        oracle_revenues.append(result['v_net_revenue'])
                        oracle_costs.append(result['v_net_cost'])
                        oracle_times.append(result['solving_time'])

                        # Calculate R2C ratio
                        if result['v_net_cost'] > 0:
                            r2c = result['v_net_revenue'] / result['v_net_cost']
                            oracle_r2c_ratios.append(r2c)

                    found = True
                    found_results += 1
                    break

            if not found:
                not_found += 1

        # Calculate aggregate metrics
        if objective == 'rac':
            oracle_metric = (oracle_successes / len(topo_test)) * 100 if len(topo_test) > 0 else 0
        elif objective == 'lrc':
            oracle_metric = np.mean(oracle_r2c_ratios) if oracle_r2c_ratios else 0
        elif objective == 'lar':
            oracle_metric = np.mean(oracle_revenues) if oracle_revenues else 0
        elif objective == 'ast':
            oracle_metric = np.mean(oracle_times) if oracle_times else 0
        elif objective == 'balanced':
            if oracle_successes > 0 and oracle_revenues and oracle_times:
                oracle_metric = np.mean([
                    0.8 * rev - 0.2 * t
                    for rev, t in zip(oracle_revenues, oracle_times)
                ])
            else:
                oracle_metric = 0

        oracle_results[objective][topology] = {
            'oracle_metric': oracle_metric,
            'success_count': oracle_successes,
            'total_vnrs': len(topo_test),
            'found_results': found_results,
            'not_found': not_found,
            'no_best_algo': no_best_algo
        }

        print(f"  {topology:12s}:")
        print(f"    Oracle {objective.upper()}: {oracle_metric:8.2f}")
        print(f"    Successes: {oracle_successes}/{len(topo_test)}")
        print(f"    Found in records: {found_results}/{len(topo_test)}")
        print(f"    Not found: {not_found}")
        print(f"    No best algo: {no_best_algo}")

# ============================================================================
# Step 4: Save Results
# ============================================================================

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

for objective in objectives:
    print(f"\n{objective.upper()} ({objective_labels[objective]}):")
    for topology in topologies:
        if topology in oracle_results[objective]:
            data = oracle_results[objective][topology]
            print(f"  {topology:12s}: Oracle={data['oracle_metric']:8.2f}")

# Save to JSON
output_file = Path(__file__).parent / 'models' / 'oracle_performance_true.json'
output_file.parent.mkdir(exist_ok=True)

with open(output_file, 'w') as f:
    # Convert numpy types to native Python types for JSON serialization
    json_data = {}
    for objective in objectives:
        json_data[objective] = {}
        for topology in topologies:
            if topology in oracle_results[objective]:
                data = oracle_results[objective][topology]
                json_data[objective][topology] = {
                    'oracle_metric': float(data['oracle_metric']),
                    'success_count': int(data['success_count']),
                    'total_vnrs': int(data['total_vnrs']),
                    'found_results': int(data['found_results']),
                    'not_found': int(data['not_found']),
                    'no_best_algo': int(data['no_best_algo'])
                }

    json.dump(json_data, f, indent=2)

print(f"\n✅ Saved to: models/oracle_performance_true.json")
print("="*80)
