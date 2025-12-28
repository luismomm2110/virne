# RW-Rank-BFS Tree Topology Experiment

This directory contains experiment scripts for running the **RW-Rank-BFS (Random Walk Rank with BFS Trials)** algorithm on a tree topology with clean switches (routing-only nodes).

## Algorithm Overview

**RW-Rank-BFS** is a heuristic node-ranking based Virtual Network Embedding (VNE) algorithm that uses random walk to rank nodes and employs BFS (Breadth-First Search) trials for deployment instead of traditional two-stage mapping.

- **Type**: Heuristic (Node-Ranking with BFS Trials)
- **Implementation**: `virne/solver/heuristic/bfs_trials.py:81`
- **Reference**: Cheng et al. "Virtual Network Embedding Through Topology-Aware Node Ranking". ACM SIGCOMM Computer Communication Review, 2011.

### Key Features:
- Uses random walk algorithm for node ranking
- BFS-based deployment strategy for integrated node and link mapping
- Level-based exploration starting from highest-ranked node
- Considers topology structure through random walk probabilities
- Explores multiple physical node placements through BFS trials

### How It Works:
1. **Node Ranking**: Ranks both virtual and physical nodes using random walk
2. **Level Assignment**: Computes BFS levels from highest-ranked virtual node
3. **BFS Deployment**: Explores physical network using BFS to find valid embeddings
   - Starts from highest-ranked physical node
   - Places virtual nodes level-by-level
   - Backtracks when necessary (controlled by max_visit and max_depth)

## Experiment Configuration

### Physical Network
- **Topology**: Binary tree with 5 levels
- **Total nodes**: 31 (15 switches + 16 hosts)
- **Switches**: Routing-only (CPU=0, cannot host virtual nodes)
- **Hosts**: 16 leaf nodes with CPU resources [50-100] units
- **Links**: Bandwidth [50-100] units

### Virtual Network Requests (VNRs)
- **Number of requests**: 200 per seed
- **VNR size**: 2-10 nodes per request
- **Connection probability**: 50% (random topology)
- **Node resource demands**: [0-20] units
- **Link resource demands**: [0-50] units
- **Lifetime**: Exponentially distributed (avg 500 time units)
- **Arrival process**: Poisson process

### Experiment Parameters
- **Random seeds**: 5 seeds (0, 1, 2, 3, 4) for statistical significance
- **Solver**: `rw_rank_bfs`
- **Configuration file**: `settings/main_tree_rw_rank_bfs.yaml`
- **BFS Parameters**:
  - `max_visit`: Maximum number of nodes to visit during BFS
  - `max_depth`: Maximum BFS depth for exploration
  - `k_shortest`: Number of shortest paths to consider

## Files

### Main Runner Script
- **`main_tree_rw_rank_bfs.py`**: Single experiment runner with Hydra configuration
  - Uses `settings/main_tree_rw_rank_bfs.yaml`
  - Sets switches to routing-only (CPU=0)
  - Runs RW-Rank-BFS solver

### Experiment Runners

#### Option 1: Python Script (Recommended)
- **`run_rw_rank_bfs_tree_experiment.py`**: Runs 5 seeds sequentially in Python
  ```bash
  python run_rw_rank_bfs_tree_experiment.py
  ```

#### Option 2: Bash Script
- **`run_rw_rank_bfs_tree_5seeds.sh`**: Runs 5 seeds sequentially in Bash
  ```bash
  ./run_rw_rank_bfs_tree_5seeds.sh
  ```

## Usage

### Quick Start (Run all 5 seeds)

```bash
# Using Python script
python run_rw_rank_bfs_tree_experiment.py

# OR using Bash script
./run_rw_rank_bfs_tree_5seeds.sh
```

### Run Single Seed

```bash
# Run with specific seed (e.g., seed=2)
python main_tree_rw_rank_bfs.py experiment.seed=2

# Run with custom run_id
python main_tree_rw_rank_bfs.py \
    experiment.seed=0 \
    experiment.run_id=my_custom_run
```

### Custom Configuration

```bash
# Override specific parameters
python main_tree_rw_rank_bfs.py \
    experiment.seed=0 \
    solver.max_visit=500 \
    solver.max_depth=10 \
    solver.k_shortest=5
```

## Expected Output

### During Execution
```
====================    Start     ====================

Running RW-Rank-BFS solver on tree topology with clean switches (routing-only)
Seed: 0
Solver: rw_rank_bfs

Physical network configured:
  - Switches (routing-only): 15 nodes with CPU=0
  - Hosts (compute nodes): 16 nodes with CPU>0
  - Total nodes: 31
  - Total links: 30

Generating 200 virtual network requests...
Running 200 VNR allocations with RW-Rank-BFS solver...
```

### Results Location
```
virne/rw_rank_bfs/
├── rw_rank_bfs_tree_seed_0/
│   ├── records/
│   │   └── summary.csv
│   └── logs/
│       ├── running.log
│       └── tensorboard/
├── rw_rank_bfs_tree_seed_1/
│   └── ...
├── rw_rank_bfs_tree_seed_2/
│   └── ...
├── rw_rank_bfs_tree_seed_3/
│   └── ...
└── rw_rank_bfs_tree_seed_4/
    └── ...
```

### Key Metrics Collected

Each experiment records:
- **Acceptance Rate**: Percentage of successfully embedded VNRs
- **R2C Ratio**: Revenue-to-Cost ratio (higher is better)
- **Long-term R2C Ratio**: R2C over extended time period
- **Success Count**: Number of successfully embedded VNRs
- **Place Failures**: Number of node placement failures
- **Route Failures**: Number of link routing failures
- **Early Rejections**: Number of requests rejected early
- **Total Revenue**: Sum of revenue from accepted requests
- **Total Cost**: Sum of costs for resource allocation
- **Solution Time**: Time taken to solve each VNR
- **BFS Statistics**: Number of nodes visited, depth reached

## Analysis

### View Individual Seed Results

```bash
# View summary for a specific seed
cat virne/rw_rank_bfs/rw_rank_bfs_tree_seed_0/records/summary.csv
```

### Compare Across Seeds

After running all 5 seeds, you can aggregate and compare results:

```python
import pandas as pd

# Load all seed results
seeds = [0, 1, 2, 3, 4]
results = []

for seed in seeds:
    df = pd.read_csv(f'virne/rw_rank_bfs/rw_rank_bfs_tree_seed_{seed}/records/summary.csv')
    results.append(df)

# Calculate statistics across seeds
acceptance_rates = [df['acceptance_rate'].iloc[0] for df in results]
avg_acceptance = sum(acceptance_rates) / len(acceptance_rates)
print(f"Average acceptance rate across 5 seeds: {avg_acceptance:.4f}")
```

### Compare with Other Algorithms

Compare RW-Rank-BFS results with other solvers:

```bash
# View MIP results
cat virne/mip/mip_tree_seed_0/records/summary.csv

# View PL-Rank results
cat virne/pl_rank/pl_rank_tree_seed_0/records/summary.csv

# View RW-Rank (standard) results
cat virne/rw_rank/rw_rank_tree_seed_0/records/summary.csv

# View RW-Rank-BFS results
cat virne/rw_rank_bfs/rw_rank_bfs_tree_seed_0/records/summary.csv
```

## Expected Performance

### Time Complexity
- **Node Ranking**: O(|V_p|² × iterations) for random walk convergence
- **BFS Deployment**: O(max_visit × |V_p|) with backtracking
- **Overall**: Depends on BFS exploration parameters (max_visit, max_depth)

### Typical Execution Time
- **Per VNR**: ~0.01-0.5 seconds (depends on BFS exploration)
- **200 VNRs**: ~2-100 seconds total (varies with max_visit)
- **5 seeds**: ~10-500 seconds total

RW-Rank-BFS may find better solutions than greedy two-stage methods due to BFS exploration, but takes longer than simple heuristics. Still much faster than exact solvers (MIP, D-Rounding).

### Parameter Tuning

**max_visit**: Controls exploration breadth
- Lower (100-200): Faster but may miss good solutions
- Higher (500-1000): Slower but more thorough exploration

**max_depth**: Controls exploration depth
- Lower (5-10): Limits backtracking depth
- Higher (15-20): More extensive backtracking

**k_shortest**: Number of shortest paths considered
- Lower (1-3): Faster routing decisions
- Higher (5-10): More routing options

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure you're in the project root directory
   ```bash
   cd /path/to/virne
   python run_rw_rank_bfs_tree_experiment.py
   ```

2. **Config Not Found**: Verify config file exists
   ```bash
   ls settings/main_tree_rw_rank_bfs.yaml
   ```

3. **Permission Denied** (bash script):
   ```bash
   chmod +x run_rw_rank_bfs_tree_5seeds.sh
   ./run_rw_rank_bfs_tree_5seeds.sh
   ```

4. **Slow Execution**: Reduce BFS parameters
   ```bash
   python main_tree_rw_rank_bfs.py \
       experiment.seed=0 \
       solver.max_visit=200 \
       solver.max_depth=5
   ```

5. **Low Acceptance Rate**: Try increasing exploration parameters
   ```bash
   python main_tree_rw_rank_bfs.py \
       experiment.seed=0 \
       solver.max_visit=1000 \
       solver.max_depth=15
   ```

## Algorithm Comparison

### RW-Rank-BFS vs. RW-Rank (Standard)
- **RW-Rank-BFS**: Uses BFS trials for integrated mapping
  - More exploration, potentially better solutions
  - Slower due to backtracking
  - Better for complex topologies

- **RW-Rank**: Uses two-stage greedy mapping
  - Faster, simpler approach
  - May miss optimal solutions
  - Good for large-scale scenarios

### When to Use RW-Rank-BFS
- When solution quality is more important than speed
- On smaller problem instances where BFS exploration is feasible
- When you want to explore the trade-off between exploration and speed

## Related Experiments

- **MIP Experiment**: `run_mip_tree_experiment.py` - Exact solver (slower, optimal)
- **D-Rounding Experiment**: `run_drounding_tree_experiment.py` - Exact solver with rounding
- **PL-Rank Experiment**: `run_pl_rank_tree_experiment.py` - Location-priority heuristic
- **RW-Rank Experiment**: `run_rw_rank_tree_experiment.py` - Standard random walk (two-stage)
- **Other Heuristics**: Modify `solver.solver_name` to try:
  - `nrm_rank` - Network Resource Metric ranking
  - `grc_rank` - Global Resource Capacity ranking
  - `ffd_rank` - First Fit Decreasing ranking

## References

1. Cheng, X., Su, S., Zhang, Z., Wang, H., Yang, F., Luo, Y., & Wang, J. (2011). "Virtual Network Embedding Through Topology-Aware Node Ranking". ACM SIGCOMM Computer Communication Review, 41(2), 38-47.

2. Project Repository: [ViRNE - Virtual Network Embedding](https://github.com/GeminiLight/virne)

## Next Steps

1. Run the experiments: `python run_rw_rank_bfs_tree_experiment.py`
2. Analyze acceptance rates and R2C ratios across seeds
3. Compare RW-Rank-BFS performance with:
   - RW-Rank (standard two-stage)
   - PL-Rank
   - Exact solvers (MIP, D-Rounding)
4. Tune BFS parameters (max_visit, max_depth) for optimal performance
5. Visualize results (acceptance rate vs. time, resource utilization)
6. Study trade-offs between exploration depth and execution time
