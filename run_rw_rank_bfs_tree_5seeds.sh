#!/bin/bash

# Run RW-Rank-BFS solver on tree topology with 5 different seeds
# Each run will have 200 VNR requests on a tree topology with clean switches (CPU=0)
#
# RW-Rank-BFS (Random Walk Rank with BFS Trials) is a heuristic node-ranking based
# solver that uses random walk to rank nodes and BFS trials for deployment.
# Reference: Cheng et al. "Virtual Network Embedding Through Topology-Aware
#            Node Ranking". ACM SIGCOMM Computer Communication Review, 2011.

echo "============================================"
echo "RW-Rank-BFS Tree Topology Experiment"
echo "Running 5 seeds (0, 1, 2, 3, 4)"
echo "============================================"
echo ""

# Array of seeds to run
SEEDS=(0 1 2 3 4)

# Loop through each seed
for seed in "${SEEDS[@]}"
do
    echo "--------------------------------------------"
    echo "Starting experiment with seed: $seed"
    echo "Solver: RW-Rank-BFS (Random Walk with BFS)"
    echo "Topology: Tree with clean switches"
    echo "VNRs: 200 requests"
    echo "BFS Parameters: max_visit=500, max_depth=10"
    echo "--------------------------------------------"

    # Run the experiment
    python main_tree_rw_rank_bfs.py \
        solver.solver_name=rw_rank_bfs \
        experiment.seed=$seed \
        experiment.run_id="rw_rank_bfs_tree_seed_$seed"

    # Check if the command succeeded
    if [ $? -eq 0 ]; then
        echo "✓ Seed $seed completed successfully"
    else
        echo "✗ Seed $seed failed!"
        exit 1
    fi

    echo ""
done

echo "============================================"
echo "All experiments completed!"
echo "============================================"
echo ""
echo "Results saved in:"
echo "  virne/rw_rank_bfs/rw_rank_bfs_tree_seed_*/records/"
echo ""
echo "Next steps:"
echo "  1. Analyze results across all seeds"
echo "  2. Compare acceptance rates and R2C ratios"
echo "  3. Compare with other solvers:"
echo "     - RW-Rank (standard two-stage)"
echo "     - PL-Rank (location-priority heuristic)"
echo "     - MIP and D-Rounding (exact solvers)"
echo "  4. Study BFS exploration vs. solution quality"
echo ""
