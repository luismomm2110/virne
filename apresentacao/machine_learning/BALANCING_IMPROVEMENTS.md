# Melhorias de Balanceamento das Árvores de Decisão

## Comparação: Antes vs Depois

### Resultados ANTES (árvores não balanceadas):
| Objetivo | Accuracy | F1-Weighted | F1-Macro | Problema Principal |
|----------|----------|-------------|----------|-------------------|
| RAC | 48.30% | 0.41 | - | Classes minoritárias com F1=0.00 |
| LAR | 37.60% | 0.34 | - | pl_rank não previsto (F1=0.00) |
| LRC | 32.09% | 0.32 | - | mip não previsto (F1=0.00) |

### Resultados DEPOIS (árvores balanceadas):
| Objetivo | Accuracy | F1-Weighted | F1-Macro | Melhoria |
|----------|----------|-------------|----------|----------|
| RAC | **67.42%** | **0.68** | **0.59** | **+19.12pp** (+39.6%) |
| LAR | **53.65%** | **0.54** | **0.49** | **+16.05pp** (+42.7%) |
| LRC | **58.51%** | **0.59** | **0.50** | **+26.42pp** (+82.3%) |

## Técnicas Aplicadas

### 1. Class Weights Customizados (Estratégia Agressiva)
- **Antes**: `compute_sample_weight('balanced')` - pesos mais conservadores
- **Depois**: `1 / sqrt(class_frequency)` - pesos mais agressivos para classes raras
- **Exemplo RAC**: pso_meta (17 amostras) recebe peso 10x vs ga_meta (987 amostras) com peso 1.31x

### 2. Hiperparâmetros Ajustados
- **max_depth**: 5 → 10 (permite mais splits para classes minoritárias)
- **min_samples_leaf**: 10 → 3 (permite folhas menores)
- **min_samples_split**: 20 → 6 (permite splits com menos amostras)

### 3. Performance por Classe (RAC - exemplo)

#### ANTES:
```
d_round:     F1 = 0.00 (nunca previsto)
ga_meta:     F1 = 0.63
mcts:        F1 = 0.55
pl_rank:     F1 = 0.48
pso_meta:    F1 = 0.00 (nunca previsto)
rw_rank_bfs: F1 = 0.00 (nunca previsto)
```

#### DEPOIS:
```
d_round:     F1 = 0.57 ✅ (agora previsto!)
ga_meta:     F1 = 0.71 ✅ (+12.7%)
mcts:        F1 = 0.75 ✅ (+36.4%)
pl_rank:     F1 = 0.85 ✅ (+77.1%)
pso_meta:    F1 = 0.13 ✅ (agora previsto, mas ainda baixo)
rw_rank_bfs: F1 = 0.60 ✅ (agora previsto!)
```

## Métricas de Qualidade

### F1-Macro (média aritmética do F1 de todas as classes)
- **RAC**: 0.59 (muito melhor que antes, onde algumas classes tinham F1=0.00)
- **LAR**: 0.49
- **LRC**: 0.50

### Classes Minoritárias Agora Funcionam
- **Antes**: Classes com <50 amostras tinham F1=0.00
- **Depois**: Todas as classes têm F1>0.00 (algumas ainda baixas, mas funcionando)

## Como Usar

### Treinar Modelos Balanceados:
```bash
cd apresentacao/machine_learning/pipeline
python 3_train_decision_trees_balanced.py
```

### Opções de Balanceamento:
1. **'balanced'**: Pesos conservadores (sklearn padrão)
2. **'aggressive'**: `1/sqrt(frequency)` - usado no treinamento atual ✅
3. **'log'**: `1/log(frequency)` - ainda mais agressivo
4. **'inverse'**: `1/frequency` - mais agressivo

### Ativar SMOTE (oversampling):
```python
training_config['use_smote'] = True
# Requer: pip install imbalanced-learn
```

## Arquivos Gerados

- `models/decision_trees_balanced.pkl` - Modelos treinados
- `models/tree_results_balanced.json` - Métricas detalhadas
- `models/tree_balanced_*.png` - Visualizações das árvores
- `models/confusion_balanced_*.png` - Matrizes de confusão

## Próximos Passos

1. ✅ Modelos balanceados treinados
2. ⏳ Atualizar script de avaliação para usar modelos balanceados
3. ⏳ Comparar resultados balanceados vs não balanceados no artigo
4. ⏳ Testar SMOTE para melhorar ainda mais classes muito minoritárias (pso_meta)

