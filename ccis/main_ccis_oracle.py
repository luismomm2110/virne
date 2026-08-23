"""
Ponto de entrada para a execução do oráculo guloso.

Uso:
    python ccis/main_ccis_oracle.py --config-name=main_tree_ccis_oracle experiment.seed=0
    python ccis/main_ccis_oracle.py --config-name=main_fat_tree_ccis_oracle experiment.seed=0

Para validar o mecanismo com um custo reduzido antes de uma execução completa,
restrinja o conjunto de candidatos e o número de requisições:

    python ccis/main_ccis_oracle.py --config-name=main_tree_ccis_oracle \
        'solver.oracle_candidates=[pl_rank,rw_rank_bfs,d_round]' \
        v_sim_setting.num_v_nets=20

Observação sobre a rede física: este roteiro não zera a capacidade de
processamento dos comutadores. Os roteiros existentes em
``apresentacao/algoritmos/`` alteram ``system.env.p_net`` após a construção do
sistema, mas ``BaseEnvironment.__init__`` já copiou a rede em ``init_p_net`` e
``reset()`` a restaura a partir dessa cópia antes da primeira requisição, de
modo que a alteração é descartada. As linhas de base já produzidas, portanto,
foram obtidas sem comutadores dedicados exclusivamente ao roteamento, e o
oráculo reproduz a mesma condição para que a comparação seja legítima.
"""

import os
import sys

import hydra
from omegaconf import DictConfig

# Permite a execução direta do arquivo, sem instalação do pacote.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from virne.system import BaseSystem
from virne.utils.config import add_simulation_into_config, generate_run_id

# A importação registra 'greedy_oracle' no SolverRegistry.
import ccis.solver  # noqa: F401


@hydra.main(version_base=None, config_path='settings', config_name='main_tree_ccis_oracle')
def run(config: DictConfig) -> None:
    print(f"\n{'-' * 20}    Oráculo Guloso    {'-' * 20}\n")
    print(f'Topologia: {config.p_net_setting.topology.type}')
    print(f'Semente: {config.experiment.seed}')
    print(f'Candidatos: {list(config.solver.oracle_candidates)}')

    if config.experiment.run_id == 'auto':
        config.experiment.run_id = generate_run_id()
    add_simulation_into_config(config)

    system = BaseSystem.from_config(config)
    system.run()

    print(f"\n{'-' * 20}      Concluído       {'-' * 20}\n")


if __name__ == '__main__':
    run()
