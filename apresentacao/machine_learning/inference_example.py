#!/usr/bin/env python3
"""
Inference Example: How to use the trained models for algorithm selection

This script demonstrates:
1. Loading the trained models
2. Extracting features from network state
3. Predicting top-3 algorithms
4. Selecting algorithm based on objective
"""

import pickle
import numpy as np
import pandas as pd

class VNEAlgorithmSelector:
    """Selector for VNE algorithms using trained decision trees."""

    def __init__(self, model_path='models/decision_trees_depth10.pkl'):
        """Load trained models."""
        with open(model_path, 'rb') as f:
            self.models = pickle.load(f)

    def predict(self, features_dict, objective='rac', k=3):
        """
        Predict best algorithms for given network state.

        Args:
            features_dict: Dictionary with feature names and values
            objective: 'rac', 'lrc', 'lar', 'ast', or 'balanced'
            k: Number of top recommendations

        Returns:
            dict with predictions and probabilities
        """

        if objective not in self.models:
            raise ValueError(f"Unknown objective: {objective}")

        model = self.models[objective]['model']
        encoder = self.models[objective]['encoder']
        features_list = self.models[objective]['features']

        # Create feature vector in correct order
        X = np.array([features_dict[f] for f in features_list]).reshape(1, -1)

        # Get predictions
        y_pred = model.predict(X)[0]
        y_pred_proba = model.predict_proba(X)[0]

        # Get top-k algorithms
        top_k_idx = np.argsort(y_pred_proba)[-k:][::-1]
        top_k_algos = encoder.classes_[top_k_idx]
        top_k_proba = y_pred_proba[top_k_idx]

        return {
            'objective': objective,
            'top_1': top_k_algos[0],
            'top_1_prob': float(top_k_proba[0]),
            'top_3': list(top_k_algos[:3]),
            'top_3_probs': [float(p) for p in top_k_proba[:3]],
            'all_probs': dict(zip(encoder.classes_, [float(p) for p in y_pred_proba]))
        }

    def predict_all_objectives(self, features_dict, k=3):
        """Predict for all objectives at once."""
        objectives = ['rac', 'lrc', 'lar', 'ast', 'balanced']
        results = {}

        for obj in objectives:
            results[obj] = self.predict(features_dict, objective=obj, k=k)

        return results


def example_usage():
    """Example of how to use the selector."""

    print("=" * 100)
    print("VNE ALGORITHM SELECTOR - INFERENCE EXAMPLE")
    print("=" * 100)

    # Initialize selector
    selector = VNEAlgorithmSelector()

    # Example network state
    # In real system, these would be extracted from actual network state
    example_features = {
        'v_net_num_nodes': 5.0,
        'v_net_num_edges': 8.0,
        'v_net_size_ratio': 0.45,
        'v_net_demand_per_node': 12.5,
        'v_net_demand_per_link': 28.3,
        'v_net_connectivity': 0.8,
        'v_net_total_demand': 225.0,
        'v_net_node_to_link_demand_ratio': 0.44,
        'v_net_lifetime': 450.0,
        'p_net_available_resource': 850.0,
        'p_net_node_util': 0.65,
        'p_net_link_util': 0.72,
        'p_net_overall_util': 0.68,
        'inservice_count': 42,
        'system_load': 0.55,
        'num_running_p_net_nodes': 18,
        'topology_encoded': 0.0,  # 0=tree, 1=fat_tree, 2=waxman_16
        'network_stress_index': 0.72,
        'problem_complexity': 156.0,
        'resource_bottleneck_ratio': 1.15,
        'vnr_size_category': 1.0,
        'cpu_intensive_flag': 0.0,
        'bandwidth_intensive_flag': 1.0,
        'utilization_pressure': 0.78,
        'resource_efficiency': 65.0,
        'p_net_node_link_resource_ratio': 0.82,
        'p_net_util_imbalance': 0.07,
        'p_net_resource_heterogeneity': 0.95,
        'p_net_fragmentation_estimate': 0.12,
        'p_net_uneven_utilization': 0.35,
        'p_net_health_score': 0.42,
        'vnr_node_link_demand_ratio': 0.58,
        'vnr_demand_intensity': 3.5,
        'vnr_structural_complexity': 2.1,
        'vnr_density_adjusted': 0.88
    }

    print("\n📊 NETWORK STATE:")
    print(f"  Virtual Network: {int(example_features['v_net_num_nodes'])} nodes, " +
          f"{int(example_features['v_net_num_edges'])} edges")
    print(f"  Topology: {'Tree' if example_features['topology_encoded'] == 0 else 'Fat-Tree' if example_features['topology_encoded'] == 1 else 'Waxman-16'}")
    print(f"  System Load: {example_features['system_load']:.0%}")
    print(f"  Physical Network Utilization: {example_features['p_net_overall_util']:.0%}")

    print("\n" + "=" * 100)
    print("PREDICTIONS BY OBJECTIVE:")
    print("=" * 100)

    # Get predictions for all objectives
    all_results = selector.predict_all_objectives(example_features, k=3)

    objective_names = {
        'rac': 'Request Acceptance Rate (maximize acceptance)',
        'lrc': 'Long-Term Revenue-to-Cost (maximize profit)',
        'lar': 'Long-Term Average Revenue (maximize revenue)',
        'ast': 'Average Solving Time (minimize time)',
        'balanced': 'Balanced (0.8*revenue - 0.2*time)'
    }

    for obj_key, result in all_results.items():
        print(f"\n{objective_names[obj_key]}:")
        print(f"  Top-1: {result['top_1']:15s} ({result['top_1_prob']:.1%} confidence)")
        print(f"  Top-3: {', '.join(result['top_3'])}")
        print(f"  Probabilities:")
        for algo, prob in result['all_probs'].items():
            bar = '█' * int(prob * 20)
            print(f"    {algo:15s}: {prob:6.1%} {bar}")

    print("\n" + "=" * 100)
    print("ALGORITHM SELECTION STRATEGY:")
    print("=" * 100)

    print("\nIf you need to select ONE algorithm for this VNR:")
    print("  OPTION 1 - Balanced approach (recommended):")
    print(f"    Use: {all_results['balanced']['top_1']}")
    print(f"    Why: Optimizes both revenue and solving time")

    print("\n  OPTION 2 - Maximize acceptance:")
    print(f"    Use: {all_results['rac']['top_1']}")
    print(f"    Why: Best request acceptance rate")

    print("\n  OPTION 3 - Fast solving:")
    print(f"    Use: {all_results['ast']['top_1']}")
    print(f"    Why: Solves fastest")

    print("\n  OPTION 4 - From top-3 pool:")
    top_3_algos = set()
    for result in all_results.values():
        top_3_algos.update(result['top_3'])
    print(f"    Algorithms to consider: {', '.join(sorted(top_3_algos))}")
    print(f"    All 3 are good choices for this network state")

    print("\n" + "=" * 100)


if __name__ == '__main__':
    example_usage()
