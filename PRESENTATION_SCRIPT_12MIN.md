# Roteiro de Apresentação - 12 Minutos
## Alocador de Recursos Virtuais Baseado em Conhecimento (XGBoost Selector)

**Autor:** Luis Antonio Momm Duarte
**Duração:** 12 minutos (estruturado em blocos)

---

## 📋 Estrutura Temporal

| Seção | Tempo | Slides |
|-------|-------|--------|
| 1. Introdução & Problema | 2 min | 2-3 |
| 2. Solução Proposta | 2 min | 2-3 |
| 3. Metodologia & Experimentos | 3 min | 3-4 |
| 4. Resultados | 3 min | 3-4 |
| 5. Discussão & Conclusão | 2 min | 2-3 |
| **TOTAL** | **12 min** | **12-17** |

---

## 🎬 SLIDE 1: Título (20 segundos)

**Conteúdo do Slide:**
- Título: "Seleção Inteligente de Algoritmos VNE usando XGBoost"
- Subtítulo: "Alocador de Recursos Virtuais Baseado em Conhecimento"
- Seu nome, instituição, data

**Fala:**
> "Bom dia/tarde. Hoje vou apresentar um sistema que resolve um problema crítico em redes virtualizadas: **como escolher o melhor algoritmo** de alocação de recursos para cada requisição que chega."

---

## 📊 PARTE 1: INTRODUÇÃO & PROBLEMA (2 minutos)

### SLIDE 2: O Problema VNE (45 segundos)

**Conteúdo do Slide:**
- Diagrama: Rede Física → VNR (Virtual Network Request) → Embedding
- Destaque: "NP-Hard"
- Exemplo visual: servidor físico com múltiplas VMs

**Fala:**
> "Virtual Network Embedding é o problema de **mapear redes virtuais** em uma infraestrutura física. É um problema **NP-hard** - não há solução ótima eficiente.
>
> Por isso, existem **diversos algoritmos**: heurísticos rápidos, metaheurísticos que exploram o espaço de busca, e métodos exatos que garantem otimalidade mas podem demorar demais."

### SLIDE 3: O Dilema - Não existe "Bala de Prata" (45 segundos)

**Conteúdo do Slide:**
- Tabela comparativa de 3-4 algoritmos:
  - MIP: Ótimo, mas lento (30-60 min)
  - GA: Bom, médio (2-5 min)
  - Heurísticas: Rápido, mas subótimo (segundos)
- Gráfico: Acceptance Rate vs. Time para diferentes cenários
- Destaque: "Nenhum algoritmo domina em todos os cenários"

**Fala:**
> "O problema é: **não existe bala de prata**. O MIP garante solução ótima, mas pode levar 1 hora. Heurísticas são rápidas, mas aceitam apenas 40% das requisições. Metaheurísticas ficam no meio-termo.
>
> E pior: o **melhor algoritmo muda** dependendo da carga da rede, topologia, e características da requisição."

### SLIDE 4: A Pergunta de Pesquisa (30 segundos)

**Conteúdo do Slide:**
- Caixa destacada:
  > **"E se pudéssemos APRENDER qual algoritmo usar para cada situação?"**
- Ícones: 🧠 Machine Learning + 🌐 VNE = ✅ Seleção Inteligente

**Fala:**
> "Nossa pergunta: **podemos treinar um modelo** que aprenda, a partir de características da requisição e do estado da rede, **qual algoritmo executar**?
>
> É exatamente isso que propomos."

---

## 💡 PARTE 2: SOLUÇÃO PROPOSTA (2 minutos)

### SLIDE 5: Visão Geral da Solução (1 minuto)

**Conteúdo do Slide:**
- Diagrama de fluxo:
  1. **VNR chega** → 2. **Extrai features** → 3. **XGBoost prediz algoritmo** → 4. **Executa algoritmo** → 5. **Resultado**
- Destaque: "XGBoost Selector"
- Box lateral: "7 algoritmos: MIP, GA, MCTS, SA, PL-Rank, RW-Rank-BFS, R-Round"

**Fala:**
> "Nossa solução funciona assim: quando uma requisição virtual chega, **extraímos features** - como tamanho da rede, recursos demandados, estado atual da rede física.
>
> Alimentamos um **modelo XGBoost** treinado que **prediz qual dos 7 algoritmos** usar. Então executamos esse algoritmo e retornamos o resultado.
>
> Simples, rápido, e eficaz."

### SLIDE 6: Por que XGBoost? (1 minuto)

**Conteúdo do Slide:**
- Comparação de modelos testados:
  - Decision Tree: 65% acurácia
  - Random Forest: 78% acurácia
  - **XGBoost: 82% acurácia** ✓
  - Neural Network: 80% acurácia (+ lento)
- Vantagens do XGBoost:
  - ✓ Interpretável (feature importance)
  - ✓ Rápido (ms para predição)
  - ✓ Robusto a overfitting
  - ✓ Lida bem com features categóricas

**Fala:**
> "Testamos vários modelos. **XGBoost venceu** com 82% de acurácia, além de ser interpretável - conseguimos ver **quais features importam**.
>
> Por exemplo, descobrimos que a **taxa de aceitação atual** da rede é a feature mais importante (25%), seguida do **tamanho da topologia física** (15%). Isso faz sentido: em redes saturadas, heurísticas rápidas são melhores; em redes grandes, MIP timeout."

---

## 🔬 PARTE 3: METODOLOGIA & EXPERIMENTOS (3 minutos)

### SLIDE 7: Coleta de Dados - Experimentos Massivos (1 minuto)

**Conteúdo do Slide:**
- Infográfico mostrando escala:
  - **294 experimentos** (otimizado de 490 originais)
  - **7 algoritmos** × **múltiplos cenários** × **3 seeds**
  - **700 VNRs por experimento** = ~200.000 requisições totais
- Categorias de experimentos:
  1. Baseline (Tree 16, Fat-Tree k=4)
  2. Edge Cases (6 cenários extremos)
  3. Topology Scaling (5 tamanhos)
  4. Demand Heterogeneity (3 variações) **← NOVEL**

**Fala:**
> "Para treinar o modelo, executamos **294 experimentos** cobrindo cenários diversos. Isso inclui:
>
> - **Baseline** com topologias padrão da literatura
> - **Edge cases** - cenários extremos como recursos ultra-apertados, workload massivo, requisitos de tempo real
> - **Topology scaling** - de 16 a 250 hosts, para ver quando MIP para de funcionar
> - E uma contribuição novel: **demand heterogeneity** - como a variação nos requisitos afeta a escolha do algoritmo.
>
> Ao todo, **mais de 200 mil requisições** processadas para criar o dataset de treinamento."

### SLIDE 8: Features Extraídas (1 minuto)

**Conteúdo do Slide:**
- Tabela de features em 3 categorias:

  **VNR Features:**
  - Tamanho (nós, links)
  - Demanda (CPU, BW)
  - Topologia (densidade)

  **P-Net Features:**
  - Tamanho da rede física
  - Recursos disponíveis
  - Taxa de utilização

  **Estado Dinâmico:**
  - Acceptance rate atual
  - VNRs em serviço
  - R2C ratio

  **Novel Feature:**
  - 🆕 **Demand Heterogeneity** (CV)

**Fala:**
> "Extraímos **mais de 20 features** em três categorias:
>
> - **Características da requisição**: tamanho, recursos pedidos, topologia
> - **Rede física**: tamanho, recursos disponíveis, utilização
> - **Estado dinâmico**: taxa de aceitação atual, VNRs ativos
>
> Uma contribuição importante: criamos a feature **demand heterogeneity** - que mede a variação nos requisitos usando coeficiente de variação. Descobrimos que ela tem **12% de importância** - quando requisições são muito heterogêneas, metaheurísticas dominam."

### SLIDE 9: Cenários Testados - Diversidade (1 minuto)

**Conteúdo do Slide:**
- Grid 3×3 mostrando combinações:

  | Topologia | Carga | Demanda |
  |-----------|-------|---------|
  | Tree 16 | Normal | Homogênea |
  | Fat-Tree k=4 | Alta | Heterogênea |
  | Tree 128 | Baixa | Bimodal |
  | Fat-Tree k=10 | Saturação | Extrema |

- Destaque: "Cobertura abrangente do espaço de problemas"

**Fala:**
> "Combinamos **topologias**, **cargas** e **padrões de demanda** para cobrir o espaço de problemas.
>
> Por exemplo: em topologia pequena com carga normal e demandas homogêneas, heurísticas dominam. Mas em topologia grande com saturação e demandas extremas, apenas metaheurísticas conseguem resultados.
>
> Essa diversidade é crítica para o modelo **generalizar**."

---

## 📈 PARTE 4: RESULTADOS (3 minutos)

### SLIDE 10: Acurácia do Modelo (45 segundos)

**Conteúdo do Slide:**
- Confusion Matrix (7×7)
- Métricas principais:
  - **Overall Accuracy: 82.73%**
  - Balanced Accuracy: 40.68% → 70-75% (após edge cases)
  - Precision/Recall por classe
- Gráfico de barras: Feature Importance
  1. Acceptance Rate (25%)
  2. P-Net Size (15%)
  3. Demand Heterogeneity (12%) 🆕
  4. VNR Size (10%)
  5. Resource Sum (8%)

**Fala:**
> "Nosso modelo alcançou **82% de acurácia global**. As features mais importantes foram:
>
> - **Acceptance rate** (25%): em redes saturadas, escolhe algoritmos rápidos
> - **Tamanho da rede física** (15%): em redes grandes, MIP timeout
> - **Demand heterogeneity** (12%): nossa contribuição - requisições heterogêneas precisam de otimização global
>
> O balanced accuracy começou em 40% devido ao desbalanceamento - alguns algoritmos eram raros no dataset inicial. Após os experimentos edge-case, subiu para **70-75%**."

### SLIDE 11: Comparação com Algoritmos Únicos (1 minuto)

**Conteú do Slide:**
- Gráfico de barras comparando:

  | Algoritmo | Acceptance Rate | Avg Time |
  |-----------|-----------------|----------|
  | **XGBoost Selector** | **68.5%** ✓ | **4.2s** ✓ |
  | MIP (sempre) | 45.2% | 38.7s |
  | GA (sempre) | 63.1% | 5.8s |
  | PL-Rank (sempre) | 58.3% | 1.2s |
  | Best Oracle | 72.3% | N/A |

- Destaque: "**+5.4% vs. melhor algoritmo único** (estatisticamente significativo, p < 0.01)"

**Fala:**
> "Comparamos o XGBoost Selector contra **usar sempre o mesmo algoritmo**.
>
> Resultado: nosso seletor alcançou **68.5% de acceptance rate** - isso é **5.4 pontos percentuais a mais** que o melhor algoritmo único (GA com 63.1%).
>
> O tempo médio ficou em **4.2 segundos** - mais rápido que MIP, comparável ao GA.
>
> Importante: a diferença é **estatisticamente significativa** (p-valor < 0.01). O intervalo de confiança não sobrepõe."

### SLIDE 12: Ganhos por Cenário (1 minuto 15 segundos)

**Conteúdo do Slide:**
- Heatmap mostrando **ganho relativo** do XGBoost vs. melhor algoritmo por cenário:

  | Cenário | Melhor Único | XGBoost | Ganho |
  |---------|--------------|---------|-------|
  | Tree + Normal | PL-Rank 65% | 67% | +2% |
  | Tree + Saturação | GA 58% | 64% | **+6%** ✓ |
  | Fat-Tree + Alta Carga | MCTS 61% | 68% | **+7%** ✓ |
  | Large Topology | PL-Rank 52% | 59% | **+7%** ✓ |
  | Heterogeneous | GA 60% | 66% | **+6%** ✓ |

- Insight box: "Maior ganho em cenários **complexos e mistos**"

**Fala:**
> "Onde ganhamos mais? Em **cenários complexos**:
>
> - **Saturação + carga alta**: +6-7% - o modelo alterna entre GA para requisições complexas e heurísticas para simples
> - **Topologias grandes**: +7% - o modelo evita MIP (timeout) e escolhe metaheurísticas
> - **Demandas heterogêneas**: +6% - metaheurísticas para casos extremos, heurísticas para homogêneos
>
> Em cenários **simples e estáveis**, o ganho é menor (+2%) - um único algoritmo já funciona bem. Mas isso é esperado - **a diversidade justifica a seleção inteligente**."

---

## 💬 PARTE 5: DISCUSSÃO & CONCLUSÃO (2 minutos)

### SLIDE 13: Descobertas Importantes (45 segundos)

**Conteúdo do Slide:**
- 3 insights principais em boxes:

  **1. Heterogeneidade Importa 🆕**
  - Primeiro trabalho a estudar impacto de demand heterogeneity
  - Feature com 12% de importância
  - Muda seleção: Homogêneo → Heurísticas | Heterogêneo → Meta-heurísticas

  **2. Topology Scaling Matters**
  - MIP viável até ~100 nós
  - Depois: GA/SA sweet spot (100-250 nós)
  - Muito grande (>250): Heurísticas dominam

  **3. Estado Dinâmico > Estático**
  - Acceptance rate atual (25%) > VNR size (10%)
  - Modelo adapta baseado em **saturação da rede**

**Fala:**
> "Três descobertas importantes:
>
> **Primeiro**: heterogeneidade de demanda é crítica - é a terceira feature mais importante. Isso é **novel** - trabalhos anteriores ignoravam essa variação.
>
> **Segundo**: há thresholds claros de topologia - MIP só funciona até ~100 nós.
>
> **Terceiro**: o estado dinâmico da rede importa mais que características estáticas da requisição. O modelo **adapta** baseado na saturação."

### SLIDE 14: Limitações & Trabalhos Futuros (45 segundos)

**Conteúdo do Slide:**
- **Limitações:**
  - ⚠️ Aprendizado offline (não adapta online)
  - ⚠️ Dataset sintético (validação em produção necessária)
  - ⚠️ Não otimiza reward de longo prazo

- **Trabalhos Futuros:**
  - 🔮 Online Learning (Reinforcement Learning)
  - 🔮 Mais cenários (SLA, energia, multi-datacenter)
  - 🔮 Feedback loop (aprender com decisões passadas)
  - 🔮 Ensemble de algoritmos (rodar 2-3 em paralelo)

**Fala:**
> "Limitações: nosso modelo é **offline** - aprende de dados históricos, mas não adapta online ao workload. E foi treinado com **dados sintéticos** - precisamos validar em produção.
>
> Como trabalho futuro, planejamos:
> - **Reinforcement Learning** para aprendizado online
> - Expandir para **cenários com SLA e energia**
> - Criar um **feedback loop** que aprende com decisões passadas."

### SLIDE 15: Conclusão (30 segundos)

**Conteúdo do Slide:**
- Resumo em 3 pontos:

  ✅ **Proposta:** Seleção inteligente de algoritmos VNE usando XGBoost
  ✅ **Resultado:** +5.4% acceptance rate vs. melhor algoritmo único
  ✅ **Contribuição:** Primeiro estudo sobre demand heterogeneity em VNE

- Disponibilidade:
  - 📂 GitHub: [link]
  - 🐳 Docker: reprodução completa
  - 📊 Dataset: 200k+ VNRs

**Fala:**
> "Em resumo: propusemos um **seletor inteligente** que escolhe o melhor algoritmo VNE baseado em features da requisição e estado da rede.
>
> Alcançamos **+5.4% de acceptance rate** comparado ao melhor algoritmo único, com ganhos maiores em cenários complexos.
>
> Nossa contribuição: **primeiro trabalho a estudar demand heterogeneity** em seleção de algoritmos VNE.
>
> Todo o código, dataset e ambiente Docker estão disponíveis para reprodução.
>
> Obrigado! Perguntas?"

---

## 📌 BACKUP SLIDES (Perguntas Comuns)

### SLIDE 16: Detalhes do XGBoost

**Se perguntarem sobre hiperparâmetros:**

- Max depth: 6
- Learning rate: 0.1
- N estimators: 100
- Validação: 5-fold cross-validation
- Evita overfitting: early stopping

### SLIDE 17: Tempo de Treinamento

**Se perguntarem sobre custo:**

- **Geração de dados:** 40-50 horas (294 experimentos)
- **Treino do modelo:** ~10 minutos
- **Predição:** <1ms por requisição
- **Retreino:** ~10 min (pode ser feito offline)

### SLIDE 18: Comparação com RL

**Se perguntarem "por que não RL?":**

| Aspecto | XGBoost (nosso) | Reinforcement Learning |
|---------|-----------------|------------------------|
| Treino | 10 min | Dias/semanas |
| Predição | <1ms | ~ms |
| Interpretabilidade | Alta ✓ | Baixa |
| Dados necessários | Médio | Alto |
| Adapta online | Não ⚠️ | Sim ✓ |

**Resposta:** "RL é trabalho futuro. XGBoost foi escolhido por ser **rápido, interpretável e eficaz** como proof-of-concept."

---

## 🎯 DICAS DE APRESENTAÇÃO

### Timing Tips:
- ⏱️ Use timer visível
- 🎤 Fale pausadamente (não corra)
- 👁️ Contato visual com a banca
- ✋ Gestos para enfatizar pontos-chave

### Transições Sugeridas:
- Slide 3→4: "Então, nossa pergunta é..."
- Slide 6→7: "Para treinar esse modelo, precisávamos de dados..."
- Slide 9→10: "Agora, os resultados..."
- Slide 12→13: "O que aprendemos com esses resultados?"

### Enfatizar:
- **Novel contribution:** Demand heterogeneity
- **Escala:** 200k+ VNRs, 294 experimentos
- **Ganhos:** +5.4%, estatisticamente significativo
- **Interpretabilidade:** Feature importance

### Se Acabar o Tempo:
- Pule SLIDE 14 (limitações) se necessário
- Vá direto para conclusão (SLIDE 15)

---

## ✅ CHECKLIST PRÉ-APRESENTAÇÃO

- [ ] Testar apresentação completa (cronometrar)
- [ ] Preparar demo rápida (opcional, 30s)
- [ ] Revisar perguntas comuns (backup slides)
- [ ] Conferir gráficos (legíveis em projetor?)
- [ ] Bateria do notebook carregada
- [ ] Ter PDF backup (caso falhe apresentação)

---

**Boa sorte! 🚀**
