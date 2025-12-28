# Oracle Performance: A Posteriori Algorithm Selection

## Overview

The **Oracle** represents the theoretical maximum performance achievable if we could always select the **optimal algorithm for each Virtual Network Request (VNR)**.

It is a **a posteriori** metric, meaning we evaluate it by looking back at historical execution results to determine which algorithm would have been the best choice for each VNR.

---

## Definition

For each VNR, the Oracle asks:

> **"If we had selected the best-performing algorithm(s) for this specific VNR (from the execution history), would the VNR have been accepted?"**

### Calculation Steps

1. **For each unique VNR** (identified by `topology`, `seed`, `v_net_id`):
   - Look at all algorithm execution results for that VNR
   - Group results by algorithm (taking the first result per algorithm)
   - Check if ANY algorithm successfully embedded the VNR

2. **If at least one algorithm succeeded**:
   - Count this VNR as an Oracle success
   - This VNR is embeddable (there exists at least one working solution)

3. **If no algorithm succeeded**:
   - Count this as an Oracle failure
   - This VNR cannot be embedded regardless of algorithm choice

4. **Calculate Oracle RAC**:
   ```
   Oracle RAC = (# VNRs where at least one algo succeeded) / (total VNRs) × 100%
   ```

---

## Why This Matters

The Oracle provides a **ceiling** for algorithm selection performance:

```
Individual Algorithm Accuracy < Model Accuracy ≤ Oracle Accuracy
```

- **Individual Algorithms**: Single heuristic/exact/meta-heuristic performance
- **Model Accuracy**: ML model's success at selecting a good algorithm
- **Oracle Accuracy**: Theoretical maximum (someone with perfect foresight)

### Example

For Tree Topology with 186 test VNRs:

```
VNR 1: Algorithms that work: {MIP, PL_RANK, GA_META}
       → Oracle can choose any of them → SUCCESS

VNR 2: Algorithms that work: {RW_RANK_BFS}
       → Oracle chooses RW_RANK_BFS → SUCCESS

VNR 3: Algorithms that work: {} (NONE!)
       → Oracle cannot embed this VNR → FAILURE

...

Oracle RAC = 182/186 = 97.85%
```

---

## Dataset Alignment Issue (Important!)

### The Problem

Initially, Oracle and Model metrics were calculated on **different test sets**:

- **Oracle**: Calculated using `vnr_clean.csv` (4,500 unique VNRs across all topologies)
- **Model**: Trained/tested using `test.csv` (617 VNRs in the test split)

This made direct comparison impossible: comparing Oracle on 4,500 VNRs vs Model on 617 VNRs.

### The Solution

**Match `test.csv` with `vnr_clean.csv` using features:**

1. For each row in `test.csv` (which has no `v_net_id`):
   - Extract feature values: `v_net_num_nodes`, `v_net_num_edges`, `v_net_demand`

2. Search `vnr_clean.csv` for a VNR with:
   - Same `topology`
   - Same feature values (with small tolerance for floating-point differences)

3. If match found:
   - Get `v_net_id` and `seed` from `vnr_clean`
   - Use these to look up execution results in `vnr_features.csv`

**Result**: 617/617 rows successfully matched (100%) ✓

---

## Final Oracle Metrics

**Oracle RAC (Request Acceptance Rate) - a posteriori, optimal algorithm selection:**

| Topology | Oracle RAC | Model Top-3 | Difference |
|----------|-----------|-------------|-----------|
| Tree | **97.85%** | 93.37% | +4.48% |
| Fat-Tree | **100.00%** | 79.30% | +20.70% |
| Waxman-16 | **99.52%** | 85.65% | +13.87% |

### Interpretation

- **Oracle ≥ Model**: ✓ Correct (Oracle is the upper bound)
- **Gap shows room for improvement**: The model's Top-3 ranking accuracy is 4-21 percentage points below Oracle
- **Larger gap on Fat-Tree**: The model struggles more here; room for better algorithm selection

---

## How Oracle Relates to Other Metrics

### vs. `best_for_rac` Label

The `best_for_rac` column in the dataset is:
```python
# For each unique VNR, pick the FIRST algorithm that succeeded
best_for_rac = first(accepted_algorithms)
```

This is **different from Oracle**:
- `best_for_rac`: One specific "winning" algorithm (for ML training target)
- **Oracle**: "Did ANY algorithm work?" (for performance ceiling)

### vs. Model Accuracy

- **Classification Accuracy**: Does the model correctly predict which algorithm is `best_for_rac`?
- **Top-3 Ranking**: Is the correct algorithm in the model's top-3 recommendations?
- **Oracle**: Would ANY of the model's recommendations work?

---

## Implementation Details

### Data Files Used

1. **`datasets/vnr_clean.csv`** (4,500 rows):
   - One row per unique VNR
   - Columns: `topology`, `seed`, `v_net_id`, `best_for_*`, features...

2. **`datasets/vnr_features.csv`** (658,222 rows):
   - One row per VNR × Algorithm combination (with execution results)
   - Columns: `topology`, `seed`, `v_net_id`, `algorithm`, `success`, `v_net_revenue`, ...

3. **`datasets/test.csv`** (617 rows):
   - ML model's test set (features only, no v_net_id)
   - Used to generate model predictions

4. **`models/oracle_performance_correct.json`**:
   - Stores final Oracle metrics

### Calculation Code

```python
import pandas as pd

vnr_feat = pd.read_csv('datasets/vnr_features.csv')
test_matched = test.copy()  # With v_net_id and seed from matching

results = {}

for topo in ['tree', 'fat_tree', 'waxman_16']:
    test_topo = test_matched[test_matched['topology'] == topo]

    best_algo_successes = 0

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

        # Group by algorithm, take first result per algorithm
        algo_results = vnr_results.groupby('algorithm').first().reset_index()

        # Check if ANY algorithm succeeded
        successes = algo_results[algo_results['success'] == True]

        if len(successes) > 0:
            best_algo_successes += 1

    oracle_rac = (best_algo_successes / len(test_topo)) * 100
    results[topo] = oracle_rac
```

---

## Key Insights

1. **Oracle is not 100%**: Some VNRs cannot be embedded regardless of algorithm choice
   - Tree: 97.85% → 4 VNRs are "unsolvable"
   - Fat-Tree: 100% → All VNRs can be solved by at least one algorithm
   - Waxman-16: 99.52% → 1 VNR is "unsolvable"

2. **Model Performance Gap**:
   - Best case (Fat-Tree): Model achieves 79.3% of Oracle's 100% (79.3% utilization)
   - Worst case (Tree): Model achieves 93.4% of Oracle's 97.85% (95.4% utilization)
   - Model can improve by recommending algorithms closer to the Oracle's optimal set

3. **Topology Differences**:
   - Fat-Tree shows largest gap (20.7%) → Model struggles with topology structure
   - Tree shows smallest gap (4.5%) → Model performs better here

---

## Related Files

- **Calculation Script**: See `calculate_oracle_correct.py` for exact implementation
- **Model Metrics**: `models/ranking_results_per_topology.json` (model Top-3 and classification accuracy)
- **Dataset Creation**: `2_prepare_dataset.py` shows how `best_for_*` labels are created

---

## Summary

The **Oracle is the theoretical performance ceiling** if we could always make the optimal algorithm choice. By comparing Model accuracy to Oracle:

- We quantify how close the ML model comes to optimal
- We identify which topologies need better algorithm selection
- We provide a reference for improvement targets
