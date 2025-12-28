#!/bin/bash

# Massive VNRs Scenario
# Expected to favor: rw_rank_bfs, r_round (only fast heuristics complete)

set -e

ALGORITHMS=("mip" "ga_meta" "mcts" "sa_meta" "pl_rank" "rw_rank_bfs" "r_round")
SEEDS=(0 1 2 3 4)
SCENARIO="massive"
TIMEOUT=20

echo "=========================================="
echo "MASSIVE VNRs SCENARIO"
echo "=========================================="
echo "VNR size: 25-40 nodes (extremely large)"
echo "Expected: MIP/MCTS timeout, heuristics succeed"
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

echo "Massive VNRs scenario completed!"
