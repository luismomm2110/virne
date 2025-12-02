# Machine Learning Pipeline para Seleção Dinâmica de Algoritmos VNE

Pipeline completo de Machine Learning para treinar um modelo **XGBoost** que seleciona dinamicamente o melhor algoritmo VNE para cada requisição.

## Estrutura

```
machine_learning/
├── 1_extract_vnr_data.py          # Extrai dados de VNRs das simulações
├── 2_prepare_dataset.py           # Feature engineering e criação de labels
├── 3_train_xgboost.py             # Treina XGBoost com CV ⭐ ATUALIZADO
├── 5_online_simulator.py          # Simulador online com seleção dinâmica
├── 6_compare_with_baselines.py    # Compara com algoritmos fixos
│
├── models/                         # Modelos treinados (.pkl)
├── datasets/                       # Datasets processados
└── results/                        # Resultados e visualizações
```

## Pipeline de Execução

### 1. Extração de Dados

Extrai dados de ~14,000 VNRs de todas as simulações:

```bash
cd apresentacao/machine_learning
python 1_extract_vnr_data.py
```

**Output**: `datasets/vnr_raw_data.csv`

### 2. Preparação do Dataset

Cria features engenheiradas e labels (melhor algoritmo por VNR):

```bash
python 2_prepare_dataset.py
```

**Outputs**:
- `datasets/vnr_features.csv` (dataset completo)
- `datasets/train.csv` (seeds 0-2)
- `datasets/val.csv` (seed 3)
- `datasets/test.csv` (seed 4)

### 3. Treinamento do XGBoost

Treina modelo com Grid Search + Cross-Validation:

```bash
python 3_train_xgboost.py
```

**Outputs**:
- `models/xgb_best_overall_model.pkl` (modelo treinado)
- `models/xgb_best_overall_label_encoder.pkl` (encoder de labels)
- `results/confusion_matrix.png`
- `results/feature_importance.png`
- `results/cv_scores.png` (curvas de aprendizado)
- `results/feature_importance.txt` (ranking completo)

### 4. Simulação Online

Roda simulação com seleção dinâmica de algoritmo:

```bash
# Simular com Dynamic Selector
python 5_online_simulator.py

# Para simular com algoritmo fixo (baseline):
# Modificar main() para usar FixedAlgorithmSimulator
```

**Output**: `results/online_sim_dynamic_seed_0.csv`

### 5. Comparação com Baselines

Compara Dynamic Selector com algoritmos fixos:

```bash
python 6_compare_with_baselines.py
```

**Outputs**:
- `results/comparison_boxplots.png`
- `results/acceptance_vs_time_scatter.png`
- `results/comparison_summary.csv`

## Features Utilizadas

### Features de VNR
- `v_net_num_nodes`: Número de nós da VNR
- `v_net_num_edges`: Número de links
- `v_net_size_ratio`: Razão do tamanho (VNR / P-Net)
- `v_net_demand_per_node`: Demanda média por nó
- `v_net_demand_per_link`: Demanda média por link
- `v_net_connectivity`: Densidade do grafo
- `v_net_lifetime`: Tempo de vida da VNR

### Features de Estado da Rede Física
- `p_net_available_resource`: Recursos disponíveis totais
- `p_net_node_util`: Utilização dos nós (%)
- `p_net_link_util`: Utilização dos links (%)
- `p_net_overall_util`: Utilização geral

### Features de Estado do Sistema
- `inservice_count`: Número de VNRs ativas
- `system_load`: Carga do sistema (%)
- `num_running_p_net_nodes`: Nós físicos em uso

### Features Temporais
- `event_time`: Tempo do evento
- `time_of_day`: Hora do dia (mod 100)

### Features Categóricas
- `topology_encoded`: Tree (0) ou Fat-Tree (1)

## Labels (Targets)

Três tipos de labels são criados para cada VNR:

1. **`best_for_acceptance`**: Algoritmo que aceita quando outros rejeitam (prioriza aceitação)
2. **`best_for_time`**: Algoritmo mais rápido entre os que aceitam (prioriza velocidade)
3. **`best_overall`**: Balanceado (0.7 × acceptance + 0.3 × speed)

Por padrão, treinamos com `best_overall`.

## Métricas de Avaliação

### Durante Treinamento
- Accuracy
- F1-Score (weighted)
- Confusion Matrix
- Feature Importance

### Durante Simulação
- Acceptance Rate (%)
- Average Time per VNR (s)
- Total Running Time (s)
- Algorithm Selection Distribution

### Comparação com Baselines
- Boxplots de Acceptance Rate e Time
- Scatter plot: Acceptance vs Time
- Regret vs Oracle (melhor possível)
- Testes estatísticos (t-test)

## Estratégia de Split

**Por Seed** (padrão):
- Train: seeds 0, 1, 2 (60%)
- Val: seed 3 (20%)
- Test: seed 4 (20%)

**Vantagens**:
- Mais realista (simula novos cenários)
- Evita data leakage entre VNRs da mesma simulação

## Hyperparameters

```python
{
    'max_depth': [8, 10, 12, 15, 20],
    'min_samples_split': [20, 30, 50, 100],
    'min_samples_leaf': [10, 20, 30, 50],
    'criterion': ['gini', 'entropy'],
    'class_weight': ['balanced', None]
}
```

Melhor combinação é escolhida via Grid Search com 4-fold Cross-Validation.

## Resultados Esperados

### Acceptance Rate
- **Dynamic Selector**: Similar ou superior aos melhores algoritmos fixos
- **Regret**: < 5% do Oracle

### Time
- **Dynamic Selector**: Mais rápido que MIP, comparável a GA/MCTS
- Evita usar MIP em casos fáceis

### Trade-off
- Balanceia aceitação e velocidade automaticamente
- Adaptativo ao estado da rede

## Exemplo de Uso

```python
# Carregar modelo treinado
import pickle
with open('models/xgb_best_overall_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Carregar label encoder
with open('models/xgb_best_overall_label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

# Extrair features de uma VNR
features = extract_features(vnr, p_net, current_time)

# Selecionar algoritmo
algo_encoded = model.predict([features])[0]
selected_algo = label_encoder.inverse_transform([algo_encoded])[0]
print(f"Algoritmo selecionado: {selected_algo}")

# Executar o algoritmo
solver = get_solver(selected_algo)
success = solver.solve(vnr, p_net)
```

## Visualizações Geradas

1. **Confusion Matrix**: Onde o modelo acerta/erra na seleção
2. **Feature Importance**: Quais features mais influenciam a decisão
3. **Tree Visualization**: Representação gráfica da árvore (primeiros níveis)
4. **Comparison Boxplots**: Acceptance Rate e Time por método
5. **Scatter Plot**: Trade-off aceitação vs tempo

## Dependências

```bash
pip install pandas numpy scikit-learn xgboost matplotlib seaborn scipy tqdm
```

**Nota**: XGBoost adicionado (vs Decision Tree original)

## Referências

Veja `ML_PIPELINE_PROPOSAL.md` para detalhes completos da proposta.

## Contato

Para dúvidas ou sugestões, veja a documentação completa em `ML_PIPELINE_PROPOSAL.md`.
