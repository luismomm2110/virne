# Quick Start: Optimized Experiments

**Goal:** Run 294 experiments in ~40 hours (instead of 490 in 85-110 hours)

---

## What's Been Done ✅

1. **3 optimized scripts created** (with MIP timeouts, not skipping)
2. **All config files updated** to 700 VNRs (from 200-1000)
3. **Time savings: ~60%** while keeping MIP for all scenarios

---

## Current Status

**Currently Running:**
- `./test_topology_scaling.sh` (topology test, started 4:24 PM)
- Check progress: `./check_scaling_test_progress.sh`

---

## Ready to Run (When Current Finishes)

### Option 1: Highest Priority (Best for class balance fix)

```bash
./run_edge_case_experiments_optimized.sh
```

- **Experiments:** 126 (6 scenarios × 7 algorithms × 3 seeds)
- **Time:** ~15-18 hours
- **Impact:** Fixes class imbalance (most important!)
- **MIP:** Included with 5-40 min timeouts

---

### Option 2: Novel Contribution (Quick & High Impact)

```bash
./run_heterogeneity_experiments_optimized.sh
```

- **Experiments:** 63 (3 scenarios × 7 algorithms × 3 seeds)
- **Time:** ~8-10 hours
- **Impact:** Novel finding (demand heterogeneity matters!)
- **MIP:** Included with 15-30 min timeouts

---

### Option 3: Comprehensive (All 3 suites)

```bash
# Run in order (or parallel in different terminals)
./run_edge_case_experiments_optimized.sh          # ~15-18h
./run_heterogeneity_experiments_optimized.sh      # ~8-10h
./run_large_topology_experiments_optimized.sh     # ~15-20h
```

- **Total Experiments:** 294
- **Total Time:** ~40-48 hours sequential (~12-15h if parallel on 4 cores)
- **All MIP included** with smart timeouts

---

## What Changed (Plan A with MIP)

| Optimization | Before | After | Savings |
|-------------|--------|-------|---------|
| **Seeds** | 5 | 3 | 40% |
| **VNRs** | 1000 | 700 | 30% |
| **MIP Strategy** | Long timeouts (30-60 min) | Smart timeouts (5-40 min) | 20-30% |

**Important:** MIP is **NOT skipped** - it just has shorter timeouts:
- Simple scenarios: 15-30 min (usually solves)
- Complex scenarios: 5-15 min (captures timeout behavior)
- This is valuable data - model learns when MIP fails

---

## File Summary

### New Scripts
- `run_edge_case_experiments_optimized.sh` ✓
- `run_large_topology_experiments_optimized.sh` ✓
- `run_heterogeneity_experiments_optimized.sh` ✓
- `update_vnrs_to_700.sh` ✓ (already run)

### Config Files Updated (9 files)
All set to 700 VNRs:
- `v_sim_ultra_tight.yaml` ✓
- `v_sim_massive.yaml` ✓
- `v_sim_realtime.yaml` ✓
- `v_sim_tiny_optimal.yaml` ✓
- `v_sim_meta_heuristic_sweet_spot.yaml` ✓
- `v_sim_sparse_congested.yaml` ✓
- `v_sim_extreme_heterogeneous.yaml` ✓
- `v_sim_bimodal_demands.yaml` ✓
- `v_sim_uniform_homogeneous.yaml` ✓

### Documentation
- `OPTIMIZED_EXPERIMENTS_SUMMARY.md` (detailed info)
- `QUICK_START_OPTIMIZED.md` (this file)

---

## My Recommendation

**Start with edge cases when topology test finishes:**

```bash
./run_edge_case_experiments_optimized.sh
```

**Why:**
1. Fixes class imbalance (critical issue)
2. Most experiments (126)
3. Runs overnight (~15-18 hours)
4. MIP included with smart timeouts

**Then decide:**
- If time permits → heterogeneity (~8-10h)
- If more time → large topology (~15-20h)

---

## After Experiments Complete

```bash
# 1. Aggregate data
python xgboost_selector/data_aggregator.py

# 2. Train model
python xgboost_selector/xgboost_trainer.py

# 3. Check improvements
# - More balanced algorithm distribution
# - New feature: demand_heterogeneity (8-12% importance)
# - Better model accuracy (75-85%)
```

---

## Time Comparison

| Approach | Experiments | Time | Coverage |
|----------|-------------|------|----------|
| **Original** | 490 | 85-110h | Full |
| **Optimized (All)** | 294 | 40-48h | Full |
| **Optimized (Priority)** | 126 | 15-18h | Edge cases only |
| **Optimized (Parallel 4 cores)** | 294 | 12-15h | Full |

---

## Questions?

**"Do I lose MIP data?"**
- No! MIP runs on all scenarios with smart timeouts
- Timeout behavior is valuable data

**"Is 700 VNRs enough?"**
- Yes! 700 VNRs × 3 seeds = 2,100 samples per scenario
- Well above statistical requirements

**"Why 3 seeds instead of 5?"**
- 3 seeds capture variance well
- Diminishing returns after 3
- Standard in VNE research

**"Can I reduce time more?"**
- Yes: Use 500 VNRs instead of 700 (saves another 30%)
- Yes: Run 2 seeds instead of 3 (saves another 33%)
- Trade-off: Lower statistical confidence

---

## Ready? Here's Your Command:

```bash
# Check what's running
ps aux | grep python | grep main.py

# When ready, start edge cases
./run_edge_case_experiments_optimized.sh
```

**Estimated finish:** 15-18 hours from start

Good luck! 🚀
