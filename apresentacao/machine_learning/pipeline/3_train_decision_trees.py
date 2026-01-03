#!/usr/bin/env python3
"""
Step 3: Train Decision Trees for Multi-Objective VNE Algorithm Selection

This script trains 5 SEPARATE decision trees, one for each VIRNe performance metric:
1. RAC (Request Acceptance Rate) - Maximize acceptance
2. LRC (Long-Term Revenue-to-Cost) - Maximize profitability
3. LAR (Long-Term Average Revenue) - Maximize revenue
4. AST (Average Solving Time) - Minimize execution time
5. BALANCED (Composite) - Maximize (0.8*revenue - 0.2*time) [only if accepted]

Input:  datasets/train.csv, datasets/val.csv
Output: models/decision_tree_*.pkl, models/tree_results.json

This multi-objective approach enables runtime switching between objectives:
- Want to maximize acceptance? Use tree_rac
- Want cost-efficiency? Use tree_lrc
- Want speed? Use tree_ast
- Want balanced profit & speed? Use tree_balanced
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, f1_score
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
        'p_net_node_util',
        'p_net_link_util',
        'p_net_overall_util',

        # System state
        'inservice_count',
        'system_load',
        'num_running_p_net_nodes',

        # Topology
        'topology_encoded',

        # Engineered features
        'network_stress_index',
        'problem_complexity',
        'resource_bottleneck_ratio',
        'vnr_size_category',
        'cpu_intensive_flag',
        'bandwidth_intensive_flag',
        'utilization_pressure',
        'resource_efficiency'
    ]


def prepare_data(df, feature_cols, target_col):
    """Prepare X and y for training."""
    # Remove rows where target is NaN (no algorithm best for this objective)
    df_clean = df[df[target_col].notna()].copy()

    X = df_clean[feature_cols]
    y = df_clean[target_col]

    return X, y, df_clean


def train_decision_tree(X_train, y_train, X_val, y_val, objective_name, label_encoder):
    """Train a single decision tree for one objective."""

    print(f"\n{'='*80}")
    print(f"Training Decision Tree for: {objective_name}")
    print(f"{'='*80}")

    # Encode labels to integers
    y_train_encoded = label_encoder.transform(y_train)
    y_val_encoded = label_encoder.transform(y_val)

    # Check class distribution
    unique_classes, counts = np.unique(y_train_encoded, return_counts=True)
    print(f"\nClass distribution in training set:")
    for class_idx, class_label, count in zip(unique_classes, label_encoder.classes_, counts):
        pct = 100 * count / len(y_train_encoded)
        print(f"  {class_label:15s}: {count:6d} samples ({pct:5.1f}%)")

    # Calculate class weights to handle imbalanced data
    from sklearn.utils.class_weight import compute_sample_weight
    sample_weights = compute_sample_weight('balanced', y_train_encoded)

    # Train decision tree with hyperparameters optimized for interpretability
    dt = DecisionTreeClassifier(
        max_depth=5,              # Limit depth for interpretability (as in ACADEMIC_ANALYSIS_OPTION2.md)
        min_samples_leaf=10,      # Prevent overfitting
        min_samples_split=20,     # Require more samples to split
        criterion='gini',         # Use Gini impurity
        random_state=42
    )

    dt.fit(X_train, y_train_encoded, sample_weight=sample_weights)

    # Evaluate on validation set
    y_pred = dt.predict(X_val)
    accuracy = accuracy_score(y_val_encoded, y_pred)
    train_accuracy = dt.score(X_train, y_train_encoded)
    f1 = f1_score(y_val_encoded, y_pred, average='weighted', zero_division=0)

    # Get classification report
    # Get only the classes that are present in this objective
    unique_classes = np.unique(np.concatenate([y_val_encoded, y_pred]))
    target_names = [label_encoder.classes_[i] for i in unique_classes]

    report = classification_report(
        y_val_encoded, y_pred,
        labels=unique_classes,
        target_names=target_names,
        zero_division=0
    )

    print(f"\nValidation Results:")
    print(f"  Accuracy:       {accuracy:.4f}")
    print(f"  Train Accuracy: {train_accuracy:.4f}")
    print(f"  Weighted F1:    {f1:.4f}")
    print(f"\nClassification Report:")
    print(report)

    return dt, {
        'accuracy': accuracy,
        'train_accuracy': train_accuracy,
        'f1_score': f1,
        'report': report,
        'confusion_matrix': confusion_matrix(y_val_encoded, y_pred)
    }


def visualize_tree(dt, feature_names, class_names, objective_key, output_dir='models'):
    """Visualize decision tree and save to file."""

    plt.figure(figsize=(20, 12))
    plot_tree(
        dt,
        feature_names=feature_names,
        class_names=class_names,
        filled=True,
        fontsize=9,
        rounded=True,
        proportion=True
    )

    plt.title(f'Decision Tree for {objective_key.upper()} Algorithm Selection', fontsize=16, fontweight='bold')
    plt.tight_layout()

    filepath = os.path.join(output_dir, f'tree_{objective_key}.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  ✓ Saved visualization: {filepath}")


def visualize_confusion_matrix(cm, class_names, objective_key, output_dir='models'):
    """Visualize and save confusion matrix."""

    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title(f'Confusion Matrix - {objective_key.upper()} Tree')
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()

    filepath = os.path.join(output_dir, f'confusion_{objective_key}.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  ✓ Saved confusion matrix: {filepath}")


def save_models(models, output_dir='models'):
    """Save all trained models to pickle file."""
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, 'decision_trees.pkl')
    with open(filepath, 'wb') as f:
        pickle.dump(models, f)

    print(f"\n✓ Saved all decision trees: {filepath}")


def save_results(results, output_dir='models'):
    """Save model evaluation results to JSON."""
    os.makedirs(output_dir, exist_ok=True)

    # Convert numpy arrays and non-serializable objects to JSON-friendly format
    results_json = {}
    for objective, metrics in results.items():
        results_json[objective] = {
            'accuracy': float(metrics['accuracy']),
            'train_accuracy': float(metrics['train_accuracy']),
            'f1_score': float(metrics['f1_score']),
            'report': metrics['report'],
            # Skip confusion_matrix for now (too large for JSON)
        }

    filepath = os.path.join(output_dir, 'tree_results.json')
    with open(filepath, 'w') as f:
        json.dump(results_json, f, indent=2)

    print(f"✓ Saved results summary: {filepath}")


def print_summary(results):
    """Print summary of all 4 trees."""

    print("\n" + "="*80)
    print("DECISION TREE TRAINING SUMMARY")
    print("="*80)

    objectives = {
        'rac': 'Request Acceptance Rate',
        'lrc': 'Long-Term Revenue-to-Cost',
        'lar': 'Long-Term Average Revenue',
        'ast': 'Average Solving Time'
    }

    print("\nModel Performance by Objective:")
    print(f"{'Objective':<25} {'Accuracy':<12} {'F1-Score':<12} {'Train Acc':<12}")
    print("-" * 70)

    for obj_key in ['rac', 'lrc', 'lar', 'ast']:
        if obj_key in results:
            metrics = results[obj_key]
            print(f"{objectives[obj_key]:<25} "
                  f"{metrics['accuracy']:<12.4f} "
                  f"{metrics['f1_score']:<12.4f} "
                  f"{metrics['train_accuracy']:<12.4f}")

    print("\nInterpretation:")
    print("  ✓ Each tree learns which algorithm is best for ONE specific objective")
    print("  ✓ Switch trees at runtime to change optimization priority")
    print("  ✓ Max depth=5 for interpretability (can visualize decision paths)")
    print("  ✓ Balanced class weights to handle class imbalance")
    print("="*80 + "\n")


if __name__ == '__main__':
    # Load training and validation data
    print("Loading training and validation datasets...")
    train_df = pd.read_csv('../datasets/train.csv')
    val_df = pd.read_csv('../datasets/val.csv')

    print(f"  Train: {train_df.shape[0]} samples")
    print(f"  Val:   {val_df.shape[0]} samples\n")

    # Select features
    feature_cols = select_features()
    print(f"Using {len(feature_cols)} features for training")

    # Combine train + val for encoding label (to get all possible algorithms)
    all_algos = pd.concat([train_df['best_for_rac'].dropna(),
                           train_df['best_for_lrc'].dropna(),
                           train_df['best_for_lar'].dropna(),
                           train_df['best_for_ast'].dropna()]).unique()

    # Create label encoder
    label_encoder = LabelEncoder()
    label_encoder.fit(all_algos)

    # Save label encoder
    os.makedirs('models', exist_ok=True)
    with open('../models/algorithm_label_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)

    print(f"\nAlgorithms: {list(label_encoder.classes_)}")
    print(f"✓ Saved label encoder: models/algorithm_label_encoder.pkl")

    # Define objectives to optimize
    objectives = {
        'rac': ('Request Acceptance Rate', 'best_for_rac'),
        'lrc': ('Long-Term Revenue-to-Cost', 'best_for_lrc'),
        'lar': ('Long-Term Average Revenue', 'best_for_lar'),
        'ast': ('Average Solving Time', 'best_for_ast'),
        'balanced': ('Balanced (0.8*revenue - 0.2*time)', 'best_for_balanced')
    }

    # Train 5 decision trees (one per objective)
    models = {}
    results = {}

    for obj_key, (obj_name, target_col) in objectives.items():
        # Prepare data for this objective
        X_train, y_train, train_clean = prepare_data(train_df, feature_cols, target_col)
        X_val, y_val, val_clean = prepare_data(val_df, feature_cols, target_col)

        print(f"\nTraining data for {obj_key.upper()}:")
        print(f"  Train samples: {len(X_train)}")
        print(f"  Val samples:   {len(X_val)}")

        # Train tree
        dt, metrics = train_decision_tree(X_train, y_train, X_val, y_val, obj_name, label_encoder)

        models[obj_key] = dt
        results[obj_key] = metrics

        # Visualize
        print(f"\nVisualizing tree...")
        visualize_tree(dt, feature_cols, label_encoder.classes_, obj_key)
        visualize_confusion_matrix(metrics['confusion_matrix'], label_encoder.classes_, obj_key)

    # Save all models
    save_models(models)
    save_results(results)

    # Print summary
    print_summary(results)

    print("\n✅ Decision tree training complete!")
    print("\nYou can now use these trees for runtime algorithm selection:")
    print("  - Import from: models/decision_trees.pkl")
    print("  - Select objective at runtime (rac, lrc, lar, or ast)")
    print("  - Predict algorithm based on network state features")