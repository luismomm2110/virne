#!/usr/bin/env python3
"""
Step 3: Train Decision Trees with Advanced Class Balancing

This version implements multiple balancing strategies to handle class imbalance:
1. Custom class weights (more aggressive than 'balanced')
2. Adjusted hyperparameters for minority classes
3. Option for SMOTE oversampling (if imblearn available)

Input:  datasets/train.csv, datasets/val.csv
Output: models/decision_trees_balanced.pkl, models/tree_results_balanced.json
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, f1_score
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
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


def compute_custom_class_weights(y_train_encoded, strategy='aggressive'):
    """
    Compute custom class weights with more aggressive balancing.
    
    Strategies:
    - 'balanced': sklearn's balanced (n_samples / (n_classes * np.bincount(y)))
    - 'aggressive': 1 / sqrt(class_frequency) - gives more weight to rare classes
    - 'log': 1 / log(class_frequency + 1) - even more aggressive
    - 'inverse': 1 / class_frequency - most aggressive
    """
    unique_classes = np.unique(y_train_encoded)
    class_counts = np.bincount(y_train_encoded)
    class_counts = class_counts[unique_classes]  # Only non-zero counts
    n_samples = len(y_train_encoded)
    n_classes = len(unique_classes)
    
    if strategy == 'balanced':
        weights = n_samples / (n_classes * class_counts)
    elif strategy == 'aggressive':
        # More weight to rare classes: 1 / sqrt(frequency)
        weights = 1.0 / np.sqrt(class_counts / n_samples)
    elif strategy == 'log':
        # Even more weight: 1 / log(frequency + 1)
        weights = 1.0 / np.log1p(class_counts / n_samples * 10)
    elif strategy == 'inverse':
        # Most aggressive: 1 / frequency
        weights = n_samples / class_counts
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    # Normalize so largest weight is 10x (prevent extreme weights)
    weights = weights / weights.max() * 10.0
    
    # Create weight dictionary
    class_weight_dict = {cls: weight for cls, weight in zip(unique_classes, weights)}
    
    return class_weight_dict


def prepare_data(df, feature_cols, target_col):
    """Prepare X and y for training."""
    # Remove rows where target is NaN
    df_clean = df[df[target_col].notna()].copy()

    X = df_clean[feature_cols]
    y = df_clean[target_col]

    return X, y, df_clean


def train_decision_tree_balanced(X_train, y_train, X_val, y_val, objective_name, label_encoder, 
                                  max_depth=10, min_samples_leaf=3, min_samples_split=6, 
                                  class_weight_strategy='aggressive', use_smote=False):
    """
    Train decision tree with advanced balancing techniques.
    
    Args:
        max_depth: Maximum tree depth (increased for minority classes)
        min_samples_leaf: Minimum samples per leaf (reduced for minority classes)
        min_samples_split: Minimum samples to split (reduced for minority classes)
        class_weight_strategy: 'balanced', 'aggressive', 'log', or 'inverse'
        use_smote: Whether to use SMOTE oversampling (requires imblearn)
    """
    
    print(f"\n{'='*80}")
    print(f"Training Balanced Decision Tree for: {objective_name}")
    print(f"{'='*80}")

    # Encode labels
    y_train_encoded = label_encoder.transform(y_train)
    y_val_encoded = label_encoder.transform(y_val)

    # Check class distribution
    unique_classes, counts = np.unique(y_train_encoded, return_counts=True)
    print(f"\nClass distribution in training set:")
    for class_idx, class_label, count in zip(unique_classes, label_encoder.classes_, counts):
        pct = 100 * count / len(y_train_encoded)
        print(f"  {class_label:15s}: {count:6d} samples ({pct:5.1f}%)")

    # Compute custom class weights
    class_weight_dict = compute_custom_class_weights(y_train_encoded, strategy=class_weight_strategy)
    
    print(f"\nClass weights ({class_weight_strategy} strategy):")
    # Create mapping from class_idx to count
    idx_to_count = dict(zip(unique_classes, counts))
    for class_idx, class_label in zip(unique_classes, label_encoder.classes_):
        weight = class_weight_dict[class_idx]
        count = idx_to_count[class_idx]
        print(f"  {class_label:15s}: {weight:6.2f}x (from {count:4d} samples)")

    # Apply SMOTE if requested (only for classes with at least 2 samples)
    if use_smote:
        try:
            from imblearn.over_sampling import SMOTE
            print(f"\n  Applying SMOTE oversampling...")
            
            # Only oversample if we have minority classes
            minority_threshold = counts.min() * 2
            need_oversampling = any(counts < minority_threshold)
            
            if need_oversampling:
                smote = SMOTE(random_state=42, k_neighbors=min(3, counts.min() - 1))
                X_train_resampled, y_train_encoded_resampled = smote.fit_resample(X_train, y_train_encoded)
                
                # Update counts
                unique_classes_resampled, counts_resampled = np.unique(y_train_encoded_resampled, return_counts=True)
                print(f"  After SMOTE:")
                for class_idx, class_label, count in zip(unique_classes_resampled, label_encoder.classes_, counts_resampled):
                    pct = 100 * count / len(y_train_encoded_resampled)
                    print(f"    {class_label:15s}: {count:6d} samples ({pct:5.1f}%)")
                
                X_train = X_train_resampled
                y_train_encoded = y_train_encoded_resampled
            else:
                print(f"  SMOTE not needed (classes are reasonably balanced)")
        except ImportError:
            print(f"  ⚠️  imblearn not available, skipping SMOTE")
            print(f"  Install with: pip install imbalanced-learn")

    # Train decision tree with balanced parameters
    dt = DecisionTreeClassifier(
        max_depth=max_depth,              # Increased for better minority class handling
        min_samples_leaf=min_samples_leaf,    # Reduced to allow splits on small classes
        min_samples_split=min_samples_split,  # Reduced for minority classes
        criterion='gini',
        class_weight=class_weight_dict,   # Use custom weights
        random_state=42
    )

    dt.fit(X_train, y_train_encoded)

    # Evaluate on validation set
    y_pred = dt.predict(X_val)
    accuracy = accuracy_score(y_val_encoded, y_pred)
    train_accuracy = dt.score(X_train, y_train_encoded)
    f1 = f1_score(y_val_encoded, y_pred, average='weighted', zero_division=0)
    f1_macro = f1_score(y_val_encoded, y_pred, average='macro', zero_division=0)

    # Classification report (only for classes present in this objective)
    unique_classes_present = np.unique(np.concatenate([y_val_encoded, y_pred]))
    target_names_present = [label_encoder.classes_[i] for i in unique_classes_present]
    
    report = classification_report(
        y_val_encoded, y_pred,
        labels=unique_classes_present,
        target_names=target_names_present,
        zero_division=0,
        output_dict=True
    )

    # Per-class metrics
    print(f"\nValidation Results:")
    print(f"  Accuracy:         {accuracy:.4f}")
    print(f"  Train Accuracy:   {train_accuracy:.4f}")
    print(f"  Weighted F1:      {f1:.4f}")
    print(f"  Macro F1:         {f1_macro:.4f}")

    print(f"\nPer-Class Performance:")
    print(f"{'Class':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
    print("-" * 65)
    for class_name in target_names_present:
        if class_name in report and isinstance(report[class_name], dict):
            metrics = report[class_name]
            print(f"{class_name:<15} {metrics['precision']:>11.3f} {metrics['recall']:>11.3f} "
                  f"{metrics['f1-score']:>11.3f} {metrics['support']:>9.0f}")

    return dt, {
        'accuracy': accuracy,
        'train_accuracy': train_accuracy,
        'f1_score': f1,
        'f1_macro': f1_macro,
        'report': report,
        'confusion_matrix': confusion_matrix(y_val_encoded, y_pred),
        'class_weights': class_weight_dict
    }


def visualize_tree(dt, feature_names, class_names, objective_key, output_dir='../models'):
    """Visualize decision tree."""
    os.makedirs(output_dir, exist_ok=True)
    
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
    
    plt.title(f'Balanced Decision Tree for {objective_key.upper()}', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    filepath = os.path.join(output_dir, f'tree_balanced_{objective_key}.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {filepath}")


def visualize_confusion_matrix(cm, class_names, objective_key, output_dir='../models'):
    """Visualize confusion matrix."""
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.title(f'Confusion Matrix - Balanced {objective_key.upper()} Tree', fontsize=14, fontweight='bold')
    plt.ylabel('True Algorithm', fontsize=12)
    plt.xlabel('Predicted Algorithm', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    filepath = os.path.join(output_dir, f'confusion_balanced_{objective_key}.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {filepath}")


def save_models(models, output_dir='../models'):
    """Save all trained models."""
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, 'decision_trees_balanced.pkl')
    with open(filepath, 'wb') as f:
        pickle.dump(models, f)
    
    print(f"\n✓ Saved balanced trees: {filepath}")


def save_results(results, output_dir='../models'):
    """Save results to JSON."""
    os.makedirs(output_dir, exist_ok=True)
    
    results_json = {}
    for objective, metrics in results.items():
        # Convert class_weights dict to serializable format
        class_weights = {str(k): float(v) for k, v in metrics['class_weights'].items()}
        
        results_json[objective] = {
            'accuracy': float(metrics['accuracy']),
            'train_accuracy': float(metrics['train_accuracy']),
            'f1_score': float(metrics['f1_score']),
            'f1_macro': float(metrics['f1_macro']),
            'class_weights': class_weights,
            'per_class': {name: {
                'precision': float(metrics['report'][name]['precision']),
                'recall': float(metrics['report'][name]['recall']),
                'f1-score': float(metrics['report'][name]['f1-score']),
                'support': int(metrics['report'][name]['support'])
            } for name in metrics['report'].keys() if name not in ['accuracy', 'macro avg', 'weighted avg']}
        }
    
    filepath = os.path.join(output_dir, 'tree_results_balanced.json')
    with open(filepath, 'w') as f:
        json.dump(results_json, f, indent=2)
    
    print(f"✓ Saved results: {filepath}")


if __name__ == '__main__':
    print("="*80)
    print("TRAINING DECISION TREES WITH ADVANCED CLASS BALANCING")
    print("="*80)
    
    # Load data
    print("\nLoading training and validation datasets...")
    train_df = pd.read_csv('../datasets/train.csv')
    val_df = pd.read_csv('../datasets/val.csv')
    
    print(f"  Train: {train_df.shape[0]} samples")
    print(f"  Val:   {val_df.shape[0]} samples")
    
    # Select features
    feature_cols = select_features()
    print(f"\nUsing {len(feature_cols)} features for training")
    
    # Get all algorithms from train + val
    all_algos = pd.concat([
        train_df['best_for_rac'].dropna(),
        train_df['best_for_lrc'].dropna(),
        train_df['best_for_lar'].dropna(),
        train_df['best_for_ast'].dropna(),
        train_df['best_for_balanced'].dropna()
    ]).unique()
    
    # Create label encoder
    label_encoder = LabelEncoder()
    label_encoder.fit(all_algos)
    
    # Save encoder
    os.makedirs('../models', exist_ok=True)
    with open('../models/algorithm_label_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)
    
    print(f"\nAlgorithms: {list(label_encoder.classes_)}")
    print(f"✓ Saved label encoder")
    
    # Define objectives
    objectives = {
        'rac': ('Request Acceptance Rate (RAC)', 'best_for_rac'),
        'lrc': ('Long-Term Revenue-to-Cost (LRC)', 'best_for_lrc'),
        'lar': ('Long-Term Average Revenue (LAR)', 'best_for_lar'),
        'ast': ('Average Solving Time (AST)', 'best_for_ast'),
        'balanced': ('Balanced (0.8*revenue - 0.2*time)', 'best_for_balanced')
    }
    
    # Training parameters
    training_config = {
        'max_depth': 10,           # Increased for better minority class handling
        'min_samples_leaf': 3,     # Reduced (was 10) to allow splits on small classes
        'min_samples_split': 6,    # Reduced (was 20) for minority classes
        'class_weight_strategy': 'aggressive',  # More aggressive than 'balanced'
        'use_smote': False          # Set True if imblearn is installed
    }
    
    print(f"\nTraining Configuration:")
    print(f"  Max Depth: {training_config['max_depth']}")
    print(f"  Min Samples Leaf: {training_config['min_samples_leaf']}")
    print(f"  Min Samples Split: {training_config['min_samples_split']}")
    print(f"  Class Weight Strategy: {training_config['class_weight_strategy']}")
    print(f"  SMOTE: {training_config['use_smote']}")
    
    # Train trees
    models = {}
    results = {}
    
    for obj_key, (obj_name, target_col) in objectives.items():
        # Prepare data
        X_train, y_train, train_clean = prepare_data(train_df, feature_cols, target_col)
        X_val, y_val, val_clean = prepare_data(val_df, feature_cols, target_col)
        
        print(f"\n{'='*80}")
        print(f"Objective: {obj_key.upper()}")
        print(f"  Train samples: {len(X_train)}")
        print(f"  Val samples:   {len(X_val)}")
        
        # Train tree
        dt, metrics = train_decision_tree_balanced(
            X_train, y_train, X_val, y_val, obj_name, label_encoder,
            **training_config
        )
        
        models[obj_key] = dt
        results[obj_key] = metrics
        
        # Visualize
        visualize_tree(dt, feature_cols, label_encoder.classes_, obj_key)
        visualize_confusion_matrix(metrics['confusion_matrix'], label_encoder.classes_, obj_key)
    
    # Save models and results
    save_models(models)
    save_results(results)
    
    # Print summary
    print("\n" + "="*80)
    print("TRAINING SUMMARY - BALANCED TREES")
    print("="*80)
    print(f"\n{'Objective':<12} {'Accuracy':<12} {'F1-Weighted':<12} {'F1-Macro':<12}")
    print("-" * 50)
    for obj_key in objectives.keys():
        if obj_key in results:
            r = results[obj_key]
            print(f"{obj_key:<12} {r['accuracy']:>11.4f} {r['f1_score']:>11.4f} {r['f1_macro']:>11.4f}")
    
    print("\n✅ Balanced decision tree training complete!")
    print("\nTo evaluate these models, run:")
    print("  python 4_evaluate_trees.py  # (will use balanced models if available)")
