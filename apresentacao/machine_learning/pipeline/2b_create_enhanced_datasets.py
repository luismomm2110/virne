#!/usr/bin/env python3
"""
Step 2b: Create Enhanced Datasets
Adds 10 engineered features to train/val/test datasets for improved model training.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_enhanced_features(df):
    """Add 10 engineered features to dataset."""
    df = df.copy()

    # ===== Network Heterogeneity Features (3) =====
    # 1. p_net_node_link_resource_ratio: Ratio of node to link utilization
    df['p_net_node_link_resource_ratio'] = (
        df['p_net_node_util'] / (df['p_net_link_util'] + 1e-6)
    )

    # 2. p_net_util_imbalance: Imbalance between node and link utilization
    df['p_net_util_imbalance'] = np.abs(
        df['p_net_node_util'] - df['p_net_link_util']
    )

    # 3. p_net_resource_heterogeneity: Variance in resource availability
    df['p_net_resource_heterogeneity'] = np.abs(
        df['p_net_node_available_resource'] / (df['p_net_link_available_resource'] + 1e-6)
    )

    # ===== Network Fragmentation Features (3) =====
    # 4. p_net_fragmentation_estimate: Estimate of network fragmentation
    # Higher when resources are scattered (high util imbalance, low availability)
    df['p_net_fragmentation_estimate'] = (
        df['p_net_util_imbalance'] * (1 - df['p_net_overall_util'])
    )

    # 5. p_net_uneven_utilization: How unevenly resources are used
    df['p_net_uneven_utilization'] = (
        np.abs(df['p_net_node_util'] - df['p_net_link_util']) *
        df['p_net_overall_util']
    )

    # 6. p_net_health_score: Overall network health (0-1, higher is better)
    # Combines available resources and balanced utilization
    df['p_net_health_score'] = (
        df['p_net_available_resource'] / 100 *
        (1 - df['p_net_util_imbalance'])
    )

    # ===== VNR Complexity Features (4) =====
    # 7. vnr_demand_intensity: Total demand relative to VNR size
    df['vnr_demand_intensity'] = (
        df['v_net_total_demand'] /
        (df['v_net_num_nodes'] * df['v_net_num_edges'] + 1)
    )

    # 8. vnr_density_adjusted: Adjusted density considering node and link demands
    df['vnr_density_adjusted'] = (
        df['v_net_connectivity'] *
        (df['v_net_demand_per_link'] / (df['v_net_demand_per_node'] + 1e-6))
    )

    # 9. vnr_node_link_demand_ratio: Ratio of node to link demands
    df['vnr_node_link_demand_ratio'] = (
        df['v_net_node_demand'] / (df['v_net_link_demand'] + 1e-6)
    )

    # 10. vnr_structural_complexity: Combined measure of VNR complexity
    df['vnr_structural_complexity'] = (
        df['v_net_connectivity'] *
        df['v_net_node_to_link_demand_ratio'] *
        np.log1p(df['v_net_lifetime'])
    )

    return df


def main():
    print("=" * 80)
    print("Creating Enhanced Datasets with New Features")
    print("=" * 80)

    dataset_dir = Path('datasets')

    # Load original datasets
    train_df = pd.read_csv(dataset_dir / 'train.csv')
    val_df = pd.read_csv(dataset_dir / 'val.csv')
    test_df = pd.read_csv(dataset_dir / 'test.csv')

    print(f"\nLoading datasets:")
    print(f"  train.csv: {train_df.shape}")
    print(f"  val.csv: {val_df.shape}")
    print(f"  test.csv: {test_df.shape}")

    # Create enhanced features
    print(f"\nAdding 10 engineered features...")
    train_enhanced = create_enhanced_features(train_df)
    val_enhanced = create_enhanced_features(val_df)
    test_enhanced = create_enhanced_features(test_df)

    # Save enhanced datasets
    train_enhanced.to_csv(dataset_dir / 'train_enhanced.csv', index=False)
    val_enhanced.to_csv(dataset_dir / 'val_enhanced.csv', index=False)
    test_enhanced.to_csv(dataset_dir / 'test_enhanced.csv', index=False)

    print(f"\n✓ Enhanced datasets saved:")
    print(f"  train_enhanced.csv: {train_enhanced.shape}")
    print(f"  val_enhanced.csv: {val_enhanced.shape}")
    print(f"  test_enhanced.csv: {test_enhanced.shape}")

    print(f"\nNew features added:")
    new_features = set(train_enhanced.columns) - set(train_df.columns)
    for i, feat in enumerate(sorted(new_features), 1):
        print(f"  {i:2d}. {feat}")


if __name__ == '__main__':
    main()
