# Simulation Results - Virtual Network Embedding

## Directory Structure

```
apresentacao/simulacoes/
├── TOPOLOGY_SUMMARY.md          # Overview of all topology results
├── WAXMAN_16_RESULTS.csv        # Consolidated Waxman-16 results
├── global_summary.csv           # Master dataset (Tree + Fat Tree)
├── training_summary.csv         # Training run summaries
│
├── waxman_16_analysis/          # Waxman-16 topology analysis
│   ├── waxman_16_detailed_results.csv
│   ├── waxman_16_comparison.csv
│   ├── WAXMAN_16_PRELIMINARY_REPORT.md
│   ├── FINDINGS_SUMMARY.txt
│   └── [other analysis documents]
│
├── d_round/                     # D-Rounding algorithm runs
├── ga_meta/                     # Genetic Algorithm (Meta) runs
├── mcts/                        # Monte Carlo Tree Search runs
├── mip/                         # Mixed Integer Programming runs
├── pl_rank/                     # PageRank-based Link runs
├── pso_meta/                    # Particle Swarm Optimization runs
├── rw_rank_bfs/                 # Random Walk + Rank + BFS runs
├── sa_meta/                     # Simulated Annealing (Meta) runs
│
└── [other directories]
```

## Key Results Files

### Master Datasets
- **`global_summary.csv`** - Comprehensive dataset with all Tree and Fat Tree runs
  - Columns: algorithm, topology, seed, acceptance_rate, r2c_ratio, timing metrics, etc.
  - Contains thousands of rows across all algorithm-topology combinations
  
- **`WAXMAN_16_RESULTS.csv`** - Waxman-16 topology results in same format
  - 35 rows (7 algorithms × 5 seeds)
  - Includes node_count, link_count fields for topology identification

### Topology-Specific Summaries
- **`waxman_16_analysis/waxman_16_detailed_results.csv`** - Per-seed detailed metrics
- **`waxman_16_analysis/waxman_16_comparison.csv`** - Aggregated statistics per algorithm

## Topologies Tested

### Tree Topology
- **Nodes:** 31-32
- **Links:** Sparse tree structure
- **Resources:** CPU [50-100], BW [50-100]
- **Characteristics:** Hierarchical, predictable structure
- **Results Location:** Algorithm subdirectories + global_summary.csv

### Fat Tree Topology  
- **Nodes:** 16-20
- **Links:** Dense (characteristic of fat tree)
- **Resources:** CPU [50-100], BW [200-400]
- **Characteristics:** High-capacity, symmetric structure
- **Results Location:** Algorithm subdirectories + global_summary.csv

### Waxman-16 Topology
- **Nodes:** 16
- **Links:** 500 (realistic random topology)
- **Resources:** CPU [50-100], BW [50-100]
- **Characteristics:** Realistic network topology, moderate density
- **Results Location:** `waxman_16_analysis/` + WAXMAN_16_RESULTS.csv

## Performance Summary

| Topology | Best Algorithm | Avg Acceptance | Consistency |
|----------|----------------|-----------------|-------------|
| Tree | Variable (context-dependent) | 15-80% | High variance |
| Fat Tree | MIP | 65-75% | Very consistent |
| Waxman-16 | MIP | 65.2% | Very consistent |

### Algorithm Rankings
1. **MIP** - Best for dense/constrained networks
2. **PL_RANK** - Competitive, especially on sparse topologies
3. **GA_META** - Good balance, reliable heuristic
4. **MCTS** - Moderate performance
5. **RW_RANK_BFS** - Context-dependent
6. **SA_META** - Variable performance
7. **D_ROUND** - Weakest across all topologies

## How to Use

### For Decision Tree Training
```python
import pandas as pd

# Load all topology results
tree_fat_tree = pd.read_csv('global_summary.csv')
waxman_16 = pd.read_csv('WAXMAN_16_RESULTS.csv')

# Combine for cross-topology training
all_results = pd.concat([tree_fat_tree, waxman_16])
```

### For Waxman-16 Analysis
```python
import pandas as pd

results = pd.read_csv('waxman_16_analysis/waxman_16_detailed_results.csv')
# Per-seed results: algorithm, acceptance_rate, r2c_ratio, etc.
```

### For Specific Topology
```python
import pandas as pd

# Tree topology
tree_only = global_summary[global_summary['p_net'].str.contains('tree')]

# Fat Tree topology  
fat_tree_only = global_summary[global_summary['p_net'].str.contains('fat_tree')]

# Waxman-16
waxman_only = pd.read_csv('WAXMAN_16_RESULTS.csv')
```

## Metrics Explained

- **acceptance_rate** - % of VNRs successfully embedded (0-1)
- **r2c_ratio** - Revenue-to-Cost ratio (resource efficiency)
- **success_count** - Number of successfully embedded VNRs out of 1000
- **total_simulation_time** - Wall-clock simulation duration (seconds)
- **node_count** - Number of nodes in physical network
- **link_count** - Number of links in physical network

## Citation Info

Results from:
- **Tree & Fat Tree:** Training phase (November-December 2024)
- **Waxman-16:** Latest experiments (December 21, 2024)

All results include:
- 5 random seeds per configuration (statistical significance)
- 1000 VNRs per simulation run
- Exponentially distributed lifetimes (mean: 500 time units)
- Poisson arrival process

See `ACADEMIC_ANALYSIS_OPTION2.md` (parent directory) for comprehensive analysis incorporating all topologies.
