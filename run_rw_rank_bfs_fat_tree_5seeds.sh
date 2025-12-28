#!/bin/bash

echo "============================================"
echo "RW-Rank-BFS Fat-Tree Topology Experiment"
echo "Running 5 seeds (0, 1, 2, 3, 4)"
echo "============================================"
echo ""

SEEDS=(0 1 2 3 4)

for seed in "${SEEDS[@]}"
do
    echo "--------------------------------------------"
    echo "Starting experiment with seed: $seed"
    echo "Solver: RW-Rank-BFS"
    echo "Topology: Fat-Tree datacenter (k=4, 16 hosts)"
    echo "--------------------------------------------"

    python main_fat_tree_rw_rank_bfs.py \
        solver.solver_name=rw_rank_bfs \
        experiment.seed=$seed \
        experiment.run_id="rw_rank_bfs_fat_tree_seed_$seed"

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
echo "Results: virne/rw_rank_bfs/rw_rank_bfs_fat_tree_seed_*/records/"
echo "============================================"
