# Pareto Efficiency Cost Analysis Guide

## Overview

This guide explains how to visualize multi-objective optimization trade-offs for Virtual Network Embedding (VNE) algorithms using Pareto efficiency cost analysis.

**Key Concept**: The Pareto cost function combines three competing objectives:
```
Cost = w1·(1 - acceptance_rate) + w2·(computational_cost/max_cost) + w3·(efficiency_loss/max_loss)
```

Lower cost = better algorithm (more efficient across all objectives)

---

## Running the Analysis

```bash
cd apresentacao/machine_learning/
python 10_pareto_efficiency_cost.py
```

### What it does:
1. Loads the trained XGBoost model and test data
2. Computes metrics for each algorithm:
   - Acceptance rate (% of successful VNRs)
   - Computational cost (estimated from problem complexity)
   - Resource efficiency (revenue / cost ratio)
3. Calculates Pareto cost with three weight configurations
4. Generates 5 visualization types + CSV export

### Output files:
All saved to `results/`:
- `pareto_2d_scatter.png` - Trade-off scatter plots
- `pareto_3d.png` - 3D multi-objective surface
- `pareto_frontier.png` - Efficient frontier and ranking
- `pareto_sensitivity.png` - Ranking under different preferences
- `pareto_radar.png` - Radar chart for top algorithms
- `pareto_analysis.csv` - Detailed metrics table

---

## Understanding the Visualizations

### 1. 2D Scatter Plots (`pareto_2d_scatter.png`)

Four subplots analyzing two-objective trade-offs:

#### Top-left: Acceptance vs Computational Cost
- **X-axis**: Acceptance rate (higher = better)
- **Y-axis**: Computational cost (lower = better)
- **Color**: Red (high cost) → Green (low cost)
- **Interpretation**: Look for algorithms in upper-left (high acceptance, low cost)

#### Top-right: Acceptance vs Resource Efficiency
- **X-axis**: Acceptance rate
- **Y-axis**: Resource efficiency (higher = better)
- **Interpretation**: Algorithms efficient at converting resources to revenue

#### Bottom-left: Computational Cost vs Resource Efficiency
- **X-axis**: Computational cost (lower = better)
- **Y-axis**: Resource efficiency
- **Interpretation**: Trade-off between efficiency and speed

#### Bottom-right: Pareto Cost Breakdown (Stacked Bar)
- Shows weighted contribution of each component
- Red = Acceptance Loss (w1=0.4)
- Orange = Time Cost (w2=0.3)
- Blue = Efficiency Loss (w3=0.3)
- **Interpretation**: Which component hurts each algorithm most?

---

### 2. 3D Pareto Surface (`pareto_3d.png`)

Shows all three objectives simultaneously:
- **X-axis**: Acceptance Rate
- **Y-axis**: Computational Cost
- **Z-axis**: Resource Efficiency
- **Color**: Pareto Cost (green = best, red = worst)

**How to read it**:
- Algorithms clustered in upper-left-back = good on all objectives
- Algorithms isolated = specialized (good at one, weak at others)
- You can rotate/zoom in your PDF viewer

---

### 3. Pareto Frontier (`pareto_frontier.png`)

Two plots identifying efficient algorithms:

#### Left: Acceptance vs Computational Cost
- Gray dots: All algorithms
- Green dots: Top 3 performers (lowest Pareto cost)
- **Interpretation**: Which algorithms dominate overall?

#### Right: Cost Ranking
- Horizontal bars sorted by Pareto cost
- Green (low cost) at bottom = better performers
- **Interpretation**: Overall ranking of algorithms

---

### 4. Sensitivity Analysis (`pareto_sensitivity.png`)

Shows how rankings change with different priorities:

Four weight configurations:
1. **Acceptance First** (w1=0.6, w2=0.2, w3=0.2)
   - Prioritize getting requests accepted
2. **Balanced** (w1=0.33, w2=0.33, w3=0.34)
   - Equal importance to all objectives
3. **Speed First** (w1=0.2, w2=0.6, w3=0.2)
   - Minimize computational cost
4. **Efficiency First** (w1=0.2, w2=0.2, w3=0.6)
   - Maximize resource efficiency

**Interpretation**:
- Algorithms at top in all charts = robust (good regardless of priorities)
- Algorithms that move around = have specific strengths

---

### 5. Radar Chart (`pareto_radar.png`)

Pentagon plot for top 4 algorithms showing:
- **Acceptance Rate**: Higher = better
- **Speed (1 - normalized cost)**: Higher = faster
- **Efficiency**: Higher = more profitable

**How to read**:
- Larger polygons = better overall
- Shape indicates algorithm strengths:
  - Balanced pentagon = good at everything
  - Tall top = good acceptance
  - Tall right = fast
  - Tall bottom = efficient

---

## Interpreting the Metrics

### Acceptance Rate
- Percentage of VNRs successfully embedded
- Higher = more requests accepted
- Trade-off: Often conflicts with speed/efficiency

### Computational Cost
**Formula**: `v_net_size_ratio × v_net_connectivity × v_net_total_demand / (p_net_available_resource + 1)`

Estimates problem difficulty:
- Larger/denser VNRs = higher cost
- Congested network = higher cost
- Low available resources = higher cost
- **Lower = faster algorithm**

### Resource Efficiency
**Formula**: `avg_revenue / avg_cost`

Measures profit per unit cost:
- **Higher = more economically efficient**
- Example: 0.72 means $0.72 profit per $1 cost
- Only computed for accepted requests

### Pareto Cost (Lower = Better)
Weighted combination of all three:
- **0.0-0.3**: Excellent (highly efficient)
- **0.3-0.5**: Good (balanced trade-offs)
- **0.5-0.7**: Acceptable (some weakness)
- **0.7-1.0**: Poor (multiple weaknesses)

---

## Real-World Interpretation: Example Results

From the sample output:

```
rw_rank_bfs: Rank 1 (Pareto Cost: 0.5250)
  - Highest resource efficiency (0.720)
  - Lowest computational cost (0.018)
  - Lower acceptance rate (24.3%)
  - Best choice for: Speed + profit
  - Use case: Low-criticality requests, real-time systems

mip: Rank 3 (Pareto Cost: 0.6562)
  - Highest acceptance rate (33.9%)
  - Highest computational cost (0.025)
  - Good resource efficiency (0.646)
  - Best choice for: Maximizing acceptances
  - Use case: Revenue optimization, less time-critical

ga_meta: Rank 4 (Pareto Cost: 0.8245)
  - Moderate on all metrics
  - Lowest resource efficiency (0.524)
  - Trade-offs not favorable
  - Recommendation: Use only if other options unavailable
```

---

## Customizing Weight Preferences

Edit `10_pareto_efficiency_cost.py` to change weights:

```python
# In plot_sensitivity_analysis():
weight_configs = [
    {'name': 'My Custom', 'w1': 0.5, 'w2': 0.3, 'w3': 0.2},
    # ... more configs
]

# Or in main():
metrics_df = compute_pareto_cost(metrics_df, w1=0.5, w2=0.2, w3=0.3)
```

**Weight Guidelines**:
- w1 (acceptance): 0.3-0.6 (usually highest)
- w2 (speed): 0.2-0.4
- w3 (efficiency): 0.2-0.4
- **Must sum to 1.0**

---

## Using Results for Algorithm Selection

### Decision Rules

**If you want: Highest acceptance rate**
→ Use MIP (Rank 3, 33.9% acceptance)

**If you want: Fastest execution**
→ Use rw_rank_bfs (Rank 1, lowest cost)

**If you want: Best profit**
→ Use rw_rank_bfs (Rank 1, efficiency 0.72)

**If you want: Balanced performance**
→ Use rw_rank_bfs or pl_rank (Rank 1-2)

### Hybrid Approach

Use an adaptive selector:
```python
if network_load < 30%:
    use rw_rank_bfs  # Fast & efficient
elif network_load < 70%:
    use mip          # Good acceptance
else:
    use pl_rank      # Balanced
```

---

## CSV Data Format

`pareto_analysis.csv` contains:

| Column | Meaning |
|--------|---------|
| algorithm | Algorithm name |
| acceptance_rate | % of accepted VNRs |
| avg_computational_cost | Estimated problem difficulty |
| resource_efficiency | Revenue/cost ratio |
| pareto_cost | Weighted multi-objective score |
| acceptance_loss | 1 - acceptance_rate |
| time_cost | Normalized computational cost |
| efficiency_loss | Normalized efficiency loss |
| rank | Overall ranking (1 = best) |

---

## Advanced Analysis

### Finding Pareto-Optimal Algorithms

Algorithms on the **true Pareto frontier** are those where:
- You can't improve one objective without worsening another

In our case, this typically includes the top 1-2 algorithms (those with lowest Pareto cost across different weight configurations).

### Trade-off Analysis

Compare algorithms on specific metrics:
```python
# Which algorithm prioritizes acceptance over speed?
# Answer: MIP (high acceptance, high cost)

# Which algorithm balances all objectives?
# Answer: rw_rank_bfs (low rank overall)
```

### Sensitivity to Network Conditions

The computational cost estimate incorporates:
- Problem size (v_net_size_ratio)
- Problem connectivity (v_net_connectivity)
- Resource demand (v_net_total_demand)
- Network congestion (p_net_available_resource)

Higher values indicate harder embedding problems → algorithms may behave differently

---

## Troubleshooting

### Issue: All algorithms have similar cost
**Cause**: Features may not be differentiating algorithms well
**Solution**: Check if acceptance rates are all very similar

### Issue: One algorithm always on Pareto frontier
**Cause**: It's a clear winner on one metric that outweighs others
**Solution**: Adjust weights in sensitivity analysis

### Issue: Efficiency values are very low (< 0.1)
**Cause**: Revenue/cost ratio indicates unprofitable embeddings
**Solution**: May need to adjust algorithm parameters or resource generation

---

## Integration with ML Selector

These insights inform XGBoost training:
- Features that show high correlation with Pareto rank
- Algorithm selection based on problem characteristics
- Weight preferences defined by business priorities

See `RUNTIME_ALGORITHM_SELECTION_PAPER.md` for ML integration details.

---

## References

**Files Generated**:
- Script: `10_pareto_efficiency_cost.py`
- Documentation: `PARETO_ANALYSIS_GUIDE.md` (this file)
- Data: `datasets/vnr_features.csv`
- Model: `models/xgb_best_overall_model.pkl`

**Related**:
- Paper: `article/RUNTIME_ALGORITHM_SELECTION_PAPER.md`
- Baseline comparison: `5_evaluate_xgboost_selector.py`
- Feature analysis: `4_analyze_feature_importance.py`

---

**Last Updated**: December 2024
**Contact**: Luis Antonio Momm Duarte
