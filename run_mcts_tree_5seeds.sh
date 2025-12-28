#!/bin/bash

# Run Monte Carlo Tree Search (MCTS) solver on tree topology with 5 different seeds
# Each run will have 200 VNR requests on a tree topology with clean switches (CPU=0)
#
# MCTS is a reinforcement learning-based solver that uses tree search with random
# simulations and UCB1 for balancing exploration and exploitation
# Reference: Soroush Haeri et al. "Virtual Network Embedding via Monte Carlo Tree Search".
#            IEEE Transactions on Cybernetics, 2018.

echo "============================================"
echo "MCTS Tree Topology Experiment"
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
    echo "Solver: Monte Carlo Tree Search (MCTS)"
    echo "Topology: Tree with clean switches"
    echo "VNRs: 200 requests"
    echo "Computation Budget: 5 iterations"
    echo "Exploration Constant: 0.5"
    echo "--------------------------------------------"

    # Run the experiment
    python main_tree_mcts.py \
        solver.solver_name=mcts \
        experiment.seed=$seed \
        experiment.run_id="mcts_tree_seed_$seed"

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
echo "  virne/mcts/mcts_tree_seed_*/records/"
echo ""
echo "Next steps:"
echo "  1. Analyze results across all seeds"
echo "  2. Compare acceptance rates and R2C ratios"
echo "  3. Compare with MIP, GA, D-Rounding, and PL-Rank solver results"
echo ""
