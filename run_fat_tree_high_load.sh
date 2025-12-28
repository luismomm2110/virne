#!/bin/bash
# Run Fat-Tree High Load experiments (Priority 3)
# 5 algorithms × 3 seeds = 15 runs

echo "=========================================="
echo "Fat-Tree HIGH LOAD Experiments"
echo "VNR: 5-15 nodes, λ=0.08 (high arrival)"
echo "Physical: Fat-tree, CPU [50-100], BW [200-400]"
echo "Expected: 10-20% acceptance"
echo "=========================================="
echo ""

# MIP - 3 seeds
echo "Starting MIP experiments (3 seeds)..."
python main_tree_saturation_mip.py --config-name=main_fat_tree_high_load experiment.seed=0 &
sleep 2
python main_tree_saturation_mip.py --config-name=main_fat_tree_high_load experiment.seed=1 &
sleep 2
python main_tree_saturation_mip.py --config-name=main_fat_tree_high_load experiment.seed=2 &
echo "  MIP: 3 runs started"

# GA - 3 seeds
echo "Starting GA experiments (3 seeds)..."
python main_tree_saturation_ga.py --config-name=main_fat_tree_high_load experiment.seed=0 &
sleep 2
python main_tree_saturation_ga.py --config-name=main_fat_tree_high_load experiment.seed=1 &
sleep 2
python main_tree_saturation_ga.py --config-name=main_fat_tree_high_load experiment.seed=2 &
echo "  GA: 3 runs started"

# MCTS - 3 seeds
echo "Starting MCTS experiments (3 seeds)..."
python main_tree_saturation_mcts.py --config-name=main_fat_tree_high_load experiment.seed=0 &
sleep 2
python main_tree_saturation_mcts.py --config-name=main_fat_tree_high_load experiment.seed=1 &
sleep 2
python main_tree_saturation_mcts.py --config-name=main_fat_tree_high_load experiment.seed=2 &
echo "  MCTS: 3 runs started"

# PL-Rank - 3 seeds
echo "Starting PL-Rank experiments (3 seeds)..."
python main_tree_saturation_pl_rank.py --config-name=main_fat_tree_high_load experiment.seed=0 &
sleep 2
python main_tree_saturation_pl_rank.py --config-name=main_fat_tree_high_load experiment.seed=1 &
sleep 2
python main_tree_saturation_pl_rank.py --config-name=main_fat_tree_high_load experiment.seed=2 &
echo "  PL-Rank: 3 runs started"

# SA - 3 seeds
echo "Starting SA experiments (3 seeds)..."
python main_tree_saturation_sa.py --config-name=main_fat_tree_high_load experiment.seed=0 &
sleep 2
python main_tree_saturation_sa.py --config-name=main_fat_tree_high_load experiment.seed=1 &
sleep 2
python main_tree_saturation_sa.py --config-name=main_fat_tree_high_load experiment.seed=2 &
echo "  SA: 3 runs started"

echo ""
echo "=========================================="
echo "All 15 experiments started in background"
echo "Monitor with: ./monitor_experiments.sh"
echo "=========================================="
