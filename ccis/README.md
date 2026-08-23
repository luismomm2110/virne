# CCIS — Oráculo Guloso para Seleção de Algoritmos de Mapeamento de Redes Virtuais

Este pacote implementa o **oráculo guloso**, que estabelece o teto de desempenho
alcançável por um seletor míope de algoritmos de mapeamento de redes virtuais
(*Virtual Network Embedding*, VNE). Todo o código novo e todos os resultados
produzidos residem neste diretório.

## 1. Motivação

O objetivo do trabalho consiste em treinar uma árvore de decisão que escolha, a
cada requisição de rede virtual (*Virtual Network Request*, VNR), o algoritmo de
mapeamento mais adequado. Para afirmar que a árvore obtém bom desempenho, é
necessário dispor de um teto, ou seja, do valor máximo que um seletor honesto
poderia atingir.

O oráculo anteriormente empregado na pipeline de aprendizado de máquina
(`apresentacao/machine_learning/calculate_true_oracle.py` e a rotulagem em
`apresentacao/machine_learning/pipeline/2_prepare_dataset.py`) não constitui um
teto válido. Aquele procedimento agrupa resultados pela chave
`(topologia, semente, identificador da requisição)` provenientes de **simulações
independentes**, uma para cada algoritmo. A partir da primeira requisição aceita,
os estados da rede física divergem entre as simulações. Quando o rótulo afirma
que, para determinada requisição, o melhor algoritmo é `ga_meta`, essa medição
ocorreu sobre um estado da rede física que nenhum dos demais algoritmos chegou a
enfrentar. A comparação alegada como direta é, portanto, causalmente inválida, e
o valor resultante não configura um limite superior alcançável, mas sim a
agregação de trajetórias mutuamente inconsistentes.

O oráculo guloso corrige essa deficiência. Trata-se de **uma única simulação** na
qual, a cada chegada de requisição, todos os algoritmos candidatos são
executados sobre **exatamente o mesmo estado** da rede física; o melhor
resultado é selecionado e efetivado; a simulação prossegue. A trajetória
resultante é coerente, pois o estado da rede física em cada instante decorre
causalmente das escolhas anteriores.

Duas propriedades delimitam a interpretação do valor obtido:

- **Constitui um teto para seletores míopes.** O oráculo conhece o desfecho de
  todos os candidatos no passo corrente, informação indisponível à árvore de
  decisão, porém desconhece as chegadas futuras. Nenhum seletor que decida
  requisição a requisição pode superá-lo.
- **Não constitui o ótimo global da trajetória.** A escolha gulosa pode consumir
  recursos de maneira a bloquear requisições futuras, de modo que um seletor
  dotado de previsão poderia superá-lo. Essa limitação deve ser declarada de
  forma explícita no texto acadêmico.

A grandeza de interesse é a **lacuna** entre a taxa de aceitação do melhor
algoritmo fixo e a do oráculo guloso, pois essa diferença corresponde exatamente
à margem passível de ser capturada pela seleção dinâmica.

## 2. Por que a implementação é enxuta

A arquitetura do virne acomoda o mecanismo sem qualquer modificação em seu
núcleo, em virtude de três características verificadas no código:

1. `SolutionStepEnvironment.get_observation` (`virne/core/environment.py`)
   entrega ao solucionador cópias profundas da rede virtual e da rede física. O
   solucionador nunca manipula a rede física autoritativa.
2. `SolutionStepEnvironment.step` (`virne/core/environment.py`) é o responsável
   por efetivar a solução recebida por meio de `controller.deploy`. Basta,
   portanto, que o solucionador devolva a melhor solução.
3. `SolverRegistry` (`virne/solver/base_solver.py`) permite registrar um
   metassolucionador que instancie os demais internamente.

O oráculo guloso consiste, assim, em **um único solucionador novo**.

## 3. Estrutura do pacote

```
ccis/
├── README.md                   este documento
├── solver/greedy_oracle.py     o metassolucionador
├── settings/                   configurações do Hydra
├── main_ccis_oracle.py         ponto de entrada
├── run_oracle_experiments.py   executor das simulações
├── build_oracle_dataset.py     construção do conjunto de treino
├── analyze_oracle.py           tabelas e resumo dos resultados
├── tests/                      teste do critério de seleção
├── datasets/                   saída: resultados por requisição
└── results/                    saída: tabelas, resumo e simulações
```

Os grupos de configuração compartilhados (`learning.yaml`, `v_sim_setting/` e
`p_net_setting/`) são referenciados por ligações simbólicas para
`apresentacao/settings/`, de modo que as condições experimentais permaneçam
idênticas às das linhas de base e não sofram divergência por duplicação.

## 4. Critério de seleção

O vencedor de cada requisição é determinado por um critério lexicográfico de
três níveis, implementado em `GreedyOracleSolver._score_candidate`:

1. **Aceitação.** Critério primário, pois a taxa de aceitação é a métrica que o
   teto se propõe a limitar.
2. **Razão entre receita e custo.** Desempata entre os candidatos que aceitam a
   requisição, privilegiando o mapeamento mais econômico, que preserva recursos
   para as chegadas futuras. Esse desempate não viola a miopia do oráculo, uma
   vez que a decisão permanece alheia às requisições vindouras.
3. **Tempo de execução.** Desempate final, favorecendo o candidato mais rápido.

Quando nenhum candidato aceita a requisição, a escolha é irrelevante para o
ambiente, pois toda rejeição consome recursos nulos; o vencedor é registrado
como `none`.

O critério é verificado por `ccis/tests/test_score_candidate.py`, que carrega a
função efetivamente executada e dispensa a instalação das dependências pesadas:

```bash
python ccis/tests/test_score_candidate.py
```

## 5. Modo de uso

### 5.0 Ambiente de execução

Os roteiros exigem o ambiente conda `virne` (Python 3.10), que reúne `hydra`,
`omegaconf`, `ortools`, `networkx`, `pandas` e a pilha do PyTorch:

```bash
conda activate virne
```

O arquivo `environment.yml` na raiz do repositório encontra-se corrompido, pois
contém apenas uma mensagem de erro do interpretador de comandos em lugar da
especificação exportada. A lista de dependências consta de `pyproject.toml`,
observando-se que os endereços dos pacotes do PyTorch Geometric ali declarados
correspondem a Linux e Python 3.10, e não se aplicam a macOS.

O teste do critério de seleção, descrito na Seção 4, dispensa esse ambiente e
executa com qualquer interpretador que disponha de `numpy`.

### 5.1 Validação do mecanismo

```bash
python ccis/run_oracle_experiments.py --smoke
```

Executa uma semente, três heurísticas rápidas e vinte requisições. Serve para
confirmar que a simulação se completa e que o arquivo de resultados é gerado.

### 5.2 Execução completa

```bash
python ccis/run_oracle_experiments.py
```

**Advertência quanto ao custo.** O oráculo executa todos os candidatos a cada
requisição. O algoritmo `mip` possui limite de dez segundos por instância
(`virne/solver/exact/mip.py`) e o `mcts` emprega orçamento de cem simulações;
ambos dominam o tempo total. Recomenda-se medir uma execução reduzida antes de
escalar para o conjunto completo de topologias e sementes.

### 5.3 Construção do conjunto de treino e análise

```bash
python ccis/build_oracle_dataset.py
python ccis/analyze_oracle.py
```

## 6. Arquivos produzidos

| Arquivo | Conteúdo |
|---|---|
| `datasets/oracle_per_vnr-*.csv` | Uma linha por requisição e candidato, com o estado da rede física idêntico entre os candidatos de uma mesma requisição. |
| `datasets/oracle_long.csv` | Concatenação dos arquivos anteriores. |
| `datasets/oracle_dataset.csv` | Uma linha por requisição, com as características observáveis e o rótulo `best_algorithm`. Entrada direta do classificador. |
| `results/oracle_main_comparison.csv` | Tabela principal: melhor algoritmo fixo, oráculo e a lacuna entre ambos. |
| `results/oracle_winner_distribution.csv` | Frequência com que cada algoritmo vence. |
| `results/oracle_disagreement.csv` | Fração de requisições nas quais os candidatos discordam. |
| `results/oracle_computational_cost.csv` | Custo de executar todos os candidatos comparado ao custo do vencedor. |
| `results/oracle_summary.json` | Todas as tabelas em formato estruturado. |

A coluna `is_decisive`, em `oracle_dataset.csv`, identifica as requisições nas
quais parte dos candidatos aceita e parte rejeita. Somente nessas a escolha
altera o desfecho, e é essa fração que dimensiona o problema de decisão de fato
enfrentado pela árvore.

## 7. Observações sobre a fidelidade experimental

### 7.1 Capacidade de processamento dos comutadores

Os roteiros existentes em `apresentacao/algoritmos/` alteram `system.env.p_net`
após a construção do sistema, com o propósito de atribuir capacidade nula de
processamento aos comutadores. Contudo, `BaseEnvironment.__init__`
(`virne/core/environment.py`) já copiou a rede física em `init_p_net`, e
`reset()` a restaura a partir dessa cópia antes da primeira requisição, de modo
que a alteração é descartada. As linhas de base já produzidas foram obtidas, em
consequência, sem comutadores dedicados exclusivamente ao roteamento. O oráculo
reproduz deliberadamente a mesma condição, para que a comparação seja legítima.

### 7.2 Dupla contagem da solução

`Counter.count_solution` (`virne/core/counter.py`) contém a atribuição
`solution['v_net_demand'] = solution['v_net_node_demand'] + solution['v_net_demand']`,
que acumula sobre o próprio valor anterior. Como o oráculo necessita da razão
entre receita e custo para ordenar os candidatos, e o ambiente invocará a mesma
contagem sobre a solução vencedora, a pontuação é realizada sobre **cópias** das
soluções. Esse cuidado mantém o comportamento do vencedor idêntico ao de uma
execução isolada.

### 7.3 Ausência de registro adicional

`Recorder.get_record` (`virne/core/recorder.py`) indexa a memória diretamente
pelo identificador do evento, pressupondo um registro por evento. Qualquer
chamada adicional a `add_record` dessincronizaria a liberação de recursos. Por
esse motivo, os resultados por requisição são gravados em arquivo próprio, sem
qualquer interferência no registrador do virne.

## 8. Verificação

1. **Registro do solucionador.**
   ```bash
   python -c "import ccis.solver; from virne.solver.base_solver import SolverRegistry; print('greedy_oracle' in SolverRegistry.list_registered())"
   ```
2. **Não regressão do vencedor.** Executar `pl_rank` isoladamente com semente
   fixa e requisições carregadas do disco; em seguida executar o oráculo com
   `solver.oracle_candidates=[pl_rank]` sob as mesmas condições. As duas
   simulações devem produzir taxa de aceitação idêntica, o que comprova que o
   metassolucionador não perturba o ambiente nem corrompe a contagem.
3. **Monotonicidade do teto.** A taxa de aceitação do oráculo deve ser maior ou
   igual à de qualquer candidato isolado sobre a mesma trajetória. O roteiro
   `analyze_oracle.py` verifica essa condição e sinaliza eventual violação.
4. **Conservação de recursos.** As asserções já presentes em
   `SolutionStepEnvironment.step` validam que os recursos consumidos
   correspondem aos custos declarados na solução, e funcionam como rede de
   segurança adicional.
