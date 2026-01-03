#!/bin/bash
# Script para executar extract_feature_importance_per_topology.py
# Tenta usar o ambiente conda virne se disponível

cd "$(dirname "$0")"

# Tentar ativar conda se disponível
if command -v conda &> /dev/null; then
    echo "Tentando ativar ambiente conda 'virne'..."
    eval "$(conda shell.bash hook)"
    conda activate virne 2>/dev/null || {
        echo "Ambiente virne não encontrado. Tentando usar python3 diretamente..."
    }
fi

# Executar o script
python3 extract_feature_importance_per_topology.py

