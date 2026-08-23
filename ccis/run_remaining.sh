#!/bin/bash
# Executa as corridas restantes do oráculo guloso de forma desacoplada do
# terminal que as dispara, de modo que o encerramento da sessão não interrompa
# o processamento.
#
# Uso:
#   setsid nohup bash ccis/run_remaining.sh > /tmp/oracle_remaining.log 2>&1 &

set -u
cd /Users/luismomm/PycharmProjects/virne || exit 1

PYTHON=/Users/luismomm/miniconda3/envs/virne/bin/python

echo "=== INICIO $(date '+%Y-%m-%d %H:%M:%S') ==="

# A opção -i do caffeinate impede a suspensão por ociosidade enquanto o
# processamento estiver em curso.
caffeinate -i "$PYTHON" ccis/run_oracle_experiments.py \
    --topologies tree --seeds 4
echo "=== TREE_SEED4_EXIT=$? $(date '+%H:%M:%S') ==="

caffeinate -i "$PYTHON" ccis/run_oracle_experiments.py \
    --topologies fat_tree --seeds 0 1 2 3 4
echo "=== FAT_TREE_EXIT=$? $(date '+%H:%M:%S') ==="

echo "=== TODAS AS CORRIDAS RESTANTES CONCLUIDAS $(date '+%Y-%m-%d %H:%M:%S') ==="
