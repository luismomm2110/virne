#!/bin/bash

# Run Edge-Case Experiments to Diversify Algorithm Selection
# This script runs 6 edge-case scenarios with all 7 algorithms (5 seeds each)
# Total: 6 scenarios × 7 algorithms × 5 seeds = 210 experiments

set -e  # Exit on error

ALGORITHMS=("mip" "ga_meta" "mcts" "sa_meta" "pl_rank" "rw_rank_bfs" "r_round")
SCENARIOS=(
    "ultra_tight"
    "massive"
    "realtime"
    "tiny_optimal"
    "meta_sweet_spot"
    "sparse_congested"
)
SEEDS=(0 1 2 3 4)

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "EDGE-CASE EXPERIMENT SUITE"
echo "=========================================="
echo "Scenarios: ${#SCENARIOS[@]}"
echo "Algorithms: ${#ALGORITHMS[@]}"
echo "Seeds per combination: ${#SEEDS[@]}"
echo "Total experiments: $((${#SCENARIOS[@]} * ${#ALGORITHMS[@]} * ${#SEEDS[@]}))"
echo "=========================================="
echo ""

TOTAL_EXPERIMENTS=$((${#SCENARIOS[@]} * ${#ALGORITHMS[@]} * ${#SEEDS[@]}))
CURRENT_EXPERIMENT=0

for scenario in "${SCENARIOS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        for seed in "${SEEDS[@]}"; do
            CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))

            echo -e "${GREEN}[${CURRENT_EXPERIMENT}/${TOTAL_EXPERIMENTS}]${NC} Running: ${YELLOW}${scenario}${NC} | Algorithm: ${YELLOW}${algorithm}${NC} | Seed: ${seed}"

            # Set timeout based on scenario
            if [ "$scenario" = "realtime" ]; then
                TIMEOUT="5"
            elif [ "$scenario" = "massive" ]; then
                TIMEOUT="20"
            elif [ "$scenario" = "tiny_optimal" ]; then
                TIMEOUT="60"
            elif [ "$scenario" = "meta_sweet_spot" ]; then
                TIMEOUT="120"
            else
                TIMEOUT="30"
            fi

            # Run experiment
            python main.py \
                --config-name="main_tree_${scenario}" \
                solver.solver_name="${algorithm}" \
                solver.max_time_in_seconds="${TIMEOUT}" \
                experiment.seed="${seed}" \
                experiment.run_id="${algorithm}_${scenario}_seed_${seed}" \
                logger.experiment_name="${scenario}_experiment" \
                2>&1 | tee -a "edge_case_experiments.log"

            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Success${NC}"
            else
                echo -e "${RED}✗ Failed${NC}"
            fi
            echo ""
        done
    done
done

echo "=========================================="
echo -e "${GREEN}All edge-case experiments completed!${NC}"
echo "=========================================="
echo "Log file: edge_case_experiments.log"
echo ""
echo "Next steps:"
echo "1. Run: python xgboost_selector/data_aggregator.py"
echo "2. Run: python xgboost_selector/xgboost_trainer.py"
echo "3. Check new class distribution and feature importance"
