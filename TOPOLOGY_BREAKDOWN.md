# Experiment Topology Breakdown

## Summary

**NO** - Not all experiments used both topologies. Here's the actual breakdown:

---

## Topology Usage by Scenario

### 1. **Normal Tree** - TREE ONLY ✓
- Topology: 32-node tree, CPU [50-100], BW [50-100]
- Algorithms tested: SA, GA, PL-Rank, RW-Rank-BFS, D-Round
- **NOT tested on fat-tree**

### 2. **Fat-Tree** - FAT-TREE ONLY ✓  
- Topology: 16-host fat-tree (k=4), CPU [50-100], BW [200-400]
- Algorithms tested: MIP, GA, PL-Rank, MCTS, RW-Rank-BFS (5 algos × 5 seeds = 25 runs)
- **NOT tested on regular tree**

### 3. **High Load** - TREE ONLY ✓
- Topology: 16-node tree, CPU [50-100], BW [200-400]
- VNR: 5-15 nodes, arrival rate λ=0.08
- Algorithms tested: MIP, GA, SA, PL-Rank, MCTS, R-Round, RW-Rank-BFS
- **NOT tested on fat-tree**

### 4. **Tight Resources** - TREE ONLY ✓
- Topology: 16-node tree, CPU [30-60], BW [100-200] (reduced capacity)
- Algorithms tested: MIP, GA, SA, PL-Rank, MCTS, R-Round, RW-Rank-BFS
- **NOT tested on fat-tree**

### 5. **Complex VNRs** - TREE ONLY ✓
- Topology: 16-node tree, CPU [50-100], BW [200-400]
- VNR: 8-20 nodes (very large)
- Algorithms tested: MIP, GA, SA, PL-Rank, MCTS, R-Round, RW-Rank-BFS
- **NOT tested on fat-tree**

---

## Actual Topology Distribution

| Scenario | Tree | Fat-Tree | Total Runs |
|----------|------|----------|------------|
| Normal Tree | ✓ (varied sizes: 16, 32 nodes) | ✗ | ~46 |
| Fat-Tree | ✗ | ✓ (k=4, 16 hosts) | 25 |
| High Load | ✓ (16 nodes) | ✗ | 35 |
| Tight Resources | ✓ (16 nodes) | ✗ | 35 |
| Complex VNRs | ✓ (16 nodes) | ✗ | 35 |
| D-Round special | ✓ (32 nodes) | ✗ | 5 |
| **TOTAL** | **~166 runs** | **25 runs** | **191** |

---

## Key Finding

**87% of your experiments used TREE topology**, only 13% used fat-tree!

### Why This Matters for Your Decision Tree:

1. **Fat-tree data is limited** - Only 25 runs, all with small VNRs (2-10 nodes)
2. **No fat-tree stress testing** - No high load, tight resources, or complex VNRs on fat-tree
3. **Topology is a critical feature** - Your XGBoost selector needs to learn:
   - Tree vs Fat-tree topology differences
   - How algorithms perform differently on each

### Recommendation:

Your **saturation scenario** should ideally be tested on **BOTH** topologies:
- Tree topology (currently running) ✓
- Fat-tree topology (missing) ✗

This would give more balanced data for the decision tree to learn topology-specific patterns.

---

## Tree Topology Variants Used

You actually used **different tree sizes**:

1. **16-node tree** - High load, tight, complex, MCTS experiments
   - CPU: [50-100] or [30-60] (tight)
   - BW: [200-400] or [100-200] (tight)

2. **32-node tree** - Normal, GA, D-Round experiments  
   - CPU: [50-100]
   - BW: [50-100] or [200-400]

This variation is GOOD - it helps the model learn about network size effects!

