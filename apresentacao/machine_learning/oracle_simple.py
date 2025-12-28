#!/usr/bin/env python3
"""
ORACLE: For each VNR, check if best_for_rac succeeded
"""

import pandas as pd
import json
from pathlib import Path

# Load data
vnr_feat = pd.read_csv('datasets/vnr_features.csv')
test_clean = pd.read_csv('datasets/vnr_clean.csv')

print("Calculating Oracle RAC...")

results = {}

for topo in ['tree', 'fat_tree', 'waxman_16']:
    topo_test = test_clean[test_clean['topology'] == topo]

    # For each VNR in test, get its best_for_rac and check if it succeeded
    successes = []

    for _, row in topo_test.iterrows():
        best_algo = row['best_for_rac']

        # Check if this algorithm succeeded for this VNR
        vnr_result = vnr_feat[
            (vnr_feat['topology'] == topo) &
            (vnr_feat['seed'] == row['seed']) &
            (vnr_feat['v_net_id'] == row['v_net_id']) &
            (vnr_feat['algorithm'] == best_algo) &
            (vnr_feat['success'] == True)
        ]

        successes.append(len(vnr_result) > 0)

    oracle_rac = (sum(successes) / len(successes)) * 100 if successes else 0
    results[topo] = oracle_rac

    print(f"{topo:15s}: {sum(successes)}/{len(successes)} = {oracle_rac:.1f}%")

# Save
with open('models/oracle_from_test_set.json', 'w') as f:
    json.dump({'rac': {t: {'oracle_metric': v} for t, v in results.items()}}, f, indent=2)

print("\n✅ Saved!")
