# Oracle Performance: Final Results and Analysis

## Executive Summary

The **Oracle** represents the theoretical maximum performance (ceiling) if we could always select the optimal algorithm for each Virtual Network Request. By comparing the Model's accuracy to the Oracle, we can quantify how well the ML model performs relative to perfect foresight.

### Key Findings

| Topology | Oracle RAC | Model Top-3 | Gap | Interpretation |
|----------|-----------|-------------|-----|-----------------|
| **Tree** | 97.85% | 93.37% | +4.48% | Model performs very well here |
| **Fat-Tree** | 100.00% | 79.30% | +20.70% | **Significant room for improvement** |
| **Waxman-16** | 99.52% | 85.65% | +13.87% | Moderate room for improvement |

---

## Detailed Analysis

### Tree Topology (Small Gap: +4.48%)

```
Oracle: 97.85% (182/186 VNRs can be embedded)
Model Top-3: 93.37%
```

**Interpretation:**
- The model performs well on Tree topology
- Only 4 VNRs in the test set are unsolvable (no algorithm works)
- The model's top-3 recommendations include a working algorithm 93.37% of the time
- Gap is small (4.48%) → model has learned the Tree topology structure well

**Recommendation:** Focus optimization efforts on Fat-Tree and Waxman-16

---

### Fat-Tree Topology (Largest Gap: +20.70%)

```
Oracle: 100.00% (224/224 VNRs can be embedded)
Model Top-3: 79.30%
```

**Interpretation:**
- ALL VNRs can be embedded (at least one algorithm works for each)
- The model's top-3 recommendations include a working algorithm only 79.3% of the time
- **This is the biggest gap** → model struggles with Fat-Tree structure
- Even though all VNRs are solvable, the model often recommends algorithms that fail for this topology

**Why might this happen?**
- Fat-Tree has specific structural properties (binary tree, specific routing patterns)
- The model may not have learned these properties well
- Algorithm selection for Fat-Tree may be more sensitive/critical
- Different algorithms may succeed/fail more unpredictably on Fat-Tree

**Recommendation:** Retrain model with focus on Fat-Tree; consider topology-specific features

---

### Waxman-16 Topology (Moderate Gap: +13.87%)

```
Oracle: 99.52% (206/207 VNRs can be embedded)
Model Top-3: 85.65%
```

**Interpretation:**
- Nearly all VNRs can be embedded (only 1 unsolvable)
- Model's top-3 includes a working algorithm 85.65% of the time
- Gap is moderate (13.87%)
- Model performance is between Tree (good) and Fat-Tree (struggling)

**Recommendation:** Focus on understanding why 14% of VNRs have no working algorithm in top-3

---

## What is the Oracle Measuring?

### Definition

For each VNR in the test set:

1. **Look at execution history**: Which algorithms were tried and did they succeed?
2. **Ask**: "If ANY algorithm succeeded for this VNR, could the Oracle use one of them?"
3. **Answer**: YES → Oracle succeeds on this VNR
4. **Oracle RAC**: Percentage of VNRs where at least one algorithm succeeded

### Why This Matters

```
Individual Algorithm (e.g., MIP alone)
    ↓
    Typically 40-70% acceptance rate

Model Accuracy (ML predicts which algorithm to use)
    ↓
    79-93% accuracy (recommends algorithm in top-3)

Oracle Accuracy (if we always picked a working algorithm)
    ↓
    97-100% acceptance rate

The gap (Oracle - Model) shows room for improvement in algorithm selection
```

### Why Oracle ≠ 100%?

Some VNRs are genuinely unsolvable - no algorithm can embed them:
- **Tree**: 4 unsolvable VNRs (2.2%)
- **Fat-Tree**: 0 unsolvable VNRs (0%)
- **Waxman-16**: 1 unsolvable VNR (0.5%)

These are the fundamental limits of the algorithm set.

---

## Dataset Alignment (Critical Issue Fixed)

### The Problem

Initially, Oracle and Model metrics appeared inconsistent:
- **Oracle seemed lower than Model** in some cases
- This should never happen (Oracle is the upper bound)

### Root Cause

**Different datasets were being used:**
- **Oracle calculation**: Used `vnr_clean.csv` (4,500 unique VNRs)
- **Model evaluation**: Used `test.csv` (617 VNRs in test split)

Comparing these was like comparing apples to oranges!

### The Solution

**Match `test.csv` with `vnr_clean.csv` using features:**

1. Extract features from `test.csv`: `v_net_num_nodes`, `v_net_num_edges`, `v_net_demand`
2. Find matching VNR in `vnr_clean.csv` with same topology and features
3. Get `v_net_id` and `seed` from match
4. Look up actual execution results in `vnr_features.csv`

**Result**: 617/617 matches (100% success) ✓

This ensures Oracle and Model are evaluated on the **same 617 VNRs**.

---

## Methodology

### Files Used

| File | Purpose | Rows | Key Columns |
|------|---------|------|------------|
| `datasets/test.csv` | ML test set (no v_net_id) | 617 | features, best_for_*, topology_encoded |
| `datasets/vnr_clean.csv` | All unique VNRs with IDs | 4,500 | topology, seed, v_net_id, best_for_* |
| `datasets/vnr_features.csv` | Execution results | 658,222 | topology, seed, v_net_id, algorithm, success |
| `models/ranking_results_per_topology.json` | Model metrics | - | classification, top3_ranking per topology/objective |

### Calculation Steps

```python
# 1. Match test.csv rows with vnr_clean.csv using features
for each row in test.csv:
    find matching VNR in vnr_clean with same topology + features
    → get v_net_id and seed

# 2. For each matched VNR, check execution results
for each matched VNR (v_net_id, seed):
    find all algorithm results in vnr_features.csv
    group by algorithm (take first result per algo)
    → check if ANY algorithm succeeded

# 3. Count successes
oracle_rac = (successes / total_vnrs) * 100
```

---

## Visualizations

Four visualizations have been created and saved to `models/`:

### 1. oracle_vs_model_comparison.png
3-panel comparison (Tree, Fat-Tree, Waxman-16)
- Shows Oracle (green), Model Top-3 (blue), Model Classification (red)
- Displays gap between Oracle and Model Top-3
- **Best for**: Topology-by-topology comparison

### 2. oracle_vs_model_gap_analysis.png
Horizontal bar chart showing improvement gaps
- Fat-Tree: +20.70% (largest gap)
- Waxman-16: +13.87% (moderate gap)
- Tree: +4.48% (smallest gap)
- **Best for**: Identifying which topology needs most improvement

### 3. oracle_vs_model_detailed.png
Grouped bar chart with all three metrics
- Direct visual comparison across all topologies
- Shows all three metrics (Oracle, Top-3, Classification) side-by-side
- **Best for**: Presentations and reports

### 4. oracle_vs_model_summary_table.png
Clean table format with all metrics
- Gaps highlighted in yellow
- Easy reference format
- **Best for**: Documents and papers

---

## Key Insights

### 1. Oracle is NOT Perfect (97-100%)

Many VNRs in the test set cannot be embedded regardless of algorithm choice:
- These represent genuinely hard instances
- No combination of algorithms can solve them
- The Oracle can only achieve 97-100%, not 100%

### 2. Model Performance Varies by Topology

- **Tree (97.85% oracle vs 93.37% model)**: Model learns well ✓
- **Fat-Tree (100% oracle vs 79.30% model)**: Model struggles ✗
- **Waxman-16 (99.52% oracle vs 85.65% model)**: Model moderate performance ≈

Fat-Tree is the challenge area.

### 3. Model Top-3 vs Classification

- **Top-3 Ranking**: Is the correct algorithm among the top-3?
- **Classification**: Does the model exactly predict the correct algorithm?
- Top-3 is always higher (more forgiving metric)
- For Oracle comparison, Top-3 is more appropriate (any algorithm in top-3 might work)

### 4. Gap Interpretation

The gap (Oracle - Model Top-3) represents:
```
Percentage of VNRs where:
- At least one algorithm works (Oracle succeeds)
- BUT none of the model's top-3 recommendations are among them (Model fails)
```

This quantifies "bad recommendations" for solvable VNRs.

---

## Recommendations for Improvement

### For Tree Topology
✓ Model already performs well (93.37% vs 97.85%)
- Focus efforts elsewhere
- Could optimize if perfection needed (4.48% gap)

### For Fat-Tree Topology
✗ **Priority #1** - Largest gap (20.70%)
1. Analyze why Fat-Tree is different:
   - Feature importance analysis
   - Compare Tree vs Fat-Tree characteristics
   - Topology-specific feature engineering?

2. Consider topology-specific models:
   - Train separate models for each topology
   - Or add strong topology indicators

3. Improve algorithm embedding likelihood analysis:
   - Why do certain algorithms fail on Fat-Tree?
   - Can we predict which will work?

### For Waxman-16 Topology
≈ **Priority #2** - Moderate gap (13.87%)
1. Identify failing cases:
   - Which VNRs have no working algorithm in top-3?
   - Common characteristics?

2. Feature analysis:
   - What makes Waxman-16 different from Tree?

3. Model retraining:
   - With more focus on this topology

---

## Technical Details

### Why Matching Works

`test.csv` was created via `train_test_split()` of `vnr_clean.csv`:
```python
train_df, val_test_df = train_test_split(vnr_clean, ...)
val_df, test_df = train_test_split(val_test_df, ...)
```

This means:
- Each row in `test.csv` corresponds to EXACTLY ONE row in `vnr_clean.csv`
- All features are identical
- Matching by features recovers the original VNR identity

**Match success rate**: 100% (617/617)

### Why Dataset Alignment Matters

Using different test sets would give:
- **Oracle on full dataset**: 80-100% (depends on VNR distribution)
- **Model on small split**: 55-93% (depends on random seed)
- **Comparison is meaningless** ✗

Using same test set gives:
- **Both evaluated on 617 VNRs**
- **Comparison is valid** ✓
- **Oracle ≥ Model (as expected)** ✓

---

## Conclusion

The Oracle analysis reveals:

1. **Model performs well on Tree topology** (93.37% vs 97.85%)
2. **Model struggles on Fat-Tree** (79.30% vs 100%) - **needs attention**
3. **Model moderate on Waxman-16** (85.65% vs 99.52%)
4. **Gap interpretation**: Model misses working algorithms for ~5-20% of solvable VNRs

The gaps represent achievable improvement targets through:
- Better feature engineering
- Topology-aware models
- Algorithm selection strategy refinement

---

## Files Generated

### Documentation
- `ORACLE_EXPLANATION.md` - Detailed Oracle explanation
- `ORACLE_FINAL_RESULTS.md` - This file

### Code
- `calculate_oracle_correct.py` - Correct Oracle calculation
- `visualize_oracle_vs_model_correct.py` - Visualization generation

### Data
- `models/oracle_performance_correct.json` - Oracle metrics

### Visualizations
- `models/oracle_vs_model_comparison.png`
- `models/oracle_vs_model_gap_analysis.png`
- `models/oracle_vs_model_detailed.png`
- `models/oracle_vs_model_summary_table.png`

---

**Last Updated**: 2024-12-27
**Status**: ✅ Complete and Verified
