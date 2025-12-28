#!/usr/bin/env python3
"""
Calculate Oracle Performance for ALL Metrics

Oracle (a posteriori): For each VNR and each metric, if ANY algorithm achieved
the best performance for that metric, the Oracle would select one of the
best-performing algorithms.

Metrics calculated:
1. RAC (Acceptance Rate): % of accepted VNRs
2. Revenue: Total revenue generated
3. Cost: Total cost spent
4. Revenue-Cost Ratio (LRC): Revenue / Cost (higher is better)
5. Acceptance Rate with Revenue (LAR): How much revenue from accepted VNRs
6. Solving Time (AST): Average solving time per accepted VNR
7. Balanced Score: Weighted combination of RAC and efficiency
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path

print("=" * 80)
print("ORACLE PERFORMANCE CALCULATION - ALL METRICS")
print("=" * 80)

# Load datasets
print("\n📂 Loading datasets...")

vnr_feat = pd.read_csv('datasets/vnr_features.csv')
print(f"  ✓ vnr_features.csv: {len(vnr_feat)} rows")

vnr_clean = pd.read_csv('datasets/vnr_clean.csv')
print(f"  ✓ vnr_clean.csv: {len(vnr_clean)} rows")

test = pd.read_csv('datasets/test.csv')
print(f"  ✓ test.csv: {len(test)} rows")

# ============================================================================
# STEP 1: Match test.csv with vnr_clean using features
# ============================================================================

print("\n🔗 Matching test.csv with vnr_clean.csv using features...")

topo_map = {0: 'tree', 1: 'fat_tree', 2: 'waxman_16'}
test['topology'] = test['topology_encoded'].map(topo_map)

test['matched_v_net_id'] = None
test['matched_seed'] = None

matches_found = 0
match_cols = ['v_net_num_nodes', 'v_net_num_edges', 'v_net_demand']

for idx, test_row in test.iterrows():
    topo = test_row['topology']

    clean_matches = vnr_clean[
        (vnr_clean['topology'] == topo) &
        (vnr_clean['v_net_num_nodes'] == test_row['v_net_num_nodes']) &
        (vnr_clean['v_net_num_edges'] == test_row['v_net_num_edges']) &
        (np.abs(vnr_clean['v_net_demand'] - test_row['v_net_demand']) < 1)
    ]

    if len(clean_matches) > 0:
        test.at[idx, 'matched_v_net_id'] = clean_matches.iloc[0]['v_net_id']
        test.at[idx, 'matched_seed'] = clean_matches.iloc[0]['seed']
        matches_found += 1

print(f"  ✓ Matched {matches_found}/{len(test)} rows ({100*matches_found/len(test):.1f}%)")

test_matched = test[test['matched_v_net_id'].notna()].copy()

print(f"\n  VNRs by topology after matching:")
for topo in ['tree', 'fat_tree', 'waxman_16']:
    count = len(test_matched[test_matched['topology'] == topo])
    print(f"    {topo:12s}: {count} VNRs")

# ============================================================================
# STEP 2: Calculate Oracle for each metric
# ============================================================================

print("\n" + "=" * 80)
print("CALCULATING ORACLE FOR ALL METRICS")
print("=" * 80)

results = {}

METRICS = {
    'rac': {
        'name': 'Acceptance Rate',
        'column': 'success',
        'type': 'binary',  # 1 if success
        'direction': 'maximize'
    },
    'revenue': {
        'name': 'Total Revenue',
        'column': 'v_net_revenue',
        'type': 'sum',
        'direction': 'maximize'
    },
    'cost': {
        'name': 'Total Cost',
        'column': 'v_net_cost',
        'type': 'sum',
        'direction': 'minimize'
    },
    'time_cost': {
        'name': 'Total Time Cost',
        'column': 'v_net_time_cost',
        'type': 'sum',
        'direction': 'minimize'
    },
    'solving_time': {
        'name': 'Average Solving Time',
        'column': 'clock_time_per_vnr',
        'type': 'average',
        'direction': 'minimize'
    },
    'time_revenue': {
        'name': 'Time Revenue',
        'column': 'v_net_time_revenue',
        'type': 'sum',
        'direction': 'maximize'
    }
}

for topo in ['tree', 'fat_tree', 'waxman_16']:
    test_topo = test_matched[test_matched['topology'] == topo]

    if len(test_topo) == 0:
        print(f"\n{topo:12s}: No test data")
        continue

    results[topo] = {}

    for metric_key, metric_config in METRICS.items():
        oracle_value = calculate_oracle_for_metric(
            test_topo,
            vnr_feat,
            topo,
            metric_key,
            metric_config
        )

        results[topo][metric_key] = oracle_value
        print(f"\n{topo} - {metric_config['name']}:")
        print(f"  Oracle: {oracle_value:.2f}")

# ============================================================================
# STEP 3: Save results
# ============================================================================

print("\n" + "=" * 80)
print("Saving results...")

output_file = Path("models/oracle_all_metrics.json")

json_data = results

with open(output_file, 'w') as f:
    json.dump(json_data, f, indent=2)

print(f"✅ Saved: {output_file}")

# ============================================================================
# Helper function
# ============================================================================

def calculate_oracle_for_metric(test_topo, vnr_feat, topo, metric_key, metric_config):
    """Calculate Oracle value for a specific metric"""

    metric_column = metric_config['column']
    metric_type = metric_config['type']
    direction = metric_config['direction']

    total_value = 0
    successes = 0

    for idx, row in test_topo.iterrows():
        v_net_id = int(row['matched_v_net_id'])
        seed = int(row['matched_seed'])

        # Get all algorithm results for this VNR
        vnr_results = vnr_feat[
            (vnr_feat['topology'] == topo) &
            (vnr_feat['seed'] == seed) &
            (vnr_feat['v_net_id'] == v_net_id)
        ]

        if len(vnr_results) == 0:
            continue

        algo_results = vnr_results.groupby('algorithm').first().reset_index()

        # For RAC: check if ANY algorithm succeeded
        if metric_key == 'rac':
            if (algo_results['success'] == True).any():
                successes += 1
        else:
            # For other metrics: find the best value across all algorithms
            if (algo_results['success'] == True).any():
                successful_algos = algo_results[algo_results['success'] == True]

                if direction == 'maximize':
                    best_value = successful_algos[metric_column].max()
                else:  # minimize
                    best_value = successful_algos[metric_column].min()

                total_value += best_value
                successes += 1

    if metric_key == 'rac':
        oracle_value = (successes / len(test_topo)) * 100
    elif metric_type == 'sum':
        oracle_value = total_value
    elif metric_type == 'average':
        oracle_value = total_value / successes if successes > 0 else 0
    else:
        oracle_value = 0

    return oracle_value

print("\n✅ Oracle calculation complete!")
