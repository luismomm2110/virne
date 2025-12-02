#!/usr/bin/env python3
"""
SA for Fat-Tree topology - NO MULTIPROCESSING VERSION
Fixes pickle error by using sequential execution instead of threading
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


def run_sa_fat_tree(seed=0):
    """Run SA on fat-tree topology with specified seed"""

    # Load config
    config_path = 'settings/main_fat_tree_sa.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Override seed
    config['seed'] = seed

    # Create output directory
    save_dir = f'virne/sa_meta/sa_fat_tree_seed_{seed}'
    os.makedirs(save_dir, exist_ok=True)

    print(f"=" * 80)
    print(f"Running SA on Fat-Tree topology (seed={seed})")
    print(f"Config: {config_path}")
    print(f"Output: {save_dir}")
    print(f"=" * 80)

    # Initialize components
    scenario = BasicScenario.from_config(config)

    # Run simulation
    scenario.run(
        solver_name='sa_meta',
        num_epochs=1,
        start_epoch=0,
        save_dir=save_dir,
        verbose=1
    )

    print(f"\n✓ Completed SA fat-tree seed {seed}")
    print(f"  Results saved to: {save_dir}")


if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    # Patch SA to use sequential execution
    from virne.solver.meta_heuristic.simulated_annealing_solver import SimulatedAnnealingSolver

    original_meta_run = SimulatedAnnealingSolver.meta_run

    def patched_meta_run(self, v_net, p_net):
        """Sequential version without threading"""
        self.initialize(v_net, p_net)
        # Run individuals sequentially instead of with threads
        for individual in self.individuals:
            self.evolve(individual)
        self.update_best_individual(self.individuals)
        return self.best_individual.best_solution

    # Apply patch
    SimulatedAnnealingSolver.meta_run = patched_meta_run

    # Run simulation
    run_sa_fat_tree(seed)
