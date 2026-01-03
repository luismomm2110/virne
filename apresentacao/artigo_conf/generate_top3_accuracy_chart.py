#!/usr/bin/env python3
"""
Generate Top-3 Accuracy visualization for the article.
"""

import matplotlib.pyplot as plt
import numpy as np

def create_top3_accuracy_chart():
    """Create a grouped bar chart for Top-3 Accuracy by objective and topology"""

    # Data from Table II
    objectives = ['RAC', 'LRC', 'LAR']
    tree = [93.37, 90.06, 81.77]
    fat_tree = [79.30, 77.97, 69.60]
    waxman = [85.65, 81.34, 78.47]

    # Setup
    x = np.arange(len(objectives))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 7))

    # Bars
    bars1 = ax.bar(x - width, tree, width, label='Tree', color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x, fat_tree, width, label='Fat-Tree', color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.2)
    bars3 = ax.bar(x + width, waxman, width, label='Waxman-16', color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.2)

    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

    add_value_labels(bars1)
    add_value_labels(bars2)
    add_value_labels(bars3)

    # Customize
    ax.set_ylabel('Top-3 Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Optimization Objective', fontsize=12, fontweight='bold')
    ax.set_title('Top-3 Accuracy per Objective and Topology', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(objectives, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.axhline(y=88.40, color='#3498db', linestyle='--', linewidth=1.5, alpha=0.5, label='Tree Avg (88.40%)')
    ax.axhline(y=75.62, color='#e74c3c', linestyle='--', linewidth=1.5, alpha=0.5, label='Fat-Tree Avg (75.62%)')
    ax.axhline(y=81.82, color='#2ecc71', linestyle='--', linewidth=1.5, alpha=0.5, label='Waxman Avg (81.82%)')

    ax.legend(loc='lower left', fontsize=10, framealpha=0.95)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf/top3_accuracy_chart.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Chart saved: top3_accuracy_chart.png")
    plt.close()

if __name__ == '__main__':
    create_top3_accuracy_chart()
