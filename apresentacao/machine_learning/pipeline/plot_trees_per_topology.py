#!/usr/bin/env python3
"""
Plotar árvores de decisão:
- Por topologia (Fat-Tree e Waxman-16), usando `decision_trees_per_topology.pkl`
- Globais (treinadas em todos os cenários), usando `decision_trees.pkl`

Parte 1: modelos por topologia
-------------------------------
Gera uma figura COMPLETA da árvore de decisão para cada combinação
(topologia, objetivo), mostrando explicitamente os splits por feature
e as classes (algoritmos) nas folhas.

Topologias suportadas (nomes de chave no pickle per-topology):
- 'fat_tree'
- 'waxman_16'

Objetivos disponíveis por topologia:
- 'rac', 'lrc', 'lar', 'ast', 'balanced'

Saída:
- Imagens das árvores por topologia em:
    ../models/trees_per_topology/tree_<topologia>_<objetivo>.pdf
    ../models/trees_per_topology/tree_<topologia>_<objetivo>.png

Parte 2: modelos globais
------------------------
Plota também as árvores globais treinadas em `decision_trees.pkl`,
nas quais a feature `topology_encoded` aparece explicitamente nos splits,
permitindo visualizar como o modelo é topology-aware.

Objetivos globais:
- 'rac', 'lrc', 'lar', 'ast', 'balanced'

Saída:
- Imagens das árvores globais em:
    ../models/trees_global/tree_global_<objetivo>.pdf
    ../models/trees_global/tree_global_<objetivo>.png

Como executar:
1) Ative o ambiente:
   conda activate virne

2) Vá até o diretório do pipeline:
   cd apresentacao/machine_learning/pipeline

3) Rode o script:
   python3 plot_trees_per_topology.py

Depois disso, inclua as figuras geradas no LaTeX/artigo conforme desejado.
"""

import os
import sys
import pickle
from typing import Dict, Any, List

import matplotlib.pyplot as plt
from sklearn.tree import plot_tree


# Caminho para o Python do conda env (para lembrar o usuário, como em outros scripts)
CONDA_PYTHON = "/Users/luismomm/miniconda3/envs/virne/bin/python3"

if os.path.exists(CONDA_PYTHON) and sys.executable != CONDA_PYTHON:
    print(
        f"NOTA: Para garantir compatibilidade, execute com: {CONDA_PYTHON} "
        f"plot_trees_per_topology.py"
    )
    print("Ou ative o ambiente conda: conda activate virne\n")


PER_TOPO_MODELS_PATH = os.path.join("..", "models", "decision_trees_per_topology.pkl")
GLOBAL_MODELS_PATH = os.path.join("..", "models", "decision_trees.pkl")

PER_TOPO_OUTPUT_DIR = os.path.join("..", "models", "trees_per_topology")
GLOBAL_OUTPUT_DIR = os.path.join("..", "models", "trees_global")

# Topologias que queremos visualizar explicitamente
TARGET_TOPOLOGIES = ["fat_tree", "waxman_16"]


def load_models(model_path: str):
    """Carrega modelos a partir de um pickle."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Arquivo de modelos não encontrado: {model_path}")

    print("=" * 80)
    print(f"Carregando modelos de: {model_path}")
    print("=" * 80)

    with open(model_path, "rb") as f:
        models = pickle.load(f)

    return models


def ensure_output_dir(output_dir: str) -> None:
    """Garante que o diretório de saída exista."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"Diretório de saída: {os.path.abspath(output_dir)}")


def plot_single_tree(
    topo_name: str,
    obj_key: str,
    model_info: Dict[str, Any],
    output_dir: str,
    figsize=(24, 14),
) -> None:
    """
    Plota uma única árvore de decisão (modelo sklearn).

    Para modelos por topologia:
        topo_name = nome da topologia
        obj_key   = objetivo (rac, lrc, ...)

    Para modelos globais:
        topo_name = 'global'
        obj_key   = objetivo (rac, lrc, ...)
    """
    model = model_info["model"]
    features: List[str] = model_info.get("features", [])
    encoder = model_info.get("encoder", None)

    class_names = None
    if encoder is not None and hasattr(encoder, "classes_"):
        class_names = list(encoder.classes_)

    topo_label = topo_name.replace("_", "-")
    obj_label = obj_key.upper()

    print(f"\nGerando árvore para topologia='{topo_name}', objetivo='{obj_key}'")
    print(f"  - Nº de features: {len(features)}")
    if hasattr(model, "max_depth"):
        print(f"  - Profundidade máxima do modelo: {model.max_depth}")

    plt.figure(figsize=figsize)
    plot_tree(
        model,
        feature_names=features if features else None,
        class_names=class_names,
        filled=True,
        rounded=True,
        proportion=True,
        fontsize=9,
    )

    plt.title(
        f"Decision Tree - Topologia: {topo_label}, Objetivo: {obj_label}",
        fontsize=16,
        fontweight="bold",
    )
    plt.tight_layout()

    base_filename = f"tree_{topo_name}_{obj_key}"
    pdf_path = os.path.join(output_dir, base_filename + ".pdf")
    png_path = os.path.join(output_dir, base_filename + ".png")

    plt.savefig(pdf_path, bbox_inches="tight")
    plt.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"  ✓ Salvo: {pdf_path}")
    print(f"  ✓ Salvo: {png_path}")


def plot_per_topology() -> None:
    """Carrega os modelos por topologia e plota árvores para Fat-Tree e Waxman-16."""
    models = load_models(PER_TOPO_MODELS_PATH)
    print(f"Topologias disponíveis no pickle per-topology: {list(models.keys())}")
    ensure_output_dir(PER_TOPO_OUTPUT_DIR)

    # Filtrar apenas as topologias de interesse
    available_topos = set(models.keys())
    selected_topos = [t for t in TARGET_TOPOLOGIES if t in available_topos]

    if not selected_topos:
        print(
            f"Nenhuma das topologias alvo {TARGET_TOPOLOGIES} foi encontrada em "
            f"{PER_TOPO_MODELS_PATH}."
        )
        print("Topologias disponíveis:", available_topos)
        return

    print("\nTopologias selecionadas para visualização:", selected_topos)

    # Para cada topologia, plotar uma árvore para cada objetivo disponível
    for topo_name in selected_topos:
        topo_models = models[topo_name]
        objectives = sorted(topo_models.keys())

        print("\n" + "-" * 80)
        print(f"TOPOLOGIA: {topo_name.upper()}")
        print("-" * 80)
        print(f"Objetivos disponíveis: {objectives}")

        for obj_key in objectives:
            model_info = topo_models[obj_key]
            plot_single_tree(topo_name, obj_key, model_info, PER_TOPO_OUTPUT_DIR)

    print("\n" + "=" * 80)
    print("GERAÇÃO DE ÁRVORES POR TOPOLOGIA CONCLUÍDA!")
    print("=" * 80)
    print(f"As figuras por topologia estão em: {os.path.abspath(PER_TOPO_OUTPUT_DIR)}")


def plot_global_models() -> None:
    """
    Carrega os modelos globais (`decision_trees.pkl`) e plota
    uma árvore por objetivo. Aqui a feature `topology_encoded`
    aparece explicitamente, permitindo ver como o modelo é
    topology-aware.
    """
    if not os.path.exists(GLOBAL_MODELS_PATH):
        print(f"\n[AVISO] Arquivo de modelos globais não encontrado: {GLOBAL_MODELS_PATH}")
        print("Pulando plotagem das árvores globais.")
        return

    print("\n" + "=" * 80)
    print(f"Carregando modelos globais de: {GLOBAL_MODELS_PATH}")
    print("=" * 80)

    with open(GLOBAL_MODELS_PATH, "rb") as f:
        global_models = pickle.load(f)

    # Espera-se que seja um dicionário {obj_key: DecisionTreeClassifier}
    if not isinstance(global_models, dict):
        print(
            "[AVISO] Formato inesperado em decision_trees.pkl; "
            "esperado dict {objetivo: modelo}."
        )
        return

    objectives = sorted(global_models.keys())
    print(f"Objetivos globais disponíveis: {objectives}")

    ensure_output_dir(GLOBAL_OUTPUT_DIR)

    # Precisamos das features na mesma ordem usada no treino global ENHANCED
    # (`3_train_decision_trees_enhanced.py`), que utiliza 25 features originais
    # + 10 novas (total 35). Definimos aqui a mesma função `select_features`,
    # mantida em sincronia com aquele script.
    def select_features():
        return [
            # VNR characteristics
            "v_net_num_nodes",
            "v_net_num_edges",
            "v_net_size_ratio",
            "v_net_demand_per_node",
            "v_net_demand_per_link",
            "v_net_connectivity",
            "v_net_total_demand",
            "v_net_node_to_link_demand_ratio",
            "v_net_lifetime",
            # Physical network state
            "p_net_available_resource",
            "p_net_node_util",
            "p_net_link_util",
            "p_net_overall_util",
            # System state
            "inservice_count",
            "system_load",
            "num_running_p_net_nodes",
            # Topology
            "topology_encoded",
            # Original engineered features
            "network_stress_index",
            "problem_complexity",
            "resource_bottleneck_ratio",
            "vnr_size_category",
            "cpu_intensive_flag",
            "bandwidth_intensive_flag",
            "utilization_pressure",
            "resource_efficiency",
            # NEW: Heterogeneidade de Recursos (3 features)
            "p_net_node_link_resource_ratio",
            "p_net_util_imbalance",
            "p_net_resource_heterogeneity",
            # NEW: Fragmentação e Saúde da Rede (3 features)
            "p_net_fragmentation_estimate",
            "p_net_uneven_utilization",
            "p_net_health_score",
            # NEW: Características VNR (4 features)
            "vnr_node_link_demand_ratio",
            "vnr_demand_intensity",
            "vnr_structural_complexity",
            "vnr_density_adjusted",
        ]

    feature_names = select_features()

    # Carregar o label encoder global para ter os nomes das classes/algoritmos
    encoder_path = os.path.join("..", "models", "algorithm_label_encoder.pkl")
    class_names = None
    if os.path.exists(encoder_path):
        with open(encoder_path, "rb") as f:
            encoder = pickle.load(f)
        if hasattr(encoder, "classes_"):
            class_names = list(encoder.classes_)
            print(f"Algoritmos (classes) globais: {class_names}")
    else:
        print(f"[AVISO] Label encoder global não encontrado em: {encoder_path}")

    for obj_key in objectives:
        dt_model = global_models[obj_key]
        model_info = {
            "model": dt_model,
            "features": feature_names,
            "encoder": None,
        }
        # Usamos topo_name='global' para diferenciar nos nomes de arquivo/título
        plot_single_tree("global", obj_key, model_info, GLOBAL_OUTPUT_DIR)

    print("\n" + "=" * 80)
    print("GERAÇÃO DE ÁRVORES GLOBAIS CONCLUÍDA!")
    print("=" * 80)
    print(f"As figuras globais estão em: {os.path.abspath(GLOBAL_OUTPUT_DIR)}")


def main() -> None:
    """Plota árvores por topologia e também as árvores globais."""
    # Parte 1: modelos por topologia
    plot_per_topology()

    # Parte 2: modelos globais (onde topology_encoded aparece)
    plot_global_models()


if __name__ == "__main__":
    main()


