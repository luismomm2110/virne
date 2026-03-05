# Melhorias e Cortes Pendentes para Caber em 8 Páginas

> Itens já realizados não estão listados aqui.
> Já feito: remoção da CDF figure (inference latency), condensação do Related Work (5→2 subseções), remoção da Discussion, remoção da regra formalizada (linha 109).

---

## 1. Remover Figura 4 — `algorithm_comparison_all_metrics` (~0.5 página)

**Onde:** Linhas 253-258 (figure environment) + linhas 251-252 (texto referenciando)

**Justificativa:** A Tabela 1 (`tab:algorithm-summary`) já demonstra que nenhum algoritmo é universalmente ótimo. A figura ocupa quase meia página e é redundante com a tabela.

**Ação:** Remover o `\begin{figure*}...\end{figure*}` e adaptar o parágrafo anterior para referenciar apenas a tabela.

---

## 2. Unificar as 3 figuras de Feature Importance em 1 com subfigures (~0.7 página)

**Onde:** Figuras 6, 7 e 8 (`per_objective_rac`, `per_objective_lrc`, `per_objective_lar`) — linhas 347-366

**Justificativa:** Cada figura ocupa ~1/3 de página. Três figuras separadas com captions individuais ocupam espaço excessivo.

**Opções:**
- **(A)** Criar 1 figure com 3 subfigures lado a lado (usando `\subcaption`)
- **(B)** Manter apenas RAC (a mais relevante) e resumir LRC e LAR em 1-2 frases no texto

---

## 3. Encurtar a Introdução (~0.3 página)

**Onde:** Linhas 44-69

**Problemas:**
- Linhas 62-68: dois parágrafos que restam o que já foi dito nos parágrafos anteriores
- Linha 58-60: sobrepõe com Related Work (algorithm selection + knowledge-based schedulers)

**Ação:** Fundir os dois últimos parágrafos da intro em um só, removendo repetições.

---

## 4. Cortar descrição genérica do Virne (~0.2 página)

**Onde:** Linhas 169-170 (primeira metade do parágrafo sobre Virne)

**Problema:** "Virne offers highly customizable simulations for various network scenarios, including cloud datacenters, edge computing, and 5G networks. The platform implements more than 30 NFV-RA algorithms..." — isso é descrição de marketing, não contribui para o artigo.

**Ação:** Manter apenas: "Data were collected using the Virne platform~\cite{wang2024virne}, an event-driven benchmarking framework for NFV-RA problems." e ir direto para a configuração.

---

## 5. Encurtar explicação da árvore de decisão (Sec 2.2) (~0.2 página)

**Onde:** Linhas 96-107

**Problema:** A explicação do caminho na árvore (linha 107) é muito verbosa — descreve passo a passo o que a figura já mostra visualmente.

**Ação:** Reduzir o parágrafo da linha 107 para 2-3 frases, deixando a figura falar por si.

---

## 6. Encurtar a Conclusão (~0.15 página)

**Onde:** Linhas 399-406

**Problema:** O primeiro parágrafo redefine o problema VNE (já feito na Intro e no Background). Começa com "The Virtual Network Embedding (VNE) problem is fundamental..." — repetição desnecessária.

**Ação:** Começar diretamente com os resultados: "This work proposed an approach for zero-touch selection..."

---

## 7. Fundir Seção 2.3 (Multi-Objective) na Metodologia (~0.1 página)

**Onde:** Linhas 127-130

**Problema:** Apenas 4 linhas de conteúdo. É curta demais para ser uma subseção standalone.

**Ação:** Mover o conteúdo para a Seção 4.3 (Multi-Objective Architecture), onde o mesmo conceito é descrito com mais detalhe.

---

## Estimativa Total de Economia

| Item | Economia estimada |
|------|-------------------|
| 1. Remover Fig. 4 | ~0.5 pág |
| 2. Unificar Figs. 6-8 | ~0.7 pág |
| 3. Encurtar Intro | ~0.3 pág |
| 4. Cortar descrição Virne | ~0.2 pág |
| 5. Encurtar Sec 2.2 | ~0.2 pág |
| 6. Encurtar Conclusão | ~0.15 pág |
| 7. Fundir Sec 2.3 | ~0.1 pág |
| **Total** | **~2.15 pág** |

> Combinado com os cortes já realizados (~1 página), deve ser suficiente para chegar a 8 páginas.