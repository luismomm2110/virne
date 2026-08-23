"""
Treino da árvore de decisão para seleção de algoritmos de mapeamento.

O conjunto de treino provém do oráculo guloso, no qual todos os candidatos
disputaram exatamente o mesmo estado da rede física a cada requisição. O rótulo
``best_algorithm`` é, portanto, causalmente válido, ao contrário da rotulagem
obtida por agregação de simulações independentes.

Três decisões de projeto merecem registro:

1. **Divisão por semente, e não aleatória.** As requisições de uma mesma
   simulação são fortemente correlacionadas, pois o estado da rede física
   evolui de forma contínua ao longo da trajetória: requisições consecutivas
   enfrentam estados quase idênticos. Uma divisão aleatória colocaria
   requisições vizinhas em treino e teste, e a acurácia medida refletiria
   memorização, não generalização. A divisão por semente garante que o conjunto
   de teste corresponda a trajetórias inteiramente inéditas.

2. **Seleção do modelo pela consequência, e não pela acurácia.** O modelo é
   escolhido pela taxa de aceitação que a sua escolha efetivamente alcança, e
   não pela coincidência com o rótulo. A distinção é relevante porque em boa
   parte das requisições diversos candidatos aceitam: discordar do rótulo não
   implica errar a decisão.

3. **Apenas características observáveis no instante da decisão.** Todas as
   colunas que descrevem o desfecho — ``accepted_*``, ``best_*``,
   ``num_candidates_accepted``, ``is_decisive`` — são descartadas, sob pena de
   vazamento. Esse cuidado é o que a rotulagem anterior não observava, ao
   manter ``v_net_time_cost`` e ``v_net_time_revenue`` entre as variáveis
   preditoras.

Uso:
    python ccis/train_decision_tree.py
"""

import json
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier, export_text

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(PROJECT_ROOT, 'ccis', 'datasets', 'oracle_dataset.csv')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'ccis', 'results')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'ccis', 'models')

# Sementes reservadas a cada finalidade. A separação por trajetória inteira é o
# que impede o vazamento descrito no cabeçalho.
TRAIN_SEEDS = [0, 1, 2]
VAL_SEEDS = [3]
TEST_SEEDS = [4]

# Colunas descartadas por descreverem o desfecho, e não o estado observável.
LEAKAGE_PREFIXES = ('accepted_', 'best_', 'time_', 'r2c_')
LEAKAGE_COLUMNS = {
    'num_candidates_accepted', 'num_candidates', 'oracle_total_solve_time_ms',
    'any_accepted', 'is_decisive',
}
# Colunas de identificação, sem valor preditivo legítimo. A coluna 'event_time'
# é observável, porém funciona como indicador da fase da simulação e induziria
# o modelo a memorizar a duração fixa de trezentas requisições; a saturação da
# rede já se encontra representada em 'p_net_node_util' e 'inservice_count'.
IDENTIFIER_COLUMNS = {'topology', 'seed', 'v_net_id', 'event_time'}

CANDIDATE_DEPTHS = [3, 4, 5, 6, 8, 10, 12, None]


# ---------------------------------------------------------------------- #
# Preparação
# ---------------------------------------------------------------------- #

def select_features(frame: pd.DataFrame) -> list:
    """Devolve as colunas admissíveis como variáveis preditoras."""
    features = []
    for column in frame.columns:
        if column == 'best_algorithm':
            continue
        if column in IDENTIFIER_COLUMNS or column in LEAKAGE_COLUMNS:
            continue
        if column.startswith(LEAKAGE_PREFIXES):
            continue
        features.append(column)
    return features


def split_by_seed(frame: pd.DataFrame):
    """Divide o conjunto por semente, preservando trajetórias inteiras."""
    train = frame[frame['seed'].isin(TRAIN_SEEDS)]
    val = frame[frame['seed'].isin(VAL_SEEDS)]
    test = frame[frame['seed'].isin(TEST_SEEDS)]
    return train, val, test


# ---------------------------------------------------------------------- #
# Avaliação pela consequência
# ---------------------------------------------------------------------- #

def acceptance_of_choice(frame: pd.DataFrame, choices) -> float:
    """
    Taxa de aceitação efetivamente alcançada pelas escolhas do modelo.

    Para cada requisição, consulta-se a coluna ``accepted_<algoritmo>``
    correspondente ao algoritmo escolhido. A predição do rótulo ``none``
    equivale a rejeitar a requisição sem tentativa, e portanto não obtém
    aceitação.

    Esta é a métrica que importa: um seletor pode divergir do rótulo e ainda
    assim obter a aceitação, sempre que o algoritmo escolhido também aceite a
    requisição.
    """
    accepted = np.zeros(len(frame), dtype=bool)
    choices = np.asarray(choices)
    for algorithm in np.unique(choices):
        if algorithm == 'none':
            continue
        column = f'accepted_{algorithm}'
        if column not in frame.columns:
            continue
        mask = choices == algorithm
        accepted[mask] = frame.loc[mask, column].to_numpy(dtype=bool)
    return float(accepted.mean())


def evaluate(frame: pd.DataFrame, choices, label: str) -> dict:
    """Reúne as métricas de um conjunto de escolhas."""
    truth = frame['best_algorithm'].to_numpy()
    decisive = frame['is_decisive'].to_numpy(dtype=bool)
    return {
        'strategy': label,
        'acceptance_achieved': acceptance_of_choice(frame, choices),
        'label_accuracy': float(accuracy_score(truth, choices)),
        'label_accuracy_decisive': (float(accuracy_score(truth[decisive],
                                                         np.asarray(choices)[decisive]))
                                    if decisive.any() else float('nan')),
    }


def baseline_choices(frame: pd.DataFrame, algorithm: str):
    """Escolhas de um seletor que sempre elege o mesmo algoritmo."""
    return np.full(len(frame), algorithm)


def predict_without_abstention(model, features_frame):
    """
    Prediz sempre um algoritmo, jamais o rótulo ``none``.

    O rótulo ``none`` designa as requisições que nenhum candidato aceita, e
    corresponde à maioria dos casos. Predizê-lo equivale a rejeitar a
    requisição sem tentativa alguma, o que garante a não aceitação. Ora, uma
    tentativa malsucedida custa apenas tempo de processamento e não consome
    recurso algum da rede física, ao passo que a abstenção descarta toda
    possibilidade de aceitação.

    Sob o objetivo de maximizar a taxa de aceitação, portanto, a abstenção
    nunca é vantajosa, e esta função elege a classe de maior probabilidade
    entre as demais. A abstenção só faria sentido sob um objetivo que
    valorizasse a economia de tempo, hipótese alheia ao presente trabalho.
    """
    probabilities = model.predict_proba(features_frame)
    classes = np.asarray(model.classes_)
    admissible = classes != 'none'
    if not admissible.any():
        return model.predict(features_frame)
    masked = probabilities[:, admissible]
    return classes[admissible][masked.argmax(axis=1)]


# ---------------------------------------------------------------------- #
# Treino
# ---------------------------------------------------------------------- #

def train_and_select(train, val, features, random_state: int = 42):
    """
    Treina árvores sob diferentes profundidades e ponderações de classe, e
    elege a de melhor consequência no conjunto de validação.

    A ponderação das classes é tratada como hiperparâmetro porque a maximização
    da taxa de aceitação não constitui um problema equilibrado: a ponderação
    ``balanced`` favorece as classes raras em detrimento do ``mip``, que é ao
    mesmo tempo a classe mais frequente e o candidato mais eficaz.
    """
    x_train, y_train = train[features], train['best_algorithm']
    results = []
    best_model, best_score, best_config = None, -1.0, None

    for class_weight in [None, 'balanced']:
        for depth in CANDIDATE_DEPTHS:
            model = DecisionTreeClassifier(
                max_depth=depth,
                min_samples_leaf=20,
                class_weight=class_weight,
                random_state=random_state)
            model.fit(x_train, y_train)
            choices = predict_without_abstention(model, val[features])
            score = acceptance_of_choice(val, choices)
            results.append({
                'max_depth': depth,
                'class_weight': str(class_weight),
                'val_acceptance': score,
                'val_acceptance_with_abstention': acceptance_of_choice(
                    val, model.predict(val[features])),
                'num_leaves': int(model.get_n_leaves()),
            })
            if score > best_score:
                best_model, best_score = model, score
                best_config = (depth, class_weight)

    return best_model, best_config, pd.DataFrame(results)


def report_on_test(model, test, features, ceiling: float) -> pd.DataFrame:
    """
    Compara a árvore com os seletores de referência sobre o conjunto de teste.

    O teto corresponde à fração de requisições que ao menos um candidato aceita,
    ou seja, ao próprio oráculo guloso restrito ao conjunto de teste.
    """
    rows = [
        evaluate(test, predict_without_abstention(model, test[features]),
                 'árvore de decisão'),
        evaluate(test, model.predict(test[features]),
                 'árvore com abstenção (none)'),
    ]

    algorithms = sorted(c.replace('accepted_', '')
                        for c in test.columns if c.startswith('accepted_'))
    for algorithm in algorithms:
        rows.append(evaluate(test, baseline_choices(test, algorithm),
                             f'fixo: {algorithm}'))

    rows.append({
        'strategy': 'ORÁCULO GULOSO (teto)',
        'acceptance_achieved': ceiling,
        'label_accuracy': 1.0,
        'label_accuracy_decisive': 1.0,
    })
    return pd.DataFrame(rows).sort_values('acceptance_achieved', ascending=False)


# ---------------------------------------------------------------------- #
# Execução
# ---------------------------------------------------------------------- #

def run_for_subset(data: pd.DataFrame, features: list, scope: str) -> dict:
    """Treina e avalia um modelo sobre um recorte do conjunto."""
    train, val, test = split_by_seed(data)
    print(f'\n{"=" * 74}\nESCOPO: {scope}\n{"=" * 74}')
    print(f'treino {len(train)} | validação {len(val)} | teste {len(test)} requisições')

    model, config, sweep = train_and_select(train, val, features)
    depth, class_weight = config
    print(f'\nBusca de hiperparâmetros (métrica: aceitação alcançada na validação):')
    print(sweep.sort_values('val_acceptance', ascending=False)
          .to_string(index=False, float_format=lambda v: f'{v:.4f}'))
    print(f'\nConfiguração eleita: profundidade {depth}, ponderação {class_weight}')

    ceiling = float(test['any_accepted'].mean())
    comparison = report_on_test(model, test, features, ceiling)
    print(f'\nDesempenho sobre o conjunto de teste (semente {TEST_SEEDS[0]}):')
    print(comparison.to_string(index=False, float_format=lambda v: f'{v:.4f}'))

    tree_row = comparison[comparison['strategy'] == 'árvore de decisão'].iloc[0]
    fixed = comparison[comparison['strategy'].str.startswith('fixo:')]
    best_fixed = fixed.loc[fixed['acceptance_achieved'].idxmax()]

    tree_acc = float(tree_row['acceptance_achieved'])
    fixed_acc = float(best_fixed['acceptance_achieved'])
    gap = ceiling - fixed_acc
    captured = (tree_acc - fixed_acc) / gap if gap > 1e-9 else float('nan')

    print(f'\nMelhor algoritmo fixo: {best_fixed["strategy"]} = {fixed_acc:.4f}')
    print(f'Árvore de decisão:     {tree_acc:.4f}')
    print(f'Teto do oráculo:       {ceiling:.4f}')
    print(f'Lacuna disponível:     {gap:.4f}')
    print(f'Lacuna capturada:      {captured:.1%}')

    importance = (pd.DataFrame({'feature': features,
                                'importance': model.feature_importances_})
                  .sort_values('importance', ascending=False))
    print(f'\nDez características mais influentes:')
    print(importance.head(10).to_string(index=False, float_format=lambda v: f'{v:.4f}'))

    return {
        'scope': scope, 'max_depth': depth, 'class_weight': str(class_weight),
        'num_leaves': int(model.get_n_leaves()),
        'ceiling': ceiling, 'best_fixed': best_fixed['strategy'],
        'best_fixed_acceptance': fixed_acc, 'tree_acceptance': tree_acc,
        'gap_available': gap, 'gap_captured': captured,
        'label_accuracy': float(tree_row['label_accuracy']),
        'label_accuracy_decisive': float(tree_row['label_accuracy_decisive']),
        'model': model, 'features': features,
        'sweep': sweep, 'comparison': comparison, 'importance': importance,
    }


def main() -> int:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    data = pd.read_csv(DATASET_PATH)
    features = select_features(data)
    print(f'{len(data)} requisições, {len(features)} características preditoras.')
    print(f'Descartadas por vazamento ou identificação: '
          f'{len(data.columns) - len(features) - 1}.')

    outcomes = [run_for_subset(data, features, 'global (as duas topologias)')]
    for topology in sorted(data['topology'].unique()):
        subset = data[data['topology'] == topology]
        # No recorte por topologia a codificação da topologia é constante e,
        # portanto, desprovida de informação.
        subset_features = [f for f in features if f != 'topology_encoded']
        outcomes.append(run_for_subset(subset, subset_features, f'topologia {topology}'))

    summary = pd.DataFrame([{k: v for k, v in o.items()
                             if k not in ('model', 'features', 'sweep',
                                          'comparison', 'importance')}
                            for o in outcomes])
    print(f'\n{"=" * 74}\nRESUMO\n{"=" * 74}')
    print(summary.to_string(index=False, float_format=lambda v: f'{v:.4f}'))

    summary.to_csv(os.path.join(RESULTS_DIR, 'tree_summary.csv'), index=False)
    for outcome in outcomes:
        slug = outcome['scope'].split()[-1].strip('()')
        outcome['comparison'].to_csv(
            os.path.join(RESULTS_DIR, f'tree_comparison_{slug}.csv'), index=False)
        outcome['importance'].to_csv(
            os.path.join(RESULTS_DIR, f'tree_importance_{slug}.csv'), index=False)

    with open(os.path.join(MODELS_DIR, 'decision_trees.pkl'), 'wb') as handle:
        pickle.dump({o['scope']: {'model': o['model'], 'features': o['features']}
                     for o in outcomes}, handle)

    global_outcome = outcomes[0]
    rules_path = os.path.join(RESULTS_DIR, 'tree_rules_global.txt')
    with open(rules_path, 'w') as handle:
        handle.write(export_text(global_outcome['model'],
                                 feature_names=list(global_outcome['features']),
                                 max_depth=4))

    with open(os.path.join(RESULTS_DIR, 'tree_summary.json'), 'w') as handle:
        json.dump(summary.to_dict(orient='records'), handle, indent=2, default=float)

    print(f'\nModelos em {MODELS_DIR}')
    print(f'Tabelas e regras em {RESULTS_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
