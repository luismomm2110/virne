#!/usr/bin/env python3
"""
Generate Improvement vs Baseline comparison chart with all objectives.
"""

import matplotlib.pyplot as plt
import numpy as np

def create_improvement_chart():
    """Create a horizontal bar chart for improvement vs baseline"""

    # Data: Improvement in percentage points
    objectives = ['RAC', 'LRC', 'LAR']
    improvements = [54.0, 58.2, 58.2]
    colors = ['#3498db', '#e74c3c', '#2ecc71']

    fig, ax = plt.subplots(figsize=(12, 7))

    # Create horizontal bars
    bars = ax.barh(objectives, improvements, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, improvements)):
        ax.text(value + 1, i, f'+{value:.1f}pp',
               va='center', fontsize=12, fontweight='bold')

    # Customize
    ax.set_xlabel('Accuracy Improvement (percentage points)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Optimization Objective', fontsize=12, fontweight='bold')
    ax.set_title('Dynamic Selection (Top-3) vs Best Fixed Algorithm\nImprovement per Objective',
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 70)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Add a vertical line at 50pp to highlight the midpoint
    ax.axvline(x=50, color='gray', linestyle=':', linewidth=2, alpha=0.5)

    plt.tight_layout()
    plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf/improvement_by_objective_chart.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Improvement chart saved: improvement_by_objective_chart.png")
    plt.close()

if __name__ == '__main__':
    create_improvement_chart()
