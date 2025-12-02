#!/usr/bin/env python3
"""
Generate beautiful visualizations of Tree and Fat-Tree topologies for presentation.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np


def create_tree_topology(num_hosts=32, branching_factor=2):
    """
    Create a binary tree topology visualization.

    Args:
        num_hosts: Number of leaf nodes (hosts)
        branching_factor: Number of children per switch

    Returns:
        G: NetworkX graph
        pos: Node positions for plotting
        node_types: Dict mapping node_id to type ('host' or 'switch')
    """
    G = nx.Graph()
    node_types = {}

    # Calculate number of levels needed
    import math
    num_levels = int(math.ceil(math.log(num_hosts, branching_factor))) + 1

    # Create tree structure
    node_id = 0
    level_nodes = {0: [node_id]}  # Root at level 0
    node_types[node_id] = 'switch'
    node_id += 1

    # Build tree level by level
    for level in range(1, num_levels):
        level_nodes[level] = []
        for parent in level_nodes[level - 1]:
            for _ in range(branching_factor):
                if node_id >= num_hosts + (num_hosts - 1):  # Total nodes
                    break
                G.add_edge(parent, node_id)

                # Last level = hosts, others = switches
                if level == num_levels - 1:
                    node_types[node_id] = 'host'
                else:
                    node_types[node_id] = 'switch'

                level_nodes[level].append(node_id)
                node_id += 1

    # Create hierarchical layout
    pos = {}
    for level, nodes in level_nodes.items():
        y = -(level * 2)  # Vertical spacing
        x_spacing = 8.0 / (len(nodes) + 1)
        for i, node in enumerate(nodes):
            pos[node] = ((i + 1) * x_spacing - 4, y)

    return G, pos, node_types


def create_fat_tree_topology(k=4):
    """
    Create a Fat-Tree topology visualization.

    Args:
        k: Number of ports per switch (must be even)

    Returns:
        G: NetworkX graph
        pos: Node positions for plotting
        node_types: Dict mapping node_id to type and layer
    """
    G = nx.Graph()
    node_types = {}
    node_id = 0

    # Calculate components
    num_pods = k
    num_core = (k // 2) ** 2
    num_aggr_per_pod = k // 2
    num_edge_per_pod = k // 2
    num_hosts_per_edge = k // 2

    # Layer 1: Core switches
    core_switches = []
    for i in range(num_core):
        core_switches.append(node_id)
        node_types[node_id] = {'type': 'switch', 'layer': 'core'}
        node_id += 1

    # For each pod
    pods = []
    for pod in range(num_pods):
        pod_aggr = []
        pod_edge = []
        pod_hosts = []

        # Aggregation switches
        for i in range(num_aggr_per_pod):
            pod_aggr.append(node_id)
            node_types[node_id] = {'type': 'switch', 'layer': 'aggregation'}
            node_id += 1

        # Edge switches
        for i in range(num_edge_per_pod):
            pod_edge.append(node_id)
            node_types[node_id] = {'type': 'switch', 'layer': 'edge'}
            node_id += 1

        # Hosts
        for edge_switch in pod_edge:
            for i in range(num_hosts_per_edge):
                pod_hosts.append(node_id)
                node_types[node_id] = {'type': 'host', 'layer': 'host'}
                # Connect host to edge switch
                G.add_edge(edge_switch, node_id)
                node_id += 1

        # Connect aggregation to edge within pod
        for aggr in pod_aggr:
            for edge in pod_edge:
                G.add_edge(aggr, edge)

        # Connect aggregation to core
        for i, aggr in enumerate(pod_aggr):
            # Each aggregation connects to k/2 core switches
            for j in range(k // 2):
                core_idx = i * (k // 2) + j
                if core_idx < len(core_switches):
                    G.add_edge(aggr, core_switches[core_idx])

        pods.append({'aggr': pod_aggr, 'edge': pod_edge, 'hosts': pod_hosts})

    # Create layout
    pos = {}

    # Core layer (top)
    y_core = 6
    x_spacing_core = 8.0 / (len(core_switches) + 1)
    for i, node in enumerate(core_switches):
        pos[node] = ((i + 1) * x_spacing_core - 4, y_core)

    # Pods (aggregation, edge, hosts)
    pod_width = 8.0 / num_pods
    for pod_idx, pod in enumerate(pods):
        pod_x_base = -4 + pod_idx * pod_width + pod_width / 2

        # Aggregation layer
        y_aggr = 4
        for i, node in enumerate(pod['aggr']):
            x_offset = (i - len(pod['aggr']) / 2 + 0.5) * 0.3
            pos[node] = (pod_x_base + x_offset, y_aggr)

        # Edge layer
        y_edge = 2
        for i, node in enumerate(pod['edge']):
            x_offset = (i - len(pod['edge']) / 2 + 0.5) * 0.3
            pos[node] = (pod_x_base + x_offset, y_edge)

        # Host layer
        y_host = 0
        for i, node in enumerate(pod['hosts']):
            x_offset = (i - len(pod['hosts']) / 2 + 0.5) * 0.15
            pos[node] = (pod_x_base + x_offset, y_host)

    return G, pos, node_types


def plot_tree_topology(save_path='apresentacao/tree_topology.png'):
    """Generate and save Tree topology visualization."""

    fig, ax = plt.subplots(figsize=(16, 10))

    # Create topology
    G, pos, node_types = create_tree_topology(num_hosts=32, branching_factor=2)

    # Separate nodes by type
    switches = [n for n, t in node_types.items() if t == 'switch']
    hosts = [n for n, t in node_types.items() if t == 'host']

    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.4, width=1.5, edge_color='#666666')

    # Draw switches (internal nodes)
    nx.draw_networkx_nodes(
        G, pos, nodelist=switches,
        node_color='#3498db',  # Blue
        node_size=600,
        node_shape='s',  # Square
        alpha=0.9,
        label='Switches (CPU=0, routing only)'
    )

    # Draw hosts (leaf nodes)
    nx.draw_networkx_nodes(
        G, pos, nodelist=hosts,
        node_color='#2ecc71',  # Green
        node_size=600,
        node_shape='o',  # Circle
        alpha=0.9,
        label='Hosts (CPU=50-100)'
    )

    # Add title and info
    plt.title('Tree Topology (Binary Tree)',
              fontsize=20, fontweight='bold', pad=20)

    # Add statistics box
    stats_text = f"""Topology Statistics:
• Total nodes: {len(G.nodes())}
• Hosts: {len(hosts)} (leaf nodes with CPU)
• Switches: {len(switches)} (internal nodes, routing only)
• Total links: {len(G.edges())}
• Branching factor: 2
• Structure: Hierarchical binary tree
• Bandwidth: 50-100 units per link
"""

    plt.text(0.02, 0.98, stats_text,
             transform=ax.transAxes,
             fontsize=11,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # Legend
    plt.legend(loc='upper right', fontsize=12, framealpha=0.9)

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Tree topology saved: {save_path}")
    plt.close()


def plot_fat_tree_topology(save_path='apresentacao/fat_tree_topology.png'):
    """Generate and save Fat-Tree topology visualization."""

    fig, ax = plt.subplots(figsize=(16, 12))

    # Create topology
    k = 4
    G, pos, node_types = create_fat_tree_topology(k=k)

    # Separate nodes by layer
    core = [n for n, t in node_types.items() if t['layer'] == 'core']
    aggr = [n for n, t in node_types.items() if t['layer'] == 'aggregation']
    edge = [n for n, t in node_types.items() if t['layer'] == 'edge']
    hosts = [n for n, t in node_types.items() if t['layer'] == 'host']

    # Draw edges with different colors for different connections
    # Core to Aggregation
    core_aggr_edges = [(u, v) for u, v in G.edges() if u in core or v in core]
    nx.draw_networkx_edges(G, pos, edgelist=core_aggr_edges,
                          alpha=0.3, width=2, edge_color='#e74c3c')

    # Other edges
    other_edges = [(u, v) for u, v in G.edges() if u not in core and v not in core]
    nx.draw_networkx_edges(G, pos, edgelist=other_edges,
                          alpha=0.4, width=1.5, edge_color='#666666')

    # Draw nodes by layer
    # Core switches
    nx.draw_networkx_nodes(
        G, pos, nodelist=core,
        node_color='#e74c3c',  # Red
        node_size=800,
        node_shape='D',  # Diamond
        alpha=0.9,
        label=f'Core Switches ({len(core)})'
    )

    # Aggregation switches
    nx.draw_networkx_nodes(
        G, pos, nodelist=aggr,
        node_color='#f39c12',  # Orange
        node_size=600,
        node_shape='s',  # Square
        alpha=0.9,
        label=f'Aggregation Switches ({len(aggr)})'
    )

    # Edge switches
    nx.draw_networkx_nodes(
        G, pos, nodelist=edge,
        node_color='#3498db',  # Blue
        node_size=600,
        node_shape='s',  # Square
        alpha=0.9,
        label=f'Edge Switches ({len(edge)})'
    )

    # Hosts
    nx.draw_networkx_nodes(
        G, pos, nodelist=hosts,
        node_color='#2ecc71',  # Green
        node_size=400,
        node_shape='o',  # Circle
        alpha=0.9,
        label=f'Hosts ({len(hosts)})'
    )

    # Add layer labels
    ax.text(-4.5, 6, 'Core Layer', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.3))
    ax.text(-4.5, 4, 'Aggregation Layer', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.3))
    ax.text(-4.5, 2, 'Edge Layer', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.3))
    ax.text(-4.5, 0, 'Host Layer', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.3))

    # Title
    plt.title(f'Fat-Tree Topology (k={k})',
              fontsize=20, fontweight='bold', pad=20)

    # Add statistics box
    num_pods = k
    stats_text = f"""Topology Statistics:
• Total nodes: {len(G.nodes())}
• Hosts: {len(hosts)} (k³/4 = {k}³/4)
• Switches: {len(core) + len(aggr) + len(edge)}
  - Core: {len(core)}
  - Aggregation: {len(aggr)}
  - Edge: {len(edge)}
• Total links: {len(G.edges())}
• Pods: {num_pods}
• k (ports per switch): {k}
• Structure: 3-tier datacenter topology
• Bandwidth: 200-400 units per link
• Redundancy: Multiple paths between hosts
"""

    plt.text(0.02, 0.98, stats_text,
             transform=ax.transAxes,
             fontsize=11,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # Legend
    plt.legend(loc='upper right', fontsize=12, framealpha=0.9)

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Fat-Tree topology saved: {save_path}")
    plt.close()


def plot_side_by_side_comparison(save_path='apresentacao/topologies_comparison.png'):
    """Generate side-by-side comparison of both topologies."""

    fig = plt.figure(figsize=(20, 10))

    # Tree topology (left)
    ax1 = plt.subplot(1, 2, 1)
    G_tree, pos_tree, types_tree = create_tree_topology(num_hosts=16, branching_factor=2)

    switches_tree = [n for n, t in types_tree.items() if t == 'switch']
    hosts_tree = [n for n, t in types_tree.items() if t == 'host']

    nx.draw_networkx_edges(G_tree, pos_tree, alpha=0.4, width=1.5, edge_color='#666666')
    nx.draw_networkx_nodes(G_tree, pos_tree, nodelist=switches_tree,
                          node_color='#3498db', node_size=400, node_shape='s', alpha=0.9)
    nx.draw_networkx_nodes(G_tree, pos_tree, nodelist=hosts_tree,
                          node_color='#2ecc71', node_size=400, node_shape='o', alpha=0.9)

    ax1.set_title('Tree Topology (Binary Tree)', fontsize=16, fontweight='bold', pad=15)
    ax1.text(0.5, -0.05, f'{len(hosts_tree)} hosts + {len(switches_tree)} switches = {len(G_tree.nodes())} nodes',
             transform=ax1.transAxes, ha='center', fontsize=12)
    ax1.axis('off')

    # Fat-Tree topology (right)
    ax2 = plt.subplot(1, 2, 2)
    G_fat, pos_fat, types_fat = create_fat_tree_topology(k=4)

    core = [n for n, t in types_fat.items() if t['layer'] == 'core']
    aggr = [n for n, t in types_fat.items() if t['layer'] == 'aggregation']
    edge = [n for n, t in types_fat.items() if t['layer'] == 'edge']
    hosts_fat = [n for n, t in types_fat.items() if t['layer'] == 'host']

    nx.draw_networkx_edges(G_fat, pos_fat, alpha=0.3, width=1)
    nx.draw_networkx_nodes(G_fat, pos_fat, nodelist=core,
                          node_color='#e74c3c', node_size=500, node_shape='D', alpha=0.9)
    nx.draw_networkx_nodes(G_fat, pos_fat, nodelist=aggr,
                          node_color='#f39c12', node_size=400, node_shape='s', alpha=0.9)
    nx.draw_networkx_nodes(G_fat, pos_fat, nodelist=edge,
                          node_color='#3498db', node_size=400, node_shape='s', alpha=0.9)
    nx.draw_networkx_nodes(G_fat, pos_fat, nodelist=hosts_fat,
                          node_color='#2ecc71', node_size=300, node_shape='o', alpha=0.9)

    ax2.set_title('Fat-Tree Topology (k=4)', fontsize=16, fontweight='bold', pad=15)
    ax2.text(0.5, -0.05, f'{len(hosts_fat)} hosts + {len(core)+len(aggr)+len(edge)} switches = {len(G_fat.nodes())} nodes',
             transform=ax2.transAxes, ha='center', fontsize=12)
    ax2.axis('off')

    # Overall title
    fig.suptitle('VNE Topologies Comparison', fontsize=20, fontweight='bold', y=0.98)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Comparison saved: {save_path}")
    plt.close()


if __name__ == '__main__':
    import os

    print("Generating topology visualizations for presentation...\n")

    # Create output directory
    os.makedirs('apresentacao', exist_ok=True)

    # Generate all visualizations
    plot_tree_topology('apresentacao/tree_topology.png')
    plot_fat_tree_topology('apresentacao/fat_tree_topology.png')
    plot_side_by_side_comparison('apresentacao/topologies_comparison.png')

    print("\n✅ All visualizations generated successfully!")
    print("\nGenerated files:")
    print("  1. apresentacao/tree_topology.png")
    print("  2. apresentacao/fat_tree_topology.png")
    print("  3. apresentacao/topologies_comparison.png")
