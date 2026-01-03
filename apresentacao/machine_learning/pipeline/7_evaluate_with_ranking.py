#!/usr/bin/env python3
"""
Step 7: Evaluate Per-Topology Models with Top-K Ranking

This script evaluates the per-topology models using:
1. Classification (exact match): strict but low accuracy
2. Top-3 Ranking: pragmatic, accepts if in top 3
3. Adaptive: hybrid approach
"""

import pandas as pd
import numpy as np
import pickle
import json
from sklearn.metrics import accuracy_score

def evaluate_ranking(y_true, y_pred_proba, k=3):
    """Top-K ranking accuracy.

    Args:
        y_true: encoded labels (0, 1, 2, ...)
        y_pred_proba: probability matrix from model
    """
    correct = 0
    for true_label_encoded, proba in zip(y_true, y_pred_proba):
        # Get top k class indices
        top_k_idx = np.argsort(proba)[-k:]

        # Check if true label is in top k
        if true_label_encoded in top_k_idx:
            correct += 1

    return correct / len(y_true) if len(y_true) > 0 else 0.0

def evaluate_adaptive(y_true, y_pred, y_pred_proba, y_encoder, threshold=0.1):
    """Adaptive: use ranking when uncertain."""
    correct = 0
    classification_used = 0
    ranking_used = 0
    confidences = []

    for i, true_label in enumerate(y_true):
        # Calculate confidence
        sorted_proba = np.sort(y_pred_proba[i])[::-1]
        confidence = (sorted_proba[0] - sorted_proba[1]) / (sorted_proba[0] + 1e-6)
        confidences.append(confidence)

        if confidence > threshold:
            # Use strict classification
            if y_pred[i] == true_label:
                correct += 1
            classification_used += 1
        else:
            # Use ranking (top-3)
            top_k_idx = np.argsort(y_pred_proba[i])[-3:]
            top_k_labels = y_encoder.classes_[top_k_idx]

            if true_label in top_k_labels:
                correct += 1
            ranking_used += 1

    accuracy = correct / len(y_true) if len(y_true) > 0 else 0.0
    avg_confidence = np.mean(confidences) if confidences else 0.0
    confidence_std = np.std(confidences) if confidences else 0.0

    return accuracy, classification_used, ranking_used, avg_confidence, confidence_std

def main():
    print("=" * 100)
    print("EVALUATION: PER-TOPOLOGY MODELS WITH RANKING")
    print("=" * 100)

    # Load data
    val_df = pd.read_csv('../datasets/val_enhanced.csv')

    # Load models
    with open('../models/decision_trees_per_topology.pkl', 'rb') as f:
        models = pickle.load(f)

    topologies = {0: 'tree', 1: 'fat_tree', 2: 'waxman_16'}
    objectives = {
        'rac': 'best_for_rac',
        'lrc': 'best_for_lrc',
        'lar': 'best_for_lar',
        'ast': 'best_for_ast',
        'balanced': 'best_for_balanced'
    }

    results = {}

    # Evaluate per topology
    for topo_code, topo_name in topologies.items():
        print(f"\n{'=' * 100}")
        print(f"TOPOLOGY: {topo_name.upper()}")
        print(f"{'=' * 100}")

        # Filter validation data by topology
        val_topo = val_df[val_df['topology_encoded'] == topo_code]

        if len(val_topo) == 0:
            print(f"⚠️  No validation data for {topo_name}")
            continue

        print(f"Validation samples: {len(val_topo)}\n")

        results[topo_name] = {}

        for obj_key, target_col in objectives.items():
            if topo_name not in models or obj_key not in models[topo_name]:
                print(f"⚠️  No model for {topo_name}/{obj_key}")
                continue

            # Get model and encoder
            model_dict = models[topo_name][obj_key]
            model = model_dict['model']
            encoder = model_dict['encoder']
            features = model_dict['features']

            # Get data
            y_val = val_topo[target_col].dropna()
            X_val_obj = val_topo.loc[y_val.index, features].copy()

            if len(y_val) == 0:
                print(f"⚠️  No labels for {obj_key}")
                continue

            # Encode labels
            y_val_encoded = encoder.transform(y_val)

            # Predictions
            y_pred = model.predict(X_val_obj)
            y_pred_proba = model.predict_proba(X_val_obj)

            # Evaluate
            acc_class = accuracy_score(y_val_encoded, y_pred)
            acc_ranking = evaluate_ranking(y_val_encoded, y_pred_proba, k=3)
            acc_adaptive, class_used, ranking_used, avg_conf, conf_std = evaluate_adaptive(
                y_val_encoded, y_pred, y_pred_proba, encoder, threshold=0.1
            )

            results[topo_name][obj_key] = {
                'n_samples': len(y_val),
                'classification': float(acc_class),
                'top3_ranking': float(acc_ranking),
                'adaptive': float(acc_adaptive),
                'classification_used': int(class_used),
                'ranking_used': int(ranking_used),
                'avg_confidence': float(avg_conf),
                'confidence_std': float(conf_std)
            }

            print(f"{obj_key.upper():12s} (n={len(y_val):3d}):")
            print(f"  Classification (strict):   {acc_class:6.1%}")
            print(f"  Top-3 Ranking (pragmatic): {acc_ranking:6.1%}")
            print(f"  Adaptive (hybrid):         {acc_adaptive:6.1%}")
            if class_used > 0 or ranking_used > 0:
                print(f"    ├─ Classification used: {class_used:4d} ({class_used/(class_used+ranking_used)*100:5.1f}%)")
                print(f"    ├─ Ranking used:        {ranking_used:4d} ({ranking_used/(class_used+ranking_used)*100:5.1f}%)")
                print(f"    └─ Avg confidence:      {avg_conf:.3f} ± {conf_std:.3f}")
            print()

    # Save results
    with open('../models/ranking_results_per_topology.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("✓ Saved: models/ranking_results_per_topology.json")

    # Print summary
    print("\n" + "=" * 100)
    print("SUMMARY TABLE")
    print("=" * 100)

    for topo_name in ['tree', 'fat_tree', 'waxman_16']:
        if topo_name not in results:
            continue

        print(f"\n{topo_name.upper()}:")
        print(f"{'Objective':<12} {'Classification':<18} {'Top-3 Ranking':<18} {'Adaptive':<18} {'Best':<15}")
        print("-" * 80)

        for obj_key in objectives.keys():
            if obj_key in results[topo_name]:
                r = results[topo_name][obj_key]
                class_acc = r['classification']
                ranking_acc = r['top3_ranking']
                adaptive_acc = r['adaptive']

                best_acc = max(class_acc, ranking_acc, adaptive_acc)
                if best_acc == ranking_acc:
                    best_name = "RANKING"
                elif best_acc == adaptive_acc:
                    best_name = "ADAPTIVE"
                else:
                    best_name = "CLASSIFICATION"

                print(f"{obj_key:<12} {class_acc:<18.1%} {ranking_acc:<18.1%} {adaptive_acc:<18.1%} {best_name:<15}")

    # Overall comparison
    print("\n" + "=" * 100)
    print("BEST STRATEGY BY TOPOLOGY")
    print("=" * 100)

    for topo_name in ['tree', 'fat_tree', 'waxman_16']:
        if topo_name not in results:
            continue

        print(f"\n{topo_name.upper()}:")

        for obj_key in objectives.keys():
            if obj_key in results[topo_name]:
                r = results[topo_name][obj_key]

                # Find best
                class_acc = r['classification']
                ranking_acc = r['top3_ranking']
                adaptive_acc = r['adaptive']

                best_acc = max(class_acc, ranking_acc, adaptive_acc)

                if best_acc == ranking_acc:
                    strategy = f"TOP-3 RANKING"
                    improvement = f"+{(ranking_acc - class_acc)*100:.1f}pp"
                elif best_acc == adaptive_acc:
                    strategy = f"ADAPTIVE"
                    improvement = f"+{(adaptive_acc - class_acc)*100:.1f}pp"
                else:
                    strategy = f"CLASSIFICATION"
                    improvement = "-"

                print(f"  {obj_key:10s}: {strategy:20s} {best_acc:6.1%} ({improvement})")


if __name__ == '__main__':
    main()
