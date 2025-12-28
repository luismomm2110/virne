"""
GA-Meta experiments on Waxman 16-node random topology.

Usage:
    python main_waxman_16_ga_meta.py experiment.seed=0
"""

import hydra
from omegaconf import DictConfig
from virne.system import BaseSystem
from virne.utils.config import add_simulation_into_config, generate_run_id


@hydra.main(version_base=None, config_path="settings", config_name="main_waxman_16_ga_meta")
def run(config: DictConfig):
    print(f"\n{'-' * 20}    Start     {'-' * 20}\n")
    print("Running GA-Meta solver on Waxman 16-node random topology")
    print(f"Seed: {config.experiment.seed}")
    print(f"Solver: {config.solver.solver_name}")

    if config.experiment.run_id == 'auto':
        config.experiment.run_id = generate_run_id()
    add_simulation_into_config(config)

    system = BaseSystem.from_config(config)
    system.run()

    print(f"\n{'-' * 20}   Complete   {'-' * 20}\n")


if __name__ == '__main__':
    run()
