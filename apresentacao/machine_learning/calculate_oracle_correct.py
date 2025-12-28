#!/usr/bin/env python3
"""
Calculate Oracle Performance - CORRECT VERSION

Oracle (a posteriori): For each VNR, if ANY algorithm successfully embedded it,
the Oracle would select one of the working algorithms and succeed.

Key insight: Oracle measures the theoretical maximum performance if we could
always choose optimally, i.e., the ceiling for algorithm selection performance.

This version correctly:
1. Matches test.csv (617 VNRs without v_net_id) with vnr_clean.csv using features
2. Calculates Oracle only on the same test set used to evaluate the model
3. Compares Oracle with Model metrics in a fair way
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path

print("=" * 80)
print("ORACLE PERFORMANCE CALCULATION - CORRECT VERSION")
print("=" * 80)

# Load datasets
print("\n📂 Loading datasets...")

vnr_feat = pd.read_csv('datasets/vnr_features.csv')
print(f"  ✓ vnr_features.csv: {len(vnr_feat)} rows (VNR × Algorithm results)")

vnr_clean = pd.read_csv('datasets/vnr_clean.csv')
print(f"  ✓ vnr_clean.csv: {len(vnr_clean)} rows (unique VNRs)")

test = pd.read_csv('datasets/test.csv')
print(f"  ✓ test.csv: {len(test)} rows (model test set, no v_net_id)")

# ============================================================================
# STEP 1: Match test.csv with vnr_clean using features
# ============================================================================

print("\n🔗 Matching test.csv with vnr_clean.csv using features...")

# Decode topology
topo_map = {0: 'tree', 1: 'fat_tree', 2: 'waxman_16'}
test['topology'] = test['topology_encoded'].map(topo_map)

# Add columns to store matched v_net_id and seed
test['matched_v_net_id'] = None
test['matched_seed'] = None

matches_found = 0
match_cols = ['v_net_num_nodes', 'v_net_num_edges', 'v_net_demand']

for idx, test_row in test.iterrows():
    topo = test_row['topology']

    # Search vnr_clean for matching features
    clean_matches = vnr_clean[
        (vnr_clean['topology'] == topo) &
        (vnr_clean['v_net_num_nodes'] == test_row['v_net_num_nodes']) &
        (vnr_clean['v_net_num_edges'] == test_row['v_net_num_edges']) &
        (np.abs(vnr_clean['v_net_demand'] - test_row['v_net_demand']) < 1)  # Floating point tolerance
    ]

    if len(clean_matches) > 0:
        # Take first match
        test.at[idx, 'matched_v_net_id'] = clean_matches.iloc[0]['v_net_id']
        test.at[idx, 'matched_seed'] = clean_matches.iloc[0]['seed']
        matches_found += 1

print(f"  ✓ Matched {matches_found}/{len(test)} rows ({100*matches_found/len(test):.1f}%)")

# Filter to matched rows only
test_matched = test[test['matched_v_net_id'].notna()].copy()

print(f"\n  VNRs by topology after matching:")
for topo in ['tree', 'fat_tree', 'waxman_16']:
    count = len(test_matched[test_matched['topology'] == topo])
    print(f"    {topo:12s}: {count} VNRs")

# ============================================================================
# STEP 2: Calculate Oracle for each topology
# ============================================================================

print("\n" + "=" * 80)
print("CALCULATING ORACLE PERFORMANCE (a posteriori)")
print("=" * 80)

results = {}

for topo in ['tree', 'fat_tree', 'waxman_16']:
    test_topo = test_matched[test_matched['topology'] == topo]

    if len(test_topo) == 0:
        print(f"\n{topo:12s}: No test data")
        continue

    successes = 0
    unsolvable_vnrs = []

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
            print(f"    WARNING: VNR {v_net_id} seed {seed} not found in vnr_features")
            continue

        # Group by algorithm and take first result per algorithm
        # (Some algorithms have multiple attempts per VNR)
        algo_results = vnr_results.groupby('algorithm').first().reset_index()

        # Check if ANY algorithm succeeded
        algo_successes = algo_results[algo_results['success'] == True]

        if len(algo_successes) > 0:
            # At least one algorithm worked → Oracle succeeds
            successes += 1
        else:
            # No algorithm worked → VNR is unsolvable
            unsolvable_vnrs.append(v_net_id)

    oracle_rac = (successes / len(test_topo)) * 100

    results[topo] = {
        'oracle_rac': oracle_rac,
        'successes': successes,
        'total': len(test_topo),
        'unsolvable_count': len(unsolvable_vnrs)
    }

    print(f"\n{topo:12s}:")
    print(f"  Oracle RAC: {successes}/{len(test_topo)} = {oracle_rac:7.2f}%")
    print(f"  Unsolvable VNRs: {len(unsolvable_vnrs)}")

# ============================================================================
# STEP 3: Compare with Model metrics
# ============================================================================

print("\n" + "=" * 80)
print("ORACLE vs MODEL COMPARISON")
print("=" * 80)

model_file = Path("models/ranking_results_per_topology.json")
with open(model_file) as f:
    model_data = json.load(f)

print(f"\n{'Topology':<12s} {'Oracle RAC':<15s} {'Model Top-3':<15s} {'Model Class':<15s} {'Oracle≥Top-3?':<15s}")
print("-" * 75)

comparison_results = {}

for topo in ['tree', 'fat_tree', 'waxman_16']:
    if topo not in results:
        continue

    oracle_val = results[topo]['oracle_rac']

    if topo in model_data and 'rac' in model_data[topo]:
        model_top3 = model_data[topo]['rac']['top3_ranking'] * 100
        model_class = model_data[topo]['rac']['classification'] * 100
        is_valid = oracle_val >= model_top3
        symbol = "✓" if is_valid else "✗"

        comparison_results[topo] = {
            'oracle_rac': oracle_val,
            'model_top3': model_top3,
            'model_class': model_class,
            'valid': is_valid
        }

        print(f"{topo:<12s} {oracle_val:>6.2f}%         {model_top3:>6.2f}%         {model_class:>6.2f}%          {symbol}")

# ============================================================================
# STEP 4: Save results
# ============================================================================

print("\n" + "=" * 80)
print("Saving results...")

output_file = Path("models/oracle_performance_correct.json")

json_data = {
    "rac": {}
}

for topo in ['tree', 'fat_tree', 'waxman_16']:
    if topo in results:
        data = results[topo]
        json_data["rac"][topo] = {
            "oracle_metric": float(data['oracle_rac']),
            "num_vnrs": int(data['total']),
            "successes": int(data['successes']),
            "unsolvable": int(data['unsolvable_count'])
        }

with open(output_file, 'w') as f:
    json.dump(json_data, f, indent=2)

print(f"✅ Saved: {output_file}")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("""
The Oracle represents the theoretical maximum performance if we could always
select the optimal algorithm for each VNR.

Key Findings:
""")

for topo in ['tree', 'fat_tree', 'waxman_16']:
    if topo in comparison_results:
        comp = comparison_results[topo]
        gap = comp['oracle_rac'] - comp['model_top3']
        print(f"""
{topo.upper()}:
  - Oracle RAC: {comp['oracle_rac']:.2f}%
    (If we could always choose an algorithm that works, {comp['oracle_rac']:.2f}% of VNRs would succeed)

  - Model Top-3: {comp['model_top3']:.2f}%
    (Model's top-3 recommendations include a working algorithm {comp['model_top3']:.2f}% of the time)

  - Gap: {gap:+.2f} percentage points
    (Room for improvement in algorithm selection)
""")

print("\n✅ Oracle calculation complete! Use oracle_performance_correct.json for visualizations.")
