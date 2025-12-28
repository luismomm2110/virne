# PL-Rank Tree Topology Experiment

This directory contains experiment scripts for running the **PL-Rank (Priority of Location)** algorithm on a tree topology with clean switches (routing-only nodes).

## Algorithm Overview

**PL-Rank** is a heuristic node-ranking based Virtual Network Embedding (VNE) algorithm that considers node proximity and location priority when mapping virtual networks onto physical infrastructure.

- **Type**: Heuristic (Node-Ranking)
- **Implementation**: `virne/solver/heuristic/node_rank.py:168`
- **Reference**: Fan et al. "Efficient Virtual Network Embedding of Cloud-Based Data Center Networks into Optical Networks". IEEE TPDS, 2021.

### Key Features:
- Uses NRM (Network Resource Metric) for node ranking
- Considers node proximity and location priority
- Two-stage mapping: node placement followed by link routing
- Custom path ranking for efficient link embedding

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
- **Solver**: `pl_rank`
- **Configuration file**: `settings/main_tree_pl_rank.yaml`

## Files

### Main Runner Script
- **`main_tree_pl_rank.py`**: Single experiment runner with Hydra configuration
  - Uses `settings/main_tree_pl_rank.yaml`
  - Sets switches to routing-only (CPU=0)
  - Runs PL-Rank solver

### Experiment Runners

#### Option 1: Python Script (Recommended)
- **`run_pl_rank_tree_experiment.py`**: Runs 5 seeds sequentially in Python
  ```bash
  python run_pl_rank_tree_experiment.py
  ```

#### Option 2: Bash Script
- **`run_pl_rank_tree_5seeds.sh`**: Runs 5 seeds sequentially in Bash
  ```bash
  ./run_pl_rank_tree_5seeds.sh
  ```

## Usage

### Quick Start (Run all 5 seeds)

```bash
# Using Python script
python run_pl_rank_tree_experiment.py

# OR using Bash script
./run_pl_rank_tree_5seeds.sh
```

### Run Single Seed

```bash
# Run with specific seed (e.g., seed=2)
python main_tree_pl_rank.py experiment.seed=2

# Run with custom run_id
python main_tree_pl_rank.py \
    experiment.seed=0 \
    experiment.run_id=my_custom_run
```

### Custom Configuration

```bash
# Override specific parameters
python main_tree_pl_rank.py \
    experiment.seed=0 \
    solver.k_shortest=20 \
    solver.matching_mathod=greedy
```

## Expected Output

### During Execution
```
====================    Start     ====================

Running PL-Rank solver on tree topology with clean switches (routing-only)
Seed: 0
Solver: pl_rank

Physical network configured:
  - Switches (routing-only): 15 nodes with CPU=0
  - Hosts (compute nodes): 16 nodes with CPU>0
  - Total nodes: 31
  - Total links: 30

Generating 200 virtual network requests...
Running 200 VNR allocations with PL-Rank solver...
```

### Results Location
```
virne/pl_rank/
├── pl_rank_tree_seed_0/
│   ├── records/
│   │   └── summary.csv
│   └── logs/
│       ├── running.log
│       └── tensorboard/
├── pl_rank_tree_seed_1/
│   └── ...
├── pl_rank_tree_seed_2/
│   └── ...
├── pl_rank_tree_seed_3/
│   └── ...
└── pl_rank_tree_seed_4/
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

## Analysis

### View Individual Seed Results

```bash
# View summary for a specific seed
cat virne/pl_rank/pl_rank_tree_seed_0/records/summary.csv
```

### Compare Across Seeds

After running all 5 seeds, you can aggregate and compare results:

```python
import pandas as pd

# Load all seed results
seeds = [0, 1, 2, 3, 4]
results = []

for seed in seeds:
    df = pd.read_csv(f'virne/pl_rank/pl_rank_tree_seed_{seed}/records/summary.csv')
    results.append(df)

# Calculate statistics across seeds
acceptance_rates = [df['acceptance_rate'].iloc[0] for df in results]
avg_acceptance = sum(acceptance_rates) / len(acceptance_rates)
print(f"Average acceptance rate across 5 seeds: {avg_acceptance:.4f}")
```

### Compare with Other Algorithms

Compare PL-Rank results with MIP and D-Rounding:

```bash
# View MIP results
cat virne/mip/mip_tree_seed_0/records/summary.csv

# View D-Rounding results
cat virne/d_round/drounding_tree_seed_0/records/summary.csv

# View PL-Rank results
cat virne/pl_rank/pl_rank_tree_seed_0/records/summary.csv
```

## Expected Performance

### Time Complexity
- **Node Mapping**: O(|V_v| × |V_p|) where V_v is virtual nodes, V_p is physical nodes
- **Link Routing**: O(|E_v| × k × |E_p|) where E_v is virtual edges, k is k-shortest paths

### Typical Execution Time
- **Per VNR**: ~0.01-0.1 seconds (much faster than MIP)
- **200 VNRs**: ~2-20 seconds total
- **5 seeds**: ~10-100 seconds total

PL-Rank is significantly faster than exact solvers (MIP, D-Rounding) but may achieve slightly lower acceptance rates.

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure you're in the project root directory
   ```bash
   cd /path/to/virne
   python run_pl_rank_tree_experiment.py
   ```

2. **Config Not Found**: Verify config file exists
   ```bash
   ls settings/main_tree_pl_rank.yaml
   ```

3. **Permission Denied** (bash script):
   ```bash
   chmod +x run_pl_rank_tree_5seeds.sh
   ./run_pl_rank_tree_5seeds.sh
   ```

4. **Low Acceptance Rate**: This is expected on tree topologies with routing-only switches, as embedding options are limited

## Related Experiments

- **MIP Experiment**: `run_mip_tree_experiment.py` - Exact solver (slower, optimal)
- **D-Rounding Experiment**: `run_drounding_tree_experiment.py` - Exact solver with rounding
- **Other Heuristics**: Modify `solver.solver_name` to try:
  - `nrm_rank` - Network Resource Metric ranking
  - `grc_rank` - Global Resource Capacity ranking
  - `ffd_rank` - First Fit Decreasing ranking

## References

1. Fan, P., Chen, Z., Yang, Y., & Xu, F. (2021). "Efficient Virtual Network Embedding of Cloud-Based Data Center Networks into Optical Networks". IEEE Transactions on Parallel and Distributed Systems (TPDS), 32(12), 2986-3000.

2. Project Repository: [ViRNE - Virtual Network Embedding](https://github.com/GeminiLight/virne)

## Next Steps

1. Run the experiments: `python run_pl_rank_tree_experiment.py`
2. Analyze acceptance rates and R2C ratios across seeds
3. Compare PL-Rank performance with MIP and D-Rounding
4. Visualize results (acceptance rate vs. time, resource utilization)
5. Run sensitivity analysis with different parameters
