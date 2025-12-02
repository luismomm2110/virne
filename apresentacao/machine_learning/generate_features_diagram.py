import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Configuração de estilo
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

# Criar figura
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Título principal
ax.text(5, 11.3, 'Features Utilizadas no Modelo XGBoost',
        ha='center', va='top', fontsize=18, fontweight='bold')
ax.text(5, 10.8, '17 Características para Seleção Dinâmica de Algoritmos VNE',
        ha='center', va='top', fontsize=12, style='italic', color='#555')

# Cores para cada categoria
colors = {
    'vnr': '#3498db',      # Azul
    'pnet': '#e74c3c',     # Vermelho
    'system': '#2ecc71',   # Verde
    'context': '#9b59b6'   # Roxo
}

# Definir features por categoria
features = {
    'Características da VNR (9)': {
        'color': colors['vnr'],
        'items': [
            'v_net_num_nodes - Número de nós virtuais',
            'v_net_num_edges - Número de enlaces virtuais',
            'v_net_size_ratio - Razão tamanho VNR / P-Net',
            'v_net_demand_per_node - Demanda média por nó',
            'v_net_demand_per_link - Demanda média por enlace',
            'v_net_connectivity - Densidade de conexões',
            'v_net_total_demand - Demanda total de recursos',
            'v_net_node_to_link_demand_ratio - Razão demanda nós/enlaces',
            'v_net_lifetime - Tempo de vida da requisição'
        ]
    },
    'Estado da Rede Física (4)': {
        'color': colors['pnet'],
        'items': [
            'p_net_available_resource - Recursos disponíveis totais',
            'p_net_node_util - Utilização média dos nós',
            'p_net_link_util - Utilização média dos enlaces',
            'p_net_overall_util - Utilização geral da rede'
        ]
    },
    'Estado do Sistema (3)': {
        'color': colors['system'],
        'items': [
            'inservice_count - Quantidade de VNRs ativas',
            'system_load - Carga normalizada do sistema',
            'num_running_p_net_nodes - Nós físicos em uso'
        ]
    },
    'Contexto (1)': {
        'color': colors['context'],
        'items': [
            'topology_encoded - Tipo de topologia (Tree vs Fat-Tree)'
        ]
    }
}

# Posição inicial
y_pos = 9.5
box_height = 0.35
spacing = 0.15

# Desenhar cada categoria
for category, data in features.items():
    # Título da categoria
    ax.text(0.3, y_pos, category,
            ha='left', va='top', fontsize=13, fontweight='bold',
            color=data['color'])

    y_pos -= 0.5

    # Desenhar cada feature
    for i, feature in enumerate(data['items']):
        # Box colorido
        box = FancyBboxPatch((0.5, y_pos - box_height), 8.5, box_height,
                             boxstyle="round,pad=0.05",
                             edgecolor=data['color'],
                             facecolor=data['color'],
                             alpha=0.15,
                             linewidth=2)
        ax.add_patch(box)

        # Texto da feature
        ax.text(0.7, y_pos - box_height/2, feature,
                ha='left', va='center', fontsize=10)

        y_pos -= (box_height + spacing)

    y_pos -= 0.3  # Espaço extra entre categorias

# Adicionar legenda de importância
legend_y = 1.5
ax.text(5, legend_y, 'Top 5 Features Mais Importantes (Gain):',
        ha='center', va='top', fontsize=11, fontweight='bold')

importance_data = [
    ('1. topology_encoded', 27.90),
    ('2. v_net_size_ratio', 16.06),
    ('3. p_net_link_util', 1.44),
    ('4. p_net_node_util', 1.08),
    ('5. p_net_overall_util', 0.79)
]

legend_y -= 0.4
for feature, importance in importance_data:
    # Barra de importância
    bar_width = importance / 30 * 3  # Normalizar para caber na visualização
    bar = FancyBboxPatch((5 - bar_width/2, legend_y - 0.15), bar_width, 0.2,
                         boxstyle="round,pad=0.01",
                         facecolor='#f39c12',
                         alpha=0.7)
    ax.add_patch(bar)

    # Texto
    ax.text(2, legend_y, feature, ha='left', va='center', fontsize=9)
    ax.text(8, legend_y, f'{importance:.2f}', ha='right', va='center',
            fontsize=9, fontweight='bold', color='#f39c12')

    legend_y -= 0.35

# Rodapé com estatísticas
footer_y = 0.3
ax.text(5, footer_y,
        'Total: 17 Features | Acurácia do Modelo: 93,33% | F1-Score: 92,36%',
        ha='center', va='center', fontsize=10,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.8))

# Salvar
plt.tight_layout()
plt.savefig('/Users/luismomm/PycharmProjects/virne/apresentacao/machine_learning/features_diagram.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Diagrama de features salvo em: apresentacao/machine_learning/features_diagram.png")

plt.show()