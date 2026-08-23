"""
Análise do oráculo guloso: teto de desempenho, distribuição de vencedores,
discordância entre algoritmos e custo computacional.

O resultado principal para o trabalho é a lacuna entre a taxa de aceitação do
melhor algoritmo fixo e a do oráculo guloso, pois essa diferença corresponde
exatamente à margem que a seleção dinâmica é capaz de capturar.

Uso:
    python ccis/analyze_oracle.py
"""

import glob
import json
import os
from collections import defaultdict

import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CCIS_DIR = os.path.join(PROJECT_ROOT, 'ccis')
DATASETS_DIR = os.path.join(CCIS_DIR, 'datasets')
RESULTS_DIR = os.path.join(CCIS_DIR, 'results')
ORACLE_SIM_DIR = os.path.join(RESULTS_DIR, 'simulacoes')
BASELINE_SIM_DIR = os.path.join(PROJECT_ROOT, 'apresentacao', 'simulacoes')


# ---------------------------------------------------------------------- #
# Leitura dos resultados
# ---------------------------------------------------------------------- #

def load_per_vnr_data() -> pd.DataFrame:
    """Carrega e concatena os resultados por requisição de todas as corridas."""
    paths = sorted(glob.glob(os.path.join(DATASETS_DIR, 'oracle_per_vnr-*.csv')))
    if not paths:
        raise FileNotFoundError(
            f'Nenhum arquivo oracle_per_vnr-*.csv em {DATASETS_DIR}. '
            f'Execute ccis/run_oracle_experiments.py antes da análise.')
    frames = []
    for path in paths:
        frame = pd.read_csv(path)
        frame['run_file'] = os.path.basename(path)
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    print(f'Carregados {len(paths)} arquivos, {len(data):,} linhas '
          f'(requisição × algoritmo).')
    return data


def read_summaries(root_dir: str) -> pd.DataFrame:
    """
    Lê os arquivos summary.csv sob um diretório de simulações.

    O campo ``acceptance_rate`` é calculado por ``Counter.summary_records``
    (``virne/core/counter.py``) ao final de cada simulação.
    """
    paths = glob.glob(os.path.join(root_dir, '*', '*', 'summary.csv'))
    rows = []
    for path in paths:
        try:
            frame = pd.read_csv(path)
        except Exception:
            continue
        if frame.empty:
            continue
        record = frame.iloc[-1].to_dict()
        record['solver_name'] = record.get(
            'solver_name', os.path.basename(os.path.dirname(os.path.dirname(path))))
        rows.append(record)
    return pd.DataFrame(rows)


def infer_topology(summaries: pd.DataFrame) -> pd.DataFrame:
    """Deduz a topologia a partir do caminho do conjunto de redes físicas."""
    if summaries.empty or 'p_net_dataset_dir' not in summaries.columns:
        summaries['topology'] = 'unknown'
        return summaries

    def classify(value: str) -> str:
        text = str(value)
        for name in ('fat_tree', 'tree', 'waxman'):
            if name in text:
                return name
        return 'unknown'

    summaries['topology'] = summaries['p_net_dataset_dir'].map(classify)
    return summaries


# ---------------------------------------------------------------------- #
# Análises
# ---------------------------------------------------------------------- #

def acceptance_from_per_vnr(data: pd.DataFrame) -> pd.DataFrame:
    """
    Taxa de aceitação de cada candidato medida sobre os estados visitados pela
    trajetória do oráculo, e a do próprio oráculo.

    Esta medida difere da taxa de uma simulação isolada: aqui todos os
    candidatos são avaliados sobre a mesma trajetória. É a comparação
    causalmente válida, e a única na qual a monotonicidade do teto se sustenta
    por construção.
    """
    rows = []
    for topology, group in data.groupby('topology'):
        num_vnrs = group.groupby(['seed', 'v_net_id']).ngroups
        for algorithm, sub in group.groupby('algorithm'):
            rows.append({
                'topology': topology,
                'algorithm': algorithm,
                'acceptance_rate': sub['result'].mean(),
                'avg_r2c_ratio': sub.loc[sub['result'], 'v_net_r2c_ratio'].mean(),
                'avg_solve_time_ms': sub['solve_time_ms'].mean(),
                'num_vnrs': num_vnrs,
            })
        winners = group.drop_duplicates(subset=['seed', 'v_net_id'])
        rows.append({
            'topology': topology,
            'algorithm': 'GREEDY_ORACLE',
            'acceptance_rate': (winners['num_candidates_accepted'] > 0).mean(),
            'avg_r2c_ratio': group.loc[group['is_winner'] & group['result'],
                                       'v_net_r2c_ratio'].mean(),
            'avg_solve_time_ms': winners['oracle_total_solve_time_ms'].mean(),
            'num_vnrs': num_vnrs,
        })
    return pd.DataFrame(rows).sort_values(
        ['topology', 'acceptance_rate'], ascending=[True, False])


def winner_distribution(data: pd.DataFrame) -> pd.DataFrame:
    """
    Frequência com que cada algoritmo é escolhido pelo oráculo.

    Uma concentração acentuada em um único algoritmo indica que a seleção
    dinâmica tem pouco a ganhar, e esse é por si só um resultado relevante.
    """
    winners = data[data['is_winner']].copy()
    winners.loc[winners['num_candidates_accepted'] == 0, 'algorithm'] = 'none'
    rows = []
    for topology, group in winners.groupby('topology'):
        counts = group['algorithm'].value_counts()
        total = counts.sum()
        for algorithm, count in counts.items():
            rows.append({
                'topology': topology,
                'algorithm': algorithm,
                'num_wins': int(count),
                'share': count / total,
            })
    return pd.DataFrame(rows).sort_values(
        ['topology', 'num_wins'], ascending=[True, False])


def disagreement_rate(data: pd.DataFrame) -> pd.DataFrame:
    """
    Fração de requisições nas quais os candidatos discordam quanto à aceitação.

    Esta fração dimensiona o problema de decisão de fato enfrentado pela árvore:
    fora dela, qualquer escolha produz o mesmo desfecho.
    """
    rows = []
    for topology, group in data.groupby('topology'):
        per_vnr = group.groupby(['seed', 'v_net_id']).agg(
            num_accepted=('result', 'sum'),
            num_candidates=('result', 'size'))
        all_accept = (per_vnr['num_accepted'] == per_vnr['num_candidates']).mean()
        none_accept = (per_vnr['num_accepted'] == 0).mean()
        rows.append({
            'topology': topology,
            'num_vnrs': len(per_vnr),
            'all_accept': all_accept,
            'none_accept': none_accept,
            'disagreement': 1.0 - all_accept - none_accept,
        })
    return pd.DataFrame(rows)


def computational_cost(data: pd.DataFrame) -> pd.DataFrame:
    """Custo de executar todos os candidatos comparado ao custo do vencedor."""
    rows = []
    for topology, group in data.groupby('topology'):
        winners = group[group['is_winner']]
        per_vnr = group.drop_duplicates(subset=['seed', 'v_net_id'])
        total_ms = per_vnr['oracle_total_solve_time_ms'].mean()
        winner_ms = winners['solve_time_ms'].mean()
        rows.append({
            'topology': topology,
            'oracle_total_ms_per_vnr': total_ms,
            'winner_ms_per_vnr': winner_ms,
            'overhead_factor': total_ms / winner_ms if winner_ms else float('nan'),
        })
    return pd.DataFrame(rows)


def baseline_comparison(per_vnr_table: pd.DataFrame) -> pd.DataFrame:
    """
    Tabela principal: melhor algoritmo fixo, oráculo e a lacuna entre ambos.
    """
    rows = []
    for topology, group in per_vnr_table.groupby('topology'):
        oracle = group[group['algorithm'] == 'GREEDY_ORACLE']
        fixed = group[group['algorithm'] != 'GREEDY_ORACLE']
        if oracle.empty or fixed.empty:
            continue
        best_fixed = fixed.loc[fixed['acceptance_rate'].idxmax()]
        oracle_rate = float(oracle.iloc[0]['acceptance_rate'])
        rows.append({
            'topology': topology,
            'best_fixed_algorithm': best_fixed['algorithm'],
            'best_fixed_acceptance': float(best_fixed['acceptance_rate']),
            'oracle_acceptance': oracle_rate,
            'gap_absolute': oracle_rate - float(best_fixed['acceptance_rate']),
            'gap_relative': (oracle_rate / float(best_fixed['acceptance_rate']) - 1.0)
                            if best_fixed['acceptance_rate'] else float('nan'),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------- #
# Apresentação
# ---------------------------------------------------------------------- #

def show(title: str, frame: pd.DataFrame) -> None:
    print(f'\n{"=" * 72}\n{title}\n{"=" * 72}')
    if frame.empty:
        print('(sem dados)')
    else:
        print(frame.to_string(index=False, float_format=lambda v: f'{v:.4f}'))


def main() -> int:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    data = load_per_vnr_data()

    per_vnr_table = acceptance_from_per_vnr(data)
    comparison = baseline_comparison(per_vnr_table)
    winners = winner_distribution(data)
    disagreement = disagreement_rate(data)
    cost = computational_cost(data)

    show('Tabela principal: melhor algoritmo fixo contra o oráculo guloso', comparison)
    show('Desempenho por algoritmo sobre a trajetória do oráculo', per_vnr_table)
    show('Distribuição de vencedores', winners)
    show('Discordância entre os candidatos', disagreement)
    show('Custo computacional do oráculo', cost)

    # Simulações isoladas, quando disponíveis. Servem de contexto, mas não são
    # comparáveis ao teto de forma estrita: cada uma percorreu uma trajetória
    # distinta da rede física.
    isolated = infer_topology(read_summaries(BASELINE_SIM_DIR))
    if not isolated.empty and 'acceptance_rate' in isolated.columns:
        aggregated = (isolated.groupby(['topology', 'solver_name'])['acceptance_rate']
                      .agg(['mean', 'std', 'count']).reset_index()
                      .sort_values(['topology', 'mean'], ascending=[True, False]))
        show('Contexto: simulações isoladas (trajetórias distintas, não comparáveis '
             'diretamente ao teto)', aggregated)

    for name, frame in [('main_comparison', comparison),
                        ('per_algorithm', per_vnr_table),
                        ('winner_distribution', winners),
                        ('disagreement', disagreement),
                        ('computational_cost', cost)]:
        frame.to_csv(os.path.join(RESULTS_DIR, f'oracle_{name}.csv'), index=False)

    summary = {
        'main_comparison': comparison.to_dict(orient='records'),
        'per_algorithm': per_vnr_table.to_dict(orient='records'),
        'winner_distribution': winners.to_dict(orient='records'),
        'disagreement': disagreement.to_dict(orient='records'),
        'computational_cost': cost.to_dict(orient='records'),
    }
    summary_path = os.path.join(RESULTS_DIR, 'oracle_summary.json')
    with open(summary_path, 'w') as handle:
        json.dump(summary, handle, indent=2, default=float)
    print(f'\nResumo gravado em {summary_path}')
    print(f'Tabelas gravadas em {RESULTS_DIR}')

    # Verificação de monotonicidade: por construção, o oráculo não pode perder
    # para nenhum candidato sobre a mesma trajetória.
    violations = comparison[comparison['gap_absolute'] < -1e-9]
    if not violations.empty:
        print('\nATENÇÃO: o teto foi violado, o que indica erro na medição:')
        print(violations.to_string(index=False))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
