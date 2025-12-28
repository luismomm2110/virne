#!/usr/bin/env python3
"""
List all simulation data available in the project
"""

import os
from pathlib import Path
from collections import defaultdict
import pandas as pd

print("="*80)
print("INVENTÁRIO COMPLETO DE DADOS DE SIMULAÇÃO")
print("="*80)

# =============================================================================
# 1. DADOS AGREGADOS (ROOT)
# =============================================================================

print("\n" + "="*80)
print("1. DADOS AGREGADOS (diretório raiz)")
print("="*80)

root_csvs = list(Path('.').glob('*.csv'))
print(f"\nTotal de arquivos CSV no root: {len(root_csvs)}")

for csv_file in sorted(root_csvs):
    size = csv_file.stat().st_size
    size_mb = size / (1024 * 1024)
    
    try:
        df = pd.read_csv(csv_file)
        rows = len(df)
        cols = len(df.columns)
        print(f"\n{csv_file.name}")
        print(f"  Tamanho: {size_mb:.2f} MB")
        print(f"  Dimensões: {rows:,} linhas × {cols} colunas")
        
        # Show first few columns
        col_sample = ', '.join(df.columns[:5].tolist())
        if len(df.columns) > 5:
            col_sample += f", ... ({len(df.columns)-5} mais)"
        print(f"  Colunas: {col_sample}")
    except Exception as e:
        print(f"\n{csv_file.name}")
        print(f"  Tamanho: {size_mb:.2f} MB")
        print(f"  Erro ao ler: {e}")

# =============================================================================
# 2. EXPERIMENTOS POR ALGORITMO
# =============================================================================

print("\n" + "="*80)
print("2. EXPERIMENTOS POR ALGORITMO (virne/)")
print("="*80)

virne_dir = Path('virne')
algorithms = [d for d in virne_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

experiment_summary = defaultdict(lambda: defaultdict(int))
total_experiments = 0

for algo_dir in sorted(algorithms):
    algo_name = algo_dir.name
    
    # Find all experiment directories (contain "seed")
    experiment_dirs = [d for d in algo_dir.iterdir() if d.is_dir() and 'seed' in d.name]
    
    # Count by scenario
    scenarios = defaultdict(int)
    for exp_dir in experiment_dirs:
        # Extract scenario from directory name
        # Example: mip_tree_seed_0 -> tree
        parts = exp_dir.name.replace(f"{algo_name}_", "").rsplit("_seed_", 1)
        if len(parts) == 2:
            scenario = parts[0]
            scenarios[scenario] += 1
            total_experiments += 1
    
    if scenarios:
        print(f"\n{algo_name.upper()}: {len(experiment_dirs)} experimentos")
        for scenario, count in sorted(scenarios.items()):
            print(f"  - {scenario:20s}: {count:2d} runs")
            experiment_summary[scenario][algo_name] = count

# =============================================================================
# 3. MATRIZ CENÁRIO × ALGORITMO
# =============================================================================

print("\n" + "="*80)
print("3. MATRIZ: CENÁRIO × ALGORITMO")
print("="*80)

# Get all scenarios and algorithms
all_scenarios = sorted(set(experiment_summary.keys()))
all_algos = sorted(set(algo for scenario_data in experiment_summary.values() for algo in scenario_data.keys()))

# Print header
print(f"\n{'Cenário':<20}", end='')
for algo in all_algos:
    print(f"{algo:>12}", end='')
print(f"{'Total':>12}")
print("-" * (20 + 12 * (len(all_algos) + 1)))

# Print rows
for scenario in all_scenarios:
    print(f"{scenario:<20}", end='')
    row_total = 0
    for algo in all_algos:
        count = experiment_summary[scenario].get(algo, 0)
        if count > 0:
            print(f"{count:>12}", end='')
            row_total += count
        else:
            print(f"{'—':>12}", end='')
    print(f"{row_total:>12}")

# Print totals
print("-" * (20 + 12 * (len(all_algos) + 1)))
print(f"{'TOTAL':<20}", end='')
for algo in all_algos:
    algo_total = sum(experiment_summary[scenario].get(algo, 0) for scenario in all_scenarios)
    print(f"{algo_total:>12}", end='')
print(f"{total_experiments:>12}")

# =============================================================================
# 4. SUMMARY FILES
# =============================================================================

print("\n" + "="*80)
print("4. ARQUIVOS SUMMARY DISPONÍVEIS")
print("="*80)

summary_files = list(virne_dir.glob('*/*/summary.csv'))
print(f"\nTotal de summary.csv: {len(summary_files)}")

# Group by algorithm
summary_by_algo = defaultdict(list)
for sf in summary_files:
    algo = sf.parent.parent.name
    summary_by_algo[algo].append(sf)

for algo in sorted(summary_by_algo.keys()):
    files = summary_by_algo[algo]
    print(f"\n{algo}: {len(files)} summaries")

# =============================================================================
# 5. RECORDS FILES
# =============================================================================

print("\n" + "="*80)
print("5. ARQUIVOS DE RECORDS (detalhados)")
print("="*80)

records_files = list(virne_dir.glob('*/*/records/*.csv'))
print(f"\nTotal de records/*.csv: {len(records_files)}")

# Sample size
total_records_size = sum(f.stat().st_size for f in records_files)
print(f"Tamanho total: {total_records_size / (1024**3):.2f} GB")

# =============================================================================
# 6. DADOS DO XGBOOST
# =============================================================================

print("\n" + "="*80)
print("6. MODELOS E DADOS DO XGBOOST")
print("="*80)

# Models
models_dir = Path('models')
if models_dir.exists():
    model_files = list(models_dir.glob('*.pkl'))
    print(f"\nModelos treinados: {len(model_files)}")
    for mf in sorted(model_files):
        size_mb = mf.stat().st_size / (1024 * 1024)
        print(f"  - {mf.name}: {size_mb:.2f} MB")
else:
    print("\nDiretório 'models/' não encontrado")

# XGBoost data files
xgb_files = [
    'vnr_aggregated_data.csv',
    'vnr_comparison_dataset.csv',
    'vnr_features.csv',
    'xgboost_predictions.csv',
    'xgboost_vs_fixed_results.csv',
    'xgboost_selector_simulation_results.csv',
    'xgboost_per_vnr_composite.csv',
]

print(f"\nArquivos de dados XGBoost:")
for xf in xgb_files:
    xf_path = Path(xf)
    if xf_path.exists():
        size_mb = xf_path.stat().st_size / (1024 * 1024)
        df = pd.read_csv(xf_path)
        print(f"  ✓ {xf}: {size_mb:.2f} MB ({len(df):,} linhas)")
    else:
        print(f"  ✗ {xf}: Não encontrado")

# =============================================================================
# 7. ANÁLISES E COMPARAÇÕES
# =============================================================================

print("\n" + "="*80)
print("7. ARQUIVOS DE ANÁLISE E COMPARAÇÃO")
print("="*80)

analysis_files = [
    'corrected_algorithm_metrics.csv',
    'statistical_comparison_results.csv',
    'scenario_composite_comparison.csv',
    'publication_table.csv',
]

print(f"\nArquivos de análise:")
for af in analysis_files:
    af_path = Path(af)
    if af_path.exists():
        df = pd.read_csv(af_path)
        print(f"  ✓ {af}: {len(df)} linhas")
    else:
        print(f"  ✗ {af}: Não encontrado")

# =============================================================================
# 8. DOCUMENTAÇÃO
# =============================================================================

print("\n" + "="*80)
print("8. DOCUMENTAÇÃO E RELATÓRIOS")
print("="*80)

md_files = list(Path('.').glob('*.md'))
md_files = [f for f in md_files if f.name not in ['README.md', 'outline.md']]

print(f"\nArquivos Markdown: {len(md_files)}")
for mf in sorted(md_files):
    size_kb = mf.stat().st_size / 1024
    print(f"  - {mf.name}: {size_kb:.1f} KB")

# =============================================================================
# RESUMO FINAL
# =============================================================================

print("\n" + "="*80)
print("RESUMO FINAL")
print("="*80)

print(f"\n📊 Experimentos:")
print(f"   - Total de runs: {total_experiments}")
print(f"   - Algoritmos testados: {len(all_algos)}")
print(f"   - Cenários testados: {len(all_scenarios)}")
print(f"   - Summary files: {len(summary_files)}")
print(f"   - Records files: {len(records_files)} ({total_records_size / (1024**3):.2f} GB)")

print(f"\n📁 Dados agregados:")
print(f"   - CSV files (root): {len(root_csvs)}")

models_count = len(list(models_dir.glob('*.pkl'))) if models_dir.exists() else 0
print(f"\n🤖 XGBoost:")
print(f"   - Modelos treinados: {models_count}")
print(f"   - Datasets: {sum(1 for xf in xgb_files if Path(xf).exists())}/{len(xgb_files)}")

print(f"\n📄 Documentação:")
print(f"   - Relatórios Markdown: {len(md_files)}")

print("\n" + "="*80)

