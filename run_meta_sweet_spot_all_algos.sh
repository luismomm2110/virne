#!/bin/bash

# Meta-Heuristic Sweet Spot Scenario
# Expected to favor: ga_meta, sa_meta

set -e

ALGORITHMS=("mip" "ga_meta" "mcts" "sa_meta" "pl_rank" "rw_rank_bfs" "r_round")
SEEDS=(0 1 2 3 4)
SCENARIO="meta_sweet_spot"
TIMEOUT=120

echo "=========================================="
echo "META-HEURISTIC SWEET SPOT SCENARIO"
echo "=========================================="
echo "VNR size: 12-22 nodes (medium-large)"
echo "Demand range: Very wide (5-50 CPU, 10-120 BW)"
echo "Expected: GA/SA excel, MIP struggles, greedy suboptimal"
echo "=========================================="

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        echo "Running: ${algorithm} (seed ${seed})"

        python main.py \
            --config-name="main_tree_${SCENARIO}" \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_${SCENARIO}_seed_${seed}" \
            logger.experiment_name="${SCENARIO}_experiment"

        echo ""
    done
done

echo "Meta-heuristic sweet spot scenario completed!"
