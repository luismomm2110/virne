#!/bin/bash

# Run Simulated Annealing (SA) solver on tree topology with 5 different seeds
# Each run will have 200 VNR requests on a tree topology with clean switches (CPU=0)
#
# SA is a probabilistic meta-heuristic optimization algorithm inspired by
# the annealing process in metallurgy. It's effective for VNE problems.

echo "============================================"
echo "SA Tree Topology Experiment"
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
    echo "Solver: SA (Meta-Heuristic)"
    echo "Topology: Tree with clean switches"
    echo "VNRs: 200 requests"
    echo "--------------------------------------------"

    # Run the experiment
    python main_tree_sa.py \
        solver.solver_name=sa_meta \
        experiment.seed=$seed \
        experiment.run_id="sa_meta_tree_seed_$seed"

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
echo "  virne/sa_meta/sa_meta_tree_seed_*/records/"
echo ""
echo "Next steps:"
echo "  1. Analyze results across all seeds"
echo "  2. Compare acceptance rates and R2C ratios"
echo "  3. Compare with MIP, GA, MCTS, PL-Rank, and RW-Rank-BFS results"
echo "  4. Use as training data for decision tree selector"
echo ""
