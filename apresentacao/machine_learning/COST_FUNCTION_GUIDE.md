# Cost Function Guide: Revenue-Time Optimization

## Overview

**Step 10** now uses a **Revenue-Time cost function** to select the best VNE algorithm based on maximizing revenue while minimizing time.

## Cost Function Formula

```
Cost = -w1·(revenue/max_revenue) + w2·(time/max_time)

where:
- w1 = weight for revenue (default: 0.6)
- w2 = weight for time (default: 0.4)
- w1 + w2 = 1.0

Lower cost = better algorithm
```

## Components

### 1. Revenue (Maximization)
- **Metric**: Average revenue per successfully embedded VNR
- **Objective**: MAXIMIZE
- **Normalization**: Divide by max revenue across all algorithms
- **Contribution**: `-w1 * revenue_norm`
  - Negative sign because we want to maximize (lower cost = higher revenue)
  - w1 controls priority (higher w1 = prioritize revenue)

### 2. Time (Minimization)
- **Metric**: Average problem difficulty (computational cost proxy)
- **Calculation**: `VNR_size × connectivity × demand / (available_resources + 1)`
- **Objective**: MINIMIZE
- **Normalization**: Divide by max time across all algorithms
- **Contribution**: `+w2 * time_norm`
  - Positive sign because we want to minimize
  - w2 controls priority (higher w2 = prioritize speed)

## Weight Tuning

### Default Configuration (w1=0.6, w2=0.4)
- Prioritizes revenue generation (60%)
- Minimizes execution time (40%)
- Best for: Revenue-focused scenarios

### Alternative Configurations

```python
# Speed priority
w1=0.3, w2=0.7   # Favor fast algorithms (e.g., RW_RANK_BFS)

# Balanced
w1=0.5, w2=0.5   # Equal importance to revenue and time

# Revenue extreme
w1=0.8, w2=0.2   # Strong revenue focus (e.g., MIP)
```

## Improving Model Accuracy

Your current accuracy metrics are low (10-17% for multi-objective trees). Here's how to improve:

### 1. Problem: Class Imbalance
- **Issue**: On Waxman-16, MIP wins 100% of time → tree always predicts MIP
- **Solution**: Reframe as **ranking problem** instead of classification
  - Instead of "predict the best algorithm" (0% for 2nd best)
  - Try "predict top-3 best algorithms" or "rank algorithms"
  - Evaluate with ranking metrics (top-1, top-2 accuracy)

### 2. Problem: Feature Engineering
- **Current features**: Basic topology and VNR characteristics
- **Missing context**:
  - Network utilization (congestion level)
  - Resource fragmentation
  - VNR size/connectivity relative to network
  - Current network state (available resources by region)
- **Solution**: Add derived features that capture decision boundaries
  ```python
  # Example new features
  utilization_ratio = used_resources / total_resources
  fragmentation_score = std(available_resources_per_node)
  vnr_complexity = v_net_size * v_net_connectivity * avg_demand
  network_density = total_links / (nodes * (nodes-1) / 2)
  ```

### 3. Problem: Single Tree Can't Capture Nuance
- **Issue**: One tree tries to predict from {MIP, PL_RANK, GA_META, ...}
- **Solution**: Train multiple trees per objective
  - Tree 1: Predict "best for revenue"
  - Tree 2: Predict "best for speed"
  - Tree 3: Predict "best for acceptance"
  - At runtime: Combine based on current priorities

### 4. Problem: Training Set Imbalance
- **Current data**: Waxman-16 shows MIP dominates 100% (5/5 seeds)
- **Solution**:
  - Collect more diverse topologies (tree, fat-tree, random-tree)
  - Vary network conditions (congestion, load, resource distribution)
  - Create synthetic "hard cases" where MIP fails
  - Sample training data to balance classes

### 5. Problem: Not Capturing Context Switches
- **Issue**: Decision tree sees same features → same prediction
- **Solution**: Add network state features that change decision
  - Peak utilization in last window
  - Resources remaining (global and per-node)
  - Recent acceptance rate trends
  - Time since algorithm's last success/failure

## Metrics to Track

Instead of just accuracy, track:

```python
# Ranking metrics (better for imbalanced data)
top_1_accuracy = (predicted_rank == 1).mean()
top_2_accuracy = (predicted_rank <= 2).mean()
top_3_accuracy = (predicted_rank <= 3).mean()

# Cost metrics
predicted_cost = -w1 * (actual_revenue/max_rev) + w2 * (actual_time/max_time)
oracle_cost = best_possible_cost_for_sample
regret = (predicted_cost - oracle_cost) / oracle_cost  # % worse than optimal

# Per-objective metrics
revenue_accuracy = correlation(predicted_revenue, actual_revenue)
time_accuracy = correlation(predicted_time, actual_time)
```

## Implementation Steps

### Step 1: Reframe as Ranking Problem
```python
# Current: classification accuracy (10%)
from sklearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier(max_depth=5)

# Better: ranking-based evaluation
from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y_algorithm)

# Predict probabilities and rank
y_pred_proba = model.predict_proba(X)  # Shape: (n_samples, n_classes)
predicted_ranks = np.argsort(-y_pred_proba, axis=1)  # Best to worst

# Evaluate ranking
true_rank = np.where(y_encoded == true_algo_index)[0][0]
predicted_rank = np.where(predicted_ranks[0] == true_algo_index)[0][0]
is_top_1 = (predicted_rank == 0)
is_top_2 = (predicted_rank <= 1)
is_top_3 = (predicted_rank <= 2)
```

### Step 2: Add Context Features
```python
# Current minimal features
features = [
    'v_net_size_ratio',
    'v_net_connectivity',
    'v_net_total_demand',
    'p_net_available_resource'
]

# Add context-aware features
def create_extended_features(df):
    df['utilization'] = (df['p_net_used_resource'] /
                         (df['p_net_available_resource'] + df['p_net_used_resource']))
    df['vnr_to_network_ratio'] = df['v_net_size_ratio'] / df['p_net_nodes']
    df['resource_tightness'] = 1.0 / (df['p_net_available_resource'] + 1)
    df['problem_difficulty'] = (df['v_net_size_ratio'] *
                                df['v_net_connectivity'] *
                                df['v_net_total_demand'] /
                                (df['p_net_available_resource'] + 1))
    return df
```

### Step 3: Train Objective-Specific Trees
```python
from sklearn.tree import DecisionTreeClassifier

objectives = ['best_for_revenue', 'best_for_speed', 'best_for_acceptance']

models = {}
for obj in objectives:
    # Create binary target: is this algorithm best for this objective?
    y = df['algorithm'] == df[obj]

    model = DecisionTreeClassifier(max_depth=7, min_samples_leaf=10)
    model.fit(X, y)
    models[obj] = model

# At prediction time
def predict_best_algorithm(x, priority='revenue'):
    scores = {}
    for algo in algorithms:
        revenue_score = models['best_for_revenue'].predict_proba(x)[0, 1]
        speed_score = models['best_for_speed'].predict_proba(x)[0, 1]
        acceptance_score = models['best_for_acceptance'].predict_proba(x)[0, 1]

        # Weighted combination based on priority
        if priority == 'revenue':
            score = 0.6 * revenue_score + 0.3 * acceptance_score + 0.1 * speed_score
        elif priority == 'speed':
            score = 0.6 * speed_score + 0.2 * revenue_score + 0.2 * acceptance_score
        else:  # balanced
            score = 0.4 * revenue_score + 0.3 * speed_score + 0.3 * acceptance_score

        scores[algo] = score

    return max(scores, key=scores.get)
```

### Step 4: Evaluate with Real VNE Performance
```python
# Instead of tree accuracy, measure actual VNE outcomes
def evaluate_selector(df_test, model):
    results = []

    for idx, row in df_test.iterrows():
        X = row[feature_cols].values.reshape(1, -1)

        # Tree prediction
        predicted_algo = model.predict(X)[0]

        # Actual outcome with that algorithm
        actual_revenue = row[f'{predicted_algo}_revenue']
        actual_time = row[f'{predicted_algo}_time']

        # Oracle: best algorithm for this instance
        oracle_algo = row['best_algorithm']
        oracle_revenue = row[f'{oracle_algo}_revenue']
        oracle_time = row[f'{oracle_algo}_time']

        # Metrics
        revenue_regret = (oracle_revenue - actual_revenue) / oracle_revenue
        time_regret = (actual_time - oracle_time) / oracle_time

        results.append({
            'predicted': predicted_algo,
            'oracle': oracle_algo,
            'correct': predicted_algo == oracle_algo,
            'revenue_regret': revenue_regret,
            'time_regret': time_regret
        })

    df_results = pd.DataFrame(results)

    print(f"Accuracy: {df_results['correct'].mean():.1%}")
    print(f"Avg Revenue Regret: {df_results['revenue_regret'].mean():.1%}")
    print(f"Avg Time Regret: {df_results['time_regret'].mean():.1%}")
```

## Summary

The **Revenue-Time cost function** is now correctly implemented in Step 10. To improve model accuracy from 10% to 50%+:

1. **Reframe**: Use ranking-based evaluation (top-k accuracy)
2. **Features**: Add context-aware features (utilization, fragmentation, complexity)
3. **Architecture**: Train multiple objective-specific trees
4. **Data**: Collect more diverse scenarios and topologies
5. **Evaluation**: Measure regret against oracle, not just classification accuracy

This approach treats algorithm selection as a context-dependent problem, not a fixed classification.
