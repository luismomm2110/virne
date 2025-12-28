#!/usr/bin/env python3
"""
Calculate TRUE Oracle Performance - FAST VERSION.

Para cada VNR em test_clean.csv:
1. Encontra o best_for_rac
2. Busca se aquele algoritmo teve sucesso NAQUELE VNR específico em vnr_features.csv
3. Conta como sucesso se sim, fracasso se não
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

print("=" * 80)
print("CALCULATING TRUE ORACLE PERFORMANCE (FAST VERSION)")
print("=" * 80)

# ============================================================================
# Carregar dados
# ============================================================================

print("\n📂 Loading datasets...")

# Dados brutos: (topology, algorithm, seed, v_net_id, success, v_net_revenue, ...)
all_vnr = pd.read_csv('datasets/vnr_features.csv')
print(f"  ✓ vnr_features.csv: {len(all_vnr)} rows")

# Dados de teste (one row per VNR, com best_for_* labels)
test_clean = pd.read_csv('datasets/vnr_clean.csv')
print(f"  ✓ vnr_clean.csv: {len(test_clean)} rows")

# ============================================================================
# Crear índice rápido: para cada (topology, algorithm, seed, v_net_id),
# armazenar se houve sucesso
# ============================================================================

print("\n🔍 Creating fast lookup index...")

# Para cada (topology, seed, v_net_id, algorithm), encontrar se houve sucesso
# Usar agg para performance
success_by_vnr_algo = all_vnr.groupby(['topology', 'seed', 'v_net_id', 'algorithm'], as_index=False)['success'].any()
success_by_vnr_algo.columns = ['topology', 'seed', 'v_net_id', 'algorithm', 'had_success']

print(f"  ✓ Created index with {len(success_by_vnr_algo)} entries")

# Converter para dicionário para busca O(1)
success_dict = {}
for _, row in success_by_vnr_algo.iterrows():
    key = (row['topology'], row['seed'], row['v_net_id'], row['algorithm'])
    success_dict[key] = row['had_success']

print(f"  ✓ Converted to dict for fast lookup")

# ============================================================================
# Calcular Oracle
# ============================================================================

print("\n🎯 Calculating Oracle Performance...\n")

objectives = ['rac', 'lrc', 'lar', 'ast', 'balanced']
topologies = ['tree', 'fat_tree', 'waxman_16']

oracle_results = {}

for objective in objectives:
    oracle_results[objective] = {}
    best_col = f'best_for_{objective}'

    print(f"{'=' * 70}")
    print(f"OBJECTIVE: {objective.upper()}")
    print(f"{'=' * 70}")

    for topology in topologies:
        # Filtrar test_clean para esta topologia
        topo_test = test_clean[test_clean['topology'] == topology].copy()

        if len(topo_test) == 0:
            print(f"  {topology:12s}: No test data")
            continue

        # Para cada VNR, verificar se o best_for_* teve sucesso
        successes = 0
        matches = 0
        not_found = 0

        # Valores para cálculos de métrica
        oracle_values = []

        for idx, vnr_row in topo_test.iterrows():
            best_algo = vnr_row[best_col]

            if pd.isna(best_algo):
                continue

            # Buscar no índice
            key = (topology, vnr_row['seed'], vnr_row['v_net_id'], best_algo)

            if key in success_dict:
                matches += 1
                had_success = success_dict[key]

                if had_success:
                    successes += 1
                    oracle_values.append(1.0)
                else:
                    oracle_values.append(0.0)

                # Para LRC, LAR, AST, buscar os valores reais
                if objective != 'rac':
                    algo_result = all_vnr[
                        (all_vnr['topology'] == topology) &
                        (all_vnr['seed'] == vnr_row['seed']) &
                        (all_vnr['v_net_id'] == vnr_row['v_net_id']) &
                        (all_vnr['algorithm'] == best_algo) &
                        (all_vnr['success'] == True)  # Apenas os bem-sucedidos
                    ]

                    if len(algo_result) > 0:
                        result_row = algo_result.iloc[0]

                        if objective == 'lrc':
                            if result_row['v_net_cost'] > 0:
                                r2c = result_row['v_net_revenue'] / result_row['v_net_cost']
                                oracle_values[-1] = r2c
                            else:
                                oracle_values[-1] = 0.0

                        elif objective == 'lar':
                            oracle_values[-1] = float(result_row['v_net_revenue'])

                        elif objective == 'ast':
                            oracle_values[-1] = float(result_row['num_interactions'])

                        elif objective == 'balanced':
                            if result_row['success']:
                                oracle_values[-1] = 0.8 * float(result_row['v_net_revenue']) - 0.2 * float(result_row['num_interactions'])
                            else:
                                oracle_values[-1] = 0.0
            else:
                not_found += 1

        # Calcular métrica agregada
        oracle_value = np.mean(oracle_values) if oracle_values else 0

        oracle_results[objective][topology] = {
            'oracle_value': oracle_value,
            'matches_found': matches,
            'not_found': not_found,
            'total_vnrs': len(topo_test),
            'successes': successes if objective == 'rac' else None
        }

        match_pct = (matches / len(topo_test)) * 100 if len(topo_test) > 0 else 0

        print(f"  {topology:12s}:")
        print(f"    Oracle {objective.upper():8s}: {oracle_value:10.2f}")
        if objective == 'rac':
            print(f"    Success rate: {successes}/{matches} ({100*successes/matches if matches > 0 else 0:.1f}%)")
        print(f"    Matches: {matches}/{len(topo_test)} ({match_pct:.1f}%)")
        print(f"    Not found: {not_found}")

# ============================================================================
# Salvar resultados
# ============================================================================

print("\n" + "=" * 70)
print("Saving results...")

output_file = Path(__file__).parent / 'models' / 'oracle_performance_true_final.json'
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
                'total_vnrs': int(data['total_vnrs'])
            }
            if data['successes'] is not None:
                json_data[objective][topology]['successes'] = int(data['successes'])

with open(output_file, 'w') as f:
    json.dump(json_data, f, indent=2)

print(f"✅ Saved: models/oracle_performance_true_final.json")
print("=" * 70)
