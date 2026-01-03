#!/usr/bin/env python3
"""
Generate visualization of Waxman topology for the article.
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def generate_waxman_topology(num_nodes=16, seed=42):
    """Generate Waxman random topology"""
    np.random.seed(seed)
    G = nx.waxman_graph(
        n=num_nodes,
        alpha=0.5,  # Probability scaling factor
        beta=0.2,   # Distance scaling factor
        seed=seed
    )
    return G

def visualize_waxman_topology(G, output_path):
    """Visualize Waxman topology and save as PNG"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Use spring layout for better visualization
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, width=1.5, alpha=0.6, edge_color='gray')

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color='#FF6B6B',  # Red nodes
        node_size=800,
        alpha=0.9,
        edgecolors='darkred',
        linewidths=2
    )

    # Draw labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_weight='bold')

    # Title
    ax.set_title('Waxman Random Topology (16 nodes)', fontsize=14, fontweight='bold', pad=20)

    # Add statistics box
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    avg_degree = 2 * num_edges / num_nodes

    stats_text = (
        f'Topology Statistics:\n'
        f'• Total nodes: {num_nodes}\n'
        f'• Total edges: {num_edges}\n'
        f'• Average degree: {avg_degree:.2f}\n'
        f'• Waxman parameters: α=0.5, β=0.2'
    )

    ax.text(
        0.02, 0.98, stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    )

    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Topology visualization saved to: {output_path}")
    plt.close()

def main():
    # Generate topology
    G = generate_waxman_topology(num_nodes=16, seed=42)

    # Output path
    output_path = '/Users/luismomm/PycharmProjects/virne/apresentacao/artigo_conf/waxman_16_topology.png'

    # Visualize
    visualize_waxman_topology(G, output_path)

if __name__ == '__main__':
    main()
