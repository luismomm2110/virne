"""
Executor das simulações do oráculo guloso sobre as topologias e sementes.

Cada combinação de topologia e semente é executada em um processo separado, no
mesmo estilo de ``apresentacao/run_ml_balanced_data_generation.py``.

Advertência quanto ao custo: o oráculo executa todos os candidatos a cada
requisição. O algoritmo ``mip`` possui limite de dez segundos por instância
(``virne/solver/exact/mip.py``) e o ``mcts`` emprega orçamento de cem
simulações, de modo que ambos dominam o tempo total. Recomenda-se medir uma
execução reduzida antes de escalar.

Uso:
    python ccis/run_oracle_experiments.py                    # execução completa
    python ccis/run_oracle_experiments.py --smoke            # validação rápida
    python ccis/run_oracle_experiments.py --seeds 0 1 2 --topologies tree
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_SCRIPT = os.path.join(PROJECT_ROOT, 'ccis', 'main_ccis_oracle.py')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'ccis', 'results')

DEFAULT_TOPOLOGIES = ['tree', 'fat_tree']
DEFAULT_SEEDS = [0, 1, 2, 3, 4]
DEFAULT_TIMEOUT = 14400  # quatro horas por execução

FAST_CANDIDATES = ['pl_rank', 'rw_rank_bfs', 'd_round']


def build_command(topology: str, seed: int, args: argparse.Namespace) -> list:
    """Monta a linha de comando do Hydra para uma execução."""
    command = [
        sys.executable, MAIN_SCRIPT,
        f'--config-name=main_{topology}_ccis_oracle',
        f'experiment.seed={seed}',
    ]
    if args.candidates:
        command.append('solver.oracle_candidates=[' + ','.join(args.candidates) + ']')
    if args.num_v_nets is not None:
        command.append(f'v_sim_setting.num_v_nets={args.num_v_nets}')
    return command


def run_one(topology: str, seed: int, args: argparse.Namespace) -> dict:
    """Executa uma combinação de topologia e semente, devolvendo o desfecho."""
    command = build_command(topology, seed, args)
    print(f'\n{"=" * 70}')
    print(f'Topologia={topology}  semente={seed}')
    print(' '.join(command))
    print('=' * 70)

    started_at = time.perf_counter()
    try:
        completed = subprocess.run(
            command, cwd=PROJECT_ROOT, capture_output=True, text=True,
            timeout=args.timeout)
        elapsed = time.perf_counter() - started_at
        succeeded = completed.returncode == 0
        if not succeeded:
            print(f'FALHA (código {completed.returncode})')
            print(completed.stderr[-4000:])
        else:
            print(f'Concluído em {elapsed / 60:.1f} min')
        return {
            'topology': topology, 'seed': seed, 'success': succeeded,
            'returncode': completed.returncode, 'elapsed_s': elapsed,
            'stderr_tail': completed.stderr[-2000:] if not succeeded else '',
        }
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - started_at
        print(f'TEMPO EXCEDIDO após {elapsed / 60:.1f} min')
        return {
            'topology': topology, 'seed': seed, 'success': False,
            'returncode': None, 'elapsed_s': elapsed,
            'stderr_tail': 'timeout',
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--topologies', nargs='+', default=DEFAULT_TOPOLOGIES)
    parser.add_argument('--seeds', nargs='+', type=int, default=DEFAULT_SEEDS)
    parser.add_argument('--candidates', nargs='+', default=None,
                        help='Restringe o conjunto de candidatos.')
    parser.add_argument('--num-v-nets', type=int, default=None,
                        help='Sobrescreve o número de requisições por simulação.')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument('--smoke', action='store_true',
                        help='Validação rápida: uma semente, três candidatos, 20 requisições.')
    args = parser.parse_args()

    if args.smoke:
        args.seeds = [args.seeds[0]]
        args.candidates = args.candidates or FAST_CANDIDATES
        args.num_v_nets = args.num_v_nets or 20
        args.timeout = min(args.timeout, 1800)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    outcomes = [run_one(topology, seed, args)
                for topology in args.topologies
                for seed in args.seeds]

    num_ok = sum(1 for o in outcomes if o['success'])
    total_hours = sum(o['elapsed_s'] for o in outcomes) / 3600
    print(f'\n{"=" * 70}')
    print(f'Execuções bem-sucedidas: {num_ok}/{len(outcomes)}  '
          f'(tempo total: {total_hours:.2f} h)')
    for outcome in outcomes:
        if not outcome['success']:
            print(f'  falhou: {outcome["topology"]} semente {outcome["seed"]}')

    report_path = os.path.join(
        RESULTS_DIR, f'oracle_runs-{datetime.now():%Y%m%dT%H%M%S}.json')
    with open(report_path, 'w') as handle:
        json.dump(outcomes, handle, indent=2)
    print(f'Relatório das execuções: {report_path}')

    return 0 if num_ok == len(outcomes) else 1


if __name__ == '__main__':
    raise SystemExit(main())
