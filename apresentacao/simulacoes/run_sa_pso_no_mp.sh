#!/bin/bash
#
# Run SA and PSO simulations without multiprocessing
# Fixes pickle errors by using sequential execution
#

set -e  # Exit on error

cd "$(dirname "$0")"

echo "================================================================================"
echo "Running SA and PSO simulations (NO MULTIPROCESSING)"
echo "================================================================================"
echo ""
echo "This will run:"
echo "  - SA: tree seeds 0-4, fat-tree seeds 0-4 (10 simulations)"
echo "  - PSO: tree seeds 0-4, fat-tree seeds 0-4 (10 simulations)"
echo "  Total: 20 simulations"
echo ""
echo "Note: Sequential execution is slower but avoids pickle errors"
echo ""

# Make scripts executable
chmod +x main_tree_sa_no_mp.py
chmod +x main_fat_tree_sa_no_mp.py
chmod +x main_tree_pso_no_mp.py
chmod +x main_fat_tree_pso_no_mp.py

# Counter
completed=0
total=20

# Run SA - Tree topology
echo "================================ SA - TREE ================================"
for seed in 0 1 2 3 4; do
    echo ""
    echo "[$((completed+1))/$total] Running SA tree seed $seed..."
    python main_tree_sa_no_mp.py $seed > logs/tree_sa_seed${seed}_no_mp.log 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ Completed SA tree seed $seed"
        completed=$((completed+1))
    else
        echo "  ✗ Failed SA tree seed $seed (check logs/tree_sa_seed${seed}_no_mp.log)"
    fi
done

# Run SA - Fat-Tree topology
echo ""
echo "============================= SA - FAT-TREE ==============================="
for seed in 0 1 2 3 4; do
    echo ""
    echo "[$((completed+1))/$total] Running SA fat-tree seed $seed..."
    python main_fat_tree_sa_no_mp.py $seed > logs/fat_tree_sa_seed${seed}_no_mp.log 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ Completed SA fat-tree seed $seed"
        completed=$((completed+1))
    else
        echo "  ✗ Failed SA fat-tree seed $seed (check logs/fat_tree_sa_seed${seed}_no_mp.log)"
    fi
done

# Run PSO - Tree topology
echo ""
echo "=============================== PSO - TREE ================================"
for seed in 0 1 2 3 4; do
    echo ""
    echo "[$((completed+1))/$total] Running PSO tree seed $seed..."
    python main_tree_pso_no_mp.py $seed > logs/tree_pso_seed${seed}_no_mp.log 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ Completed PSO tree seed $seed"
        completed=$((completed+1))
    else
        echo "  ✗ Failed PSO tree seed $seed (check logs/tree_pso_seed${seed}_no_mp.log)"
    fi
done

# Run PSO - Fat-Tree topology
echo ""
echo "============================ PSO - FAT-TREE ==============================="
for seed in 0 1 2 3 4; do
    echo ""
    echo "[$((completed+1))/$total] Running PSO fat-tree seed $seed..."
    python main_fat_tree_pso_no_mp.py $seed > logs/fat_tree_pso_seed${seed}_no_mp.log 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ Completed PSO fat-tree seed $seed"
        completed=$((completed+1))
    else
        echo "  ✗ Failed PSO fat-tree seed $seed (check logs/fat_tree_pso_seed${seed}_no_mp.log)"
    fi
done

echo ""
echo "================================================================================"
echo "COMPLETED: $completed / $total simulations"
echo "================================================================================"
echo ""

if [ $completed -eq $total ]; then
    echo "✓ All simulations completed successfully!"
    echo ""
    echo "Results saved to:"
    echo "  - virne/sa_meta/sa_tree_seed_*/records/temp-*.csv"
    echo "  - virne/sa_meta/sa_fat_tree_seed_*/records/temp-*.csv"
    echo "  - virne/pso_meta/pso_tree_seed_*/records/temp-*.csv"
    echo "  - virne/pso_meta/pso_fat_tree_seed_*/records/temp-*.csv"
    echo ""
    echo "Next step: Extract data"
    echo "  cd ../machine_learning"
    echo "  python 1_extract_vnr_data.py"
else
    echo "⚠️  Some simulations failed. Check logs in logs/ directory"
fi
echo ""
