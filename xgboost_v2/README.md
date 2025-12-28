# XGBoost VNE Selector v2

Sistema de seleção de algoritmos VNE baseado em XGBoost com **score customizável**.

## 🎯 Características

- ✅ Score configurável (aceitação, tempo, R2C)
- ✅ Train/Test split automático
- ✅ Cross-validation (k-fold)
- ✅ Métricas detalhadas
- ✅ Visualizações (feature importance, confusion matrix)
- ✅ Fácil de usar

## 📦 Instalação

```bash
pip install xgboost pandas scikit-learn matplotlib seaborn
```

## 🚀 Uso Rápido

### 1. Treinar com configuração padrão (balanceada)

```bash
python train_xgboost_v2.py
```

Isso irá:
- Usar pesos: 60% aceitação, 30% tempo, 10% R2C
- Train/test split: 80/20
- Cross-validation: 5 folds
- Salvar modelo em `xgboost_v2/models/`

### 2. Treinar focando apenas em aceitação

```bash
python train_xgboost_v2.py --score-config acceptance_only
```

### 3. Treinar com pesos customizados

```bash
python train_xgboost_v2.py \
    --score-config custom \
    --w-acceptance 0.7 \
    --w-time 0.2 \
    --w-r2c 0.1
```

### 4. Ajustar hiperparâmetros do XGBoost

```bash
python train_xgboost_v2.py \
    --max-depth 8 \
    --learning-rate 0.05 \
    --n-estimators 200
```

## ⚙️ Configurações de Score Pré-definidas

| Nome | Aceitação | Tempo | R2C | Descrição |
|------|-----------|-------|-----|-----------|
| `acceptance_only` | 100% | 0% | 0% | Maximiza aceitação |
| `balanced` | 60% | 30% | 10% | Balanceado (padrão) |
| `fast` | 30% | 60% | 10% | Prioriza velocidade |
| `quality` | 40% | 10% | 50% | Prioriza qualidade (R2C) |
| `acceptance_speed` | 70% | 30% | 0% | Foco em aceitação e velocidade |

## 📊 Fórmula do Score

```python
score = w_acceptance * acceptance_rate - w_time * normalized_time + w_r2c * r2c_ratio
```

Onde:
- `acceptance_rate`: 1.0 se aceita, 0.0 se rejeita
- `normalized_time`: tempo normalizado (0-1, menor é melhor)
- `r2c_ratio`: revenue-to-cost ratio (maior é melhor)

O algoritmo com **maior score** é escolhido como o "melhor" para aquela VNR.

## 📁 Estrutura de Arquivos

```
xgboost_v2/
├── config.py              # Configurações (score, treino, XGBoost)
├── data_processor.py      # Processa dados e calcula scores
├── trainer.py             # Treina modelo com CV
├── README.md             # Este arquivo
│
├── training_dataset.csv   # Dataset gerado (criado automaticamente)
│
├── models/               # Modelos treinados
│   ├── xgboost_vne_selector.json
│   ├── xgboost_vne_selector_label_encoder.pkl
│   └── xgboost_vne_selector_metadata.json
│
└── outputs/              # Visualizações e resultados
    ├── feature_importance.png
    ├── confusion_matrix.png
    └── training_results.json
```

## 📖 Exemplo Completo

```bash
# 1. Treinar focando em aceitação
python train_xgboost_v2.py \
    --score-config acceptance_only \
    --model-name selector_acc_only \
    --test-size 0.2 \
    --cv-folds 5

# 2. Treinar focando em velocidade
python train_xgboost_v2.py \
    --score-config fast \
    --model-name selector_fast \
    --max-depth 8 \
    --n-estimators 200

# 3. Treinar com pesos customizados
python train_xgboost_v2.py \
    --score-config custom \
    --w-acceptance 0.8 \
    --w-time 0.15 \
    --w-r2c 0.05 \
    --model-name selector_custom
```

## 🔍 Parâmetros Disponíveis

### Score
- `--score-config`: Configuração pré-definida ou 'custom'
- `--w-acceptance`: Peso para aceitação (se custom)
- `--w-time`: Peso para tempo (se custom)
- `--w-r2c`: Peso para R2C (se custom)

### Dados
- `--data-file`: Arquivo CSV com dados (padrão: vnr_aggregated_data.csv)
- `--output-dir`: Diretório de saída (padrão: xgboost_v2)
- `--skip-data-prep`: Pular preparação de dados

### Treinamento
- `--test-size`: Proporção para teste (padrão: 0.2)
- `--cv-folds`: Número de folds CV (padrão: 5)
- `--random-seed`: Seed para reprodutibilidade (padrão: 42)

### XGBoost
- `--max-depth`: Profundidade das árvores (padrão: 6)
- `--learning-rate`: Taxa de aprendizado (padrão: 0.1)
- `--n-estimators`: Número de árvores (padrão: 100)

## 📈 Saída do Treinamento

O script irá:

1. **Preparar dados:**
   - Calcular score para cada (VNR, algoritmo)
   - Identificar melhor algoritmo por VNR
   - Salvar dataset em `training_dataset.csv`

2. **Treinar modelo:**
   - Split train/test
   - Cross-validation
   - Treinar XGBoost
   - Avaliar no teste

3. **Gerar visualizações:**
   - Feature importance
   - Confusion matrix

4. **Salvar modelo:**
   - Modelo XGBoost (.json)
   - Label encoder (.pkl)
   - Metadados (.json)

## 📊 Métricas Reportadas

- **CV Accuracy:** Acurácia média em cross-validation
- **Test Accuracy:** Acurácia no conjunto de teste
- **Classification Report:** Precision, Recall, F1 por algoritmo
- **Confusion Matrix:** Matriz de confusão visual

## 💡 Dicas

### 1. Qual configuração de score usar?

- **Produção com deadline:** `acceptance_speed` (70% acc, 30% time)
- **Produção sem deadline:** `acceptance_only` (100% acc)
- **Pesquisa/análise:** `balanced` (60% acc, 30% time, 10% r2c)
- **Benchmark velocidade:** `fast` (30% acc, 60% time)

### 2. Como ajustar XGBoost?

Comece com padrões e ajuste se:
- **Overfitting:** Diminuir `max_depth`, `n_estimators`
- **Underfitting:** Aumentar `max_depth`, `n_estimators`
- **Treino lento:** Diminuir `n_estimators`, aumentar `learning_rate`

### 3. Quantos dados preciso?

Mínimo recomendado:
- 1000+ VNRs únicas
- Pelo menos 50 exemplos por algoritmo
- Distribuição balanceada entre cenários

## 🔬 Análise Avançada

### Comparar diferentes configurações

```bash
# Treinar 3 modelos
python train_xgboost_v2.py --score-config acceptance_only --model-name model_acc
python train_xgboost_v2.py --score-config balanced --model-name model_bal
python train_xgboost_v2.py --score-config fast --model-name model_fast

# Comparar resultados (ver training_results.json em cada output)
```

### Usar modelo treinado (futuro)

```python
from xgboost_v2.predictor import VNEPredictor

# Carregar modelo
predictor = VNEPredictor()
predictor.load_model('xgboost_v2/models/xgboost_vne_selector')

# Predizer para nova VNR
vnr_state = {
    'v_net_num_nodes': 5,
    'v_net_num_egdes': 6,
    'v_net_demand': 150,
    # ... outras features
}

best_algo, confidence = predictor.predict(vnr_state)
print(f"Use {best_algo} (confidence: {confidence:.2%})")
```

## 🐛 Troubleshooting

**Erro: "ModuleNotFoundError: No module named 'xgboost'"**
```bash
pip install xgboost
```

**Erro: "FileNotFoundError: vnr_aggregated_data.csv"**
```bash
# Certifique-se de estar no diretório correto
cd /Users/luismomm/PycharmProjects/virne
python train_xgboost_v2.py
```

**Aviso: "Pesos não somam 1.0"**
- Isso é apenas um aviso
- Pesos serão usados como especificados
- Para melhor interpretação, ajuste para somar 1.0

**Acurácia muito baixa (<50%)**
- Verifique distribuição de classes (pode estar desbalanceada)
- Tente ajustar pesos do score
- Aumente `n_estimators` ou `max_depth`

## 📚 Referências

- XGBoost: https://xgboost.readthedocs.io/
- Scikit-learn: https://scikit-learn.org/
- Paper original ViRNE: [adicionar link]

## 🤝 Contribuições

Melhorias futuras:
- [ ] Hyperparameter tuning automático (GridSearchCV)
- [ ] Suporte a mais métricas (latência, energia)
- [ ] Feature engineering automático
- [ ] Preditor online (API REST)
- [ ] Dashboard interativo

---

**Versão:** 2.0.0
**Autor:** Luis Antonio Momm Duarte
**Data:** 24 de Novembro de 2025
