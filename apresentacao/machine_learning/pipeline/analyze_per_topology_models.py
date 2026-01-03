#!/usr/bin/env python3
"""
Análise dos modelos decision_trees_per_topology.pkl
Extrai informações sobre estrutura, importância de features, e gera resumo
"""

import pickle
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

def analyze_per_topology_models():
    """Analisa os modelos por topologia e gera resumo detalhado."""
    
    # Caminho do arquivo
    model_path = '../models/decision_trees_per_topology.pkl'
    results_path = '../models/tree_results_per_topology.json'
    
    # Carregar modelos
    print("="*80)
    print("ANÁLISE DOS MODELOS POR TOPOLOGIA")
    print("="*80)
    print(f"\nCarregando modelos de: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"❌ Arquivo não encontrado: {model_path}")
        return
    
    with open(model_path, 'rb') as f:
        models = pickle.load(f)
    
    # Carregar resultados se existirem
    results = None
    if os.path.exists(results_path):
        with open(results_path, 'r') as f:
            results = json.load(f)
        print(f"✓ Carregados resultados de: {results_path}")
    
    print(f"✓ Modelos carregados com sucesso!")
    
    # Objetivos
    objectives = {
        'rac': 'Request Acceptance Rate (RAC)',
        'lrc': 'Long-Term Revenue-to-Cost (LRC)',
        'lar': 'Long-Term Average Revenue (LAR)',
        'ast': 'Average Solving Time (AST)',
        'balanced': 'Balanced'
    }
    
    # Estrutura dos modelos
    print("\n" + "="*80)
    print("ESTRUTURA DOS MODELOS")
    print("="*80)
    
    print(f"\nTopologias disponíveis: {list(models.keys())}")
    print(f"Total de topologias: {len(models)}")
    
    # Analisar cada topologia
    all_importance_data = []
    summary_data = []
    
    for topo_name in sorted(models.keys()):
        print(f"\n{'-'*80}")
        print(f"TOPOLOGIA: {topo_name.upper()}")
        print(f"{'-'*80}")
        
        topo_models = models[topo_name]
        print(f"  Objetivos disponíveis: {list(topo_models.keys())}")
        print(f"  Total de modelos: {len(topo_models)}")
        
        for obj_key in sorted(topo_models.keys()):
            model_info = topo_models[obj_key]
            
            print(f"\n  Objetivo: {obj_key.upper()} - {objectives.get(obj_key, obj_key)}")
            
            # Informações do modelo
            model = model_info['model']
            features = model_info.get('features', [])
            encoder = model_info.get('encoder', None)
            
            print(f"    - Tipo: {type(model).__name__}")
            print(f"    - Features: {len(features)}")
            
            if hasattr(model, 'max_depth'):
                print(f"    - Max Depth: {model.max_depth}")
            if hasattr(model, 'n_classes_'):
                print(f"    - Classes: {model.n_classes_}")
            if encoder is not None and hasattr(encoder, 'classes_'):
                print(f"    - Algoritmos: {list(encoder.classes_)}")
            
            # Extrair importância de features
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                
                # Criar DataFrame para esta combinação
                df = pd.DataFrame({
                    'feature': features,
                    'importance': importances,
                    'topology': topo_name,
                    'objective': obj_key,
                    'objective_name': objectives.get(obj_key, obj_key)
                })
                
                # Ordenar por importância
                df = df.sort_values('importance', ascending=False)
                
                # Adicionar informações de resultados se disponíveis
                if results and topo_name in results and obj_key in results[topo_name]:
                    res = results[topo_name][obj_key]
                    df['accuracy'] = res.get('accuracy', None)
                    df['top2_accuracy'] = res.get('top2_accuracy', None)
                    df['top3_accuracy'] = res.get('top3_accuracy', None)
                    df['f1_score'] = res.get('f1_score', None)
                    df['n_samples'] = res.get('n_samples', None)
                    
                    print(f"    - Accuracy: {res.get('accuracy', 'N/A'):.1%}")
                    print(f"    - Top-2 Accuracy: {res.get('top2_accuracy', 'N/A'):.1%}")
                    print(f"    - Top-3 Accuracy: {res.get('top3_accuracy', 'N/A'):.1%}")
                    print(f"    - F1-Score: {res.get('f1_score', 'N/A'):.4f}")
                    print(f"    - N Samples: {res.get('n_samples', 'N/A')}")
                    
                    # Adicionar ao summary
                    summary_data.append({
                        'topology': topo_name,
                        'objective': obj_key,
                        'objective_name': objectives.get(obj_key, obj_key),
                        'accuracy': res.get('accuracy', None),
                        'top2_accuracy': res.get('top2_accuracy', None),
                        'top3_accuracy': res.get('top3_accuracy', None),
                        'f1_score': res.get('f1_score', None),
                        'n_samples': res.get('n_samples', None),
                        'n_features': len(features),
                        'n_classes': model.n_classes_ if hasattr(model, 'n_classes_') else None
                    })
                else:
                    print(f"    - Métricas: Não disponíveis em tree_results_per_topology.json")
                
                # Top 5 features
                print(f"\n    Top 5 Features mais importantes:")
                for idx, row in df.head(5).iterrows():
                    print(f"      {row['feature']:40s} {row['importance']:8.4f}")
                
                all_importance_data.append(df)
    
    # Criar DataFrame consolidado
    if all_importance_data:
        all_df = pd.concat(all_importance_data, ignore_index=True)
        
        # Salvar CSV com importância de features
        output_dir = '../results'
        os.makedirs(output_dir, exist_ok=True)
        
        csv_path = f'{output_dir}/feature_importance_per_topology_objective.csv'
        all_df.to_csv(csv_path, index=False)
        print(f"\n✓ Salvo: {csv_path}")
        
        # Criar DataFrame de resumo
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_csv = f'{output_dir}/models_per_topology_summary.csv'
            summary_df.to_csv(summary_csv, index=False)
            print(f"✓ Salvo: {summary_csv}")
    
    # Estatísticas gerais
    print("\n" + "="*80)
    print("ESTATÍSTICAS GERAIS")
    print("="*80)
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        
        print(f"\nTotal de modelos: {len(summary_df)}")
        print(f"Topologias: {summary_df['topology'].nunique()}")
        print(f"Objetivos: {summary_df['objective'].nunique()}")
        
        print(f"\nAccuracy média por objetivo:")
        obj_means = summary_df.groupby('objective')['accuracy'].mean().sort_values(ascending=False)
        for obj, acc in obj_means.items():
            print(f"  {obj.upper():12s} {acc:.1%}")
        
        print(f"\nAccuracy média por topologia:")
        topo_means = summary_df.groupby('topology')['accuracy'].mean().sort_values(ascending=False)
        for topo, acc in topo_means.items():
            print(f"  {topo:20s} {acc:.1%}")
        
        print(f"\nTop-3 Accuracy média por objetivo:")
        obj_top3 = summary_df.groupby('objective')['top3_accuracy'].mean().sort_values(ascending=False)
        for obj, acc in obj_top3.items():
            print(f"  {obj.upper():12s} {acc:.1%}")
    
    # Análise de importância de features
    if all_importance_data:
        print("\n" + "="*80)
        print("ANÁLISE DE IMPORTÂNCIA DE FEATURES")
        print("="*80)
        
        all_df = pd.concat(all_importance_data, ignore_index=True)
        
        # Features mais importantes em geral
        feature_avg = all_df.groupby('feature')['importance'].mean().sort_values(ascending=False)
        
        print(f"\nTop 15 Features mais importantes (média geral):")
        for i, (feat, imp) in enumerate(feature_avg.head(15).items(), 1):
            print(f"  {i:2d}. {feat:40s} {imp:.4f}")
        
        # Features mais importantes por objetivo
        print(f"\nTop 5 Features por objetivo (média entre topologias):")
        for obj in sorted(all_df['objective'].unique()):
            obj_df = all_df[all_df['objective'] == obj]
            obj_feat_avg = obj_df.groupby('feature')['importance'].mean().sort_values(ascending=False)
            print(f"\n  {obj.upper()}:")
            for i, (feat, imp) in enumerate(obj_feat_avg.head(5).items(), 1):
                print(f"    {i}. {feat:38s} {imp:.4f}")
        
        # Features mais importantes por topologia
        print(f"\nTop 5 Features por topologia (média entre objetivos):")
        for topo in sorted(all_df['topology'].unique()):
            topo_df = all_df[all_df['topology'] == topo]
            topo_feat_avg = topo_df.groupby('feature')['importance'].mean().sort_values(ascending=False)
            print(f"\n  {topo.upper()}:")
            for i, (feat, imp) in enumerate(topo_feat_avg.head(5).items(), 1):
                print(f"    {i}. {feat:38s} {imp:.4f}")
    
    # Gerar resumo em texto
    generate_text_summary(summary_data, all_importance_data if all_importance_data else None, output_dir)
    
    print("\n" + "="*80)
    print("ANÁLISE COMPLETA!")
    print("="*80)


def generate_text_summary(summary_data, importance_data, output_dir):
    """Gera um resumo em texto formatado."""
    
    summary_path = f'{output_dir}/per_topology_models_summary.txt'
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RESUMO: MODELOS POR TOPOLOGIA\n")
        f.write("="*80 + "\n\n")
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            
            f.write("ESTRUTURA DOS MODELOS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total de modelos: {len(summary_df)}\n")
            f.write(f"Topologias: {summary_df['topology'].nunique()}\n")
            f.write(f"Objetivos: {summary_df['objective'].nunique()}\n\n")
            
            f.write("DESEMPENHO POR OBJETIVO\n")
            f.write("-"*80 + "\n")
            obj_stats = summary_df.groupby('objective').agg({
                'accuracy': ['mean', 'std', 'min', 'max'],
                'top3_accuracy': 'mean'
            }).round(3)
            
            for obj in sorted(summary_df['objective'].unique()):
                obj_df = summary_df[summary_df['objective'] == obj]
                f.write(f"\n{obj.upper()}:\n")
                f.write(f"  Accuracy média: {obj_df['accuracy'].mean():.1%} (std: {obj_df['accuracy'].std():.1%})\n")
                f.write(f"  Top-3 Accuracy média: {obj_df['top3_accuracy'].mean():.1%}\n")
                f.write(f"  Range: {obj_df['accuracy'].min():.1%} - {obj_df['accuracy'].max():.1%}\n")
            
            f.write("\n\nDESEMPENHO POR TOPOLOGIA\n")
            f.write("-"*80 + "\n")
            for topo in sorted(summary_df['topology'].unique()):
                topo_df = summary_df[summary_df['topology'] == topo]
                f.write(f"\n{topo.upper()}:\n")
                f.write(f"  Accuracy média: {topo_df['accuracy'].mean():.1%}\n")
                f.write(f"  Top-3 Accuracy média: {topo_df['top3_accuracy'].mean():.1%}\n")
                f.write(f"  Número de modelos: {len(topo_df)}\n")
            
            f.write("\n\nTABELA DETALHADA\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Topologia':<20} {'Objetivo':<12} {'Accuracy':<12} {'Top-3 Acc':<12} {'F1':<8} {'N Samples':<12}\n")
            f.write("-"*80 + "\n")
            
            for _, row in summary_df.sort_values(['topology', 'objective']).iterrows():
                f.write(f"{row['topology']:<20} {row['objective']:<12} "
                       f"{row['accuracy']:.1%}     {row['top3_accuracy']:.1%}     "
                       f"{row['f1_score']:.4f}  {row['n_samples']:<12.0f}\n")
        
        if importance_data:
            all_df = pd.concat(importance_data, ignore_index=True)
            
            f.write("\n\nFEATURES MAIS IMPORTANTES (GERAL)\n")
            f.write("-"*80 + "\n")
            feature_avg = all_df.groupby('feature')['importance'].mean().sort_values(ascending=False)
            for i, (feat, imp) in enumerate(feature_avg.head(20).items(), 1):
                f.write(f"{i:2d}. {feat:<50} {imp:.4f}\n")
    
    print(f"✓ Resumo salvo em: {summary_path}")


if __name__ == '__main__':
    analyze_per_topology_models()

