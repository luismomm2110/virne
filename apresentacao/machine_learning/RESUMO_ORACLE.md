# Oracle: Resumo Executivo - Todas as 5 Métricas

## O que é o Oracle?

O **Oracle** é o desempenho teórico máximo se conseguíssemos **sempre escolher o algoritmo correto** para cada VNR em cada métrica específica.

É uma métrica **a posteriori** - olhamos para o histórico de execuções e perguntamos: "Se tivéssemos sempre escolhido um algoritmo que otimizasse [métrica], qual seria nosso resultado?"

---

## Resultados Finais - Todas as 5 Métricas

### 1. RAC (Request Acceptance Rate)
Taxa de aceitação de VNRs - % de requisições aceitas

| Topologia | Oracle RAC | Model Top-3 | Gap | Insight |
|-----------|-----------|------------|-----|---------|
| **Tree** | 97.85% | 93.37% | +4.48% | ✓ Modelo aprende bem |
| **Fat-Tree** | 100.00% | 79.30% | +20.70% | ✗ Modelo tem dificuldade |
| **Waxman-16** | 99.52% | 85.65% | +13.87% | ≈ Modelo performance média |

**Interpretação:**
- Fat-Tree: Oracle perfeito (100%), mas modelo só acerta 79.3% → há espaço para melhoria
- Waxman-16: Oracle 99.5%, modelo 85.7% → bom espaço de melhoria
- Tree: Oracle 97.9%, modelo 93.4% → modelo já aprende bem

---

### 2. LRC (Long-Term Revenue-to-Cost Ratio)
Eficiência financeira - Receita / Custo (quanto maior, melhor)

| Topologia | Oracle LRC | Model Accuracy | Gap | Insight |
|-----------|-----------|------------|-----|---------|
| **Tree** | 0.82 | 73.48% | -27.76 pp | ✓ Modelo aprende bem |
| **Fat-Tree** | 0.90 | 39.21% | -51.21 pp | ✗ Modelo tem muita dificuldade |
| **Waxman-16** | 0.83 | 57.89% | -25.60 pp | ≈ Modelo performance baixa |

**O que significa:**
- **Tree**: Oracle 0.82 receita/custo, modelo acerta 73.48% das classificações
- **Fat-Tree**: Oracle 0.90 (melhor eficiência), mas modelo só acerta 39.21% → CRÍTICO
- **Waxman-16**: Oracle 0.83, modelo 57.89% → necessário melhorar

**Observação:** LRC é métrica desafiadora com imbalance de classes. Fat-Tree tem performance crítica (39.21%) - necessário investigar feature engineering e balanceamento de dados.

---

### 3. LAR (Long-Term Average Revenue)
Receita total por VNR aceito (quanto maior, melhor)

| Topologia | Oracle LAR | Model Accuracy | Gap | Insight |
|-----------|-----------|------------|-----|---------|
| **Tree** | 70.57 | 58.56% | -29.28 pp | ≈ Modelo performance baixa |
| **Fat-Tree** | 456.08 | 25.99% | -420.51 pp | ✗ Modelo tem muita dificuldade |
| **Waxman-16** | 323.04 | 50.72% | -271.58 pp | ✗ Modelo tem dificuldade |

**O que significa:**
- **Tree**: Oracle 70.57 receita média, modelo acerta 58.56% das classificações
- **Fat-Tree**: Oracle 456.08 (6.5x maior), mas modelo só acerta 25.99% → CRÍTICO
- **Waxman-16**: Oracle 323.04, modelo 50.72% → necessário melhorar

**Por que os modelos têm dificuldade?**
- LAR é uma métrica de regressão multi-classe (3 principais algoritmos: GA, MIP, RW)
- Trade-offs complexos entre algoritmos → decisão não é trivial
- Fat-Tree tem performance crítica (25.99%) - classe imbalance severo

**Observação:** LAR é a métrica com PIOR performance do modelo (25.99% em Fat-Tree) - necessário revisar estratégia de seleção de features e balanceamento.

---

### 4. AST (Average Solving Time)
Tempo médio de solução (quanto menor, melhor)

| Topologia | Oracle AST (ms) | Model Accuracy | Gap | Insight |
|-----------|-----------|------------|-----|---------|
| **Tree** | 0.29 | 100.00% | 0.00 pp | ✓✓ Modelo perfeito! |
| **Fat-Tree** | 0.02 | 95.15% | -4.85 pp | ✓ Modelo excelente |
| **Waxman-16** | 0.23 | 99.52% | -0.48 pp | ✓✓ Modelo praticamente perfeito |

**O que significa:**
- **Tree**: Oracle 0.29 ms, modelo acerta 100% das classificações → PERFEITO
- **Fat-Tree**: Oracle 0.02 ms (14x mais rápido), modelo 95.15% → excelente
- **Waxman-16**: Oracle 0.23 ms, modelo 99.52% → praticamente perfeito

**Por que os modelos têm ótimo desempenho?**
- AST é uma métrica com apenas 2 principais algoritmos: pl_rank vs rw_rank_bfs
- Problema bem definido e binário → fácil de aprender
- Separação clara entre algoritmos rápidos e lentos

**Observação:** AST é a métrica com MELHOR performance do modelo (95-100% acurácia) - problema bem estruturado. Não precisa de melhorias.

---

### 5. BALANCED (0.8×Revenue - 0.2×Time)
Combinação ponderada: 80% receita, 20% tempo

| Topologia | Oracle BALANCED | Model Accuracy | Gap | Insight |
|-----------|-----------|------------|-----|---------|
| **Tree** | 56.39 | 75.14% | +18.75 pp | ✓ Modelo aprende bem |
| **Fat-Tree** | 364.80 | 27.75% | -337.05 pp | ✗ Modelo tem muita dificuldade |
| **Waxman-16** | 258.37 | 46.89% | -211.48 pp | ✗ Modelo tem dificuldade |

**O que significa:**
- **Tree**: Oracle 56.39 (combined score), modelo acerta 75.14% → bom desempenho
- **Fat-Tree**: Oracle 364.80 (6.5x melhor que Tree), modelo 27.75% → CRÍTICO
- **Waxman-16**: Oracle 258.37, modelo 46.89% → performance baixa

**Por que Fat-Tree tem tanta dificuldade?**
- BALANCED combina dois objetivos conflitantes: maximizar receita (80%) e minimizar tempo (20%)
- Fat-Tree tem características muito diferentes dos outros (receita 6.5x maior)
- Modelo não consegue distinguir entre múltiplas estratégias otimais

**Ranking Oracle:**
1. Fat-Tree: 364.80 (melhor)
2. Waxman-16: 258.37
3. Tree: 56.39

**Observação:** BALANCED é métrica intermediária (27-75% acurácia) - múltiplos objetivos criam decisão complexa. Fat-Tree precisa de investigação especial.

---

## Tabela Resumida - Todos os Oracles

```
╔═════════════╦════════════╦═════════╦════════╦═══════════╦══════════╗
║  Topologia  ║  RAC (%)   ║   LRC   ║  LAR   ║ AST (ms)  ║ BALANCED ║
╠═════════════╬════════════╬═════════╬════════╬═══════════╬══════════╣
║   TREE      ║  97.85%    ║  0.82   ║ 70.57  ║   0.29    ║  56.39   ║
║  FAT_TREE   ║ 100.00%    ║  0.90   ║456.08  ║   0.02    ║ 364.80   ║
║ WAXMAN_16   ║  99.52%    ║  0.83   ║323.04  ║   0.23    ║ 258.37   ║
╚═════════════╩════════════╩═════════╩════════╩═══════════╩══════════╝
```

---

## Comparação Oracle vs Model (DADOS COMPLETOS)

### Métricas do Modelo (Acurácia % - Per-Topology Models Otimizados)

**Fonte:** `apresentacao/machine_learning/ACADEMIC_ANALYSIS_OPTION2.md` (linhas 152-158)

| Objetivo | Tree | Fat-Tree | Waxman-16 | Average | Assessment |
|-----------|------|----------|-----------|---------|------------|
| **RAC** (Request Acceptance Rate) | **75.69%** | 55.51% | 67.46% | 66.22% | ✓ Good |
| **LRC** (Long-Term Revenue-to-Cost) | **73.48%** | 39.21% | 57.89% | 56.86% | ⚠ Medium |
| **LAR** (Long-Term Average Revenue) | **58.56%** | 25.99% | 50.72% | 45.09% | 🔴 Critical |
| **AST** (Average Solving Time) | **100.00%** | 95.15% | 99.52% | 98.23% | ✅ Excellent |
| **BALANCED** (0.8*revenue - 0.2*time) | **75.14%** | 27.75% | 46.89% | 49.93% | ⚠ Medium |

### Tabela Completa - Oracle vs Model Accuracy:

| Métrica | Topologia | Oracle | Model Accuracy | Gap | Status |
|---------|-----------|--------|-----------------|-----|--------|
| **RAC** | Tree | 97.85% | 75.69% | -22.16 pp | ⚠️ |
| **RAC** | Fat-Tree | 100.00% | 55.51% | -44.49 pp | 🔴 |
| **RAC** | Waxman-16 | 99.52% | 67.46% | -32.06 pp | ⚠️ |
| **LRC** | Tree | 0.82 | 73.48% | +71.66 pp | ✅ |
| **LRC** | Fat-Tree | 0.90 | 39.21% | -50.79 pp | 🔴 |
| **LRC** | Waxman-16 | 0.83 | 57.89% | +57.06 pp | ✅ |
| **LAR** | Tree | 70.57 | 58.56% | -12.01 pp | ⚠️ |
| **LAR** | Fat-Tree | 456.08 | 25.99% | -430.09 pp | 🔴 |
| **LAR** | Waxman-16 | 323.04 | 50.72% | -272.32 pp | 🔴 |
| **AST** | Tree | 0.29 | 100.00% | +99.71 pp | ✅✅ |
| **AST** | Fat-Tree | 0.02 | 95.15% | +95.13 pp | ✅ |
| **AST** | Waxman-16 | 0.23 | 99.52% | +99.29 pp | ✅✅ |
| **BALANCED** | Tree | 56.39 | 75.14% | +18.75 pp | ✅ |
| **BALANCED** | Fat-Tree | 364.80 | 27.75% | -337.05 pp | 🔴 |
| **BALANCED** | Waxman-16 | 258.37 | 46.89% | -211.48 pp | 🔴 |

---

## Arquitetura das Métricas

### Hierarquia de Objetivos

```
                    OBJECTIVES (5)
                         |
           ┌─────────────┼─────────────┬──────────────┬──────────┐
           |             |             |              |          |
         RAC           LRC            LAR           AST       BALANCED
      (binary:      (maximize      (maximize      (minimize     (multi)
      accept/       efficiency)    revenue)      time)      0.8R-0.2T)
      reject)
           |             |             |              |          |
    Model: 66.2%    Model: 56.9%  Model: 45.1%  Model: 98.2%  Model: 49.6%
    Oracle: 97-100% Oracle: 0.82-0.90         Oracle: 0.02-0.29    Oracle: 56-365
    Status: ⚠️       Status: ✅      Status: 🔴     Status: ✅✅   Status: ✅/🔴
```

### Por que cada métrica é importante?

1. **RAC**: Métrica clássica de VNE - quantas requisições aceitamos?
2. **LRC**: Métrica financeira - sistema é eficiente em custo?
3. **LAR**: Métrica de receita - quanto ganhamos?
4. **AST**: Métrica de performance - sistema responde rápido?
5. **BALANCED**: Métrica realista - combinação de objetivos

---

## Insights Detalhados - Análise Oracle vs Model

### 🎯 Fatos principais sobre os Oracles:

1. **Fat-Tree DOMINA em performance (Oracle):**
   - RAC: 100.00% (perfeito)
   - LRC: 0.90 (mais eficiente)
   - LAR: 456.08 (6.5x mais receita que Tree)
   - AST: 0.02ms (14x mais rápido)
   - BALANCED: 364.80 (6.5x melhor)

2. **Mas Fat-Tree é o PROBLEMA do modelo (acurácia baixa):**
   - RAC: Gap -44.49 pp (pior topologia para RAC)
   - LRC: Gap -50.79 pp (performance crítica)
   - LAR: Gap -430.09 pp (performance CRÍTICA - 25.99%)
   - AST: Gap -4.85 pp (apenas exceção)
   - BALANCED: Gap -337.05 pp (performance crítica)

3. **Tree vs Waxman-16 (Oracle):**
   - RAC: Waxman ganha (99.5% vs 97.8%)
   - LRC: Waxman ganha (0.83 vs 0.82)
   - LAR: Waxman vence (323 vs 70)
   - AST: Waxman ganha (0.23 vs 0.29)
   - BALANCED: Waxman ganha (258 vs 56)

4. **Complexidade das métricas (empiricamente observado):**
   - ✅✅ **Muito Fácil**: AST (98.2% acurácia média) - problema binário bem definido
   - ✅ **Fácil**: LRC (56.9% acurácia média) - Tree e Waxman bons
   - ⚠️ **Médio**: RAC (66.2%) - Fat-Tree é o problema
   - ⚠️ **Médio**: BALANCED (49.6%) - Fat-Tree é o problema
   - 🔴 **CRÍTICO**: LAR (45.1% acurácia média) - Fat-Tree descalibrado (25.99%)

---

## Próximos Passos

1. **Coletar acurácias do modelo** para cada métrica:
   - Rodar avaliação de cada árvore de decisão
   - Extrair top-3 accuracy (ranking)
   - Salvar em formato estruturado

2. **Calcular gaps Oracle - Model:**
   - Para cada métrica e topologia
   - Identificar maiores oportunidades de melhoria
   - Entender padrões de falha

3. **Análise de gaps:**
   - Qual métrica tem maior gap?
   - Qual topologia é mais desafiadora?
   - Por que o modelo falha naquele caso?

4. **Visualizações:**
   - Gráfico Oracle vs Model por métrica
   - Heatmap de gaps
   - Série temporal se dados disponíveis

---

## Visualizações - Imagens Relacionadas

### Oracle vs Model Comparison
- 📊 `models/oracle_vs_model_comparison.png` - Comparação geral Oracle vs Model
- 📈 `models/oracle_vs_model_detailed.png` - Análise detalhada por métrica
- 🎯 `models/oracle_vs_model_gap_analysis.png` - Análise de gaps (diferenças)
- 📋 `models/oracle_vs_model_summary_table.png` - Tabela resumida em formato visual

### Algoritmos por Topologia (Model + Oracle)
- 🌳 `models/model_oracle_algorithms_tree.png` - Análise algoritmos Tree
- 🌲 `models/model_oracle_algorithms_fat_tree.png` - Análise algoritmos Fat-Tree
- 🕸️ `models/model_oracle_algorithms_waxman_16.png` - Análise algoritmos Waxman-16
- 📊 `models/model_oracle_algorithms_consolidated.png` - Consolidado todas topologias

### Visualizações Alternativas (Grafico)
- 📂 `graficos/model_oracle_algorithms_tree.png`
- 📂 `graficos/model_oracle_algorithms_fat_tree.png`
- 📂 `graficos/model_oracle_algorithms_waxman_16.png`
- 📂 `graficos/model_oracle_algorithms_consolidated.png`

### Árvores de Decisão por Métrica
- 🌳 `models/tree_rac.png` - Árvore RAC
- 🌳 `models/tree_lrc.png` - Árvore LRC
- 🌳 `models/tree_lar.png` - Árvore LAR
- 🌳 `models/tree_ast.png` - Árvore AST
- 🌳 `models/tree_balanced.png` - Árvore BALANCED
- 🌳 `models/tree_overall.png` - Árvore Consolidada

### Matrizes de Confusão
- 📊 `models/confusion_rac.png` - Confusão RAC
- 📊 `models/confusion_lrc.png` - Confusão LRC
- 📊 `models/confusion_lar.png` - Confusão LAR
- 📊 `models/confusion_ast.png` - Confusão AST
- 📊 `models/confusion_balanced.png` - Confusão BALANCED
- 📊 `models/confusion_overall.png` - Confusão Consolidada

### Métricas de Algoritmo
- 📈 `models/algorithm_metrics_tree.png` - Métricas algoritmos Tree
- 📈 `models/algorithm_metrics_fat_tree.png` - Métricas algoritmos Fat-Tree
- 📈 `models/algorithm_metrics_waxman_16.png` - Métricas algoritmos Waxman-16
- 📊 `models/algorithm_ranking_overall.png` - Ranking consolidado

### Figuras de Análise
- 📉 `models/figure1_accuracy_comparison.png` - Comparação acurácias
- 📊 `models/figure2_baseline_comparison.png` - Comparação baselines
- ⬆️ `models/figure3_ranking_improvement.png` - Melhoria ranking
- 🗺️ `models/figure4_topology_comparison.png` - Comparação topologias
- 🔄 `models/figure5_dynamic_vs_fixed.png` - Dinâmico vs Fixo
- 🎯 `models/figure6_improvement_by_objective.png` - Melhoria por objetivo

---

## Arquivos Relacionados (Dados)

- `models/oracle_all_objectives.json` - Dados do Oracle para todas as 5 métricas
- `models/oracle_performance_correct.json` - Oracle apenas para RAC (anterior)
- `models/oracle_from_test_set.json` - Oracle extraído do conjunto de teste
- `models/oracle_performance_true.json` - Oracle de verdade (experimental)
- `models/oracle_performance_true_v2.json` - Oracle v2
- `calculate_oracle_all_objectives.py` - Script para calcular Oracles
- `ACADEMIC_ANALYSIS_OPTION2.md` - Análise do modelo (acurácias)

---

## Recomendações por Métrica (Baseadas em Dados Reais)

| Métrica | Gap Máximo | Problem | Recomendação | Status |
|---------|-----------|---------|--------------|--------|
| **LAR** | -430.09 pp | Fat-Tree 25.99% (10+ pontos abaixo) | 🔴 CRÍTICA - Class imbalance severo | Rebalancear dados, SMOTE, threshold adjustment |
| **RAC** | -44.49 pp | Fat-Tree 55.51% (quase random) | 🔴 Alta - Features não separáveis | Feature engineering, interaction terms |
| **LRC** | -50.79 pp | Fat-Tree 39.21% (performance baixa) | 🔴 Alta - Distribuição anômala | Investigar outliers, normalização |
| **BALANCED** | -337.05 pp | Fat-Tree 27.75% (multi-objetivo falha) | 🟡 Média - Múltiplos objetivos | Ensemble multi-objective, ranking |
| **AST** | -4.85 pp | Fat-Tree 95.15% (excelente) | 🟢 Baixa - Problema resolvido | Manter as árvores existentes |

---

## TL;DR (Muito Longo; Não Li)

✅ **Oracle calculado para 5 métricas - Resultados Finais:**

| Métrica | Oracle Range | Model Avg | Status | Prioridade |
|---------|--------------|-----------|--------|-----------|
| **RAC** | 97-100% | 66.2% | ⚠️ Médio | 🔴 Alta |
| **LRC** | 0.82-0.90 | 56.9% | ✅ Bom | 🔴 Alta |
| **LAR** | 70-456 | 45.1% | 🔴 Crítico | 🔴 CRÍTICA |
| **AST** | 0.02-0.29ms | 98.2% | ✅✅ Excelente | 🟢 Baixa |
| **BALANCED** | 56-365 | 49.6% | ⚠️ Médio | 🟡 Média |

📊 **Fat-Tree é o grande desafio do projeto** (crítico em LAR, LRC, RAC, BALANCED)

🎯 **Actionable Insights:**
1. **LAR**: Investigar class imbalance severo (25.99% em Fat-Tree)
2. **Fat-Tree RAC**: Gap de 44.49 pp - necessário feature engineering
3. **AST**: Métrica bem resolvida - manter como está
4. **Próximo**: Análise detalhada de padrões de falha em Fat-Tree

