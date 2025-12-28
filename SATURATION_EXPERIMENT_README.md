# VNE SATURATION SCENARIO EXPERIMENTS

## Overview

This experiment tests all VNE algorithms under **extreme network saturation** conditions with very large VNRs that heavily consume physical network resources.

## Scenario Configuration

### Virtual Network Requests (VNRs)
- **Size**: 15-30 nodes (VERY LARGE - 2-3x larger than "complex" scenario)
- **Topology**: Random with 60% connectivity
- **Node CPU Demand**: 20-60 units (2x larger than complex)
- **Link BW Demand**: 40-150 units (1.5x larger than complex)
- **Arrival Rate**: λ = 0.06 (moderate-high)
- **Lifetime**: 800 time units (long - resources stay allocated)
- **Total VNRs**: 200

### Physical Network
- **Topology**: 16-node binary tree
- **Node CPU Capacity**: 50-100 units per node
- **Link BW Capacity**: 200-400 units per link
- **Total Nodes**: 31 (16 hosts + 15 switches)

### Expected Behavior
- **Acceptance Rate**: <5% (extreme saturation)
- **Resource Contention**: Very high - each VNR demands 300-1800 CPU units and 600-4500 BW units
- **Algorithm Challenge**: Most VNRs will be rejected due to insufficient resources
- **Timeout**: 10 seconds per VNR for MIP solver (prevents extremely long solve times)

## Comparison with Other Scenarios

| Scenario | VNR Size | Node Demand | Link Demand | Expected Acceptance |
|----------|----------|-------------|-------------|---------------------|
| Normal   | 2-10     | 0-20        | 0-50        | 40-46%             |
| High Load| 5-15     | 5-30        | 10-70       | 7-17%              |
| Complex  | 8-20     | 10-40       | 20-100      | 1.5%               |
| **SATURATION** | **15-30** | **20-60** | **40-150** | **<5%** |

## Algorithms Tested

1. **MIP** - Exact solver (slow, optimal)
2. **PL-Rank** - Fast heuristic based on node ranking
3. **RW-Rank-BFS** - Fast heuristic with BFS
4. **GA** - Genetic Algorithm meta-heuristic
5. **MCTS** - Monte Carlo Tree Search
6. **SA** - Simulated Annealing
7. **R-Round** - Random rounding baseline

## Running the Experiments

### Run All Algorithms (5 seeds each)
```bash
./run_saturation_all_algos.sh
```

### Run Individual Algorithm
```bash
# MIP
python main_tree_saturation_mip.py experiment.seed=0

# PL-Rank
python main_tree_saturation_pl_rank.py experiment.seed=0

# RW-Rank-BFS
python main_tree_saturation_rw_rank_bfs.py experiment.seed=0

# GA
python main_tree_saturation_ga.py experiment.seed=0

# MCTS
python main_tree_saturation_mcts.py experiment.seed=0

# SA
python main_tree_saturation_sa.py experiment.seed=0

# R-Round
python main_tree_saturation_r_round.py experiment.seed=0
```

## Expected Results

### Hypothesis
- **All algorithms** will have very low acceptance rates (<5%)
- **Exact methods (MIP)** may still find optimal solutions but will be very slow
- **Meta-heuristics (GA, SA, MCTS)** may perform slightly better due to better exploration
- **Fast heuristics (PL-Rank, RW-Rank-BFS)** will be fast but may miss rare feasible solutions

### Key Metrics to Compare
1. **Acceptance Rate** - How many VNRs were successfully embedded
2. **Solution Time** - How long each algorithm took
3. **Resource Efficiency** - R2C ratio (revenue-to-cost)
4. **Failure Patterns** - Why VNRs failed (node shortage vs link shortage)

## Output Files

Results will be saved to:
```
virne/
├── mip_saturation_seed_0/
├── pl_rank_saturation_seed_0/
├── rw_rank_bfs_saturation_seed_0/
├── ga_meta_saturation_seed_0/
├── mcts_saturation_seed_0/
├── sa_meta_saturation_seed_0/
├── r_round_saturation_seed_0/
└── ... (seeds 1-4)
```

Each directory contains:
- `records/summary.csv` - Per-VNR results
- `logs/running.log` - Execution logs
- `logs/events.out.tfevents.*` - TensorBoard logs

## Purpose for Decision Tree Learning

This saturation scenario helps the decision tree learn:
1. **When to reject early** - Some VNRs are impossible to embed
2. **Resource threshold detection** - Minimum resources needed for large VNRs
3. **Algorithm limits** - Which algorithms handle extreme cases better
4. **Failure mode patterns** - Why embeddings fail under saturation

## Analysis Questions

After running experiments:
1. Which algorithm has the highest acceptance rate under saturation?
2. Is there a speed vs. quality tradeoff even at low acceptance rates?
3. Do meta-heuristics explore better solutions than greedy heuristics?
4. At what VNR size does acceptance drop to zero?
5. Can we predict VNR rejection based on size and current network load?

---

**Created**: 2025-11-21
**Author**: Luis Antonio Momm Duarte
**Purpose**: Test VNE algorithms under extreme network saturation