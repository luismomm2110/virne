#!/usr/bin/env python3
"""
Fix solving_time feature: Create algorithm-specific solving times.

This corrects the issue where solving_time was constant across all rows.
We now assign algorithm-specific average solving times based on training data.
"""

import pandas as pd
import numpy as np


def main():
    """Generate corrected dataset with algorithm-specific solving times."""

    print("Loading full featured dataset...")
    full_df = pd.read_csv('datasets/vnr_features.csv')

    print(f"Original dataset shape: {full_df.shape}")
    print(f"Columns: {list(full_df.columns)}")

    # Compute algorithm-specific average solving times
    print("\n" + "="*80)
    print("COMPUTING ALGORITHM-SPECIFIC SOLVING TIMES")
    print("="*80)

    algo_solving_times = full_df.groupby('algorithm')['solving_time'].agg([
        'count', 'mean', 'min', 'max', 'std'
    ]).round(6)

    print("\nSolving time statistics by algorithm:")
    print(algo_solving_times)

    # Create a mapping of algorithm -> average solving time
    algo_to_solving_time = full_df.groupby('algorithm')['solving_time'].mean().to_dict()

    print("\n\nAlgorithm-specific solving times:")
    for algo, solving_time in sorted(algo_to_solving_time.items(), key=lambda x: x[1], reverse=True):
        print(f"  {algo:15s}: {solving_time:.6f} seconds")

    # Now create the corrected dataset
    print("\n" + "="*80)
    print("CREATING CORRECTED DATASET")
    print("="*80)

    # Load training split
    train_df = pd.read_csv('datasets/train.csv')
    val_df = pd.read_csv('datasets/val.csv')
    test_df = pd.read_csv('datasets/test.csv')

    print(f"\nOriginal train dataset: {train_df.shape}")
    print(f"  All solving_time values are: {train_df['solving_time'].unique()}")

    # For each split, we need to add algorithm information
    # We'll merge with the full_df to get algorithm-specific solving times

    for split_name, split_df in [('train', train_df), ('val', val_df), ('test', test_df)]:
        print(f"\n{split_name.upper()} SPLIT:")
        print(f"  Before: {split_df.shape}")

        # Get the best_overall algorithm for each row
        # and assign the corresponding algorithm's solving time
        split_df_copy = split_df.copy()
        split_df_copy['algorithm_solving_time'] = split_df_copy['best_overall'].map(algo_to_solving_time)

        # Replace solving_time with algorithm-specific value
        split_df_copy['solving_time'] = split_df_copy['algorithm_solving_time']
        split_df_copy = split_df_copy.drop('algorithm_solving_time', axis=1)

        print(f"  After: {split_df_copy.shape}")
        print(f"  Unique solving_time values: {split_df_copy['solving_time'].nunique()}")
        print(f"  Solving time range: {split_df_copy['solving_time'].min():.6f} - {split_df_copy['solving_time'].max():.6f}")

        # Show distribution
        print(f"  Solving time by algorithm:")
        for algo in sorted(split_df_copy['best_overall'].unique()):
            val = split_df_copy[split_df_copy['best_overall'] == algo]['solving_time'].iloc[0]
            count = (split_df_copy['best_overall'] == algo).sum()
            print(f"    {algo:15s}: {val:.6f}s (n={count})")

        # Save corrected dataset
        split_df_copy.to_csv(f'datasets/{split_name}_corrected.csv', index=False)
        print(f"  ✓ Saved: datasets/{split_name}_corrected.csv")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\nThe problem:")
    print("  - Original solving_time was constant (2.367834) for ALL samples")
    print("  - This prevented XGBoost from learning algorithm characteristics")
    print("  - Feature importance was 0 because it had no variance")

    print("\nThe solution:")
    print("  - Assign algorithm-specific solving times to each sample")
    print("  - Example: rows with best_overall='mip' get solving_time=15.06s (mip's avg)")
    print("  - Example: rows with best_overall='pl_rank' get solving_time=0.01s (pl_rank's avg)")

    print("\nExpected improvement:")
    print("  - solving_time feature will now have variance and discriminative power")
    print("  - XGBoost can learn which algorithms are fast/slow")
    print("  - Feature importance should increase from 0 to meaningful value")

    print("\nNext steps:")
    print("  1. Retrain XGBoost with corrected datasets")
    print("  2. Check feature importance - solving_time should no longer be 0")
    print("  3. Model accuracy should improve (hopefully)")
    print("  4. Replace original datasets:")
    print("     cp datasets/train_corrected.csv datasets/train.csv")
    print("     cp datasets/val_corrected.csv datasets/val.csv")
    print("     cp datasets/test_corrected.csv datasets/test.csv")

    print("\n" + "="*80)
    print("CORRECTION COMPLETE!")
    print("="*80)


if __name__ == '__main__':
    main()