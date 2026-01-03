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
    """Load trained decision trees and label encoder.
    Tries to load balanced models first, falls back to regular models.
    """
    # Try balanced models first
    balanced_path = '../models/decision_trees_balanced.pkl'
    regular_path = '../models/decision_trees.pkl'
    
    if os.path.exists(balanced_path):
        print("  ✓ Loading BALANCED decision trees (improved class balancing)")
        with open(balanced_path, 'rb') as f:
            models = pickle.load(f)
    elif os.path.exists(regular_path):
        print("  ✓ Loading regular decision trees")
        with open(regular_path, 'rb') as f:
            models = pickle.load(f)
    else:
        raise FileNotFoundError(f"No model file found. Expected {balanced_path} or {regular_path}")

    with open('../models/algorithm_label_encoder.pkl', 'rb') as f:
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


def visualize_results(results, label_encoder, output_dir='models', objective_key=None):
    """Create visualization plots."""
    
    suffix = f"_{objective_key}" if objective_key else ""

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

    filepath = os.path.join(output_dir, f'evaluation_confusion_matrix{suffix}.png')
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
    filepath = os.path.join(output_dir, f'evaluation_metrics{suffix}.png')
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
    test_df = pd.read_csv('../datasets/test.csv')

    print(f"✓ Loaded {len(test_df)} test samples")
    print(f"✓ Loaded models for: {list(models.keys())}")
    
    # Check if using balanced models
    using_balanced = os.path.exists('../models/decision_trees_balanced.pkl')
    if using_balanced:
        print(f"  → Using BALANCED models with improved class balancing")

    # Map objectives to their target columns
    objective_to_target = {
        'rac': 'best_for_rac',
        'lar': 'best_for_lar',
        'lrc': 'best_for_lrc',
        'ast': 'best_for_ast',
        'balanced': 'best_for_balanced'
    }

    # Select which objectives to evaluate (RAC, LAR, LRC as requested)
    objectives_to_evaluate = ['rac', 'lar', 'lrc']
    
    # Verify target columns exist
    missing_cols = []
    for obj in objectives_to_evaluate:
        if obj in objective_to_target:
            target_col = objective_to_target[obj]
            if target_col not in test_df.columns:
                missing_cols.append(f"{obj} -> {target_col}")
    
    if missing_cols:
        raise ValueError(f"Missing target columns in test dataset: {missing_cols}")

    # Get features expected by the models (try to infer from first model)
    # Try to get feature names from the model itself if available
    try:
        first_model = list(models.values())[0]
        if hasattr(first_model, 'feature_names_in_'):
            expected_features = list(first_model.feature_names_in_)
            print(f"  Usando features do modelo: {len(expected_features)} features")
        else:
            # Fall back to select_features if model doesn't have feature names
            expected_features = select_features()
            print(f"  Usando features padrão: {len(expected_features)} features")
    except:
        expected_features = select_features()
        print(f"  Usando features padrão: {len(expected_features)} features")
    
    # Check which features are missing
    missing_features = [f for f in expected_features if f not in test_df.columns]
    if missing_features:
        print(f"  ⚠️  Aviso: {len(missing_features)} features faltando no dataset, preenchendo com 0:")
        for f in missing_features:
            print(f"      - {f}")
            test_df[f] = 0.0
    
    # Select only features that are expected (and available or created)
    feature_cols = [f for f in expected_features if f in test_df.columns]
    X_test = test_df[feature_cols]
    
    # Verify we have all expected features
    if len(feature_cols) != len(expected_features):
        missing = set(expected_features) - set(feature_cols)
        raise ValueError(f"Features faltando mesmo após tentar criar: {missing}")

    print(f"\n{'='*80}")
    print(f"AVALIANDO {len(objectives_to_evaluate)} ÁRVORES: {', '.join(obj.upper() for obj in objectives_to_evaluate)}")
    print(f"{'='*80}\n")

    # Evaluate each objective
    results = {}
    for obj_key in objectives_to_evaluate:
        if obj_key not in models:
            print(f"⚠️  Aviso: Modelo '{obj_key}' não encontrado, pulando...")
            continue
        
        target_col = objective_to_target[obj_key]
        y_test = test_df[target_col]
        
        # Get objective name
        obj_names = {
            'rac': 'Request Acceptance Rate (RAC)',
            'lar': 'Long-Term Average Revenue (LAR)',
            'lrc': 'Long-Term Revenue-to-Cost (LRC)',
            'ast': 'Average Solving Time (AST)',
            'balanced': 'Balanced (0.8*revenue - 0.2*time)'
        }
        objective_name = obj_names.get(obj_key, obj_key.upper())
        
        model = models[obj_key]
        results[obj_key] = evaluate_objective(X_test, y_test, model, label_encoder, objective_name)

    # Generate summary table
    print(f"\n{'='*80}")
    print("RESUMO DAS ACURÁCIAS")
    print(f"{'='*80}")
    print(f"{'Objetivo':<25} {'Acurácia':<15} {'F1-Score':<15} {'Top-2':<15} {'Top-3':<15}")
    print("-" * 80)
    for obj_key in objectives_to_evaluate:
        if obj_key in results:
            r = results[obj_key]
            obj_name = obj_names.get(obj_key, obj_key.upper())
            print(f"{obj_name:<25} {r['accuracy']*100:>6.2f}%      {r['f1_score']:>6.4f}      {r['top2_accuracy']*100:>6.2f}%      {r['top3_accuracy']*100:>6.2f}%")
    print(f"{'='*80}\n")

    # Visualize each result
    for obj_key in objectives_to_evaluate:
        if obj_key in results:
            print(f"Gerando visualizações para {obj_key.upper()}...")
            visualize_results(results[obj_key], label_encoder, output_dir='../models', objective_key=obj_key)

    # Generate and save individual reports
    all_reports = []
    for obj_key in objectives_to_evaluate:
        if obj_key in results:
            # Create a modified test_df with the appropriate target column
            target_col = objective_to_target[obj_key]
            test_df_with_target = test_df.copy()
            test_df_with_target['best_overall'] = test_df_with_target[target_col]
            
            report_text = generate_report(results[obj_key], label_encoder, test_df_with_target)
            all_reports.append(f"\n\n{'='*80}\n")
            all_reports.append(f"RELATÓRIO PARA {obj_key.upper()}\n")
            all_reports.append(f"{'='*80}\n")
            all_reports.append(report_text)
            
            # Save individual report
            report_file = f'../models/evaluation_report_{obj_key}.txt'
            with open(report_file, 'w') as f:
                f.write(report_text)
            print(f"✓ Saved report: {report_file}")

    # Save combined metrics as JSON
    metrics_json = {}
    for obj_key in objectives_to_evaluate:
        if obj_key in results:
            metrics_json[obj_key] = {
                'accuracy': float(results[obj_key]['accuracy']),
                'f1_score': float(results[obj_key]['f1_score']),
                'top2_accuracy': float(results[obj_key]['top2_accuracy']),
                'top3_accuracy': float(results[obj_key]['top3_accuracy']),
            }

    with open('../models/evaluation_metrics.json', 'w') as f:
        json.dump(metrics_json, f, indent=2)
    print(f"\n✓ Saved metrics JSON: models/evaluation_metrics.json")

    # Print combined summary
    print("\n" + "="*80)
    print("✅ AVALIAÇÃO COMPLETA")
    print("="*80)
    print(f"\nResumo das Acurácias:")
    for obj_key in objectives_to_evaluate:
        if obj_key in results:
            obj_name = obj_names.get(obj_key, obj_key.upper())
            acc = results[obj_key]['accuracy'] * 100
            print(f"  • {obj_name}: {acc:.2f}%")
