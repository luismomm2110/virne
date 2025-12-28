#!/bin/bash

# OPTIMIZED Large Topology Experiments (Plan A)
# Optimizations:
#   - 3 seeds instead of 5 (40% reduction)
#   - 700 VNRs instead of 1000 (configured in YAML)
#   - Reduced MIP timeouts on large topologies (10-15 min max)
# Total: 5 topologies × 7 algorithms × 3 seeds = 105 experiments (vs 175 original)
# Estimated time: ~15-20 hours (vs ~40-50 hours)

set -e

ALGORITHMS=("mip" "ga_meta" "mcts" "sa_meta" "pl_rank" "rw_rank_bfs" "r_round")
# OPTIMIZED: 3 seeds instead of 5
SEEDS=(0 1 2)

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "OPTIMIZED LARGE TOPOLOGY EXPERIMENT SUITE"
echo "=========================================="
echo -e "${BLUE}Optimizations Applied:${NC}"
echo "  • Seeds: 3 (reduced from 5)"
echo "  • VNRs: 700 (reduced from 1000, set in YAML)"
echo "  • MIP timeouts: 10-15 min max on large topologies"
echo ""
echo "Total experiments: 105 (vs 175 original)"
echo "Estimated time savings: ~60%"
echo "=========================================="
echo ""

TOTAL_EXPERIMENTS=$((5 * ${#ALGORITHMS[@]} * ${#SEEDS[@]}))
CURRENT_EXPERIMENT=0

# ============================================
# MEDIUM TREE (64 hosts, 127 total nodes)
# ============================================
echo -e "${BLUE}=========================================="
echo "MEDIUM TREE TOPOLOGY (64 hosts)"
echo -e "==========================================${NC}"

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))
        echo -e "${GREEN}[${CURRENT_EXPERIMENT}/${TOTAL_EXPERIMENTS}]${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) on Medium Tree"

        # Adjust timeout based on algorithm
        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=900  # 15 min for MIP (reduced from original)
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=120
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=90
        else
            TIMEOUT=60  # Heuristics still fast
        fi

        python main.py \
            --config-name="main_medium_tree_ga" \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_medium_tree_seed_${seed}" \
            logger.experiment_name="medium_tree_experiment_optimized" \
            2>&1 | tee -a "large_topology_optimized.log"

        echo ""
    done
done

# ============================================
# LARGE TREE (128 hosts, 255 total nodes)
# ============================================
echo -e "${BLUE}=========================================="
echo "LARGE TREE TOPOLOGY (128 hosts)"
echo -e "==========================================${NC}"

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))
        echo -e "${GREEN}[${CURRENT_EXPERIMENT}/${TOTAL_EXPERIMENTS}]${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) on Large Tree"

        # MIP gets aggressive timeout on large topology
        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=900  # 15 min max (likely to timeout, but we capture that)
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=150
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=120
        else
            TIMEOUT=90
        fi

        python main.py \
            --config-name="main_large_tree_ga" \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_large_tree_seed_${seed}" \
            logger.experiment_name="large_tree_experiment_optimized" \
            2>&1 | tee -a "large_topology_optimized.log"

        echo ""
    done
done

# ============================================
# MEDIUM FAT-TREE (k=6: 54 hosts, 99 total)
# ============================================
echo -e "${BLUE}=========================================="
echo "MEDIUM FAT-TREE TOPOLOGY (k=6, 54 hosts)"
echo -e "==========================================${NC}"

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))
        echo -e "${GREEN}[${CURRENT_EXPERIMENT}/${TOTAL_EXPERIMENTS}]${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) on Medium Fat-Tree"

        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=900  # 15 min
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=120
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=90
        else
            TIMEOUT=60
        fi

        python main.py \
            --config-name="main_medium_fat_tree_ga" \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_medium_fat_tree_seed_${seed}" \
            logger.experiment_name="medium_fat_tree_experiment_optimized" \
            2>&1 | tee -a "large_topology_optimized.log"

        echo ""
    done
done

# ============================================
# LARGE FAT-TREE (k=8: 128 hosts, 208 total)
# ============================================
echo -e "${BLUE}=========================================="
echo "LARGE FAT-TREE TOPOLOGY (k=8, 128 hosts)"
echo -e "==========================================${NC}"

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))
        echo -e "${GREEN}[${CURRENT_EXPERIMENT}/${TOTAL_EXPERIMENTS}]${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) on Large Fat-Tree"

        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=900  # 15 min (will timeout often)
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=150
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=120
        else
            TIMEOUT=90
        fi

        python main.py \
            --config-name="main_large_fat_tree_ga" \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_large_fat_tree_seed_${seed}" \
            logger.experiment_name="large_fat_tree_experiment_optimized" \
            2>&1 | tee -a "large_topology_optimized.log"

        echo ""
    done
done

# ============================================
# VERY LARGE FAT-TREE (k=10: 250 hosts)
# ============================================
echo -e "${BLUE}=========================================="
echo "VERY LARGE FAT-TREE TOPOLOGY (k=10, 250 hosts)"
echo -e "==========================================${NC}"
echo -e "${RED}NOTE: MIP will timeout on most VNRs (this is expected data)${NC}"
echo ""

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))
        echo -e "${GREEN}[${CURRENT_EXPERIMENT}/${TOTAL_EXPERIMENTS}]${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) on Very Large Fat-Tree"

        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=600  # 10 min (will timeout on most, but that's valuable data)
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=180
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=150
        else
            TIMEOUT=90
        fi

        python main.py \
            --config-name="main" \
            p_net_setting=very_large_fat_tree_p_net \
            v_sim_setting=v_sim_700_requests \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_very_large_fat_tree_seed_${seed}" \
            logger.experiment_name="very_large_fat_tree_experiment_optimized" \
            2>&1 | tee -a "large_topology_optimized.log"

        echo ""
    done
done

echo "=========================================="
echo -e "${GREEN}All optimized large topology experiments completed!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}Time Savings Summary:${NC}"
echo "  • Experiments: 105 (vs 175 original) = 40% reduction"
echo "  • With 700 VNRs: Additional 30% time reduction"
echo "  • MIP timeouts: Saves 20-30% on large topologies"
echo "  • Combined: ~60% total time saved"
echo ""
echo "Topologies tested:"
echo "  - Medium Tree: 64 hosts (127 total nodes)"
echo "  - Large Tree: 128 hosts (255 total nodes)"
echo "  - Medium Fat-Tree k=6: 54 hosts (99 total nodes)"
echo "  - Large Fat-Tree k=8: 128 hosts (208 total nodes)"
echo "  - Very Large Fat-Tree k=10: 250 hosts (375 total nodes)"
echo ""
echo "Log file: large_topology_optimized.log"
echo ""
echo "Next steps:"
echo "1. Run: python xgboost_selector/data_aggregator.py"
echo "2. Check how 'p_net_size' feature importance changes"
echo "3. Expect shift: MIP/MCTS down, PL-Rank/GA up on large nets"
echo ""