#!/usr/bin/env python3
"""
Option 2: Train Multiple Objective-Specific Decision Trees

Instead of one "best_overall" tree, train separate trees for:
  1. best_for_acceptance: Which algorithm maximizes success rate?
  2. best_for_cost: Which algorithm minimizes embedding cost?
  3. best_for_speed: Which algorithm minimizes execution time?
  4. best_balanced: Equal weight across all three objectives

This allows runtime decisions based on current priorities:
  - High congestion? Use best_for_acceptance
  - Resource constraints? Use best_for_cost
  - Real-time SLA? Use best_for_speed
  - Balanced SLA? Use best_balanced
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns


def select_features():
    """Define feature columns for training."""
    return [
        # VNR characteristics
        'v_net_num_nodes',
        'v_net_num_edges',
        'v_net_size_ratio',
        'v_net_demand_per_node',
        'v_net_demand_per_link',
        'v_net_connectivity',
        'v_net_total_demand',
        'v_net_node_to_link_demand_ratio',
        'v_net_lifetime',

        # Physical network state
        'p_net_available_resource',
        'p_net_node_resource_utilization',
        'p_net_link_resource_utilization',
        'p_net_overall_util',
        'p_net_node_util',
        'p_net_link_util',

        # System state
        'inservice_count',
        'system_load',
        'num_running_p_net_nodes',

        # Topology
        'topology_encoded',
    ]


def create_target_variables(df):
    """
    Create target variables for each objective.
    For each VNR, determine which algorithm is best for that objective.
    """

    print("Creating target variables for each objective...")

    df['best_for_acceptance'] = None
    df['best_for_cost'] = None
    df['best_for_speed'] = None
    df['best_balanced'] = None

    # Group by VNR instance
    vnr_groups = df.groupby(['topology', 'seed', 'v_net_id'])

    for (topo, seed, vnr_id), group in vnr_groups:
        group_indices = group.index

        # Best for acceptance: algorithm with highest success rate
        best_acceptance_idx = group['success'].idxmax()
        best_acceptance_algo = df.loc[best_acceptance_idx, 'algorithm']

        # Best for cost: algorithm with lowest cost
        best_cost_idx = group['v_net_cost'].idxmin()
        best_cost_algo = df.loc[best_cost_idx, 'algorithm']

        # Best for speed: algorithm with lowest execution time
        best_speed_idx = group['clock_time_per_vnr'].idxmin()
        best_speed_algo = df.loc[best_speed_idx, 'algorithm']

        # Best balanced: equal weight across all three metrics
        # Normalize each metric to [0,1]
        success_scores = group['success'].values
        cost_scores = (group['v_net_cost'].max() - group['v_net_cost'].values) / (group['v_net_cost'].max() - group['v_net_cost'].min() + 1e-6)
        speed_scores = (group['clock_time_per_vnr'].max() - group['clock_time_per_vnr'].values) / (group['clock_time_per_vnr'].max() - group['clock_time_per_vnr'].min() + 1e-6)

        balanced_scores = (success_scores + cost_scores + speed_scores) / 3
        best_balanced_idx = group.index[np.argmax(balanced_scores)]
        best_balanced_algo = df.loc[best_balanced_idx, 'algorithm']

        # Assign labels to all rows in this VNR group
        df.loc[group_indices, 'best_for_acceptance'] = best_acceptance_algo
        df.loc[group_indices, 'best_for_cost'] = best_cost_algo
        df.loc[group_indices, 'best_for_speed'] = best_speed_algo
        df.loc[group_indices, 'best_balanced'] = best_balanced_algo

    print("Target variables created!")
    return df


def train_objective_tree(X_train, y_train, X_val, y_val, objective_name, max_depth=10):
    """Train a decision tree for a specific objective."""

    print(f"\n{'='*70}")
    print(f"Training tree for: {objective_name}")
    print(f"{'='*70}")

    # Encode labels
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    y_val_encoded = label_encoder.transform(y_val)

    print(f"Classes: {label_encoder.classes_}")
    print(f"Class distribution in training:")
    unique, counts = np.unique(y_train_encoded, return_counts=True)
    for cls, count in zip(label_encoder.classes_, counts):
        print(f"  {cls}: {count} ({100*count/len(y_train):.1f}%)")

    # Train decision tree with class weights to handle imbalance
    from sklearn.utils.class_weight import compute_sample_weight
    sample_weights = compute_sample_weight('balanced', y_train_encoded)

    model = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_split=20,
        min_samples_leaf=10,
        random_state=42,
        class_weight='balanced'
    )

    model.fit(X_train, y_train_encoded, sample_weight=sample_weights)

    # Evaluate
    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)

    train_acc = accuracy_score(y_train_encoded, y_train_pred)
    val_acc = accuracy_score(y_val_encoded, y_val_pred)

    print(f"\nTraining accuracy: {train_acc:.4f}")
    print(f"Validation accuracy: {val_acc:.4f}")

    print(f"\nValidation Classification Report:")
    print(classification_report(y_val_encoded, y_val_pred,
                              target_names=label_encoder.classes_,
                              zero_division=0))

    return model, label_encoder, train_acc, val_acc


def main():
    # Load dataset
    print("Loading dataset...")
    df = pd.read_csv('apresentacao/machine_learning/datasets/vnr_features.csv')
    print(f"Loaded {len(df):,} samples")

    # Create target variables for each objective
    df = create_target_variables(df)

    # Select features
    features = select_features()

    # Prepare data
    print(f"\nPreparing data with {len(features)} features...")
    X = df[features].copy()

    # Handle missing values
    X = X.fillna(X.mean())

    # Split data
    X_train, X_temp, idx_train, idx_temp = train_test_split(
        X, X.index, test_size=0.30, random_state=42
    )
    X_val, X_test, idx_val, idx_test = train_test_split(
        X_temp, idx_temp, test_size=0.50, random_state=42
    )

    print(f"Train: {len(X_train):,}, Val: {len(X_val):,}, Test: {len(X_test):,}")

    # Train separate trees for each objective
    objectives = [
        'best_for_acceptance',
        'best_for_cost',
        'best_for_speed',
        'best_balanced'
    ]

    models = {}
    encoders = {}
    results = {}

    for objective in objectives:
        y_train = df.loc[idx_train, objective]
        y_val = df.loc[idx_val, objective]

        # Remove NaN values
        valid_train = ~y_train.isna()
        valid_val = ~y_val.isna()

        X_train_obj = X_train[valid_train]
        y_train_obj = y_train[valid_train]
        X_val_obj = X_val[valid_val]
        y_val_obj = y_val[valid_val]

        print(f"\n{objective}:")
        print(f"  Training samples: {len(y_train_obj)}, Validation samples: {len(y_val_obj)}")

        # Train model
        model, encoder, train_acc, val_acc = train_objective_tree(
            X_train_obj, y_train_obj,
            X_val_obj, y_val_obj,
            objective,
            max_depth=8
        )

        models[objective] = model
        encoders[objective] = encoder
        results[objective] = {
            'train_accuracy': train_acc,
            'val_accuracy': val_acc,
            'num_classes': len(encoder.classes_),
            'classes': encoder.classes_
        }

    # Save models
    print(f"\n{'='*70}")
    print("Saving models...")
    print(f"{'='*70}")

    model_dir = 'apresentacao/machine_learning/models_option2'
    os.makedirs(model_dir, exist_ok=True)

    for objective in objectives:
        model_path = f'{model_dir}/{objective}_tree.pkl'
        encoder_path = f'{model_dir}/{objective}_encoder.pkl'

        with open(model_path, 'wb') as f:
            pickle.dump(models[objective], f)

        with open(encoder_path, 'wb') as f:
            pickle.dump(encoders[objective], f)

        print(f"✓ Saved {objective}")
        print(f"    Model: {model_path}")
        print(f"    Encoder: {encoder_path}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY: Multiple Objective Trees")
    print(f"{'='*70}")

    for objective in objectives:
        res = results[objective]
        print(f"\n{objective}:")
        print(f"  Classes: {res['num_classes']} algorithms")
        print(f"  Training accuracy: {res['train_accuracy']:.4f}")
        print(f"  Validation accuracy: {res['val_accuracy']:.4f}")

    print(f"\n{'='*70}")
    print("HOW TO USE THESE MODELS")
    print(f"{'='*70}")
    print("""
1. Load features from new VNR request
2. Based on current network state, choose objective:

   if p_net_overall_util > 0.8:
       # Network congested → maximize acceptance
       model = load_model('best_for_acceptance_tree.pkl')
       algo = model.predict(features)

   elif available_resources < threshold:
       # Resource constrained → minimize cost
       model = load_model('best_for_cost_tree.pkl')
       algo = model.predict(features)

   elif real_time_sla:
       # Real-time requirement → minimize time
       model = load_model('best_for_speed_tree.pkl')
       algo = model.predict(features)

   else:
       # Normal case → balanced
       model = load_model('best_balanced_tree.pkl')
       algo = model.predict(features)

3. Execute selected algorithm
""")


if __name__ == '__main__':
    main()
