"""
Aprendizado sensível ao custo para a seleção de algoritmos de mapeamento.

O treino convencional, conduzido em ``ccis/train_decision_tree.py``, trata
todos os erros como equivalentes e maximiza a coincidência com o rótulo. O
diagnóstico obtido naquele experimento revelou a inadequação dessa formulação:
a árvore alcançou acurácia superior à do melhor algoritmo fixo nas requisições
decisivas e, ainda assim, obteve taxa de aceitação inferior. A causa reside na
assimetria dos erros. Substituir o candidato mais eficaz por outro que também
aceitaria a requisição nada acrescenta, ao passo que substituí-lo por um que a
rejeita custa uma aceitação. Sob a acurácia, ambos os desfechos contam o mesmo.

Duas formulações são aqui avaliadas.

**Formulação por ponderação.** O treino restringe-se às requisições decisivas,
isto é, àquelas em que parte dos candidatos aceita e parte rejeita, pois apenas
nelas a escolha altera o desfecho. Cada exemplo recebe peso inversamente
proporcional ao número de candidatos que aceitam a requisição: quanto mais raro
o acerto, mais oneroso o erro, e maior a atenção que o exemplo merece.

**Formulação por redução binária.** Em lugar de um classificador de oito
classes, treina-se um classificador binário por candidato, encarregado de
estimar a probabilidade de que aquele candidato aceite a requisição diante do
estado corrente. A escolha recai sobre o candidato de maior probabilidade
estimada. Trata-se da formulação diretamente alinhada ao objetivo: maximizar a
probabilidade de aceitação não exige identificar o melhor candidato, mas apenas
identificar algum candidato que aceite.

Uso:
    python ccis/train_cost_sensitive.py
"""

import json
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(PROJECT_ROOT, 'ccis', 'datasets', 'oracle_dataset.csv')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'ccis', 'results')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'ccis', 'models')

TRAIN_SEEDS = [0, 1, 2]
VAL_SEEDS = [3]
TEST_SEEDS = [4]

LEAKAGE_PREFIXES = ('accepted_', 'best_', 'time_', 'r2c_')
LEAKAGE_COLUMNS = {
    'num_candidates_accepted', 'num_candidates', 'oracle_total_solve_time_ms',
    'any_accepted', 'is_decisive',
}
IDENTIFIER_COLUMNS = {'topology', 'seed', 'v_net_id', 'event_time'}

CANDIDATE_DEPTHS = [3, 4, 5, 6, 8, 10, 12, None]
MIN_SAMPLES_LEAF = [5, 10, 20]


# ---------------------------------------------------------------------- #
# Preparação
# ---------------------------------------------------------------------- #

def select_features(frame: pd.DataFrame) -> list:
    """Devolve as colunas admissíveis como variáveis preditoras."""
    return [c for c in frame.columns
            if c != 'best_algorithm'
            and c not in IDENTIFIER_COLUMNS
            and c not in LEAKAGE_COLUMNS
            and not c.startswith(LEAKAGE_PREFIXES)]


def split_by_seed(frame: pd.DataFrame):
    """Divide o conjunto por semente, preservando trajetórias inteiras."""
    return (frame[frame['seed'].isin(TRAIN_SEEDS)],
            frame[frame['seed'].isin(VAL_SEEDS)],
            frame[frame['seed'].isin(TEST_SEEDS)])


def algorithm_names(frame: pd.DataFrame) -> list:
    """Nomes dos candidatos, extraídos das colunas de desfecho."""
    return sorted(c.replace('accepted_', '')
                  for c in frame.columns if c.startswith('accepted_'))


# ---------------------------------------------------------------------- #
# Avaliação pela consequência
# ---------------------------------------------------------------------- #

def acceptance_of_choice(frame: pd.DataFrame, choices) -> float:
    """Taxa de aceitação efetivamente alcançada pelas escolhas."""
    accepted = np.zeros(len(frame), dtype=bool)
    choices = np.asarray(choices)
    for algorithm in np.unique(choices):
        column = f'accepted_{algorithm}'
        if column not in frame.columns:
            continue
        mask = choices == algorithm
        accepted[mask] = frame.loc[mask, column].to_numpy(dtype=bool)
    return float(accepted.mean())


# ---------------------------------------------------------------------- #
# Formulação por ponderação
# ---------------------------------------------------------------------- #

def cost_weights(frame: pd.DataFrame) -> np.ndarray:
    """
    Peso de cada exemplo, proporcional ao custo de errar a escolha.

    O peso é inversamente proporcional ao número de candidatos que aceitam a
    requisição. Quando um único candidato aceita, o erro custa a aceitação
    integralmente, e o exemplo recebe o peso máximo; quando muitos aceitam, o
    erro é quase inconsequente, e o peso decresce na mesma proporção.
    """
    accepted = frame['num_candidates_accepted'].to_numpy(dtype=float)
    total = frame['num_candidates'].to_numpy(dtype=float)
    return np.where(accepted > 0, total / np.maximum(accepted, 1.0), 0.0)


def train_weighted(train, val, features, random_state: int = 42):
    """
    Treina sobre as requisições decisivas, ponderadas pelo custo do erro.

    As requisições não decisivas são excluídas porque nelas a escolha não altera
    o desfecho: ou nenhum candidato aceita, ou todos aceitam. Mantê-las apenas
    diluiria o sinal de aprendizado.
    """
    decisive = train[train['is_decisive']]
    x_train = decisive[features]
    y_train = decisive['best_algorithm']
    weights = cost_weights(decisive)

    records, best_model, best_score, best_config = [], None, -1.0, None
    for depth in CANDIDATE_DEPTHS:
        for leaf in MIN_SAMPLES_LEAF:
            model = DecisionTreeClassifier(
                max_depth=depth, min_samples_leaf=leaf, random_state=random_state)
            model.fit(x_train, y_train, sample_weight=weights)
            score = acceptance_of_choice(val, model.predict(val[features]))
            records.append({'max_depth': depth, 'min_samples_leaf': leaf,
                            'val_acceptance': score,
                            'num_leaves': int(model.get_n_leaves())})
            if score > best_score:
                best_model, best_score, best_config = model, score, (depth, leaf)
    return best_model, best_config, pd.DataFrame(records), len(decisive)


# ---------------------------------------------------------------------- #
# Formulação por redução binária
# ---------------------------------------------------------------------- #

class BinaryReductionSelector:
    """
    Seletor composto por um classificador binário por candidato.

    Cada classificador estima a probabilidade de que o respectivo candidato
    aceite a requisição diante do estado observado, e a escolha recai sobre o
    candidato de maior probabilidade estimada.
    """

    def __init__(self, algorithms, max_depth=None, min_samples_leaf=10,
                 random_state=42):
        self.algorithms = list(algorithms)
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        self.models = {}

    def fit(self, frame, features):
        for algorithm in self.algorithms:
            target = frame[f'accepted_{algorithm}'].to_numpy(dtype=int)
            model = DecisionTreeClassifier(
                max_depth=self.max_depth,
                min_samples_leaf=self.min_samples_leaf,
                random_state=self.random_state)
            # Um candidato que jamais aceita, como o pso_meta, apresenta classe
            # única e não admite ajuste; a probabilidade é fixada em zero.
            if len(np.unique(target)) < 2:
                self.models[algorithm] = float(target.mean())
            else:
                model.fit(frame[features], target)
                self.models[algorithm] = model
        return self

    def predict_proba_matrix(self, frame, features):
        """Matriz de probabilidades estimadas, com uma coluna por candidato."""
        columns = []
        for algorithm in self.algorithms:
            model = self.models[algorithm]
            if isinstance(model, float):
                columns.append(np.full(len(frame), model))
            else:
                columns.append(model.predict_proba(frame[features])[:, 1])
        return np.column_stack(columns)

    def predict(self, frame, features):
        matrix = self.predict_proba_matrix(frame, features)
        return np.asarray(self.algorithms)[matrix.argmax(axis=1)]


def train_binary_reduction(train, val, features, algorithms, random_state: int = 42):
    """Ajusta a profundidade e o tamanho mínimo de folha por validação."""
    records, best_model, best_score, best_config = [], None, -1.0, None
    for depth in CANDIDATE_DEPTHS:
        for leaf in MIN_SAMPLES_LEAF:
            selector = BinaryReductionSelector(
                algorithms, max_depth=depth, min_samples_leaf=leaf,
                random_state=random_state).fit(train, features)
            score = acceptance_of_choice(val, selector.predict(val, features))
            records.append({'max_depth': depth, 'min_samples_leaf': leaf,
                            'val_acceptance': score})
            if score > best_score:
                best_model, best_score, best_config = selector, score, (depth, leaf)
    return best_model, best_config, pd.DataFrame(records)


# ---------------------------------------------------------------------- #
# Execução
# ---------------------------------------------------------------------- #

def run_for_subset(data: pd.DataFrame, features: list, scope: str) -> dict:
    """Treina e compara as duas formulações sobre um recorte do conjunto."""
    train, val, test = split_by_seed(data)
    algorithms = algorithm_names(data)
    print(f'\n{"=" * 78}\nESCOPO: {scope}\n{"=" * 78}')
    print(f'treino {len(train)} | validação {len(val)} | teste {len(test)} requisições')

    weighted, w_config, w_sweep, num_decisive = train_weighted(train, val, features)
    print(f'\nFormulação por ponderação: {num_decisive} requisições decisivas no '
          f'treino ({num_decisive / len(train):.1%} do total)')
    print(f'  configuração eleita: profundidade {w_config[0]}, folha mínima {w_config[1]}'
          f' | validação {w_sweep["val_acceptance"].max():.4f}')

    binary, b_config, b_sweep = train_binary_reduction(train, val, features, algorithms)
    print(f'Formulação por redução binária:')
    print(f'  configuração eleita: profundidade {b_config[0]}, folha mínima {b_config[1]}'
          f' | validação {b_sweep["val_acceptance"].max():.4f}')

    ceiling = float(test['any_accepted'].mean())
    truth = test['best_algorithm'].to_numpy()
    decisive_mask = test['is_decisive'].to_numpy(dtype=bool)

    strategies = {
        'ponderada (custo do erro)': weighted.predict(test[features]),
        'redução binária': binary.predict(test, features),
    }
    rows = []
    for label, choices in strategies.items():
        rows.append({
            'strategy': label,
            'acceptance_achieved': acceptance_of_choice(test, choices),
            'label_accuracy': float(accuracy_score(truth, choices)),
            'label_accuracy_decisive': float(accuracy_score(
                truth[decisive_mask], np.asarray(choices)[decisive_mask])),
        })
    for algorithm in algorithms:
        choices = np.full(len(test), algorithm)
        rows.append({
            'strategy': f'fixo: {algorithm}',
            'acceptance_achieved': acceptance_of_choice(test, choices),
            'label_accuracy': float(accuracy_score(truth, choices)),
            'label_accuracy_decisive': float(accuracy_score(
                truth[decisive_mask], choices[decisive_mask])),
        })
    rows.append({'strategy': 'ORÁCULO GULOSO (teto)', 'acceptance_achieved': ceiling,
                 'label_accuracy': 1.0, 'label_accuracy_decisive': 1.0})

    comparison = pd.DataFrame(rows).sort_values('acceptance_achieved', ascending=False)
    print(f'\nDesempenho sobre o conjunto de teste (semente {TEST_SEEDS[0]}):')
    print(comparison.to_string(index=False, float_format=lambda v: f'{v:.4f}'))

    fixed = comparison[comparison['strategy'].str.startswith('fixo:')]
    best_fixed = fixed.loc[fixed['acceptance_achieved'].idxmax()]
    fixed_acc = float(best_fixed['acceptance_achieved'])
    gap = ceiling - fixed_acc

    print(f'\n{"estratégia":<28}{"aceitação":>12}{"lacuna capturada":>20}')
    print(f'{"-" * 60}')
    print(f'{best_fixed["strategy"]:<28}{fixed_acc:>12.4f}{"referência":>20}')
    best_label, best_acc = None, -1.0
    for label in strategies:
        accuracy = float(comparison.loc[comparison['strategy'] == label,
                                        'acceptance_achieved'].iloc[0])
        captured = (accuracy - fixed_acc) / gap if gap > 1e-9 else float('nan')
        print(f'{label:<28}{accuracy:>12.4f}{captured:>19.1%}')
        if accuracy > best_acc:
            best_label, best_acc = label, accuracy
    print(f'{"ORÁCULO (teto)":<28}{ceiling:>12.4f}{1.0:>19.1%}')

    return {
        'scope': scope, 'ceiling': ceiling,
        'best_fixed': best_fixed['strategy'], 'best_fixed_acceptance': fixed_acc,
        'gap_available': gap,
        'weighted_acceptance': float(comparison.loc[
            comparison['strategy'] == 'ponderada (custo do erro)',
            'acceptance_achieved'].iloc[0]),
        'binary_acceptance': float(comparison.loc[
            comparison['strategy'] == 'redução binária',
            'acceptance_achieved'].iloc[0]),
        'best_strategy': best_label, 'best_strategy_acceptance': best_acc,
        'gap_captured': (best_acc - fixed_acc) / gap if gap > 1e-9 else float('nan'),
        'comparison': comparison, 'weighted_model': weighted, 'binary_model': binary,
        'features': features,
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
                             if k not in ('comparison', 'weighted_model',
                                          'binary_model', 'features')}
                            for o in outcomes])
    print(f'\n{"=" * 78}\nRESUMO\n{"=" * 78}')
    print(summary.to_string(index=False, float_format=lambda v: f'{v:.4f}'))

    summary.to_csv(os.path.join(RESULTS_DIR, 'cost_sensitive_summary.csv'), index=False)
    for outcome in outcomes:
        slug = outcome['scope'].replace(' ', '_')
        outcome['comparison'].to_csv(
            os.path.join(RESULTS_DIR, f'cost_sensitive_comparison_{slug}.csv'),
            index=False)
    with open(os.path.join(MODELS_DIR, 'cost_sensitive_models.pkl'), 'wb') as handle:
        pickle.dump({o['scope']: {'weighted': o['weighted_model'],
                                  'binary': o['binary_model'],
                                  'features': o['features']} for o in outcomes}, handle)
    with open(os.path.join(RESULTS_DIR, 'cost_sensitive_summary.json'), 'w') as handle:
        json.dump(summary.to_dict(orient='records'), handle, indent=2, default=float)

    print(f'\nModelos em {MODELS_DIR}\nTabelas em {RESULTS_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
