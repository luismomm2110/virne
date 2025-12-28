#!/bin/bash

# Script to run GA_Meta vs RW_Rank_BFS comparison on high-saturation scenarios
# 2 topologies × 2 algorithms × 3 seeds = 12 simulations

set -e

echo "=========================================="
echo "GA_Meta vs RW_Rank_BFS Comparison"
echo "High-Saturation Scenarios"
echo "=========================================="

# Create output directory
mkdir -p virne/ga_vs_rw_comparison

# Array of configurations
declare -a CONFIGS=(
    "main_tree_ga_meta_favoring"
    "main_tree_rw_rank_bfs_favoring"
    "main_fat_tree_ga_meta_favoring"
    "main_fat_tree_rw_rank_bfs_favoring"
)

SEEDS=(0 1 2)
TOTAL_RUNS=12
CURRENT_RUN=0

# Run each configuration with 3 seeds
for CONFIG in "${CONFIGS[@]}"; do
    for SEED in "${SEEDS[@]}"; do
        CURRENT_RUN=$((CURRENT_RUN + 1))

        echo ""
        echo "=========================================="
        echo "Run $CURRENT_RUN/$TOTAL_RUNS: $CONFIG (seed=$SEED)"
        echo "=========================================="

        # Run simulation
        python3 main.py \
            --config-name=$CONFIG \
            experiment.seed=$SEED \
            2>&1 | tee "virne/ga_vs_rw_comparison/${CONFIG}_seed${SEED}.log"

        # Copy results
        if [ -d "virne/${CONFIG}" ]; then
            mv "virne/${CONFIG}" "virne/ga_vs_rw_comparison/${CONFIG}_seed${SEED}"
        fi

        echo "✓ Completed: $CONFIG seed $SEED"
        sleep 2
    done
done

echo ""
echo "=========================================="
echo "All simulations completed!"
echo "Results saved in: virne/ga_vs_rw_comparison/"
echo "=========================================="
