#!/usr/bin/env python3
"""
Calcular Top-1 Accuracy (mesma métrica de treinamento)
e comparar com algoritmo fixo.
"""

import json
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

print("="*80)
print("CÁLCULO DE TOP-1 ACCURACY (MESMA MÉTRICA DE TREINAMENTO)")
print("="*80)

# Carregar dados
test_data = pd.read_csv('datasets/test_enhanced.csv')
with open('models/decision_trees_depth10.pkl', 'rb') as f:
    models_dict = pickle.load(f)

objectives = ['rac', 'lrc', 'lar']
objective_columns = {
    'rac': 'best_for_rac',
    'lrc': 'best_for_lrc',
    'lar': 'best_for_lar'
}
algorithms = ['d_round', 'ga_meta', 'mcts', 'mip', 'pl_rank', 'pso_meta', 'rw_rank_bfs', 'sa_meta']

results = []

for obj in objectives:
    print(f"\n{'='*80}")
    print(f"OBJETIVO: {obj.upper()}")
    print("="*80)
    
    col_name = objective_columns[obj]
    y_true = test_data[col_name].values
    
    model = models_dict[obj]['model']
    encoder = models_dict[obj]['encoder']
    feature_names = models_dict[obj]['features']
    
    X_test = test_data[feature_names].values
    
    # Predições do modelo
    y_pred_encoded = model.predict(X_test)
    y_pred = encoder.inverse_transform(y_pred_encoded)
    
    # Calcular Top-1 Accuracy
    top1_correct = sum(y_pred == y_true)
    top1_accuracy = (top1_correct / len(y_true)) * 100
    
    # Calcular baseline (algoritmo fixo)
    fixed_results = {}
    for algo in algorithms:
        algo_correct = sum(y_true == algo)
        algo_accuracy = (algo_correct / len(y_true)) * 100
        fixed_results[algo] = algo_accuracy
    
    best_fixed = max(fixed_results.items(), key=lambda x: x[1])
    best_fixed_algo = best_fixed[0]
    best_fixed_accuracy = best_fixed[1]
    
    # Comparação
    improvement = top1_accuracy - best_fixed_accuracy
    
    print(f"\nTotal de VNRs no teste: {len(y_true)}")
    print(f"\n🤖 MODELO DINÂMICO (Top-1):")
    print(f"  Accuracy: {top1_accuracy:.2f}%")
    print(f"  Acertos: {top1_correct}/{len(y_true)}")
    
    print(f"\n🔧 BASELINE (MELHOR ALGORITMO FIXO):")
    print(f"  Algoritmo: {best_fixed_algo}")
    print(f"  Accuracy: {best_fixed_accuracy:.2f}%")
    
    print(f"\n📈 COMPARAÇÃO:")
    print(f"  Melhoria: {improvement:+.2f}pp")
    if improvement > 0:
        print(f"  ✅ MODELO É MELHOR ({improvement:.2f}pp de vantagem)")
    elif improvement < 0:
        print(f"  ❌ MODELO É PIOR ({abs(improvement):.2f}pp de desvantagem)")
    else:
        print(f"  ⚖️ EMPATE")
    
    # Mostrar todos os algoritmos fixos para contexto
    print(f"\n📊 TODOS OS ALGORITMOS FIXOS:")
    sorted_algos = sorted(fixed_results.items(), key=lambda x: x[1], reverse=True)
    for algo, acc in sorted_algos:
        marker = "👑" if algo == best_fixed_algo else "  "
        print(f"  {marker} {algo:15s}: {acc:6.2f}%")
    
    results.append({
        'objective': obj.upper(),
        'top1_accuracy': top1_accuracy,
        'top1_correct': top1_correct,
        'total': len(y_true),
        'best_fixed_algo': best_fixed_algo,
        'best_fixed_accuracy': best_fixed_accuracy,
        'improvement': improvement,
        'is_better': improvement > 0
    })

# RESUMO FINAL
print(f"\n{'='*80}")
print("RESUMO FINAL - TOP-1 ACCURACY")
print("="*80)
print(f"\n{'Objetivo':<10} {'Modelo Top-1':<15} {'Best Fixed':<15} {'Fixed Acc':<12} {'Melhoria':<12} {'Status'}")
print("-" * 80)
for r in results:
    status = "✅ MELHOR" if r['is_better'] else "❌ PIOR" if r['improvement'] < 0 else "⚖️ EMPATE"
    print(f"{r['objective']:<10} {r['top1_accuracy']:>6.2f}% ({r['top1_correct']:>3}/{r['total']:<3}) {r['best_fixed_algo']:<15} {r['best_fixed_accuracy']:>6.2f}%     {r['improvement']:>+6.2f}pp    {status}")

# Estatísticas gerais
avg_model = np.mean([r['top1_accuracy'] for r in results])
avg_fixed = np.mean([r['best_fixed_accuracy'] for r in results])
avg_improvement = np.mean([r['improvement'] for r in results])
all_better = all(r['is_better'] for r in results)

print(f"\n{'='*80}")
print("ESTATÍSTICAS GERAIS")
print("="*80)
print(f"  Média Modelo (Top-1):     {avg_model:.2f}%")
print(f"  Média Best Fixed:         {avg_fixed:.2f}%")
print(f"  Melhoria Média:           {avg_improvement:+.2f}pp")
print(f"\n  {'✅ Modelo é melhor em TODOS os objetivos' if all_better else '⚠️ Modelo NÃO é melhor em todos os objetivos'}")

# Comparação com Top-3 (para contexto)
print(f"\n{'='*80}")
print("COMPARAÇÃO: TOP-1 vs TOP-3")
print("="*80)
with open('models/dynamic_vs_fixed_comparison.json', 'r') as f:
    json_data = json.load(f)

print(f"\n{'Objetivo':<10} {'Top-1':<12} {'Top-3':<12} {'Diferença':<12}")
print("-" * 50)
for r in results:
    obj_lower = r['objective'].lower()
    top3 = json_data[obj_lower]['dynamic_ranking']
    diff = top3 - r['top1_accuracy']
    print(f"{r['objective']:<10} {r['top1_accuracy']:>6.2f}%     {top3:>6.2f}%     {diff:>+6.2f}pp")

print(f"\n{'='*80}")
print("CONCLUSÃO")
print("="*80)
if all_better:
    print("✅ O modelo dinâmico (Top-1) é MELHOR que o melhor algoritmo fixo")
    print(f"   em TODOS os objetivos, com melhoria média de {avg_improvement:.2f}pp")
elif avg_improvement > 0:
    print("⚠️ O modelo dinâmico (Top-1) é melhor em média, mas não em todos os objetivos")
    print(f"   Melhoria média: {avg_improvement:.2f}pp")
else:
    print("❌ O modelo dinâmico (Top-1) NÃO é melhor que o melhor algoritmo fixo")
    print(f"   Desvantagem média: {abs(avg_improvement):.2f}pp")

print(f"\n💡 Observação: Top-3 accuracy é {avg_model + (np.mean([json_data[r['objective'].lower()]['dynamic_ranking'] for r in results]) - avg_model):.2f}%")
print(f"   (muito maior que Top-1, mas Top-1 é a métrica de treinamento)")


