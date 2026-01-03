# Correção de Acurácia - Resultados Finais

**Data:** Gerado automaticamente
**Modelos:** Árvores de Decisão Balanceadas

---

## Resumo Executivo

Após aplicação de técnicas avançadas de balanceamento de classes, os modelos de árvore de decisão apresentaram melhoria significativa em relação aos modelos não balanceados.

---

## Resultados Antes vs Depois do Balanceamento

### Acurácia (Top-1)

| Objetivo | ANTES | DEPOIS | Melhoria |
|----------|-------|--------|----------|
| **RAC** (Taxa de Aceitação) | 48,30% | **67,26%** | **+18,96pp** (+39,3%) |
| **LAR** (Receita Média) | 37,60% | **48,14%** | **+10,54pp** (+28,0%) |
| **LRC** (Razão Receita-Custo) | 32,09% | **54,46%** | **+22,37pp** (+69,7%) |

### F1-Score (Weighted)

| Objetivo | ANTES | DEPOIS | Melhoria |
|----------|-------|--------|----------|
| **RAC** | 0,41 | **0,68** | **+65,9%** |
| **LAR** | 0,34 | **0,48** | **+41,2%** |
| **LRC** | 0,32 | **0,55** | **+71,9%** |

### Top-3 Accuracy

| Objetivo | ANTES | DEPOIS | Melhoria |
|----------|-------|--------|----------|
| **RAC** | 70,50% | **85,90%** | **+15,40pp** |
| **LAR** | 72,12% | **79,09%** | **+6,97pp** |
| **LRC** | 61,59% | **83,95%** | **+22,36pp** |

---

## Comparação com Baseline (Algoritmo Fixo)

O baseline foi definido como o algoritmo mais frequentemente ótimo no conjunto de teste.

| Objetivo | Algoritmo Baseline | Acurácia Baseline | Árvore Balanceada | Melhoria | Ganho Relativo |
|----------|-------------------|-------------------|-------------------|----------|----------------|
| **RAC** | GA_Meta | 34,36% | **67,26%** | **+32,90pp** | **+95,8%** |
| **LRC** | PL_Rank | 27,23% | **54,46%** | **+27,23pp** | **+100,0%** |
| **LAR** | GA_Meta | 22,85% | **48,14%** | **+25,29pp** | **+110,7%** |

**Melhoria média:** +28,5 pontos percentuais (~2x o baseline)

---

## Métricas Detalhadas por Objetivo

### RAC (Request Acceptance Rate)

```
Acurácia:        67,26%
F1-Score (Wt):   0,68
F1-Score (Macro): 0,56
Top-2 Accuracy:  82,66%
Top-3 Accuracy:  85,90%
```

**F1-Score por Classe (RAC):**

| Algoritmo | Precisão | Recall | F1-Score | Support |
|-----------|----------|--------|----------|---------|
| GA_Meta | 0,73 | 0,74 | **0,73** | 212 |
| MCTS | 0,78 | 0,72 | **0,75** | 155 |
| PL_Rank | 0,77 | 0,66 | **0,71** | 56 |
| D_Round | 0,61 | 0,59 | **0,60** | 95 |
| MIP | 0,49 | 0,57 | **0,53** | 54 |
| SA_Meta | 0,43 | 0,56 | **0,49** | 34 |
| RW_Rank_BFS | 0,67 | 0,25 | **0,36** | 8 |
| PSO_Meta | 0,22 | 0,67 | **0,33** | 3 |

---

### LAR (Long-Term Average Revenue)

```
Acurácia:        48,14%
F1-Score (Wt):   0,48
F1-Score (Macro): 0,46
Top-2 Accuracy:  67,59%
Top-3 Accuracy:  79,09%
```

**F1-Score por Classe (LAR):**

| Algoritmo | Precisão | Recall | F1-Score | Support |
|-----------|----------|--------|----------|---------|
| MCTS | 0,49 | 0,54 | **0,51** | 102 |
| PL_Rank | 0,54 | 0,64 | **0,58** | 80 |
| GA_Meta | 0,49 | 0,48 | **0,49** | 141 |
| SA_Meta | 0,59 | 0,44 | **0,51** | 72 |
| D_Round | 0,46 | 0,42 | **0,44** | 67 |
| MIP | 0,45 | 0,41 | **0,43** | 117 |
| RW_Rank_BFS | 0,33 | 0,39 | **0,36** | 18 |
| PSO_Meta | 0,29 | 0,40 | **0,33** | 20 |

---

### LRC (Long-Term Revenue-to-Cost)

```
Acurácia:        54,46%
F1-Score (Wt):   0,55
F1-Score (Macro): 0,46
Top-2 Accuracy:  74,55%
Top-3 Accuracy:  83,95%
```

**F1-Score por Classe (LRC):**

| Algoritmo | Precisão | Recall | F1-Score | Support |
|-----------|----------|--------|----------|---------|
| SA_Meta | 0,68 | 0,73 | **0,70** | 125 |
| PL_Rank | 0,67 | 0,56 | **0,61** | 168 |
| MIP | 0,67 | 0,50 | **0,57** | 110 |
| PSO_Meta | 0,45 | 0,59 | **0,51** | 22 |
| GA_Meta | 0,38 | 0,53 | **0,44** | 72 |
| MCTS | 0,48 | 0,41 | **0,44** | 78 |
| RW_Rank_BFS | 0,20 | 0,39 | **0,27** | 28 |
| D_Round | 0,18 | 0,14 | **0,16** | 14 |

---

## Técnicas de Treinamento Aplicadas

### 1. Pesos de Classe Customizados (Estratégia Agressiva)

Em vez do balanceamento padrão do scikit-learn, utilizamos:

$$w_i = \frac{1}{\sqrt{f_i}}$$

Onde $f_i$ é a frequência relativa da classe $i$.

**Exemplo de pesos aplicados (RAC):**

| Classe | Amostras | Peso Aplicado |
|--------|----------|---------------|
| PSO_Meta | 17 | **10,00x** |
| RW_Rank_BFS | 39 | **6,60x** |
| SA_Meta | 159 | **3,27x** |
| MIP | 251 | **2,60x** |
| PL_Rank | 259 | **2,56x** |
| D_Round | 442 | **1,96x** |
| MCTS | 724 | **1,53x** |
| GA_Meta | 987 | **1,31x** |

### 2. Hiperparâmetros Ajustados

| Parâmetro | Valor Anterior | Valor Atual | Justificativa |
|-----------|----------------|-------------|---------------|
| max_depth | 5 | **10** | Mais profundidade para classes minoritárias |
| min_samples_leaf | 10 | **3** | Permite folhas menores |
| min_samples_split | 20 | **6** | Permite splits com menos amostras |
| criterion | gini | gini | Mantido |
| class_weight | balanced | **custom** | Pesos agressivos |

### 3. Métricas de Avaliação

- **F1-Score Ponderado**: Média ponderada pelo suporte de cada classe
- **F1-Score Macro**: Média aritmética (trata todas as classes igualmente)
- **Top-K Accuracy**: Verifica se o algoritmo ótimo está entre os K mais prováveis

---

## Arquivos Gerados

- `models/decision_trees_balanced.pkl` - Modelos treinados
- `models/tree_results_balanced.json` - Métricas detalhadas
- `models/tree_balanced_*.png` - Visualizações das árvores
- `models/confusion_balanced_*.png` - Matrizes de confusão
- `models/evaluation_confusion_matrix_*.png` - Matrizes de confusão (avaliação)
- `models/evaluation_metrics_*.png` - Gráficos de métricas

---

## Conclusões

1. **Técnicas de balanceamento são essenciais**: Classes minoritárias que antes tinham F1=0 agora têm valores positivos.

2. **Melhoria significativa sobre baseline**: Aproximadamente 2x a acurácia do algoritmo fixo.

3. **Top-3 Accuracy é alta**: Entre 79% e 86%, indicando que o algoritmo ótimo está quase sempre entre as principais predições.

4. **Trade-off interpretabilidade vs. performance**: Árvores de decisão mantêm interpretabilidade com performance competitiva.

---

## Para Atualização do Artigo

Valores a usar no artigo:

```
- Top-3 Accuracy: 79,1% a 85,9%
- Melhoria média vs baseline: +28,5pp (~2x)
- F1-Score Ponderado: RAC 0,68, LRC 0,55, LAR 0,48
- F1-Score Macro: RAC 0,56, LRC 0,46, LAR 0,46
- Acurácia: RAC 67,26%, LRC 54,46%, LAR 48,14%
```

