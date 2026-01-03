#!/usr/bin/env python3
"""
Step 8: Generate per-VNR algorithm selections using trained XGBoost model.

This script loads the trained model and makes predictions for each VNR,
outputting detailed logs showing:
- VNR characteristics
- Network state when VNR arrives
- Predicted algorithm
- Confidence/probability of prediction
"""

import pickle
import pandas as pd
import numpy as np
import os
from datetime import datetime


def load_model_and_data():
    """Load trained model and test data."""

    print("Loading model and data...")

    # Load model
    with open('../models/xgb_best_overall_model.pkl', 'rb') as f:
        model = pickle.load(f)

    # Load label encoder
    with open('../models/xgb_best_overall_model_label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)

    # Load full featured dataset
    full_df = pd.read_csv('../datasets/vnr_features.csv')

    # Load test split
    test_df = pd.read_csv('../datasets/test.csv')

    print(f"  Model classes: {label_encoder.classes_}")
    print(f"  Test data: {len(test_df)} records")
    print(f"  Unique VNRs: {test_df.groupby(['topology', 'seed', 'v_net_id']).ngroups if all(col in test_df.columns for col in ['topology', 'seed', 'v_net_id']) else 'unknown'}")

    return model, label_encoder, test_df, full_df


def engineer_features(df):
    """Compute engineered features like training had."""
    df = df.copy()

    # Network Stress Index
    df['network_stress_index'] = (df['p_net_node_util'] + df['p_net_link_util']) / 2

    # Problem Complexity Score
    df['problem_complexity'] = df['v_net_connectivity'] * df['v_net_total_demand']

    # Resource Bottleneck Ratio
    df['resource_bottleneck_ratio'] = (
        df['v_net_demand_per_node'] / (df['v_net_demand_per_link'] + 1e-6)
    )

    # VNR Size Category
    df['vnr_size_category'] = pd.cut(
        df['v_net_num_nodes'],
        bins=[0, 4, 7, 15],
        labels=[0, 1, 2],
        ordered=False
    ).astype(int)

    # CPU Intensive Flag
    df['cpu_intensive_flag'] = (
        df['v_net_demand_per_node'] > df['v_net_demand_per_link']
    ).astype(int)

    # Bandwidth Intensive Flag
    df['bandwidth_intensive_flag'] = (
        df['v_net_demand_per_link'] > df['v_net_demand_per_node']
    ).astype(int)

    # Utilization Pressure
    df['utilization_pressure'] = df['p_net_node_util'] * df['p_net_link_util']

    # Resource Efficiency Metric
    df['resource_efficiency'] = (
        df['p_net_available_resource'] / (df['v_net_total_demand'] + 1e-6)
    )

    return df


def extract_features(df):
    """Extract feature columns used by the model."""

    # First engineer the computed features
    df = engineer_features(df)

    # Exact features the model was trained on
    feature_cols = [
        'v_net_num_nodes', 'v_net_num_edges', 'v_net_size_ratio',
        'v_net_demand_per_node', 'v_net_demand_per_link', 'v_net_connectivity',
        'v_net_total_demand', 'v_net_node_to_link_demand_ratio', 'v_net_lifetime',
        'p_net_available_resource', 'p_net_node_util', 'p_net_link_util',
        'p_net_overall_util', 'inservice_count', 'system_load',
        'num_running_p_net_nodes', 'topology_encoded',
        'network_stress_index', 'problem_complexity', 'resource_bottleneck_ratio',
        'vnr_size_category', 'cpu_intensive_flag', 'bandwidth_intensive_flag',
        'utilization_pressure', 'resource_efficiency'
    ]

    return df[feature_cols]


def predict_per_vnr(model, label_encoder, test_df):
    """
    Make predictions for each VNR and collect detailed results.

    Returns a list of dictionaries with VNR info and predictions.
    """

    print("\nProcessing VNRs and making predictions...")

    # Remove duplicates: keep only one record per VNR
    # Group by identifiers to get unique VNRs
    if all(col in test_df.columns for col in ['topology', 'seed', 'v_net_id']):
        vnr_groups = test_df.groupby(['topology', 'seed', 'v_net_id']).first().reset_index()
    else:
        # If no identifiers, just use all rows
        vnr_groups = test_df.copy()

    print(f"  Processing {len(vnr_groups)} unique VNRs...")

    predictions = []

    for idx, row in vnr_groups.iterrows():
        # Extract features for this VNR
        features_df = extract_features(pd.DataFrame([row]))

        # Make prediction
        pred_encoded = model.predict(features_df)[0]
        pred_algo = label_encoder.inverse_transform([pred_encoded])[0]

        # Get probability distribution (if available)
        pred_proba = None
        try:
            proba = model.predict_proba(features_df)[0]
            pred_proba = {algo: float(prob) for algo, prob in zip(label_encoder.classes_, proba)}
        except:
            pass

        # Collect result
        result = {
            'vnr_index': idx,
            'topology': row.get('topology', 'unknown'),
            'seed': row.get('seed', 'unknown'),
            'v_net_id': row.get('v_net_id', 'unknown'),
            'predicted_algorithm': pred_algo,
            'prediction_probabilities': pred_proba,
            # VNR characteristics
            'v_net_num_nodes': int(row['v_net_num_nodes']) if 'v_net_num_nodes' in row else None,
            'v_net_num_edges': int(row['v_net_num_edges']) if 'v_net_num_edges' in row else None,
            'v_net_connectivity': float(row['v_net_connectivity']) if 'v_net_connectivity' in row else None,
            'v_net_total_demand': float(row['v_net_total_demand']) if 'v_net_total_demand' in row else None,
            'v_net_lifetime': float(row['v_net_lifetime']) if 'v_net_lifetime' in row else None,
            # Physical network state
            'p_net_available_resource': float(row['p_net_available_resource']) if 'p_net_available_resource' in row else None,
            'p_net_overall_util': float(row['p_net_overall_util']) if 'p_net_overall_util' in row else None,
            # System state
            'inservice_count': int(row['inservice_count']) if 'inservice_count' in row else None,
            'system_load': float(row['system_load']) if 'system_load' in row else None,
        }

        predictions.append(result)

        # Print progress every 100 VNRs
        if (idx + 1) % 100 == 0:
            print(f"    Processed {idx + 1} VNRs...")

    return predictions


def print_predictions_summary(predictions, label_encoder):
    """Print summary of predictions."""

    print("\n" + "="*100)
    print("PER-VNR ALGORITHM PREDICTIONS SUMMARY")
    print("="*100)
    print(f"\nTotal VNRs processed: {len(predictions)}")

    # Count predictions by algorithm
    algo_counts = {}
    for pred in predictions:
        algo = pred['predicted_algorithm']
        algo_counts[algo] = algo_counts.get(algo, 0) + 1

    print("\nAlgorithm selection distribution:")
    print("-" * 60)
    for algo in label_encoder.classes_:
        count = algo_counts.get(algo, 0)
        pct = (count / len(predictions) * 100) if len(predictions) > 0 else 0
        print(f"  {algo:15s}: {count:4d} VNRs ({pct:5.1f}%)")

    # Group by topology if available
    if predictions[0].get('topology') and predictions[0]['topology'] != 'unknown':
        print("\n" + "="*100)
        print("PREDICTIONS BY TOPOLOGY")
        print("="*100)

        topologies = set(p['topology'] for p in predictions)
        for topo in sorted(topologies):
            topo_preds = [p for p in predictions if p['topology'] == topo]
            topo_counts = {}
            for pred in topo_preds:
                algo = pred['predicted_algorithm']
                topo_counts[algo] = topo_counts.get(algo, 0) + 1

            print(f"\n{topo.upper()} ({len(topo_preds)} VNRs):")
            print("-" * 60)
            for algo in label_encoder.classes_:
                count = topo_counts.get(algo, 0)
                pct = (count / len(topo_preds) * 100) if len(topo_preds) > 0 else 0
                print(f"  {algo:15s}: {count:4d} VNRs ({pct:5.1f}%)")


def save_csv_predictions(predictions, output_path='../results/vnr_predictions.csv'):
    """Save predictions to CSV for further analysis."""

    # Create dataframe
    rows = []
    for pred in predictions:
        row = {
            'vnr_index': pred['vnr_index'],
            'topology': pred['topology'],
            'seed': pred['seed'],
            'v_net_id': pred['v_net_id'],
            'predicted_algorithm': pred['predicted_algorithm'],
            'v_net_num_nodes': pred['v_net_num_nodes'],
            'v_net_num_edges': pred['v_net_num_edges'],
            'v_net_connectivity': pred['v_net_connectivity'],
            'v_net_total_demand': pred['v_net_total_demand'],
            'v_net_lifetime': pred['v_net_lifetime'],
            'p_net_available_resource': pred['p_net_available_resource'],
            'p_net_overall_util': pred['p_net_overall_util'],
            'inservice_count': pred['inservice_count'],
            'system_load': pred['system_load'],
        }

        # Add probabilities if available
        if pred['prediction_probabilities']:
            for algo, prob in pred['prediction_probabilities'].items():
                row[f'prob_{algo}'] = prob

        rows.append(row)

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n✓ Predictions saved to CSV: {output_path}")
    print(f"  Rows: {len(df)}, Columns: {len(df.columns)}")


def save_detailed_log(predictions, output_path='../results/vnr_predictions_detailed.txt'):
    """Save detailed predictions to text log."""

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("="*100 + "\n")
        f.write("DETAILED PER-VNR ALGORITHM PREDICTIONS\n")
        f.write("="*100 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total VNRs: {len(predictions)}\n\n")

        for idx, pred in enumerate(predictions, 1):
            f.write(f"\n{'─'*100}\n")
            f.write(f"VNR #{idx:4d} | Topology: {pred['topology']:10s} | Seed: {str(pred['seed']):5s} | VNet ID: {str(pred['v_net_id']):5s}\n")
            f.write(f"{'─'*100}\n\n")

            # VNR characteristics
            f.write("VNR CHARACTERISTICS:\n")
            f.write(f"  Size:              {pred['v_net_num_nodes']} nodes, {pred['v_net_num_edges']} edges\n")
            f.write(f"  Connectivity:      {pred['v_net_connectivity']:.4f}\n")
            f.write(f"  Total Demand:      {pred['v_net_total_demand']:.2f} units\n")
            f.write(f"  Lifetime:          {pred['v_net_lifetime']:.2f} time units\n\n")

            # Physical network state
            f.write("PHYSICAL NETWORK STATE AT ARRIVAL:\n")
            f.write(f"  Available Resource: {pred['p_net_available_resource']:.2f} units\n")
            f.write(f"  Overall Utilization: {pred['p_net_overall_util']:.2%}\n")
            f.write(f"  Active VNRs:        {pred['inservice_count']}\n")
            f.write(f"  System Load:        {pred['system_load']:.2%}\n\n")

            # Prediction
            f.write("ALGORITHM SELECTION:\n")
            f.write(f"  Selected Algorithm: {pred['predicted_algorithm']}\n")

            if pred['prediction_probabilities']:
                f.write(f"  Confidence Scores:\n")
                for algo, prob in sorted(pred['prediction_probabilities'].items(), key=lambda x: x[1], reverse=True):
                    bar_width = int(prob * 40)
                    bar = '█' * bar_width + '░' * (40 - bar_width)
                    f.write(f"    {algo:15s}: {prob:.4f} [{bar}]\n")

            f.write("\n")

    print(f"✓ Detailed log saved: {output_path}")


def main():
    """Main execution."""

    # Load model and data
    model, label_encoder, test_df, full_df = load_model_and_data()

    # Make predictions per VNR
    predictions = predict_per_vnr(model, label_encoder, test_df)

    # Print summary
    print_predictions_summary(predictions, label_encoder)

    # Save results
    print("\n" + "="*100)
    print("SAVING RESULTS")
    print("="*100)

    save_csv_predictions(predictions)
    save_detailed_log(predictions)

    print("\n" + "="*100)
    print("PREDICTION COMPLETE!")
    print("="*100)
    print("\nGenerated files:")
    print("  - results/vnr_predictions.csv (machine-readable)")
    print("  - results/vnr_predictions_detailed.txt (human-readable with details)")


if __name__ == '__main__':
    main()