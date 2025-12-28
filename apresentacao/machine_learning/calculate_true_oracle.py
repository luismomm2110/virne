#!/usr/bin/env python3
"""
Calculate TRUE Oracle Performance - Opção 2: Para cada VNR em teste,
se SEMPRE escolhêssemos o algoritmo best_for_*, qual seria o desempenho real?

Este script:
1. Carrega vnr_raw_data.csv (dados individuais de cada VNR × Algoritmo)
2. Carrega test.csv (VNRs usados para teste do modelo)
3. Para cada VNR no teste, encontra seu best_for_rac
4. Busca o resultado real daquele (VNR, algoritmo, topologia, seed)
5. Calcula o oráculo verdadeiro: "Se sempre escolhêssemos best_for_rac,
   qual seria nossa taxa de aceitação?"
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

print("=" * 80)
print("CALCULATING TRUE ORACLE PERFORMANCE (Opção 2)")
print("=" * 80)

# ============================================================================
# Passo 1: Carregar dados
# ============================================================================

print("\n📂 Loading datasets...")

# Dados brutos com labels: vnr_features.csv tem tudo (algorithm, topology, seed, v_net_id, best_for_*, success)
features_file = Path(__file__).parent / "datasets" / "vnr_features.csv"
all_vnr_data = pd.read_csv(features_file)
print(f"  ✓ vnr_features.csv: {len(all_vnr_data)} linhas")

# Dados de teste limpo (uma linha por VNR, com best_for_*)
test_clean_file = Path(__file__).parent / "datasets" / "vnr_clean.csv"
test_clean = pd.read_csv(test_clean_file)
print(f"  ✓ vnr_clean.csv: {len(test_clean)} linhas")

# Dados de teste do modelo (split 70/15/15)
test_file = Path(__file__).parent / "datasets" / "test.csv"
test_model = pd.read_csv(test_file)
print(f"  ✓ test.csv (model test set): {len(test_model)} linhas")

# vnr_clean.csv não tem topology_encoded, vou recalcular
# Usar vnr_features.csv para ter o mapping
topo_map = {'tree': 'tree', 'fat_tree': 'fat_tree', 'waxman_16': 'waxman_16'}
test_clean['topology'] = test_clean['topology'].map(topo_map)

# ============================================================================
# Passo 2: Criar índice dos dados brutos para busca rápida
# ============================================================================

print("\n🔍 Indexing VNR features data for fast lookup...")

# Criar chave única para cada combinação
all_vnr_data['_key'] = (
    all_vnr_data['topology'] + '|' +
    all_vnr_data['algorithm'] + '|' +
    all_vnr_data['seed'].astype(str) + '|' +
    all_vnr_data['v_net_id'].astype(str)
)

raw_indexed = {}
for idx, row in all_vnr_data.iterrows():
    key = row['_key']
    if key not in raw_indexed:
        raw_indexed[key] = row

print(f"  ✓ Indexed {len(raw_indexed)} unique (topology, algorithm, seed, v_net_id)")

# ============================================================================
# Passo 3: Calcular Oracle para cada objetivo
# ============================================================================

objectives = ['rac', 'lrc', 'lar', 'ast', 'balanced']
topologies = ['tree', 'fat_tree', 'waxman_16']

print("\n🎯 Calculating Oracle Performance...\n")

oracle_results = {}

for objective in objectives:
    oracle_results[objective] = {}
    best_col = f'best_for_{objective}'

    print(f"{'=' * 70}")
    print(f"OBJECTIVE: {objective.upper()}")
    print(f"{'=' * 70}")

    for topology in topologies:
        # Filtrar dados de teste para esta topologia
        topo_test = test_clean[test_clean['topology'] == topology].copy()

        if len(topo_test) == 0:
            print(f"  {topology:12s}: No test data")
            continue

        # Simular Oracle: para cada VNR no teste, tentar usar best_for_* e contar resultado real
        oracle_results_list = []
        matches = 0
        not_found = 0
        no_best_algo = 0

        for idx, vnr_row in topo_test.iterrows():
            best_algo = vnr_row[best_col]

            # Pular se não tem algoritmo selecionado como best
            if pd.isna(best_algo):
                no_best_algo += 1
                continue

            # Construir chave para buscar nos dados brutos
            # Problema: não sabemos qual seed foi usado para este VNR no teste
            # Solução: tentar todos os seeds (0-4 são os comuns)
            found = False
            for seed in range(0, 10):  # Tentar seeds 0-9
                key = f"{topology}|{best_algo}|{seed}|{int(vnr_row['v_net_id'])}"

                if key in raw_indexed:
                    result = raw_indexed[key]
                    # IMPORTANTE: pegamos apenas a PRIMEIRA linha (idx.item())
                    # Mas há múltiplas tentativas, então precisamos usar ALL linhas com essa chave
                    # e pegar a que finalmente teve sucesso

                    # Buscar TODOS os resultados deste (algo, seed, vnr_id)
                    matching_rows = all_vnr_data[all_vnr_data['_key'] == key]

                    if len(matching_rows) > 0:
                        # Procurar se há alguma tentativa bem-sucedida
                        successful = matching_rows[matching_rows['success'] == True]

                        if len(successful) > 0:
                            # Usar o primeiro sucesso
                            result = successful.iloc[0]
                            oracle_results_list.append({
                                'vnr_id': vnr_row['v_net_id'],
                                'algorithm': best_algo,
                                'success': True,
                                'v_net_revenue': float(result.get('v_net_revenue', 0)),
                                'v_net_cost': float(result.get('v_net_cost', 0)),
                                'num_interactions': float(result.get('num_interactions', 0)),
                            })
                        else:
                            # Nenhuma tentativa foi bem-sucedida
                            oracle_results_list.append({
                                'vnr_id': vnr_row['v_net_id'],
                                'algorithm': best_algo,
                                'success': False,
                                'v_net_revenue': 0.0,
                                'v_net_cost': 0.0,
                                'num_interactions': 0.0,
                            })

                        matches += 1
                        found = True
                        break

            if not found:
                not_found += 1

        # Calcular métrica agregada
        if objective == 'rac':
            # Taxa de aceitação: % de VNRs aceitos
            if oracle_results_list:
                successes = sum(1 for r in oracle_results_list if r['success'])
                oracle_value = (successes / len(oracle_results_list)) * 100
            else:
                oracle_value = 0

        elif objective == 'lrc':
            # Revenue-to-Cost ratio
            valid = [r for r in oracle_results_list if r['v_net_cost'] > 0]
            if valid:
                ratios = [r['v_net_revenue'] / r['v_net_cost'] for r in valid]
                oracle_value = np.mean(ratios)
            else:
                oracle_value = 0

        elif objective == 'lar':
            # Long-term Average Revenue
            if oracle_results_list:
                revenues = [r['v_net_revenue'] for r in oracle_results_list]
                oracle_value = np.mean(revenues) if revenues else 0
            else:
                oracle_value = 0

        elif objective == 'ast':
            # Average Solving Time
            if oracle_results_list:
                times = [r['num_interactions'] for r in oracle_results_list]
                oracle_value = np.mean(times) if times else 0
            else:
                oracle_value = 0

        elif objective == 'balanced':
            # Composite: 0.8*revenue - 0.2*time (only for accepted)
            accepted = [r for r in oracle_results_list if r['success']]
            if accepted:
                scores = [0.8 * r['v_net_revenue'] - 0.2 * r['num_interactions'] for r in accepted]
                oracle_value = np.mean(scores)
            else:
                oracle_value = 0

        oracle_results[objective][topology] = {
            'oracle_value': oracle_value,
            'matches_found': matches,
            'not_found': not_found,
            'no_best_algo': no_best_algo,
            'total_vnrs': len(topo_test)
        }

        match_pct = (matches / len(topo_test)) * 100 if len(topo_test) > 0 else 0

        print(f"  {topology:12s}:")
        print(f"    Oracle {objective.upper():8s}: {oracle_value:10.2f}")
        print(f"    Matches found: {matches}/{len(topo_test)} ({match_pct:.1f}%)")
        print(f"    Not found: {not_found}")
        print(f"    No best algo: {no_best_algo}")

# ============================================================================
# Passo 4: Comparação com Modelo
# ============================================================================

print("\n" + "=" * 70)
print("ORACLE vs MODEL COMPARISON")
print("=" * 70)

# Carregar model results
model_results_file = Path(__file__).parent / "models" / "ranking_results_per_topology.json"
with open(model_results_file) as f:
    model_results = json.load(f)

for objective in objectives:
    print(f"\n{objective.upper()}:")
    for topology in topologies:
        if topology in oracle_results[objective]:
            oracle_data = oracle_results[objective][topology]
            oracle_val = oracle_data['oracle_value']

            # Obter model accuracy
            topo_model = topology if topology != 'waxman_16' else 'waxman_16'
            if topo_model in model_results and objective in model_results[topo_model]:
                model_acc = model_results[topo_model][objective]['classification'] * 100
                model_top3 = model_results[topo_model][objective]['top3_ranking'] * 100
            else:
                model_acc = 0
                model_top3 = 0

            print(f"  {topology:12s}: Oracle={oracle_val:8.2f}  |  Model={model_top3:6.1f}%")

# ============================================================================
# Passo 5: Salvar resultados
# ============================================================================

print("\n" + "=" * 70)
print("Saving results...")

output_file = Path(__file__).parent / 'models' / 'oracle_performance_true_v2.json'
output_file.parent.mkdir(exist_ok=True)

json_data = {}
for objective in objectives:
    json_data[objective] = {}
    for topology in topologies:
        if topology in oracle_results[objective]:
            data = oracle_results[objective][topology]
            json_data[objective][topology] = {
                'oracle_value': float(data['oracle_value']),
                'matches_found': int(data['matches_found']),
                'not_found': int(data['not_found']),
                'no_best_algo': int(data['no_best_algo']),
                'total_vnrs': int(data['total_vnrs'])
            }

with open(output_file, 'w') as f:
    json.dump(json_data, f, indent=2)

print(f"✅ Saved: models/oracle_performance_true_v2.json")
print("=" * 70)
