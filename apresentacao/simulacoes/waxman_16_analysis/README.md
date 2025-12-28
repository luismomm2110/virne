# Waxman 16 Campaign - Analysis and Timing Clarification

## Campaign Summary

**Status:** ✅ Complete (35/35 simulations)
- **Date:** 2025-12-21
- **Topology:** 16-node Waxman random network (α=0.5, β=0.2)
- **Algorithms:** 7 (MIP, PL-RANK, GA-Meta, SA-Meta, MCTS, RW-RANK-BFS, D-Round)
- **Seeds per Algorithm:** 5 (seeds 0-4)
- **Total VNRs Processed:** 7,000 (200 per run)

---

## Files in This Directory

### Campaign Results
- **`waxman_16_detailed_results.csv`** - Full results for all 35 runs
  - Columns: algorithm, seed, acceptance_rate, r2c_ratio, success_count, etc.
  - Ready for statistical analysis

- **`waxman_16_comparison.csv`** - Aggregated comparison table
  - Summary metrics by algorithm
  - Min/max/std dev statistics
  - Good for presentations

### Reports and Analysis
- **`WAXMAN_16_PRELIMINARY_REPORT.md`** - Comprehensive campaign report
  - Performance rankings
  - Algorithm tier analysis
  - Variance analysis
  - **INCLUDES TIME METRIC CLARIFICATION**

- **`FINDINGS_SUMMARY.txt`** - Executive summary
  - Key findings formatted for quick reading
  - Performance comparison
  - Algorithm recommendations

### Time Measurement Documentation
- **`TIME_METRIC_ANALYSIS.md`** - Detailed explanation of why `total_simulation_time` is misleading
  - What the metric actually measures
  - Why it appears MIP is "fast"
  - What real metrics would show
  - Recommendations for actual speed measurement

- **`TIMING_CLARIFICATION.txt`** - Visual summary of the timing paradox
  - The problem in boxed format
  - What we measured vs. what we expected
  - Correct interpretation guide

---

## Key Finding: The Time Metric Issue

### What `total_simulation_time` Actually Is
```
total_simulation_time = v_net_arrival_time of last VNR in simulation
                     ≈ 4684 seconds for ALL algorithms
                     = Simulated timeline, NOT algorithm CPU time
```

### The Misleading Calculation
```
"time per success" = 4684 seconds / success_count

MIP:      4684 / 130.4 successes = 35.9 sec/success  ← appears fastest
D-Round:  4684 / 66.4 successes  = 70.5 sec/success  ← appears slowest

This is WRONG! It shows quality advantage, not speed.
```

### Reality Check
- MIP is an **exact solver** (exponential worst-case complexity)
- D-Round is a **greedy heuristic** (polynomial complexity)
- MIP should theoretically be **slower**, not faster
- The metric doesn't measure algorithm execution time

### What We Should Have
```
Real timing would show (expected):
- D-Round:      5-15 milliseconds per VNR
- PL-RANK:      15-50 milliseconds per VNR
- GA-Meta:      50-200 milliseconds per VNR
- MIP:          100-5000 milliseconds per VNR

NOT 35.9 seconds (that's simulator time, not algorithm time!)
```

---

## Next Steps: Implement Real Time Measurement

We've created two guides for adding proper execution time tracking:

1. **`ALGORITHM_TIME_MEASUREMENT_GUIDE.md`** (in repo root)
   - Complete implementation strategy
   - Code examples for all major components
   - Integration with cost functions
   - Expected results

2. **`QUICK_TIME_IMPLEMENTATION.md`** (in repo root)
   - Minimal code changes
   - Step-by-step instructions
   - Quick test procedure
   - Verification script

### Quick Implementation Checklist
```
- [ ] Add time.perf_counter() wrapping to solver.solve() methods
- [ ] Store elapsed time in milliseconds in solution record
- [ ] Update Counter to calculate average/p95 solve times
- [ ] Re-run Waxman 16 campaign (or subset for validation)
- [ ] Verify times are realistic (milliseconds, not seconds)
- [ ] Use real times in decision tree cost function
```

---

## Performance Results (Current Campaign)

### Algorithm Rankings (by Acceptance Rate)
| Rank | Algorithm    | Acceptance | R2C Ratio | Stability |
|------|--------------|------------|-----------|-----------|
| 1    | MIP          | 65.2%      | 0.5591    | ±6.7%     |
| 2    | PL-RANK      | 53.4%      | 0.4072    | ±6.3% ✓   |
| 3    | GA-Meta      | 50.0%      | 0.3879    | ±7.7%     |
| 4    | MCTS         | 47.7%      | 0.3121    | ±7.7%     |
| 5    | RW-RANK-BFS  | 47.5%      | 0.3815    | ±7.4%     |
| 6    | SA-Meta      | 46.1%      | 0.3707    | ±8.2%     |
| 7    | D-Round      | 33.2%      | 0.1642    | ±7.0%     |

### Key Insights
- **MIP clearly dominates** (65.2% vs 33.2% D-Round = 32% gap)
- **PL-RANK is best heuristic** with most consistent performance
- **Meta-heuristics cluster** (GA, MCTS, RW within 2.5%)
- **SA-Meta underperforms** with highest variability

---

## Using These Results

### For Academic Papers
- Use `WAXMAN_16_PRELIMINARY_REPORT.md` as basis
- Reference the time metric clarification
- Propose real timing measurement as future work

### For Algorithm Selection
- Quality-critical scenarios: **Use MIP** (65.2%)
- Speed-critical (before implementing real timing): **Use PL-RANK** (53.4%, most stable)
- Balanced scenarios: **Use GA-Meta** (50.0%, mid-tier)

### For Decision Tree Training
- Include acceptance_rate, r2c_ratio, and network parameters
- Once real timing is implemented: include solve_time_ms
- Use realistic time weights in cost function

---

## Files Generated

### In This Directory
```
apresentacao/simulacoes/waxman_16_analysis/
├── waxman_16_detailed_results.csv
├── waxman_16_comparison.csv
├── WAXMAN_16_PRELIMINARY_REPORT.md
├── FINDINGS_SUMMARY.txt
├── TIME_METRIC_ANALYSIS.md
├── TIMING_CLARIFICATION.txt
└── README.md (this file)
```

### In Repository Root
```
virne/
├── ALGORITHM_TIME_MEASUREMENT_GUIDE.md
├── QUICK_TIME_IMPLEMENTATION.md
└── CLAUDE.md (project context)
```

---

## Campaign Validation

All 35 simulations completed successfully:
- ✅ PL-RANK: 5 seeds
- ✅ SA-Meta: 5 seeds
- ✅ GA-Meta: 5 seeds
- ✅ MCTS: 5 seeds
- ✅ RW-RANK-BFS: 5 seeds
- ✅ MIP: 5 seeds
- ✅ D-Round: 5 seeds

Each run processed 200 VNRs on 16-node Waxman random topology.

---

## Questions?

Refer to:
1. `WAXMAN_16_PRELIMINARY_REPORT.md` for campaign details
2. `TIME_METRIC_ANALYSIS.md` for time metric explanation
3. `ALGORITHM_TIME_MEASUREMENT_GUIDE.md` for implementation help
4. `QUICK_TIME_IMPLEMENTATION.md` for quick start

Generated: 2025-12-21
Campaign Progress: 100% complete
