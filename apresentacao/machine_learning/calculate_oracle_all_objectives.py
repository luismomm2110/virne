#!/usr/bin/env python3
"""
Calculate Oracle Performance for ALL 5 OBJECTIVES

Oracle (a posteriori): For each VNR and each objective, if ANY algorithm achieved
the best performance for that objective, the Oracle would select one of the
best-performing algorithms.

Objectives:
1. RAC (Request Acceptance Rate) - % of accepted VNRs
2. LRC (Long-Term Revenue-to-Cost) - Revenue / Cost ratio
3. LAR (Long-Term Average Revenue) - Total revenue per accepted VNR
4. AST (Average Solving Time) - Time cost per accepted VNR
5. BALANCED (0.8*revenue - 0.2*time) - Weighted combination
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path

print("=" * 80)
print("ORACLE PERFORMANCE CALCULATION - ALL 5 OBJECTIVES")
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
# HELPER FUNCTION
# ============================================================================

def calculate_oracle_for_objective(test_topo, vnr_feat, topo, obj_key, obj_config):
    """Calculate Oracle value for a specific objective"""

    total_value = 0
    count = 0

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

        # Filter for successful embeddings if required
        if obj_config.get('filter_success', False):
            algo_results = algo_results[algo_results['success'] == True]

        if len(algo_results) == 0:
            continue

        # Calculate metric based on objective type
        if obj_key == 'balanced':
            # Formula-based calculation
            algo_results['metric'] = algo_results.apply(
                lambda row: obj_config['formula'](
                    row[obj_config['metric_cols']['revenue']],
                    row[obj_config['metric_cols']['time']]
                ),
                axis=1
            )
        else:
            # Direct metric column
            algo_results['metric'] = algo_results[obj_config['metric_col']]

        # Find best value according to direction
        if obj_config['direction'] == 'maximize':
            best_value = algo_results['metric'].max()
        else:  # minimize
            best_value = algo_results['metric'].min()

        total_value += best_value
        count += 1

    # Calculate average
    oracle_value = total_value / count if count > 0 else 0

    return oracle_value

# ============================================================================
# STEP 2: Define Objectives
# ============================================================================

OBJECTIVES = {
    'lrc': {
        'name': 'Long-Term Revenue-to-Cost',
        'metric_col': 'v_net_r2c_ratio',  # Revenue / Cost
        'direction': 'maximize',
        'filter_success': True,  # Only count successful embeddings
    },
    'lar': {
        'name': 'Long-Term Average Revenue',
        'metric_col': 'v_net_revenue',
        'direction': 'maximize',
        'filter_success': True,
    },
    'ast': {
        'name': 'Average Solving Time',
        'metric_col': 'clock_time_per_vnr',
        'direction': 'minimize',
        'filter_success': True,
    },
    'balanced': {
        'name': 'Balanced (0.8*revenue - 0.2*time)',
        'metric_cols': {'revenue': 'v_net_revenue', 'time': 'clock_time_per_vnr'},
        'direction': 'maximize',
        'formula': lambda r, t: 0.8 * r - 0.2 * t,
        'filter_success': True,
    }
}

# ============================================================================
# STEP 3: Calculate Oracle for each objective
# ============================================================================

print("\n" + "=" * 80)
print("CALCULATING ORACLE FOR ALL OBJECTIVES")
print("=" * 80)

results = {}

for topo in ['tree', 'fat_tree', 'waxman_16']:
    test_topo = test_matched[test_matched['topology'] == topo]

    if len(test_topo) == 0:
        print(f"\n{topo:12s}: No test data")
        continue

    print(f"\n{topo.upper()}:")
    print("-" * 60)

    results[topo] = {}

    for obj_key, obj_config in OBJECTIVES.items():
        oracle_value = calculate_oracle_for_objective(
            test_topo,
            vnr_feat,
            topo,
            obj_key,
            obj_config
        )

        results[topo][obj_key] = oracle_value
        print(f"  {obj_config['name']:40s}: {oracle_value:10.2f}")

# ============================================================================
# STEP 4: Load existing RAC Oracle for comparison
# ============================================================================

print("\n" + "=" * 80)
print("ORACLE SUMMARY - ALL 5 OBJECTIVES")
print("=" * 80)

# Load RAC Oracle
rac_file = Path("models/oracle_performance_correct.json")
with open(rac_file) as f:
    rac_data = json.load(f)

# Print summary table
print("\n" + "=" * 120)
print(f"{'Topology':<12s} {'RAC (%)':<12s} {'LRC':<12s} {'LAR':<12s} {'AST (ms)':<12s} {'BALANCED':<12s}")
print("-" * 120)

for topo in ['tree', 'fat_tree', 'waxman_16']:
    rac_val = rac_data.get('rac', {}).get(topo, {}).get('oracle_metric', 0)
    lrc_val = results.get(topo, {}).get('lrc', 0)
    lar_val = results.get(topo, {}).get('lar', 0)
    ast_val = results.get(topo, {}).get('ast', 0)
    bal_val = results.get(topo, {}).get('balanced', 0)

    print(f"{topo:<12s} {rac_val:>10.2f}% {lrc_val:>10.2f}  {lar_val:>10.2f}  {ast_val:>10.2f}  {bal_val:>10.2f}")

# ============================================================================
# STEP 5: Save results
# ============================================================================

print("\n" + "=" * 80)
print("Saving results...")

output_file = Path("models/oracle_all_objectives.json")

json_data = {
    "rac": rac_data.get("rac", {}),  # Include RAC for reference
    "lrc": {},
    "lar": {},
    "ast": {},
    "balanced": {}
}

for topo in ['tree', 'fat_tree', 'waxman_16']:
    if topo in results:
        json_data["lrc"][topo] = float(results[topo].get('lrc', 0))
        json_data["lar"][topo] = float(results[topo].get('lar', 0))
        json_data["ast"][topo] = float(results[topo].get('ast', 0))
        json_data["balanced"][topo] = float(results[topo].get('balanced', 0))

with open(output_file, 'w') as f:
    json.dump(json_data, f, indent=2)

print(f"✅ Saved: {output_file}")

print("\n✅ Oracle calculation complete!")
print(f"All results saved to models/oracle_all_objectives.json")
