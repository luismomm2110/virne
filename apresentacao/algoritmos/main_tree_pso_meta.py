"""
Modified PSO solver for tree topology - NO MULTIPROCESSING VERSION

This script patches the PSO solver to use sequential execution instead of mp.Process.
This fixes the pickle error: "TypeError: cannot pickle '_thread.lock' object"

Usage:
    python main_tree_pso_no_mp.py experiment.seed=0
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


def patch_pso_solver():
    """Patch PSO solver to use sequential execution instead of multiprocessing"""
    from virne.solver.meta_heuristic.particle_swarm_optimization_solver import ParticleSwarmOptimizationSolver

    original_meta_run = ParticleSwarmOptimizationSolver.meta_run

    def patched_meta_run(self, v_net, p_net):
        """Sequential version without multiprocessing"""
        print("  [PATCHED] Running PSO without mp.Process (sequential execution)")
        self.initialize(v_net, p_net)
        # Run iterations sequentially instead of with mp.Process
        for iteration_id in range(self.max_iteration):
            for particle in self.particles:
                self.evolve(particle)
            self.update_best_individual(self.particles)
        return self.best_individual.best_solution

    ParticleSwarmOptimizationSolver.meta_run = patched_meta_run
    print("✓ PSO solver patched: multiprocessing disabled, using sequential execution\n")


@hydra.main(version_base=None, config_path="settings", config_name="main_tree_sa")
def run(config: DictConfig):
    """
    Run the VNE simulation with tree topology and PSO (no multiprocessing).
    """
    print(f"\n{'-' * 20}    Start (PSO NO-MP)    {'-' * 20}\n")
    print("Running Particle Swarm Optimization (PSO) solver on tree topology")
    print("MODE: Sequential execution (NO multiprocessing)")
    print(f"Seed: {config.experiment.seed}")
    print(f"Solver: pso_meta\n")

    # Override solver to PSO
    config.solver.solver_name = 'pso_meta'

    # Patch PSO solver BEFORE creating system
    patch_pso_solver()

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

    print(f"\n{'-' * 20}   Complete (PSO NO-MP)   {'-' * 20}\n")


if __name__ == '__main__':
    run()
