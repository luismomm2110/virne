# WX500 Simulation Status & Next Steps

## Current Status

🔄 **WX500 Simulations Running in Background**

- **Start Time:** 2025-12-20 22:14:31
- **Total Expected:** 40 simulations (8 algorithms × 5 seeds)
- **Algorithms:** mip, ga_meta, pso_meta, sa_meta, pl_rank, rw_rank_bfs, mcts, d_round
- **Topology:** WX500 (500-node Waxman graph)
- **VNRs per simulation:** 1000
- **Seeds:** 0, 1, 2, 3, 4

## Monitoring Progress

### Option 1: Quick Check
```bash
bash monitor_wx500_progress.sh
```

### Option 2: Watch for Results
```bash
# In separate terminal, watch for summary files
watch -n 10 'find virne -name "summary.csv" | wc -l'
```

### Option 3: Check Running Processes
```bash
ps aux | grep main_wx500
```

## Expected Timeline

**Typical Execution Times per Simulation:**
- Fast algorithms (heuristics): 5-15 minutes
  - rw_rank_bfs: ~10 minutes
  - pl_rank: ~10 minutes
- Medium algorithms: 15-30 minutes
  - ga_meta: ~20 minutes
  - pso_meta: ~20 minutes
- Slow algorithms: 30-60+ minutes
  - mip: ~45 minutes (solver overhead)
  - sa_meta: ~30 minutes
- Variable algorithms: 20-40 minutes
  - mcts: ~25 minutes
  - d_round: ~20 minutes

**Total Runtime Estimate:**
- Sequential (one at a time): 15-20 hours
- Current mode (one per algorithm): ~1 hour per algorithm = 8 hours total

## Results Location

When simulations complete, results will be in:

```
virne/
├── mip/
│   ├── {run_id_seed_0}/records/summary.csv
│   ├── {run_id_seed_1}/records/summary.csv
│   └── ...
├── ga_meta/
├── pso_meta/
├── sa_meta/
├── pl_rank/
├── rw_rank_bfs/
├── mcts/
└── d_round/
```

Each `summary.csv` contains:
- `acceptance_rate` - % of VNRs accepted
- `revenue` - Total revenue generated
- `cost` - Total resource cost
- `substrate_node_utilization` - Network utilization
- `substrate_link_utilization` - Link utilization
- `average_embedding_time` - Average time per embedding

## Next Steps (After Simulations Complete)

### Step 1: Extract Results
```bash
python extract_wx500_results.py
```

This will:
- ✓ Find all completed simulations
- ✓ Extract summary.csv from each
- ✓ Combine into single results file
- ✓ Show algorithm comparison (acceptance, time, utilization)
- ✓ Save to `virne/wx500_results_summary.csv`

### Step 2: Extract Individual VNR Data
```bash
python apresentacao/machine_learning/1_extract_vnr_data.py
```

This will:
- ✓ Parse all individual VNR records
- ✓ Create feature vectors
- ✓ Combine tree + fat_tree + WX500 data

### Step 3: Prepare Combined Dataset
```bash
python apresentacao/machine_learning/2_prepare_dataset.py
```

This will:
- ✓ Calculate target variables (best_for_acceptance, etc.)
- ✓ Create new vnr_features.csv with all topologies
- ✓ Generate train/val/test splits

### Step 4: Retrain Option 2 Trees
```bash
python train_multiple_objective_trees.py
```

This will:
- ✓ Retrain all 4 objective-specific trees
- ✓ Use expanded dataset (tree + fat_tree + WX500)
- ✓ Save improved models to models_option2/

### Step 5: Test Improvements
```bash
python inference_option2.py --test
```

This will:
- ✓ Show predictions with new models
- ✓ Compare decision-making across topologies
- ✓ Demonstrate improved accuracy

## Commands to Run Later

### Check Simulation Progress
```bash
# Count completed simulations
find virne -name "summary.csv" | wc -l

# Show which algorithms are done
for algo in mip ga_meta pso_meta sa_meta pl_rank rw_rank_bfs mcts d_round; do
    count=$(find virne/$algo -name "summary.csv" 2>/dev/null | wc -l)
    echo "$algo: $count/5 seeds completed"
done
```

### Monitor in Real-Time
```bash
# Watch summary file count
watch -n 5 'echo "Completed: $(find virne -name summary.csv | wc -l) / 40"'

# Watch directory sizes
watch -n 10 'du -sh virne/*/ | sort -h'
```

### Extract Results When Ready
```bash
# Option A: Automatic (run this script when simulations are done)
python extract_wx500_results.py

# Option B: Manual inspection first
find virne -name "summary.csv" -type f | head -5 | xargs head -5

# Option C: Count completed
find virne -name "summary.csv" -type f | wc -l
```

## What This Adds to Your Dataset

### Current Dataset (tree + fat_tree):
- Samples: 112,287
- Topologies: 2 (31 nodes, 20 nodes)
- Algorithms: 8
- Best algorithm distribution: Dominated by one per topology

### After WX500:
- Samples: 112,287 + ~8,000 (8 algos × 1000 VNRs per seed × 5 seeds ≈ 40,000)
- **Estimated total: ~152,287 samples**
- Topologies: 3 (31 nodes, 20 nodes, **500 nodes**)
- **New diversity:** Large-scale topology data
- **Better class balance:** Different algorithms may dominate on WX500

### Expected Impact:
- ✅ Better decision tree generalization
- ✅ More diverse algorithm preference patterns
- ✅ More robust Option 2 trees
- ✅ Better understanding of topology effects
- ✅ Improved real-world applicability

## Troubleshooting

### Simulations Seem Stalled
```bash
# Check if any processes are running
ps aux | grep main_wx500 | grep -v grep

# Check output logs
tail -f virne/mip/*/logs/running.log

# Check disk space
df -h
```

### Extract Script Finds No Results
```bash
# Verify simulations completed
find virne -type d -name "*wx500*" | head -10

# Check if summary files exist
find virne -name "summary.csv" | head -10

# Check specific algorithm
ls -la virne/mip/*/records/summary.csv
```

### Want to Stop Simulations
```bash
# Kill all WX500 simulations
pkill -f main_wx500

# Or specific algorithm
pkill -f main_wx500_mip
```

## Expected Benefits

After retraining with WX500 data:

**Better Algorithm Selection:**
- Trees learn topology-specific patterns
- Different trees recommend different algorithms based on network size
- Improved accuracy when deployed on real networks

**More Insights:**
- Understand which algorithms excel on large-scale networks
- See how algorithm performance changes with scale
- Better trade-offs for acceptance vs cost vs speed

**Real-World Ready:**
- Trained on 3 different topology types
- More robust decision boundaries
- Better generalization to unseen networks

## Questions?

If something doesn't work:
1. Check simulation logs: `tail -f virne/mip/*/logs/running.log`
2. Check if processes are running: `ps aux | grep main_wx500`
3. Check disk space: `df -h`
4. Check for errors: `find virne -name "*.log" | xargs grep -i error`

---

**Last Updated:** 2025-12-20 22:14:31
**Status:** Simulations Running ⏳
