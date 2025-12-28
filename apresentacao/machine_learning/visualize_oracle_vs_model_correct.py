#!/usr/bin/env python3
"""
Visualize Oracle vs Model Performance - CORRECT VERSION

Creates comprehensive visualizations comparing:
- Oracle (a posteriori, optimal algorithm selection)
- Model Top-3 (ML model's ranking accuracy)
- Model Classification (ML model's exact algorithm prediction)
- Individual Algorithms
"""

import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 11

print("=" * 80)
print("ORACLE VS MODEL VISUALIZATION - CORRECT VERSION")
print("=" * 80)

# ============================================================================
# Load data
# ============================================================================

print("\n📂 Loading data...")

# Load Oracle metrics (correct, on test set)
with open('models/oracle_performance_correct.json') as f:
    oracle_data = json.load(f)

# Load Model metrics
with open('models/ranking_results_per_topology.json') as f:
    model_data = json.load(f)

# Load algorithm individual metrics (if available)
try:
    with open('models/algorithm_metrics.csv') as f:
        algo_metrics = pd.read_csv('models/algorithm_metrics.csv')
        algo_metrics_available = True
except:
    algo_metrics_available = False
    print("  ⚠️  algorithm_metrics.csv not found (will skip individual algo bars)")

print("  ✓ Oracle data loaded")
print("  ✓ Model data loaded")
if algo_metrics_available:
    print("  ✓ Algorithm metrics loaded")

# ============================================================================
# Prepare data for visualization
# ============================================================================

topologies = ['tree', 'fat_tree', 'waxman_16']
topo_labels = {
    'tree': 'Tree',
    'fat_tree': 'Fat-Tree',
    'waxman_16': 'Waxman-16'
}

# Extract metrics
data_viz = []

for topo in topologies:
    oracle_rac = oracle_data['rac'][topo]['oracle_metric']
    model_top3 = model_data[topo]['rac']['top3_ranking'] * 100
    model_class = model_data[topo]['rac']['classification'] * 100

    data_viz.append({
        'topology': topo_labels[topo],
        'Oracle': oracle_rac,
        'Model Top-3': model_top3,
        'Model Classification': model_class
    })

df_viz = pd.DataFrame(data_viz)

print("\n" + "=" * 80)
print("METRICS SUMMARY")
print("=" * 80)
print(df_viz.to_string(index=False))

# ============================================================================
# Create visualization: Oracle vs Model Comparison
# ============================================================================

print("\n📊 Creating visualizations...")

fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle('Oracle vs Model Performance: RAC (Request Acceptance Rate)',
             fontsize=16, fontweight='bold', y=1.02)

colors = {
    'Oracle': '#2ecc71',          # Green
    'Model Top-3': '#3498db',     # Blue
    'Model Classification': '#e74c3c'  # Red
}

for idx, topo in enumerate(topologies):
    ax = axes[idx]

    oracle_val = oracle_data['rac'][topo]['oracle_metric']
    model_top3 = model_data[topo]['rac']['top3_ranking'] * 100
    model_class = model_data[topo]['rac']['classification'] * 100

    metrics = ['Oracle', 'Model Top-3', 'Model Classification']
    values = [oracle_val, model_top3, model_class]
    bar_colors = [colors[m] for m in metrics]

    # Create bar chart
    bars = ax.bar(metrics, values, color=bar_colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    # Add value labels on top of bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=11)

    # Add gap annotation
    gap = oracle_val - model_top3
    ax.text(0.5, max(values) * 0.5, f'Gap: {gap:+.1f}%',
            ha='center', fontsize=12, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_title(f'{topo_labels[topo]} Topology', fontweight='bold', fontsize=12)
    ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=0.3)
    ax.set_xticklabels(metrics, rotation=15, ha='right')

plt.tight_layout()
plt.savefig('models/oracle_vs_model_comparison.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: models/oracle_vs_model_comparison.png")
plt.close()

# ============================================================================
# Create visualization: Gap Analysis
# ============================================================================

fig, ax = plt.subplots(figsize=(12, 6))

gaps = []
topo_names = []

for topo in topologies:
    oracle_val = oracle_data['rac'][topo]['oracle_metric']
    model_top3 = model_data[topo]['rac']['top3_ranking'] * 100
    gap = oracle_val - model_top3

    gaps.append(gap)
    topo_names.append(topo_labels[topo])

bars = ax.barh(topo_names, gaps, color=['#f39c12', '#e74c3c', '#9b59b6'],
               alpha=0.8, edgecolor='black', linewidth=1.5)

# Add value labels
for bar, val in zip(bars, gaps):
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height()/2.,
            f'{val:+.2f}%',
            ha='left', va='center', fontweight='bold', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

ax.set_xlabel('Gap: Oracle - Model Top-3 (%)', fontweight='bold', fontsize=12)
ax.set_title('Algorithm Selection: Room for Improvement\n(Higher = More room to improve)',
             fontweight='bold', fontsize=14)
ax.set_xlim(0, max(gaps) * 1.2)
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('models/oracle_vs_model_gap_analysis.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: models/oracle_vs_model_gap_analysis.png")
plt.close()

# ============================================================================
# Create visualization: All metrics together
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 7))

x = np.arange(len(topologies))
width = 0.25

oracle_vals = [oracle_data['rac'][t]['oracle_metric'] for t in topologies]
model_top3_vals = [model_data[t]['rac']['top3_ranking'] * 100 for t in topologies]
model_class_vals = [model_data[t]['rac']['classification'] * 100 for t in topologies]

bars1 = ax.bar(x - width, oracle_vals, width, label='Oracle',
               color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1)
bars2 = ax.bar(x, model_top3_vals, width, label='Model Top-3',
               color='#3498db', alpha=0.8, edgecolor='black', linewidth=1)
bars3 = ax.bar(x + width, model_class_vals, width, label='Model Classification',
               color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1)

# Add value labels
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Topology', fontweight='bold', fontsize=12)
ax.set_ylabel('RAC (%)', fontweight='bold', fontsize=12)
ax.set_title('Oracle vs Model Performance Across Topologies', fontweight='bold', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels([topo_labels[t] for t in topologies])
ax.legend(loc='lower right', fontsize=11)
ax.set_ylim(0, 105)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('models/oracle_vs_model_detailed.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: models/oracle_vs_model_detailed.png")
plt.close()

# ============================================================================
# Create a summary table visualization
# ============================================================================

fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('off')

# Prepare table data
table_data = []
table_data.append(['Topology', 'Oracle RAC', 'Model Top-3', 'Model Class', 'Gap'])

for topo in topologies:
    oracle_val = oracle_data['rac'][topo]['oracle_metric']
    model_top3 = model_data[topo]['rac']['top3_ranking'] * 100
    model_class = model_data[topo]['rac']['classification'] * 100
    gap = oracle_val - model_top3

    table_data.append([
        topo_labels[topo],
        f'{oracle_val:.2f}%',
        f'{model_top3:.2f}%',
        f'{model_class:.2f}%',
        f'{gap:+.2f}%'
    ])

# Create table
table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                colWidths=[0.2, 0.2, 0.2, 0.2, 0.2])

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

# Style header row
for i in range(5):
    table[(0, i)].set_facecolor('#34495e')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Style data rows
colors_table = ['#ecf0f1', '#bdc3c7']
for i in range(1, len(table_data)):
    for j in range(5):
        table[(i, j)].set_facecolor(colors_table[i % 2])

        # Highlight gap column
        if j == 4:
            table[(i, j)].set_facecolor('#fff3cd')
            table[(i, j)].set_text_props(weight='bold')

plt.title('Oracle vs Model Performance Summary', fontweight='bold', fontsize=14, pad=20)
plt.tight_layout()
plt.savefig('models/oracle_vs_model_summary_table.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: models/oracle_vs_model_summary_table.png")
plt.close()

# ============================================================================
# Print summary
# ============================================================================

print("\n" + "=" * 80)
print("VISUALIZATION SUMMARY")
print("=" * 80)

print("""
Created 4 visualizations:

1. oracle_vs_model_comparison.png
   → 3-panel comparison (Tree, Fat-Tree, Waxman-16)
   → Shows Oracle vs Model Top-3 vs Model Classification
   → Highlights gap for each topology

2. oracle_vs_model_gap_analysis.png
   → Horizontal bar chart of improvement gaps
   → Shows room for model improvement

3. oracle_vs_model_detailed.png
   → Grouped bar chart all metrics together
   → Easy comparison across topologies

4. oracle_vs_model_summary_table.png
   → Clean table format with all metrics
   → Highlights gaps in yellow

Key Insights:
""")

for topo in topologies:
    oracle_val = oracle_data['rac'][topo]['oracle_metric']
    model_top3 = model_data[topo]['rac']['top3_ranking'] * 100
    model_class = model_data[topo]['rac']['classification'] * 100
    gap = oracle_val - model_top3

    print(f"\n{topo_labels[topo]}:")
    print(f"  Oracle RAC: {oracle_val:.2f}%")
    print(f"  Model Top-3: {model_top3:.2f}%")
    print(f"  Model Classification: {model_class:.2f}%")
    print(f"  Gap (room to improve): {gap:+.2f}%")

print("\n✅ All visualizations created successfully!")
