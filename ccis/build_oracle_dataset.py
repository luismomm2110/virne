"""
Construção do conjunto de treino a partir dos resultados do oráculo guloso.

Produz dois arquivos em ``ccis/datasets``:

``oracle_long.csv``
    Formato longo, uma linha por requisição e candidato. Preserva o desfecho de
    todos os algoritmos e serve para análises de ordenação e para funções de
    custo alternativas.

``oracle_dataset.csv``
    Formato largo, uma linha por requisição, com as características do estado e
    o rótulo ``best_algorithm``. É a entrada direta de um classificador.

A diferença essencial em relação à rotulagem de
``apresentacao/machine_learning/pipeline/2_prepare_dataset.py`` é a validade
causal: naquele arquivo os candidatos são comparados a partir de simulações
independentes, cujos estados da rede física divergem após a primeira aceitação;
aqui todos disputam exatamente o mesmo estado.

Uso:
    python ccis/build_oracle_dataset.py
"""

import glob
import os

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(PROJECT_ROOT, 'ccis', 'datasets')

# Características do estado, idênticas para todos os candidatos de uma mesma
# requisição. Somente estas podem alimentar o classificador, pois somente estas
# são observáveis no instante da decisão.
STATE_COLUMNS = [
    'topology', 'seed', 'v_net_id', 'event_time',
    'v_net_num_nodes', 'v_net_num_links', 'v_net_lifetime',
    'v_net_node_demand', 'v_net_link_demand', 'v_net_total_demand',
    'v_net_connectivity', 'v_net_avg_degree',
    'v_net_max_node_demand', 'v_net_max_link_demand',
    'p_net_node_available', 'p_net_link_available',
    'p_net_node_util', 'p_net_link_util',
    'p_net_min_node_available', 'p_net_min_link_available',
    'inservice_count',
]


def load_long_format() -> pd.DataFrame:
    """Concatena os resultados de todas as corridas no formato longo."""
    paths = sorted(glob.glob(os.path.join(DATASETS_DIR, 'oracle_per_vnr-*.csv')))
    if not paths:
        raise FileNotFoundError(
            f'Nenhum arquivo oracle_per_vnr-*.csv em {DATASETS_DIR}. '
            f'Execute ccis/run_oracle_experiments.py antes desta etapa.')
    data = pd.concat([pd.read_csv(path) for path in paths], ignore_index=True)
    print(f'{len(paths)} arquivos, {len(data):,} linhas no formato longo.')
    return data


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    """
    Deriva características a partir do estado observável.

    Cada uma delas é uma razão entre grandezas já presentes, escolhida por
    expressar a pressão exercida pela requisição sobre os recursos ainda
    disponíveis. Nenhuma constante empírica é empregada, ao contrário da
    engenharia de características da pipeline anterior.
    """
    result = frame.copy()

    def safe_divide(numerator, denominator):
        return np.where(np.abs(denominator) > 1e-12, numerator / denominator, 0.0)

    result['node_demand_pressure'] = safe_divide(
        result['v_net_node_demand'], result['p_net_node_available'])
    result['link_demand_pressure'] = safe_divide(
        result['v_net_link_demand'], result['p_net_link_available'])
    result['node_bottleneck_pressure'] = safe_divide(
        result['v_net_max_node_demand'], result['p_net_min_node_available'])
    result['link_bottleneck_pressure'] = safe_divide(
        result['v_net_max_link_demand'], result['p_net_min_link_available'])
    result['node_to_link_demand_ratio'] = safe_divide(
        result['v_net_node_demand'], result['v_net_link_demand'])
    result['demand_per_node'] = safe_divide(
        result['v_net_node_demand'], result['v_net_num_nodes'])
    result['demand_per_link'] = safe_divide(
        result['v_net_link_demand'], result['v_net_num_links'])
    result['utilization_imbalance'] = result['p_net_node_util'] - result['p_net_link_util']
    result['request_complexity'] = result['v_net_num_nodes'] * result['v_net_connectivity']
    result['topology_encoded'] = pd.Categorical(result['topology']).codes
    return result


def build_wide_format(long_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Reduz o formato longo a uma linha por requisição, com o rótulo do vencedor.

    Também são anexadas colunas ``accepted_<algoritmo>``, que permitem avaliar
    um seletor por sua consequência (aceitou ou não) e não apenas pela
    coincidência com o rótulo. Um seletor pode discordar do rótulo e ainda
    assim obter a aceitação, quando vários candidatos aceitam a requisição.
    """
    key = ['topology', 'seed', 'v_net_id']
    available_state = [c for c in STATE_COLUMNS if c in long_frame.columns]
    wide = long_frame.groupby(key, as_index=False)[available_state].first()

    winners = long_frame[long_frame['is_winner']].copy()
    winners.loc[winners['num_candidates_accepted'] == 0, 'algorithm'] = 'none'
    label = winners.groupby(key, as_index=False).agg(
        best_algorithm=('algorithm', 'first'),
        best_r2c_ratio=('v_net_r2c_ratio', 'first'),
        best_solve_time_ms=('solve_time_ms', 'first'))
    wide = wide.merge(label, on=key, how='left')

    counts = long_frame.groupby(key, as_index=False).agg(
        num_candidates_accepted=('result', 'sum'),
        num_candidates=('result', 'size'),
        oracle_total_solve_time_ms=('oracle_total_solve_time_ms', 'first'))
    wide = wide.merge(counts, on=key, how='left')
    wide['any_accepted'] = wide['num_candidates_accepted'] > 0
    # Verdadeiro quando a escolha importa: parte dos candidatos aceita e parte
    # rejeita a mesma requisição.
    wide['is_decisive'] = ((wide['num_candidates_accepted'] > 0) &
                           (wide['num_candidates_accepted'] < wide['num_candidates']))

    # Além do desfecho, registram-se o tempo de execução e a razão entre
    # receita e custo de cada candidato. Nenhuma dessas colunas é observável no
    # instante da decisão, e portanto nenhuma delas pode servir de variável
    # preditora; todas se destinam à avaliação das escolhas do seletor,
    # inclusive quanto ao custo computacional incorrido.
    for algorithm, group in long_frame.groupby('algorithm'):
        per_algorithm = group.groupby(key, as_index=False).agg(
            **{f'accepted_{algorithm}': ('result', 'first'),
               f'time_{algorithm}': ('solve_time_ms', 'first'),
               f'r2c_{algorithm}': ('v_net_r2c_ratio', 'first')})
        wide = wide.merge(per_algorithm, on=key, how='left')

    return engineer_features(wide)


def main() -> int:
    long_frame = load_long_format()
    long_path = os.path.join(DATASETS_DIR, 'oracle_long.csv')
    long_frame.to_csv(long_path, index=False)

    wide_frame = build_wide_format(long_frame)
    wide_path = os.path.join(DATASETS_DIR, 'oracle_dataset.csv')
    wide_frame.to_csv(wide_path, index=False)

    print(f'\nFormato longo: {long_path}  ({len(long_frame):,} linhas)')
    print(f'Formato largo: {wide_path}  ({len(wide_frame):,} requisições)')
    print(f'\nRequisições decisivas (a escolha altera o desfecho): '
          f'{wide_frame["is_decisive"].mean():.1%}')
    print('\nDistribuição do rótulo best_algorithm:')
    print(wide_frame['best_algorithm'].value_counts().to_string())
    print('\nPor topologia:')
    print(pd.crosstab(wide_frame['topology'], wide_frame['best_algorithm']).to_string())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
