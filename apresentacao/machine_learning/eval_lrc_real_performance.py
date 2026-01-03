"""
Evaluate LRC model on REAL PERFORMANCE
LRC = Long-Term Revenue-to-Cost Ratio (maximize profitability)
"""

import pandas as pd
import numpy as np
import pickle

print("="*80)
print("EVALUATING LRC MODEL - REAL PERFORMANCE")
print("="*80)

# Load test data (use original dataset that model was trained on)
test_df = pd.read_csv('datasets/test.csv')
algo_metrics = pd.read_csv('models/algorithm_comparison_metrics.csv')

print(f"\nTest set size: {len(test_df)}")
print(f"Algorithm metrics shape: {algo_metrics.shape}")

# Map topology codes
topo_map = {0: 'fat_tree', 1: 'tree', 2: 'waxman'}

# Define feature columns (must match training - exactly 19 features)
feature_cols = [
    # VNR characteristics (8 features)
    'v_net_num_nodes',
    'v_net_num_edges',
    'v_net_size_ratio',
    'v_net_demand_per_node',
    'v_net_demand_per_link',
    'v_net_connectivity',
    'v_net_total_demand',
    'v_net_node_to_link_demand_ratio',

    # Physical network state (4 features)
    'p_net_available_resource',
    'p_net_node_util',
    'p_net_link_util',
    'p_net_overall_util',

    # System state (2 features)
    'inservice_count',
    'num_running_p_net_nodes',

    # Time and topology (5 features)
    'v_net_lifetime',
    'v_net_time_cost',
    'v_net_time_revenue',
    'p_net_num_nodes',
    'topology_encoded'
]

# Load global LRC model
print(f"\n{'='*80}")
print("LOADING GLOBAL LRC MODEL")
print(f"{'='*80}")

model_path = "models_option2/best_for_cost_tree.pkl"
encoder_path = "models_option2/best_for_cost_encoder.pkl"

with open(model_path, 'rb') as f:
    model = pickle.load(f)
with open(encoder_path, 'rb') as f:
    encoder = pickle.load(f)

print(f"✓ Loaded LRC model and encoder")

# Make predictions
print(f"\n{'='*80}")
print("MAKING PREDICTIONS")
print(f"{'='*80}")

X_test = test_df[feature_cols].fillna(0).values
y_pred_encoded = model.predict(X_test)
y_pred = encoder.inverse_transform(y_pred_encoded)

test_df['predicted_algorithm_lrc'] = y_pred

print(f"Predictions made for {len(test_df)} instances")

# Calculate real performance using revenue_cost_ratio
print(f"\n{'='*80}")
print("CALCULATING REAL PERFORMANCE")
print(f"{'='*80}")

# Create algorithm -> LRC (revenue_cost_ratio) mapping
algo_to_lrc = dict(zip(algo_metrics['algorithm'], algo_metrics['revenue_cost_ratio']))

print(f"\nAlgorithm LRC values (revenue_cost_ratio):")
for algo, lrc in sorted(algo_to_lrc.items(), key=lambda x: x[1], reverse=True):
    print(f"  {algo:15s}: {lrc:10.4f}")

# Calculate baseline (weighted by ground truth distribution)
baseline_lrc = 0.0
for algo, count in test_df['best_for_lrc'].value_counts().items():
    weight = count / len(test_df)
    lrc = algo_to_lrc.get(algo, 0)
    baseline_lrc += weight * lrc
print(f"\nBaseline LRC (weighted by ground truth): {baseline_lrc:.4f}")

# Calculate model performance
model_lrc = 0.0
for algo, count in test_df['predicted_algorithm_lrc'].value_counts().items():
    weight = count / len(test_df)
    lrc = algo_to_lrc.get(algo, 0)
    model_lrc += weight * lrc
print(f"Model LRC (global):                     {model_lrc:.4f}")

improvement = model_lrc - baseline_lrc
improvement_pct = 100 * improvement / baseline_lrc if baseline_lrc != 0 else 0

print(f"\nImprovement: {improvement:+.4f} ({improvement_pct:+.2f}%)")
if improvement > 0:
    print("✓ SUCCESS - Real performance improved!")
else:
    print("✗ FAILED - Performance worsened")

# Detailed breakdown by topology
print(f"\n{'='*80}")
print("BREAKDOWN BY TOPOLOGY")
print(f"{'='*80}")

for topo_code, topo_name in topo_map.items():
    test_subset = test_df[test_df['topology_encoded'] == topo_code]

    if len(test_subset) == 0:
        continue

    # Baseline for this topology
    baseline_lrc_topo = 0.0
    for algo, count in test_subset['best_for_lrc'].value_counts().items():
        weight = count / len(test_subset)
        lrc = algo_to_lrc.get(algo, 0)
        baseline_lrc_topo += weight * lrc

    # Model for this topology
    model_lrc_topo = 0.0
    for algo, count in test_subset['predicted_algorithm_lrc'].value_counts().items():
        weight = count / len(test_subset)
        lrc = algo_to_lrc.get(algo, 0)
        model_lrc_topo += weight * lrc

    improvement_topo = model_lrc_topo - baseline_lrc_topo
    improvement_pct_topo = 100 * improvement_topo / baseline_lrc_topo if baseline_lrc_topo != 0 else 0

    print(f"\n{topo_name}:")
    print(f"  Baseline: {baseline_lrc_topo:.4f}")
    print(f"  Model:    {model_lrc_topo:.4f}")
    print(f"  Improvement: {improvement_topo:+.4f} ({improvement_pct_topo:+.2f}%)")

# Predictions distribution
print(f"\n{'='*80}")
print("PREDICTION DISTRIBUTION")
print(f"{'='*80}")

pred_dist = test_df['predicted_algorithm_lrc'].value_counts().sort_values(ascending=False)
print("\nAlgorithm predictions:")
for algo, count in pred_dist.items():
    pct = 100 * count / len(test_df)
    print(f"  {algo:15s}: {count:4d} ({pct:5.1f}%)")

# Ground truth distribution
print(f"\nGround truth distribution (for comparison):")
gt_dist = test_df['best_for_lrc'].value_counts().sort_values(ascending=False)
for algo, count in gt_dist.items():
    pct = 100 * count / len(test_df)
    print(f"  {algo:15s}: {count:4d} ({pct:5.1f}%)")

print(f"\n{'='*80}")
print("CONCLUSION")
print(f"{'='*80}")
print(f"""
LRC model results:
- Baseline LRC:  {baseline_lrc:.4f}
- Model LRC:     {model_lrc:.4f}
- Improvement:   {improvement:+.4f} ({improvement_pct:+.2f}%)

{'✓ SUCCESS' if improvement > 0 else '✗ FAILED'}: Real performance {'improved' if improvement > 0 else 'worsened'}
""")