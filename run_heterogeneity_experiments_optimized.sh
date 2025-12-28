#!/bin/bash

# OPTIMIZED Demand Heterogeneity Experiments (Plan A)
# Optimizations:
#   - 3 seeds instead of 5 (40% reduction)
#   - 700 VNRs instead of 1000 (configured in YAML)
#   - Smart MIP timeouts based on scenario complexity
# Total: 3 scenarios × 7 algorithms × 3 seeds = 63 experiments (vs 105 original)
# Estimated time: ~8-10 hours (vs ~15-20 hours)
#
# Tests how VNR demand variation affects algorithm selection:
#   - Uniform Homogeneous (narrow 10-20x variation): Heuristics dominate
#   - Extreme Heterogeneous (100-200x variation): GA/SA/MIP dominate
#   - Bimodal (light + heavy, no middle): Mixed strategies

set -e

ALGORITHMS=("mip" "ga_meta" "mcts" "sa_meta" "pl_rank" "rw_rank_bfs" "r_round")
# OPTIMIZED: 3 seeds instead of 5
SEEDS=(0 1 2)

SCENARIOS=(
    "uniform_homogeneous"
    "extreme_heterogeneous"
    "bimodal_demands"
)

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

TOTAL_EXPERIMENTS=$((${#SCENARIOS[@]} * ${#ALGORITHMS[@]} * ${#SEEDS[@]}))

echo "=========================================="
echo "OPTIMIZED DEMAND HETEROGENEITY EXPERIMENTS"
echo "=========================================="
echo -e "${BLUE}Optimizations Applied:${NC}"
echo "  • Seeds: 3 (reduced from 5)"
echo "  • VNRs: 700 (reduced from 1000, set in YAML)"
echo "  • MIP smart timeouts (15-30 min)"
echo ""
echo "Scenarios: ${#SCENARIOS[@]}"
echo "Algorithms: ${#ALGORITHMS[@]}"
echo "Total experiments: ${TOTAL_EXPERIMENTS} (vs 105 original)"
echo "Estimated time savings: ~55-60%"
echo ""
echo -e "${YELLOW}Goal:${NC} Test how demand variation affects algorithm selection"
echo "  • Homogeneous (10-20x): Expect heuristics to dominate"
echo "  • Heterogeneous (100-200x): Expect GA/SA/MIP to dominate"
echo "  • Bimodal: Expect mixed strategies"
echo "=========================================="
echo ""

CURRENT_EXPERIMENT=0

# ============================================
# UNIFORM HOMOGENEOUS (Control scenario)
# ============================================
echo -e "${BLUE}=========================================="
echo "UNIFORM HOMOGENEOUS (Narrow variation)"
echo "Node: 15-25 CPU, Link: 40-60 BW"
echo -e "==========================================${NC}"
echo "Expected: Heuristics (PL-Rank, RW-Rank-BFS) should dominate"
echo ""

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))
        echo -e "${GREEN}[${CURRENT_EXPERIMENT}/${TOTAL_EXPERIMENTS}]${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) - Homogeneous"

        # MIP should solve homogeneous quickly
        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=900  # 15 min (homogeneous is easier for MIP)
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=60
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=45
        else
            TIMEOUT=30  # Heuristics fast
        fi

        python main.py \
            --config-name="main" \
            p_net_setting=tree_p_net_setting \
            v_sim_setting=v_sim_uniform_homogeneous \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_homogeneous_seed_${seed}" \
            logger.experiment_name="heterogeneity_experiments_optimized" \
            2>&1 | tee -a "heterogeneity_experiments_optimized.log"

        echo ""
    done
done

# ============================================
# EXTREME HETEROGENEOUS (Challenging)
# ============================================
echo -e "${BLUE}=========================================="
echo "EXTREME HETEROGENEOUS (100-200x variation)"
echo "Node: 1-100 CPU, Link: 1-200 BW"
echo -e "==========================================${NC}"
echo "Expected: GA/SA/MIP should dominate (global optimization needed)"
echo ""

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))
        echo -e "${GREEN}[${CURRENT_EXPERIMENT}/${TOTAL_EXPERIMENTS}]${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) - Heterogeneous"

        # MIP needs more time on heterogeneous
        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=1800  # 30 min (heterogeneity is harder)
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=120
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=90
        else
            TIMEOUT=60
        fi

        python main.py \
            --config-name="main" \
            p_net_setting=tree_p_net_setting \
            v_sim_setting=v_sim_extreme_heterogeneous \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_heterogeneous_seed_${seed}" \
            logger.experiment_name="heterogeneity_experiments_optimized" \
            2>&1 | tee -a "heterogeneity_experiments_optimized.log"

        echo ""
    done
done

# ============================================
# BIMODAL DEMANDS (Mixed: light + heavy)
# ============================================
echo -e "${BLUE}=========================================="
echo "BIMODAL DEMANDS (Light + Heavy, no middle)"
echo "Two clusters: (1-20, 10-40) and (80-100, 150-200)"
echo -e "==========================================${NC}"
echo "Expected: GA/PL-Rank mixed (bimodal structure)"
echo ""

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))
        echo -e "${GREEN}[${CURRENT_EXPERIMENT}/${TOTAL_EXPERIMENTS}]${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) - Bimodal"

        # Bimodal complexity between homogeneous and extreme
        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=1200  # 20 min
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=90
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=60
        else
            TIMEOUT=45
        fi

        python main.py \
            --config-name="main" \
            p_net_setting=tree_p_net_setting \
            v_sim_setting=v_sim_bimodal_demands \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_bimodal_seed_${seed}" \
            logger.experiment_name="heterogeneity_experiments_optimized" \
            2>&1 | tee -a "heterogeneity_experiments_optimized.log"

        echo ""
    done
done

echo "=========================================="
echo -e "${GREEN}All optimized heterogeneity experiments completed!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}Time Savings Summary:${NC}"
echo "  • Experiments: 63 (vs 105 original) = 40% reduction"
echo "  • With 700 VNRs: Additional 30% time reduction"
echo "  • Smart MIP timeouts: Saves 10-20%"
echo "  • Combined: ~55-60% total time saved"
echo ""
echo "Log file: heterogeneity_experiments_optimized.log"
echo ""
echo -e "${YELLOW}Expected Insights:${NC}"
echo "  1. New feature 'demand_heterogeneity' (CV) becomes important (8-12% importance)"
echo "  2. Algorithm selection shifts based on variation:"
echo "     - Homogeneous (CV < 1.0): Heuristics 60-70%"
echo "     - Heterogeneous (CV > 3.0): GA/SA 50-60%"
echo "     - Bimodal: Mixed strategies"
echo "  3. First work to study demand heterogeneity in VNE algorithm selection"
echo ""
echo "Next steps:"
echo "1. Run: python xgboost_selector/data_aggregator.py"
echo "2. Run: python xgboost_selector/xgboost_trainer.py"
echo "3. Check 'demand_heterogeneity' feature importance (expect 8-12%)"
echo "4. Analyze how algorithm distribution changes across scenarios"
echo ""
