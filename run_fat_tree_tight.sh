#!/bin/bash
# Run Fat-Tree Tight Resources experiments (Priority 1)
# 4 algorithms × 3 seeds = 12 runs

echo "=========================================="
echo "Fat-Tree TIGHT RESOURCES Experiments"
echo "VNR: 2-10 nodes, CPU [0-20], BW [0-50]"
echo "Physical: Fat-tree, CPU [30-60], BW [100-200]"
echo "Expected: 30-40% acceptance"
echo "=========================================="
echo ""

# MIP - 3 seeds
echo "Starting MIP experiments (3 seeds)..."
python main_tree_saturation_mip.py --config-name=main_fat_tree_tight experiment.seed=0 &
sleep 2
python main_tree_saturation_mip.py --config-name=main_fat_tree_tight experiment.seed=1 &
sleep 2
python main_tree_saturation_mip.py --config-name=main_fat_tree_tight experiment.seed=2 &
echo "  MIP: 3 runs started"

# GA - 3 seeds
echo "Starting GA experiments (3 seeds)..."
python main_tree_saturation_ga.py --config-name=main_fat_tree_tight experiment.seed=0 &
sleep 2
python main_tree_saturation_ga.py --config-name=main_fat_tree_tight experiment.seed=1 &
sleep 2
python main_tree_saturation_ga.py --config-name=main_fat_tree_tight experiment.seed=2 &
echo "  GA: 3 runs started"

# MCTS - 3 seeds
echo "Starting MCTS experiments (3 seeds)..."
python main_tree_saturation_mcts.py --config-name=main_fat_tree_tight experiment.seed=0 &
sleep 2
python main_tree_saturation_mcts.py --config-name=main_fat_tree_tight experiment.seed=1 &
sleep 2
python main_tree_saturation_mcts.py --config-name=main_fat_tree_tight experiment.seed=2 &
echo "  MCTS: 3 runs started"

# PL-Rank - 3 seeds
echo "Starting PL-Rank experiments (3 seeds)..."
python main_tree_saturation_pl_rank.py --config-name=main_fat_tree_tight experiment.seed=0 &
sleep 2
python main_tree_saturation_pl_rank.py --config-name=main_fat_tree_tight experiment.seed=1 &
sleep 2
python main_tree_saturation_pl_rank.py --config-name=main_fat_tree_tight experiment.seed=2 &
echo "  PL-Rank: 3 runs started"

echo ""
echo "=========================================="
echo "All 12 experiments started in background"
echo "Monitor with: ./monitor_experiments.sh"
echo "=========================================="
