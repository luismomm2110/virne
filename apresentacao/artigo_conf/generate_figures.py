#!/usr/bin/env python3
"""
Gera as figuras de árvore de decisão para o artigo.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

def create_tree_structure():
    """Cria figura de estrutura genérica de árvore de decisão."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Cores
    internal_color = '#FFE5CC'  # Laranja claro
    leaf_color = '#CCE5FF'      # Azul claro
    split_color = '#FFFFCC'     # Amarelo claro

    # Função para desenhar nó
    def draw_node(x, y, text, color, width=1.2, height=0.6):
        box = FancyBboxPatch((x-width/2, y-height/2), width, height,
                            boxstyle="round,pad=0.1",
                            edgecolor='black', facecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=19, weight='bold')

    # Função para desenhar seta
    def draw_arrow(x1, y1, x2, y2, label=''):
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                              arrowstyle='->', mutation_scale=20,
                              linewidth=2, color='black')
        ax.add_patch(arrow)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx+0.3, my, label, fontsize=16, style='italic',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Nível 0: Raiz
    y_level0 = 9
    draw_node(5, y_level0,
             'All Data (N)\nAll Mixed Classes',
             internal_color, width=3.0, height=1.0)

    # Nível 1: Primeiro Split
    y_level1 = 7.5
    x_left1, x_right1 = 2.5, 7.5

    draw_node(x_left1, y_level1,
             'node_utilization ≤ 60%\nN/2 data',
             split_color, width=2.5, height=0.9)
    draw_node(x_right1, y_level1,
             'node_utilization > 60%\nN/2 data',
             split_color, width=2.5, height=0.9)

    draw_arrow(5, y_level0-0.4, x_left1, y_level1+0.35, 'Yes')
    draw_arrow(5, y_level0-0.4, x_right1, y_level1+0.35, 'No')

    # Nível 2: Segundo Split (lado esquerdo)
    y_level2 = 6
    x_left2a, x_left2b = 1, 4

    draw_node(x_left2a, y_level2,
             'vnr_size ≤ 5 nodes\n250 data',
             split_color, width=2.3, height=0.9)
    draw_node(x_left2b, y_level2,
             'vnr_size > 5 nodes\n250 data',
             split_color, width=2.3, height=0.9)

    draw_arrow(x_left1, y_level1-0.35, x_left2a, y_level2+0.35, 'Yes')
    draw_arrow(x_left1, y_level1-0.35, x_left2b, y_level2+0.35, 'No')

    # Nível 2: Segundo Split (lado direito)
    x_right2a, x_right2b = 6, 9

    draw_node(x_right2a, y_level2,
             'connectivity > 0.5\n300 data',
             split_color, width=2.3, height=0.9)
    draw_node(x_right2b, y_level2,
             'connectivity ≤ 0.5\n200 data',
             split_color, width=2.3, height=0.9)

    draw_arrow(x_right1, y_level1-0.35, x_right2a, y_level2+0.35, 'Yes')
    draw_arrow(x_right1, y_level1-0.35, x_right2b, y_level2+0.35, 'No')

    # Nível 3: Folhas (Leafs)
    y_level3 = 4.2

    # Folhas lado esquerdo
    draw_node(0.3, y_level3, 'MIP\n(Exact)', leaf_color, width=1.6, height=0.8)
    draw_node(1.7, y_level3, 'GA-Meta\n(Meta)', leaf_color, width=1.6, height=0.8)
    draw_node(3.2, y_level3, 'PSO-Meta\n(Meta)', leaf_color, width=1.6, height=0.8)
    draw_node(4.8, y_level3, 'GA-Meta\n(Meta)', leaf_color, width=1.6, height=0.8)

    # Folhas lado direito
    draw_node(6, y_level3, 'GA-Meta\n(Meta)', leaf_color, width=1.6, height=0.8)
    draw_node(7.5, y_level3, 'PL-Rank\n(Heuristic)', leaf_color, width=1.6, height=0.8)
    draw_node(9, y_level3, 'MIP\n(Exact)', leaf_color, width=1.6, height=0.8)

    # Setas para folhas
    draw_arrow(x_left2a, y_level2-0.35, 0.3, y_level3+0.3)
    draw_arrow(x_left2a, y_level2-0.35, 1.7, y_level3+0.3)
    draw_arrow(x_left2b, y_level2-0.35, 3.2, y_level3+0.3)
    draw_arrow(x_left2b, y_level2-0.35, 4.8, y_level3+0.3)

    draw_arrow(x_right2a, y_level2-0.35, 6, y_level3+0.3)
    draw_arrow(x_right2a, y_level2-0.35, 7.5, y_level3+0.3)
    draw_arrow(x_right2b, y_level2-0.35, 9, y_level3+0.3)

    plt.tight_layout()
    plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf/tree_structure.png',
               dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Criado: tree_structure.png")
    plt.close()


def create_tree_example_path():
    """Cria figura com exemplo concreto de caminho de decisão."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Cores
    selected_color = '#FFD700'    # Ouro (caminho selecionado)
    unselected_color = '#E8E8E8'  # Cinza claro (não selecionado)
    leaf_selected = '#90EE90'     # Verde claro (folha resultado)

    # Função para desenhar nó
    def draw_node(x, y, text, color, width=1.2, height=0.6, selected=False, linewidth=2):
        lw = 3 if selected else linewidth
        box = FancyBboxPatch((x-width/2, y-height/2), width, height,
                            boxstyle="round,pad=0.1",
                            edgecolor='darkgreen' if selected else 'black',
                            facecolor=color, linewidth=lw)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=9, weight='bold')

    # Função para desenhar seta
    def draw_arrow(x1, y1, x2, y2, label='', selected=False):
        color = 'darkgreen' if selected else 'gray'
        lw = 3 if selected else 1
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                              arrowstyle='->', mutation_scale=20,
                              linewidth=lw, color=color)
        ax.add_patch(arrow)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx+0.3, my, label, fontsize=9, style='italic', weight='bold' if selected else 'normal',
                   bbox=dict(boxstyle='round', facecolor='yellow' if selected else 'white', alpha=0.9))

    # Nível 0: Raiz
    y_level0 = 9
    draw_node(5, y_level0, 'RAIZ\nTodos os Dados', selected_color,
             width=2.5, height=0.8, selected=True)

    # Nível 1: Primeiro Split - Mostra o caminho selecionado
    y_level1 = 7.5
    x_left1 = 2.5
    x_right1 = 7.5

    # Lado esquerdo: SIM (selecionado)
    draw_node(x_left1, y_level1, 'utilização_nodes\n≤ 60%\nSIM ✓',
             selected_color, width=2, height=0.7, selected=True)

    # Lado direito: NÃO (não selecionado)
    draw_node(x_right1, y_level1, 'utilização_nodes\n> 60%\n(NÃO)',
             unselected_color, width=2, height=0.7, selected=False)

    draw_arrow(5, y_level0-0.4, x_left1, y_level1+0.35, 'Sim', selected=True)
    draw_arrow(5, y_level0-0.4, x_right1, y_level1+0.35, 'Não', selected=False)

    # Nível 2: Segundo Split - Mostra o caminho selecionado
    y_level2 = 6
    x_left2a = 1
    x_left2b = 4

    # Lado esquerdo SIM (selecionado)
    draw_node(x_left2a, y_level2, 'tamanho_vnr\n≤ 5 nós\nSIM ✓',
             selected_color, width=1.8, height=0.7, selected=True)

    # Lado esquerdo NÃO (não selecionado)
    draw_node(x_left2b, y_level2, 'tamanho_vnr\n> 5 nós\n(NÃO)',
             unselected_color, width=1.8, height=0.7, selected=False)

    draw_arrow(x_left1, y_level1-0.35, x_left2a, y_level2+0.35, 'Sim', selected=True)
    draw_arrow(x_left1, y_level1-0.35, x_left2b, y_level2+0.35, 'Não', selected=False)

    # Lado direito (não selecionado - mostrar em cinza)
    draw_node(5.5, y_level2, '(...)', unselected_color, width=1.5, height=0.5, selected=False)
    draw_arrow(x_right1, y_level1-0.35, 5.5, y_level2+0.25, '', selected=False)

    # Nível 3: Terceiro Split - Mostra o caminho selecionado
    y_level3 = 4.5
    x_left3a = 0.3
    x_left3b = 1.7

    # Lado esquerdo SIM (selecionado)
    draw_node(x_left3a, y_level3, 'utilização_nós\n> 70%\nSIM ✓',
             selected_color, width=1.6, height=0.7, selected=True)

    # Lado esquerdo NÃO (não selecionado)
    draw_node(x_left3b, y_level3, 'utilização_nós\n≤ 70%\n(NÃO)',
             unselected_color, width=1.6, height=0.7, selected=False)

    draw_arrow(x_left2a, y_level2-0.35, x_left3a, y_level3+0.35, 'Sim', selected=True)
    draw_arrow(x_left2a, y_level2-0.35, x_left3b, y_level3+0.35, 'Não', selected=False)

    # Resultado Final: FOLHA
    y_leaf = 2.8
    draw_node(x_left3a, y_leaf, 'RESULTADO\nSelecione: MIP\n(Exato, Ótimo\npara Congestionamento)',
             leaf_selected, width=1.8, height=1.0, selected=True)

    draw_arrow(x_left3a, y_level3-0.35, x_left3a, y_leaf+0.5, '', selected=True)

    # Regra resumida
    ax.text(5, 1.2, 'REGRA EXTRAÍDA:', fontsize=12, weight='bold', ha='center')
    ax.text(5, 0.7,
           'SE (utilização_nodes ≤ 60%) E\n(tamanho_vnr ≤ 5 nós) E\n(utilização_nós > 70%)',
           fontsize=10, ha='center',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    ax.text(5, -0.3,
           'ENTÃO selecione MIP\n(garantido ótimo em cenário de congestionamento)',
           fontsize=10, ha='center', style='italic',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))

    # Legenda
    ax.text(0.3, 9.8, '━━━ Caminho Selecionado (VERDE)',
           fontsize=9, weight='bold', color='darkgreen')
    ax.text(4, 9.8, '━━━ Caminhos Não Selecionados (CINZA)',
           fontsize=9, weight='bold', color='gray')

    plt.tight_layout()
    plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf/tree_example_path.png',
               dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Criado: tree_example_path.png")
    plt.close()


def create_tree_visualization_example():
    """Cria figura com exemplo de visualização de árvore simplificada."""
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Cores
    node_color = '#E8F4F8'
    leaf_color = '#FFE5E5'

    # Função para desenhar nó simplificado
    def draw_simple_node(x, y, text, width=1.2, height=0.5):
        box = mpatches.FancyBboxPatch((x-width/2, y-height/2), width, height,
                                     boxstyle="round,pad=0.05",
                                     edgecolor='navy', facecolor=node_color, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=14, weight='bold')

    # Função para desenhar seta
    def draw_arrow_simple(x1, y1, x2, y2, label=''):
        arrow = mpatches.FancyArrowPatch((x1, y1), (x2, y2),
                                        arrowstyle='->', mutation_scale=15,
                                        linewidth=1.5, color='navy')
        ax.add_patch(arrow)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx+0.2, my, label, fontsize=12, style='italic')

    # Árvore simplificada (3 níveis)
    # Nível 0
    draw_simple_node(5, 9, 'root\n8000 samples', width=1.5, height=0.6)

    # Nível 1
    draw_simple_node(2, 7.5, 'feature_4\nvalue < 0.5', width=1.4, height=0.6)
    draw_simple_node(8, 7.5, 'feature_2\nvalue > 0.3', width=1.4, height=0.6)

    draw_arrow_simple(4.2, 8.7, 2.7, 7.8)
    draw_arrow_simple(5.8, 8.7, 7.3, 7.8)

    # Nível 2 (esquerda)
    draw_simple_node(0.5, 6, 'class: MIP\n2100', width=1.2, height=0.6)
    draw_simple_node(3.5, 6, 'feature_7\nvalue < 0.8', width=1.2, height=0.6)

    draw_arrow_simple(1.2, 7.2, 0.8, 6.3)
    draw_arrow_simple(2.3, 7.2, 3.2, 6.3)

    # Nível 2 (direita)
    draw_simple_node(6.5, 6, 'class: GA\n1800', width=1.2, height=0.6)
    draw_simple_node(9.5, 6, 'class: PSO\n2200', width=1.2, height=0.6)

    draw_arrow_simple(7.6, 7.2, 7.2, 6.3)
    draw_arrow_simple(8.4, 7.2, 9.2, 6.3)

    # Nível 3 (folhas)
    draw_simple_node(2.5, 4.5, 'class: GA-Meta\n950', width=1.2, height=0.6)
    draw_simple_node(4.5, 4.5, 'class: SA-Meta\n650', width=1.2, height=0.6)

    draw_arrow_simple(3.2, 5.7, 2.8, 4.8)
    draw_arrow_simple(3.8, 5.7, 4.2, 4.8)

    # Título e descrição
    ax.text(5, 2.8, 'Árvore de Decisão Treinada para Seleção de Algoritmo VNE',
           ha='center', fontsize=16, weight='bold')

    ax.text(5, 2.2, 'Exemplo: Árvore com 3 níveis, 1024 nós totais de dados particionados recursivamente',
           ha='center', fontsize=14, style='italic')

    ax.text(5, 1.6, 'Cada caminho raiz→folha representa uma regra de decisão automaticamente aprendida',
           ha='center', fontsize=12)

    ax.text(5, 1.0, 'Números entre parênteses indicam quantidade de VNRs em cada partição durante treinamento',
           ha='center', fontsize=11, color='gray')

    plt.tight_layout()
    plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf/tree_visualization_example.png',
               dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Criado: tree_visualization_example.png")
    plt.close()


def create_tree_example_path_english():
    """Creates figure with concrete example of decision path - English version."""
    fig, ax = plt.subplots(figsize=(20, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(2.5, 10.5)
    ax.axis('off')

    # Colors
    selected_color = '#FFD700'    # Gold (selected path)
    unselected_color = '#E8E8E8'  # Light gray (not selected)
    leaf_selected = '#90EE90'     # Light green (result leaf)

    # Function to draw node
    def draw_node(x, y, text, color, width=1.2, height=0.6, selected=False, linewidth=2):
        lw = 4 if selected else linewidth
        box = FancyBboxPatch((x-width/2, y-height/2), width, height,
                            boxstyle="round,pad=0.1",
                            edgecolor='darkgreen' if selected else 'black',
                            facecolor=color, linewidth=lw)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=18, weight='bold')

    # Function to draw arrow
    def draw_arrow(x1, y1, x2, y2, label='', selected=False):
        color = 'darkgreen' if selected else 'gray'
        lw = 4 if selected else 2
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                              arrowstyle='->', mutation_scale=25,
                              linewidth=lw, color=color)
        ax.add_patch(arrow)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx+0.3, my, label, fontsize=18, style='italic', weight='bold' if selected else 'normal',
                   bbox=dict(boxstyle='round', facecolor='yellow' if selected else 'white', alpha=0.9))

    # Level 0: Root
    y_level0 = 9
    draw_node(5, y_level0, 'ROOT\nAll Data', selected_color,
             width=2.5, height=0.8, selected=True)

    # Level 1: First Split - Shows selected path
    y_level1 = 7.5
    x_left1 = 2.5
    x_right1 = 7.5

    # Left side: YES (selected)
    draw_node(x_left1, y_level1, 'node_utilization\n≤ 60%\nYES ✓',
             selected_color, width=2.4, height=0.7, selected=True)

    # Right side: NO (not selected)
    draw_node(x_right1, y_level1, 'node_utilization\n> 60%\n(NO)',
             unselected_color, width=2.4, height=0.7, selected=False)

    draw_arrow(5, y_level0-0.4, x_left1, y_level1+0.35, 'Yes', selected=True)
    draw_arrow(5, y_level0-0.4, x_right1, y_level1+0.35, 'No', selected=False)

    # Level 2: Second Split - Shows selected path
    y_level2 = 6
    x_left2a = 1.2
    x_left2b = 4

    # Left side YES (selected)
    draw_node(x_left2a, y_level2, 'vnr_size\n≤ 5 nodes\nYES ✓',
             selected_color, width=2.0, height=0.7, selected=True)

    # Left side NO (not selected)
    draw_node(x_left2b, y_level2, 'vnr_size\n> 5 nodes\n(NO)',
             unselected_color, width=2.0, height=0.7, selected=False)

    draw_arrow(x_left1, y_level1-0.35, x_left2a, y_level2+0.35, 'Yes', selected=True)
    draw_arrow(x_left1, y_level1-0.35, x_left2b, y_level2+0.35, 'No', selected=False)

    # Right side (not selected - show in gray)
    draw_node(5.5, y_level2, '(...)', unselected_color, width=1.5, height=0.5, selected=False)
    draw_arrow(x_right1, y_level1-0.35, 5.5, y_level2+0.25, '', selected=False)

    # Level 3: Third Split - Shows selected path
    y_level3 = 4.5
    x_left3a = 1.1
    x_left3b = 3.0

    # Left side YES (selected)
    draw_node(x_left3a, y_level3, 'node_utilization\n> 70%\nYES ✓',
             selected_color, width=2.0, height=0.7, selected=True)

    # Left side NO (not selected)
    draw_node(x_left3b, y_level3, 'node_utilization\n≤ 70%\n(NO)',
             unselected_color, width=2.0, height=0.7, selected=False)

    draw_arrow(x_left2a, y_level2-0.35, x_left3a, y_level3+0.35, 'Yes', selected=True)
    draw_arrow(x_left2a, y_level2-0.35, x_left3b, y_level3+0.35, 'No', selected=False)

    # Final Result: LEAF
    y_leaf = 3.0
    draw_node(x_left3a, y_leaf, 'RESULT\nSelect: MIP\n(Exact, Optimal\nfor Congestion)',
             leaf_selected, width=2.0, height=1.0, selected=True)

    draw_arrow(x_left3a, y_level3-0.35, x_left3a, y_leaf+0.5, '', selected=True)

    # Legend
    ax.text(0.3, 9.8, '━━━ Selected Path (GREEN)',
           fontsize=18, weight='bold', color='darkgreen')
    ax.text(4, 9.8, '━━━ Non-Selected Paths (GRAY)',
           fontsize=18, weight='bold', color='gray')

    plt.tight_layout()
    plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf/tree_example_path_en.png',
               dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Created: tree_example_path_en.png")
    plt.close()


def create_tree_visualization_example_english():
        """Creates figure with simplified tree visualization example - English version."""
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Colors
        node_color = '#E8F4F8'
        leaf_color = '#FFE5E5'

        # Function to draw simplified node
        def draw_simple_node(x, y, text, width=1.8, height=0.8):
            box = mpatches.FancyBboxPatch((x-width/2, y-height/2), width, height,
                                         boxstyle="round,pad=0.05",
                                         edgecolor='navy', facecolor=node_color, linewidth=2.0)
            ax.add_patch(box)
            ax.text(x, y, text, ha='center', va='center', fontsize=18, weight='bold')

        # Function to draw arrow
        def draw_arrow_simple(x1, y1, x2, y2, label=''):
            arrow = mpatches.FancyArrowPatch((x1, y1), (x2, y2),
                                            arrowstyle='->', mutation_scale=15,
                                            linewidth=1.5, color='navy')
            ax.add_patch(arrow)
            if label:
                mx, my = (x1+x2)/2, (y1+y2)/2
                ax.text(mx+0.2, my, label, fontsize=12, style='italic')

        # Simplified tree (3 levels)
        # Level 0
        draw_simple_node(5, 9, 'root\n8000 samples', width=2.0, height=0.8)

        # Level 1
        draw_simple_node(2, 7.5, 'feature_4\nvalue < 0.5', width=1.8, height=0.8)
        draw_simple_node(8, 7.5, 'feature_2\nvalue > 0.3', width=1.8, height=0.8)

        draw_arrow_simple(4.2, 8.7, 2.7, 7.8)
        draw_arrow_simple(5.8, 8.7, 7.3, 7.8)

        # Level 2 (left)
        draw_simple_node(0.5, 6, 'class: MIP\n2100', width=1.8, height=0.8)
        draw_simple_node(3.5, 6, 'feature_7\nvalue < 0.8', width=1.8, height=0.8)

        draw_arrow_simple(1.2, 7.2, 0.8, 6.3)
        draw_arrow_simple(2.3, 7.2, 3.2, 6.3)

        # Level 2 (right)
        draw_simple_node(6.5, 6, 'class: GA\n1800', width=1.8, height=0.8)
        draw_simple_node(9.5, 6, 'class: PSO\n2200', width=1.8, height=0.8)

        draw_arrow_simple(7.6, 7.2, 7.2, 6.3)
        draw_arrow_simple(8.4, 7.2, 9.2, 6.3)

        # Level 3 (leaves)
        draw_simple_node(2.5, 4.5, 'class: GA-Meta\n950', width=1.8, height=0.8)
        draw_simple_node(4.5, 4.5, 'class: SA-Meta\n650', width=1.8, height=0.8)

        draw_arrow_simple(3.2, 5.7, 2.8, 4.8)
        draw_arrow_simple(3.8, 5.7, 4.2, 4.8)

        # Title and description
        ax.text(5, 2.8, 'Trained Decision Tree for VNE Algorithm Selection',
               ha='center', fontsize=30, weight='bold')

        ax.text(5, 2.2, 'Example: Tree with 3 levels, 1024 total data nodes recursively partitioned',
               ha='center', fontsize=26, style='italic')

        ax.text(5, 1.6, 'Each root→leaf path represents an automatically learned decision rule',
               ha='center', fontsize=28)

        ax.text(5, 1.0, 'Numbers in parentheses indicate quantity of VNRs in each partition during training',
               ha='center', fontsize=26, color='gray')

        plt.tight_layout()
        plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf/tree_visualization_example_en.png',
                   dpi=300, bbox_inches='tight', facecolor='white')
        print("✅ Created: tree_visualization_example_en.png")
        plt.close()


if __name__ == '__main__':
    print("Gerando figuras de árvore de decisão...")
    create_tree_structure()
    create_tree_example_path()
    create_tree_example_path_english()
    create_tree_visualization_example()
    create_tree_visualization_example_english()
    print("\n✅ Todas as figuras foram criadas com sucesso!")
    print("\nArquivos gerados:")
    print("  - tree_structure.png")
    print("  - tree_example_path.png")
    print("  - tree_example_path_en.png")
    print("  - tree_visualization_example.png")
    print("  - tree_visualization_example_en.png")