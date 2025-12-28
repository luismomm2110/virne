# Decision Trees Pipeline: Data Flow Diagram

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Extract VNR Data                                             │
│ File: 1_extract_vnr_data.py                                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │ Input: apresentacao/simulacoes/*/records│
        │        temp-*.csv files                 │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────────────────────────────────┐
        │ Process each VNR arrival event:                 │
        │ - Algorithm used (ga_meta, mip, etc)           │
        │ - VNR characteristics (nodes, edges, demand)   │
        │ - Physical network state (utilization)         │
        │ - Outcome (success, cost, revenue)             │
        └─────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │ Output: datasets/vnr_raw_data.csv       │
        │ ~14,000 rows (VNRs × algorithms)        │
        │ Columns:                                │
        │ - algorithm, topology, seed             │
        │ - v_net_num_nodes, v_net_num_edges     │
        │ - v_net_lifetime, v_net_demand_*       │
        │ - p_net_available_resource             │
        │ - p_net_node_util, p_net_link_util     │
        │ - success, v_net_r2c_ratio             │
        │ - v_net_revenue, v_net_cost            │
        └─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Prepare Dataset & Create Labels (MODIFIED)                   │
│ File: 2_prepare_dataset.py                                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │ a) Add Real Clock Times                 │
        │    From summary.csv files               │
        │    clock_time_per_vnr =                │
        │      clock_running_time / success_count │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────────────────────────┐
        │ b) Create Features                      │
        │    - Normalize physical network state   │
        │    - Calculate problem complexity       │
        │    - Add engineered features (8 new)    │
        │    Result: 27 total features            │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────────────────────────┐
        │ c) CREATE 4 OBJECTIVE LABELS (NEW!) ⭐  │
        │                                         │
        │ For each unique VNR:                    │
        │   Group by (topology, seed, v_net_id)   │
        │   Test all 8 algorithms on it           │
        │                                         │
        │ best_for_rac:                          │
        │   Which algo has success=True?          │
        │                                         │
        │ best_for_lrc:                          │
        │   Which algo has max v_net_r2c_ratio?   │
        │                                         │
        │ best_for_lar:                          │
        │   Which algo has max v_net_revenue?     │
        │                                         │
        │ best_for_ast:                          │
        │   Which algo has min clock_time?        │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────────────────────────┐
        │ d) Remove Data Leakage Columns          │
        │    Delete: algorithm, success           │
        │    Delete: v_net_r2c_ratio              │
        │    Delete: v_net_revenue, v_net_cost    │
        │    Delete: clock_time_per_vnr           │
        │    Keep: all 27 features + 4 labels     │
        │                                         │
        │    Why? Can't know these before         │
        │    running the algorithm!               │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────────────────────────┐
        │ e) Create One Row Per VNR               │
        │    (not per algorithm run)              │
        │    Keep labels: best_for_rac, etc       │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────────────────────────┐
        │ f) Split Data                           │
        │    Train: 70% (stratified by label)     │
        │    Val:   15% (stratified by label)     │
        │    Test:  15% (stratified by label)     │
        └─────────────────────────────────────────┘
                              │
                              ↓
        ┌────────────────────────────────────────────┐
        │ Output:                                    │
        │ - datasets/vnr_features.csv (full data)    │
        │ - datasets/train.csv (~70% rows)          │
        │ - datasets/val.csv (~15% rows)            │
        │ - datasets/test.csv (~15% rows)           │
        │                                            │
        │ Each has columns:                          │
        │ [27 features] + [4 labels]                │
        │                                            │
        │ Labels are PRESERVED for training!        │
        └────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Train Decision Trees (NEW)                                   │
│ File: 3_train_decision_trees.py                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────────────────────────┐
        │ For each objective (RAC, LRC, LAR, AST) │
        │   Loop:                                  │
        │                                         │
        │   1. Filter data:                       │
        │      df_rac = data[best_for_rac != NaN]│
        │                                         │
        │   2. Prepare X, y:                      │
        │      X = [27 features]                  │
        │      y = best_for_rac (algorithm name)  │
        │                                         │
        │   3. Encode y:                          │
        │      0=d_round, 1=ga_meta, 2=mip, etc   │
        │      (using LabelEncoder)               │
        │                                         │
        │   4. Train tree:                        │
        │      DecisionTreeClassifier(             │
        │        max_depth=5,                      │
        │        min_samples_leaf=10,              │
        │        balanced weights                  │
        │      )                                   │
        │      tree.fit(X_train, y_train)         │
        │                                         │
        │   5. Evaluate:                          │
        │      y_pred = tree.predict(X_val)       │
        │      accuracy, f1, confusion_matrix     │
        │                                         │
        │   6. Visualize:                         │
        │      Save tree_rac.png, etc             │
        │      Save confusion_rac.png, etc        │
        │                                         │
        └─────────────────────────────────────────┘
                              │
                              ↓
        ┌────────────────────────────────────────────┐
        │ Output:                                    │
        │ - models/decision_trees.pkl               │
        │   Contains: {                             │
        │     'rac': DecisionTreeClassifier(...),   │
        │     'lrc': DecisionTreeClassifier(...),   │
        │     'lar': DecisionTreeClassifier(...),   │
        │     'ast': DecisionTreeClassifier(...)    │
        │   }                                        │
        │                                            │
        │ - models/algorithm_label_encoder.pkl      │
        │   Maps: 0→d_round, 1→ga_meta, etc        │
        │                                            │
        │ - models/tree_results.json                │
        │   Performance metrics for each tree       │
        │                                            │
        │ - models/tree_rac.png                     │
        │   models/tree_lrc.png                     │
        │   models/tree_lar.png                     │
        │   models/tree_ast.png                     │
        │   (Visualizations of decision paths)      │
        │                                            │
        │ - models/confusion_rac.png, etc          │
        │   (Confusion matrices)                    │
        └────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: Runtime Use (Not yet automated)                             │
│ Deploy in simulator or external system                              │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────────────────────────┐
        │ When new VNR arrives:                   │
        │                                         │
        │ 1. Extract 27 features from network     │
        │    state and VNR characteristics        │
        │                                         │
        │ 2. Choose objective at runtime:         │
        │    objective = 'rac'  # or lrc, lar, ast
        │                                         │
        │ 3. Use appropriate tree:                │
        │    tree = models[objective]             │
        │    prediction = tree.predict([features])│
        │    algo_idx = prediction[0]             │
        │    algorithm = encoder.classes_[idx]    │
        │                                         │
        │ 4. Run algorithm:                       │
        │    result = VNE_Simulator.embed(        │
        │      vnr, algorithm                     │
        │    )                                    │
        │                                         │
        │ 5. Record outcome:                      │
        │    (success, cost, revenue, time)       │
        │                                         │
        └─────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │ Output:                                 │
        │ VNE solution using predicted algorithm  │
        │ (instead of always using same algo)     │
        └─────────────────────────────────────────┘
```

## Key Data Transformation Summary

| Stage | Format | Size | Purpose |
|-------|--------|------|---------|
| Raw simulation output | temp-*.csv | 631 files | Original VNE results |
| Extracted data | vnr_raw_data.csv | 14,000 rows | All VNR executions |
| With features | vnr_features.csv | 14,000 rows | 27 features + 4 labels |
| One row/VNR | vnr_clean.csv | ~1,750 rows | One sample per unique VNR |
| Train split | train.csv | ~1,225 rows | 70% for training |
| Val split | val.csv | ~263 rows | 15% for validation |
| Test split | test.csv | ~263 rows | 15% for final testing |

## Label Statistics

For each objective, count how many VNRs each algorithm is "best":

```
best_for_rac (Acceptance Rate):
  mip:        234 VNRs (13.4%)
  ga_meta:    198 VNRs (11.3%)
  rw_rank_bfs: 156 VNRs (8.9%)
  ...

best_for_lrc (Revenue-to-Cost):
  ga_meta:    287 VNRs (16.4%)
  mip:        245 VNRs (14.0%)
  ...

best_for_lar (Average Revenue):
  ga_meta:    312 VNRs (17.8%)
  mip:        268 VNRs (15.3%)
  ...

best_for_ast (Solving Time):
  rw_rank_bfs: 421 VNRs (24.1%)
  d_round:     289 VNRs (16.5%)
  ...
```

Class imbalance is why we use **balanced class weights** in Decision Tree!

## Feature Space

Each sample (VNR at decision time) has 27 features:

```python
features = [
    # VNR Characteristics (9 features)
    v_net_num_nodes,              # 2-10
    v_net_num_edges,              # 1-45
    v_net_size_ratio,             # 0.0625-0.3125 (normalized)
    v_net_demand_per_node,        # 0-20
    v_net_demand_per_link,        # 0-50
    v_net_connectivity,           # 0-1 (density)
    v_net_total_demand,           # 0-70
    v_net_node_to_link_demand_ratio,  # 0-inf
    v_net_lifetime,               # exponential ~500 avg

    # Physical Network State (7 features)
    p_net_available_resource,     # varies by topology
    p_net_node_util,              # 0-1
    p_net_link_util,              # 0-1
    p_net_overall_util,           # 0-1
    inservice_count,              # 0-max_vnrs
    system_load,                  # 0-1 normalized
    num_running_p_net_nodes,      # varies

    # Engineered Features (8 features)
    network_stress_index,         # 0-1 (avg of node+link util)
    problem_complexity,           # connectivity × demand
    resource_bottleneck_ratio,    # node_demand / link_demand
    vnr_size_category,            # 0/1/2 (small/med/large)
    cpu_intensive_flag,           # 0/1
    bandwidth_intensive_flag,     # 0/1
    utilization_pressure,         # node_util × link_util
    resource_efficiency,          # available / demanded
]
```

## Decision Tree Decision Making

Example: What does tree_rac do?

```
Tree tries to answer: "Given network state, which algorithm will accept most VNRs?"

         [network_stress_index <= 0.5]
          /                           \
         /                             \
    [v_net_connectivity <= 0.3]    [p_net_node_util <= 0.7]
      /              \               /            \
  rw_rank_bfs    mip or ga       mip or rw     [v_net_num_nodes <= 5]
  (simple networks)  (complex)  (moderate)        /            \
                               mip           ga_meta       mip
                             (stressed)    (resource      (few
                                           rich)          nodes)
```

**Interpretation:**
- Stressed network (high congestion) → Use MIP (exact solver)
- Simple VNRs → Use RW_RANK_BFS (fast heuristic)
- Complex VNRs with available resources → Use GA_META (good balance)

This is automatically learned from data!
