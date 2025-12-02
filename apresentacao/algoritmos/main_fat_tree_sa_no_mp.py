"""
Modified SA solver for fat-tree topology - NO MULTIPROCESSING VERSION

This script patches the SA solver to use sequential execution instead of threading.
This fixes the pickle error: "TypeError: cannot pickle '_thread.lock' object"

Usage:
    python main_fat_tree_sa_no_mp.py experiment.seed=0
"""

import os
import hydra
from omegaconf import DictConfig, OmegaConf, open_dict
from virne.system import BaseSystem
from virne.utils.config import add_simulation_into_config, generate_run_id


def set_switches_to_routing_only(p_net):
    """
    Set CPU=0 for all switch nodes (layer='switch') in the physical network.
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


def patch_sa_solver():
    """Patch SA solver to use sequential execution instead of threading"""
    from virne.solver.meta_heuristic.simulated_annealing_solver import SimulatedAnnealingSolver

    original_meta_run = SimulatedAnnealingSolver.meta_run

    def patched_meta_run(self, v_net, p_net):
        """Sequential version without threading"""
        print("  [PATCHED] Running SA without threading (sequential execution)")
        self.initialize(v_net, p_net)
        # Run individuals sequentially instead of with threads
        for individual in self.individuals:
            self.evolve(individual)
        self.update_best_individual(self.individuals)
        return self.best_individual.best_solution

    SimulatedAnnealingSolver.meta_run = patched_meta_run
    print("✓ SA solver patched: threading disabled, using sequential execution\n")


@hydra.main(version_base=None, config_path="settings", config_name="main_fat_tree_sa")
def run(config: DictConfig):
    """
    Run the VNE simulation with fat-tree topology and SA (no multiprocessing).
    """
    print(f"\n{'-' * 20}    Start (SA NO-MP)    {'-' * 20}\n")
    print("Running Simulated Annealing (SA) solver on fat-tree topology")
    print("MODE: Sequential execution (NO threading)")
    print(f"Seed: {config.experiment.seed}")
    print(f"Solver: {config.solver.solver_name}\n")

    # Patch SA solver BEFORE creating system
    patch_sa_solver()

    # Configure run ID
    if config.experiment.run_id == 'auto':
        config.experiment.run_id = generate_run_id()
    add_simulation_into_config(config)

    # Create system from config
    system = BaseSystem.from_config(config)

    # Modify physical network to set switches to routing-only
    print("Setting switches to routing-only (CPU=0)...")
    system.env.p_net = set_switches_to_routing_only(system.env.p_net)

    # Run the simulation
    system.run()

    print(f"\n{'-' * 20}   Complete (SA NO-MP)   {'-' * 20}\n")


if __name__ == '__main__':
    run()
