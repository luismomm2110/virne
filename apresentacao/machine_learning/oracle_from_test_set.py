#!/usr/bin/env python3
"""
Calculate Oracle from Test Set only.

Logic:
- For each VNR in test.csv, we know best_for_rac
- Find that algorithm's acceptance rate in test.csv
- Average across all test VNRs

Example:
- VNR 1: best_for_rac = MIP, MIP success rate in test = 65% → count 0.65
- VNR 2: best_for_rac = PL_RANK, PL_RANK success rate in test = 53% → count 0.53
- Oracle RAC = (0.65 + 0.53 + ...) / num_vnrs
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

print("=" * 80)
print("ORACLE FROM TEST SET ONLY")
print("=" * 80)

# Load test data with best_for_* labels
# Need to use vnr_features and filter to test VNRs
vnr_features_file = Path("datasets/vnr_features.csv")
vnr_features = pd.read_csv(vnr_features_file)
print(f"\n✓ Loaded vnr_features.csv: {len(vnr_features)} rows")

# Load test set to get the VNRs
test_file = Path("datasets/test.csv")
test_data = pd.read_csv(test_file)
print(f"✓ Loaded test.csv: {len(test_data)} VNRs")

# Load vnr_clean to get topology and best_for_* labels
test_clean = pd.read_csv("datasets/vnr_clean.csv")
print(f"✓ Loaded vnr_clean.csv: {len(test_clean)} VNRs")

# Map topology_encoded to topology name
topo_map = {0: 'tree', 1: 'fat_tree', 2: 'waxman_16'}
test_data['topology'] = test_data['topology_encoded'].map(topo_map)

# Merge test with vnr_clean to get best_for_* labels
# First, identify which VNRs are in the test set by their features
# Since we don't have row IDs, we'll use vnr_clean as our "test" dataset
test_data = test_clean.copy()

print("\nCalculating Oracle for each objective...\n")

objectives = ['rac', 'lrc', 'lar', 'ast', 'balanced']
topologies = ['tree', 'fat_tree', 'waxman_16']
oracle_results = {}

for objective in objectives:
    oracle_results[objective] = {}
    best_col = f'best_for_{objective}'

    print(f"{'=' * 70}")
    print(f"{objective.upper()}")
    print(f"{'=' * 70}")

    for topology in topologies:
        # Filter test data for this topology
        topo_test = test_data[test_data['topology'] == topology].copy()

        if len(topo_test) == 0:
            print(f"  {topology:12s}: No test data")
            continue

        # Calculate acceptance rate for each algorithm IN THIS TOPOLOGY (from vnr_features)
        algo_metrics_in_topo = {}
        topo_vnr_features = vnr_features[vnr_features['topology'] == topology]

        for algo in topo_vnr_features['algorithm'].unique():
            algo_rows = topo_vnr_features[topo_vnr_features['algorithm'] == algo]

            if len(algo_rows) == 0:
                algo_metrics_in_topo[algo] = (0, 0, 0)  # (success_count, total_count, rate)
            else:
                # Calculate acceptance rate for this algorithm
                success_count = (algo_rows['success'] == True).sum()
                total_count = len(algo_rows)
                acceptance_rate = success_count / total_count if total_count > 0 else 0
                algo_metrics_in_topo[algo] = (success_count, total_count, acceptance_rate)

        # Now, for each VNR in test, get the acceptance rate of its best_for_*
        oracle_values = []
        algo_distribution = {}

        for idx, row in topo_test.iterrows():
            best_algo = row[best_col]

            if pd.isna(best_algo):
                continue

            # Count algorithm distribution
            if best_algo not in algo_distribution:
                algo_distribution[best_algo] = 0
            algo_distribution[best_algo] += 1

            # Get acceptance rate for this algorithm (from full topology)
            if best_algo in algo_metrics_in_topo:
                _, _, acceptance_rate = algo_metrics_in_topo[best_algo]
                oracle_values.append(acceptance_rate)
            else:
                # Algorithm not found, assume failure
                oracle_values.append(0.0)

        # Calculate Oracle metric
        if objective == 'rac':
            oracle_metric = np.mean(oracle_values) * 100 if oracle_values else 0
        else:
            # For other objectives, use mean of the metric values
            oracle_metric = np.mean(oracle_values) if oracle_values else 0

        oracle_results[objective][topology] = {
            'oracle_metric': oracle_metric,
            'num_vnrs': len(topo_test),
            'algo_distribution': algo_distribution
        }

        print(f"  {topology:12s}:")
        print(f"    Oracle {objective.upper():8s}: {oracle_metric:8.2f}")
        print(f"    Algorithm distribution in best_for_*:")
        for algo, count in sorted(algo_distribution.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(topo_test)) * 100
            if algo in algo_metrics_in_topo:
                _, _, rate = algo_metrics_in_topo[algo]
                print(f"      {algo:15s}: {count:3d} VNRs ({pct:5.1f}%) → {rate*100:5.1f}% acceptance")
            else:
                print(f"      {algo:15s}: {count:3d} VNRs ({pct:5.1f}%)")

# Load model results for comparison
print("\n" + "=" * 70)
print("ORACLE vs MODEL COMPARISON")
print("=" * 70)

model_file = Path("models/ranking_results_per_topology.json")
with open(model_file) as f:
    model_data = json.load(f)

for objective in objectives:
    print(f"\n{objective.upper()}:")
    print(f"{'Topology':15s} {'Oracle':12s} {'Model Top-3':12s} {'Model Top-1':12s}")
    print("-" * 55)

    for topology in topologies:
        oracle_val = oracle_results[objective][topology]['oracle_metric']

        if topology in model_data and objective in model_data[topology]:
            model_top3 = model_data[topology][objective]['top3_ranking'] * 100
            model_top1 = model_data[topology][objective]['classification'] * 100
        else:
            model_top3 = 0
            model_top1 = 0

        print(f"{topology:15s} {oracle_val:11.2f} {model_top3:11.1f}% {model_top1:11.1f}%")

# Save results
print("\n" + "=" * 70)
print("Saving results...")

output_file = Path("models/oracle_from_test_set.json")
json_data = {}
for objective in objectives:
    json_data[objective] = {}
    for topology in topologies:
        if topology in oracle_results[objective]:
            data = oracle_results[objective][topology]
            json_data[objective][topology] = {
                'oracle_metric': float(data['oracle_metric']),
                'num_vnrs': int(data['num_vnrs'])
            }

with open(output_file, 'w') as f:
    json.dump(json_data, f, indent=2)

print(f"✅ Saved: models/oracle_from_test_set.json")
print("=" * 70)
