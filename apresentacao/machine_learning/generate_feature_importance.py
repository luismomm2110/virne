import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Configuração de estilo
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11

# Criar figura
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Título principal
ax.text(5, 11.5, 'Importância das Features - Modelo XGBoost',
        ha='center', va='top', fontsize=20, fontweight='bold')
ax.text(5, 11.0, 'Top 5 Características que Determinam a Seleção de Algoritmo VNE',
        ha='center', va='top', fontsize=13, style='italic', color='#555')

# Dados de importância
importance_data = [
    ('topology_encoded', 27.90, 'Tipo de topologia (Tree vs Fat-Tree)', '#9b59b6', 'Contexto'),
    ('v_net_size_ratio', 16.06, 'Razão tamanho VNR / P-Net', '#3498db', 'VNR'),
    ('p_net_link_util', 1.44, 'Utilização média dos enlaces', '#e74c3c', 'Rede Física'),
    ('p_net_node_util', 1.08, 'Utilização média dos nós', '#e74c3c', 'Rede Física'),
    ('p_net_overall_util', 0.79, 'Utilização geral da rede', '#e74c3c', 'Rede Física'),
]

# Normalizar para percentual
total_importance = sum([x[1] for x in importance_data])
importance_percentages = [(x[0], x[1], x[2], x[3], x[4], (x[1]/total_importance)*100)
                          for x in importance_data]

# Desenhar barras horizontais
y_start = 9.5
bar_height = 0.8
spacing = 0.6

for i, (feature, gain, description, color, category, percentage) in enumerate(importance_percentages):
    y_pos = y_start - i * (bar_height + spacing)

    # Desenhar barra
    max_bar_width = 7.5
    bar_width = (gain / 27.90) * max_bar_width  # Normalizar pela maior

    # Barra com gradiente simulado
    bar = FancyBboxPatch((1.5, y_pos - bar_height/2), bar_width, bar_height,
                         boxstyle="round,pad=0.05",
                         facecolor=color,
                         edgecolor=color,
                         linewidth=2,
                         alpha=0.7)
    ax.add_patch(bar)

    # Rank number (grande)
    rank_circle = plt.Circle((0.5, y_pos), 0.35,
                            facecolor=color,
                            edgecolor='white',
                            linewidth=3,
                            zorder=10)
    ax.add_patch(rank_circle)
    ax.text(0.5, y_pos, str(i+1),
            ha='center', va='center', fontsize=18, fontweight='bold',
            color='white', zorder=11)

    # Nome da feature
    ax.text(1.2, y_pos + 0.15, feature,
            ha='right', va='center', fontsize=12, fontweight='bold')

    # Categoria (tag)
    category_box = FancyBboxPatch((1.2, y_pos - 0.35), 0.8, 0.25,
                                 boxstyle="round,pad=0.03",
                                 facecolor=color,
                                 alpha=0.3)
    ax.add_patch(category_box)
    ax.text(1.6, y_pos - 0.225, category,
            ha='center', va='center', fontsize=8, style='italic')

    # Valor de importância (dentro da barra)
    if bar_width > 2:
        ax.text(1.5 + bar_width - 0.3, y_pos, f'{gain:.2f}',
                ha='right', va='center', fontsize=14, fontweight='bold',
                color='white')
    else:
        ax.text(1.5 + bar_width + 0.2, y_pos, f'{gain:.2f}',
                ha='left', va='center', fontsize=14, fontweight='bold',
                color=color)

    # Percentual
    ax.text(9.2, y_pos, f'{percentage:.1f}%',
            ha='left', va='center', fontsize=11, fontweight='bold',
            color=color)

    # Descrição
    ax.text(1.5, y_pos - 0.5, description,
            ha='left', va='top', fontsize=10, color='#666', style='italic')

# Linha divisória
ax.plot([0.2, 9.8], [4.5, 4.5], 'k--', alpha=0.3, linewidth=1)

# Seção de insights
insight_y = 4.0
ax.text(5, insight_y, '🔍 Principais Descobertas',
        ha='center', va='top', fontsize=15, fontweight='bold')

insights = [
    ('DOMINÂNCIA DA TOPOLOGIA',
     'topology_encoded sozinha representa 58,8% da importância total.\nO tipo de rede física é o fator mais determinante.',
     '#9b59b6'),

    ('TAMANHO IMPORTA',
     'v_net_size_ratio (33,9%) mostra que requisições grandes/pequenas\nprecisamde algoritmos diferentes.',
     '#3498db'),

    ('ESTADO DA REDE',
     'As 3 features de utilização (7,3% combinadas) indicam que\no congestionamento influencia mas não domina a decisão.',
     '#e74c3c'),
]

insight_y -= 0.7
box_width = 9.0
box_height = 0.9

for title, text, color in insights:
    # Box do insight
    insight_box = FancyBboxPatch((0.5, insight_y - box_height), box_width, box_height,
                                boxstyle="round,pad=0.1",
                                facecolor=color,
                                alpha=0.15,
                                edgecolor=color,
                                linewidth=2)
    ax.add_patch(insight_box)

    # Título do insight
    ax.text(0.7, insight_y - 0.15, title,
            ha='left', va='top', fontsize=11, fontweight='bold', color=color)

    # Texto do insight
    ax.text(0.7, insight_y - 0.35, text,
            ha='left', va='top', fontsize=9, color='#333')

    insight_y -= (box_height + 0.2)

# Conclusão em destaque
conclusion_y = 0.8
conclusion_box = FancyBboxPatch((0.3, conclusion_y - 0.6), 9.4, 0.55,
                               boxstyle="round,pad=0.1",
                               facecolor='#f39c12',
                               alpha=0.2,
                               edgecolor='#f39c12',
                               linewidth=3)
ax.add_patch(conclusion_box)

ax.text(5, conclusion_y - 0.15, '💡 CONCLUSÃO PRINCIPAL',
        ha='center', va='top', fontsize=12, fontweight='bold', color='#f39c12')

ax.text(5, conclusion_y - 0.4,
        'A topologia da rede e o tamanho relativo da VNR determinam 92,7% das decisões do modelo.',
        ha='center', va='top', fontsize=11, color='#333')

# Adicionar legenda de métrica
ax.text(9.5, 10.2, 'Gain', ha='center', va='center', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#ecf0f1'))

# Salvar
plt.tight_layout()
plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/machine_learning/feature_importance_detailed.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Gráfico de importância de features salvo em: apresentacao/machine_learning/feature_importance_detailed.png")

plt.close()

# Criar segunda visualização - Gráfico de pizza
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Gráfico de pizza 1 - Top 5
colors_pie = ['#9b59b6', '#3498db', '#e74c3c', '#e74c3c', '#e74c3c']
explode = (0.1, 0.05, 0, 0, 0)

labels = [f"{data[0]}\n{data[1]:.2f}" for data in importance_data]
sizes = [data[1] for data in importance_data]

wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
                                     autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)

ax1.set_title('Distribuição da Importância\nTop 5 Features', fontsize=14, fontweight='bold', pad=20)

# Gráfico de pizza 2 - Agrupado por categoria
category_importance = {
    'Topologia': 27.90,
    'Tamanho VNR': 16.06,
    'Estado Rede Física': 1.44 + 1.08 + 0.79,
}

colors_cat = ['#9b59b6', '#3498db', '#e74c3c']
explode_cat = (0.1, 0.05, 0)

labels_cat = [f"{k}\n{v:.2f}" for k, v in category_importance.items()]
sizes_cat = list(category_importance.values())

wedges2, texts2, autotexts2 = ax2.pie(sizes_cat, explode=explode_cat, labels=labels_cat,
                                        colors=colors_cat, autopct='%1.1f%%', startangle=90,
                                        textprops={'fontsize': 11})

for autotext in autotexts2:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(12)

ax2.set_title('Importância por Categoria', fontsize=14, fontweight='bold', pad=20)

plt.suptitle('Análise de Importância das Features - XGBoost VNE',
             fontsize=16, fontweight='bold', y=0.98)

plt.tight_layout()
plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/machine_learning/feature_importance_pies.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Gráfico de pizza salvo em: apresentacao/machine_learning/feature_importance_pies.png")

plt.close()

print("\n✅ Ambas as visualizações foram geradas com sucesso!")