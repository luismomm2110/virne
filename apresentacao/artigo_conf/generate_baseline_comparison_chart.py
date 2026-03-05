#!/usr/bin/env python3
"""
Gera gráfico de comparação de acurácia: Baseline vs Árvore de Decisão
Baseado na Tabela IV (tab:baseline-comparison)
"""

import matplotlib.pyplot as plt
import numpy as np

def create_baseline_comparison_chart():
    """Cria gráfico de barras comparando acurácia baseline vs árvore"""
    
    # Dados da tabela
    objectives = ['RAC', 'LRC', 'LAR']
    baseline_accuracy = [34.36, 27.23, 22.85]  # %
    tree_accuracy = [67.26, 54.46, 48.14]  # %
    improvements = [32.90, 27.23, 25.29]  # pontos percentuais
    relative_gains = [95.8, 100.0, 110.7]  # %
    
    # Configuração da figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Posições das barras
    x = np.arange(len(objectives))
    width = 0.35
    
    # Criar barras
    bars1 = ax.bar(x - width/2, baseline_accuracy, width,
                   label='Baseline (Fixed Algorithm)',
                   color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, tree_accuracy, width,
                   label='Decision Tree',
                   color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Adicionar valores nas barras
    for i, (bar1, bar2, imp, rel) in enumerate(zip(bars1, bars2, improvements, relative_gains)):
        # Valores nas barras baseline
        ax.text(bar1.get_x() + bar1.get_width()/2, bar1.get_height() + 1,
               f'{baseline_accuracy[i]:.2f}%',
               ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Valores nas barras árvore
        ax.text(bar2.get_x() + bar2.get_width()/2, bar2.get_height() + 1,
               f'{tree_accuracy[i]:.2f}%',
               ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Melhoria acima das barras
        max_height = max(baseline_accuracy[i], tree_accuracy[i])
        ax.text(bar2.get_x() + bar2.get_width()/2, max_height + 8,
               f'+{imp:.2f}pp\n(+{rel:.1f}%)',
               ha='center', va='bottom', fontsize=9, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # Customização
    ax.set_xlabel('Optimization Objective', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Accuracy Comparison: Baseline vs Decision Tree\nby Optimization Objective',
                fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(objectives, fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf/baseline_comparison_chart.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Gráfico de comparação baseline criado: baseline_comparison_chart.png")
    plt.close()

if __name__ == '__main__':
    create_baseline_comparison_chart()

