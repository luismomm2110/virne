#!/usr/bin/env python3
"""
Analyze correlation between LRC and LAR model predictions.

This script investigates why LRC and LAR have identical improvement values.
"""

import json
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from scipy.stats import pearsonr
from collections import Counter

print("="*80)
print("ANÁLISE DE CORRELAÇÃO ENTRE PREDIÇÕES LRC E LAR")
print("="*80)

# Load test data
print("\n1. Carregando dados de teste...")
test_data = pd.read_csv('datasets/test_enhanced.csv')
print(f"   Total de amostras: {len(test_data)}")

# Load models
print("\n2. Carregando modelos...")
with open('models/decision_trees_depth10.pkl', 'rb') as f:
    models_dict = pickle.load(f)

lrc_model = models_dict['lrc']['model']
lrc_encoder = models_dict['lrc']['encoder']
lrc_features = models_dict['lrc']['features']

lar_model = models_dict['lar']['model']
lar_encoder = models_dict['lar']['encoder']
lar_features = models_dict['lar']['features']

print(f"   ✓ Modelos carregados")

# Get ground truth labels
print("\n3. Obtendo labels verdadeiros...")
y_true_lrc = test_data['best_for_lrc'].values
y_true_lar = test_data['best_for_lar'].values

# Make predictions
print("\n4. Fazendo predições...")
X_test_lrc = test_data[lrc_features].values
X_test_lar = test_data[lar_features].values

# LRC predictions
y_pred_lrc_encoded = lrc_model.predict(X_test_lrc)
y_pred_lrc = lrc_encoder.inverse_transform(y_pred_lrc_encoded)
y_pred_lrc_proba = lrc_model.predict_proba(X_test_lrc)

# LAR predictions
y_pred_lar_encoded = lar_model.predict(X_test_lar)
y_pred_lar = lar_encoder.inverse_transform(y_pred_lar_encoded)
y_pred_lar_proba = lar_model.predict_proba(X_test_lar)

print(f"   ✓ Predições feitas para {len(y_pred_lrc)} amostras")

# ============================================================================
# ANALYSIS 1: How often do models predict the same algorithm?
# ============================================================================
print("\n" + "="*80)
print("ANÁLISE 1: QUANTAS VEZES OS MODELOS PREDIZEM O MESMO ALGORITMO?")
print("="*80)

same_prediction = (y_pred_lrc == y_pred_lar).sum()
same_pct = (same_prediction / len(y_pred_lrc)) * 100

print(f"\nPredições idênticas: {same_prediction}/{len(y_pred_lrc)} ({same_pct:.1f}%)")
print(f"Predições diferentes: {len(y_pred_lrc) - same_prediction}/{len(y_pred_lrc)} ({100-same_pct:.1f}%)")

# ============================================================================
# ANALYSIS 2: Correlation between ground truth labels
# ============================================================================
print("\n" + "="*80)
print("ANÁLISE 2: CORRELAÇÃO ENTRE LABELS VERDADEIROS (GROUND TRUTH)")
print("="*80)

same_gt = (y_true_lrc == y_true_lar).sum()
same_gt_pct = (same_gt / len(y_true_lrc)) * 100

print(f"\nMesmo algoritmo é melhor para LRC e LAR: {same_gt}/{len(y_true_lrc)} ({same_gt_pct:.1f}%)")

# Distribution comparison
print("\nDistribuição dos algoritmos (Ground Truth):")
print(f"\n{'Algoritmo':<15} {'LRC Count':<12} {'LAR Count':<12} {'Diferença':<12}")
print("-" * 60)

all_algos = set(list(y_true_lrc) + list(y_true_lar))
for algo in sorted(all_algos):
    lrc_count = (y_true_lrc == algo).sum()
    lar_count = (y_true_lar == algo).sum()
    diff = abs(lrc_count - lar_count)
    print(f"{algo:<15} {lrc_count:<12} {lar_count:<12} {diff:<12}")

# ============================================================================
# ANALYSIS 3: Correlation between predictions
# ============================================================================
print("\n" + "="*80)
print("ANÁLISE 3: CORRELAÇÃO ENTRE PREDIÇÕES DOS MODELOS")
print("="*80)

# Convert predictions to numeric for correlation
algo_to_num = {algo: i for i, algo in enumerate(sorted(set(list(y_pred_lrc) + list(y_pred_lar))))}
y_pred_lrc_num = np.array([algo_to_num[algo] for algo in y_pred_lrc])
y_pred_lar_num = np.array([algo_to_num[algo] for algo in y_pred_lar])

correlation, p_value = pearsonr(y_pred_lrc_num, y_pred_lar_num)
print(f"\nCorrelação de Pearson entre predições: {correlation:.4f} (p-value: {p_value:.4f})")

# ============================================================================
# ANALYSIS 4: Top-3 overlap
# ============================================================================
print("\n" + "="*80)
print("ANÁLISE 4: SOBREPOSIÇÃO NO TOP-3")
print("="*80)

top3_overlaps = []
for i in range(len(y_pred_lrc_proba)):
    # Get top-3 for LRC
    lrc_top3_idx = np.argsort(y_pred_lrc_proba[i])[-3:][::-1]
    lrc_top3 = set(lrc_encoder.classes_[lrc_top3_idx])
    
    # Get top-3 for LAR
    lar_top3_idx = np.argsort(y_pred_lar_proba[i])[-3:][::-1]
    lar_top3 = set(lar_encoder.classes_[lar_top3_idx])
    
    # Calculate overlap
    overlap = len(lrc_top3 & lar_top3)
    top3_overlaps.append(overlap)

avg_overlap = np.mean(top3_overlaps)
print(f"\nMédia de algoritmos em comum no Top-3: {avg_overlap:.2f} de 3")
print(f"Distribuição de sobreposição:")
overlap_dist = Counter(top3_overlaps)
for overlap_count in sorted(overlap_dist.keys()):
    count = overlap_dist[overlap_count]
    pct = (count / len(top3_overlaps)) * 100
    print(f"  {overlap_count} algoritmos em comum: {count} amostras ({pct:.1f}%)")

# ============================================================================
# ANALYSIS 5: Accuracy comparison
# ============================================================================
print("\n" + "="*80)
print("ANÁLISE 5: COMPARAÇÃO DE ACURÁCIA")
print("="*80)

# Top-3 accuracy for LRC
lrc_top3_correct = 0
for i, true_algo in enumerate(y_true_lrc):
    top3_idx = np.argsort(y_pred_lrc_proba[i])[-3:][::-1]
    true_encoded = lrc_encoder.transform([true_algo])[0]
    if true_encoded in top3_idx:
        lrc_top3_correct += 1
lrc_top3_acc = (lrc_top3_correct / len(y_true_lrc)) * 100

# Top-3 accuracy for LAR
lar_top3_correct = 0
for i, true_algo in enumerate(y_true_lar):
    top3_idx = np.argsort(y_pred_lar_proba[i])[-3:][::-1]
    true_encoded = lar_encoder.transform([true_algo])[0]
    if true_encoded in top3_idx:
        lar_top3_correct += 1
lar_top3_acc = (lar_top3_correct / len(y_true_lar)) * 100

print(f"\nTop-3 Accuracy:")
print(f"  LRC: {lrc_top3_acc:.2f}%")
print(f"  LAR: {lar_top3_acc:.2f}%")
print(f"  Diferença: {abs(lrc_top3_acc - lar_top3_acc):.2f}pp")

# Load comparison data to verify
print("\n" + "="*80)
print("VERIFICAÇÃO: Comparando com dados do JSON")
print("="*80)

with open('models/dynamic_vs_fixed_comparison.json', 'r') as f:
    comparison_data = json.load(f)

lrc_dynamic = comparison_data['lrc']['dynamic_ranking']
lar_dynamic = comparison_data['lar']['dynamic_ranking']
lrc_fixed = comparison_data['lrc']['best_fixed_accuracy']
lar_fixed = comparison_data['lar']['best_fixed_accuracy']

print(f"\nValores do JSON:")
print(f"  LRC dynamic: {lrc_dynamic:.10f}%")
print(f"  LAR dynamic: {lar_dynamic:.10f}%")
print(f"  LRC fixed:   {lrc_fixed:.10f}%")
print(f"  LAR fixed:   {lar_fixed:.10f}%")

print(f"\nMelhorias:")
lrc_imp = lrc_dynamic - lrc_fixed
lar_imp = lar_dynamic - lar_fixed
print(f"  LRC: {lrc_imp:.10f}pp")
print(f"  LAR: {lar_imp:.10f}pp")
print(f"  Diferença: {abs(lrc_imp - lar_imp):.20f}pp")

print(f"\nDiferenças:")
print(f"  Dynamic (LRC - LAR): {lrc_dynamic - lar_dynamic:.10f}pp")
print(f"  Fixed (LRC - LAR):   {lrc_fixed - lar_fixed:.10f}pp")
print(f"  Diferença das diferenças: {abs((lrc_dynamic - lar_dynamic) - (lrc_fixed - lar_fixed)):.20f}pp")

# ============================================================================
# CONCLUSION
# ============================================================================
print("\n" + "="*80)
print("CONCLUSÃO")
print("="*80)

print(f"""
Os valores de melhoria são idênticos porque:

1. Diferença entre valores dinâmicos = Diferença entre valores fixos
   - LRC_dynamic - LAR_dynamic = {lrc_dynamic - lar_dynamic:.10f}pp
   - LRC_fixed - LAR_fixed = {lrc_fixed - lar_fixed:.10f}pp
   - Portanto: (LRC_dynamic - LRC_fixed) = (LAR_dynamic - LAR_fixed)

2. Correlação entre predições: {correlation:.4f}
   - {'Alta correlação' if correlation > 0.7 else 'Correlação moderada' if correlation > 0.4 else 'Baixa correlação'}

3. Sobreposição no Top-3: {avg_overlap:.2f} algoritmos em comum
   - {'Alta sobreposição' if avg_overlap > 2.0 else 'Sobreposição moderada' if avg_overlap > 1.0 else 'Baixa sobreposição'}

4. Predições idênticas: {same_pct:.1f}% das vezes
   - {'Modelos fazem predições muito similares' if same_pct > 50 else 'Modelos fazem predições diferentes'}
""")

print("="*80)

