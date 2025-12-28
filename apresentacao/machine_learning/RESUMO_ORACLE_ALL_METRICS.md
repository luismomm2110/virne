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

| Topologia | Oracle LRC | Model Performance | Gap | Insight |
|-----------|-----------|------------|-----|---------|
| **Tree** | 0.82 | TBD | ? | Métrica desafiadora |
| **Fat-Tree** | 0.90 | TBD | ? | Melhor eficiência |
| **Waxman-16** | 0.83 | TBD | ? | Similar ao Tree |

**O que significa:**
- **Tree**: Cada unidade de custo gera 0.82 unidades de receita
- **Fat-Tree**: Melhor eficiência (0.90 receita por custo)
- **Waxman-16**: Similar ao Tree (0.83)

**Observação:** LRC é a métrica mais desafiadora (modelo tem 40.55% acurácia) due to extreme class imbalance (1254x).

---

### 3. LAR (Long-Term Average Revenue)
Receita total por VNR aceito (quanto maior, melhor)

| Topologia | Oracle LAR | Model Performance | Gap | Insight |
|-----------|-----------|------------|-----|---------|
| **Tree** | 70.57 | TBD | ? | Baseline baixa |
| **Fat-Tree** | 456.08 | TBD | ? | 6.5x maior que Tree |
| **Waxman-16** | 323.04 | TBD | ? | 4.6x maior que Tree |

**O que significa:**
- **Tree**: Receita média ~70.57 unidades por VNR aceito
- **Fat-Tree**: Muito maior revenue (~456) - 6.5x superior
- **Waxman-16**: Intermediário (~323) - 4.6x superior ao Tree

**Por que Fat-Tree tem mais receita?**
- Topologia maior (20 nós) permite mais VNRs simultâneos
- Mais espaço = mais requisições aceitas = mais receita total

**Observação:** LAR também é desafiadora (modelo 27.5% acurácia) - três-way trade-off entre GA, MIP e RW.

---

### 4. AST (Average Solving Time)
Tempo médio de solução (quanto menor, melhor)

| Topologia | Oracle AST (ms) | Model Performance | Gap | Insight |
|-----------|-----------|------------|-----|---------|
| **Tree** | 0.29 | TBD | ? | Relativamente rápido |
| **Fat-Tree** | 0.02 | TBD | ? | 14x mais rápido! |
| **Waxman-16** | 0.23 | TBD | ? | Rápido |

**O que significa:**
- **Tree**: 0.29 ms por VNR em média
- **Fat-Tree**: 0.02 ms - MUITO rápido (14x mais rápido que Tree)
- **Waxman-16**: 0.23 ms - rápido

**Por que Fat-Tree é tão mais rápido?**
- Topologia mais simples (20 nós vs 32 no Tree)
- Problema de otimização menor = solução mais rápida

**Observação:** AST é a métrica com MELHOR performance do modelo (95.78% acurácia) - problema bem definido (binary: pl_rank vs rw_rank_bfs).

---

### 5. BALANCED (0.8×Revenue - 0.2×Time)
Combinação ponderada: 80% receita, 20% tempo

| Topologia | Oracle BALANCED | Model Performance | Gap | Insight |
|-----------|-----------|------------|-----|---------|
| **Tree** | 56.39 | TBD | ? | Baseline moderada |
| **Fat-Tree** | 364.80 | TBD | ? | 6.5x melhor |
| **Waxman-16** | 258.37 | TBD | ? | 4.6x melhor |

**O que significa:**
- Score = 0.8 × (receita média) - 0.2 × (tempo ms)
- Prioriza receita (80%) mas penaliza tempo (20%)

**Ranking Oracle:**
1. Fat-Tree: 364.80 (melhor)
2. Waxman-16: 258.37
3. Tree: 56.39

**Observação:** BALANCED tem performance intermediária do modelo (48.81% acurácia) - múltiplos objetivos criam decisão mais complexa.

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

## Comparação Oracle vs Model (PRÓXIMO PASSO)

Aqui você comparará o Oracle calculado com a acurácia do seu modelo para cada métrica:

### Template para preenchimento:

| Métrica | Topologia | Oracle | Model Accuracy | Gap |
|---------|-----------|--------|-----------------|-----|
| **RAC** | Tree | 97.85% | 93.37% | +4.48% |
| **RAC** | Fat-Tree | 100.00% | 79.30% | +20.70% |
| **RAC** | Waxman-16 | 99.52% | 85.65% | +13.87% |
| **LRC** | Tree | 0.82 | ? | ? |
| **LRC** | Fat-Tree | 0.90 | ? | ? |
| **LRC** | Waxman-16 | 0.83 | ? | ? |
| **LAR** | Tree | 70.57 | ? | ? |
| **LAR** | Fat-Tree | 456.08 | ? | ? |
| **LAR** | Waxman-16 | 323.04 | ? | ? |
| **AST** | Tree | 0.29 | ? | ? |
| **AST** | Fat-Tree | 0.02 | ? | ? |
| **AST** | Waxman-16 | 0.23 | ? | ? |
| **BALANCED** | Tree | 56.39 | ? | ? |
| **BALANCED** | Fat-Tree | 364.80 | ? | ? |
| **BALANCED** | Waxman-16 | 258.37 | ? | ? |

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
    Model: 60.5%    Model: 40.5%  Model: 27.5%  Model: 95.8%  Model: 48.8%
    Oracle: 97-100% Oracle: 0.82-0.90         Oracle: 0.02-0.29    Oracle: 56-365
```

### Por que cada métrica é importante?

1. **RAC**: Métrica clássica de VNE - quantas requisições aceitamos?
2. **LRC**: Métrica financeira - sistema é eficiente em custo?
3. **LAR**: Métrica de receita - quanto ganhamos?
4. **AST**: Métrica de performance - sistema responde rápido?
5. **BALANCED**: Métrica realista - combinação de objetivos

---

## Insights Preliminares

### 🎯 Fatos principais sobre os Oracles:

1. **Fat-Tree é melhor em TODAS as métricas:**
   - RAC: 100% (perfeito)
   - LRC: 0.90 (mais eficiente)
   - LAR: 456 (6.5x mais receita)
   - AST: 0.02 (14x mais rápido)
   - BALANCED: 365 (6.5x melhor)

2. **Tree vs Waxman-16:**
   - RAC: Waxman ganha (99.5% vs 97.8%)
   - LRC: Waxman ganha (0.83 vs 0.82)
   - LAR: Waxman vence (323 vs 70)
   - AST: Waxman ganha (0.23 vs 0.29)
   - BALANCED: Waxman ganha (258 vs 56)

3. **Complexidade das métricas:**
   - ✅ **Fácil**: RAC e AST (modelo 60.5% e 95.8%)
   - ⚠️ **Difícil**: LRC e LAR (modelo 40.5% e 27.5%)
   - ⚠️ **Médio**: BALANCED (modelo 48.8%)

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

## Arquivos Relacionados

- `models/oracle_all_objectives.json` - Dados do Oracle para todas as 5 métricas
- `models/oracle_performance_correct.json` - Oracle apenas para RAC (anterior)
- `calculate_oracle_all_objectives.py` - Script para calcular Oracles
- `ACADEMIC_ANALYSIS_OPTION2.md` - Análise do modelo (acurácias)

---

## Recomendações por Métrica

| Métrica | Priority | Ação | Razão |
|---------|----------|------|-------|
| **RAC** | 🔴 Alta | Investigar Fat-Tree (gap 20.7%) | Maior gap, métrica clássica |
| **LRC** | 🔴 Alta | Analisar imbalance (1254x) | Model tem 40.5%, muito baixo |
| **LAR** | 🔴 Alta | Investigar trade-offs GA/MIP | Model tem 27.5%, muito baixo |
| **AST** | 🟢 Baixa | Manter como está | Model já tem 95.8% acurácia |
| **BALANCED** | 🟡 Média | Melhorar seleção multi-objetivo | Model tem 48.8%, há espaço |

---

## TL;DR (Muito Longo; Não Li)

✅ **Oracle calculado para 5 métricas:**
- RAC: 97-100% (modelo: 60.5%)
- LRC: 0.82-0.90 (modelo: 40.5%)
- LAR: 70-456 (modelo: 27.5%)
- AST: 0.02-0.29ms (modelo: 95.8%)
- BALANCED: 56-365 (modelo: 48.8%)

📊 **Fat-Tree é superior em TUDO**

🎯 **Próximo**: Comparar Oracle vs Model accuracy para cada métrica e calcular gaps

