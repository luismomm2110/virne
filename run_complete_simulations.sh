#!/bin/bash
# Script COMPLETO para rodar todas simulações em Tree e Fat-Tree
# Para treinar XGBoost com dados completos
#
# Total: 8 algoritmos × 2 topologias × 5 seeds = 80 simulações
# Tempo estimado: 4-8 horas

set -e  # Exit on error

echo "=========================================================================="
echo "SIMULAÇÕES COMPLETAS PARA TREINAMENTO XGBOOST"
echo "=========================================================================="
echo ""
echo "Configuração:"
echo "  - Topologias: Tree, Fat-Tree"
echo "  - Algoritmos: 8 (GA, MIP, MCTS, SA, PL_Rank, RW_Rank_BFS, D_Round, R_Round)"
echo "  - Seeds: 5 (0-4)"
echo "  - VNRs por simulação: 200"
echo "  - Total de simulações: 80"
echo ""

# Criar diretórios
mkdir -p logs
mkdir -p results

# Backup de dados antigos
if [ -f "vnr_aggregated_data.csv" ]; then
    echo "📦 Fazendo backup de dados antigos..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    mv vnr_aggregated_data.csv "vnr_aggregated_data_backup_${timestamp}.csv"
    echo "   Backup salvo: vnr_aggregated_data_backup_${timestamp}.csv"
fi

# Configurações
NUM_VNRS=200
SEEDS=(0 1 2 3 4)

# Algoritmos e seus scripts
declare -A TREE_SCRIPTS=(
    ["ga_meta"]="main_tree_ga.py"
    ["mip"]="main_tree_mip.py"
    ["mcts"]="main_tree_mcts.py"
    ["sa_meta"]="main_tree_sa.py"
    ["pl_rank"]="main_tree_pl_rank.py"
    ["rw_rank_bfs"]="main_tree_rw_rank_bfs.py"
    ["d_round"]="main_tree_drounding.py"
    ["r_round"]="main_tree_drounding.py"
)

declare -A FAT_TREE_SCRIPTS=(
    ["ga_meta"]="main_fat_tree_ga.py"
    ["mip"]="main_fat_tree_mip.py"
    ["mcts"]="main_fat_tree_mcts.py"
    ["sa_meta"]="main_fat_tree_sa.py"
    ["pl_rank"]="main_fat_tree_pl_rank.py"
    ["rw_rank_bfs"]="main_fat_tree_rw_rank_bfs.py"
    ["d_round"]="main_fat_tree_drounding.py"
    ["r_round"]="main_fat_tree_drounding.py"
)

# Topologias
TOPOLOGIES=("tree" "fat_tree")

# Contador
TOTAL_SIMS=$((${#TREE_SCRIPTS[@]} * ${#TOPOLOGIES[@]} * ${#SEEDS[@]}))
CURRENT=0
START_TIME=$(date +%s)

# Função para calcular tempo decorrido
function elapsed_time() {
    local current=$(date +%s)
    local elapsed=$((current - START_TIME))
    local hours=$((elapsed / 3600))
    local mins=$(((elapsed % 3600) / 60))
    local secs=$((elapsed % 60))
    printf "%02d:%02d:%02d" $hours $mins $secs
}

# Rodar simulações
for TOPO in "${TOPOLOGIES[@]}"; do
    echo ""
    echo "=========================================================================="
    echo "TOPOLOGIA: ${TOPO^^}"
    echo "=========================================================================="

    # Definir configurações baseadas na topologia
    if [ "$TOPO" == "tree" ]; then
        P_NET_SETTING="tree_p_net_setting"
        V_SIM_SETTING="v_sim_setting"
        declare -n SCRIPTS=TREE_SCRIPTS
    else
        P_NET_SETTING="fat_tree_p_net_setting"
        V_SIM_SETTING="v_sim_setting"
        declare -n SCRIPTS=FAT_TREE_SCRIPTS
    fi

    for ALGO in "${!SCRIPTS[@]}"; do
        SCRIPT="${SCRIPTS[$ALGO]}"

        # Verificar se script existe
        if [ ! -f "$SCRIPT" ]; then
            echo "⚠ AVISO: Script não encontrado: $SCRIPT (pulando $ALGO em $TOPO)"
            continue
        fi

        for SEED in "${SEEDS[@]}"; do
            CURRENT=$((CURRENT + 1))
            PROGRESS=$((CURRENT * 100 / TOTAL_SIMS))

            echo ""
            echo "[$CURRENT/$TOTAL_SIMS - ${PROGRESS}%] [$(elapsed_time)] $TOPO :: $ALGO (seed=$SEED)"
            echo "----------------------------------------"

            LOG_FILE="logs/${TOPO}_${ALGO}_seed${SEED}.log"

            # Executar simulação
            python "$SCRIPT" \
                p_net_setting="$P_NET_SETTING" \
                v_sim_setting="$V_SIM_SETTING" \
                solver.solver_name="$ALGO" \
                experiment.seed=$SEED \
                experiment.num_vnrs=$NUM_VNRS \
                > "$LOG_FILE" 2>&1

            # Verificar sucesso
            if [ $? -eq 0 ]; then
                echo "✓ Concluído"
            else
                echo "✗ ERRO! Ver log: $LOG_FILE"
                # Continuar mesmo com erro
            fi
        done
    done
done

echo ""
echo "=========================================================================="
echo "TODAS SIMULAÇÕES CONCLUÍDAS!"
echo "=========================================================================="
echo "Tempo total: $(elapsed_time)"
echo ""

# Validar dados
echo "Validando dados coletados..."
if [ -f "vnr_aggregated_data.csv" ]; then
    python validate_simulation_data.py --data-file vnr_aggregated_data.csv

    echo ""
    echo "=========================================================================="
    echo "PRÓXIMOS PASSOS"
    echo "=========================================================================="
    echo ""
    echo "1. Limpar dados:"
    echo "   python -c \"
import pandas as pd
df = pd.read_csv('vnr_aggregated_data.csv')
df = df[df['event_type'] == 1]
df['uid'] = df['v_net_id'].astype(str) + '_' + df['seed'].astype(str) + '_' + df['event_time'].astype(str) + '_' + df['algorithm']
df_clean = df.drop_duplicates(subset='uid', keep='first')
df_clean.to_csv('vnr_aggregated_data_clean.csv', index=False)
print(f'Limpeza: {len(df):,} → {len(df_clean):,} registros')
\""
    echo ""
    echo "2. Filtrar VNRs completas (8 algoritmos):"
    echo "   python -c \"
import pandas as pd
df = pd.read_csv('vnr_aggregated_data_clean.csv')
df['vnr_uid'] = df['v_net_id'].astype(str) + '_' + df['seed'].astype(str) + '_' + df['event_time'].astype(str)
vnr_counts = df.groupby('vnr_uid').size()
complete_vnrs = vnr_counts[vnr_counts == 8].index
df_complete = df[df['vnr_uid'].isin(complete_vnrs)]
df_complete.to_csv('vnr_complete_data.csv', index=False)
print(f'VNRs completas: {len(complete_vnrs):,} ({len(df_complete):,} registros)')
\""
    echo ""
    echo "3. Treinar XGBoost:"
    echo "   python train_xgboost_v2.py --score-config acceptance_only --data-file vnr_complete_data.csv"
    echo ""
    echo "4. Comparar resultados:"
    echo "   python compare_xgboost_v2.py --data-file vnr_complete_data.csv"
    echo ""
else
    echo "⚠ AVISO: Arquivo vnr_aggregated_data.csv não encontrado!"
    echo "   Verifique se as simulações geraram os dados corretamente."
fi

echo "=========================================================================="
