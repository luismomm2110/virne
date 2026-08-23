"""
Teste do critério de seleção do oráculo guloso.

O critério de ordenação define o significado científico do teto medido, razão
pela qual convém verificá-lo de forma isolada. O teste carrega a função
efetivamente executada em ``ccis/solver/greedy_oracle.py``, e não uma
reimplementação, substituindo por módulos simulados as dependências do virne
que não são exercidas por esta função. Em consequência, o teste dispensa a
instalação de ``omegaconf``, ``hydra`` e ``ortools``.

Uso:
    python ccis/tests/test_score_candidate.py
"""

import importlib.util
import os
import sys
import types

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOLVER_PATH = os.path.join(PROJECT_ROOT, 'ccis', 'solver', 'greedy_oracle.py')


def load_solver_module():
    """Carrega o módulo do oráculo com dependências simuladas."""
    core = types.ModuleType('virne.core')

    class Solution:
        @staticmethod
        def from_v_net(v_net):
            return {}

    core.Solution = Solution

    base_solver = types.ModuleType('virne.solver.base_solver')

    class Solver:
        def __init__(self, *args, **kwargs):
            pass

    class SolverRegistry:
        _registry = {}

        @classmethod
        def register(cls, solver_name, solver_type=None, **kwargs):
            def decorator(handler_cls):
                cls._registry[solver_name] = handler_cls
                return handler_cls
            return decorator

        @classmethod
        def get(cls, name):
            return cls._registry[name]

    base_solver.Solver = Solver
    base_solver.SolverRegistry = SolverRegistry

    sys.modules.update({
        'virne': types.ModuleType('virne'),
        'virne.core': core,
        'virne.solver': types.ModuleType('virne.solver'),
        'virne.solver.base_solver': base_solver,
    })

    spec = importlib.util.spec_from_file_location('greedy_oracle', SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_candidate(name, accepted, r2c_ratio, solve_time_ms):
    """Constrói uma avaliação sintética de candidato."""
    return {
        'name': name, 'accepted': accepted, 'r2c_ratio': r2c_ratio,
        'solve_time_ms': solve_time_ms, 'revenue': 0.0, 'cost': 0.0,
    }


def main() -> int:
    module = load_solver_module()
    solver_cls = module.GreedyOracleSolver
    # A função de pontuação não depende do estado da instância, de modo que uma
    # instância não inicializada é suficiente para exercitá-la.
    instance = solver_cls.__new__(solver_cls)

    def winner(candidates):
        return max(candidates, key=lambda c: solver_cls._score_candidate(instance, c))['name']

    failures = []

    def check(description, obtained, expected):
        passed = obtained == expected
        print(('  ok    ' if passed else '  FALHA') + f' | {description}')
        if not passed:
            failures.append(f'{description}: obtido {obtained!r}, esperado {expected!r}')

    print('\n1. A aceitação prevalece sobre a razão entre receita e custo')
    check('rejeição com razão elevada perde para aceitação com razão baixa',
          winner([make_candidate('rejeita', False, 99.0, 1.0),
                  make_candidate('aceita', True, 0.1, 500.0)]),
          'aceita')

    print('\n2. Entre os que aceitam, prevalece a maior razão entre receita e custo')
    check('razão 0,9 vence razão 0,5 ainda que mais lenta',
          winner([make_candidate('rapido_caro', True, 0.5, 1.0),
                  make_candidate('lento_barato', True, 0.9, 900.0)]),
          'lento_barato')

    print('\n3. Havendo empate na razão, prevalece o menor tempo')
    check('mesma razão, menor tempo',
          winner([make_candidate('lento', True, 0.7, 800.0),
                  make_candidate('rapido', True, 0.7, 12.0)]),
          'rapido')

    print('\n4. Não havendo aceitação, a comparação recai sobre o tempo')
    check('todos rejeitam a requisição',
          winner([make_candidate('a', False, 0.0, 90.0),
                  make_candidate('b', False, 0.0, 3.0)]),
          'b')

    print('\n5. Cenário com os oito candidatos')
    eight = [
        make_candidate('pl_rank', True, 0.62, 4.0),
        make_candidate('rw_rank_bfs', False, 0.0, 6.0),
        make_candidate('d_round', True, 0.58, 120.0),
        make_candidate('sa_meta', True, 0.71, 300.0),
        make_candidate('ga_meta', True, 0.71, 280.0),
        make_candidate('pso_meta', False, 0.0, 250.0),
        make_candidate('mcts', True, 0.40, 900.0),
        make_candidate('mip', True, 0.88, 10000.0),
    ]
    check('mip vence pela razão, apesar de consumir dez segundos',
          winner(eight), 'mip')
    check('sem o mip, ga_meta vence sa_meta pelo tempo, com razão empatada',
          winner([c for c in eight if c['name'] != 'mip']), 'ga_meta')

    print('\n6. Estrutura da chave de ordenação')
    key = solver_cls._score_candidate(instance, make_candidate('x', True, 0.5, 10.0))
    check('a chave é uma tupla de três elementos',
          isinstance(key, tuple) and len(key) == 3, True)
    check('o tempo ingressa negado, pois a ordenação busca o máximo',
          key[2] == -10.0, True)

    print('\n' + '=' * 60)
    if failures:
        print(f'{len(failures)} falha(s):')
        for failure in failures:
            print('  -', failure)
        return 1
    print('Todos os casos foram aprovados.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
