#!/bin/bash

echo "============================================"
echo "PL-Rank Fat-Tree Topology Experiment"
echo "Running 5 seeds (0, 1, 2, 3, 4)"
echo "============================================"
echo ""

SEEDS=(0 1 2 3 4)

for seed in "${SEEDS[@]}"
do
    echo "--------------------------------------------"
    echo "Starting experiment with seed: $seed"
    echo "Solver: PL-Rank"
    echo "Topology: Fat-Tree datacenter (k=4, 16 hosts)"
    echo "--------------------------------------------"

    python main_fat_tree_pl_rank.py \
        solver.solver_name=pl_rank \
        experiment.seed=$seed \
        experiment.run_id="pl_rank_fat_tree_seed_$seed"

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
echo "Results: virne/pl_rank/pl_rank_fat_tree_seed_*/records/"
echo "============================================"
