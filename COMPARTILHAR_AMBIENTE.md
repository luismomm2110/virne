# Como Compartilhar o Ambiente ViRNE com Conda

## 🎯 Para Você (Exportar o Ambiente)

### Opção 1: Exportar Ambiente Completo (Recomendado)

```bash
# 1. Ativar o ambiente
conda activate virne

# 2. Exportar com versões exatas (mais reprodutível)
conda env export > environment-exact.yml

# 3. Exportar sem builds específicos (mais portável)
conda env export --no-builds > environment.yml

# 4. Exportar apenas pacotes principais (mais flexível)
conda env export --from-history > environment-minimal.yml
```

**Recomendação**: Use `environment.yml` (sem builds) para máxima portabilidade entre sistemas operacionais diferentes.

---

## 📦 Para Outra Pessoa (Importar o Ambiente)

### Passo 1: Instalar Conda/Miniconda

Se a pessoa não tiver Conda:

```bash
# macOS/Linux
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# ou via homebrew (macOS)
brew install miniconda
conda init
```

### Passo 2: Criar Ambiente a partir do arquivo

```bash
# Clone o repositório ou copie os arquivos
git clone <seu-repo>
cd virne

# Criar ambiente a partir do environment.yml
conda env create -f environment.yml

# Isso irá:
# 1. Criar ambiente chamado "virne"
# 2. Instalar Python 3.10
# 3. Instalar todas as dependências (PyTorch, PyG, XGBoost, etc.)
```

### Passo 3: Ativar e Instalar ViRNE

```bash
# Ativar o ambiente
conda activate virne

# Instalar o pacote ViRNE em modo desenvolvimento
pip install -e .

# Verificar instalação
python -c "import virne; print('✓ ViRNE instalado com sucesso!')"
```

### Passo 4: Testar

```bash
# Testar simulação
python apresentacao/algoritmos/main_tree_ga.py experiment.seed=0 v_sim_setting.num_v_nets=10

# Testar ML pipeline
cd apresentacao/machine_learning
python 3_train_xgboost.py
```

---

## 📋 Arquivos para Compartilhar

### Mínimo necessário:
```
virne/
├── environment.yml              # ← Arquivo Conda principal
├── pyproject.toml              # Para instalação do pacote
├── virne/                      # Código fonte
├── apresentacao/               # Scripts e dados
└── COMPARTILHAR_AMBIENTE.md    # Este guia
```

### Como compartilhar:

#### Opção A: Git (Recomendado)
```bash
# 1. Adicionar environment.yml ao git
git add environment.yml COMPARTILHAR_AMBIENTE.md
git commit -m "Add conda environment file"
git push

# 2. A outra pessoa clona
git clone <seu-repo>
cd virne
conda env create -f environment.yml
```

#### Opção B: ZIP
```bash
# Criar arquivo ZIP sem dados pesados
zip -r virne-ambiente.zip \
  environment.yml \
  pyproject.toml \
  virne/ \
  apresentacao/*.md \
  apresentacao/machine_learning/*.py \
  apresentacao/algoritmos/*.py \
  apresentacao/algoritmos/settings/ \
  COMPARTILHAR_AMBIENTE.md

# Enviar virne-ambiente.zip
```

#### Opção C: Docker (já criado)
```bash
# Alternativa: usar o Dockerfile.apresentacao
docker build -f Dockerfile.apresentacao -t virne-ml .
docker run -it virne-ml bash
```

---

## 🔧 Troubleshooting para Outra Pessoa

### Erro: "ResolvePackageNotFound"

```bash
# Solução 1: Usar environment.yml sem builds
conda env create -f environment.yml

# Solução 2: Se ainda falhar, instalar manualmente
conda create -n virne python=3.10
conda activate virne
conda install pytorch=2.0.0 cpuonly -c pytorch
conda install pyg -c pyg
pip install -r requirements.txt  # Se você criar um
```

### Erro: "PyTorch Geometric not found"

```bash
# Instalar PyG via conda (mais fácil)
conda install pyg -c pyg

# Ou via pip (alternativa)
pip install torch-geometric
```

### Erro: "Permission denied"

```bash
# Dar permissões aos scripts
chmod +x apresentacao/machine_learning/*.sh
chmod +x apresentacao/algoritmos/*.py
```

### Erro: "Module 'virne' not found"

```bash
# Instalar em modo desenvolvimento
pip install -e .

# Ou adicionar ao PYTHONPATH temporariamente
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

---

## 🎓 Instruções Simples para Iniciantes

### Setup em 4 comandos:

```bash
# 1. Criar ambiente
conda env create -f environment.yml

# 2. Ativar
conda activate virne

# 3. Instalar pacote
pip install -e .

# 4. Testar
python -c "import virne; print('Funcionou!')"
```

---

## 📊 Comparação de Métodos

| Método | Vantagens | Desvantagens |
|--------|-----------|--------------|
| **Conda (environment.yml)** | ✅ Reprodutível<br>✅ Gerencia dependências system-level<br>✅ Funciona cross-platform | ⚠️ Requer Conda instalado<br>⚠️ Pode ser lento |
| **pip (requirements.txt)** | ✅ Mais rápido<br>✅ Padrão Python | ❌ PyTorch Geometric complicado<br>❌ Não gerencia Python version |
| **Docker** | ✅ Totalmente isolado<br>✅ Inclui OS | ❌ Grande (~2GB)<br>❌ Mais complexo |
| **pyproject.toml** | ✅ Moderno<br>✅ Padrão PEP 517 | ⚠️ Pode não resolver PyG automaticamente |

**Recomendação**: Use **Conda (environment.yml)** para máxima compatibilidade.

---

## 🚀 Quick Start para Apresentação

Se alguém só quer rodar a apresentação (ML pipeline):

```bash
# 1. Setup
conda env create -f environment.yml
conda activate virne
pip install -e .

# 2. Rodar pipeline ML (usa dados já gerados)
cd apresentacao/machine_learning
python 3_train_xgboost.py
python 6_create_comparison_plots.py

# 3. Ver resultados
ls results/
open results/confusion_matrix.png
```

**Tempo total**: ~5 minutos setup + 2 minutos execução

---

## 📝 Checklist para Compartilhar

Antes de compartilhar, garanta que você tem:

- [ ] `environment.yml` atualizado
- [ ] `README.md` com instruções
- [ ] `COMPARTILHAR_AMBIENTE.md` (este arquivo)
- [ ] Dados de exemplo em `apresentacao/simulacoes/` (opcional)
- [ ] Scripts documentados com comentários
- [ ] `.gitignore` para não commitar dados pesados
- [ ] Testes básicos funcionando

---

## 💡 Dicas Extras

### Atualizar environment.yml quando adicionar pacotes:

```bash
conda activate virne
conda install novo-pacote
conda env export --no-builds > environment.yml
git add environment.yml
git commit -m "Update dependencies"
```

### Criar requirements.txt alternativo (para pip):

```bash
pip freeze > requirements.txt
# Editar manualmente para remover pacotes desnecessários
```

### Clonar ambiente para outra máquina:

```bash
# Máquina A (sua)
conda env export > environment.yml

# Máquina B (outra pessoa)
conda env create -f environment.yml
conda activate virne
```

---

## 🎯 Exemplo Real de Uso

### Você:
```bash
# Exportar
conda activate virne
conda env export --no-builds > environment.yml
git add environment.yml
git push
```

### Colega:
```bash
# Importar
git clone https://github.com/seu-usuario/virne
cd virne
conda env create -f environment.yml
conda activate virne
pip install -e .

# Executar
python apresentacao/machine_learning/3_train_xgboost.py
# ✓ Funciona!
```

---

**Resumo**: Mande o `environment.yml` + código fonte, e a pessoa roda `conda env create -f environment.yml` → funciona!
