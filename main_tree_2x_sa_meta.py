"""
SA-Meta experiments on Tree 2x topology (64 nodes).

This script runs the SA-Meta solver on the larger Tree 2x topology
for comparative analysis with PL-Rank.

Usage:
    python main_tree_2x_sa_meta.py p_net_setting=tree_2x_p_net_setting \
                                   v_sim_setting=v_sim_200_requests \
                                   solver.solver_name=sa_meta \
                                   experiment.seed=0
"""

import os
import hydra
from omegaconf import DictConfig, OmegaConf, open_dict
from virne.system import BaseSystem
from virne.utils.config import add_simulation_into_config, generate_run_id


def set_switches_to_routing_only(p_net):
    """
    Set CPU=0 for all switch nodes (layer='switch') in the physical network.
    This makes switches routing-only, unable to host virtual nodes.

    Args:
        p_net: PhysicalNetwork instance

    Returns:
        Modified PhysicalNetwork instance
    """
    num_switches = 0
    num_hosts = 0

    for node_id in p_net.nodes:
        layer = p_net.nodes[node_id].get('layer', 'host')
        if layer == 'switch':
            p_net.nodes[node_id]['cpu'] = 0
            p_net.nodes[node_id]['max_cpu'] = 0
            num_switches += 1
        else:
            num_hosts += 1

    print(f"\nPhysical network configured:")
    print(f"  - Switches (routing-only): {num_switches} nodes with CPU=0")
    print(f"  - Hosts (compute nodes): {num_hosts} nodes with CPU>0")
    print(f"  - Total nodes: {num_switches + num_hosts}")
    print(f"  - Total links: {p_net.num_links}\n")

    return p_net


@hydra.main(version_base=None, config_path="settings", config_name="main_tree_2x_sa_meta")
def run(config: DictConfig):
    """
    Run the VNE simulation with Tree 2x topology.
    """
    print(f"\n{'-' * 20}    Start     {'-' * 20}\n")
    print("Running SA-Meta solver on Tree 2x topology (64 nodes)")
    print(f"Seed: {config.experiment.seed}")
    print(f"Solver: {config.solver.solver_name}")

    if config.experiment.run_id == 'auto':
        config.experiment.run_id = generate_run_id()
    add_simulation_into_config(config)

    system = BaseSystem.from_config(config)

    print("\nSetting switches to routing-only (CPU=0)...")
    system.env.p_net = set_switches_to_routing_only(system.env.p_net)

    system.run()

    print(f"\n{'-' * 20}   Complete   {'-' * 20}\n")


if __name__ == '__main__':
    run()
