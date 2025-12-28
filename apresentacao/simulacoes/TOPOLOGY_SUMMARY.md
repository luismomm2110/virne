# Simulation Results Summary - All Topologies

## Overview

This directory contains comprehensive VNE simulation results across three topologies:

1. **Tree** (32 nodes, sparse connectivity)
2. **Fat Tree** (16 nodes, 200-400 bandwidth)
3. **Waxman-16** (16 nodes, 500 links, realistic topology)

## Results by Topology

### Tree Topology (32 nodes)
- **Location:** Algorithm-specific subdirectories (d_round/, ga_meta/, mcts/, mip/, pl_rank/, pso_meta/, rw_rank_bfs/, sa_meta/)
- **Data:** Individual run folders with simulation outputs
- **Characteristics:** Sparse connectivity, variable algorithm performance

### Fat Tree Topology (16 nodes)
- **Location:** Algorithm-specific subdirectories (d_round/, ga_meta/, mcts/, mip/, pl_rank/, pso_meta/, rw_rank_bfs/, sa_meta/)
- **Data:** Individual run folders with simulation outputs
- **Characteristics:** Higher bandwidth resources (200-400), MIP dominates

### Waxman-16 Topology (16 nodes)
- **Location:** `waxman_16_analysis/`
- **Files:**
  - `waxman_16_comparison.csv` - Aggregated results per algorithm
  - `waxman_16_detailed_results.csv` - Per-seed detailed results
  - `WAXMAN_16_PRELIMINARY_REPORT.md` - Comprehensive analysis
  - `FINDINGS_SUMMARY.txt` - Key findings
  - Additional analysis documents

## Cross-Topology Performance Comparison

| Topology | Nodes | Best Algorithm | Avg Acceptance | Notes |
|----------|-------|----------------|-----------------|-------|
| Tree | 32 | Variable | 15-80% | High variability, depends on conditions |
| Fat Tree | 16 | MIP | 65-75% | Consistent MIP dominance |
| Waxman-16 | 16 | MIP | 65.2% | Clear MIP winner across all seeds |

## Key Files

### Global Summary
- `global_summary.csv` - Master dataset with all simulation runs and metrics

### Topology-Specific Analysis
- `waxman_16_analysis/` - Complete Waxman-16 analysis
- Algorithm directories - Individual run data for Tree and Fat Tree topologies

### Meta Information
- `TOPOLOGY_SUMMARY.md` - This file
- `ACADEMIC_ANALYSIS_OPTION2.md` - (parent directory) Academic analysis incorporating all topologies

## How to Use These Results

1. **For Algorithm Comparison:** See `global_summary.csv` for comprehensive metrics
2. **For Waxman-16 Deep Dive:** See `waxman_16_analysis/waxman_16_detailed_results.csv`
3. **For Tree Topology:** Check individual algorithm subdirectories
4. **For Decision Tree Training:** Use `global_summary.csv` with topology and algorithm labels

## Metrics Included

- Acceptance rate (% VNRs successfully embedded)
- Resource efficiency (R2C ratio)
- Simulation time
- Node/link utilization
- Embedding cost metrics
- Multiple random seeds for statistical validity

