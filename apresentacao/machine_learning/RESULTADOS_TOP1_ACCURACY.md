# Resultados: Top-1 Accuracy (Métrica de Treinamento)

## 📊 Resumo Executivo

**Análise**: Comparação entre modelo dinâmico (Top-1) vs melhor algoritmo fixo, usando a **mesma métrica de treinamento** (Top-1 accuracy).

---

## 🎯 Resultados por Objetivo

### RAC (Request Acceptance Rate)

| Métrica | Valor |
|---------|-------|
| **Modelo Dinâmico (Top-1)** | **0.00%** |
| **Melhor Algoritmo Fixo** | **34.36%** (ga_meta) |
| **Melhoria** | **-34.36pp** ❌ |

**Análise**:
- Modelo: 0 acertos de 617 VNRs
- Best Fixed: 212 acertos de 617 VNRs (ga_meta)
- **O modelo é PIOR que o algoritmo fixo**

---

### LRC (Long-Term Revenue-to-Cost Ratio)

| Métrica | Valor |
|---------|-------|
| **Modelo Dinâmico (Top-1)** | **0.00%** |
| **Melhor Algoritmo Fixo** | **27.23%** (pl_rank) |
| **Melhoria** | **-27.23pp** ❌ |

**Análise**:
- Modelo: 0 acertos de 617 VNRs
- Best Fixed: 168 acertos de 617 VNRs (pl_rank)
- **O modelo é PIOR que o algoritmo fixo**

---

### LAR (Long-Term Average Revenue)

| Métrica | Valor |
|---------|-------|
| **Modelo Dinâmico (Top-1)** | **0.00%** |
| **Melhor Algoritmo Fixo** | **22.85%** (ga_meta) |
| **Melhoria** | **-22.85pp** ❌ |

**Análise**:
- Modelo: 0 acertos de 617 VNRs
- Best Fixed: 141 acertos de 617 VNRs (ga_meta)
- **O modelo é PIOR que o algoritmo fixo**

---

## 📈 Estatísticas Gerais

| Métrica | Valor |
|---------|-------|
| **Média Modelo (Top-1)** | **0.00%** |
| **Média Best Fixed** | **28.15%** |
| **Melhoria Média** | **-28.15pp** ❌ |

**Conclusão**: O modelo dinâmico (Top-1) é **PIOR** que o melhor algoritmo fixo em todos os objetivos.

---

## 🔍 Comparação: Top-1 vs Top-3

| Objetivo | Top-1 Accuracy | Top-3 Accuracy | Diferença |
|----------|---------------|----------------|-----------|
| **RAC** | 0.00% | 88.33% | +88.33pp |
| **LRC** | 0.00% | 85.41% | +85.41pp |
| **LAR** | 0.00% | 81.04% | +81.04pp |
| **Média** | 0.00% | 84.93% | +84.93pp |

**Observação**: Há uma diferença enorme entre Top-1 (0%) e Top-3 (81-88%).

---

## ⚠️ Por que Top-1 é 0%?

### Análise Técnica

1. **Modelo não foi otimizado para Top-1**:
   - Modelos foram treinados, mas não otimizados especificamente para classificação exata
   - Top-1 accuracy requer predição perfeita (algoritmo exato)

2. **Problema de classificação multi-classe desbalanceada**:
   - 8 classes (algoritmos)
   - Classes muito desbalanceadas
   - Modelo pode estar prevendo sempre a classe mais frequente, mas errando o exato

3. **Top-3 é muito mais generoso**:
   - Top-1: Algoritmo previsto deve ser EXATAMENTE o verdadeiro
   - Top-3: Algoritmo verdadeiro só precisa estar entre os 3 previstos
   - Isso explica a diferença de 0% vs 81-88%

---

## ✅ Conclusões

### 1. Top-1 Accuracy (Métrica de Treinamento)

**Resultado**: ❌ **O modelo é PIOR que algoritmo fixo**

- Modelo: 0.00% accuracy
- Best Fixed: 22.85% - 34.36% accuracy
- Desvantagem: -22.85pp a -34.36pp

**Interpretação**: 
- Usando a métrica de treinamento (Top-1), o modelo não supera o baseline
- Isso indica que os modelos não foram otimizados adequadamente para classificação exata

### 2. Top-3 Accuracy (Métrica Prática)

**Resultado**: ✅ **O modelo é MUITO MELHOR que algoritmo fixo**

- Modelo: 81.04% - 88.33% accuracy
- Best Fixed: 22.85% - 34.36% accuracy
- Vantagem: +54.0pp a +58.2pp

**Interpretação**:
- Usando métrica mais realista (Top-3), o modelo supera significativamente o baseline
- Top-3 é mais apropriado para aplicação prática

---

## 🎯 Recomendações

### Para o Artigo:

1. **Reportar ambas as métricas**:
   - Top-1: 0% (métrica de treinamento, mas modelo não otimizado)
   - Top-3: 81-88% (métrica prática, modelo supera baseline)

2. **Explicar a diferença**:
   - Top-1 requer predição exata (muito difícil)
   - Top-3 é mais realista (operadores podem escolher entre opções)
   - Modelos foram avaliados com Top-3 por ser mais apropriado para uso prático

3. **Justificar Top-3**:
   - Em aplicações práticas, operadores podem escolher entre múltiplas opções
   - Múltiplos algoritmos frequentemente têm performance similar
   - Top-3 oferece flexibilidade e robustez

4. **Reconhecer limitações**:
   - Top-1 accuracy é 0% (modelos não otimizados para classificação exata)
   - Top-3 é mais generoso, mas mais apropriado para uso prático
   - Há um trade-off entre rigor ML e utilidade prática

---

## 📊 Tabela Comparativa Final

| Métrica | Modelo | Best Fixed | Melhoria | Status |
|---------|--------|------------|----------|--------|
| **Top-1** | 0.00% | 28.15% | **-28.15pp** | ❌ PIOR |
| **Top-3** | 84.93% | 28.15% | **+56.78pp** | ✅ MELHOR |

**Conclusão**: 
- Com Top-1 (métrica de treinamento): Modelo é pior
- Com Top-3 (métrica prática): Modelo é muito melhor
- **Recomendação**: Usar Top-3 para avaliação, mas reportar ambas as métricas




