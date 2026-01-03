# Artigo Conferência: Seleção Zero-Touch de Algoritmos VNE

## Título
**Seleção Zero-Touch de Algoritmos de Virtual Network Embedding usando Árvores de Decisão Multi-Objetivo**

## Resumo da Abordagem

Este artigo apresenta uma metodologia completa para seleção automática de algoritmos VNE baseada em **árvores de decisão multi-objetivo**, habilitando operação totalmente autônoma sem intervenção do operador.

### Diferenças em Relação ao XGBoost (artigo_final.tex)

| Aspecto | XGBoost (artigo_final) | Árvores Multi-Objetivo (este) |
|---------|------------------------|------------------------------|
| **Modelo** | XGBoost (ensemble único) | 5 árvores especializadas (1 por objetivo) |
| **Objetivos** | Implícito (classificação) | Explícito: RAC, LRC, LAR, AST, BALANCED |
| **Interpretabilidade** | Caixa preta | Completa (caminhos de decisão visíveis) |
| **Métrica Chave** | 93.33% acurácia exata | 69.6%-93.4% top-3 accuracy |
| **Melhoria vs Baseline** | ~1.67pp vs oráculo | +49.41pp vs baseline |
| **Latência** | ~0.01s | <1ms |
| **Foco** | Desempenho de ML | Administração zero-touch |

## Estrutura do Artigo

1. **Introdução** - Motivação, problema, contribuições
2. **Referencial Teórico** - VNE, árvores de decisão, otimização multi-objetivo
3. **Trabalhos Relacionados** - Posicionamento em relação à literatura
4. **Metodologia** - Coleta de dados, features (27), arquitetura multi-objetivo
5. **Resultados** - Top-3 accuracy, comparações, interpretabilidade, latência
6. **Discussão** - Viabilidade, limitações, trabalhos futuros
7. **Conclusão** - Resumo e impacto

## Dados e Experimentos

### Topologias Testadas
- **Tree**: 32 hosts, 31 switches (63 nós total)
- **Fat-Tree**: k=4, 16 servidores, 20 switches (36 nós)
- **Waxman-16**: 16 nós, 500 links

### Algoritmos VNE
MIP, GA-Meta, PSO-Meta, SA-Meta, MCTS, PL-Rank, RW-Rank-BFS, D-Round

### Features (27 total)
- 9 características de VNR
- 4 características de estado da rede física
- 3 características de estado do sistema
- 10 features engineerizados (heterogeneidade, fragmentação)
- 1 contexto (topologia)

### Objetivos (5 modelos)
- **RAC**: Maximizar taxa de aceitação
- **LRC**: Minimizar custo (latência de resolução)
- **LAR**: Minimizar latência média de resposta
- **AST**: Minimizar tempo de processamento
- **BALANCED**: Otimização balanceada

## Resultados Principais

### Top-3 Accuracy por Objetivo

| Objetivo | Tree | Fat-Tree | Waxman-16 |
|----------|------|----------|-----------|
| RAC | 93.37% | 79.30% | 85.65% |
| LRC | 90.06% | 77.97% | 81.34% |
| LAR | 81.77% | 69.60% | 78.47% |
| AST | 100.00% | 95.15% | 99.52% |
| BALANCED | 90.06% | 61.67% | 74.16% |

### Comparação vs Baseline

| Métrica | Baseline | Árvore (Top-3) | Oráculo | Melhoria |
|---------|----------|---|---------|---|
| Média | 34.81% | 84.23% | 100.00% | **+49.41pp** |

### Performance
- **Latência de Predição**: <1ms
- **Gap vs Oráculo**: 15.77pp
- **Interpretabilidade**: Completa (caminhos visíveis)

## Como Compilar

### Requisitos
- LaTeX (TeX Live ou MiKTeX)
- BibTeX

### Compilação
```bash
cd /Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf

# Compilar
pdflatex artigo_multiobjetivo.tex
bibtex artigo_multiobjetivo
pdflatex artigo_multiobjetivo.tex
pdflatex artigo_multiobjetivo.tex

# Resultado
# artigo_multiobjetivo.pdf
```

### Compilação com Makefile (se disponível)
```bash
make
```

## Contribuições Principais

1. **Framework Zero-Touch**: Seleção automática de algoritmos VNE sem intervenção manual
2. **Multi-Objetivo**: Cinco modelos especializados, não apenas um
3. **Interpretável**: Decisões podem ser explicadas aos operadores
4. **Prático**: Latência <1ms, pronto para produção
5. **Validado**: +49.41pp sobre baseline, 15.77pp do oráculo

## Venues Recomendadas

- IEEE Transactions on Network and Service Management
- IEEE/ACM Transactions on Networking
- USENIX NSDI
- ACM CoNEXT
- IEEE/IFIP IM (International Conference on Integrated Network Management)
- Conferências de SDN/NFV

## Próximos Passos

### Crítico (Deve Fazer)
1. Gerar visualizações de árvores de decisão (fragmentos)
2. Criar tabelas de top-3 accuracy por topologia
3. Adicionar figura de latência vs XGBoost
4. Comparar interpretabilidade com RL (caixa preta vs árvore)

### Aprimoramentos Recomendados
1. Adicionar topologia WX500 (500 nós) para maior escala
2. Comparar com SATzilla (árvore única baseline)
3. Teste de stress em condições extremas
4. Transfer learning entre topologias

### Opcional
1. Análise de sensibilidade de hiperparâmetros
2. Curvas de aprendizado
3. Discussão de deployment em produção

## Estrutura de Arquivos

```
artigo_conf/
├── artigo_multiobjetivo.tex     # Artigo principal (este arquivo)
├── references.bib                # Referências bibliográficas
├── README.md                      # Este arquivo
└── (images/)                      # Pasta para imagens/figuras (a ser criada)
    ├── tree_visualization_example.png
    ├── top3_accuracy_comparison.png
    └── latency_comparison.png
```

## Notas Importantes

1. **Métricas**: Top-3 accuracy é mais apropriada que exatidão simples para este domínio
2. **Interpretabilidade**: Principal vantagem vs aprendizado profundo
3. **Zero-Touch**: Sistema opera autonomamente sem configuração manual
4. **Multi-Objetivo**: Permite operadores priorizarem diferentes objetivos em tempo de execução

## Contato

Luis Antonio Momm Duarte
luis.duarte@edu.udesc.br
Universidade do Estado de Santa Catarina

---

*Última atualização: Dezembro 2024*