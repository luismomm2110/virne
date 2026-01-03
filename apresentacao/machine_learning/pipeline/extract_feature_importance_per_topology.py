#!/usr/bin/env python3
"""
Extrai e exibe as features mais importantes por topologia e objetivo
dos modelos decision_trees_per_topology.pkl

Uso: python3 extract_feature_importance_per_topology.py
Requer: ambiente conda virne ativado ou scikit-learn instalado
"""

import pickle
import json
import sys
import os

# Adicionar caminho do conda env se disponível
conda_python = '/Users/luismomm/miniconda3/envs/virne/bin/python3'
if os.path.exists(conda_python) and sys.executable != conda_python:
    print(f"NOTA: Para garantir compatibilidade, execute com: {conda_python} extract_feature_importance_per_topology.py")
    print(f"Ou ative o ambiente conda: conda activate virne\n")

def get_top_features_by_importance(model, features, top_n=10):
    """Extrai as top N features mais importantes de um modelo."""
    if not hasattr(model, 'feature_importances_'):
        return []
    
    importances = model.feature_importances_
    
    # Criar lista de (feature, importance) e ordenar
    feat_imp = list(zip(features, importances))
    feat_imp.sort(key=lambda x: x[1], reverse=True)
    
    return feat_imp[:top_n]

def main():
    """Extrai e exibe features importantes por topologia e objetivo."""
    
    model_path = '../models/decision_trees_per_topology.pkl'
    
    print("="*80)
    print("FEATURES MAIS IMPORTANTES POR TOPOLOGIA E OBJETIVO")
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
    
    # Processar cada topologia
    for topo_name in sorted(models.keys()):
        print(f"\n{'='*80}")
        print(f"TOPOLOGIA: {topo_name.upper()}")
        print(f"{'='*80}")
        
        for obj_key in sorted(models[topo_name].keys()):
            model_info = models[topo_name][obj_key]
            model = model_info['model']
            features = model_info.get('features', [])
            
            print(f"\n  {objectives.get(obj_key, obj_key).upper()}:")
            print(f"  {'-'*76}")
            
            top_features = get_top_features_by_importance(model, features, top_n=10)
            
            if top_features:
                for i, (feat, imp) in enumerate(top_features, 1):
                    print(f"    {i:2d}. {feat:50s} {imp:.4f}")
            else:
                print("    (Importância de features não disponível)")
    
    # Resumo: features mais importantes em geral
    print(f"\n{'='*80}")
    print("RESUMO: TOP 15 FEATURES MAIS IMPORTANTES (MÉDIA GERAL)")
    print(f"{'='*80}")
    
    # Agregar todas as importâncias
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
    
    # Calcular média
    avg_imp = {feat: all_feat_imp[feat] / count_feat[feat] 
               for feat in all_feat_imp.keys()}
    
    # Ordenar e mostrar top 15
    sorted_features = sorted(avg_imp.items(), key=lambda x: x[1], reverse=True)
    
    for i, (feat, imp) in enumerate(sorted_features[:15], 1):
        print(f"  {i:2d}. {feat:50s} {imp:.4f}")
    
    # Por objetivo
    print(f"\n{'='*80}")
    print("TOP 10 FEATURES POR OBJETIVO (MÉDIA ENTRE TOPOLOGIAS)")
    print(f"{'='*80}")
    
    for obj_key in sorted(objectives.keys()):
        print(f"\n  {objectives[obj_key].upper()}:")
        print(f"  {'-'*76}")
        
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
            
            for i, (feat, imp) in enumerate(obj_sorted[:10], 1):
                print(f"    {i:2d}. {feat:48s} {imp:.4f}")
    
    # Por topologia
    print(f"\n{'='*80}")
    print("TOP 10 FEATURES POR TOPOLOGIA (MÉDIA ENTRE OBJETIVOS)")
    print(f"{'='*80}")
    
    for topo_name in sorted(models.keys()):
        print(f"\n  {topo_name.upper()}:")
        print(f"  {'-'*76}")
        
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
            
            for i, (feat, imp) in enumerate(topo_sorted[:10], 1):
                print(f"    {i:2d}. {feat:48s} {imp:.4f}")

if __name__ == '__main__':
    main()

