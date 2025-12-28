#!/usr/bin/env python3
"""VNE Experiment: SATURATION Scenario with SA Solver"""

import hydra
from omegaconf import DictConfig
from virne.system import BaseSystem

@hydra.main(version_base=None, config_path='settings', config_name='main_tree_saturation')
def main(config: DictConfig):
    config.solver.solver_name = 'sa_meta'
    config.logger.experiment_name = f'sa_meta_saturation_seed_{config.experiment.seed}'
    config.experiment.run_id = f'sa_meta_saturation_seed_{config.experiment.seed}'

    system = BaseSystem.from_config(config)
    system.run()

if __name__ == '__main__':
    main()