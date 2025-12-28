"""
WX500 Page Rank Heuristic Solver
Run PL-Rank (Page-Rank based heuristic) on WX500 topology.

Usage:
    python main_wx500_pl_rank.py experiment.seed=0
    python main_wx500_pl_rank.py experiment.seed=0 v_sim_setting.num_v_nets=500
"""

import os
import hydra
from omegaconf import DictConfig
from virne.system import BaseSystem
from virne.utils.config import add_simulation_into_config, generate_run_id


@hydra.main(version_base=None, config_path="settings", config_name="main_wx500_pl_rank")
def run(config: DictConfig):
    """Run the VNE simulation with WX500 topology and PL-Rank solver."""
    print(f"\n{'-' * 20}    Start     {'-' * 20}\n")
    print("Running PL-Rank solver on WX500 (500-node Waxman topology)")
    print(f"Seed: {config.experiment.seed}")
    print(f"Solver: {config.solver.solver_name}")

    # Configure run ID
    if config.experiment.run_id == 'auto':
        config.experiment.run_id = generate_run_id()
    add_simulation_into_config(config)

    # Create system from config
    system = BaseSystem.from_config(config)

    # Print network info
    print(f"Physical network: {system.env.p_net.num_nodes} nodes, {system.env.p_net.num_links} links")

    # Run the simulation
    system.run()

    print(f"\n{'-' * 20}   Complete   {'-' * 20}\n")


if __name__ == '__main__':
    run()
