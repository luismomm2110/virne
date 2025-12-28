#!/usr/bin/env python3
"""
Calculate Best Single Algorithm Baseline vs Decision Tree Comparison

This script:
1. Uses TEST SET only (no data leakage)
2. Identifies best single algorithm for each objective
3. Calculates baseline accuracy (when best algo was correct)
4. Compares against tree top-3 ranking accuracy
5. Generates comparison report
"""

import pandas as pd
import numpy as np
import pickle
import json
from sklearn.preprocessing import LabelEncoder

def main():
    print("="*100)
    print("BEST SINGLE ALGORITHM BASELINE vs DECISION TREE COMPARISON")
    print("="*100)

    # Load TEST data only
    test_df = pd.read_csv('datasets/test_enhanced.csv')
    print(f"\nTest set size: {len(test_df)} samples")

    # Load the trained models
    with open('models/decision_trees_per_topology.pkl', 'rb') as f:
        models = pickle.load(f)

    # Load current results to get tree accuracies
    with open('models/ranking_results_per_topology.json', 'r') as f:
        tree_results = json.load(f)

    # Define objectives
    objectives = ['rac', 'lrc', 'lar', 'ast', 'balanced']
    topology_names = ['tree', 'fat_tree', 'waxman_16']

    # Store comparison results
    comparison_results = {}

    print("\n" + "="*100)
    print("BEST SINGLE ALGORITHM BASELINE IDENTIFICATION (from TEST SET)")
    print("="*100)

    baselines = {}
    for obj in objectives:
        col_name = f'best_for_{obj}'
        algo_counts = test_df[col_name].value_counts()
        best_algo = algo_counts.idxmax()
        count = algo_counts.max()
        baseline_accuracy = count / len(test_df)

        baselines[obj] = {
            'algorithm': best_algo,
            'count': int(count),
            'accuracy': baseline_accuracy
        }

        print(f"\n{obj.upper()}:")
        print(f"  Best Algorithm: {best_algo}")
        print(f"  Baseline Accuracy: {baseline_accuracy*100:.2f}% ({count}/{len(test_df)})")

    # Now compare against tree accuracies
    print("\n" + "="*100)
    print("COMPARISON: DECISION TREE vs BEST SINGLE ALGORITHM BASELINE")
    print("="*100)

    comparison_data = []

    for obj in objectives:
        print(f"\n{obj.upper()}:")
        print("-" * 80)

        baseline_algo = baselines[obj]['algorithm']
        baseline_acc = baselines[obj]['accuracy']

        # Collect tree accuracies across topologies
        tree_accs = []
        for topo_name in topology_names:
            if topo_name in tree_results and obj in tree_results[topo_name]:
                tree_acc = tree_results[topo_name][obj]['top3_ranking']
                tree_accs.append(tree_acc)

        # Average tree accuracy across topologies
        avg_tree_acc = np.mean(tree_accs) if tree_accs else 0

        # Calculate improvement
        improvement = (avg_tree_acc - baseline_acc) * 100
        improvement_pp = improvement  # percentage points
        improvement_relative = (avg_tree_acc / baseline_acc - 1) * 100 if baseline_acc > 0 else 0

        comparison_data.append({
            'objective': obj.upper(),
            'baseline_algorithm': baseline_algo,
            'baseline_accuracy': baseline_acc * 100,
            'tree_accuracy': avg_tree_acc * 100,
            'improvement_pp': improvement_pp,
            'improvement_relative': improvement_relative,
            'tree_better': avg_tree_acc > baseline_acc
        })

        print(f"  Baseline Algorithm: {baseline_algo}")
        print(f"  Baseline Accuracy: {baseline_acc*100:.2f}%")
        print(f"  ")
        print(f"  Decision Tree (Top-3 Ranking):")
        for topo_name in topology_names:
            if topo_name in tree_results and obj in tree_results[topo_name]:
                tree_acc = tree_results[topo_name][obj]['top3_ranking']
                print(f"    {topo_name}: {tree_acc*100:.2f}%")
        print(f"    Average: {avg_tree_acc*100:.2f}%")
        print(f"  ")
        print(f"  Improvement:")
        print(f"    Absolute: +{improvement_pp:.2f} percentage points")
        print(f"    Relative: +{improvement_relative:.2f}%")
        print(f"    Tree better: {'YES' if avg_tree_acc > baseline_acc else 'NO'}")

    # Summary table
    print("\n" + "="*100)
    print("SUMMARY TABLE")
    print("="*100)

    summary_df = pd.DataFrame(comparison_data)
    print("\n" + summary_df.to_string(index=False))

    # Save results
    with open('models/baseline_comparison.json', 'w') as f:
        comparison_dict = {row['objective']: {
            'baseline_algorithm': row['baseline_algorithm'],
            'baseline_accuracy': round(row['baseline_accuracy'], 2),
            'tree_accuracy': round(row['tree_accuracy'], 2),
            'improvement_pp': round(row['improvement_pp'], 2),
            'improvement_relative': round(row['improvement_relative'], 2),
            'tree_better': row['tree_better']
        } for _, row in summary_df.iterrows()}
        json.dump(comparison_dict, f, indent=2)

    # Save summary table as CSV
    summary_df.to_csv('models/baseline_comparison_summary.csv', index=False)

    print("\n✓ Results saved to:")
    print("  - models/baseline_comparison.json")
    print("  - models/baseline_comparison_summary.csv")

    # Overall statistics
    print("\n" + "="*100)
    print("OVERALL STATISTICS")
    print("="*100)

    avg_baseline = summary_df['baseline_accuracy'].mean()
    avg_tree = summary_df['tree_accuracy'].mean()
    avg_improvement = summary_df['improvement_pp'].mean()
    tree_wins = summary_df['tree_better'].sum()

    print(f"\nAverage Baseline Accuracy: {avg_baseline:.2f}%")
    print(f"Average Tree Accuracy: {avg_tree:.2f}%")
    print(f"Average Improvement: +{avg_improvement:.2f} percentage points")
    print(f"Tree better in: {tree_wins}/{len(summary_df)} objectives")

    print("\n" + "="*100)

if __name__ == "__main__":
    main()