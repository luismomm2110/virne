#!/usr/bin/env python3
"""
Calcular Top-1 Accuracy CORRETO (com decodificação)
"""

import json
import pickle
import pandas as pd
import numpy as np

print("="*80)
print("CÁLCULO CORRETO DE TOP-1 ACCURACY")
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
    y_true = test_data[col_name].values  # Strings
    
    model = models_dict[obj]['model']
    encoder = models_dict[obj]['encoder']
    feature_names = models_dict[obj]['features']
    
    X_test = test_data[feature_names].values
    
    # CORREÇÃO: Decodificar predições antes de comparar
    y_pred_encoded = model.predict(X_test)  # Índices codificados
    y_pred = encoder.inverse_transform(y_pred_encoded)  # Decodificar para strings
    y_pred_proba = model.predict_proba(X_test)
    
    # Calcular Top-1 Accuracy (CORRETO)
    top1_correct = sum(y_pred == y_true)
    top1_accuracy = (top1_correct / len(y_true)) * 100
    
    # Calcular Top-3 Accuracy (para comparação)
    top3_correct = 0
    for i, (true_label, proba) in enumerate(zip(y_true, y_pred_proba)):
        top_3_idx = np.argsort(proba)[-3:][::-1]
        true_label_encoded = encoder.transform([true_label])[0]
        if true_label_encoded in top_3_idx:
            top3_correct += 1
    top3_accuracy = (top3_correct / len(y_true)) * 100
    
    # Calcular baseline (algoritmo fixo)
    fixed_results = {}
    for algo in algorithms:
        algo_correct = sum(y_true == algo)
        algo_accuracy = (algo_correct / len(y_true)) * 100
        fixed_results[algo] = algo_accuracy
    
    best_fixed = max(fixed_results.items(), key=lambda x: x[1])
    best_fixed_algo = best_fixed[0]
    best_fixed_accuracy = best_fixed[1]
    
    # Comparações
    improvement_top1 = top1_accuracy - best_fixed_accuracy
    improvement_top3 = top3_accuracy - best_fixed_accuracy
    
    print(f"\nTotal de VNRs: {len(y_true)}")
    print(f"\n🤖 MODELO DINÂMICO:")
    print(f"  Top-1 Accuracy: {top1_accuracy:.2f}% ({top1_correct}/{len(y_true)})")
    print(f"  Top-3 Accuracy: {top3_accuracy:.2f}% ({top3_correct}/{len(y_true)})")
    
    print(f"\n🔧 BASELINE (MELHOR ALGORITMO FIXO):")
    print(f"  Algoritmo: {best_fixed_algo}")
    print(f"  Accuracy: {best_fixed_accuracy:.2f}%")
    
    print(f"\n📈 COMPARAÇÃO:")
    print(f"  Top-1 vs Fixed: {improvement_top1:+.2f}pp {'✅ MELHOR' if improvement_top1 > 0 else '❌ PIOR' if improvement_top1 < 0 else '⚖️ EMPATE'}")
    print(f"  Top-3 vs Fixed: {improvement_top3:+.2f}pp {'✅ MELHOR' if improvement_top3 > 0 else '❌ PIOR'}")
    
    results.append({
        'objective': obj.upper(),
        'top1_accuracy': top1_accuracy,
        'top1_correct': top1_correct,
        'top3_accuracy': top3_accuracy,
        'top3_correct': top3_correct,
        'total': len(y_true),
        'best_fixed_algo': best_fixed_algo,
        'best_fixed_accuracy': best_fixed_accuracy,
        'improvement_top1': improvement_top1,
        'improvement_top3': improvement_top3,
        'is_better_top1': improvement_top1 > 0,
        'is_better_top3': improvement_top3 > 0
    })

# RESUMO FINAL
print(f"\n{'='*80}")
print("RESUMO FINAL")
print("="*80)
print(f"\n{'Objetivo':<10} {'Top-1':<12} {'Top-3':<12} {'Best Fixed':<15} {'Fixed':<10} {'Top-1 vs':<12} {'Top-3 vs':<12}")
print(f"{'':<10} {'Accuracy':<12} {'Accuracy':<12} {'Algoritmo':<15} {'Accuracy':<10} {'Fixed':<12} {'Fixed':<12}")
print("-" * 90)
for r in results:
    status_top1 = "✅" if r['is_better_top1'] else "❌" if r['improvement_top1'] < 0 else "⚖️"
    status_top3 = "✅" if r['is_better_top3'] else "❌"
    print(f"{r['objective']:<10} {r['top1_accuracy']:>6.2f}%     {r['top3_accuracy']:>6.2f}%     {r['best_fixed_algo']:<15} {r['best_fixed_accuracy']:>6.2f}%     {r['improvement_top1']:>+6.2f}pp {status_top1}   {r['improvement_top3']:>+6.2f}pp {status_top3}")

# Estatísticas
avg_top1 = np.mean([r['top1_accuracy'] for r in results])
avg_top3 = np.mean([r['top3_accuracy'] for r in results])
avg_fixed = np.mean([r['best_fixed_accuracy'] for r in results])
avg_imp_top1 = np.mean([r['improvement_top1'] for r in results])
avg_imp_top3 = np.mean([r['improvement_top3'] for r in results])

print(f"\n{'='*80}")
print("ESTATÍSTICAS GERAIS")
print("="*80)
print(f"  Média Top-1 Accuracy:     {avg_top1:.2f}%")
print(f"  Média Top-3 Accuracy:     {avg_top3:.2f}%")
print(f"  Média Best Fixed:         {avg_fixed:.2f}%")
print(f"  Melhoria Média (Top-1):   {avg_imp_top1:+.2f}pp")
print(f"  Melhoria Média (Top-3):   {avg_imp_top3:+.2f}pp")

all_better_top1 = all(r['is_better_top1'] for r in results)
all_better_top3 = all(r['is_better_top3'] for r in results)

print(f"\n{'='*80}")
print("CONCLUSÃO")
print("="*80)
if all_better_top1:
    print("✅ Top-1: Modelo é MELHOR que algoritmo fixo em TODOS os objetivos")
elif avg_imp_top1 > 0:
    print("⚠️ Top-1: Modelo é melhor em média, mas não em todos os objetivos")
else:
    print("❌ Top-1: Modelo NÃO é melhor que algoritmo fixo")

if all_better_top3:
    print("✅ Top-3: Modelo é MELHOR que algoritmo fixo em TODOS os objetivos")
    print(f"   Melhoria média: {avg_imp_top3:.2f}pp")

# Salvar resultados atualizados
print(f"\n{'='*80}")
print("ATUALIZANDO JSON COM VALORES CORRETOS")
print("="*80)

# Carregar JSON existente
with open('models/dynamic_vs_fixed_comparison.json', 'r') as f:
    json_data = json.load(f)

# Atualizar com valores corretos
for r in results:
    obj_lower = r['objective'].lower()
    json_data[obj_lower]['dynamic_classification'] = r['top1_accuracy']
    print(f"  {obj_lower.upper()}: Top-1 atualizado de 0.0% para {r['top1_accuracy']:.2f}%")

# Salvar JSON atualizado
with open('models/dynamic_vs_fixed_comparison.json', 'w') as f:
    json.dump(json_data, f, indent=2)

print("\n✅ JSON atualizado com valores corretos!")


