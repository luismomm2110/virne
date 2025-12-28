#!/bin/bash

# Large Topology Experiments
# Tests how algorithm selection changes with physical network size
#
# Topologies tested:
#   Small:  Tree (16 hosts),  Fat-Tree k=4 (16 hosts)   - BASELINE
#   Medium: Tree (64 hosts),  Fat-Tree k=6 (54 hosts)
#   Large:  Tree (128 hosts), Fat-Tree k=8 (128 hosts)
#   XLarge: Fat-Tree k=10 (250 hosts)
#
# Expected behavior:
#   - MIP becomes less viable as topology grows (timeout)
#   - MCTS struggles with large search space
#   - GA/SA sweet spot on medium-large topologies
#   - PL-Rank, RW-Rank-BFS dominate on very large topologies

set -e

ALGORITHMS=("mip" "ga_meta" "mcts" "sa_meta" "pl_rank" "rw_rank_bfs" "r_round")
SEEDS=(0 1 2 3 4)

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "LARGE TOPOLOGY EXPERIMENT SUITE"
echo "=========================================="
echo ""

# ============================================
# MEDIUM TREE (64 hosts, 127 total nodes)
# ============================================
echo -e "${BLUE}=========================================="
echo "MEDIUM TREE TOPOLOGY (64 hosts)"
echo -e "==========================================${NC}"

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        echo -e "${GREEN}Running:${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) on Medium Tree"

        # Adjust timeout based on algorithm
        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=120  # MIP needs more time on larger topology
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=120
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=90
        else
            TIMEOUT=60  # Heuristics still fast
        fi

        python main.py \
            --config-name="main" \
            p_net_setting=medium_tree_p_net \
            v_sim_setting=v_sim_200_requests \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_medium_tree_seed_${seed}" \
            logger.experiment_name="medium_tree_experiment"

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
        echo -e "${GREEN}Running:${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) on Large Tree"

        # MIP likely to timeout on many VNRs
        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=180  # Even more time, but may still timeout
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=150
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=120
        else
            TIMEOUT=90
        fi

        python main.py \
            --config-name="main" \
            p_net_setting=large_tree_p_net \
            v_sim_setting=v_sim_200_requests \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_large_tree_seed_${seed}" \
            logger.experiment_name="large_tree_experiment"

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
        echo -e "${GREEN}Running:${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) on Medium Fat-Tree"

        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=120
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=120
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=90
        else
            TIMEOUT=60
        fi

        python main.py \
            --config-name="main" \
            p_net_setting=medium_fat_tree_p_net \
            v_sim_setting=v_sim_200_requests \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_medium_fat_tree_seed_${seed}" \
            logger.experiment_name="medium_fat_tree_experiment"

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
        echo -e "${GREEN}Running:${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) on Large Fat-Tree"

        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=180
        elif [ "$algorithm" = "ga_meta" ] || [ "$algorithm" = "sa_meta" ]; then
            TIMEOUT=150
        elif [ "$algorithm" = "mcts" ]; then
            TIMEOUT=120
        else
            TIMEOUT=90
        fi

        python main.py \
            --config-name="main" \
            p_net_setting=large_fat_tree_p_net \
            v_sim_setting=v_sim_200_requests \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_large_fat_tree_seed_${seed}" \
            logger.experiment_name="large_fat_tree_experiment"

        echo ""
    done
done

# ============================================
# VERY LARGE FAT-TREE (k=10: 250 hosts)
# ============================================
echo -e "${BLUE}=========================================="
echo "VERY LARGE FAT-TREE TOPOLOGY (k=10, 250 hosts)"
echo -e "==========================================${NC}"
echo "WARNING: MIP will likely timeout on most VNRs"
echo ""

for seed in "${SEEDS[@]}"; do
    for algorithm in "${ALGORITHMS[@]}"; do
        echo -e "${GREEN}Running:${NC} ${YELLOW}${algorithm}${NC} (seed ${seed}) on Very Large Fat-Tree"

        if [ "$algorithm" = "mip" ]; then
            TIMEOUT=300  # 5 minutes, but likely to timeout anyway
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
            v_sim_setting=v_sim_200_requests \
            solver.solver_name="${algorithm}" \
            solver.max_time_in_seconds="${TIMEOUT}" \
            experiment.seed="${seed}" \
            experiment.run_id="${algorithm}_very_large_fat_tree_seed_${seed}" \
            logger.experiment_name="very_large_fat_tree_experiment"

        echo ""
    done
done

echo "=========================================="
echo -e "${GREEN}All large topology experiments completed!${NC}"
echo "=========================================="
echo ""
echo "Topologies tested:"
echo "  - Medium Tree: 64 hosts (127 total nodes)"
echo "  - Large Tree: 128 hosts (255 total nodes)"
echo "  - Medium Fat-Tree k=6: 54 hosts (99 total nodes)"
echo "  - Large Fat-Tree k=8: 128 hosts (208 total nodes)"
echo "  - Very Large Fat-Tree k=10: 250 hosts (375 total nodes)"
echo ""
echo "Next steps:"
echo "1. Run: python xgboost_selector/data_aggregator.py"
echo "2. Check how 'p_net_size' feature importance changes"
echo "3. Expect shift: MIP/MCTS down, PL-Rank/GA up on large nets"
