#!/usr/bin/env python3
"""
Simple evaluation: Compare XGBoost selector predictions with actual best algorithms.
"""

import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    """Main evaluation function."""

    # Load model
    print("Loading trained model...")
    with open('models/xgb_best_overall_model.pkl', 'rb') as f:
        model = pickle.load(f)

    with open('models/xgb_best_overall_model_label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)

    print(f"Model loaded. Classes: {label_encoder.classes_}\n")

    # Load test data
    test_df = pd.read_csv('datasets/test.csv')
    print(f"Test set: {len(test_df)} VNRs")

    # Define features (must match training)
    feature_cols = [
        'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
        'v_net_demand_per_node', 'v_net_demand_per_link', 'v_net_connectivity',
        'v_net_total_demand', 'v_net_node_to_link_demand_ratio', 'v_net_lifetime',
        'p_net_available_resource', 'p_net_node_util', 'p_net_link_util',
        'p_net_overall_util', 'inservice_count', 'system_load',
        'num_running_p_net_nodes', 'solving_time', 'topology_encoded'
    ]

    # Prepare data
    X_test = test_df[feature_cols]
    y_test = test_df['best_overall']

    # Predict
    y_pred_encoded = model.predict(X_test)
    y_pred = label_encoder.inverse_transform(y_pred_encoded)

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    print("="*80)
    print("XGBOOST DYNAMIC SELECTOR - TEST SET EVALUATION")
    print("="*80)
    print(f"\nOverall Metrics:")
    print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  F1-Score (weighted): {f1:.4f}")

    print(f"\n\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred, labels=label_encoder.classes_)
    print(f"\n\nConfusion Matrix:")
    print(f"{'':15} " + " ".join([f"{c:>12}" for c in label_encoder.classes_]))
    for i, row_label in enumerate(label_encoder.classes_):
        print(f"{row_label:15} " + " ".join([f"{cm[i,j]:>12}" for j in range(len(label_encoder.classes_))]))

    # Per-algorithm analysis
    print(f"\n\n{'='*80}")
    print("PER-ALGORITHM ANALYSIS")
    print(f"{'='*80}")

    results_by_algo = []
    for algo in label_encoder.classes_:
        true_count = (y_test == algo).sum()
        pred_count = (y_pred == algo).sum()
        correct = ((y_test == algo) & (y_pred == algo)).sum()

        if true_count > 0:
            recall = correct / true_count
        else:
            recall = 0

        if pred_count > 0:
            precision = correct / pred_count
        else:
            precision = 0

        results_by_algo.append({
            'Algorithm': algo,
            'True Count': true_count,
            'Predicted Count': pred_count,
            'Correct': correct,
            'Recall': recall,
            'Precision': precision
        })

    results_df = pd.DataFrame(results_by_algo)
    print(results_df.to_string(index=False))

    # Simulate acceptance rate improvement
    print(f"\n\n{'='*80}")
    print("SIMULATED PERFORMANCE COMPARISON")
    print(f"{'='*80}")

    # Load original full dataset to get actual performance
    full_df = pd.read_csv('datasets/vnr_features.csv')

    # For each VNR in test set, compare:
    # 1. What XGBoost selected
    # 2. What was actually best
    # 3. Success rate if we had used a fixed algorithm

    # Get test VNR IDs
    test_vnr_ids = test_df[['topology', 'seed', 'v_net_id']].values

    comparison_results = []

    for i, (topo, seed, vnr_id) in enumerate(test_vnr_ids):
        # Get all algorithm runs for this VNR
        vnr_runs = full_df[(full_df['topology'] == topo) &
                            (full_df['seed'] == seed) &
                            (full_df['v_net_id'] == vnr_id)]

        if len(vnr_runs) == 0:
            continue

        # XGBoost prediction
        xgb_algo = y_pred[i]
        true_best = y_test.iloc[i]

        # Get success for XGBoost choice
        xgb_run = vnr_runs[vnr_runs['algorithm'] == xgb_algo]
        xgb_success = xgb_run['success'].iloc[0] if len(xgb_run) > 0 else False
        xgb_time = xgb_run['solving_time'].iloc[0] if len(xgb_run) > 0 else 999

        # Get success for true best
        best_run = vnr_runs[vnr_runs['algorithm'] == true_best]
        best_success = best_run['success'].iloc[0] if len(best_run) > 0 else False
        best_time = best_run['solving_time'].iloc[0] if len(best_run) > 0 else 999

        comparison_results.append({
            'vnr_id': vnr_id,
            'xgb_algo': xgb_algo,
            'true_best': true_best,
            'correct_prediction': xgb_algo == true_best,
            'xgb_success': xgb_success,
            'best_success': best_success,
            'xgb_time': xgb_time,
            'best_time': best_time
        })

    comp_df = pd.DataFrame(comparison_results)

    print(f"\nXGBoost Dynamic Selector Results:")
    print(f"  Acceptance Rate: {comp_df['xgb_success'].mean():.2%}")
    print(f"  Average Solving Time: {comp_df['xgb_time'].mean():.4f}s")
    print(f"  Correct Algorithm Selection: {comp_df['correct_prediction'].mean():.2%}")

    print(f"\nOracle (Always Best) Results:")
    print(f"  Acceptance Rate: {comp_df['best_success'].mean():.2%}")
    print(f"  Average Solving Time: {comp_df['best_time'].mean():.4f}s")

    print(f"\nRegret vs Oracle:")
    print(f"  Acceptance Gap: {(comp_df['best_success'].mean() - comp_df['xgb_success'].mean())*100:.2f}%")
    print(f"  Time Overhead: {(comp_df['xgb_time'].mean() - comp_df['best_time'].mean()):.4f}s")

    # Compare with fixed algorithms
    print(f"\n\n{'='*80}")
    print("COMPARISON WITH FIXED ALGORITHM BASELINES")
    print(f"{'='*80}")

    baseline_results = []
    for algo in ['d_round', 'rw_rank_bfs', 'pl_rank', 'sa_meta', 'ga_meta', 'mip']:
        algo_results = []
        for i, (topo, seed, vnr_id) in enumerate(test_vnr_ids):
            vnr_runs = full_df[(full_df['topology'] == topo) &
                                (full_df['seed'] == seed) &
                                (full_df['v_net_id'] == vnr_id)]

            algo_run = vnr_runs[vnr_runs['algorithm'] == algo]
            if len(algo_run) > 0:
                success = algo_run['success'].iloc[0]
                time = algo_run['solving_time'].iloc[0]
                algo_results.append({'success': success, 'time': time})

        if len(algo_results) > 0:
            df_algo = pd.DataFrame(algo_results)
            baseline_results.append({
                'Algorithm': algo,
                'Acceptance Rate': f"{df_algo['success'].mean():.2%}",
                'Avg Time (s)': f"{df_algo['time'].mean():.4f}",
                'VNRs Tested': len(algo_results)
            })

    baseline_df = pd.DataFrame(baseline_results)

    # Add XGBoost row
    xgb_row = pd.DataFrame([{
        'Algorithm': 'XGBoost Dynamic',
        'Acceptance Rate': f"{comp_df['xgb_success'].mean():.2%}",
        'Avg Time (s)': f"{comp_df['xgb_time'].mean():.4f}",
        'VNRs Tested': len(comp_df)
    }])

    oracle_row = pd.DataFrame([{
        'Algorithm': 'Oracle (Best)',
        'Acceptance Rate': f"{comp_df['best_success'].mean():.2%}",
        'Avg Time (s)': f"{comp_df['best_time'].mean():.4f}",
        'VNRs Tested': len(comp_df)
    }])

    final_comparison = pd.concat([baseline_df, xgb_row, oracle_row], ignore_index=True)
    print(f"\n{final_comparison.to_string(index=False)}")

    print(f"\n{'='*80}")
    print("EVALUATION COMPLETE")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()