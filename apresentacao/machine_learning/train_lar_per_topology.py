"""
Train per-topology LAR models
Each topology gets its own decision tree trained on subset where that topology is known good
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
from sklearn.metrics import accuracy_score, classification_report

print("="*80)
print("TRAINING PER-TOPOLOGY LAR MODELS")
print("="*80)

# Load datasets
train_df = pd.read_csv('datasets/train_enhanced_v2.csv')
val_df = pd.read_csv('datasets/val_enhanced_v2.csv')
test_df = pd.read_csv('datasets/test_enhanced_v2.csv')

# Define feature columns
feature_cols = [col for col in train_df.columns
                if col not in ['algorithm', 'seed', 'topology_encoded', 'num_vnrs', 'avg_time',
                              'best_for_rac', 'best_for_lrc', 'best_for_lar',
                              'best_for_ast', 'best_for_balanced']]

# Map topology codes
topo_map = {0: 'fat_tree', 1: 'tree', 2: 'waxman'}

# Track models
models = {}
encoders = {}
accuracies = {}

for topo_code, topo_name in topo_map.items():
    print(f"\n{'='*80}")
    print(f"TOPOLOGY {topo_code}: {topo_name}")
    print(f"{'='*80}")

    # Get subset for this topology
    train_subset = train_df[train_df['topology_encoded'] == topo_code].copy()
    val_subset = val_df[val_df['topology_encoded'] == topo_code].copy()
    test_subset = test_df[test_df['topology_encoded'] == topo_code].copy()

    print(f"Train size: {len(train_subset)}")
    print(f"Val size: {len(val_subset)}")
    print(f"Test size: {len(test_subset)}")

    # Show distribution
    print(f"\nLAR distribution in training set:")
    dist = train_subset['best_for_lar'].value_counts().sort_values(ascending=False)
    for algo, count in dist.items():
        pct = 100 * count / len(train_subset)
        print(f"  {algo:15s}: {count:4d} ({pct:5.1f}%)")

    # Prepare data
    X_train = train_subset[feature_cols].fillna(0).values
    y_train = train_subset['best_for_lar'].values

    X_val = val_subset[feature_cols].fillna(0).values
    y_val = val_subset['best_for_lar'].values

    X_test = test_subset[feature_cols].fillna(0).values
    y_test = test_subset['best_for_lar'].values

    # Encode labels
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    y_val_encoded = le.transform(y_val)
    y_test_encoded = le.transform(y_test)

    # Train decision tree
    print(f"\nTraining Decision Tree with max_depth=8...")
    model = DecisionTreeClassifier(
        max_depth=8,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    )
    model.fit(X_train, y_train_encoded)

    # Evaluate
    train_acc = accuracy_score(y_train_encoded, model.predict(X_train))
    val_acc = accuracy_score(y_val_encoded, model.predict(X_val))
    test_acc = accuracy_score(y_test_encoded, model.predict(X_test))

    print(f"Train accuracy: {train_acc:.2%}")
    print(f"Val accuracy: {val_acc:.2%}")
    print(f"Test accuracy: {test_acc:.2%}")

    # Store
    models[topo_code] = model
    encoders[topo_code] = le
    accuracies[topo_code] = {'train': train_acc, 'val': val_acc, 'test': test_acc}

    # Show feature importance
    importances = model.feature_importances_
    top_features = np.argsort(importances)[-10:][::-1]
    print(f"\nTop 10 important features:")
    for idx in top_features:
        if importances[idx] > 0:
            print(f"  {feature_cols[idx]:30s}: {importances[idx]:.4f}")

# Save models
print(f"\n{'='*80}")
print("SAVING MODELS")
print(f"{'='*80}")

for topo_code, model in models.items():
    topo_name = topo_map[topo_code]
    model_path = f"models_option2/best_for_speed_lar_per_topo_{topo_name}.pkl"
    encoder_path = f"models_option2/best_for_speed_encoder_lar_per_topo_{topo_name}.pkl"

    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    with open(encoder_path, 'wb') as f:
        pickle.dump(encoders[topo_code], f)

    print(f"✓ {model_path}")
    print(f"✓ {encoder_path}")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print("\nAccuracies by topology:")
for topo_code, topo_name in topo_map.items():
    acc = accuracies[topo_code]
    print(f"\n{topo_name}:")
    print(f"  Train: {acc['train']:.2%}")
    print(f"  Val:   {acc['val']:.2%}")
    print(f"  Test:  {acc['test']:.2%}")