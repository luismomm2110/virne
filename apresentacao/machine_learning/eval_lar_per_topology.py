"""
Evaluate per-topology LAR models on REAL PERFORMANCE
"""

import pandas as pd
import numpy as np
import pickle
import sys

print("="*80)
print("EVALUATING PER-TOPOLOGY LAR MODELS - REAL PERFORMANCE")
print("="*80)

# Load test data
test_df = pd.read_csv('datasets/test_enhanced_v2.csv')
algo_metrics = pd.read_csv('models/algorithm_comparison_metrics.csv')

print(f"\nTest set size: {len(test_df)}")
print(f"Algorithm metrics shape: {algo_metrics.shape}")
print(f"\nAlgorithm metrics (LAR = revenue_cost_ratio):")
print(algo_metrics[['algorithm', 'revenue_cost_ratio']].to_string(index=False))

# Map topology codes
topo_map = {0: 'fat_tree', 1: 'tree', 2: 'waxman'}

# Define feature columns
feature_cols = [col for col in test_df.columns
                if col not in ['algorithm', 'seed', 'topology_encoded', 'num_vnrs', 'avg_time',
                              'best_for_rac', 'best_for_lrc', 'best_for_lar',
                              'best_for_ast', 'best_for_balanced']]

# Load per-topology models
print(f"\n{'='*80}")
print("LOADING MODELS")
print(f"{'='*80}")

models = {}
encoders = {}

for topo_code, topo_name in topo_map.items():
    model_path = f"models_option2/best_for_speed_lar_per_topo_{topo_name}.pkl"
    encoder_path = f"models_option2/best_for_speed_encoder_lar_per_topo_{topo_name}.pkl"

    with open(model_path, 'rb') as f:
        models[topo_code] = pickle.load(f)
    with open(encoder_path, 'rb') as f:
        encoders[topo_code] = pickle.load(f)

    print(f"✓ Loaded {topo_name} model and encoder")

# Make predictions per topology
print(f"\n{'='*80}")
print("MAKING PREDICTIONS")
print(f"{'='*80}")

predictions = []

for topo_code, topo_name in topo_map.items():
    test_subset = test_df[test_df['topology_encoded'] == topo_code].copy()
    print(f"\nTopology {topo_code} ({topo_name}): {len(test_subset)} samples")

    if len(test_subset) == 0:
        print("  Skipping (no samples)")
        continue

    # Get features and make predictions
    X = test_subset[feature_cols].fillna(0).values
    model = models[topo_code]
    encoder = encoders[topo_code]

    y_pred_encoded = model.predict(X)
    y_pred = encoder.inverse_transform(y_pred_encoded)

    # Store predictions with indices
    for idx, (orig_idx, pred_algo) in enumerate(zip(test_subset.index, y_pred)):
        predictions.append({
            'original_index': orig_idx,
            'topology': topo_code,
            'predicted_algorithm': pred_algo
        })

# Create predictions dataframe
pred_df = pd.DataFrame(predictions).set_index('original_index')
test_df_indexed = test_df.set_index(test_df.index)

# Add predictions to test data
test_df_with_pred = test_df.copy()
test_df_with_pred['predicted_algorithm_lar_per_topo'] = pred_df.loc[test_df.index, 'predicted_algorithm'].values

# Calculate real performance
print(f"\n{'='*80}")
print("CALCULATING REAL PERFORMANCE")
print(f"{'='*80}")

# Create algorithm -> LAR mapping
algo_to_lar = dict(zip(algo_metrics['algorithm'], algo_metrics['revenue_cost_ratio']))

print(f"\nAlgorithm LAR values (revenue_cost_ratio):")
for algo, lar in sorted(algo_to_lar.items(), key=lambda x: x[1], reverse=True):
    print(f"  {algo:15s}: {lar:10.4f}")

# Calculate baseline (random selection weighted by distribution)
baseline_lar = 0.0
for algo, count in test_df['best_for_lar'].value_counts().items():
    weight = count / len(test_df)
    lar = algo_to_lar.get(algo, 0)
    baseline_lar += weight * lar
print(f"\nBaseline LAR (weighted by ground truth): {baseline_lar:.4f}")

# Calculate model performance
model_lar = 0.0
for algo, count in test_df_with_pred['predicted_algorithm_lar_per_topo'].value_counts().items():
    weight = count / len(test_df_with_pred)
    lar = algo_to_lar.get(algo, 0)
    model_lar += weight * lar
print(f"Model LAR (per-topology):               {model_lar:.4f}")

improvement = model_lar - baseline_lar
improvement_pct = 100 * improvement / baseline_lar if baseline_lar != 0 else 0

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
    pred_subset = test_df_with_pred[test_df_with_pred['topology_encoded'] == topo_code]

    if len(test_subset) == 0:
        continue

    # Baseline for this topology
    baseline_lar_topo = 0.0
    for algo, count in test_subset['best_for_lar'].value_counts().items():
        weight = count / len(test_subset)
        lar = algo_to_lar.get(algo, 0)
        baseline_lar_topo += weight * lar

    # Model for this topology
    model_lar_topo = 0.0
    for algo, count in pred_subset['predicted_algorithm_lar_per_topo'].value_counts().items():
        weight = count / len(pred_subset)
        lar = algo_to_lar.get(algo, 0)
        model_lar_topo += weight * lar

    improvement_topo = model_lar_topo - baseline_lar_topo
    improvement_pct_topo = 100 * improvement_topo / baseline_lar_topo if baseline_lar_topo != 0 else 0

    print(f"\n{topo_name}:")
    print(f"  Baseline: {baseline_lar_topo:.4f}")
    print(f"  Model:    {model_lar_topo:.4f}")
    print(f"  Improvement: {improvement_topo:+.4f} ({improvement_pct_topo:+.2f}%)")

# Predictions distribution
print(f"\n{'='*80}")
print("PREDICTION DISTRIBUTION (Per-Topology Model)")
print(f"{'='*80}")

pred_dist = test_df_with_pred['predicted_algorithm_lar_per_topo'].value_counts().sort_values(ascending=False)
print("\nAlgorithm predictions:")
for algo, count in pred_dist.items():
    pct = 100 * count / len(test_df_with_pred)
    print(f"  {algo:15s}: {count:4d} ({pct:5.1f}%)")

# Ground truth distribution
print(f"\nGround truth distribution (for comparison):")
gt_dist = test_df['best_for_lar'].value_counts().sort_values(ascending=False)
for algo, count in gt_dist.items():
    pct = 100 * count / len(test_df)
    print(f"  {algo:15s}: {count:4d} ({pct:5.1f}%)")

print(f"\n{'='*80}")
print("CONCLUSION")
print(f"{'='*80}")
print(f"""
Per-topology LAR model results:
- Baseline LAR:  {baseline_lar:.4f}
- Model LAR:     {model_lar:.4f}
- Improvement:   {improvement:+.4f} ({improvement_pct:+.2f}%)

{'✓ SUCCESS' if improvement > 0 else '✗ FAILED'}: Real performance {'improved' if improvement > 0 else 'worsened'}
""")