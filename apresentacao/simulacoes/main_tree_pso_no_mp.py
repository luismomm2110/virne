#!/usr/bin/env python3
"""
PSO for Tree topology - NO MULTIPROCESSING VERSION
Fixes pickle error by using sequential execution instead of mp.Process
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from virne.data import Generator, Writer
from virne.solver import REGISTRY as SOLVER_REGISTRY
from virne.core import Controller, Recorder, Counter, Logger
from virne.network import PhysicalNetwork
from virne.system import BasicScenario
import yaml


def run_pso_tree(seed=0):
    """Run PSO on tree topology with specified seed"""

    # Load config - reuse SA config and change solver
    config_path = 'settings/main_tree_sa.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Override seed and solver
    config['seed'] = seed
    config['solver_name'] = 'pso_meta'

    # Create output directory
    save_dir = f'virne/pso_meta/pso_tree_seed_{seed}'
    os.makedirs(save_dir, exist_ok=True)

    print(f"=" * 80)
    print(f"Running PSO on Tree topology (seed={seed})")
    print(f"Config: {config_path}")
    print(f"Output: {save_dir}")
    print(f"=" * 80)

    # Initialize components
    scenario = BasicScenario.from_config(config)

    # Run simulation
    scenario.run(
        solver_name='pso_meta',
        num_epochs=1,
        start_epoch=0,
        save_dir=save_dir,
        verbose=1
    )

    print(f"\n✓ Completed PSO tree seed {seed}")
    print(f"  Results saved to: {save_dir}")


if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    # Patch PSO to use sequential execution
    from virne.solver.meta_heuristic.particle_swarm_optimization_solver import ParticleSwarmOptimizationSolver

    original_meta_run = ParticleSwarmOptimizationSolver.meta_run

    def patched_meta_run(self, v_net, p_net):
        """Sequential version without multiprocessing"""
        self.initialize(v_net, p_net)
        # Run iterations sequentially instead of with mp.Process
        for iteration_id in range(self.max_iteration):
            for particle in self.particles:
                self.evolve(particle)
            self.update_best_individual(self.particles)
        return self.best_individual.best_solution

    # Apply patch
    ParticleSwarmOptimizationSolver.meta_run = patched_meta_run

    # Run simulation
    run_pso_tree(seed)
