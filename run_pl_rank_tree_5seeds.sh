#!/bin/bash

# Run PL-Rank solver on tree topology with 5 different seeds
# Each run will have 200 VNR requests on a tree topology with clean switches (CPU=0)
#
# PL-Rank (Priority of Location) is a heuristic node-ranking based solver
# Reference: Fan et al. "Efficient Virtual Network Embedding of Cloud-Based
#            Data Center Networks into Optical Networks". TPDS, 2021.

echo "============================================"
echo "PL-Rank Tree Topology Experiment"
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
    echo "Solver: PL-Rank (Priority of Location)"
    echo "Topology: Tree with clean switches"
    echo "VNRs: 200 requests"
    echo "--------------------------------------------"

    # Run the experiment
    python main_tree_pl_rank.py \
        solver.solver_name=pl_rank \
        experiment.seed=$seed \
        experiment.run_id="pl_rank_tree_seed_$seed"

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
echo "  virne/pl_rank/pl_rank_tree_seed_*/records/"
echo ""
echo "Next steps:"
echo "  1. Analyze results across all seeds"
echo "  2. Compare acceptance rates and R2C ratios"
echo "  3. Compare with MIP and D-Rounding solver results"
echo ""
