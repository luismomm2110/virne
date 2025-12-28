#!/usr/bin/env python3
"""
Visualize Model vs Oracle vs Individual Algorithms - CORRETO v2

Oráculo = MÉDIA de TODOS os algoritmos marcados como best_for_*
(porque best_for_* é ambíguo quando múltiplos algoritmos têm mesmo resultado)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import json

# Load evaluation metrics (model performance)
ranking_results = Path(__file__).parent / "models" / "ranking_results_per_topology.json"
with open(ranking_results) as f:
    model_results = json.load(f)

# Load algorithm metrics
metrics_file = Path(__file__).parent / "models" / "algorithm_metrics.csv"
algorithm_df = pd.read_csv(metrics_file)

# Load test data
test_file = Path(__file__).parent / "datasets" / "test_enhanced.csv"
test_data = pd.read_csv(test_file)

# Define objectives
objectives = ['rac', 'lrc', 'lar', 'ast', 'balanced']
objective_labels = {
    'rac': 'Taxa de Aceitação (RAC) %',
    'lrc': 'Razão Receita-para-Custo (LRC)',
    'lar': 'Receita Média (LAR)',
    'ast': 'Tempo Médio (AST) segundos',
    'balanced': 'Objetivo Balanceado'
}

topologies = ['tree', 'fat_tree', 'waxman_16']
topology_mapping = {'tree': 'Tree', 'fat_tree': 'Fat-Tree', 'waxman_16': 'Waxman-16'}
topology_to_id = {'tree': 0, 'fat_tree': 1, 'waxman_16': 2}

# Color mapping for algorithms
algorithm_colors = {
    'mip': '#D84A51',
    'sa_meta': '#F5A962',
    'd_round': '#4472C4',
    'ga_meta': '#C4A0E1',
    'rw_rank_bfs': '#70AD47',
    'pl_rank': '#3FA9A5',
    'mcts': '#FFC000',
    'pso_meta': '#5B9BD5'
}

algorithm_order = ['mip', 'pl_rank', 'ga_meta', 'mcts', 'rw_rank_bfs', 'sa_meta', 'd_round', 'pso_meta']

print("📊 Calculando Oráculo CORRETO (média de TODOS best_for_*)...\n")

# Calculate oracle and model performance
results = {}

for objective in objectives:
    results[objective] = {}
    oracle_col = f'best_for_{objective}'

    for topo_name in topologies:
        topo_id = topology_to_id[topo_name]
        topo_data = test_data[test_data['topology_encoded'] == topo_id].copy()

        if len(topo_data) == 0:
            continue

        # ORÁCULO CORRETO: Para cada VNR, usa o algoritmo best_for_* e conta seu performance
        # Simula: "Se SEMPRE escolhéssemos o best_for_rac, qual seria nossa taxa de aceitação?"

        oracle_values = []
        best_algos_counts = {}

        for idx, row in topo_data.iterrows():
            best_algo = row[oracle_col]

            if pd.isna(best_algo):
                continue

            if best_algo not in best_algos_counts:
                best_algos_counts[best_algo] = 0
            best_algos_counts[best_algo] += 1

            # Procura a performance MÉDIA deste algoritmo nesta topologia
            # Interpretação: Se este algoritmo foi selecionado para este VNR,
            # sua taxa de sucesso é igual à taxa média deste algoritmo nesta topologia
            algo_data = algorithm_df[
                (algorithm_df['algorithm'] == best_algo) &
                (algorithm_df['topology'] == topo_name)
            ]

            if len(algo_data) > 0:
                metric_value = algo_data[objective].values[0]
                oracle_values.append(metric_value)
            else:
                # Se o algoritmo não foi testado nesta topologia, assume fracasso
                if objective == 'rac':
                    oracle_values.append(0.0)

        oracle_value = np.mean(oracle_values) if oracle_values else 0

        # DEBUG: Print distribution of best_for_* algorithms
        if topo_name == topologies[0]:  # Only print for first topology to avoid spam
            print(f"    {objective.upper()} - {topology_mapping[topo_name]}: best_for_* distribution:")
            for algo, count in best_algos_counts.items():
                pct = (count / len(topo_data)) * 100
                print(f"      {algo:15s}: {count:3d} VNRs ({pct:5.1f}%)")

        # Get model performance
        if topo_name in model_results:
            if objective in model_results[topo_name]:
                model_accuracy_top3 = model_results[topo_name][objective]['top3_ranking'] * 100
                model_accuracy_top1 = model_results[topo_name][objective]['classification'] * 100
            else:
                model_accuracy_top3 = 0
                model_accuracy_top1 = 0
        else:
            model_accuracy_top3 = 0
            model_accuracy_top1 = 0

        # Get individual algorithm performance
        algo_perfs = {}
        for algo in algorithm_order:
            algo_data = algorithm_df[
                (algorithm_df['algorithm'] == algo) &
                (algorithm_df['topology'] == topo_name)
            ]

            if len(algo_data) > 0:
                algo_perfs[algo] = algo_data[objective].values[0]
            else:
                algo_perfs[algo] = 0

        results[objective][topo_name] = {
            'oracle': oracle_value,
            'model_top3': model_accuracy_top3,
            'model_top1': model_accuracy_top1,
            'algorithms': algo_perfs,
            'best_algos_counts': best_algos_counts,
            'n_samples': len(topo_data)
        }

        print(f"{objective.upper()} - {topology_mapping[topo_name]:10s}: Oracle={oracle_value:.1f}, Model={model_accuracy_top3:.1f}%")

print("\n✅ Oráculo calculado\n")

# Create consolidated comparison figure
print("📈 Criando gráfico consolidado...\n")

fig, axes = plt.subplots(5, 1, figsize=(16, 20))

for ax_idx, objective in enumerate(objectives):
    ax = axes[ax_idx]

    # Calculate averages across topologies
    oracle_avg = 0
    model_top3_avg = 0
    algo_avgs = {algo: 0 for algo in algorithm_order}
    count = 0

    for topo_name in topologies:
        if topo_name in results[objective]:
            data = results[objective][topo_name]
            oracle_avg += data['oracle']
            model_top3_avg += data['model_top3']
            for algo in algorithm_order:
                algo_avgs[algo] += data['algorithms'].get(algo, 0)
            count += 1

    if count > 0:
        oracle_avg /= count
        model_top3_avg /= count
        for algo in algorithm_order:
            algo_avgs[algo] /= count

    # Sort algorithms by performance
    algo_sorted = sorted(algorithm_order, key=lambda x: algo_avgs[x], reverse=True)

    # Prepare data for plotting
    labels = ['Modelo\n(Top-3)', 'Oráculo'] + algo_sorted
    values = [model_top3_avg, oracle_avg] + [algo_avgs[algo] for algo in algo_sorted]

    # Colors
    colors = ['#3498db', '#27ae60'] + [algorithm_colors[algo] for algo in algo_sorted]

    # Create bar chart
    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.2)

    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{val:.1f}',
               ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel('Score/Métrica', fontsize=12, fontweight='bold')
    ax.set_title(f'{objective_labels[objective]}', fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

plt.suptitle('Modelo Top-3 vs Oráculo (média dos best_for_*) vs Algoritmos Individuais',
             fontsize=16, fontweight='bold', y=0.998)
plt.tight_layout()

output_dir = Path(__file__).parent / 'graficos'
output_dir.mkdir(exist_ok=True)
output_file = output_dir / 'model_oracle_algorithms_consolidated.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✅ Saved: graficos/model_oracle_algorithms_consolidated.png")
plt.close()

# Create per-topology figures
print("📊 Criando gráficos por topologia...\n")

for topo_name in topologies:
    fig, axes = plt.subplots(5, 1, figsize=(14, 18))

    for ax_idx, objective in enumerate(objectives):
        ax = axes[ax_idx]

        if topo_name not in results[objective]:
            continue

        data = results[objective][topo_name]

        # Sort algorithms
        algo_sorted = sorted(algorithm_order, key=lambda x: data['algorithms'].get(x, 0), reverse=True)

        # Prepare data
        labels = ['Modelo\n(Top-3)', 'Oráculo'] + algo_sorted
        values = [data['model_top3'], data['oracle']] + [data['algorithms'][algo] for algo in algo_sorted]

        # Colors
        colors = ['#3498db', '#27ae60'] + [algorithm_colors[algo] for algo in algo_sorted]

        # Create bar chart
        x = np.arange(len(labels))
        bars = ax.bar(x, values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.2)

        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax.set_ylabel('Score/Métrica', fontsize=11, fontweight='bold')
        ax.set_title(f'{objective_labels[objective]}', fontsize=12, fontweight='bold', pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

    plt.suptitle(f'Topologia {topology_mapping[topo_name]}: Modelo vs Oráculo vs Algoritmos',
                 fontsize=15, fontweight='bold', y=0.998)
    plt.tight_layout()

    output_file = output_dir / f'model_oracle_algorithms_{topo_name}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: graficos/model_oracle_algorithms_{topo_name}.png")
    plt.close()

# Print summary
print("\n" + "="*80)
print("📊 RESUMO - MODELO vs ORÁCULO vs ALGORITMOS (CORRIGIDO)")
print("="*80)

for objective in objectives:
    oracle_avg = 0
    model_top3_avg = 0
    count = 0

    for topo_name in topologies:
        if topo_name in results[objective]:
            data = results[objective][topo_name]
            oracle_avg += data['oracle']
            model_top3_avg += data['model_top3']
            count += 1

    if count > 0:
        oracle_avg /= count
        model_top3_avg /= count

    print(f"\n{objective.upper()} ({objective_labels[objective]}):")
    print(f"  Oráculo (média best_for_*):      {oracle_avg:6.1f}")
    print(f"  Modelo Top-3 (acurácia):        {model_top3_avg:6.1f}%")

print("\n" + "="*80)
print("✅ Visualizations complete!")
print("="*80)
