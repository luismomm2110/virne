#!/bin/bash

# Run Tree 2x and Fat-Tree 2x simulations with SA-Meta
# Comparison with PL-RANK to validate topology size effect on algorithm performance
# 5 seeds for SA-Meta on each topology = 10 total simulations

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║    2X TOPOLOGIES SA-META CAMPAIGN - PL-RANK vs SA-META           ║"
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

echo "Starting SA-Meta simulation campaign..."
echo ""

# SA-Meta on Tree 2x (seeds 0-4)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 1: SA-Meta on Tree 2x (64 nodes) - 5 seeds"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for seed in 0 1 2 3 4; do
    run_simulation "main_tree_2x_sa_meta.py" $seed "sa_meta" "Tree 2x"
done
echo ""

# SA-Meta on Fat-Tree 2x (seeds 0-4)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 2: SA-Meta on Fat-Tree 2x (32 nodes) - 5 seeds"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for seed in 0 1 2 3 4; do
    run_simulation "main_fat_tree_2x_sa_meta.py" $seed "sa_meta" "Fat-Tree 2x"
done
echo ""

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║               ✅ SA-META CAMPAIGN COMPLETED!                      ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "✓ SA-Meta on Tree 2x: 5 seeds (0-4)"
echo "✓ SA-Meta on Fat-Tree 2x: 5 seeds (0-4)"
echo ""
echo "Total: 10 simulations completed"
echo ""
echo "Next: Extract and compare results with PL-RANK on 2x topologies"
