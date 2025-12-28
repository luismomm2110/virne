#!/usr/bin/env python3
"""
VNE Experiment: SATURATION Scenario with MIP Solver
Large VNRs (15-30 nodes) with high resource demands to saturate the network
Tests algorithm performance under extreme resource contention
"""

import hydra
from omegaconf import DictConfig
from virne.system import BaseSystem
from virne.utils.config import add_simulation_into_config, generate_run_id

@hydra.main(version_base=None, config_path='settings', config_name='main_tree_saturation')
def main(config: DictConfig):
    # Override solver to MIP
    config.solver.solver_name = 'mip'
    config.logger.experiment_name = f'mip_saturation_seed_{config.experiment.seed}'
    config.experiment.run_id = f'mip_saturation_seed_{config.experiment.seed}'

    print("\n" + "="*80)
    print("VNE SATURATION SCENARIO - MIP SOLVER")
    print("="*80)
    print(f"Seed: {config.experiment.seed}")
    print(f"VNR Size: 15-30 nodes")
    print(f"Node CPU Demand: 20-60 units")
    print(f"Link BW Demand: 40-150 units")
    print(f"Physical Network: 16-node tree, CPU [50-100], BW [200-400]")
    print(f"Timeout: 10 seconds per VNR")
    print("Expected: <5% acceptance rate (extreme saturation)")
    print("="*80 + "\n")

    # Configure run ID and simulation
    if config.experiment.run_id == 'auto':
        config.experiment.run_id = generate_run_id()
    add_simulation_into_config(config)

    system = BaseSystem.from_config(config)
    system.run()

if __name__ == '__main__':
    main()
