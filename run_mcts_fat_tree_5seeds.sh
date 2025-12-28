#!/bin/bash

echo "============================================"
echo "MCTS Fat-Tree Topology Experiment"
echo "Running 5 seeds (0, 1, 2, 3, 4)"
echo "============================================"
echo ""

SEEDS=(0 1 2 3 4)

for seed in "${SEEDS[@]}"
do
    echo "--------------------------------------------"
    echo "Starting experiment with seed: $seed"
    echo "Solver: MCTS"
    echo "Topology: Fat-Tree datacenter (k=4, 16 hosts)"
    echo "--------------------------------------------"

    python main_fat_tree_mcts.py \
        solver.solver_name=mcts \
        experiment.seed=$seed \
        experiment.run_id="mcts_fat_tree_seed_$seed"

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
echo "Results: virne/mcts/mcts_fat_tree_seed_*/records/"
echo "============================================"
