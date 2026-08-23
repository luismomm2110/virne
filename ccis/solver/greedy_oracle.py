# ==============================================================================
# Oráculo guloso para seleção de algoritmos de mapeamento de redes virtuais.
# Autor: Luis Antonio Momm Duarte
# ==============================================================================
"""
Solucionador que implementa o oráculo guloso.

A cada chegada de uma requisição de rede virtual (VNR), este solucionador
executa todos os algoritmos candidatos sobre **exatamente o mesmo estado** da
rede física (PN), seleciona o melhor resultado segundo um critério declarado e
devolve apenas a solução vencedora ao ambiente. A simulação prossegue a partir
da consequência causal dessa escolha.

Duas propriedades delimitam a interpretação científica do resultado:

1. Trata-se de um teto para seletores míopes. O oráculo conhece o desfecho de
   todos os candidatos no passo corrente, informação indisponível a qualquer
   seletor real, mas desconhece as chegadas futuras. Nenhum seletor que decida
   requisição a requisição pode superá-lo.
2. Não se trata do ótimo global da trajetória. A escolha gulosa pode consumir
   recursos de maneira a bloquear requisições futuras, de modo que um seletor
   dotado de previsão poderia superá-lo.

A validade do rótulo produzido decorre de um único fato arquitetural: os
candidatos recebem cópias independentes do mesmo estado. O ambiente entrega ao
solucionador cópias profundas de ``v_net`` e ``p_net`` por meio de
``SolutionStepEnvironment.get_observation``, e apenas a solução devolvida é
efetivada na rede física autoritativa por ``SolutionStepEnvironment.step``.
"""

import copy
import csv
import os
import time
from typing import Any, Dict, List, Optional

import numpy as np

from virne.core import Solution
from virne.solver.base_solver import Solver, SolverRegistry


# Conjunto padrão de candidatos, idêntico ao empregado nas simulações isoladas
# que constituem as linhas de base do trabalho.
DEFAULT_ORACLE_CANDIDATES = [
    'pl_rank',
    'rw_rank_bfs',
    'd_round',
    'sa_meta',
    'ga_meta',
    'pso_meta',
    'mcts',
    'mip',
]

# Colunas do arquivo de resultados por requisição. A ordem é fixa para que os
# arquivos de corridas distintas possam ser concatenados diretamente.
CSV_FIELDNAMES = [
    # Identificação
    'topology', 'seed', 'v_net_id', 'event_id', 'event_time',
    # Características da requisição virtual
    'v_net_num_nodes', 'v_net_num_links', 'v_net_lifetime',
    'v_net_node_demand', 'v_net_link_demand', 'v_net_total_demand',
    'v_net_connectivity', 'v_net_avg_degree',
    'v_net_max_node_demand', 'v_net_max_link_demand',
    # Estado da rede física imediatamente antes da decisão
    'p_net_node_available', 'p_net_link_available',
    'p_net_node_util', 'p_net_link_util',
    'p_net_min_node_available', 'p_net_min_link_available',
    'inservice_count',
    # Resultado de cada candidato
    'algorithm', 'result', 'v_net_revenue', 'v_net_cost', 'v_net_r2c_ratio',
    'solve_time_ms', 'place_result', 'route_result', 'description',
    # Rótulo e custo do oráculo
    'is_winner', 'num_candidates_accepted', 'oracle_total_solve_time_ms',
]


@SolverRegistry.register(solver_name='greedy_oracle', solver_type='oracle')
class GreedyOracleSolver(Solver):
    """
    Oráculo guloso: executa todos os candidatos sobre o mesmo estado da rede
    física e efetiva o melhor resultado.
    """

    def __init__(self, controller, recorder, counter, logger, config, **kwargs) -> None:
        super(GreedyOracleSolver, self).__init__(
            controller, recorder, counter, logger, config, **kwargs)

        self.candidate_names: List[str] = self._read_candidate_names(config)
        self.candidates: Dict[str, Solver] = {}
        for name in self.candidate_names:
            candidate_cls = SolverRegistry.get(name)
            # Os candidatos são construídos sem argumentos opcionais, de modo
            # que cada classe aplique os próprios padrões (por exemplo, 'mip'
            # sobrescreve shortest_method para 'mcf' e 'd_round' para
            # 'bfs_shortest' no respectivo __init__). Isso reproduz o
            # comportamento das corridas isoladas.
            self.candidates[name] = candidate_cls(controller, recorder, counter, logger, config)

        self._apply_time_limits(config)

        self.topology_name: str = self._read_topology_name(config)
        self.csv_path: str = self._build_csv_path(config)
        self._csv_initialized: bool = False
        # Capacidade total da rede física, memorizada na primeira chamada, na
        # qual a rede ainda se encontra intacta logo após o reinício.
        self._p_net_node_capacity: Optional[float] = None
        self._p_net_link_capacity: Optional[float] = None

        self.logger.info(
            f'Oráculo guloso inicializado com {len(self.candidates)} candidatos: '
            f'{", ".join(self.candidate_names)}')
        self.logger.info(f'Resultados por requisição em: {self.csv_path}')

    # ------------------------------------------------------------------ #
    # Configuração
    # ------------------------------------------------------------------ #

    @staticmethod
    def _read_candidate_names(config) -> List[str]:
        """Lê a lista de candidatos da configuração, com padrão explícito."""
        names = None
        solver_config = getattr(config, 'solver', None)
        if solver_config is not None:
            names = getattr(solver_config, 'oracle_candidates', None)
        if names is None:
            return list(DEFAULT_ORACLE_CANDIDATES)
        return [str(name) for name in names]

    def _apply_time_limits(self, config) -> None:
        """
        Ajusta o limite de tempo dos candidatos baseados em programação linear.

        Os solucionadores ``mip``, ``d_round`` e ``r_round`` expõem o atributo
        ``MAX_TIME_IN_SECONDS``, consultado a cada resolução em
        ``virne/solver/exact/`` no momento de configurar o limite do OR-Tools.
        Alterá-lo por instância surte efeito imediato e não afeta as demais
        execuções do virne, de modo que as linhas de base já produzidas
        permanecem reproduzíveis com o valor original.

        O ajuste é relevante porque o ``mip`` esgota o limite em praticamente
        toda instância, sem jamais provar otimalidade, e por isso domina o
        custo total do oráculo. Reduzir o limite diminui a qualidade das
        soluções que ele produz, razão pela qual o valor efetivamente aplicado
        é registrado no diário de execução.
        """
        limits = None
        solver_config = getattr(config, 'solver', None)
        if solver_config is not None:
            limits = getattr(solver_config, 'candidate_time_limits', None)
        if not limits:
            return

        for name, seconds in dict(limits).items():
            candidate = self.candidates.get(name)
            if candidate is None:
                continue
            if not hasattr(candidate, 'MAX_TIME_IN_SECONDS'):
                self.logger.warning(
                    f'O candidato {name} não expõe MAX_TIME_IN_SECONDS; '
                    f'o limite de tempo configurado foi ignorado.')
                continue
            previous = candidate.MAX_TIME_IN_SECONDS
            candidate.MAX_TIME_IN_SECONDS = seconds
            self.logger.info(
                f'Limite de tempo de {name} ajustado de {previous} s para {seconds} s.')

    @staticmethod
    def _read_topology_name(config) -> str:
        """Extrai o nome da topologia física da configuração."""
        try:
            return str(config.p_net_setting.topology.type)
        except Exception:
            return 'unknown'

    def _build_csv_path(self, config) -> str:
        """
        Constrói o caminho absoluto do arquivo de resultados por requisição.

        O caminho é absoluto porque o Hydra altera o diretório de trabalho do
        processo, o que invalidaria caminhos relativos.
        """
        package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        datasets_dir = os.path.join(package_root, 'datasets')
        os.makedirs(datasets_dir, exist_ok=True)
        run_id = str(config.experiment.run_id)
        fname = f'oracle_per_vnr-{self.topology_name}-seed_{config.experiment.seed}-{run_id}.csv'
        return os.path.join(datasets_dir, fname)

    # ------------------------------------------------------------------ #
    # Extração de características
    # ------------------------------------------------------------------ #

    def _extract_v_net_features(self, v_net) -> Dict[str, Any]:
        """Resume a requisição virtual em características escalares."""
        node_demands = np.array(
            v_net.get_node_attrs_data(self.counter.node_resource_attrs))
        link_demands = np.array(
            v_net.get_link_attrs_data(self.counter.link_resource_attrs))

        num_nodes = v_net.num_nodes
        num_links = v_net.num_links
        max_links = num_nodes * (num_nodes - 1) / 2 if num_nodes > 1 else 1

        node_demand_sum = float(node_demands.sum()) / max(self.counter.num_node_resource_attrs, 1)
        link_demand_sum = float(link_demands.sum())

        return {
            'v_net_num_nodes': num_nodes,
            'v_net_num_links': num_links,
            'v_net_lifetime': float(getattr(v_net, 'lifetime', float('nan'))),
            'v_net_node_demand': node_demand_sum,
            'v_net_link_demand': link_demand_sum,
            'v_net_total_demand': node_demand_sum + link_demand_sum,
            'v_net_connectivity': num_links / max_links,
            'v_net_avg_degree': (2 * num_links / num_nodes) if num_nodes else 0.0,
            'v_net_max_node_demand': float(node_demands.max()) if node_demands.size else 0.0,
            'v_net_max_link_demand': float(link_demands.max()) if link_demands.size else 0.0,
        }

    def _extract_p_net_features(self, p_net) -> Dict[str, Any]:
        """
        Resume o estado da rede física imediatamente antes da decisão.

        Estas características são idênticas para todos os candidatos, e é
        justamente essa identidade que torna o rótulo causalmente válido.
        """
        node_available = np.array(
            p_net.get_node_attrs_data(self.counter.node_resource_attrs))
        link_available = np.array(
            p_net.get_link_attrs_data(self.counter.link_resource_attrs))

        node_sum = float(node_available.sum())
        link_sum = float(link_available.sum())

        # Na primeira chamada a rede ainda se encontra intacta, pois o reinício
        # do ambiente acabou de restaurá-la a partir de init_p_net. Portanto o
        # total disponível nesse instante corresponde à capacidade total.
        if self._p_net_node_capacity is None:
            self._p_net_node_capacity = node_sum
            self._p_net_link_capacity = link_sum

        node_capacity = self._p_net_node_capacity or 1.0
        link_capacity = self._p_net_link_capacity or 1.0

        return {
            'p_net_node_available': node_sum,
            'p_net_link_available': link_sum,
            'p_net_node_util': 1.0 - node_sum / node_capacity,
            'p_net_link_util': 1.0 - link_sum / link_capacity,
            'p_net_min_node_available': float(node_available.min()) if node_available.size else 0.0,
            'p_net_min_link_available': float(link_available.min()) if link_available.size else 0.0,
        }

    # ------------------------------------------------------------------ #
    # Avaliação dos candidatos
    # ------------------------------------------------------------------ #

    def _evaluate_candidate(self, name: str, v_net, p_net) -> Dict[str, Any]:
        """
        Executa um candidato sobre uma cópia independente do estado.

        A cópia por candidato é obrigatória: as meta-heurísticas efetivam a
        solução na própria cópia da rede física por meio de
        ``controller.deploy``, e o MCTS realiza o mapeamento com ``inplace=True``.
        Sem a cópia, o segundo candidato receberia um estado já consumido pelo
        primeiro.
        """
        sub_instance = {'v_net': copy.deepcopy(v_net), 'p_net': copy.deepcopy(p_net)}

        start_time = time.perf_counter()
        try:
            solution = self.candidates[name].solve(sub_instance)
            failed_with_error = False
            error_description = ''
        except Exception as exc:  # noqa: BLE001 - falha de candidato não derruba a simulação
            solution = Solution.from_v_net(v_net)
            solution['result'] = False
            failed_with_error = True
            error_description = f'{type(exc).__name__}: {exc}'
            self.logger.warning(
                f'Candidato {name} lançou exceção na VNR {getattr(v_net, "id", "?")}: '
                f'{error_description}')
        solve_time_ms = (time.perf_counter() - start_time) * 1000

        # A pontuação é calculada sobre cópias. Counter.count_solution acumula
        # o campo 'v_net_demand' sobre o próprio valor anterior; pontuar sobre a
        # solução original a corromperia antes de o ambiente contá-la novamente.
        counted = self.counter.count_solution(copy.deepcopy(v_net), copy.deepcopy(solution))

        accepted = bool(counted.get('result', False))
        if accepted and counted.get('v_net_total_hard_constraint_violation', 0) > 0:
            # O ambiente rejeita soluções que violem restrições rígidas; o
            # oráculo antecipa essa rejeição para não escolher um vencedor que
            # seria descartado logo em seguida.
            accepted = False

        return {
            'name': name,
            'solution': solution,
            'accepted': accepted,
            'r2c_ratio': float(counted.get('v_net_r2c_ratio', 0.0)),
            'revenue': float(counted.get('v_net_revenue', 0.0)),
            'cost': float(counted.get('v_net_cost', 0.0)),
            'solve_time_ms': solve_time_ms,
            'place_result': bool(counted.get('place_result', False)),
            'route_result': bool(counted.get('route_result', False)),
            'description': error_description or str(counted.get('description', '')),
            'failed_with_error': failed_with_error,
        }

    def _score_candidate(self, evaluation: Dict[str, Any]):
        """
        Devolve a chave de ordenação de um candidato. O candidato de maior
        chave é o escolhido pelo oráculo, e essa escolha define o significado
        científico do teto medido.

        O critério é lexicográfico, em três níveis:

        1. **Aceitação.** Constitui o critério primário, pois a taxa de
           aceitação é a métrica que o teto se propõe a limitar. Como
           ``False < True`` em Python, o candidato que aceita a requisição
           sempre precede aquele que a rejeita.
        2. **Razão entre receita e custo.** Desempata entre os candidatos que
           aceitam a requisição. Valores maiores correspondem a mapeamentos
           mais econômicos, que preservam recursos para as chegadas futuras.
           Cabe observar que esse desempate não viola a miopia do oráculo: a
           decisão continua a ser tomada sem qualquer conhecimento das
           requisições vindouras, apenas privilegiando a solução que consome
           menos recursos para atender a requisição corrente.
        3. **Tempo de execução, negado.** Desempate final. A negação é
           necessária porque a ordenação busca o valor máximo, ao passo que o
           menor tempo é o desejável.

        Quando nenhum candidato aceita a requisição, todos apresentam
        ``accepted`` falso e razão nula, de sorte que a comparação recai sobre
        o tempo. A escolha é, nesse caso, irrelevante para o ambiente, uma vez
        que toda rejeição consome recursos nulos; o campo ``winner`` é
        registrado como ``none`` em ``solve``.

        O dicionário recebido contém, entre outros campos:
            - ``accepted`` (bool): a requisição foi aceita por este candidato.
            - ``r2c_ratio`` (float): razão entre receita e custo do mapeamento.
            - ``revenue`` (float): receita obtida com a requisição.
            - ``cost`` (float): custo dos recursos consumidos.
            - ``solve_time_ms`` (float): tempo de execução do candidato.

        Args:
            evaluation: o resultado da avaliação de um candidato.

        Returns:
            Uma chave comparável na qual o maior valor corresponde ao melhor
            candidato.
        """
        return (
            bool(evaluation['accepted']),
            float(evaluation['r2c_ratio']),
            -float(evaluation['solve_time_ms']),
        )

    # ------------------------------------------------------------------ #
    # Registro em arquivo
    # ------------------------------------------------------------------ #

    def _write_rows(self, rows: List[Dict[str, Any]]) -> None:
        """Anexa as linhas ao arquivo de resultados, criando o cabeçalho."""
        write_header = not self._csv_initialized and not os.path.exists(self.csv_path)
        with open(self.csv_path, 'a+', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES, extrasaction='ignore')
            if write_header:
                writer.writeheader()
            writer.writerows(rows)
        self._csv_initialized = True

    # ------------------------------------------------------------------ #
    # Interface do solucionador
    # ------------------------------------------------------------------ #

    def solve(self, instance: dict) -> Solution:
        v_net, p_net = instance['v_net'], instance['p_net']

        # O estado é capturado antes de qualquer tentativa, de modo que as
        # características registradas sejam as mesmas enfrentadas por todos os
        # candidatos.
        v_net_features = self._extract_v_net_features(v_net)
        p_net_features = self._extract_p_net_features(p_net)

        evaluations = [self._evaluate_candidate(name, v_net, p_net)
                       for name in self.candidate_names]

        best = max(evaluations, key=self._score_candidate)
        num_accepted = sum(1 for e in evaluations if e['accepted'])
        total_time_ms = sum(e['solve_time_ms'] for e in evaluations)

        # Se nenhum candidato aceitou a requisição, a escolha é irrelevante
        # para o ambiente, pois toda rejeição consome recursos nulos. O rótulo
        # devolvido ao ambiente registra essa condição como 'none'.
        #
        # A marcação em arquivo, no entanto, recai sempre sobre o candidato de
        # maior pontuação, ainda que nenhum tenha aceitado a requisição. Desse
        # modo o invariante "exatamente uma linha vencedora por requisição" se
        # mantém, e os consumidores dos dados distinguem os dois casos pela
        # coluna 'num_candidates_accepted'.
        winner_name = best['name'] if best['accepted'] else 'none'
        marked_winner = best['name']

        common = {
            'topology': self.topology_name,
            'seed': self.config.experiment.seed,
            'v_net_id': getattr(v_net, 'id', None),
            'event_id': self.recorder.state.get('event_id'),
            'event_time': self.recorder.state.get('event_time'),
            'inservice_count': self.recorder.state.get('inservice_count'),
            'num_candidates_accepted': num_accepted,
            'oracle_total_solve_time_ms': total_time_ms,
            **v_net_features,
            **p_net_features,
        }
        rows = [
            {
                **common,
                'algorithm': e['name'],
                'result': e['accepted'],
                'v_net_revenue': e['revenue'],
                'v_net_cost': e['cost'],
                'v_net_r2c_ratio': e['r2c_ratio'],
                'solve_time_ms': e['solve_time_ms'],
                'place_result': e['place_result'],
                'route_result': e['route_result'],
                'description': e['description'],
                'is_winner': e['name'] == marked_winner,
            }
            for e in evaluations
        ]
        self._write_rows(rows)

        solution = best['solution']
        # O tempo registrado é o do vencedor, ou seja, o custo que um seletor
        # real pagaria ao escolher corretamente. O custo de executar todos os
        # candidatos permanece disponível em 'oracle_total_solve_time_ms'.
        solution['v_net_solve_time'] = best['solve_time_ms']
        solution['oracle_selected_algorithm'] = winner_name
        return solution
