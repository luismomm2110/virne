#!/usr/bin/env python3
"""
Create 2x topologies: Tree with 64 nodes and Fat-Tree with 32 nodes
"""

import yaml

# Configuration for Tree 2x (64 nodes)
tree_2x_config = {
    'p_net_setting': {
        'topology': {
            'type': 'tree',
            'num_nodes': 64,
            'wm_alpha': 0.5,
            'wm_beta': 0.2
        },
        'node_attrs_setting': [
            {
                'name': 'cpu',
                'owner': 'node',
                'type': 'resource',
                'distribution': 'uniform',
                'dtype': 'int',
                'generative': True,
                'low': 50,
                'high': 100
            },
            {
                'name': 'max_cpu',
                'owner': 'node',
                'type': 'extrema',
                'originator': 'cpu'
            }
        ],
        'link_attrs_setting': [
            {
                'name': 'bw',
                'owner': 'link',
                'type': 'resource',
                'distribution': 'uniform',
                'dtype': 'int',
                'generative': True,
                'low': 50,
                'high': 100
            },
            {
                'name': 'max_bw',
                'owner': 'link',
                'type': 'extrema',
                'originator': 'bw'
            }
        ],
        'output': {
            'save_dir': 'dataset/p_net',
            'file_name': 'tree64_p_net.gml'
        }
    }
}

# Configuration for Fat-Tree 2x (32 nodes)
fattree_2x_config = {
    'p_net_setting': {
        'topology': {
            'type': 'fat_tree',
            'num_nodes': 32,
            'wm_alpha': 0.5,
            'wm_beta': 0.2
        },
        'node_attrs_setting': [
            {
                'name': 'cpu',
                'owner': 'node',
                'type': 'resource',
                'distribution': 'uniform',
                'dtype': 'int',
                'generative': True,
                'low': 50,
                'high': 100
            },
            {
                'name': 'max_cpu',
                'owner': 'node',
                'type': 'extrema',
                'originator': 'cpu'
            }
        ],
        'link_attrs_setting': [
            {
                'name': 'bw',
                'owner': 'link',
                'type': 'resource',
                'distribution': 'uniform',
                'dtype': 'int',
                'generative': True,
                'low': 200,
                'high': 400
            },
            {
                'name': 'max_bw',
                'owner': 'link',
                'type': 'extrema',
                'originator': 'bw'
            }
        ],
        'output': {
            'save_dir': 'dataset/p_net',
            'file_name': 'fat_tree32_p_net.gml'
        }
    }
}

# Save configurations
print("Creating 2x topology configurations...")
print("")

# Tree 2x
with open('settings/p_net_setting/tree_2x_p_net.yaml', 'w') as f:
    yaml.dump(tree_2x_config, f, default_flow_style=False)
print("✅ Created: settings/p_net_setting/tree_2x_p_net.yaml")

# Fat-Tree 2x
with open('settings/p_net_setting/fat_tree_2x_p_net.yaml', 'w') as f:
    yaml.dump(fattree_2x_config, f, default_flow_style=False)
print("✅ Created: settings/p_net_setting/fat_tree_2x_p_net.yaml")

print("")
print("╔════════════════════════════════════════════════════════════════════╗")
print("║        2X TOPOLOGIES CONFIGURATION CREATED SUCCESSFULLY            ║")
print("╚════════════════════════════════════════════════════════════════════╝")
print("")
print("New topologies configured:")
print("  • Tree 2x: 64 nodes (vs original 32)")
print("  • Fat-Tree 2x: 32 nodes (vs original 16)")
print("")
print("Next: Create VNR configurations and run simulations")
