# Plan: Extract Real AST (Average Solving Time) from Simulation Records

**Status:** Ready to implement
**Estimated effort:** 1-2 hours
**Goal:** Fix AST labels by using real per-VNR solving times instead of aggregate times

---

## Problem Statement

Current issue:
- AST labels are based on **aggregate solving time** (clock_running_time / success_count per algorithm)
- This means all VNRs in the same seed see the SAME solving time for each algorithm
- Result: Models learn seed-based patterns, not VNR-based patterns
- Performance: Models achieve 99% classification accuracy but give NO performance improvement

Solution:
- Extract **individual solving times** for EACH VNR embedding
- Create labels based on which algorithm was actually faster FOR THAT VNR
- Retrain with correct ground truth
- Expected: Model can learn "small VNRs → use X", "large VNRs → use Y", etc.

---

## Data Structure

### Simulation Records Location
```
simulacoes/
├── pl_rank/
│   ├── Luisas-MacBook-Air.local-20251201T060105-3316/
│   │   ├── config.yaml
│   │   ├── summary.csv
│   │   └── records/
│   │       └── pl_rank-Luisas-MacBook-Air.local-20251201T060105-3316-20251201T060105.csv
│   └── ... (more runs)
├── rw_rank_bfs/
├── ga_meta/
└── ... (other algorithms)
```

### Record File Structure
Each `records/*.csv` file contains one row per **event** (not per VNR):
```
Columns: v_net_id, v_net_num_nodes, v_net_num_edges, event_type, event_time,
         seed, result, v_net_node_demand, v_net_link_demand, ...
```

Key columns:
- `v_net_id`: Virtual network ID (0, 1, 2, ...)
- `event_type`: 1=arrival/embedding, 0=departure
- `event_time`: Simulation time when event occurred
- `result`: "Success" or "False"
- `seed`: Random seed used in this simulation run

**Important:** Multiple events per VNR (arrival + departure)
- Event arrival: When VNR arrives and is embedded
- Event departure: When VNR leaves the network

---

## Step-by-Step Implementation Plan

### Phase 1: Extract Raw Data from Simulations

**Goal:** Collect all solving times for each (algorithm, seed, topology, v_net_id)

**Steps:**

1. **Find all record files**
   ```python
   from pathlib import Path
   import glob

   ALGO_DIRS = ["pl_rank", "rw_rank_bfs", "ga_meta", "mcts", "mip", "sa_meta", "d_round", "pso_meta"]
   SIM_PATH = Path("simulacoes")

   for algo in ALGO_DIRS:
       records = glob.glob(str(SIM_PATH / algo / "**/records/*.csv"), recursive=True)
       # Process each record file
   ```

2. **For each record file, extract solving time**
   ```python
   def extract_solving_times(record_file):
       """
       Read a record file and extract solving time for each VNR

       Input: record file for one algorithm/run combination
       Output: dict {v_net_id: solving_time}

       Approach:
       - Read CSV file
       - Filter for successful embeddings (result == "Success")
       - Group by v_net_id
       - For each VNR:
         - Find event_time when it arrived (first occurrence)
         - This is the solving time for this VNR
       """
       import pandas as pd

       df = pd.read_csv(record_file)
       solving_times = {}

       # Group by VNR
       for vnr_id, group in df.groupby('v_net_id'):
           # Get first event (arrival/embedding)
           first_event = group.iloc[0]
           if first_event['result'] == 'Success':
               solving_times[vnr_id] = first_event['event_time']

       return solving_times
   ```

3. **Aggregate results by (algorithm, seed, topology)**
   ```python
   # Structure: {algorithm: {seed: {topology: {v_net_id: solving_time}}}}
   all_times = {algo: {} for algo in ALGO_DIRS}

   for algo in ALGO_DIRS:
       records = glob.glob(...)
       for record_file in records:
           # Extract seed and topology from config.yaml in parent directory
           times = extract_solving_times(record_file)
           all_times[algo][seed][topology] = times
   ```

### Phase 2: Create Correct AST Labels

**Goal:** For each VNR, determine which algorithm was actually fastest

**Steps:**

1. **Merge with existing datasets**
   ```python
   # Load existing train/val/test datasets
   train_df = pd.read_csv("datasets/train.csv")  # Has: topology, seed, and other features

   # Add real solving times from extracted data
   for idx, row in train_df.iterrows():
       algo = row['algorithm']
       seed = row['seed']
       topology = row['topology']
       v_net_id = row.get('v_net_id', None)  # Need to check if this column exists

       if v_net_id is not None:
           real_time = all_times[algo][seed][topology][v_net_id]
           train_df.loc[idx, 'solving_time_real'] = real_time
   ```

2. **Create new labels**
   ```python
   # Group by (topology, seed, v_net_id)
   # Find which algorithm had minimum solving_time_real

   for group_id, group in train_df.groupby(['topology', 'seed', 'v_net_id']):
       # Find algorithm with minimum solving_time_real
       best_algo = group.loc[group['solving_time_real'].idxmin(), 'algorithm']
       train_df.loc[group.index, 'best_for_ast_corrected'] = best_algo
   ```

3. **Validate new labels**
   ```python
   # Check that we have more variation now
   print("Old AST labels (aggregate):")
   print(train_df['best_for_ast'].value_counts())

   print("\nNew AST labels (real per-VNR):")
   print(train_df['best_for_ast_corrected'].value_counts())
   # Should show more balanced distribution
   ```

### Phase 3: Update Datasets

**Goal:** Add corrected AST labels to all datasets

**Steps:**

1. **Apply to all datasets**
   ```python
   for dataset_name in ['train', 'val', 'test']:
       df = pd.read_csv(f"datasets/{dataset_name}.csv")
       # Apply the same logic to extract and add best_for_ast_corrected
       df.to_csv(f"datasets/{dataset_name}_ast_corrected.csv", index=False)
   ```

2. **Create enhanced versions**
   ```python
   # Create train_enhanced_ast_corrected.csv with all features + new labels
   # Do this for all three datasets
   ```

### Phase 4: Retrain Models

**Goal:** Train AST models with correct labels

**Steps:**

1. **Use corrected labels for training**
   ```python
   # Modify training script to use 'best_for_ast_corrected' instead of 'best_for_ast'

   from sklearn.tree import DecisionTreeClassifier
   import xgboost as xgb
   from sklearn.ensemble import RandomForestClassifier

   X_train = train_df[FEATURE_COLUMNS].values
   y_train = train_df['best_for_ast_corrected'].values  # Use corrected labels!

   # Train with Decision Tree, XGBoost, and Random Forest
   models = {
       'dt': DecisionTreeClassifier(max_depth=12, ...),
       'xgb': xgb.XGBClassifier(...),
       'rf': RandomForestClassifier(...)
   }

   for name, model in models.items():
       model.fit(X_train, y_train_encoded)
       # Save model
   ```

2. **Compare performance**
   ```python
   # For each model, check:
   # - Validation accuracy (should be similar or better)
   # - Real performance on test set (should be BETTER now!)
   ```

### Phase 5: Evaluate Results

**Goal:** Check if corrected AST improves real performance

**Steps:**

1. **Test on real metrics**
   ```python
   # Use step 13_calculate_tree_real_performance.py approach

   test_df = pd.read_csv("datasets/test_enhanced_ast_corrected.csv")
   algo_metrics = pd.read_csv("models/algorithm_comparison_metrics.csv")

   for model_name in ['dt', 'xgb', 'rf']:
       model = load_model(f"models_option2/best_for_speed_{model_name}_ast_corrected.pkl")
       encoder = load_encoder(f"models_option2/best_for_speed_encoder_{model_name}_ast_corrected.pkl")

       # Get predictions
       predictions = model.predict(X_test)
       predicted_algos = encoder.inverse_transform(predictions)

       # Calculate real performance
       model_avg = calculate_real_performance(predicted_algos, algo_metrics)
       baseline_avg = calculate_baseline_performance(algo_metrics)

       improvement = model_avg - baseline_avg
       print(f"{model_name}: {improvement:+.4f}")
   ```

2. **Compare with old results**
   ```
   Old AST Results (incorrect labels):
     Decision Tree (32 features): -0.0426 ❌
     XGBoost (61 features):      -0.0425 ❌
     Random Forest (61 features): -0.0425 ❌

   New AST Results (correct labels):
     Decision Tree:  ??? (should be better!)
     XGBoost:        ??? (should be better!)
     Random Forest:  ??? (should be better!)
   ```

---

## Expected Outcomes

### Success Criteria:
- ✅ Real per-VNR solving times extracted
- ✅ New labels show more variation than old labels
- ✅ Model validation accuracy > 60% (vs 98% before, which was overfitting to wrong pattern)
- ✅ Real performance improvement: model_avg > baseline_avg

### Possible Results:

**Scenario A: Success! 🎉**
```
Model learns real patterns:
  "Small VNRs (few nodes) → use algorithm X"
  "Large VNRs (many nodes) → use algorithm Y"
Result: Real performance improves!
```

**Scenario B: Still doesn't work ⚠️**
```
Even with correct labels, features don't correlate with algorithm speed.
This would mean: Algorithm speed is fundamentally unpredictable from VNR features.
Conclusion: Feature engineering approach won't help for AST.
```

---

## Files to Create/Modify

```
datasets/
├── train_ast_corrected.csv          (new: with best_for_ast_corrected)
├── val_ast_corrected.csv            (new)
├── test_ast_corrected.csv           (new)
├── train_enhanced_ast_corrected.csv (new: with all features + new labels)
├── val_enhanced_ast_corrected.csv   (new)
└── test_enhanced_ast_corrected.csv  (new)

models_option2/
├── best_for_speed_tree_ast_corrected.pkl
├── best_for_speed_encoder_ast_corrected.pkl
├── best_for_speed_xgb_ast_corrected.pkl
├── best_for_speed_encoder_xgb_ast_corrected.pkl
├── best_for_speed_rf_ast_corrected.pkl
└── best_for_speed_encoder_rf_ast_corrected.pkl

models/
└── tree_real_performance_ast_corrected.csv (results)
```

---

## Validation Checklist

Before considering AST solved:

- [ ] All record files found and parsed successfully
- [ ] Solving times extracted for all (algo, seed, topology, vnr_id)
- [ ] New labels created and have variation (not all one class)
- [ ] Labels match expected distribution (not 60% one algo)
- [ ] Models retrained with new labels
- [ ] Validation accuracy > 50% (more realistic)
- [ ] Real performance tested
- [ ] Improvement calculation shows model > baseline OR honest conclusion if still doesn't work

---

## Code Template to Start

```python
"""
Step 0: Extract AST from Simulation Records
This script extracts real solving times from simulation records
and creates corrected AST labels
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob
from tqdm import tqdm

ALGO_DIRS = ["pl_rank", "rw_rank_bfs", "ga_meta", "mcts", "mip", "sa_meta", "d_round", "pso_meta"]
SIM_PATH = Path("../simulacoes")
DATASETS_PATH = Path("datasets")

def extract_solving_times(record_file):
    """Extract solving time for each VNR from a record file"""
    df = pd.read_csv(record_file)
    solving_times = {}

    for vnr_id, group in df.groupby('v_net_id'):
        # Get first successful event (arrival/embedding)
        successful = group[group['result'] == 'Success']
        if len(successful) > 0:
            first_event = successful.iloc[0]
            solving_times[vnr_id] = first_event['event_time']

    return solving_times

def main():
    print("="*80)
    print("EXTRACTING REAL AST FROM SIMULATION RECORDS")
    print("="*80)

    # Step 1: Find all record files
    print("\nPhase 1: Finding record files...")
    record_files = {}
    for algo in ALGO_DIRS:
        record_files[algo] = glob.glob(str(SIM_PATH / algo / "**/records/*.csv"), recursive=True)
        print(f"  {algo}: {len(record_files[algo])} files")

    # Step 2: Extract solving times
    print("\nPhase 2: Extracting solving times...")
    all_times = {}
    for algo in ALGO_DIRS:
        all_times[algo] = {}
        for record_file in tqdm(record_files[algo], desc=algo):
            times = extract_solving_times(record_file)
            # TODO: Extract seed and topology from file path
            # all_times[algo][(seed, topology)] = times

    # Step 3: Add to datasets and create labels
    print("\nPhase 3: Creating corrected labels...")
    # TODO: Load train/val/test, add solving times, create best_for_ast_corrected

    # Step 4: Retrain models
    print("\nPhase 4: Retraining models...")
    # TODO: Use corrected labels

    # Step 5: Evaluate
    print("\nPhase 5: Evaluating...")
    # TODO: Run 13_calculate_tree_real_performance.py with corrected models

    print("\n" + "="*80)
    print("COMPLETE!")
    print("="*80)

if __name__ == '__main__':
    main()
```

---

## Next Steps After Completion

1. If AST works: Update article to include AST results ✅
2. If AST still doesn't work: Document why (features insufficient) and report only RAC/LRC
3. Either way: Move forward with finalizing the article

---

## Questions to Answer Before Starting

- [ ] Are v_net_id values consistent across datasets and simulations?
- [ ] Does `event_time` directly represent solving time, or needs calculation?
- [ ] How many VNRs are shared across different algorithms/seeds?
- [ ] Are there edge cases (failed embeddings, etc.) to handle?

**Recommended:** Inspect a few record files manually first to understand the data structure fully.

---

**Created:** 2025-12-30
**Status:** Ready to implement