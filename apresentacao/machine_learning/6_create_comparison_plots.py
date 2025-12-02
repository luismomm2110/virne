#!/usr/bin/env python3
"""
Create comparison plots for XGBoost selector vs baselines.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Patch


def main():
    """Generate comparison plots."""

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (14, 6)
    plt.rcParams['font.size'] = 11

    # Results from evaluation
    results = {
        'Algorithm': ['d_round', 'rw_rank_bfs', 'pl_rank', 'sa_meta', 'ga_meta', 'mip', 'XGBoost\nDynamic', 'Oracle\n(Best)'],
        'Acceptance Rate': [47.25, 31.03, 10.34, 72.41, 20.69, 90.00, 43.33, 45.00],
        'Avg Time (s)': [7.29, 0.34, 0.64, 1.31, 6.77, 15.02, 5.63, 5.65],
        'Category': ['Fixed', 'Fixed', 'Fixed', 'Fixed', 'Fixed', 'Fixed', 'Dynamic', 'Oracle']
    }

    df = pd.DataFrame(results)

    # Colors
    colors = ['#3498db' if c == 'Fixed' else ('#2ecc71' if c == 'Dynamic' else '#e74c3c')
              for c in df['Category']]

    legend_elements = [
        Patch(facecolor='#3498db', edgecolor='black', label='Fixed Algorithm'),
        Patch(facecolor='#2ecc71', edgecolor='black', label='XGBoost Dynamic'),
        Patch(facecolor='#e74c3c', edgecolor='black', label='Oracle (Best Known)')
    ]

    # Figure 1: Acceptance Rate ONLY
    fig1, ax1 = plt.subplots(figsize=(10, 8))

    bars1 = ax1.barh(df['Algorithm'], df['Acceptance Rate'], color=colors, edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Acceptance Rate (%)', fontsize=14, fontweight='bold')
    ax1.set_title('Algorithm Acceptance Rate Comparison', fontsize=16, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    ax1.set_xlim(0, 100)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars1, df['Acceptance Rate'])):
        ax1.text(val + 2, i, f'{val:.1f}%', va='center', fontsize=11, fontweight='bold')

    # Highlight XGBoost and Oracle
    ax1.axhline(y=6, color='#2ecc71', linestyle='--', linewidth=2, alpha=0.5)
    ax1.axhline(y=7, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.5)

    # Add legend
    ax1.legend(handles=legend_elements, loc='lower right', frameon=True, fontsize=11)

    plt.tight_layout()
    plt.savefig('results/acceptance_rate_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/acceptance_rate_comparison.png")
    plt.close()


    # Figure 2: Solving Time ONLY
    fig2, ax2 = plt.subplots(figsize=(10, 8))

    bars2 = ax2.barh(df['Algorithm'], df['Avg Time (s)'], color=colors, edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Average Solving Time (seconds, log scale)', fontsize=14, fontweight='bold')
    ax2.set_title('Algorithm Solving Time Comparison', fontsize=16, fontweight='bold')
    ax2.set_xscale('log')
    ax2.grid(axis='x', alpha=0.3, which='both')

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars2, df['Avg Time (s)'])):
        ax2.text(val * 1.3, i, f'{val:.2f}s', va='center', fontsize=11, fontweight='bold')

    # Highlight XGBoost and Oracle
    ax2.axhline(y=6, color='#2ecc71', linestyle='--', linewidth=2, alpha=0.5)
    ax2.axhline(y=7, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.5)

    # Add legend
    ax2.legend(handles=legend_elements, loc='lower right', frameon=True, fontsize=11)

    plt.tight_layout()
    plt.savefig('results/solving_time_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/solving_time_comparison.png")
    plt.close()

    # ALSO Keep original combined figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Plot 1: Acceptance Rate
    bars1 = ax1.barh(df['Algorithm'], df['Acceptance Rate'], color=colors, edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Acceptance Rate (%)', fontsize=13, fontweight='bold')
    ax1.set_title('Acceptance Rate Comparison', fontsize=15, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    ax1.set_xlim(0, 100)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars1, df['Acceptance Rate'])):
        ax1.text(val + 2, i, f'{val:.1f}%', va='center', fontsize=10, fontweight='bold')

    # Highlight XGBoost and Oracle
    ax1.axhline(y=6, color='#2ecc71', linestyle='--', linewidth=2, alpha=0.5)
    ax1.axhline(y=7, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.5)

    # Plot 2: Average Solving Time (log scale)
    bars2 = ax2.barh(df['Algorithm'], df['Avg Time (s)'], color=colors, edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Average Solving Time (seconds, log scale)', fontsize=13, fontweight='bold')
    ax2.set_title('Solving Time Comparison', fontsize=15, fontweight='bold')
    ax2.set_xscale('log')
    ax2.grid(axis='x', alpha=0.3, which='both')

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars2, df['Avg Time (s)'])):
        ax2.text(val * 1.3, i, f'{val:.2f}s', va='center', fontsize=10, fontweight='bold')

    # Highlight XGBoost and Oracle
    ax2.axhline(y=6, color='#2ecc71', linestyle='--', linewidth=2, alpha=0.5)
    ax2.axhline(y=7, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.5)

    fig.legend(handles=legend_elements, loc='upper center', ncol=3, frameon=True,
               fontsize=12, bbox_to_anchor=(0.5, 1.02))

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('results/comparison_bar_charts.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/comparison_bar_charts.png")
    plt.close()

    # Create scatter plot: Acceptance vs Time
    fig, ax = plt.subplots(figsize=(10, 8))

    for i, row in df.iterrows():
        color = '#3498db' if row['Category'] == 'Fixed' else ('#2ecc71' if row['Category'] == 'Dynamic' else '#e74c3c')
        marker = 'o' if row['Category'] == 'Fixed' else ('D' if row['Category'] == 'Dynamic' else '*')
        size = 150 if row['Category'] == 'Fixed' else (300 if row['Category'] == 'Dynamic' else 400)

        ax.scatter(row['Avg Time (s)'], row['Acceptance Rate'],
                   color=color, marker=marker, s=size, edgecolors='black', linewidth=2,
                   label=row['Algorithm'] if row['Category'] != 'Fixed' else None, zorder=3)

        # Add labels
        offset_x = 0.5 if row['Avg Time (s)'] < 5 else -2
        offset_y = 2
        ax.annotate(row['Algorithm'], (row['Avg Time (s)'], row['Acceptance Rate']),
                    xytext=(offset_x, offset_y), textcoords='offset points',
                    fontsize=10, fontweight='bold', ha='left')

    ax.set_xlabel('Average Solving Time (seconds)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Acceptance Rate (%)', fontsize=13, fontweight='bold')
    ax.set_title('Algorithm Performance: Acceptance vs Speed Trade-off', fontsize=15, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-1, 17)
    ax.set_ylim(0, 100)

    # Add quadrant lines
    ax.axhline(y=45, color='gray', linestyle=':', linewidth=1.5, alpha=0.5)
    ax.axvline(x=7, color='gray', linestyle=':', linewidth=1.5, alpha=0.5)
    ax.text(16, 47, 'High Acceptance', fontsize=11, ha='right', style='italic', alpha=0.7)
    ax.text(0.5, 3, 'Fast', fontsize=11, style='italic', alpha=0.7)

    plt.tight_layout()
    plt.savefig('results/acceptance_vs_time_scatter.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/acceptance_vs_time_scatter.png")
    plt.close()

    # Create summary metrics table
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')

    # Prepare data
    table_data = []
    for _, row in df.iterrows():
        table_data.append([
            row['Algorithm'],
            f"{row['Acceptance Rate']:.2f}%",
            f"{row['Avg Time (s)']:.2f}s"
        ])

    table = ax.table(cellText=table_data,
                     colLabels=['Algorithm', 'Acceptance Rate', 'Avg Solving Time'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.3, 0.3, 0.3])

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)

    # Style header
    for i in range(3):
        table[(0, i)].set_facecolor('#34495e')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Style rows
    for i in range(1, len(table_data) + 1):
        category = df.iloc[i-1]['Category']
        if category == 'Dynamic':
            color = '#d5f4e6'
        elif category == 'Oracle':
            color = '#fadbd8'
        else:
            color = '#ebf5fb' if i % 2 == 0 else 'white'

        for j in range(3):
            table[(i, j)].set_facecolor(color)
            if category != 'Fixed':
                table[(i, j)].set_text_props(weight='bold')

    plt.title('Algorithm Performance Summary', fontsize=16, fontweight='bold', pad=20)
    plt.savefig('results/summary_table.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: results/summary_table.png")
    plt.close()

    print("\n" + "="*80)
    print("ALL COMPARISON PLOTS GENERATED SUCCESSFULLY!")
    print("="*80)


if __name__ == '__main__':
    main()