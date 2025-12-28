#!/usr/bin/env python3
"""
Script para validar dados de simulação antes de treinar XGBoost
Verifica se todas as informações necessárias estão presentes e completas
"""

import pandas as pd
import sys
from pathlib import Path


def validate_simulation_data(filepath='vnr_aggregated_data.csv'):
    """
    Valida se os dados de simulação estão completos para treinar XGBoost

    Args:
        filepath: Caminho para o arquivo CSV de dados agregados

    Returns:
        bool: True se dados válidos, False caso contrário
    """
    print("="*70)
    print("VALIDAÇÃO DE DADOS PARA TREINAMENTO XGBOOST")
    print("="*70)

    # 1. Verificar se arquivo existe
    if not Path(filepath).exists():
        print(f"\n❌ ERRO: Arquivo não encontrado: {filepath}")
        return False

    print(f"\n✓ Arquivo encontrado: {filepath}")

    # 2. Carregar dados
    try:
        df = pd.read_csv(filepath)
        print(f"✓ Dados carregados: {len(df):,} registros")
    except Exception as e:
        print(f"\n❌ ERRO ao carregar arquivo: {e}")
        return False

    # 3. Verificar colunas obrigatórias
    required_columns = {
        'Features da VNR': [
            'v_net_num_nodes',
            'v_net_num_egdes',
            'v_net_demand',
            'v_net_node_demand',
            'v_net_link_demand',
            'v_net_lifetime',
            'v_net_arrival_time',
        ],
        'Features da Rede Física': [
            'p_net_available_resource',
            'p_net_node_available_resource',
            'p_net_link_available_resource',
            'p_net_node_resource_utilization',
            'p_net_link_resource_utilization',
            'inservice_count',
        ],
        'Resultados': [
            'algorithm',
            'result',
            'solving_time',
            'v_net_r2c_ratio',
        ],
        'Identificadores': [
            'v_net_id',
            'seed',
            'event_time',
            'event_type',
        ]
    }

    print("\n" + "="*70)
    print("VERIFICANDO COLUNAS OBRIGATÓRIAS")
    print("="*70)

    all_columns_ok = True
    for category, columns in required_columns.items():
        print(f"\n{category}:")
        for col in columns:
            if col in df.columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ❌ {col} - FALTANDO!")
                all_columns_ok = False

    if not all_columns_ok:
        print("\n❌ ERRO: Colunas obrigatórias faltando!")
        return False

    # 4. Filtrar apenas eventos de chegada
    df = df[df['event_type'] == 1].copy()
    print(f"\n✓ Filtrado para event_type=1: {len(df):,} registros")

    # 5. Verificar algoritmos
    print("\n" + "="*70)
    print("VERIFICANDO ALGORITMOS")
    print("="*70)

    expected_algorithms = ['ga_meta', 'mip', 'mcts', 'sa_meta',
                          'pl_rank', 'rw_rank_bfs', 'd_round', 'r_round']

    found_algorithms = df['algorithm'].unique()
    print(f"\nAlgoritmos encontrados: {len(found_algorithms)}")

    for algo in expected_algorithms:
        if algo in found_algorithms:
            count = len(df[df['algorithm'] == algo])
            print(f"  ✓ {algo:15s}: {count:,} registros")
        else:
            print(f"  ⚠ {algo:15s}: NÃO ENCONTRADO")

    # 6. Verificar dados faltantes (NaN)
    print("\n" + "="*70)
    print("VERIFICANDO DADOS FALTANTES (NaN)")
    print("="*70)

    critical_columns = [
        'v_net_num_nodes', 'v_net_num_egdes', 'v_net_demand',
        'p_net_available_resource', 'result', 'algorithm'
    ]

    has_critical_nan = False
    print("\nColunas críticas (não podem ter NaN):")
    for col in critical_columns:
        nan_count = df[col].isna().sum()
        nan_pct = nan_count / len(df) * 100
        if nan_count > 0:
            print(f"  ❌ {col:40s}: {nan_count:6d} NaN ({nan_pct:5.1f}%)")
            has_critical_nan = True
        else:
            print(f"  ✓ {col:40s}: 0 NaN")

    if has_critical_nan:
        print("\n❌ ERRO: Colunas críticas têm valores faltantes!")
        return False

    # 7. Verificar solving_time (importante mas pode ter NaN)
    print("\nColuna solving_time (pode ter alguns NaN):")
    print(f"  Algoritmo       | Total  | Aceitas | NaN    | %NaN")
    print("  " + "-"*60)

    for algo in sorted(df['algorithm'].unique()):
        algo_df = df[df['algorithm'] == algo]
        accepted = algo_df[algo_df['result'] == True]

        nan_count = accepted['solving_time'].isna().sum()
        total_accepted = len(accepted)
        nan_pct = (nan_count / total_accepted * 100) if total_accepted > 0 else 0

        status = "⚠" if nan_pct > 50 else "✓"
        print(f"  {status} {algo:15s} | {len(algo_df):6d} | {total_accepted:7d} | {nan_count:6d} | {nan_pct:5.1f}%")

    # 8. Verificar estrutura de VNRs
    print("\n" + "="*70)
    print("VERIFICANDO ESTRUTURA DE VNRs")
    print("="*70)

    df['vnr_uid'] = (
        df['v_net_id'].astype(str) + '_' +
        df['seed'].astype(str) + '_' +
        df['event_time'].astype(int).astype(str)
    )

    vnr_algo_counts = df.groupby('vnr_uid')['algorithm'].nunique()

    print(f"\nTotal de VNRs únicas: {len(vnr_algo_counts):,}")
    print(f"\nDistribuição de algoritmos por VNR:")

    for n_algos in sorted(vnr_algo_counts.unique()):
        count = (vnr_algo_counts == n_algos).sum()
        pct = count / len(vnr_algo_counts) * 100
        status = "✓" if n_algos == 8 else "⚠"
        print(f"  {status} {n_algos} algoritmos: {count:,} VNRs ({pct:.1f}%)")

    # VNRs completas (8 algoritmos)
    complete_vnrs = vnr_algo_counts[vnr_algo_counts == 8]
    print(f"\n✓ VNRs completas (8 algoritmos): {len(complete_vnrs):,}")

    if len(complete_vnrs) < 100:
        print(f"  ⚠ AVISO: Poucas VNRs completas. Recomendado: >500")

    # 9. Verificar seeds
    print("\n" + "="*70)
    print("VERIFICANDO SEEDS")
    print("="*70)

    seeds = sorted(df['seed'].unique())
    print(f"\nSeeds encontrados: {seeds}")
    print(f"Total de seeds: {len(seeds)}")

    if len(seeds) < 3:
        print(f"  ⚠ AVISO: Poucos seeds. Recomendado: ≥5 para robustez estatística")
    else:
        print(f"  ✓ Seeds suficientes para análise estatística")

    # 10. Resumo final
    print("\n" + "="*70)
    print("RESUMO FINAL")
    print("="*70)

    print(f"\n✓ Total de registros: {len(df):,}")
    print(f"✓ VNRs únicas: {len(vnr_algo_counts):,}")
    print(f"✓ VNRs completas (8 algoritmos): {len(complete_vnrs):,}")
    print(f"✓ Algoritmos: {len(found_algorithms)}")
    print(f"✓ Seeds: {len(seeds)}")

    recommendations = []

    if len(complete_vnrs) < 500:
        recommendations.append("- Execute mais simulações para ter >500 VNRs completas")

    if len(seeds) < 5:
        recommendations.append("- Use mais seeds (recomendado: 5) para robustez estatística")

    # Verificar algoritmos com muito NaN
    high_nan_algos = []
    for algo in df['algorithm'].unique():
        algo_df = df[df['algorithm'] == algo]
        accepted = algo_df[algo_df['result'] == True]
        nan_pct = accepted['solving_time'].isna().sum() / len(accepted) * 100 if len(accepted) > 0 else 0
        if nan_pct > 50:
            high_nan_algos.append(algo)

    if high_nan_algos:
        recommendations.append(f"- Verificar por que estes algoritmos não registram tempo: {', '.join(high_nan_algos)}")

    if recommendations:
        print(f"\n⚠ RECOMENDAÇÕES:")
        for rec in recommendations:
            print(f"  {rec}")
    else:
        print(f"\n✅ DADOS PRONTOS PARA TREINAMENTO!")

    print("\n" + "="*70)

    return True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Validar dados de simulação')
    parser.add_argument(
        '--data-file',
        type=str,
        default='vnr_aggregated_data.csv',
        help='Caminho para arquivo CSV de dados'
    )

    args = parser.parse_args()

    is_valid = validate_simulation_data(args.data_file)

    sys.exit(0 if is_valid else 1)
