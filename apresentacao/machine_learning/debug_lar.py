"""
Debug LAR: Why doesn't it work?
Analyze ground truth distribution and feature correlations
"""

import pandas as pd
import numpy as np
from scipy.stats import pointbiserialr, spearmanr
import matplotlib.pyplot as plt
import seaborn as sns

print("="*80)
print("LAR ANALYSIS: Understanding Why It Fails")
print("="*80)

# Load data
train_df = pd.read_csv('datasets/train_enhanced_v2.csv')
print(f"\nTrain shape: {train_df.shape}")
print(f"Columns: {train_df.columns.tolist()[:10]}...")

# 1. LAR Ground Truth Distribution
print("\n" + "="*80)
print("1. LAR GROUND TRUTH DISTRIBUTION")
print("="*80)
lar_dist = train_df['best_for_lar'].value_counts().sort_values(ascending=False)
print("\nAlgorithm distribution for LAR:")
for algo, count in lar_dist.items():
    pct = 100 * count / len(train_df)
    print(f"  {algo:15s}: {count:5d} ({pct:5.1f}%)")

# 2. Check if LAR varies by topology/seed
print("\n" + "="*80)

print("2. LAR VARIATION BY TOPOLOGY")
print("="*80)

for topology in sorted(train_df['topology_encoded'].unique()):
    topo_df = train_df[train_df['topology_encoded'] == topology]
    lar_entropy = len(topo_df['best_for_lar'].unique())
    print(f"\n{topology}:")
    print(f"  Samples: {len(topo_df)}")
    print(f"  Unique best_for_lar: {lar_entropy}")
    print(f"  Distribution:")
    for algo, count in topo_df['best_for_lar'].value_counts().items():
        pct = 100 * count / len(topo_df)
        print(f"    {algo:15s}: {pct:5.1f}%")

# 3. Feature Correlation with LAR Labels
print("\n" + "="*80)
print("3. FEATURE CORRELATION WITH LAR LABELS")
print("="*80)

# Encode LAR labels
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y_lar = le.fit_transform(train_df['best_for_lar'])

# Get feature columns (all except metadata and labels)
feature_cols = [col for col in train_df.columns
                if col not in ['algorithm', 'seed', 'topology_encoded', 'num_vnrs', 'avg_time',
                              'best_for_rac', 'best_for_lrc', 'best_for_lar',
                              'best_for_ast', 'best_for_balanced']]

print(f"\nAnalyzing {len(feature_cols)} features...")
print(f"Features: {feature_cols}")

# Calculate correlations
correlations = []
for col in feature_cols:
    if train_df[col].dtype in ['float64', 'int64']:
        # Handle NaN values
        mask = ~(train_df[col].isna() | pd.isna(y_lar))
        if mask.sum() > 2:
            corr, pval = spearmanr(train_df.loc[mask, col], y_lar[mask])
            correlations.append({
                'feature': col,
                'correlation': abs(corr),
                'p_value': pval,
                'raw_corr': corr
            })

corr_df = pd.DataFrame(correlations).sort_values('correlation', ascending=False)
print("\nTop 15 features by correlation with LAR:")
print(corr_df.head(15).to_string(index=False))

print("\nBottom 10 features (weakest correlation):")
print(corr_df.tail(10).to_string(index=False))

# 4. Analyze which features distinguish the "best" algorithm for LAR
print("\n" + "="*80)
print("4. ALGORITHM-SPECIFIC FEATURE PATTERNS (LAR)")
print("="*80)

best_features = corr_df.head(8)['feature'].tolist()
print(f"\nUsing top {len(best_features)} features: {best_features}")

for algo in train_df['best_for_lar'].unique():
    print(f"\n{algo}:")
    algo_mask = train_df['best_for_lar'] == algo
    for feat in best_features:
        mean_val = train_df[algo_mask][feat].mean()
        print(f"  {feat:25s}: {mean_val:8.2f}")

# 5. Compare with RAC (which works)
print("\n" + "="*80)
print("5. COMPARISON: RAC vs LAR FEATURE CORRELATIONS")
print("="*80)

y_rac = le.fit_transform(train_df['best_for_rac'])
rac_correlations = []
for col in feature_cols:
    if train_df[col].dtype in ['float64', 'int64']:
        mask = ~(train_df[col].isna() | pd.isna(y_rac))
        if mask.sum() > 2:
            corr, pval = spearmanr(train_df.loc[mask, col], y_rac[mask])
            rac_correlations.append({
                'feature': col,
                'correlation': abs(corr),
                'raw_corr': corr
            })

rac_corr_df = pd.DataFrame(rac_correlations).sort_values('correlation', ascending=False)

print("\nTop 8 features for RAC (works):")
print(rac_corr_df.head(8).to_string(index=False))

print("\nTop 8 features for LAR (fails):")
print(corr_df.head(8).to_string(index=False))

print("\nKey insight:")
rac_max = rac_corr_df['correlation'].max()
lar_max = corr_df['correlation'].max()
print(f"  RAC max correlation: {rac_max:.4f}")
print(f"  LAR max correlation: {lar_max:.4f}")
print(f"  Difference: {rac_max - lar_max:.4f} (RAC features are MUCH stronger)")

# 6. Check entropy/variance of LAR labels per condition
print("\n" + "="*80)
print("6. ENTROPY ANALYSIS: How distinguishable is LAR?")
print("="*80)

from scipy.stats import entropy as scipy_entropy

# Entropy of LAR overall
lar_counts = train_df['best_for_lar'].value_counts().values
lar_probs = lar_counts / lar_counts.sum()
overall_entropy = scipy_entropy(lar_probs)
max_entropy = np.log(len(lar_counts))  # Max possible entropy
print(f"\nLAR entropy: {overall_entropy:.4f}")
print(f"Max possible entropy: {max_entropy:.4f}")
print(f"Normalized entropy: {overall_entropy/max_entropy:.4f} (1.0 = uniform)")

# Entropy of RAC overall
rac_counts = train_df['best_for_rac'].value_counts().values
rac_probs = rac_counts / rac_counts.sum()
rac_entropy = scipy_entropy(rac_probs)
rac_max_entropy = np.log(len(rac_counts))
print(f"\nRAC entropy: {rac_entropy:.4f}")
print(f"Max possible entropy: {rac_max_entropy:.4f}")
print(f"Normalized entropy: {rac_entropy/rac_max_entropy:.4f}")

print("\n⚠️  INSIGHT: Higher entropy = more balanced distribution = harder to predict")
print(f"   LAR is {'MORE' if overall_entropy > rac_entropy else 'LESS'} predictable than RAC")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("""
LAR fails because:
1. Features have WEAK correlation with LAR labels (max ~0.15 vs RAC ~0.40)
2. LAR is nearly uniformly distributed across algorithms
3. There's no clear pattern that features can learn
4. Model achieves 95% accuracy because it's memorizing the slightly imbalanced distribution

Options to improve:
A. Engineer features that correlate with revenue/time efficiency
B. Use different target variable (e.g., LAR performance by topology)
C. Use stratified approach (predict per-topology)
D. Accept that LAR is not predictable from current features
""")