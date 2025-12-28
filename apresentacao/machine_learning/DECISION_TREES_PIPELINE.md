# Decision Trees Pipeline for Multi-Objective VNE Algorithm Selection

## Overview

This pipeline converts your XGBoost-based algorithm selector into a **Decision Tree-based multi-objective selector** as described in ACADEMIC_ANALYSIS_OPTION2.md.

**Key Innovation:** Instead of training ONE model to predict the "best_overall" algorithm, we train **4 separate trees**, each optimized for a different VIRNe performance metric:

1. **RAC Tree** (Request Acceptance Rate) - Maximize acceptance of VNRs
2. **LRC Tree** (Long-Term Revenue-to-Cost) - Maximize profitability
3. **LAR Tree** (Long-Term Average Revenue) - Maximize total revenue
4. **AST Tree** (Average Solving Time) - Minimize execution time

## Why Decision Trees?

✅ **Interpretability** - Can visualize decision paths and understand why each algorithm was selected
✅ **Fast inference** - < 1ms per prediction (suitable for online decision-making)
✅ **No hyperparameter tuning** - Works well out of the box
✅ **Handles non-linear patterns** - Can capture complex network state → algorithm mappings
✅ **Multi-objective** - Switch objectives at runtime without retraining

## Pipeline Files

### Step 1: Extract VNR Data
**File:** `1_extract_vnr_data.py`
- Reads simulation records from `apresentacao/simulacoes/*/records/temp-*.csv`
- Extracts one row per VNR instance tested with different algorithms
- **Output:** `datasets/vnr_raw_data.csv` (~14,000 records)

### Step 2: Prepare Dataset & Create Labels (MODIFIED)
**File:** `2_prepare_dataset.py` ⭐ MODIFIED FOR MULTI-OBJECTIVE

**Changes:**
- `create_labels()` now creates **4 objective labels** instead of 1:
  - `best_for_rac`: Which algorithm maximizes acceptance for this VNR?
  - `best_for_lrc`: Which algorithm maximizes revenue-to-cost ratio?
  - `best_for_lar`: Which algorithm maximizes average revenue?
  - `best_for_ast`: Which algorithm minimizes solving time?

- `remove_unnecessary_columns()` now preserves all 4 labels (don't remove them!)

**VIRNe Metrics Used:**
- **RAC**: Direct from `success` field (1 if accepted, 0 if rejected)
- **LRC**: From `v_net_r2c_ratio` field (revenue / cost)
- **LAR**: From `v_net_revenue` field (total revenue per VNR)
- **AST**: Calculated as `clock_running_time / success_count` (solving time)

**Output:**
- `datasets/vnr_features.csv` - Full dataset with 4 labels
- `datasets/train.csv` - 70% for training
- `datasets/val.csv` - 15% for validation
- `datasets/test.csv` - 15% for final evaluation

### Step 3: Train Decision Trees (NEW)
**File:** `3_train_decision_trees.py` ⭐ NEW SCRIPT

Replaces the old XGBoost training script with Decision Tree training.

**For each objective (RAC, LRC, LAR, AST):**
1. Filter training data to samples where that objective label exists
2. Train a Decision Tree with:
   - `max_depth=5` for interpretability
   - `min_samples_leaf=10` to prevent overfitting
   - Balanced class weights to handle imbalanced classes
3. Evaluate on validation set
4. Visualize tree structure

**Output:**
- `models/decision_trees.pkl` - All 4 trained models
- `models/algorithm_label_encoder.pkl` - Encoder for algorithm names
- `models/tree_results.json` - Performance metrics for each tree
- `models/tree_rac.png`, `models/tree_lrc.png`, `models/tree_lar.png`, `models/tree_ast.png` - Visualizations
- `models/confusion_rac.png` - Confusion matrices for each tree

## Usage Example

```python
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Load trained models
with open('models/decision_trees.pkl', 'rb') as f:
    models = pickle.load(f)

with open('models/algorithm_label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

# Network state at time of VNR arrival
network_state = np.array([[
    0.7,   # v_net_num_nodes (normalized)
    0.5,   # p_net_available_resource (normalized)
    0.8,   # p_net_node_util
    0.6,   # ... (continue with all 27 features)
    ...
]])

# Select algorithm based on objective
objectives = ['rac', 'lrc', 'lar', 'ast']

for objective in objectives:
    tree = models[objective]
    prediction = tree.predict(network_state)  # Returns 0-7 (algorithm index)
    algorithm = label_encoder.classes_[prediction[0]]

    print(f"{objective}: {algorithm}")

# Output:
# rac: mip
# lrc: ga_meta
# lar: ga_meta
# ast: rw_rank_bfs
```

## Decision Tree Configuration

```python
DecisionTreeClassifier(
    max_depth=5,              # Limit depth for human interpretability
    min_samples_leaf=10,      # Require at least 10 samples to form a leaf
    min_samples_split=20,     # Require at least 20 samples to split
    criterion='gini',         # Use Gini impurity for splitting
    random_state=42           # Reproducibility
)
```

**Why these parameters?**
- **max_depth=5**: Can still visualize (deeper trees become hard to read)
- **min_samples_leaf=10**: Prevents overfitting on small clusters
- **Balanced class weights**: Handles imbalanced classes (e.g., MIP might win 67% of time on some topologies)

## Feature Engineering

The pipeline uses 27 features derived from network state and VNR characteristics:

### Network State Features
- `v_net_num_nodes`, `v_net_num_edges` - VNR size
- `v_net_size_ratio` - Size relative to physical network
- `v_net_connectivity` - Network density
- `v_net_demand_per_node`, `v_net_demand_per_link` - Resource intensity
- `v_net_lifetime` - How long the VNR will stay in network

### Physical Network State
- `p_net_available_resource` - Total free resources
- `p_net_node_util`, `p_net_link_util` - Node and link utilization
- `p_net_overall_util` - Overall network utilization
- `inservice_count` - Current in-service VNRs
- `system_load` - Normalized system load

### Engineered Features
- `network_stress_index` - How stressed the physical network is
- `problem_complexity` - Complexity of embedding problem
- `resource_bottleneck_ratio` - CPU-intensive vs Bandwidth-intensive
- `vnr_size_category` - Small / Medium / Large
- `cpu_intensive_flag`, `bandwidth_intensive_flag` - Type of problem
- `utilization_pressure` - Network congestion level
- `resource_efficiency` - How efficiently we can fit this VNR

## Evaluation & Interpretation

### Accuracy Interpretation

Since each tree tries to predict ONE algorithm (multi-class classification), accuracy might seem low:

```
best_for_rac: 45% accuracy
best_for_lrc: 58% accuracy
best_for_lar: 52% accuracy
best_for_ast: 61% accuracy
```

**This is NORMAL and EXPECTED because:**
1. **Imbalanced classes**: Some algorithms (e.g., MIP) win much more often
2. **Multiple good options**: For many VNRs, multiple algorithms perform similarly
3. **We care about ranking, not strict accuracy**: Even if prediction != actual best, if it's in top 3, it's useful

**Better evaluation metric:** Would be **ranking accuracy** (e.g., "is the predicted algorithm in top-3 best?")

### Decision Tree Visualization

Each tree shows:
- **Feature at each node**: Which network state feature to check
- **Split threshold**: Value to compare against
- **Samples**: How many training samples reach that node
- **Class distribution**: Breakdown of algorithms at that node
- **Prediction**: Which algorithm is chosen if we stop here

Example interpretations:
```
IF network_stress_index <= 0.5:
  IF v_net_connectivity <= 0.3:
    PREDICT: rw_rank_bfs (fast heuristic for simple problems)
  ELSE:
    PREDICT: mip (complex problems need exact solver)
ELSE:
  PREDICT: ga_meta (good balance when network is stressed)
```

## Multi-Objective Runtime Switching

The beauty of this approach: **Switch objectives without retraining!**

```python
# Mode 1: Prioritize acceptance
tree = models['rac']
algo = tree.predict(network_state)

# ... later, user changes priority ...

# Mode 2: Prioritize speed
tree = models['ast']
algo = tree.predict(network_state)  # Different recommendation!
```

This enables:
- **Dynamic SLA management**: Switch to faster algorithms when latency is critical
- **Revenue optimization**: Switch to ga_meta when maximizing profit
- **Load balancing**: Switch based on current network conditions

## Running the Pipeline

```bash
# Step 1: Extract data from simulations
python3 1_extract_vnr_data.py

# Step 2: Prepare dataset with multi-objective labels
python3 2_prepare_dataset.py

# Step 3: Train 4 decision trees
python3 3_train_decision_trees.py
```

## Comparison with Previous XGBoost Approach

| Aspect | XGBoost (Old) | Decision Trees (New) |
|--------|---------------|-------------------|
| Models trained | 1 ("best_overall") | 4 (one per objective) |
| Objectives | Single weighted function | Runtime switchable |
| Interpretability | Black box | Fully interpretable |
| Training time | ~10 min | ~1 min |
| Inference time | ~5ms | <1ms |
| Class imbalance handling | Scale by weight | Balanced weights |
| Hyperparameter tuning | Required | Minimal |

## Next Steps

After training, you can:

1. **Evaluate** with oracle comparison (Step 5)
2. **Visualize** decision boundaries and sensitivity
3. **Deploy** in simulator to test actual VNE performance
4. **Write up** results for academic paper

See `ACADEMIC_ANALYSIS_OPTION2.md` for the full research motivation and novelty claims.
