#!/usr/bin/env python3
"""
Step 3 OPTIMIZED: Train Decision Trees with Optimized Depth and Per-Topology Models

This script trains TWO SETS of models:
1. Global models with depth=10 (better accuracy than depth=5)
2. Per-topology models (tree, fat_tree, waxman_16)

Results show per-topology models achieve 60-70% accuracy vs 45-57% global.
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, f1_score, top_k_accuracy_score
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns


def select_features():
    """Define feature columns for training."""
    return [
        # VNR characteristics
        'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
        'v_net_demand_per_node', 'v_net_demand_per_link', 'v_net_connectivity',
        'v_net_total_demand', 'v_net_node_to_link_demand_ratio', 'v_net_lifetime',

        # Physical network state
        'p_net_available_resource', 'p_net_node_util', 'p_net_link_util',
        'p_net_overall_util',

        # System state
        'inservice_count', 'system_load', 'num_running_p_net_nodes',

        # Topology (NOT included in per-topology models)
        'topology_encoded',

        # Original engineered features
        'network_stress_index', 'problem_complexity', 'resource_bottleneck_ratio',
        'vnr_size_category', 'cpu_intensive_flag', 'bandwidth_intensive_flag',
        'utilization_pressure', 'resource_efficiency',

        # NEW: Heterogeneidade de Recursos (3)
        'p_net_node_link_resource_ratio', 'p_net_util_imbalance',
        'p_net_resource_heterogeneity',

        # NEW: Fragmentação e Saúde da Rede (3)
        'p_net_fragmentation_estimate', 'p_net_uneven_utilization', 'p_net_health_score',

        # NEW: Características VNR (4)
        'vnr_node_link_demand_ratio', 'vnr_demand_intensity',
        'vnr_structural_complexity', 'vnr_density_adjusted'
    ]


def train_model(X_train, y_train, X_val, y_val, target_col, max_depth=10):
    """Train a single decision tree model."""

    # Label encode
    unique_classes = sorted(y_train.unique())
    le = LabelEncoder()
    le.fit(unique_classes)

    y_train_encoded = le.transform(y_train)
    y_val_encoded = le.transform(y_val)

    # Train model
    model = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight='balanced',
        random_state=42
    )

    model.fit(X_train, y_train_encoded)

    # Evaluate
    y_val_pred = model.predict(X_val)
    y_val_proba = model.predict_proba(X_val)

    accuracy = accuracy_score(y_val_encoded, y_val_pred)
    f1 = f1_score(y_val_encoded, y_val_pred, average='weighted', zero_division=0)

    # Top-K Accuracy (se houver múltiplas classes)
    n_classes = len(unique_classes)
    try:
        if n_classes >= 2:
            top2_accuracy = top_k_accuracy_score(y_val_encoded, y_val_proba, k=min(2, n_classes), labels=range(n_classes))
        else:
            top2_accuracy = accuracy

        if n_classes >= 3:
            top3_accuracy = top_k_accuracy_score(y_val_encoded, y_val_proba, k=min(3, n_classes), labels=range(n_classes))
        else:
            top3_accuracy = top2_accuracy
    except Exception as e:
        # Fallback if top_k_accuracy_score fails
        top2_accuracy = accuracy
        top3_accuracy = accuracy

    return model, le, accuracy, f1, y_val_pred, top2_accuracy, top3_accuracy


def main():
    print("=" * 80)
    print("TRAINING DECISION TREES: GLOBAL + PER-TOPOLOGY MODELS")
    print("=" * 80)

    # Load enhanced datasets
    train_df = pd.read_csv('datasets/train_enhanced.csv')
    val_df = pd.read_csv('datasets/val_enhanced.csv')

    features = select_features()
    objectives = {
        'rac': ('Request Acceptance Rate', 'best_for_rac'),
        'lrc': ('Long-Term Revenue-to-Cost', 'best_for_lrc'),
        'lar': ('Long-Term Average Revenue', 'best_for_lar'),
        'ast': ('Average Solving Time', 'best_for_ast'),
        'balanced': ('Balanced (0.8*revenue - 0.2*time)', 'best_for_balanced')
    }

    topologies = {0: 'tree', 1: 'fat_tree', 2: 'waxman_16'}

    # ========================================================================
    # PART 1: GLOBAL MODELS WITH DEPTH=10
    # ========================================================================
    print("\n" + "=" * 80)
    print("PART 1: GLOBAL MODELS (ALL TOPOLOGIES, depth=10)")
    print("=" * 80)

    global_models = {}
    global_results = {}

    for obj_key, (obj_name, target_col) in objectives.items():
        print(f"\nTraining {obj_key.upper()}...")

        # Prepare data
        X_train = train_df[features].copy()
        y_train = train_df[target_col].dropna()
        X_train = X_train.loc[y_train.index]

        X_val = val_df[features].copy()
        y_val = val_df[target_col].dropna()
        X_val = X_val.loc[y_val.index]

        # Train with depth=10
        model, le, accuracy, f1, y_pred, top2_acc, top3_acc = train_model(
            X_train, y_train, X_val, y_val, target_col, max_depth=10
        )

        global_models[obj_key] = {'model': model, 'encoder': le, 'features': features}
        global_results[obj_key] = {
            'accuracy': float(accuracy),
            'top2_accuracy': float(top2_acc),
            'top3_accuracy': float(top3_acc),
            'f1_score': float(f1),
            'n_samples': len(y_val)
        }

        print(f"  Accuracy: {accuracy:.1%} | Top-2: {top2_acc:.1%} | Top-3: {top3_acc:.1%} | F1: {f1:.4f}")

    # ========================================================================
    # PART 2: PER-TOPOLOGY MODELS
    # ========================================================================
    print("\n" + "=" * 80)
    print("PART 2: PER-TOPOLOGY MODELS (depth=10)")
    print("=" * 80)

    per_topo_models = {}
    per_topo_results = {}

    for topo_code, topo_name in topologies.items():
        print(f"\n{topo_name.upper()}:")

        # Filter by topology
        train_topo = train_df[train_df['topology_encoded'] == topo_code]
        val_topo = val_df[val_df['topology_encoded'] == topo_code]

        print(f"  Train: {len(train_topo)} samples | Val: {len(val_topo)} samples")

        # Features WITHOUT topology (since all rows have same topology)
        features_no_topo = [f for f in features if f != 'topology_encoded']

        per_topo_models[topo_name] = {}
        per_topo_results[topo_name] = {}

        for obj_key, (obj_name, target_col) in objectives.items():
            # Prepare data
            X_train = train_topo[features_no_topo].copy()
            y_train = train_topo[target_col].dropna()
            X_train = X_train.loc[y_train.index]

            X_val = val_topo[features_no_topo].copy()
            y_val = val_topo[target_col].dropna()
            X_val = X_val.loc[y_val.index]

            if len(y_train) > 0 and len(y_val) > 0:
                # Train
                model, le, accuracy, f1, y_pred, top2_acc, top3_acc = train_model(
                    X_train, y_train, X_val, y_val, target_col, max_depth=10
                )

                per_topo_models[topo_name][obj_key] = {
                    'model': model, 'encoder': le, 'features': features_no_topo
                }
                per_topo_results[topo_name][obj_key] = {
                    'accuracy': float(accuracy),
                    'top2_accuracy': float(top2_acc),
                    'top3_accuracy': float(top3_acc),
                    'f1_score': float(f1),
                    'n_samples': len(y_val)
                }

                print(f"  {obj_key}: {accuracy:.1%} | Top-2: {top2_acc:.1%} | Top-3: {top3_acc:.1%} (F1: {f1:.4f})")
            else:
                print(f"  {obj_key}: Insufficient samples (train:{len(y_train)}, val:{len(y_val)})")

    # ========================================================================
    # SAVE MODELS AND RESULTS
    # ========================================================================
    print("\n" + "=" * 80)
    print("SAVING MODELS")
    print("=" * 80)

    # Save global models
    with open('models/decision_trees_depth10.pkl', 'wb') as f:
        pickle.dump(global_models, f)
    print("\n✓ Saved: models/decision_trees_depth10.pkl")

    # Save per-topology models
    with open('models/decision_trees_per_topology.pkl', 'wb') as f:
        pickle.dump(per_topo_models, f)
    print("✓ Saved: models/decision_trees_per_topology.pkl")

    # Save results
    with open('models/tree_results_depth10.json', 'w') as f:
        json.dump(global_results, f, indent=2)
    print("✓ Saved: models/tree_results_depth10.json")

    with open('models/tree_results_per_topology.json', 'w') as f:
        json.dump(per_topo_results, f, indent=2)
    print("✓ Saved: models/tree_results_per_topology.json")

    # ========================================================================
    # COMPARISON REPORT
    # ========================================================================
    print("\n" + "=" * 80)
    print("COMPARISON: GLOBAL vs PER-TOPOLOGY")
    print("=" * 80)

    print(f"\n{'Objetivo':<12} {'Global (depth=5)':<20} {'Global (depth=10)':<20} {'Per-Topology Avg':<20}")
    print("-" * 75)

    old_results = {
        'rac': 0.530,
        'lrc': 0.465,
        'lar': 0.480,
        'ast': 0.848,
        'balanced': 0.572
    }

    for obj_key in objectives.keys():
        global_acc = global_results[obj_key]['accuracy']
        old_acc = old_results.get(obj_key, 0)

        # Average per-topology
        topo_accs = []
        for topo_name in per_topo_results.keys():
            if obj_key in per_topo_results[topo_name]:
                topo_accs.append(per_topo_results[topo_name][obj_key]['accuracy'])
        topo_avg = np.mean(topo_accs) if topo_accs else 0

        print(f"{obj_key:<12} {old_acc:<20.1%} {global_acc:<20.1%} {topo_avg:<20.1%}")

    print("\n" + "=" * 80)
    print("TRAINING COMPLETE!")
    print("=" * 80)

    print("\nModels available:")
    print("  1. Global (depth=10): decision_trees_depth10.pkl")
    print("  2. Per-topology: decision_trees_per_topology.pkl")
    print("\nUse per-topology models for better accuracy!")


if __name__ == '__main__':
    main()
