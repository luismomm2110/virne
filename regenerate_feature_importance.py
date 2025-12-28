#!/usr/bin/env python3
"""
Script para regenerar a figura de importância de features
"""

import json
import pickle
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import xgboost as xgb

# Carregar modelo da pasta apresentacao (o correto usado no artigo)
model_path = "apresentacao/machine_learning/models/xgb_best_overall_model.pkl"
encoder_path = "apresentacao/machine_learning/models/xgb_best_overall_model_label_encoder.pkl"
output_path = "xgboost_v2/outputs/feature_importance.png"

print(f"📂 Carregando modelo: {model_path}")

# Carregar modelo e encoder
with open(model_path, 'rb') as f:
    model = pickle.load(f)

with open(encoder_path, 'rb') as f:
    label_encoder = pickle.load(f)

print(f"   ✓ Modelo carregado: {type(model)}")
print(f"   ✓ Classes: {label_encoder.classes_}")

# Tentar obter feature names do modelo
try:
    feature_names = model.get_booster().feature_names
    if feature_names is None:
        # Features padrão baseadas na documentação do artigo
        feature_names = [
            'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
            'v_net_demand_per_node', 'v_net_demand_per_enlace', 'v_net_connectivity',
            'v_net_total_demand', 'v_net_node_to_enlace_demand_ratio', 'v_net_lifetime',
            'p_net_available_resource', 'p_net_node_util', 'p_net_enlace_util', 'p_net_overall_util',
            'inservice_count', 'system_load', 'num_running_p_net_nodes',
            'topology_encoded'
        ]
except:
    # Features padrão baseadas na documentação do artigo
    feature_names = [
        'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
        'v_net_demand_per_node', 'v_net_demand_per_enlace', 'v_net_connectivity',
        'v_net_total_demand', 'v_net_node_to_enlace_demand_ratio', 'v_net_lifetime',
        'p_net_available_resource', 'p_net_node_util', 'p_net_enlace_util', 'p_net_overall_util',
        'inservice_count', 'system_load', 'num_running_p_net_nodes',
        'topology_encoded'
    ]

print(f"   ✓ Features: {len(feature_names)}")

# Obter importância das features
importance = model.feature_importances_
indices = np.argsort(importance)[::-1]

# Criar figura
plt.figure(figsize=(12, 8))
plt.title('Feature Importance in XGBoost Algorithm Selector', fontsize=16, fontweight='bold', pad=20)

# Bar plot
bars = plt.barh(range(len(importance)), importance[indices], color='steelblue', edgecolor='black', linewidth=1.2)

# Configurar eixos
plt.yticks(range(len(importance)), [feature_names[i] for i in indices], fontsize=11)
plt.xlabel('Importance Score', fontsize=13, fontweight='bold')
plt.ylabel('Features', fontsize=13, fontweight='bold')

# Adicionar valores
for i, (bar, val) in enumerate(zip(bars, importance[indices])):
    plt.text(val + 0.005, i, f'{val:.4f}', va='center', fontsize=9, fontweight='bold')

# Grid
plt.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Figura salva: {output_path}")

# Copiar para template
template_path = "apresentacao/template/feature_importance.png"
import shutil
shutil.copy(output_path, template_path)
print(f"✓ Figura copiada para: {template_path}")

# Mostrar top features
print("\n📊 Top 5 features mais importantes:")
for i in range(min(5, len(importance))):
    idx = indices[i]
    print(f"   {i+1}. {feature_names[idx]:30s}: {importance[idx]:.4f}")

plt.close()