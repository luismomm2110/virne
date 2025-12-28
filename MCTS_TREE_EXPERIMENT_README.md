# Monte Carlo Tree Search (MCTS) Tree Topology Experiment

This directory contains experiment scripts for running **Monte Carlo Tree Search (MCTS)** on a tree topology with clean switches (routing-only nodes).

## Algorithm Overview

**Monte Carlo Tree Search (MCTS)** is a reinforcement learning-based algorithm that combines tree search with random sampling to make optimal decisions. It uses the UCB1 (Upper Confidence Bound) algorithm to balance exploration of new possibilities with exploitation of known good solutions.

- **Type**: Reinforcement Learning / Tree Search
- **Implementation**: `virne/solver/learning/reinforcement_learning/mcts_solver/mcts.py:16`
- **Reference**: Soroush Haeri et al. "Virtual Network Embedding via Monte Carlo Tree Search". IEEE Transactions on Cybernetics, 2018.

### Key Features:
- **Tree-based search**: Builds a search tree incrementally through simulation
- **UCB1 selection**: Balances exploration vs. exploitation using Upper Confidence Bound
- **Random simulation**: Uses Monte Carlo simulations to evaluate node quality
- **Backpropagation**: Updates node values based on simulation results
- **No training required**: Works out-of-the-box without pre-training

### MCTS Phases:

1. **Selection**: Starting from root, select child nodes using UCB1 until reaching a leaf
2. **Expansion**: Add one or more child nodes to the selected leaf node
3. **Simulation**: Run a random simulation from the new node to estimate its value
4. **Backpropagation**: Update visit counts and values for all nodes in the path

### Algorithm Parameters:
- **Computation budget**: 5 search iterations per node placement
- **Exploration constant**: 0.5 (UCB1 exploration parameter)
- **k_shortest**: 10 shortest paths for link mapping
- **Matching method**: greedy
- **Shortest path method**: k_shortest

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
- **Solver**: `mcts`
- **Configuration file**: `settings/main_tree_mcts.yaml`

## Files

### Main Runner Script
- **`main_tree_mcts.py`**: Single experiment runner with Hydra configuration
  - Uses `settings/main_tree_mcts.yaml`
  - Sets switches to routing-only (CPU=0)
  - Runs MCTS solver

### Experiment Runners

#### Option 1: Python Script (Recommended)
- **`run_mcts_tree_experiment.py`**: Runs 5 seeds sequentially in Python
  ```bash
  python run_mcts_tree_experiment.py
  ```

#### Option 2: Bash Script
- **`run_mcts_tree_5seeds.sh`**: Runs 5 seeds sequentially in Bash
  ```bash
  ./run_mcts_tree_5seeds.sh
  ```

## Usage

### Quick Start (Run all 5 seeds)

```bash
# Using Python script
python run_mcts_tree_experiment.py

# OR using Bash script
./run_mcts_tree_5seeds.sh
```

### Run Single Seed

```bash
# Run with specific seed (e.g., seed=2)
python main_tree_mcts.py experiment.seed=2

# Run with custom run_id
python main_tree_mcts.py \
    experiment.seed=0 \
    experiment.run_id=my_custom_run
```

### Custom Configuration

```bash
# Override specific parameters
python main_tree_mcts.py \
    experiment.seed=0 \
    solver.computation_budget=10 \
    solver.exploration_constant=1.0 \
    solver.k_shortest=20
```

## Expected Output

### During Execution
```
====================    Start     ====================

Running MCTS solver on tree topology with clean switches (routing-only)
Seed: 0
Solver: mcts
Computation budget: 5
Exploration constant: 0.5

Physical network configured:
  - Switches (routing-only): 15 nodes with CPU=0
  - Hosts (compute nodes): 16 nodes with CPU>0
  - Total nodes: 31
  - Total links: 30

Generating 200 virtual network requests...
Running 200 VNR allocations with MCTS solver...
```

### Results Location
```
virne/mcts/
├── mcts_tree_seed_0/
│   ├── records/
│   │   └── summary.csv
│   └── logs/
│       ├── running.log
│       └── tensorboard/
├── mcts_tree_seed_1/
│   └── ...
├── mcts_tree_seed_2/
│   └── ...
├── mcts_tree_seed_3/
│   └── ...
└── mcts_tree_seed_4/
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
cat virne/mcts/mcts_tree_seed_0/records/summary.csv
```

### Compare Across Seeds

After running all 5 seeds, you can aggregate and compare results:

```python
import pandas as pd

# Load all seed results
seeds = [0, 1, 2, 3, 4]
results = []

for seed in seeds:
    df = pd.read_csv(f'virne/mcts/mcts_tree_seed_{seed}/records/summary.csv')
    results.append(df)

# Calculate statistics across seeds
acceptance_rates = [df['acceptance_rate'].iloc[0] for df in results]
avg_acceptance = sum(acceptance_rates) / len(acceptance_rates)
print(f"Average acceptance rate across 5 seeds: {avg_acceptance:.4f}")
```

### Compare with Other Algorithms

Compare MCTS results with MIP, GA, D-Rounding, and PL-Rank:

```bash
# View MIP results
cat virne/mip/mip_tree_seed_0/records/summary.csv

# View GA results
cat virne/ga_meta/ga_meta_tree_seed_0/records/summary.csv

# View D-Rounding results
cat virne/d_round/drounding_tree_seed_0/records/summary.csv

# View PL-Rank results
cat virne/pl_rank/pl_rank_tree_seed_0/records/summary.csv

# View MCTS results
cat virne/mcts/mcts_tree_seed_0/records/summary.csv
```

## Expected Performance

### Time Complexity
- **Per Node Placement**:
  - Selection: O(B × D) where B is computation budget, D is tree depth
  - Expansion: O(|V_p|) where V_p is physical nodes
  - Simulation: O(|V_v| × |V_p| + |E_v| × k × |E_p|)
  - Backpropagation: O(D)
- **Total per VNR**: O(|V_v| × B × (|V_p| + |V_v| × |V_p| + |E_v| × k × |E_p|))

### Typical Execution Time
- **Per VNR**: ~2-8 seconds (depends on computation budget)
- **200 VNRs**: ~5-25 minutes total
- **5 seeds**: ~25-125 minutes total

MCTS typically achieves good solution quality through intelligent search, but can be slower than simple heuristics due to multiple simulations per decision.

### Performance Trade-offs
- **Pros**:
  - No training required (unlike deep RL methods)
  - Adapts to problem instances automatically
  - Balances exploration and exploitation
  - Can find high-quality solutions
  - Anytime algorithm (can stop early if needed)

- **Cons**:
  - Slower than simple heuristics
  - Performance depends on computation budget
  - Stochastic nature requires multiple runs
  - May not explore all possibilities with low budget
  - Limited by random simulation quality

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure you're in the project root directory
   ```bash
   cd /path/to/virne
   python run_mcts_tree_experiment.py
   ```

2. **Config Not Found**: Verify config file exists
   ```bash
   ls settings/main_tree_mcts.yaml
   ```

3. **Permission Denied** (bash script):
   ```bash
   chmod +x run_mcts_tree_5seeds.sh
   ./run_mcts_tree_5seeds.sh
   ```

4. **Low Acceptance Rate**: This is expected on tree topologies with routing-only switches, as embedding options are limited

5. **Slow Execution**: MCTS runs multiple simulations per node. Consider:
   - Reducing `computation_budget` (default: 5)
   - Reducing `k_shortest` (default: 10)
   - Using fewer VNRs for testing

6. **Poor Solution Quality**: If solutions are suboptimal, try:
   - Increasing `computation_budget` (more simulations)
   - Tuning `exploration_constant` (higher = more exploration)
   - Increasing `k_shortest` for link mapping

## Tuning MCTS Parameters

You can modify MCTS-specific parameters by editing the configuration:

```yaml
# In settings/main_tree_mcts.yaml
solver:
  computation_budget: 5        # Number of MCTS iterations per node
  exploration_constant: 0.5    # UCB1 exploration parameter
  k_shortest: 10              # Number of shortest paths for links
```

### Parameter Guidelines:

**computation_budget** (default: 5):
- Higher values = better solution quality but slower
- Typical range: 3-20
- 5 is a good balance for most cases

**exploration_constant** (default: 0.5):
- Higher values = more exploration of untried actions
- Lower values = more exploitation of known good actions
- Typical range: 0.1-2.0
- 0.5-1.0 works well for VNE problems

**k_shortest** (default: 10):
- Number of shortest paths to consider for link mapping
- Higher values = more routing options but slower
- Typical range: 5-20

## Related Experiments

- **MIP Experiment**: `run_mip_tree_experiment.py` - Exact solver (slower, optimal)
- **GA Experiment**: `run_ga_tree_experiment.py` - Meta-heuristic (evolutionary)
- **D-Rounding Experiment**: `run_drounding_tree_experiment.py` - Exact solver with rounding
- **PL-Rank Experiment**: `run_pl_rank_tree_experiment.py` - Fast heuristic
- **Other RL Methods**: Modify `solver.solver_name` to try:
  - `pg_cnn2` - Policy Gradient with CNN
  - `pg_seq` - Policy Gradient with Sequential model
  - `a3c_gcn` - A3C with Graph Convolutional Network

## Algorithm Details

### How MCTS Works for VNE

MCTS solves VNE by treating node placement as a sequential decision problem. For each virtual node to be placed:

1. **Build Search Tree**: Start with current physical network state as root

2. **Selection Phase**:
   - Starting from root, traverse tree using UCB1
   - UCB1 formula: `score = exploitation + c × sqrt(ln(parent_visits) / node_visits)`
   - Select child with highest UCB1 score

3. **Expansion Phase**:
   - When reaching a node not fully expanded
   - Add a new child representing a physical node placement
   - Choose physical node randomly among unvisited options

4. **Simulation Phase**:
   - From new node, randomly place remaining virtual nodes
   - Use greedy/random policy for quick rollout
   - Calculate final reward (embedding cost/revenue)

5. **Backpropagation Phase**:
   - Update visit counts for all nodes in path
   - Update value estimates with simulation reward
   - Propagate back to root

6. **Repeat**: Run simulation `computation_budget` times

7. **Select Best Action**: Choose child of root with highest exploitation value

8. **Next Virtual Node**: Repeat process for next node in VNR

### UCB1 Formula

```
UCB1(node) = exploitation + exploration

exploitation = node.value / node.visits
exploration = c × sqrt(ln(parent.visits) / node.visits)
```

Where:
- `c` is the exploration constant (controls exploration vs exploitation)
- Higher `c` = more exploration
- `c = 0` = pure exploitation (greedy)

## References

1. Soroush Haeri & Ljiljana Trajković (2018). "Virtual Network Embedding via Monte Carlo Tree Search". IEEE Transactions on Cybernetics, 48(2), 510-521.

2. Browne, C. B., Powley, E., Whitehouse, D., Lucas, S. M., Cowling, P. I., Rohlfshagen, P., ... & Colton, S. (2012). "A survey of monte carlo tree search methods". IEEE Transactions on Computational Intelligence and AI in games, 4(1), 1-43.

3. Kocsis, L., & Szepesvári, C. (2006). "Bandit based monte-carlo planning". In European conference on machine learning (pp. 282-293). Springer, Berlin, Heidelberg.

4. Project Repository: [ViRNE - Virtual Network Embedding](https://github.com/GeminiLight/virne)

## Next Steps

1. Run the experiments: `python run_mcts_tree_experiment.py`
2. Analyze acceptance rates and R2C ratios across seeds
3. Compare MCTS performance with:
   - Exact solvers (MIP, D-Rounding) - baseline optimal solutions
   - Meta-heuristics (GA, PSO) - alternative search methods
   - Heuristics (PL-Rank, NRM-Rank) - baseline fast solutions
   - Other RL methods (Policy Gradient, A3C) - learning-based approaches
4. Visualize results:
   - Acceptance rate vs. time
   - Resource utilization over time
   - Solution quality vs. execution time trade-off
   - MCTS tree statistics (depth, branching factor)
5. Experiment with MCTS parameters:
   - Try different computation budgets (3, 5, 10, 20)
   - Tune exploration constant (0.1, 0.5, 1.0, 2.0)
   - Compare with different k_shortest values
6. Analyze search tree properties:
   - Average tree depth per node placement
   - Number of nodes explored
   - Convergence behavior with more simulations
