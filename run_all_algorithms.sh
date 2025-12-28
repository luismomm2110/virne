#!/bin/bash
# Script para rodar todos os 8 algoritmos e coletar dados completos
# Usage: ./run_all_algorithms.sh

set -e  # Exit on error

echo "=========================================="
echo "EXECUTANDO SIMULAÇÕES - TODOS ALGORITMOS"
echo "=========================================="
echo ""

# Configurações
NUM_VNRS=200  # Número de VNRs por seed
NUM_SEEDS=5   # Seeds: 0,1,2,3,4
P_NET_SETTING="tree_p_net_setting"
V_SIM_SETTING="v_sim_setting"

# Algoritmos a executar
ALGORITHMS=(
    "ga_meta"
    "mip"
    "mcts"
    "sa_meta"
    "pl_rank"
    "rw_rank_bfs"
    "d_round"
    "r_round"
)

# Contador
TOTAL=$((${#ALGORITHMS[@]} * NUM_SEEDS))
CURRENT=0

# Rodar cada algoritmo com cada seed
for ALGO in "${ALGORITHMS[@]}"; do
    for SEED in {0..4}; do
        CURRENT=$((CURRENT + 1))

        echo ""
        echo "[$CURRENT/$TOTAL] Executando: $ALGO (seed=$SEED)"
        echo "----------------------------------------"

        # Determinar qual script usar baseado no algoritmo
        case $ALGO in
            "ga_meta")
                SCRIPT="main_tree_ga.py"
                ;;
            "mip")
                SCRIPT="main_tree_mip.py"
                ;;
            "mcts")
                SCRIPT="main_tree_mcts.py"
                ;;
            "sa_meta")
                SCRIPT="main_tree_sa.py"
                ;;
            "pl_rank")
                SCRIPT="main_tree_pl_rank.py"
                ;;
            "rw_rank_bfs")
                SCRIPT="main_tree_rw_rank_bfs.py"
                ;;
            "d_round")
                SCRIPT="main_tree_drounding.py"
                ;;
            "r_round")
                SCRIPT="main_tree_drounding.py"  # Usa mesmo script, algoritmo diferente
                ;;
        esac

        # Executar simulação
        python $SCRIPT \
            p_net_setting=$P_NET_SETTING \
            v_sim_setting=$V_SIM_SETTING \
            solver.solver_name=$ALGO \
            experiment.seed=$SEED \
            experiment.num_vnrs=$NUM_VNRS \
            2>&1 | tee -a "logs/simulation_${ALGO}_seed${SEED}.log"

        # Status
        if [ $? -eq 0 ]; then
            echo "✓ $ALGO seed=$SEED concluído"
        else
            echo "✗ $ALGO seed=$SEED falhou!"
        fi
    done
done

echo ""
echo "=========================================="
echo "TODAS SIMULAÇÕES CONCLUÍDAS!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Agregar resultados: python aggregate_results.py"
echo "2. Treinar XGBoost: python train_xgboost_v2.py --score-config acceptance_only --data-file vnr_aggregated_data.csv"
echo "3. Comparar: python compare_xgboost_v2.py"
