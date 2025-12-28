#!/usr/bin/env python3
"""
Quick analysis script for Waxman_16 extracted data.

Author: Luis Antonio Momm Duarte
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Load data
DATA_PATH = Path("/Users/luismomm/PycharmProjects/virne/apresentacao/machine_learning/datasets/waxman_16_raw_data.csv")
df = pd.read_csv(DATA_PATH)

print("=" * 80)
print("WAXMAN_16 DATA ANALYSIS")
print("=" * 80)

# Basic stats
print(f"\nDataset Size: {len(df):,} records")
print(f"Algorithms: {df['algorithm'].nunique()}")
print(f"Seeds: {df['seed'].nunique()}")
print(f"VNRs per algorithm: {len(df) // df['algorithm'].nunique()}")

# Algorithm Performance
print("\n" + "=" * 80)
print("ALGORITHM PERFORMANCE SUMMARY")
print("=" * 80)

perf = df.groupby('algorithm').agg({
    'success': ['sum', 'mean'],
    'v_net_revenue': 'sum',
    'v_net_cost': 'sum',
    'v_net_r2c_ratio': lambda x: x[x > 0].mean()  # Only successful
}).round(4)

perf.columns = ['Total_Success', 'Acceptance_Rate', 'Total_Revenue', 'Total_Cost', 'Avg_R2C_Ratio']
perf = perf.sort_values('Acceptance_Rate', ascending=False)
print(perf)

# Seed Variability
print("\n" + "=" * 80)
print("SEED-TO-SEED VARIABILITY")
print("=" * 80)

seed_stats = df.groupby(['algorithm', 'seed'])['success'].mean().unstack()
print("\nAcceptance Rate by Seed:")
print(seed_stats.round(4))

print("\nVariability (std dev) per Algorithm:")
variability = seed_stats.std(axis=1).sort_values(ascending=False)
for algo, std in variability.items():
    print(f"  {algo:15s}: {std:.4f}")

# VNR Size Impact
print("\n" + "=" * 80)
print("VNR SIZE IMPACT ON SUCCESS")
print("=" * 80)

# Bin VNR sizes
df['size_category'] = pd.cut(df['v_net_num_nodes'], bins=[1, 3, 6, 10], labels=['Small (2-3)', 'Medium (4-6)', 'Large (7-10)'])

size_impact = df.groupby(['algorithm', 'size_category'])['success'].mean().unstack()
print(size_impact.round(4))

# Resource Utilization at Success/Failure
print("\n" + "=" * 80)
print("RESOURCE UTILIZATION: SUCCESS vs FAILURE")
print("=" * 80)

util_comparison = df.groupby(['algorithm', 'success']).agg({
    'p_net_node_resource_utilization': 'mean',
    'p_net_link_resource_utilization': 'mean'
}).round(4)

print(util_comparison)

# Best/Worst Seeds per Algorithm
print("\n" + "=" * 80)
print("BEST AND WORST SEEDS PER ALGORITHM")
print("=" * 80)

for algo in df['algorithm'].unique():
    algo_df = df[df['algorithm'] == algo]
    seed_perf = algo_df.groupby('seed')['success'].sum()

    best_seed = seed_perf.idxmax()
    worst_seed = seed_perf.idxmin()
    best_count = seed_perf.max()
    worst_count = seed_perf.min()

    print(f"\n{algo:15s}:")
    print(f"  Best:  Seed {best_seed} ({best_count}/200 = {best_count/2:.1f}%)")
    print(f"  Worst: Seed {worst_seed} ({worst_count}/200 = {worst_count/2:.1f}%)")
    print(f"  Range: {best_count - worst_count} requests")

# Summary Statistics
print("\n" + "=" * 80)
print("OVERALL SUMMARY STATISTICS")
print("=" * 80)

print(f"\nTotal Successful Embeddings: {df['success'].sum():,} / {len(df):,} ({df['success'].mean():.2%})")
print(f"Total Revenue Generated: ${df['v_net_revenue'].sum():,.2f}")
print(f"Total Cost Incurred: ${df['v_net_cost'].sum():,.2f}")
print(f"Overall R2C Ratio: {df[df['v_net_r2c_ratio'] > 0]['v_net_r2c_ratio'].mean():.4f}")

print(f"\nAverage VNR Characteristics:")
print(f"  Nodes: {df['v_net_num_nodes'].mean():.2f}")
print(f"  Edges: {df['v_net_num_edges'].mean():.2f}")
print(f"  Lifetime: {df['v_net_lifetime'].mean():.2f} time units")
print(f"  Node Demand: {df['v_net_node_demand'].mean():.2f} units")
print(f"  Link Demand: {df['v_net_link_demand'].mean():.2f} units")

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)