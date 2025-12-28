#!/bin/bash

# Run Tree 2x and Fat-Tree 2x simulations
# Comparison: pl_rank (best) vs pso_meta (subrepresented)
# 5 seeds for each algorithm on each topology = 20 total simulations

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║     2X TOPOLOGIES SIMULATION CAMPAIGN - PL-RANK vs PSO-META       ║"
echo "║                     5 seeds per algorithm                          ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Function to run a single simulation
run_simulation() {
    local script=$1
    local seed=$2
    local algo=$3
    local topology=$4

    echo "🚀 Running: $algo on $topology - seed $seed"
    python "$script" experiment.seed=$seed 2>&1
    echo "   ✅ Completed: $algo on $topology - seed $seed"
}

# Arrays for scripts
pl_rank_scripts=("main_tree_2x_pl_rank.py" "main_fat_tree_2x_pl_rank.py")
pso_meta_scripts=("main_tree_2x_pso_meta.py" "main_fat_tree_2x_pso_meta.py")
topologies=("Tree 2x" "Fat-Tree 2x")

echo "Starting simulation campaign..."
echo ""

# PL-RANK on Tree 2x (seeds 0-4)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 1: PL-RANK on Tree 2x (64 nodes) - 5 seeds"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for seed in 0 1 2 3 4; do
    run_simulation "main_tree_2x_pl_rank.py" $seed "pl_rank" "Tree 2x"
done
echo ""

# PL-RANK on Fat-Tree 2x (seeds 0-4)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 2: PL-RANK on Fat-Tree 2x (32 nodes) - 5 seeds"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for seed in 0 1 2 3 4; do
    run_simulation "main_fat_tree_2x_pl_rank.py" $seed "pl_rank" "Fat-Tree 2x"
done
echo ""

# PSO-META on Tree 2x (seeds 0-4)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 3: PSO-META on Tree 2x (64 nodes) - 5 seeds"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for seed in 0 1 2 3 4; do
    run_simulation "main_tree_2x_pso_meta.py" $seed "pso_meta" "Tree 2x"
done
echo ""

# PSO-META on Fat-Tree 2x (seeds 0-4)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 4: PSO-META on Fat-Tree 2x (32 nodes) - 5 seeds"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for seed in 0 1 2 3 4; do
    run_simulation "main_fat_tree_2x_pso_meta.py" $seed "pso_meta" "Fat-Tree 2x"
done
echo ""

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║               ✅ ALL SIMULATIONS COMPLETED!                       ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "✓ PL-RANK on Tree 2x: 5 seeds (0-4)"
echo "✓ PL-RANK on Fat-Tree 2x: 5 seeds (0-4)"
echo "✓ PSO-META on Tree 2x: 5 seeds (0-4)"
echo "✓ PSO-META on Fat-Tree 2x: 5 seeds (0-4)"
echo ""
echo "Total: 20 simulations completed"
echo ""
echo "Next: Extract and compare results"
