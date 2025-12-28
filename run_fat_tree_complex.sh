#!/bin/bash
# Run Fat-Tree Complex VNRs experiments (Priority 2)
# 3 algorithms × 3 seeds = 9 runs

echo "=========================================="
echo "Fat-Tree COMPLEX VNRs Experiments"
echo "VNR: 8-20 nodes, CPU [10-40], BW [20-100]"
echo "Physical: Fat-tree, CPU [50-100], BW [200-400]"
echo "Expected: 2-5% acceptance"
echo "=========================================="
echo ""

# MIP - 3 seeds
echo "Starting MIP experiments (3 seeds)..."
python main_tree_saturation_mip.py --config-name=main_fat_tree_complex experiment.seed=0 &
sleep 2
python main_tree_saturation_mip.py --config-name=main_fat_tree_complex experiment.seed=1 &
sleep 2
python main_tree_saturation_mip.py --config-name=main_fat_tree_complex experiment.seed=2 &
echo "  MIP: 3 runs started"

# GA - 3 seeds
echo "Starting GA experiments (3 seeds)..."
python main_tree_saturation_ga.py --config-name=main_fat_tree_complex experiment.seed=0 &
sleep 2
python main_tree_saturation_ga.py --config-name=main_fat_tree_complex experiment.seed=1 &
sleep 2
python main_tree_saturation_ga.py --config-name=main_fat_tree_complex experiment.seed=2 &
echo "  GA: 3 runs started"

# MCTS - 3 seeds
echo "Starting MCTS experiments (3 seeds)..."
python main_tree_saturation_mcts.py --config-name=main_fat_tree_complex experiment.seed=0 &
sleep 2
python main_tree_saturation_mcts.py --config-name=main_fat_tree_complex experiment.seed=1 &
sleep 2
python main_tree_saturation_mcts.py --config-name=main_fat_tree_complex experiment.seed=2 &
echo "  MCTS: 3 runs started"

echo ""
echo "=========================================="
echo "All 9 experiments started in background"
echo "Monitor with: ./monitor_experiments.sh"
echo "=========================================="
