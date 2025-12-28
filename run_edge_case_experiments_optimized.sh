#!/bin/bash

# OPTIMIZED Edge-Case Experiments (Plan A)
# Optimizations:
#   - 3 seeds instead of 5 (40% time reduction)
#   - 700 VNRs instead of 1000 (configured in YAML files)
#   - Aggressive MIP timeouts on complex scenarios (10-15 min max)
# Total: 6 scenarios × 7 algorithms × 3 seeds = 126 experiments (vs 210 original)
# Estimated time: ~15-18 hours (vs ~30-40 hours)

set -e  # Exit on error

# All algorithms (MIP included with smart timeouts)
ALGORITHMS=("mip" "ga_meta" "mcts" "sa_meta" "pl_rank" "rw_rank_bfs" "r_round")

SCENARIOS=(
    "ultra_tight"
    "massive"
    "realtime"
    "tiny_optimal"
    "meta_sweet_spot"
    "sparse_congested"
)

# OPTIMIZED: 3 seeds instead of 5
SEEDS=(0 1 2)

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Calculate total experiments
TOTAL_EXPERIMENTS=$((${#SCENARIOS[@]} * ${#ALGORITHMS[@]} * ${#SEEDS[@]}))

echo "=========================================="
echo "OPTIMIZED EDGE-CASE EXPERIMENT SUITE"
echo "=========================================="
echo -e "${BLUE}Optimizations Applied:${NC}"
echo "  • Seeds: 3 (reduced from 5)"
echo "  • VNRs: 700 (reduced from 1000, set in YAML)"
echo "  • MIP aggressive timeouts: 10-15 min on complex scenarios"
echo ""
echo "Scenarios: ${#SCENARIOS[@]}"
echo "Algorithms: ${#ALGORITHMS[@]} (all included)"
echo "Total experiments: ${TOTAL_EXPERIMENTS} (vs 210 original)"
echo "Estimated time savings: ~55-60%"
echo "=========================================="
echo ""

CURRENT_EXPERIMENT=0

for scenario in "${SCENARIOS[@]}"; do
    echo -e "${YELLOW}Scenario: ${scenario}${NC}"

    for algorithm in "${ALGORITHMS[@]}"; do
        for seed in "${SEEDS[@]}"; do
            CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))

            echo -e "${GREEN}[${CURRENT_EXPERIMENT}/${TOTAL_EXPERIMENTS}]${NC} Running: ${YELLOW}${scenario}${NC} | Algorithm: ${YELLOW}${algorithm}${NC} | Seed: ${seed}"

            # Set timeout based on scenario AND algorithm
            # MIP gets shorter timeouts on complex scenarios
            if [ "$algorithm" = "mip" ]; then
                case "$scenario" in
                    "realtime")
                        TIMEOUT="300"  # 5 min for MIP
                        ;;
                    "massive")
                        TIMEOUT="600"  # 10 min for MIP (complex)
                        ;;
                    "sparse_congested")
                        TIMEOUT="900"  # 15 min for MIP (complex)
                        ;;
                    "tiny_optimal")
                        TIMEOUT="1800" # 30 min for MIP (optimal scenario)
                        ;;
                    "meta_sweet_spot")
                        TIMEOUT="2400" # 40 min for MIP (sweet spot)
                        ;;
                    "ultra_tight")
                        TIMEOUT="900"  # 15 min for MIP
                        ;;
                    *)
                        TIMEOUT="1800" # 30 min default for MIP
                        ;;
                esac
            else
                # Non-MIP algorithms use original timeouts
                case "$scenario" in
                    "realtime")
                        TIMEOUT="5"
                        ;;
                    "massive")
                        TIMEOUT="20"
                        ;;
                    "tiny_optimal")
                        TIMEOUT="60"
                        ;;
                    "meta_sweet_spot")
                        TIMEOUT="120"
                        ;;
                    *)
                        TIMEOUT="30"
                        ;;
                esac
            fi

            # Run experiment
            python main.py \
                --config-name="main_tree_${scenario}" \
                solver.solver_name="${algorithm}" \
                solver.max_time_in_seconds="${TIMEOUT}" \
                experiment.seed="${seed}" \
                experiment.run_id="${algorithm}_${scenario}_seed_${seed}" \
                logger.experiment_name="${scenario}_experiment_optimized" \
                2>&1 | tee -a "edge_case_experiments_optimized.log"

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
echo -e "${GREEN}All optimized edge-case experiments completed!${NC}"
echo "=========================================="
echo "Log file: edge_case_experiments_optimized.log"
echo ""
echo -e "${BLUE}Time Savings Summary:${NC}"
echo "  • Experiments: 126 (vs 210 original) = 40% reduction"
echo "  • With 700 VNRs: Additional 30% time reduction"
echo "  • MIP timeouts: Saves 20-30% on complex scenarios"
echo "  • Combined: ~55-60% total time saved"
echo ""
echo "Next steps:"
echo "1. Run: python xgboost_selector/data_aggregator.py"
echo "2. Run: python xgboost_selector/xgboost_trainer.py"
echo "3. Check new class distribution and feature importance"
echo ""