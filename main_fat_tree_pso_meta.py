#!/usr/bin/env python3
"""PSO Meta-heuristic solver on fat-tree topology"""

import hydra
from omegaconf import DictConfig
from virne.system import BaseSystem
from virne.utils.config import add_simulation_into_config, generate_run_id

def set_switches_to_routing_only(p_net):
    """Set CPU=0 for switch nodes (routing-only)"""
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
    print(f"\nPhysical network: {num_switches} switches (CPU=0), {num_hosts} hosts")
    return p_net

@hydra.main(version_base=None, config_path="settings", config_name="main_fat_tree_sa")
def run(config: DictConfig):
    config.solver.solver_name = 'pso_meta'
    config.experiment.run_id = f'pso_meta_fat_tree_seed_{config.experiment.seed}'

    if config.experiment.run_id == 'auto':
        config.experiment.run_id = generate_run_id()
    add_simulation_into_config(config)

    system = BaseSystem.from_config(config)
    system.env.p_net = set_switches_to_routing_only(system.env.p_net)
    system.run()

if __name__ == '__main__':
    run()
