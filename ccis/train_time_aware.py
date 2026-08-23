"""
Seleção de algoritmos sensível ao custo computacional.

Os experimentos anteriores mediram apenas a taxa de aceitação e concluíram que
o ``mip`` constitui adversário difícil de superar, pois isoladamente já alcança
cerca de noventa e cinco por cento do teto. Aquela comparação, contudo, ignora
uma diferença de escala considerável: o ``mip`` consome em média 1892 ms por
requisição, ao passo que o ``pl_rank`` consome 7,7 ms e o ``rw_rank_bfs``
apenas 2,4 ms, ou seja, cerca de setecentas vezes menos.

O presente experimento incorpora essa dimensão. A seleção deixa de perseguir
exclusivamente a aceitação e passa a ponderá-la contra o tempo despendido,
mediante a utilidade

    utilidade(a) = P(a aceita | estado) - lambda * tempo_medio(a) / tempo_maximo

na qual ``lambda`` exprime quantos pontos de probabilidade de aceitação se
admite sacrificar em troca da economia integral do tempo do candidato mais
oneroso. Com ``lambda`` nulo recupera-se o seletor puramente orientado à
aceitação; à medida que ``lambda`` cresce, os candidatos velozes tornam-se
progressivamente preferíveis.

O tempo médio de cada candidato é estimado sobre o conjunto de treino e
constitui informação legítima: o custo típico de um algoritmo é conhecido de
antemão, ao contrário do tempo que ele consumirá na requisição específica.

A varredura de ``lambda`` produz a fronteira de Pareto entre aceitação e tempo,
da qual se extrai o resultado de interesse prático: a configuração que preserva
a taxa de aceitação do ``mip`` com uma fração do seu custo.

Uso:
    python ccis/train_time_aware.py
"""

import json
import os
import pickle
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ccis.train_cost_sensitive import (  # noqa: E402
    BinaryReductionSelector, CANDIDATE_DEPTHS, MIN_SAMPLES_LEAF,
    acceptance_of_choice, algorithm_names, select_features, split_by_seed,
)

DATASET_PATH = os.path.join(PROJECT_ROOT, 'ccis', 'datasets', 'oracle_dataset.csv')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'ccis', 'results')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'ccis', 'models')

# Valores de lambda percorridos. A escala é logarítmica porque os tempos dos
# candidatos diferem em três ordens de grandeza.
LAMBDAS = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0]


# ---------------------------------------------------------------------- #
# Custo das escolhas
# ---------------------------------------------------------------------- #

def time_of_choice(frame: pd.DataFrame, choices) -> float:
    """
    Tempo médio efetivamente despendido pelas escolhas, em milissegundos.

    Consulta-se a coluna ``time_<algoritmo>`` correspondente ao candidato
    escolhido, de modo que o custo apurado seja o realmente incorrido, e não o
    custo médio daquele candidato.
    """
    spent = np.zeros(len(frame), dtype=float)
    choices = np.asarray(choices)
    for algorithm in np.unique(choices):
        column = f'time_{algorithm}'
        if column not in frame.columns:
            continue
        mask = choices == algorithm
        spent[mask] = frame.loc[mask, column].to_numpy(dtype=float)
    return float(spent.mean())


def mean_times(frame: pd.DataFrame, algorithms) -> np.ndarray:
    """Tempo médio de cada candidato, estimado sobre o conjunto de treino."""
    return np.array([frame[f'time_{a}'].mean() for a in algorithms])


# ---------------------------------------------------------------------- #
# Seletor sensível ao tempo
# ---------------------------------------------------------------------- #

class TimeAwareSelector:
    """
    Seletor que pondera a probabilidade de aceitação contra o custo temporal.

    Apoia-se nas probabilidades estimadas pela redução binária e subtrai delas
    uma penalidade proporcional ao tempo médio de cada candidato.
    """

    def __init__(self, binary_selector, algorithms, train_mean_times, lam: float):
        self.binary = binary_selector
        self.algorithms = np.asarray(algorithms)
        # A normalização pelo maior tempo torna lambda comparável entre
        # topologias, cujos custos absolutos diferem.
        self.normalized_times = train_mean_times / max(train_mean_times.max(), 1e-9)
        self.lam = lam

    def predict(self, frame, features):
        probabilities = self.binary.predict_proba_matrix(frame, features)
        utility = probabilities - self.lam * self.normalized_times
        return self.algorithms[utility.argmax(axis=1)]


def tune_binary(train, val, features, algorithms, random_state: int = 42):
    """Ajusta a redução binária pela aceitação alcançada na validação."""
    best_model, best_score, best_config = None, -1.0, None
    for depth in CANDIDATE_DEPTHS:
        for leaf in MIN_SAMPLES_LEAF:
            selector = BinaryReductionSelector(
                algorithms, max_depth=depth, min_samples_leaf=leaf,
                random_state=random_state).fit(train, features)
            score = acceptance_of_choice(val, selector.predict(val, features))
            if score > best_score:
                best_model, best_score, best_config = selector, score, (depth, leaf)
    return best_model, best_config, best_score


# ---------------------------------------------------------------------- #
# Fronteira e referências
# ---------------------------------------------------------------------- #

def pareto_frontier(frame: pd.DataFrame) -> pd.DataFrame:
    """
    Assinala as configurações não dominadas.

    Uma configuração é dominada quando outra alcança aceitação igual ou
    superior consumindo tempo igual ou inferior, com vantagem estrita em ao
    menos um dos dois critérios.
    """
    marks = []
    for _, row in frame.iterrows():
        dominated = (
            (frame['acceptance'] >= row['acceptance']) &
            (frame['time_ms'] <= row['time_ms']) &
            ((frame['acceptance'] > row['acceptance']) |
             (frame['time_ms'] < row['time_ms']))
        ).any()
        marks.append(not dominated)
    result = frame.copy()
    result['pareto_optimal'] = marks
    return result


def run_for_subset(data: pd.DataFrame, features: list, scope: str) -> dict:
    """Percorre a varredura de lambda sobre um recorte do conjunto."""
    train, val, test = split_by_seed(data)
    algorithms = algorithm_names(data)
    train_times = mean_times(train, algorithms)

    print(f'\n{"=" * 82}\nESCOPO: {scope}\n{"=" * 82}')
    binary, config, val_score = tune_binary(train, val, features, algorithms)
    print(f'Redução binária: profundidade {config[0]}, folha mínima {config[1]}, '
          f'aceitação na validação {val_score:.4f}')

    print(f'\nTempo médio por candidato no treino (ms):')
    for algorithm, value in sorted(zip(algorithms, train_times), key=lambda p: p[1]):
        print(f'  {algorithm:<14}{value:>10.1f}')

    # Referências: cada candidato isolado e o teto do oráculo.
    reference_rows = []
    for algorithm in algorithms:
        choices = np.full(len(test), algorithm)
        reference_rows.append({
            'strategy': f'fixo: {algorithm}',
            'acceptance': acceptance_of_choice(test, choices),
            'time_ms': time_of_choice(test, choices),
        })
    oracle_time = float(sum(test[f'time_{a}'].mean() for a in algorithms))
    reference_rows.append({
        'strategy': 'ORÁCULO GULOSO (teto)',
        'acceptance': float(test['any_accepted'].mean()),
        'time_ms': oracle_time,
    })
    references = pd.DataFrame(reference_rows)

    # Varredura de lambda.
    sweep_rows = []
    for lam in LAMBDAS:
        selector = TimeAwareSelector(binary, algorithms, train_times, lam)
        choices = selector.predict(test, features)
        distribution = pd.Series(choices).value_counts(normalize=True)
        sweep_rows.append({
            'strategy': f'seletor (lambda={lam})',
            'lambda': lam,
            'acceptance': acceptance_of_choice(test, choices),
            'time_ms': time_of_choice(test, choices),
            'share_mip': float(distribution.get('mip', 0.0)),
            'top_choice': distribution.index[0],
        })
    sweep = pareto_frontier(pd.DataFrame(sweep_rows))

    print(f'\nVarredura de lambda sobre o conjunto de teste (semente 4):')
    print(sweep[['lambda', 'acceptance', 'time_ms', 'share_mip', 'top_choice',
                 'pareto_optimal']]
          .to_string(index=False, float_format=lambda v: f'{v:.4f}'))

    print(f'\nReferências:')
    print(references.sort_values('acceptance', ascending=False)
          .to_string(index=False, float_format=lambda v: f'{v:.4f}'))

    # Resultado de interesse prático: preservar a aceitação do melhor candidato
    # isolado consumindo o menor tempo possível.
    fixed = references[references['strategy'].str.startswith('fixo:')]
    best_fixed = fixed.loc[fixed['acceptance'].idxmax()]
    matching = sweep[sweep['acceptance'] >= best_fixed['acceptance'] - 1e-9]
    print(f'\n{"-" * 82}')
    print(f'Melhor candidato isolado: {best_fixed["strategy"]} | '
          f'aceitação {best_fixed["acceptance"]:.4f} | '
          f'{best_fixed["time_ms"]:.1f} ms por requisição')

    highlight = None
    if not matching.empty:
        cheapest = matching.loc[matching['time_ms'].idxmin()]
        speedup = best_fixed['time_ms'] / max(cheapest['time_ms'], 1e-9)
        print(f'Seletor equivalente:      lambda={cheapest["lambda"]} | '
              f'aceitação {cheapest["acceptance"]:.4f} | '
              f'{cheapest["time_ms"]:.1f} ms por requisição')
        print(f'REDUÇÃO DE TEMPO:         {speedup:.1f} vezes, '
              f'com aceitação igual ou superior')
        highlight = {
            'lambda': float(cheapest['lambda']),
            'acceptance': float(cheapest['acceptance']),
            'time_ms': float(cheapest['time_ms']),
            'speedup': float(speedup),
        }
    else:
        print('Nenhuma configuração igualou a aceitação do melhor candidato isolado.')
    print(f'{"-" * 82}')

    return {
        'scope': scope,
        'best_fixed': best_fixed['strategy'],
        'best_fixed_acceptance': float(best_fixed['acceptance']),
        'best_fixed_time_ms': float(best_fixed['time_ms']),
        'ceiling_acceptance': float(test['any_accepted'].mean()),
        'oracle_time_ms': oracle_time,
        'equivalent_lambda': highlight['lambda'] if highlight else None,
        'equivalent_acceptance': highlight['acceptance'] if highlight else None,
        'equivalent_time_ms': highlight['time_ms'] if highlight else None,
        'speedup': highlight['speedup'] if highlight else None,
        'sweep': sweep, 'references': references,
        'binary_model': binary, 'train_times': train_times,
        'algorithms': algorithms, 'features': features,
    }


def main() -> int:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    data = pd.read_csv(DATASET_PATH)
    features = select_features(data)
    print(f'{len(data)} requisições, {len(features)} características preditoras.')

    outcomes = [run_for_subset(data, features, 'global')]
    for topology in sorted(data['topology'].unique()):
        subset = data[data['topology'] == topology]
        subset_features = [f for f in features if f != 'topology_encoded']
        outcomes.append(run_for_subset(subset, subset_features, topology))

    summary = pd.DataFrame([{k: v for k, v in o.items()
                             if k not in ('sweep', 'references', 'binary_model',
                                          'train_times', 'algorithms', 'features')}
                            for o in outcomes])
    print(f'\n{"=" * 82}\nRESUMO\n{"=" * 82}')
    print(summary.to_string(index=False, float_format=lambda v: f'{v:.4f}'))

    summary.to_csv(os.path.join(RESULTS_DIR, 'time_aware_summary.csv'), index=False)
    for outcome in outcomes:
        slug = outcome['scope'].replace(' ', '_')
        outcome['sweep'].to_csv(
            os.path.join(RESULTS_DIR, f'time_aware_sweep_{slug}.csv'), index=False)
        outcome['references'].to_csv(
            os.path.join(RESULTS_DIR, f'time_aware_references_{slug}.csv'), index=False)
    with open(os.path.join(MODELS_DIR, 'time_aware_models.pkl'), 'wb') as handle:
        pickle.dump({o['scope']: {'binary': o['binary_model'],
                                  'train_times': o['train_times'],
                                  'algorithms': o['algorithms'],
                                  'features': o['features']} for o in outcomes}, handle)
    with open(os.path.join(RESULTS_DIR, 'time_aware_summary.json'), 'w') as handle:
        json.dump(summary.to_dict(orient='records'), handle, indent=2, default=float)

    print(f'\nModelos em {MODELS_DIR}\nTabelas em {RESULTS_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
