#!/usr/bin/env python3

import pandas as pd
import numpy as np
import pickle
import os
import xgboost as xgb
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import (classification_report, confusion_matrix,
                              accuracy_score, f1_score, ConfusionMatrixDisplay)
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

        # Algorithm characteristics (computational effort)
        'solving_time',

        # Topology
        'topology_encoded'
    ]


def prepare_data(df, feature_cols, target_col='best_overall'):
    """Prepare X and y for training."""

    # Remove rows where target is NaN (no algorithm accepted)
    df = df[df[target_col].notna()].copy()

    X = df[feature_cols]
    y = df[target_col]


    return X, y


def train_with_grid_search(X_train, y_train, X_val, y_val, label_encoder):
    """Train XGBoost with hyperparameter tuning and class weights."""


    # Encode labels to integers (XGBoost requirement for multiclass)
    y_train_encoded = label_encoder.transform(y_train)
    y_val_encoded = label_encoder.transform(y_val)

    # Calculate class weights to handle imbalanced data
    from sklearn.utils.class_weight import compute_sample_weight
    class_weights = compute_sample_weight('balanced', y_train_encoded)

    print("\n✓ Class weights (balanced) to handle imbalance:")
    unique_classes, counts = np.unique(y_train_encoded, return_counts=True)
    for class_idx, class_label, count in zip(unique_classes, label_encoder.classes_, counts):
        weight = class_weights[y_train_encoded == class_idx][0]
        print(f"  {class_label:15s}: {count:4d} samples → weight {weight:.4f}")

    # Define parameter grid (simplified for faster training)
    param_grid = {
        'max_depth': [5, 7],
        'learning_rate': [0.1, 0.3],
        'n_estimators': [100, 200],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0],
    }

    # Base estimator - num_class must match actual unique classes in training data
    num_classes = len(np.unique(y_train_encoded))
    xgb_model = xgb.XGBClassifier(
        objective='multi:softmax',
        num_class=num_classes,
        random_state=42,
        n_jobs=-1,
        eval_metric='mlogloss'
    )

    # Cross-validation strategy (4-fold on training data)
    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)

    # Grid search
    grid_search = GridSearchCV(
        estimator=xgb_model,
        param_grid=param_grid,
        cv=cv,
        scoring='f1_weighted',
        n_jobs=-1,
        verbose=2
    )

    # Fit with sample weights to handle class imbalance
    grid_search.fit(X_train, y_train_encoded, sample_weight=class_weights)

    # Best model
    best_model = grid_search.best_estimator_


    # Evaluate on validation set
    y_val_pred = best_model.predict(X_val)
    y_val_pred_labels = label_encoder.inverse_transform(y_val_pred)
    val_accuracy = accuracy_score(y_val, y_val_pred_labels)
    val_f1 = f1_score(y_val, y_val_pred_labels, average='weighted')


    return best_model, grid_search


def evaluate_model(model, X, y, label_encoder, dataset_name='Test'):
    """Evaluate model and print detailed metrics."""


    # Predict
    y_pred_encoded = model.predict(X)
    y_pred = label_encoder.inverse_transform(y_pred_encoded)

    # Overall metrics
    accuracy = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred, average='weighted')

    # Per-class metrics
    print(classification_report(y, y_pred))

    # Confusion matrix
    cm = confusion_matrix(y, y_pred, labels=label_encoder.classes_)

    return y_pred, cm


def plot_confusion_matrix(cm, classes, output_path='results/confusion_matrix.png'):
    """Plot and save confusion matrix."""

    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix - XGBoost Selector', fontsize=14, fontweight='bold')
    plt.xlabel('Predicted Algorithm', fontsize=12)
    plt.ylabel('True Best Algorithm', fontsize=12)
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Confusion matrix saved: {output_path}")
    plt.close()


def plot_feature_importance(model, feature_names, output_path='results/feature_importance.png'):
    """Plot feature importance from XGBoost."""

    # Get importance scores
    importance_dict = model.get_booster().get_score(importance_type='weight')

    # Map feature indices to names
    importances = []
    for i, fname in enumerate(feature_names):
        feature_key = f'f{i}'
        importances.append(importance_dict.get(feature_key, 0))

    importances = np.array(importances)
    indices = np.argsort(importances)[::-1]

    # Top 15 features
    top_n = min(15, len(feature_names))
    top_indices = indices[:top_n]

    plt.figure(figsize=(10, 8))
    plt.barh(range(top_n), importances[top_indices], align='center')
    plt.yticks(range(top_n), [feature_names[i] for i in top_indices])
    plt.xlabel('Feature Importance (Weight)', fontsize=12)
    plt.title('Top Feature Importances - XGBoost', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_learning_curves(grid_search, output_path='results/cv_scores.png'):
    """Plot cross-validation learning curves."""

    cv_results = pd.DataFrame(grid_search.cv_results_)

    # Get top 10 configurations by mean test score
    top_configs = cv_results.nlargest(10, 'mean_test_score')

    plt.figure(figsize=(12, 6))

    # Plot scores
    x = range(len(top_configs))
    plt.errorbar(x, top_configs['mean_test_score'],
                 yerr=top_configs['std_test_score'],
                 fmt='o-', capsize=5, capthick=2)

    plt.xlabel('Configuration Rank', fontsize=12)
    plt.ylabel('Mean CV F1-Score', fontsize=12)
    plt.title('Top 10 Configurations - Cross-Validation Scores', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ CV scores plot saved: {output_path}")
    plt.close()


def save_model(model, label_encoder, output_path='models/xgb_balanced_model.pkl'):
    """Save trained model and label encoder to disk."""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save model
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)

    # Save label encoder
    encoder_path = output_path.replace('.pkl', '_label_encoder.pkl')
    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)

    print(f"\n✓ Model saved: {output_path}")
    print(f"✓ Label encoder saved: {encoder_path}")


def export_feature_importance_text(model, feature_names, output_path='results/feature_importance.txt'):
    """Export feature importance as text."""

    importance_dict = model.get_booster().get_score(importance_type='weight')

    # Map and sort
    importances = []
    for i, fname in enumerate(feature_names):
        feature_key = f'f{i}'
        score = importance_dict.get(feature_key, 0)
        importances.append((fname, score))

    importances.sort(key=lambda x: x[1], reverse=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write("Feature Importance (XGBoost)\n")
        f.write("="*60 + "\n\n")
        for rank, (feature, score) in enumerate(importances, 1):
            f.write(f"{rank:3d}. {feature:40s} {score:8.1f}\n")



if __name__ == '__main__':

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load data with absolute paths
    train_path = os.path.join(script_dir, 'datasets/train.csv')
    val_path = os.path.join(script_dir, 'datasets/val.csv')
    test_path = os.path.join(script_dir, 'datasets/test.csv')

    train_df = pd.read_csv(train_path)
    print(f"✓ Loaded training data: {len(train_df)} rows")

    # Check if val/test exist and have data
    val_df = pd.read_csv(val_path) if os.path.exists(val_path) else pd.DataFrame()
    test_df = pd.read_csv(test_path) if os.path.exists(test_path) else pd.DataFrame()

    # If no val/test data, use train for everything (will use CV for validation)
    if len(val_df) == 0:
        print("⚠ No validation data found - using cross-validation on training set")
        val_df = train_df.copy()
    else:
        print(f"✓ Loaded validation data: {len(val_df)} rows")

    if len(test_df) == 0:
        print("⚠ No test data found - using training set for final evaluation")
        test_df = train_df.copy()
    else:
        print(f"✓ Loaded test data: {len(test_df)} rows")


    # Select features
    feature_cols = select_features()
    target_col = 'best_overall'  # Options: 'best_for_acceptance', 'best_for_time', 'best_overall'

    X_train, y_train = prepare_data(train_df, feature_cols, target_col)
    X_val, y_val = prepare_data(val_df, feature_cols, target_col)
    X_test, y_test = prepare_data(test_df, feature_cols, target_col)

    # Create label encoder with only classes present in training data
    # This ensures XGBoost gets consecutive class labels 0,1,2,...,n-1
    unique_train_classes = sorted(y_train.unique())
    label_encoder = LabelEncoder()
    label_encoder.fit(unique_train_classes)
    for idx, label in enumerate(label_encoder.classes_):
        print(f"    {idx}: {label}")

    # Train model with grid search
    model, grid_search = train_with_grid_search(X_train, y_train, X_val, y_val, label_encoder)

    # Evaluate on test set
    y_test_pred, cm = evaluate_model(model, X_test, y_test, label_encoder, dataset_name='Test')

    # Visualizations
    plot_confusion_matrix(cm, label_encoder.classes_)
    plot_feature_importance(model, feature_cols)
    plot_learning_curves(grid_search)
    export_feature_importance_text(model, feature_cols)

    # Save model
    save_model(model, label_encoder, f'models/xgb_{target_col}_model.pkl')
