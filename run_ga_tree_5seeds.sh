#!/bin/bash

# Run Genetic Algorithm solver on tree topology with 5 different seeds
# Each run will have 200 VNR requests on a tree topology with clean switches (CPU=0)
#
# Genetic Algorithm (GA) is a meta-heuristic solver that uses evolutionary principles
# Reference: Peiying Zhang et al. "Virtual network embedding based on modified
#            genetic algorithm". Peer-to-Peer Networking and Applications, 2019.

echo "============================================"
echo "Genetic Algorithm Tree Topology Experiment"
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
    echo "Solver: Genetic Algorithm (GA)"
    echo "Topology: Tree with clean switches"
    echo "VNRs: 200 requests"
    echo "--------------------------------------------"

    # Run the experiment
    python main_tree_ga.py \
        solver.solver_name=ga_meta \
        experiment.seed=$seed \
        experiment.run_id="ga_meta_tree_seed_$seed"

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
echo "  virne/ga_meta/ga_meta_tree_seed_*/records/"
echo ""
echo "Next steps:"
echo "  1. Analyze results across all seeds"
echo "  2. Compare acceptance rates and R2C ratios"
echo "  3. Compare with MIP, D-Rounding, and PL-Rank solver results"
echo ""
