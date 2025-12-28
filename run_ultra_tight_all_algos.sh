#!/bin/bash

# Ultra-Tight Resources Scenario
# Expected to favor: pl_rank, rw_rank_bfs (fast heuristics)

set -e

ALGORITHMS=("mip" "ga_meta" "mcts" "sa_meta" "pl_rank" "rw_rank_bfs" "r_round")
SEEDS=(0 1 2 3 4)
SCENARIO="ultra_tight"
TIMEOUT=30

echo "=========================================="
echo "ULTRA-TIGHT RESOURCES SCENARIO"
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

echo "Ultra-tight scenario completed!"
