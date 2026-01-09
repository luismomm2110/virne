#!/usr/bin/env python3
"""
Verificar se o cálculo de acurácia Top-1 está correto.
O problema pode ser que y_pred está codificado e y_true está em strings.
"""

import json
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

print("="*80)
print("VERIFICAÇÃO DO CÁLCULO DE ACURÁCIA TOP-1")
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

for obj in objectives:
    print(f"\n{'='*80}")
    print(f"OBJETIVO: {obj.upper()}")
    print("="*80)
    
    col_name = objective_columns[obj]
    y_true = test_data[col_name].values  # Strings: ['ga_meta', 'pl_rank', ...]
    
    model = models_dict[obj]['model']
    encoder = models_dict[obj]['encoder']
    feature_names = models_dict[obj]['features']
    
    X_test = test_data[feature_names].values
    
    # Predições
    y_pred_encoded = model.predict(X_test)  # Índices: [0, 1, 2, ...]
    y_pred_decoded = encoder.inverse_transform(y_pred_encoded)  # Strings: ['ga_meta', 'pl_rank', ...]
    
    print(f"\nTipos de dados:")
    print(f"  y_true type: {type(y_true[0])}, exemplo: {y_true[0]}")
    print(f"  y_pred_encoded type: {type(y_pred_encoded[0])}, exemplo: {y_pred_encoded[0]}")
    print(f"  y_pred_decoded type: {type(y_pred_decoded[0])}, exemplo: {y_pred_decoded[0]}")
    
    # CÁLCULO CORRETO (comparando strings com strings)
    correct_comparison = sum(y_pred_decoded == y_true)
    accuracy_correct = (correct_comparison / len(y_true)) * 100
    
    # CÁLCULO ERRADO (comparando índices com strings) - isso daria 0!
    wrong_comparison = sum(y_pred_encoded == y_true)
    accuracy_wrong = (wrong_comparison / len(y_true)) * 100
    
    print(f"\nCálculo CORRETO (decodificado):")
    print(f"  Acertos: {correct_comparison}/{len(y_true)}")
    print(f"  Accuracy: {accuracy_correct:.2f}%")
    
    print(f"\nCálculo ERRADO (codificado):")
    print(f"  Acertos: {wrong_comparison}/{len(y_true)}")
    print(f"  Accuracy: {accuracy_wrong:.2f}%")
    
    # Verificar o que está no JSON
    with open('models/dynamic_vs_fixed_comparison.json', 'r') as f:
        json_data = json.load(f)
    
    json_top1 = json_data[obj]['dynamic_classification']
    print(f"\nValor no JSON: {json_top1}%")
    
    if abs(json_top1 - accuracy_correct) < 0.01:
        print(f"✅ JSON está CORRETO (usa decodificação)")
    elif abs(json_top1 - accuracy_wrong) < 0.01:
        print(f"❌ JSON está ERRADO (não decodifica)")
    else:
        print(f"⚠️ JSON não corresponde a nenhum cálculo")




