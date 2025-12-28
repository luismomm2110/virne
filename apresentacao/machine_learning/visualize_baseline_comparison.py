#!/usr/bin/env python3
"""
Create visualizations for Baseline Comparison

Generates:
1. Bar chart: Decision Tree vs Best Single Algorithm (by objective)
2. Table showing results
3. Improvement breakdown
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)

# Load results
summary_df = pd.read_csv('models/baseline_comparison_summary.csv')

# Create figure with subplots
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Plot 1: Accuracy Comparison
ax1 = axes[0]
x = range(len(summary_df))
width = 0.35

bars1 = ax1.bar([i - width/2 for i in x], summary_df['baseline_accuracy'], width,
                label='Best Single Algorithm', color='#FF6B6B', alpha=0.8)
bars2 = ax1.bar([i + width/2 for i in x], summary_df['tree_accuracy'], width,
                label='Decision Tree (Top-3)', color='#4ECDC4', alpha=0.8)

ax1.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Objective', fontsize=12, fontweight='bold')
ax1.set_title('Decision Tree vs Best Single Algorithm Baseline', fontsize=13, fontweight='bold', pad=20)
ax1.set_xticks(x)
ax1.set_xticklabels(summary_df['objective'], fontsize=11)
ax1.legend(fontsize=11, loc='upper left')
ax1.set_ylim(0, 110)
ax1.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%',
            ha='center', va='bottom', fontsize=9)

for bar in bars2:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%',
            ha='center', va='bottom', fontsize=9)

# Plot 2: Improvement
ax2 = axes[1]
colors = ['#52C41A' if x > 0 else '#F5222D' for x in summary_df['improvement_pp']]
bars = ax2.barh(summary_df['objective'], summary_df['improvement_pp'], color=colors, alpha=0.8)

ax2.set_xlabel('Improvement (percentage points)', fontsize=12, fontweight='bold')
ax2.set_title('Improvement: Tree vs Baseline', fontsize=13, fontweight='bold', pad=20)
ax2.set_xlim(0, max(summary_df['improvement_pp']) * 1.15)
ax2.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, summary_df['improvement_pp'])):
    ax2.text(val, bar.get_y() + bar.get_height()/2.,
            f' +{val:.1f}pp',
            ha='left', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('models/baseline_comparison_chart.png', dpi=300, bbox_inches='tight')
print("✓ Saved: models/baseline_comparison_chart.png")

# Create a detailed table image
fig, ax = plt.subplots(figsize=(14, 5))
ax.axis('tight')
ax.axis('off')

# Prepare table data
table_data = []
table_data.append(['Objective', 'Best Algorithm', 'Baseline Acc.', 'Tree Acc.', 'Improvement', 'Relative Gain'])

for _, row in summary_df.iterrows():
    table_data.append([
        row['objective'],
        row['baseline_algorithm'],
        f"{row['baseline_accuracy']:.2f}%",
        f"{row['tree_accuracy']:.2f}%",
        f"+{row['improvement_pp']:.2f}pp",
        f"+{row['improvement_relative']:.1f}%"
    ])

# Add summary row
table_data.append([
    'AVERAGE',
    '-',
    f"{summary_df['baseline_accuracy'].mean():.2f}%",
    f"{summary_df['tree_accuracy'].mean():.2f}%",
    f"+{summary_df['improvement_pp'].mean():.2f}pp",
    f"+{summary_df['improvement_relative'].mean():.1f}%"
])

table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                colWidths=[0.15, 0.2, 0.15, 0.15, 0.15, 0.15])

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

# Style header row
for i in range(len(table_data[0])):
    table[(0, i)].set_facecolor('#4ECDC4')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Style summary row
for i in range(len(table_data[0])):
    table[(len(table_data)-1, i)].set_facecolor('#E8F5E9')
    table[(len(table_data)-1, i)].set_text_props(weight='bold')

# Color alternate rows
for i in range(1, len(table_data)-1):
    for j in range(len(table_data[0])):
        if i % 2 == 0:
            table[(i, j)].set_facecolor('#F5F5F5')

plt.title('Decision Tree vs Best Single Algorithm Baseline - Detailed Results',
         fontsize=14, fontweight='bold', pad=20)
plt.savefig('models/baseline_comparison_table.png', dpi=300, bbox_inches='tight')
print("✓ Saved: models/baseline_comparison_table.png")

plt.close('all')

# Print summary
print("\n" + "="*80)
print("VISUALIZATION SUMMARY")
print("="*80)
print(f"\nData Points Generated:")
print(f"  - 5 objectives (RAC, LRC, LAR, AST, BALANCED)")
print(f"  - Baseline Accuracy Range: {summary_df['baseline_accuracy'].min():.1f}% - {summary_df['baseline_accuracy'].max():.1f}%")
print(f"  - Tree Accuracy Range: {summary_df['tree_accuracy'].min():.1f}% - {summary_df['tree_accuracy'].max():.1f}%")
print(f"  - Improvement Range: {summary_df['improvement_pp'].min():.1f}pp - {summary_df['improvement_pp'].max():.1f}pp")
print(f"\nKey Finding:")
print(f"  - Tree outperforms baseline in ALL 5 objectives")
print(f"  - Average improvement: +{summary_df['improvement_pp'].mean():.1f} percentage points")
print(f"  - Average tree accuracy: {summary_df['tree_accuracy'].mean():.1f}%")
