#!/usr/bin/env python3
"""VNE Experiment: SATURATION Scenario with RW-Rank-BFS Solver"""

import hydra
from omegaconf import DictConfig
from virne.system import BaseSystem

@hydra.main(version_base=None, config_path='settings', config_name='main_tree_saturation')
def main(config: DictConfig):
    config.solver.solver_name = 'rw_rank_bfs'
    config.logger.experiment_name = f'rw_rank_bfs_saturation_seed_{config.experiment.seed}'
    config.experiment.run_id = f'rw_rank_bfs_saturation_seed_{config.experiment.seed}'

    system = BaseSystem.from_config(config)
    system.run()

if __name__ == '__main__':
    main()