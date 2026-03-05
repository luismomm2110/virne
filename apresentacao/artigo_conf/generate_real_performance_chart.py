#!/usr/bin/env python3
"""
Gera gráfico de comparação de desempenho real: Baseline vs Árvore de Decisão
Baseado na Tabela V (tab:real-performance-improvement)
"""

import matplotlib.pyplot as plt
import numpy as np

def create_real_performance_chart():
    """Cria gráfico de barras comparando desempenho real baseline vs árvore"""
    
    # Dados da tabela
    objectives = ['RAC', 'LRC', 'LAR']
    baseline_values = [43.17, 0.4574, 70.29]  # RAC em %, LRC em razão, LAR em valor
    tree_values = [81.95, 0.7262, 113.45]
    improvements = [89.83, 58.76, 61.40]  # %
    
    # Normalizar valores para escala comparável (usar porcentagem de melhoria)
    # Vamos criar um gráfico de barras agrupadas mostrando os valores normalizados
    
    # Configuração da figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Posições das barras
    x = np.arange(len(objectives))
    width = 0.35
    
    # Criar barras
    bars1 = ax.bar(x - width/2, baseline_values, width,
                   label='Baseline (Fixed Algorithm)',
                   color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, tree_values, width,
                   label='Decision Tree',
                   color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Adicionar valores nas barras
    for i, (bar1, bar2, base, tree, imp) in enumerate(zip(bars1, bars2, 
                                                           baseline_values, tree_values, 
                                                           improvements)):
        # Valores nas barras baseline
        if i == 0:  # RAC - porcentagem
            label1 = f'{base:.2f}%'
        elif i == 1:  # LRC - razão
            label1 = f'{base:.4f}'
        else:  # LAR - valor
            label1 = f'{base:.2f}'
        
        ax.text(bar1.get_x() + bar1.get_width()/2, bar1.get_height() + max(baseline_values[i], tree_values[i])*0.02,
               label1,
               ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Valores nas barras árvore
        if i == 0:  # RAC - porcentagem
            label2 = f'{tree:.2f}%'
        elif i == 1:  # LRC - razão
            label2 = f'{tree:.4f}'
        else:  # LAR - valor
            label2 = f'{tree:.2f}'
        
        ax.text(bar2.get_x() + bar2.get_width()/2, bar2.get_height() + max(baseline_values[i], tree_values[i])*0.02,
               label2,
               ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Melhoria acima das barras
        max_height = max(baseline_values[i], tree_values[i])
        ax.text(bar2.get_x() + bar2.get_width()/2, max_height + max_height*0.08,
               f'+{imp:.2f}%',
               ha='center', va='bottom', fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # Customização
    ax.set_xlabel('Optimization Objective', fontsize=12, fontweight='bold')
    ax.set_ylabel('Value', fontsize=12, fontweight='bold')
    ax.set_title('Real Performance: Baseline vs Decision Tree\nComparison by Optimization Objective',
                fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(objectives, fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    
    # Ajustar limites do eixo Y dinamicamente
    max_all = max(max(baseline_values), max(tree_values))
    ax.set_ylim(0, max_all * 1.3)
    
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Adicionar nota sobre unidades
    ax.text(0.98, 0.98, 'Note: RAC in %, LRC as ratio, LAR in absolute value',
           transform=ax.transAxes, fontsize=8, style='italic',
           ha='right', verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf/real_performance_chart.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Gráfico de desempenho real criado: real_performance_chart.png")
    plt.close()

if __name__ == '__main__':
    create_real_performance_chart()
