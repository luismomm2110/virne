#!/usr/bin/env python3
"""
Gera gráficos de importância de features por topologia e objetivo
dos modelos decision_trees_per_topology.pkl
"""

import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9

def get_top_features(model, features, top_n=10):
    """Extrai as top N features mais importantes de um modelo."""
    if not hasattr(model, 'feature_importances_'):
        return []
    
    importances = model.feature_importances_
    feat_imp = list(zip(features, importances))
    feat_imp.sort(key=lambda x: x[1], reverse=True)
    
    return feat_imp[:top_n]

def plot_features_horizontal(features, importances, title, filename, top_n=10):
    """Plota gráfico de barras horizontal das features mais importantes."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Selecionar top N
    indices = np.arange(min(top_n, len(features)))
    
    # Criar gráfico de barras horizontal
    bars = ax.barh(indices, importances[:top_n], color='steelblue', edgecolor='black', linewidth=0.5)
    
    # Configurar labels
    ax.set_yticks(indices)
    ax.set_yticklabels([f[:45] for f in features[:top_n]], fontsize=9)
    ax.set_xlabel('Importance', fontweight='bold', fontsize=11)
    ax.set_title(title, fontweight='bold', fontsize=12, pad=10)
    
    # Inverter eixo Y para mostrar maior no topo
    ax.invert_yaxis()
    
    # Adicionar valores nas barras
    for i, (bar, imp) in enumerate(zip(bars, importances[:top_n])):
        width = bar.get_width()
        ax.text(width + max(importances[:top_n]) * 0.01, bar.get_y() + bar.get_height()/2,
               f'{imp:.4f}', ha='left', va='center', fontsize=8)
    
    # Grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✓ Salvo: {filename}")

def main():
    """Gera gráficos de importância de features."""
    
    model_path = '../models/decision_trees_per_topology.pkl'
    output_dir = '../results/feature_importance_plots'
    
    print("="*80)
    print("GERANDO GRÁFICOS DE IMPORTÂNCIA DE FEATURES")
    print("="*80)
    
    # Carregar modelos
    with open(model_path, 'rb') as f:
        models = pickle.load(f)
    
    objectives = {
        'rac': 'RAC',
        'lrc': 'LRC',
        'lar': 'LAR',
        'ast': 'AST',
        'balanced': 'Balanced'
    }
    
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    # ========================================================================
    # Gráficos por Topologia E Objetivo (15 gráficos)
    # ========================================================================
    print(f"\n1. Gerando gráficos por Topologia × Objetivo...")
    
    for topo_name in sorted(models.keys()):
        for obj_key in sorted(models[topo_name].keys()):
            model_info = models[topo_name][obj_key]
            model = model_info['model']
            features = model_info.get('features', [])
            
            top_features = get_top_features(model, features, top_n=15)
            
            if top_features:
                feat_names = [f[0] for f in top_features]
                feat_imps = [f[1] for f in top_features]
                
                title = f'Top Features - {topo_name.upper()} / {objectives.get(obj_key, obj_key).upper()}'
                filename = f'{output_dir}/per_topo_obj_{topo_name}_{obj_key}.png'
                
                plot_features_horizontal(feat_names, feat_imps, title, filename, top_n=15)
    
    # ========================================================================
    # Gráficos por Objetivo (média entre topologias) - 5 gráficos
    # ========================================================================
    print(f"\n2. Gerando gráficos por Objetivo (média entre topologias)...")
    
    for obj_key in sorted(objectives.keys()):
        obj_feat_imp = {}
        obj_count_feat = {}
        
        for topo_name in models.keys():
            if obj_key in models[topo_name]:
                model_info = models[topo_name][obj_key]
                model = model_info['model']
                features = model_info.get('features', [])
                
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    for feat, imp in zip(features, importances):
                        if feat not in obj_feat_imp:
                            obj_feat_imp[feat] = 0.0
                            obj_count_feat[feat] = 0
                        obj_feat_imp[feat] += imp
                        obj_count_feat[feat] += 1
        
        if obj_feat_imp:
            obj_avg = {feat: obj_feat_imp[feat] / obj_count_feat[feat] 
                      for feat in obj_feat_imp.keys()}
            obj_sorted = sorted(obj_avg.items(), key=lambda x: x[1], reverse=True)
            
            feat_names = [f[0] for f in obj_sorted]
            feat_imps = [f[1] for f in obj_sorted]
            
            title = f'Top Features - {objectives[obj_key].upper()} (Média entre Topologias)'
            filename = f'{output_dir}/per_objective_{obj_key}.png'
            
            plot_features_horizontal(feat_names, feat_imps, title, filename, top_n=15)
    
    # ========================================================================
    # Gráficos por Topologia (média entre objetivos) - 3 gráficos
    # ========================================================================
    print(f"\n3. Gerando gráficos por Topologia (média entre objetivos)...")
    
    for topo_name in sorted(models.keys()):
        topo_feat_imp = {}
        topo_count_feat = {}
        
        for obj_key in models[topo_name].keys():
            model_info = models[topo_name][obj_key]
            model = model_info['model']
            features = model_info.get('features', [])
            
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                for feat, imp in zip(features, importances):
                    if feat not in topo_feat_imp:
                        topo_feat_imp[feat] = 0.0
                        topo_count_feat[feat] = 0
                    topo_feat_imp[feat] += imp
                    topo_count_feat[feat] += 1
        
        if topo_feat_imp:
            topo_avg = {feat: topo_feat_imp[feat] / topo_count_feat[feat] 
                       for feat in topo_feat_imp.keys()}
            topo_sorted = sorted(topo_avg.items(), key=lambda x: x[1], reverse=True)
            
            feat_names = [f[0] for f in topo_sorted]
            feat_imps = [f[1] for f in topo_sorted]
            
            title = f'Top Features - {topo_name.upper()} (Média entre Objetivos)'
            filename = f'{output_dir}/per_topology_{topo_name}.png'
            
            plot_features_horizontal(feat_names, feat_imps, title, filename, top_n=15)
    
    # ========================================================================
    # Gráfico Geral (média de todos os modelos)
    # ========================================================================
    print(f"\n4. Gerando gráfico geral (média de todos os modelos)...")
    
    all_feat_imp = {}
    count_feat = {}
    
    for topo_name in models.keys():
        for obj_key in models[topo_name].keys():
            model_info = models[topo_name][obj_key]
            model = model_info['model']
            features = model_info.get('features', [])
            
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                for feat, imp in zip(features, importances):
                    if feat not in all_feat_imp:
                        all_feat_imp[feat] = 0.0
                        count_feat[feat] = 0
                    all_feat_imp[feat] += imp
                    count_feat[feat] += 1
    
    if all_feat_imp:
        avg_imp = {feat: all_feat_imp[feat] / count_feat[feat] 
                  for feat in all_feat_imp.keys()}
        sorted_features = sorted(avg_imp.items(), key=lambda x: x[1], reverse=True)
        
        feat_names = [f[0] for f in sorted_features]
        feat_imps = [f[1] for f in sorted_features]
        
        title = 'Top Features - Geral (Média de Todos os Modelos)'
        filename = f'{output_dir}/overall_average.png'
        
        plot_features_horizontal(feat_names, feat_imps, title, filename, top_n=20)
    
    # ========================================================================
    # Resumo
    # ========================================================================
    print(f"\n" + "="*80)
    print("GERAÇÃO DE GRÁFICOS COMPLETA!")
    print("="*80)
    print(f"\nGráficos salvos em: {output_dir}/")
    print(f"\nTotal de gráficos gerados:")
    print(f"  - Por Topologia × Objetivo: 15 gráficos")
    print(f"  - Por Objetivo (média): 5 gráficos")
    print(f"  - Por Topologia (média): 3 gráficos")
    print(f"  - Geral (média): 1 gráfico")
    print(f"  - TOTAL: 24 gráficos")

if __name__ == '__main__':
    main()

