#!/usr/bin/env python3
"""
Step 6: Compare dynamic selector with fixed algorithm baselines.

Runs multiple simulations with different seeds and generates comparative analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os


def load_all_results(results_dir='results'):
    """Load all simulation results."""

    results = []

    # Dynamic selector results
    for seed in range(5):
        file_path = f'{results_dir}/online_sim_dynamic_seed_{seed}.csv'
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            results.append({
                'method': 'Dynamic',
                'seed': seed,
                'acceptance_rate': df['success'].mean(),
                'avg_time_per_vnr': df['solving_time'].mean(),
                'total_time': df['solving_time'].sum(),
                'num_accepted': df['success'].sum()
            })

    # Fixed algorithm baselines
    algorithms = ['ga_meta', 'mip', 'mcts', 'sa_meta', 'pl_rank', 'rw_rank_bfs', 'd_round']

    for algo in algorithms:
        for seed in range(5):
            file_path = f'{results_dir}/online_sim_{algo}_seed_{seed}.csv'
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                results.append({
                    'method': algo.replace('_', '-').upper(),
                    'seed': seed,
                    'acceptance_rate': df['success'].mean(),
                    'avg_time_per_vnr': df['solving_time'].mean(),
                    'total_time': df['solving_time'].sum(),
                    'num_accepted': df['success'].sum()
                })

    return pd.DataFrame(results)


def compute_statistics(df):
    """Compute mean and std for each method."""

    stats = df.groupby('method').agg({
        'acceptance_rate': ['mean', 'std'],
        'avg_time_per_vnr': ['mean', 'std'],
        'total_time': ['mean', 'std'],
        'num_accepted': ['mean', 'std']
    }).round(4)

    return stats


def create_comparison_boxplots(df, output_dir='results'):
    """Create boxplots comparing all methods."""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Sort methods for consistent display
    method_order = sorted(df['method'].unique())
    if 'Dynamic' in method_order:
        # Put Dynamic first
        method_order.remove('Dynamic')
        method_order = ['Dynamic'] + method_order

    # Boxplot 1: Acceptance Rate
    sns.boxplot(data=df, x='method', y='acceptance_rate',
                order=method_order, ax=ax1, palette='Set3')
    ax1.set_title('Acceptance Rate Comparison', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Method', fontsize=12)
    ax1.set_ylabel('Acceptance Rate', fontsize=12)
    ax1.set_ylim([0, 1.0])
    ax1.grid(True, alpha=0.3, axis='y')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Highlight Dynamic
    if 'Dynamic' in df['method'].values:
        dynamic_pos = method_order.index('Dynamic')
        ax1.patches[dynamic_pos].set_facecolor('gold')
        ax1.patches[dynamic_pos].set_edgecolor('red')
        ax1.patches[dynamic_pos].set_linewidth(2)

    # Boxplot 2: Average Time per VNR
    sns.boxplot(data=df, x='method', y='avg_time_per_vnr',
                order=method_order, ax=ax2, palette='Set3')
    ax2.set_title('Average Time per VNR Comparison', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Method', fontsize=12)
    ax2.set_ylabel('Avg Time per VNR (seconds)', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Use log scale if needed
    time_range = df['avg_time_per_vnr'].max() / df['avg_time_per_vnr'].min()
    if time_range > 100:
        ax2.set_yscale('log')
        ax2.set_ylabel('Avg Time per VNR (seconds, log scale)', fontsize=12)

    # Highlight Dynamic
    if 'Dynamic' in df['method'].values:
        ax2.patches[dynamic_pos].set_facecolor('gold')
        ax2.patches[dynamic_pos].set_edgecolor('red')
        ax2.patches[dynamic_pos].set_linewidth(2)

    plt.tight_layout()

    output_path = f'{output_dir}/comparison_boxplots.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Comparison boxplots saved: {output_path}")
    plt.close()


def create_scatter_plot(df, output_dir='results'):
    """Create scatter plot: Acceptance Rate vs Time."""

    # Compute means per method
    means = df.groupby('method').agg({
        'acceptance_rate': 'mean',
        'avg_time_per_vnr': 'mean'
    }).reset_index()

    plt.figure(figsize=(10, 8))

    # Scatter points
    for idx, row in means.iterrows():
        color = 'red' if row['method'] == 'Dynamic' else 'blue'
        marker = 'D' if row['method'] == 'Dynamic' else 'o'
        size = 200 if row['method'] == 'Dynamic' else 100

        plt.scatter(row['avg_time_per_vnr'], row['acceptance_rate'],
                   c=color, marker=marker, s=size, alpha=0.7,
                   edgecolors='black', linewidths=1.5)

        # Annotate
        plt.annotate(row['method'],
                    (row['avg_time_per_vnr'], row['acceptance_rate']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=9, fontweight='bold' if row['method'] == 'Dynamic' else 'normal')

    plt.xlabel('Average Time per VNR (seconds)', fontsize=12)
    plt.ylabel('Acceptance Rate', fontsize=12)
    plt.title('Acceptance Rate vs Time Trade-off', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output_path = f'{output_dir}/acceptance_vs_time_scatter.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Scatter plot saved: {output_path}")
    plt.close()


def compute_regret_vs_oracle(df):
    """
    Compute regret: how far is Dynamic from the Oracle (best possible)?

    Oracle = for each seed, take the best acceptance rate and best time
             achieved by any method.
    """

    regret_results = []

    for seed in df['seed'].unique():
        seed_data = df[df['seed'] == seed]

        # Oracle values (best possible)
        oracle_acceptance = seed_data['acceptance_rate'].max()
        oracle_time = seed_data['avg_time_per_vnr'].min()

        # Dynamic values
        dynamic_row = seed_data[seed_data['method'] == 'Dynamic']
        if len(dynamic_row) > 0:
            dynamic_acceptance = dynamic_row['acceptance_rate'].values[0]
            dynamic_time = dynamic_row['avg_time_per_vnr'].values[0]

            # Regret
            acceptance_regret = oracle_acceptance - dynamic_acceptance
            time_regret = dynamic_time - oracle_time

            regret_results.append({
                'seed': seed,
                'oracle_acceptance': oracle_acceptance,
                'dynamic_acceptance': dynamic_acceptance,
                'acceptance_regret': acceptance_regret,
                'oracle_time': oracle_time,
                'dynamic_time': dynamic_time,
                'time_regret': time_regret
            })

    regret_df = pd.DataFrame(regret_results)

    print("\n" + "="*80)
    print("REGRET ANALYSIS (vs Oracle)")
    print("="*80)
    print(regret_df)
    print(f"\nMean Acceptance Regret: {regret_df['acceptance_regret'].mean():.4f}")
    print(f"Mean Time Regret: {regret_df['time_regret'].mean():.4f}s")

    return regret_df


def create_summary_table(stats_df, output_dir='results'):
    """Create and save summary statistics table."""

    output_path = f'{output_dir}/comparison_summary.csv'
    stats_df.to_csv(output_path)
    print(f"\n✓ Summary table saved: {output_path}")

    # Print to console
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(stats_df)


def run_statistical_tests(df):
    """Run statistical significance tests."""

    from scipy import stats

    print("\n" + "="*80)
    print("STATISTICAL TESTS")
    print("="*80)

    # Get Dynamic results
    dynamic = df[df['method'] == 'Dynamic']

    if len(dynamic) == 0:
        print("No Dynamic results found!")
        return

    # Compare Dynamic with each baseline
    baselines = df[df['method'] != 'Dynamic']['method'].unique()

    for baseline in baselines:
        baseline_data = df[df['method'] == baseline]

        # T-test for acceptance rate
        t_stat_acc, p_val_acc = stats.ttest_ind(
            dynamic['acceptance_rate'],
            baseline_data['acceptance_rate']
        )

        # T-test for time
        t_stat_time, p_val_time = stats.ttest_ind(
            dynamic['avg_time_per_vnr'],
            baseline_data['avg_time_per_vnr']
        )

        print(f"\nDynamic vs {baseline}:")
        print(f"  Acceptance Rate: t={t_stat_acc:.3f}, p={p_val_acc:.4f} "
              f"{'***' if p_val_acc < 0.001 else '**' if p_val_acc < 0.01 else '*' if p_val_acc < 0.05 else 'ns'}")
        print(f"  Avg Time:        t={t_stat_time:.3f}, p={p_val_time:.4f} "
              f"{'***' if p_val_time < 0.001 else '**' if p_val_time < 0.01 else '*' if p_val_time < 0.05 else 'ns'}")


def main():
    """Main comparison pipeline."""

    print("="*80)
    print("BASELINE COMPARISON ANALYSIS")
    print("="*80)

    # Load results
    print("\n1. Loading simulation results...")
    df = load_all_results()

    if len(df) == 0:
        print("ERROR: No results found!")
        print("Please run simulations first using 5_online_simulator.py")
        return

    print(f"  Loaded {len(df)} simulation runs")
    print(f"  Methods: {df['method'].unique()}")
    print(f"  Seeds: {sorted(df['seed'].unique())}")

    # Compute statistics
    print("\n2. Computing statistics...")
    stats_df = compute_statistics(df)
    create_summary_table(stats_df)

    # Create visualizations
    print("\n3. Creating visualizations...")
    create_comparison_boxplots(df)
    create_scatter_plot(df)

    # Regret analysis
    print("\n4. Computing regret vs Oracle...")
    regret_df = compute_regret_vs_oracle(df)

    # Statistical tests
    print("\n5. Running statistical tests...")
    run_statistical_tests(df)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nGenerated files:")
    print("  - results/comparison_boxplots.png")
    print("  - results/acceptance_vs_time_scatter.png")
    print("  - results/comparison_summary.csv")


def adaptive_ranking_evaluation(val_df, trees, label_encoder, feature_cols, threshold=0.10):
    """
    Evaluate models with adaptive ranking.

    Strategy:
    - Use classification when confident (high difference between top-1 and top-2)
    - Use ranking when uncertain (low difference = desprezível)

    Args:
        val_df: Validation dataframe
        trees: Dictionary of trained decision trees
        label_encoder: Label encoder for algorithms
        feature_cols: List of feature columns
        threshold: Confidence threshold (default 10%)
                   If (prob_top1 - prob_top2) / prob_top1 > threshold
                   → Use classification (strict)
                   else → Use ranking (top-3)
    """

    print("\n" + "="*90)
    print("ADAPTIVE RANKING EVALUATION")
    print("="*90)
    print(f"Strategy: Use classification when confident (diff > {threshold:.0%})")
    print(f"          Use ranking when uncertain (diff <= {threshold:.0%})")

    # Prepare validation data
    X_val = val_df[feature_cols].fillna(val_df[feature_cols].mean())

    objectives = ['rac', 'lrc', 'lar', 'ast', 'balanced']
    results = {}

    for obj in objectives:
        # Get data for this objective
        y_true = val_df[f'best_for_{obj}'].dropna().values
        valid_mask = val_df[f'best_for_{obj}'].notna().values
        X_data = X_val[valid_mask]

        if len(y_true) == 0:
            continue

        # Get model
        tree = trees[obj]

        # Predictions and probabilities
        y_pred = tree.predict(X_data)
        y_proba = tree.predict_proba(X_data)
        y_true_encoded = label_encoder.transform(y_true)

        # Classification accuracy (strict)
        classification_acc = (y_pred == y_true_encoded).mean()

        # Top-3 ranking accuracy (pragmatic)
        top_k_pred = np.argsort(-y_proba, axis=1)
        top3_acc = sum(y_true_encoded[i] in top_k_pred[i, :3]
                      for i in range(len(y_true_encoded))) / len(y_true_encoded)

        # Adaptive evaluation
        adaptive_correct = 0
        classification_used = 0
        ranking_used = 0
        confidences = []

        for i in range(len(y_true)):
            # Top-2 probabilities
            top2_probs = np.sort(y_proba[i])[-2:][::-1]
            prob_top1 = top2_probs[0]
            prob_top2 = top2_probs[1]

            # Confidence score
            confidence = (prob_top1 - prob_top2) / prob_top1 if prob_top1 > 0 else 0
            confidences.append(confidence)

            # Adaptive decision
            if confidence >= threshold:
                # High confidence: use classification
                if y_true_encoded[i] == y_pred[i]:
                    adaptive_correct += 1
                classification_used += 1
            else:
                # Low confidence: use ranking (top-3)
                if y_true_encoded[i] in top_k_pred[i, :3]:
                    adaptive_correct += 1
                ranking_used += 1

        adaptive_acc = adaptive_correct / len(y_true)

        results[obj] = {
            'classification_accuracy': classification_acc,
            'top3_accuracy': top3_acc,
            'adaptive_accuracy': adaptive_acc,
            'classification_used': classification_used,
            'ranking_used': ranking_used,
            'avg_confidence': np.mean(confidences),
            'confidence_std': np.std(confidences)
        }

        # Print results
        print(f"\n{obj.upper()}:")
        print(f"  Samples: {len(y_true)}")
        print(f"  Classification (strict):    {classification_acc:.1%}")
        print(f"  Top-3 Ranking (pragmatic):  {top3_acc:.1%}")
        print(f"  Adaptive (hybrid):          {adaptive_acc:.1%}")
        print(f"  Strategy used:")
        print(f"    - Classification: {classification_used} ({classification_used/len(y_true):.0%})")
        print(f"    - Ranking: {ranking_used} ({ranking_used/len(y_true):.0%})")
        print(f"  Confidence: {np.mean(confidences):.1%} ± {np.std(confidences):.1%}")

    # Summary table
    print("\n" + "="*90)
    print("SUMMARY TABLE")
    print("="*90)
    print("\n┌────────────┬──────────────┬──────────────┬──────────────┐")
    print("│ Objective  │ Classification│ Top-3 Ranking│ Adaptive   │")
    print("├────────────┼──────────────┼──────────────┼──────────────┤")

    for obj in objectives:
        if obj in results:
            m = results[obj]
            print(f"│ {obj:10s} │ {m['classification_accuracy']:12.1%} │ {m['top3_accuracy']:12.1%} │ {m['adaptive_accuracy']:12.1%} │")

    print("└────────────┴──────────────┴──────────────┴──────────────┘")

    print("\nKEY INSIGHT:")
    print("  • Classification: Rigoroso, exige acertar exatamente qual é o 1º")
    print("  • Top-3 Ranking: Pragmático, aceita estar entre os 3 melhores")
    print("  • Adaptive: Combina os dois - rigoroso quando apropriado, pragmático quando necessário")
    print("  • Sem gerar novos dados, sem treinar novos modelos!")

    return results


if __name__ == '__main__':
    main()

    # ADAPTIVE RANKING EVALUATION (NEW)
    print("\n" + "="*90)
    print("RUNNING ADAPTIVE RANKING EVALUATION")
    print("="*90)

    # Load trained models for adaptive evaluation
    import pickle

    try:
        with open('models/decision_trees.pkl', 'rb') as f:
            trees = pickle.load(f)

        with open('models/algorithm_label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)

        # Load validation data (using enhanced dataset with 10 new features)
        val_df = pd.read_csv('datasets/val_enhanced.csv')

        # Feature columns (35 features: 25 original + 10 new)
        feature_cols = [
            # VNR characteristics
            'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
            'v_net_demand_per_node', 'v_net_demand_per_link', 'v_net_connectivity',
            'v_net_total_demand', 'v_net_node_to_link_demand_ratio', 'v_net_lifetime',
            # Physical network state
            'p_net_available_resource', 'p_net_node_util', 'p_net_link_util', 'p_net_overall_util',
            # System state
            'inservice_count', 'system_load', 'num_running_p_net_nodes',
            # Topology
            'topology_encoded',
            # Original engineered features
            'network_stress_index', 'problem_complexity', 'resource_bottleneck_ratio',
            'vnr_size_category', 'cpu_intensive_flag', 'bandwidth_intensive_flag',
            'utilization_pressure', 'resource_efficiency',
            # NEW: Heterogeneidade de Recursos (3 features)
            'p_net_node_link_resource_ratio', 'p_net_util_imbalance', 'p_net_resource_heterogeneity',
            # NEW: Fragmentação e Saúde (3 features)
            'p_net_fragmentation_estimate', 'p_net_uneven_utilization', 'p_net_health_score',
            # NEW: Características VNR (4 features)
            'vnr_node_link_demand_ratio', 'vnr_demand_intensity', 'vnr_structural_complexity', 'vnr_density_adjusted'
        ]

        # Run adaptive ranking evaluation
        adaptive_results = adaptive_ranking_evaluation(val_df, trees, label_encoder, feature_cols, threshold=0.10)

        # Save results
        import json

        results_serializable = {}
        for obj, metrics in adaptive_results.items():
            results_serializable[obj] = {
                k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                for k, v in metrics.items()
            }

        with open('models/adaptive_ranking_results.json', 'w') as f:
            json.dump(results_serializable, f, indent=2)

        print("\n✓ Adaptive ranking results saved to models/adaptive_ranking_results.json")

    except FileNotFoundError as e:
        print(f"\nNote: Could not load trained models for adaptive evaluation: {e}")
        print("Run 3_train_decision_trees.py first to train the models")
