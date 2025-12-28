#!/usr/bin/env python3
"""
Inference Script for Option 2: Multiple Objective Trees

Shows how to use the trained objective-specific trees for real-time
algorithm selection based on current network state and priorities.

Example usage:
    python inference_option2.py --congested
    python inference_option2.py --resource-constrained
    python inference_option2.py --real-time
    python inference_option2.py --balanced
"""

import pandas as pd
import numpy as np
import pickle
import argparse


class AlgorithmSelector:
    """Select VNE algorithm based on network state and priorities."""

    def __init__(self, model_dir='apresentacao/machine_learning/models_option2'):
        """Load all trained objective-specific trees."""
        self.model_dir = model_dir

        # Load models and encoders
        self.models = {}
        self.encoders = {}

        for objective in ['best_for_acceptance', 'best_for_cost', 'best_for_speed', 'best_balanced']:
            model_path = f'{model_dir}/{objective}_tree.pkl'
            encoder_path = f'{model_dir}/{objective}_encoder.pkl'

            with open(model_path, 'rb') as f:
                self.models[objective] = pickle.load(f)

            with open(encoder_path, 'rb') as f:
                self.encoders[objective] = pickle.load(f)

        print("✓ Loaded all objective-specific trees")
        print(f"  - best_for_acceptance: {len(self.encoders['best_for_acceptance'].classes_)} algorithms")
        print(f"  - best_for_cost: {len(self.encoders['best_for_cost'].classes_)} algorithms")
        print(f"  - best_for_speed: {len(self.encoders['best_for_speed'].classes_)} algorithms")
        print(f"  - best_balanced: {len(self.encoders['best_balanced'].classes_)} algorithms")

    def select_algorithm(self, features_dict, priority='balanced', network_state=None):
        """
        Select best algorithm based on priority and network state.

        Args:
            features_dict: Dictionary with VNR features
            priority: 'acceptance', 'cost', 'speed', or 'balanced'
            network_state: Dictionary with network info (optional for diagnostics)

        Returns:
            selected_algorithm: String name of algorithm to use
            explanation: String explaining the decision
        """

        if priority == 'acceptance':
            objective = 'best_for_acceptance'
            explanation = "Maximizing acceptance rate (network congested or critical VNR)"
        elif priority == 'cost':
            objective = 'best_for_cost'
            explanation = "Minimizing cost (resource-constrained network)"
        elif priority == 'speed':
            objective = 'best_for_speed'
            explanation = "Minimizing execution time (real-time SLA)"
        elif priority == 'balanced':
            objective = 'best_balanced'
            explanation = "Balanced across all objectives (normal operation)"
        else:
            raise ValueError(f"Unknown priority: {priority}")

        # Prepare features
        features_df = pd.DataFrame([features_dict])

        # Predict
        y_pred_encoded = self.models[objective].predict(features_df)[0]
        y_pred = self.encoders[objective].inverse_transform([y_pred_encoded])[0]

        return y_pred, explanation

    def diagnose(self, features_dict, network_state=None):
        """
        Show predictions from all objective trees for comparison.
        """
        print("\n" + "=" * 70)
        print("ALGORITHM SELECTION DIAGNOSIS")
        print("=" * 70)

        if network_state:
            print(f"\nNetwork State:")
            for key, val in network_state.items():
                print(f"  {key}: {val}")

        print(f"\nVNR Characteristics:")
        for key, val in features_dict.items():
            if isinstance(val, float):
                print(f"  {key}: {val:.4f}")
            else:
                print(f"  {key}: {val}")

        print(f"\n{'Objective':<25} {'Algorithm':<20} {'Explanation'}")
        print("-" * 70)

        for objective in ['best_for_acceptance', 'best_for_cost', 'best_for_speed', 'best_balanced']:
            features_df = pd.DataFrame([features_dict])
            y_pred_encoded = self.models[objective].predict(features_df)[0]
            y_pred = self.encoders[objective].inverse_transform([y_pred_encoded])[0]

            if objective == 'best_for_acceptance':
                explanation = "High acceptance"
            elif objective == 'best_for_cost':
                explanation = "Low cost"
            elif objective == 'best_for_speed':
                explanation = "Low latency"
            else:
                explanation = "Balanced"

            print(f"{objective:<25} {y_pred:<20} {explanation}")

        print("\n" + "=" * 70)


def test_example():
    """Test with an example VNR request."""

    # Load a sample from the dataset
    df = pd.read_csv('apresentacao/machine_learning/datasets/vnr_features.csv')

    # Select features
    features = [
        'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
        'v_net_demand_per_node', 'v_net_demand_per_link', 'v_net_connectivity',
        'v_net_total_demand', 'v_net_node_to_link_demand_ratio', 'v_net_lifetime',
        'p_net_available_resource', 'p_net_node_resource_utilization',
        'p_net_link_resource_utilization', 'p_net_overall_util', 'p_net_node_util',
        'p_net_link_util', 'inservice_count', 'system_load', 'num_running_p_net_nodes',
        'topology_encoded'
    ]

    # Initialize selector
    selector = AlgorithmSelector()

    # Test 4 different scenarios
    print("\n" + "=" * 80)
    print("SCENARIO 1: Congested Network (High Utilization)")
    print("=" * 80)

    # Pick a sample with high utilization
    high_util_sample = df[df['p_net_overall_util'] > 0.6].sample(1).iloc[0]
    features_dict = high_util_sample[features].to_dict()
    network_state = {
        'Network utilization': f"{high_util_sample['p_net_overall_util']*100:.1f}%",
        'Available resources': f"{high_util_sample['p_net_available_resource']:.0f}",
        'VNR nodes': int(high_util_sample['v_net_num_nodes']),
        'VNR demand': f"{high_util_sample['v_net_demand']:.0f}"
    }

    algo, explanation = selector.select_algorithm(features_dict, priority='acceptance', network_state=network_state)
    print(f"\n→ Selected: {algo}")
    print(f"  Reason: {explanation}")
    print(f"  Rationale: When network is congested, maximize acceptance rate to serve more requests")

    # Show all options
    selector.diagnose(features_dict, network_state)

    print("\n" + "=" * 80)
    print("SCENARIO 2: Resource-Constrained Network")
    print("=" * 80)

    # Pick a sample with low available resources
    min_resources = df['p_net_available_resource'].min()
    max_resources = df['p_net_available_resource'].max()
    threshold = min_resources + (max_resources - min_resources) * 0.2  # Lower 20%
    candidates = df[df['p_net_available_resource'] < threshold]
    if len(candidates) > 0:
        low_resource_sample = candidates.sample(1).iloc[0]
    else:
        low_resource_sample = df.sample(1).iloc[0]
    features_dict = low_resource_sample[features].to_dict()
    network_state = {
        'Available resources': f"{low_resource_sample['p_net_available_resource']:.0f}",
        'Node utilization': f"{low_resource_sample['p_net_node_util']*100:.1f}%",
        'Link utilization': f"{low_resource_sample['p_net_link_util']*100:.1f}%",
        'VNR demand': f"{low_resource_sample['v_net_demand']:.0f}"
    }

    algo, explanation = selector.select_algorithm(features_dict, priority='cost', network_state=network_state)
    print(f"\n→ Selected: {algo}")
    print(f"  Reason: {explanation}")
    print(f"  Rationale: With limited resources, minimize cost to make room for future requests")

    selector.diagnose(features_dict, network_state)

    print("\n" + "=" * 80)
    print("SCENARIO 3: Real-Time SLA Requirement")
    print("=" * 80)

    # Any sample works for this scenario
    realtime_sample = df.sample(1).iloc[0]
    features_dict = realtime_sample[features].to_dict()
    network_state = {
        'SLA requirement': '< 1 second response time',
        'Current network load': f"{realtime_sample['system_load']:.2f}",
        'VNR complexity': int(realtime_sample['problem_complexity'] * 100) if 'problem_complexity' in realtime_sample else 'medium'
    }

    algo, explanation = selector.select_algorithm(features_dict, priority='speed', network_state=network_state)
    print(f"\n→ Selected: {algo}")
    print(f"  Reason: {explanation}")
    print(f"  Rationale: Must meet strict latency SLA, so choose fastest algorithm")

    selector.diagnose(features_dict, network_state)

    print("\n" + "=" * 80)
    print("SCENARIO 4: Balanced SLA (Default)")
    print("=" * 80)

    balanced_sample = df.sample(1).iloc[0]
    features_dict = balanced_sample[features].to_dict()
    network_state = {
        'Network state': 'Normal operation',
        'Utilization': f"{balanced_sample['p_net_overall_util']*100:.1f}%",
        'Available resources': f"{balanced_sample['p_net_available_resource']:.0f}"
    }

    algo, explanation = selector.select_algorithm(features_dict, priority='balanced', network_state=network_state)
    print(f"\n→ Selected: {algo}")
    print(f"  Reason: {explanation}")
    print(f"  Rationale: No specific constraints, balance acceptance rate, cost, and speed")

    selector.diagnose(features_dict, network_state)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Algorithm selector with Option 2 objective trees')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')
    parser.add_argument('--congested', action='store_true', help='Scenario: Congested network')
    parser.add_argument('--resource-constrained', action='store_true', help='Scenario: Resource-constrained')
    parser.add_argument('--real-time', action='store_true', help='Scenario: Real-time SLA')
    parser.add_argument('--balanced', action='store_true', help='Scenario: Balanced SLA')

    args = parser.parse_args()

    if args.test or not any([args.congested, args.resource_constrained, args.real_time, args.balanced]):
        test_example()
    else:
        print("Run with --test to see example scenarios")
