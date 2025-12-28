#!/usr/bin/env python3
"""Quick test to verify seed column is added"""

import hydra
from omegaconf import DictConfig
from virne.system import BaseSystem

@hydra.main(version_base=None, config_path='settings', config_name='main_tree_saturation')
def main(config: DictConfig):
    # Configure for quick test
    config.solver.solver_name = 'r_round'
    config.experiment.seed = 888
    config.experiment.run_id = f'test_seed_888'
    config.v_sim_setting.num_v_nets = 10  # Very small for quick test

    print(f"\n{'='*70}")
    print(f"TESTING: Seed column with seed={config.experiment.seed}")
    print(f"{'='*70}\n")

    system = BaseSystem.from_config(config)
    system.run()

    # Verify the seed column
    import pandas as pd
    import glob

    pattern = f"virne/r_round/test_seed_888/records/*.csv"
    files = glob.glob(pattern)

    if files:
        print(f"\n{'='*70}")
        print(f"VERIFICATION: Checking {files[0]}")
        print(f"{'='*70}\n")

        df = pd.read_csv(files[0])

        if 'seed' in df.columns:
            print(f"✓ SUCCESS: 'seed' column found in records!")
            print(f"  Seed value in CSV: {df['seed'].iloc[0]}")
            print(f"  Expected seed: {config.experiment.seed}")
            print(f"  Match: {df['seed'].iloc[0] == config.experiment.seed}")
        else:
            print(f"✗ FAILED: 'seed' column not found")
            print(f"  Last 5 columns: {df.columns.tolist()[-5:]}")
    else:
        print(f"⚠ No records file found at {pattern}")

if __name__ == '__main__':
    main()
