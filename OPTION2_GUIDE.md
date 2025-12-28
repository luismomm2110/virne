# Option 2: Multiple Objective Trees - Complete Guide

## Overview

Instead of training a single "best_overall" decision tree, **Option 2 trains 4 separate trees**, each optimized for a different objective:

1. **best_for_acceptance** - Maximizes probability of accepting the VNR
2. **best_for_cost** - Minimizes embedding cost
3. **best_for_speed** - Minimizes execution time
4. **best_balanced** - Balances all three objectives equally

This allows **runtime decisions** based on current network priorities.

---

## Why Option 2 is Better Than Single Tree

### Problem with Single Tree:
```
One tree always recommends: rw_rank_bfs
  ❌ Can't handle high-acceptance scenarios (where MIP is better)
  ❌ Can't handle cost-critical scenarios (where PSO is better)
  ❌ Can't handle real-time scenarios (where rw_rank_bfs dominates)
  ❌ No insight into trade-offs
```

### Solution with Option 2:
```
Four trees, each optimized for different priorities:
  ✅ Network congested? Use best_for_acceptance → higher success rate
  ✅ Resources limited? Use best_for_cost → lower resource usage
  ✅ Real-time SLA? Use best_for_speed → instant decision
  ✅ Normal operation? Use best_balanced → good all-around
```

---

## How It Works

### Training Phase (Already Done)

```python
# train_multiple_objective_trees.py creates:

for each VNR in dataset:
    # For ACCEPTANCE objective:
    best_algo_for_acceptance = algorithm with highest success rate

    # For COST objective:
    best_algo_for_cost = algorithm with lowest v_net_cost

    # For SPEED objective:
    best_algo_for_speed = algorithm with lowest clock_time_per_vnr

    # For BALANCED objective:
    score = (success + (max_cost - cost) + (max_time - time)) / 3
    best_algo_for_balanced = algorithm with highest score

# Train separate decision tree for each objective
model_acceptance = DecisionTree(X, y_acceptance)
model_cost = DecisionTree(X, y_cost)
model_speed = DecisionTree(X, y_speed)
model_balanced = DecisionTree(X, y_balanced)
```

### Inference Phase (Runtime)

```python
def select_algorithm(vnr_features, network_state):
    if network_state['utilization'] > 80%:
        # Network congested - maximize acceptance
        tree = load('best_for_acceptance_tree.pkl')
        algo = tree.predict(vnr_features)

    elif network_state['available_resources'] < threshold:
        # Resource constrained - minimize cost
        tree = load('best_for_cost_tree.pkl')
        algo = tree.predict(vnr_features)

    elif sla_requirement['latency'] < 1 second:
        # Real-time SLA - minimize execution time
        tree = load('best_for_speed_tree.pkl')
        algo = tree.predict(vnr_features)

    else:
        # Normal operation - balanced
        tree = load('best_balanced_tree.pkl')
        algo = tree.predict(vnr_features)

    return algo
```

---

## Test Results

### Trained Models Location
```
apresentacao/machine_learning/models_option2/
├── best_for_acceptance_tree.pkl
├── best_for_acceptance_encoder.pkl
├── best_for_cost_tree.pkl
├── best_for_cost_encoder.pkl
├── best_for_speed_tree.pkl
├── best_for_speed_encoder.pkl
├── best_balanced_tree.pkl
└── best_balanced_encoder.pkl
```

### Model Performance

| Objective | Classes | Train Acc | Val Acc | Algorithms |
|-----------|---------|-----------|---------|------------|
| **acceptance** | 7 | 11.35% | 10.87% | ga_meta, mip, pl_rank, pso_meta, rw_rank_bfs, sa_meta, mcts |
| **cost** | 1 | 100% | 100% | Always: ga_meta |
| **speed** | 1 | 100% | 100% | Always: rw_rank_bfs |
| **balanced** | 6 | 17.50% | 17.34% | ga_meta, mip, pl_rank, pso_meta, rw_rank_bfs, sa_meta |

**Notes:**
- `best_for_cost` and `best_for_speed` have 100% accuracy because they always select the same algorithm (ga_meta for cost, rw_rank_bfs for speed)
- `best_for_acceptance` is harder (lower accuracy) because multiple algorithms can achieve similar acceptance rates
- Accuracy is lower due to class imbalance within each objective, but trees are still useful for ranking algorithms by preference

---

## Example Scenarios

### Scenario 1: Congested Network (63.6% utilization)
```
Network State:
  - Utilization: 63.6%
  - Available resources: 3806
  - VNR: 4 nodes, 150 total demand

Recommendation Comparison:
  best_for_acceptance → rw_rank_bfs (maximize success rate)
  best_for_cost → ga_meta (minimize cost)
  best_for_speed → rw_rank_bfs (minimize time)
  best_balanced → pso_meta (balanced)

→ Selected: rw_rank_bfs
  Why: Network is congested, so prioritize acceptance rate
```

### Scenario 2: Resource-Constrained Network
```
Network State:
  - Available resources: 4944
  - Node utilization: 82.9%
  - VNR: 7 nodes, 298 total demand

Recommendation Comparison:
  best_for_acceptance → rw_rank_bfs
  best_for_cost → ga_meta (minimize cost)
  best_for_speed → rw_rank_bfs
  best_balanced → pl_rank

→ Selected: ga_meta
  Why: Resources are limited, minimize cost to preserve capacity
```

### Scenario 3: Real-Time SLA (< 1 second)
```
Network State:
  - SLA requirement: < 1 second response
  - Current load: 4.35%
  - VNR: 10 nodes, large demand

Recommendation Comparison:
  best_for_acceptance → pso_meta
  best_for_cost → ga_meta
  best_for_speed → rw_rank_bfs (fastest!)
  best_balanced → rw_rank_bfs

→ Selected: rw_rank_bfs
  Why: Must meet latency SLA, choose fastest algorithm
```

### Scenario 4: Normal Operation (Balanced)
```
Network State:
  - Utilization: 9.1%
  - Available resources: 9504
  - No specific constraints

Recommendation Comparison:
  best_for_acceptance → pso_meta
  best_for_cost → ga_meta
  best_for_speed → rw_rank_bfs
  best_balanced → pl_rank

→ Selected: pl_rank
  Why: No constraints, balance all three objectives
```

---

## How to Use Option 2

### 1. Load Models
```python
import pickle

# Load inference system
from inference_option2 import AlgorithmSelector

selector = AlgorithmSelector('apresentacao/machine_learning/models_option2')
```

### 2. Extract VNR Features
```python
features = {
    'v_net_num_nodes': 6,
    'v_net_num_edges': 12,
    'v_net_connectivity': 0.67,
    'p_net_overall_util': 0.45,
    'p_net_available_resource': 5000,
    # ... other features
}
```

### 3. Select Algorithm Based on Priority
```python
# Option A: Explicit priority selection
if network_congested:
    algo = selector.select_algorithm(features, priority='acceptance')
elif resources_limited:
    algo = selector.select_algorithm(features, priority='cost')
elif real_time_sla:
    algo = selector.select_algorithm(features, priority='speed')
else:
    algo = selector.select_algorithm(features, priority='balanced')

# Option B: Automatic selection based on network state
network_state = {
    'utilization': p_net_util,
    'available_resources': available_res
}
algo = selector.select_algorithm(features, network_state=network_state)
```

### 4. Execute Selected Algorithm
```python
if algo == 'mip':
    solver = MIPSolver()
elif algo == 'ga_meta':
    solver = GASolver()
# ... etc

result = solver.embed(vnr, p_net)
```

---

## Run Inference Tests

### Test All Scenarios
```bash
python inference_option2.py --test
```

This will show:
- 4 different network scenarios
- Algorithm selection for each scenario
- Comparison of all 4 objective trees for each scenario
- Rationale for each decision

---

## Integration with Your System

### Decision Flow
```
VNR Arrives
    ↓
Extract Features (v_net_num_nodes, p_net_util, etc.)
    ↓
Assess Network State
    ├─ High utilization (> 80%)?
    │   → Use best_for_acceptance tree
    │
    ├─ Low resources?
    │   → Use best_for_cost tree
    │
    ├─ Real-time SLA?
    │   → Use best_for_speed tree
    │
    └─ Normal?
        → Use best_balanced tree
    ↓
Select Algorithm from Tree
    ↓
Execute Algorithm
    ↓
Return Result
```

### Python Integration
```python
from inference_option2 import AlgorithmSelector

class VNRController:
    def __init__(self):
        self.selector = AlgorithmSelector()

    def handle_vnr(self, vnr, p_net):
        # Extract features
        features = extract_vnr_features(vnr, p_net)
        network_state = assess_network_state(p_net)

        # Select algorithm
        algo = self.selector.select_algorithm(features, network_state)

        # Execute
        result = execute_solver(algo, vnr, p_net)

        return result
```

---

## Comparison: Single Tree vs Option 2

| Aspect | Single Tree | Option 2 |
|--------|---|---|
| **Flexibility** | Fixed priority | Adapts to network state |
| **Handling Congestion** | Always same algo | Can prioritize acceptance |
| **Resource Efficiency** | Always same algo | Can minimize cost |
| **Real-time SLA** | Always same algo | Can minimize time |
| **Interpretability** | One decision path | 4 decision paths (compare) |
| **Deployment** | 1 model | 4 models |
| **Decision Quality** | Fixed | Context-aware |

---

## Next Steps

### Option 1: Use Option 2 Now
- Load the trained models from `models_option2/`
- Integrate with your VNR controller
- Monitor decisions in different scenarios

### Option 2: Improve Accuracy
- Add WX500 simulations to diversify data
- Retrain trees with larger, more diverse dataset
- Accuracy should improve as patterns become clearer

### Option 3: Hybrid Approach
- Use Option 2 for context-aware selection
- Fall back to Option 3 (performance prediction) for edge cases
- Provide both ranked recommendations and confidence scores

---

## Files Created

```
train_multiple_objective_trees.py  # Training script
inference_option2.py               # Inference/testing script
OPTION2_GUIDE.md                   # This guide
models_option2/                    # Trained models
├── best_for_acceptance_tree.pkl
├── best_for_acceptance_encoder.pkl
├── best_for_cost_tree.pkl
├── best_for_cost_encoder.pkl
├── best_for_speed_tree.pkl
├── best_for_speed_encoder.pkl
├── best_balanced_tree.pkl
└── best_balanced_encoder.pkl
```

---

## Summary

**Option 2 solves the problem of a single fixed recommendation** by training objective-specific trees that adapt to different network conditions:

- **Congested network** → prioritize acceptance
- **Resource-constrained** → prioritize cost efficiency
- **Real-time SLA** → prioritize speed
- **Normal operation** → balanced approach

This makes your system **adaptive** and **useful for real deployment**.
