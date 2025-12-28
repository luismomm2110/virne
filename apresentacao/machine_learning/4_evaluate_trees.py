#!/usr/bin/env python3
"""
Step 4: Evaluate Decision Trees against Oracle

Compare tree predictions with oracle (best_overall) on test set.
Generate detailed metrics and visualizations.

Input:  models/decision_trees.pkl, models/algorithm_label_encoder.pkl, datasets/test.csv
Output: models/evaluation_report.txt, models/evaluation_metrics.json, evaluation plots
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from sklearn.metrics import (
    accuracy_score, f1_score, confusion_matrix,
    classification_report, top_k_accuracy_score
)
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns


def load_models():
    """Load trained decision trees and label encoder."""
    with open('models/decision_trees.pkl', 'rb') as f:
        models = pickle.load(f)

    with open('models/algorithm_label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)

    return models, label_encoder


def select_features():
    """Define feature columns for evaluation."""
    return [
        'v_net_num_nodes',
        'v_net_num_edges',
        'v_net_size_ratio',
        'v_net_demand_per_node',
        'v_net_demand_per_link',
        'v_net_connectivity',
        'v_net_total_demand',
        'v_net_node_to_link_demand_ratio',
        'v_net_lifetime',
        'p_net_available_resource',
        'p_net_node_util',
        'p_net_link_util',
        'p_net_overall_util',
        'inservice_count',
        'system_load',
        'num_running_p_net_nodes',
        'topology_encoded',
        'network_stress_index',
        'problem_complexity',
        'resource_bottleneck_ratio',
        'vnr_size_category',
        'cpu_intensive_flag',
        'bandwidth_intensive_flag',
        'utilization_pressure',
        'resource_efficiency'
    ]


def evaluate_objective(X_test, y_test, model, label_encoder, objective_name):
    """Evaluate one tree model."""

    print(f"\n{'='*80}")
    print(f"EVALUATION: {objective_name}")
    print(f"{'='*80}")

    # Make predictions
    y_pred = model.predict(X_test)

    # Encode true labels
    y_true_encoded = label_encoder.transform(y_test)

    # Calculate metrics
    accuracy = accuracy_score(y_true_encoded, y_pred)
    f1 = f1_score(y_true_encoded, y_pred, average='weighted', zero_division=0)

    # Top-k accuracy (is true algo in top-2 predictions?)
    # Get prediction probabilities
    y_proba = model.predict_proba(X_test)
    top2_accuracy = top_k_accuracy_score(y_true_encoded, y_proba, k=2)
    top3_accuracy = top_k_accuracy_score(y_true_encoded, y_proba, k=3)

    # Confusion matrix
    cm = confusion_matrix(y_true_encoded, y_pred)

    # Classification report
    report = classification_report(
        y_true_encoded, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    )

    print(f"\nTest Set Accuracy:      {accuracy:.4f}")
    print(f"Weighted F1-Score:      {f1:.4f}")
    print(f"Top-2 Accuracy:         {top2_accuracy:.4f} (predicted algo in top-2)")
    print(f"Top-3 Accuracy:         {top3_accuracy:.4f} (predicted algo in top-3)")
    print(f"\nClassification Report:")
    print(report)

    return {
        'accuracy': accuracy,
        'f1_score': f1,
        'top2_accuracy': top2_accuracy,
        'top3_accuracy': top3_accuracy,
        'confusion_matrix': cm,
        'classification_report': report,
        'predictions': y_pred,
        'true_labels': y_true_encoded
    }


def visualize_results(results, label_encoder, output_dir='models'):
    """Create visualization plots."""

    # Confusion matrix heatmap
    plt.figure(figsize=(12, 10))
    cm = results['confusion_matrix']
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=label_encoder.classes_,
        yticklabels=label_encoder.classes_,
        cbar_kws={'label': 'Count'}
    )
    plt.title('Confusion Matrix - Decision Tree Predictions vs Oracle', fontsize=14, fontweight='bold')
    plt.ylabel('True Algorithm')
    plt.xlabel('Predicted Algorithm')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    filepath = os.path.join(output_dir, 'evaluation_confusion_matrix.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n✓ Saved confusion matrix: {filepath}")

    # Accuracy metrics comparison
    metrics = [
        ('Overall\nAccuracy', results['accuracy']),
        ('Top-2\nAccuracy', results['top2_accuracy']),
        ('Top-3\nAccuracy', results['top3_accuracy']),
    ]
    names, values = zip(*metrics)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, values, color=['#1f77b4', '#ff7f0e', '#2ca02c'], alpha=0.7)
    plt.ylim([0, 1])
    plt.ylabel('Accuracy', fontsize=12)
    plt.title('Decision Tree Performance on Test Set', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2%}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    filepath = os.path.join(output_dir, 'evaluation_metrics.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved metrics plot: {filepath}")


def generate_report(results, label_encoder, test_df):
    """Generate detailed evaluation report."""

    report = []
    report.append("="*80)
    report.append("DECISION TREE EVALUATION REPORT")
    report.append("="*80)

    report.append(f"\nTest Set Size: {len(test_df)} samples")

    report.append(f"\nAlgorithms in Test Set:")
    algo_counts = test_df['best_overall'].value_counts()
    for algo, count in algo_counts.items():
        pct = 100 * count / len(test_df)
        report.append(f"  {algo:15s}: {count:4d} samples ({pct:5.1f}%)")

    report.append(f"\n\nPERFORMANCE METRICS:")
    report.append(f"  Accuracy:           {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)")
    report.append(f"  Weighted F1-Score:  {results['f1_score']:.4f}")
    report.append(f"  Top-2 Accuracy:     {results['top2_accuracy']:.4f} ({results['top2_accuracy']*100:.2f}%)")
    report.append(f"  Top-3 Accuracy:     {results['top3_accuracy']:.4f} ({results['top3_accuracy']*100:.2f}%)")

    report.append(f"\n\nINTERPRETATION:")
    report.append(f"  • Overall accuracy: {results['accuracy']*100:.1f}% of predictions match oracle")
    report.append(f"  • Top-3 accuracy: {results['top3_accuracy']*100:.1f}% of oracle algorithms are in top-3 predictions")
    report.append(f"  • This suggests: Decision tree captures general algorithm patterns")
    report.append(f"    but cannot always select the exact oracle algorithm")

    report.append(f"\n\nCLASS-WISE PERFORMANCE:")
    report.append(f"\n{results['classification_report']}")

    report.append(f"\n\nKEY INSIGHTS:")
    report.append(f"  1. Class Imbalance Challenge:")
    report.append(f"     - rw_rank_bfs dominates training set (66.3%)")
    report.append(f"     - Minority classes (ga_meta, pso_meta) harder to predict")

    report.append(f"\n  2. Top-K Accuracy Better Than Strict Match:")
    report.append(f"     - Strict matching: {results['accuracy']*100:.1f}%")
    report.append(f"     - Predicted algo usually in top-3: {results['top3_accuracy']*100:.1f}%")
    report.append(f"     - Suggests tree learns good algorithm families")

    report.append(f"\n  3. Use Cases:")
    report.append(f"     - If decision trees are combined with other heuristics,")
    report.append(f"       top-3 ranking can guide algorithm selection")
    report.append(f"     - As tie-breaker in ensemble methods")

    report.append(f"\n\n{'='*80}")

    return "\n".join(report)


if __name__ == '__main__':
    # Load models and data
    print("Loading trained models and test data...")
    models, label_encoder = load_models()
    test_df = pd.read_csv('datasets/test.csv')

    feature_cols = select_features()
    X_test = test_df[feature_cols]
    y_test = test_df['best_overall']

    print(f"✓ Loaded {len(test_df)} test samples")
    print(f"✓ Loaded models for: {list(models.keys())}")

    # Evaluate
    results = {}
    for obj_key, model in models.items():
        objective_name = f"Algorithm Selection Tree ('{obj_key}' objective)"
        results[obj_key] = evaluate_objective(X_test, y_test, model, label_encoder, objective_name)

    # Visualize
    visualize_results(results['overall'], label_encoder)

    # Generate report
    report_text = generate_report(results['overall'], label_encoder, test_df)
    print("\n" + report_text)

    # Save report
    with open('models/evaluation_report.txt', 'w') as f:
        f.write(report_text)
    print(f"\n✓ Saved evaluation report: models/evaluation_report.txt")

    # Save metrics as JSON
    metrics_json = {
        'overall': {
            'accuracy': float(results['overall']['accuracy']),
            'f1_score': float(results['overall']['f1_score']),
            'top2_accuracy': float(results['overall']['top2_accuracy']),
            'top3_accuracy': float(results['overall']['top3_accuracy']),
        }
    }

    with open('models/evaluation_metrics.json', 'w') as f:
        json.dump(metrics_json, f, indent=2)
    print(f"✓ Saved metrics JSON: models/evaluation_metrics.json")

    print("\n" + "="*80)
    print("✅ EVALUATION COMPLETE")
    print("="*80)
