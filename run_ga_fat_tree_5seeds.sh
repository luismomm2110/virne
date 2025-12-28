#!/bin/bash

# Run Genetic Algorithm solver on Fat-Tree datacenter topology with 5 different seeds
# Fat-Tree provides redundant paths allowing GA to explore better solutions

echo "============================================"
echo "Genetic Algorithm Fat-Tree Topology Experiment"
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
    echo "Topology: Fat-Tree datacenter (k=4, 16 hosts)"
    echo "VNRs: 200 requests"
    echo "--------------------------------------------"

    # Run the experiment
    python main_fat_tree_ga.py \
        solver.solver_name=ga_meta \
        experiment.seed=$seed \
        experiment.run_id="ga_meta_fat_tree_seed_$seed"

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
echo "  virne/ga_meta/ga_meta_fat_tree_seed_*/records/"
echo ""
echo "Next steps:"
echo "  1. Analyze results across all seeds"
echo "  2. Compare with tree topology results"
echo "  3. Check if GA performs better on complex Fat-Tree topology"
echo ""
