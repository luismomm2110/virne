#!/bin/bash
# Run SATURATION scenario with all algorithms across 5 seeds
# Very large VNRs (15-30 nodes) to test network saturation limits

echo "========================================"
echo "VNE SATURATION SCENARIO - ALL ALGORITHMS"
echo "VNR Size: 15-30 nodes (VERY LARGE)"
echo "Node Demand: 20-60 CPU units"
echo "Link Demand: 40-150 BW units"
echo "Expected: <5% acceptance across all algos"
echo "========================================"
echo ""

SEEDS=(0 1 2 3 4)

# MIP - Exact solver (slow but optimal)
echo "Starting MIP experiments..."
for seed in "${SEEDS[@]}"; do
    echo "  Running MIP with seed $seed..."
    python main_tree_saturation_mip.py experiment.seed=$seed
done

# PL-Rank - Fast heuristic
echo "Starting PL-Rank experiments..."
for seed in "${SEEDS[@]}"; do
    echo "  Running PL-Rank with seed $seed..."
    python main_tree_saturation_pl_rank.py experiment.seed=$seed
done

# RW-Rank-BFS - Fast heuristic with BFS
echo "Starting RW-Rank-BFS experiments..."
for seed in "${SEEDS[@]}"; do
    echo "  Running RW-Rank-BFS with seed $seed..."
    python main_tree_saturation_rw_rank_bfs.py experiment.seed=$seed
done

# GA - Genetic Algorithm meta-heuristic
echo "Starting GA experiments..."
for seed in "${SEEDS[@]}"; do
    echo "  Running GA with seed $seed..."
    python main_tree_saturation_ga.py experiment.seed=$seed
done

# MCTS - Monte Carlo Tree Search
echo "Starting MCTS experiments..."
for seed in "${SEEDS[@]}"; do
    echo "  Running MCTS with seed $seed..."
    python main_tree_saturation_mcts.py experiment.seed=$seed
done

# SA - Simulated Annealing
echo "Starting SA experiments..."
for seed in "${SEEDS[@]}"; do
    echo "  Running SA with seed $seed..."
    python main_tree_saturation_sa.py experiment.seed=$seed
done

# R-Round - Random rounding
echo "Starting R-Round experiments..."
for seed in "${SEEDS[@]}"; do
    echo "  Running R-Round with seed $seed..."
    python main_tree_saturation_r_round.py experiment.seed=$seed
done

echo ""
echo "========================================"
echo "SATURATION EXPERIMENTS COMPLETE"
echo "Results saved to virne/*_saturation_seed_*/"
echo "========================================"