#!/usr/bin/env python3
"""Test if seed column is properly added to records"""

import hydra
from omegaconf import DictConfig
from virne.system import BaseSystem

@hydra.main(version_base=None, config_path='settings', config_name='main')
def main(config: DictConfig):
    # Override config for a quick test
    config.solver.solver_name = 'd_round'
    config.experiment.seed = 777  # Test seed
    config.experiment.run_id = f'test_seed_column_{config.experiment.seed}'
    config.v_sim_setting.num_v_nets = 20  # Small number for quick test

    print(f"\n{'='*60}")
    print(f"Testing seed column with seed={config.experiment.seed}")
    print(f"{'='*60}\n")

    system = BaseSystem.from_config(config)
    system.run()

    # Check the output
    import pandas as pd
    import os
    import glob

    # Find the records file
    solver_name = config.solver.solver_name
    run_id = config.experiment.run_id
    save_root = config.experiment.save_root_dir

    record_pattern = f"{save_root}/{solver_name}/{run_id}/records/*.csv"
    records_files = glob.glob(record_pattern)

    if records_files:
        print(f"\n{'='*60}")
        print(f"Checking records file: {records_files[0]}")
        print(f"{'='*60}\n")

        df = pd.read_csv(records_files[0])

        if 'seed' in df.columns:
            print(f"✓ SUCCESS: seed column found!")
            print(f"  Seed value: {df['seed'].iloc[0]}")
            print(f"  Total rows: {len(df)}")
            print(f"\nFirst few columns: {df.columns.tolist()[:10]}")
            print(f"Last few columns: {df.columns.tolist()[-5:]}")
        else:
            print(f"✗ FAILED: seed column NOT found!")
            print(f"  Available columns: {df.columns.tolist()}")
    else:
        print(f"⚠ No records files found at: {record_pattern}")

if __name__ == '__main__':
    main()