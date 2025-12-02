# Phase 1: Winner Analysis - Rare Algorithms

**Date:** 2025-11-29
**Goal:** Identify characteristics of VNRs where rare algorithms (MIP, GA, SA) win to guide data collection

---

## Dataset Overview

**Source:** `apresentacao/simulacoes/` folder
**Total Successful VNRs:** 6,037 across 7 algorithms

### Success Distribution

| Algorithm   | Successes | Percentage |
|-------------|-----------|------------|
| RW_RANK_BFS | 1,344     | 22.3%      |
| PL_RANK     | 1,234     | 20.4%      |
| MCTS        | 1,092     | 18.1%      |
| **D_ROUND** | **678**   | **11.2%**  |
| **GA_META** | **599**   | **9.9%**   |
| **MIP**     | **545**   | **9.0%**   |
| **SA_META** | **545**   | **9.0%**   |

**KEY FINDING:** In apresentacao data, rare algorithms (MIP, GA, SA) have similar success rates to d_round! This is VERY different from the ML training data where d_round dominated (75%).

---

## Comparative Algorithm Characteristics

| Algorithm   | Avg Nodes | Avg Total Demand | Demand/Node | Node Util | Link Util | Active VNRs |
|-------------|-----------|------------------|-------------|-----------|-----------|-------------|
| MIP         | 5.0       | 98.5             | **19.3**    | **0.182** | 0.255     | 10.2        |
| GA_META     | 4.8       | **429.2**        | **82.5**    | 0.223     | 0.366     | 11.7        |
| SA_META     | 4.9       | **392.0**        | **75.4**    | 0.202     | 0.314     | 10.9        |
| PL_RANK     | 4.8       | 95.4             | 19.7        | 0.214     | 0.300     | 11.6        |
| RW_RANK_BFS | 5.0       | 99.0             | 19.7        | 0.199     | 0.273     | 11.1        |
| MCTS        | 4.6       | 92.2             | 19.6        | 0.207     | 0.363     | 11.4        |
| D_ROUND     | 4.8       | 95.1             | 19.7        | **0.173** | 0.372     | 9.9         |

---

## Key Patterns Discovered

### 1. **MIP Success Pattern**
- **Lower system load:** Node util 0.182 vs 0.204 average
- **Small VNRs:** Similar to others (5.0 nodes)
- **Low demand per node:** 19.3 (lowest)
- **Moderate active VNRs:** 10.2

**Hypothesis:** MIP wins when network has spare capacity and can find optimal solutions

### 2. **GA_META Success Pattern**
- **MUCH HIGHER total demand:** 429.2 vs ~95 average (4.5× higher!)
- **EXTREME demand per node:** 82.5 vs ~20 average (4× higher!)
- **Higher system load:** Node util 0.223
- **Most active VNRs:** 11.7

**Hypothesis:** GA wins with complex, high-demand VNRs that need sophisticated search

### 3. **SA_META Success Pattern**
- **Very high total demand:** 392.0 (4× average)
- **High demand per node:** 75.4 (3.8× average)
- **Moderate system load:** Node util 0.202
- **Many active VNRs:** 10.9

**Hypothesis:** SA wins with high-demand VNRs, similar to GA but slightly less extreme

### 4. **D_ROUND Success Pattern**
- **LOWEST system load:** Node util 0.173 (but highest link util 0.372)
- **Average VNR characteristics:** Similar to heuristics
- **Fewer active VNRs:** 9.9 (lowest)

**Hypothesis:** D_round wins in lighter-loaded scenarios with standard VNRs

---

## Critical Insight: Why Training Data Was Imbalanced

The ML training dataset had **75% d_round wins** vs **11.2% in apresentacao data**.

**Possible reasons:**
1. **Different topologies:** Training data likely had more Tree topology, apresentacao has both
2. **Different workload:** Training data had lower demands
3. **Different scenarios:** Apresentacao might have targeted edge cases

**This explains why the model has trouble generalizing!**

---

## Actionable Recommendations

### 🎯 To Increase MIP Sampling:
1. **Create "optimal-seeking" scenarios:**
   - Small VNRs (2-5 nodes)
   - Low to moderate demand (demand/node < 25)
   - Spare network capacity (node util < 0.20)
   - Few competing VNRs (inservice_count < 8)

2. **Config changes:**
   - `v_net_num_nodes: [2, 5]` (smaller range)
   - `cpu_demand: [0, 15]` (lower demands)
   - `arrival_rate: 0.02` (less congestion)

### 🎯 To Increase GA_META Sampling:
1. **Create "complex high-demand" scenarios:**
   - High total demand VNRs (demand > 300)
   - Extreme demand per node (>70)
   - Moderate to high system load (node util 0.20-0.30)
   - Many active VNRs (inservice_count > 10)

2. **Config changes:**
   - `v_net_num_nodes: [4, 8]`
   - `cpu_demand: [50, 150]` (MUCH higher!)
   - `bw_demand: [100, 400]` (MUCH higher!)
   - `arrival_rate: 0.10` (high load)

### 🎯 To Increase SA_META Sampling:
1. **Create "high-demand moderate-load" scenarios:**
   - High total demand (300-400)
   - High demand per node (60-80)
   - Moderate load (node util 0.18-0.22)

2. **Config changes:**
   - Similar to GA but slightly less extreme
   - `cpu_demand: [40, 120]`
   - `bw_demand: [80, 300]`

### 🎯 To Balance Overall Dataset:
1. **Run targeted experiments:**
   - 200 VNRs with MIP-favoring config
   - 200 VNRs with GA-favoring config
   - 200 VNRs with SA-favoring config
   - 200 VNRs with mixed scenarios

2. **Test multiple seeds** (5+) for statistical significance

3. **Verify balance:** Check if rare algorithms win more frequently
nd 
4. 
---

## Next Steps

1. **Create new YAML configs** for targeted scenarios
2. **Run pilot experiments** (50 VNRs each) to validate hypotheses
3. **Measure improvement** in algorithm diversity
4. **Iterate** based on results

---

## Files to Create

- `settings/v_sim_setting/v_sim_mip_favoring.yaml` - Low demand, low load
- `settings/v_sim_setting/v_sim_ga_favoring.yaml` - High demand, high load
- `settings/v_sim_setting/v_sim_sa_favoring.yaml` - High demand, moderate load

**End of Phase 1 Analysis**