# How to Run All Fat-Tree Experiments

## Step-by-Step Instructions

### Step 0: Check Tree Saturation Status
```bash
./monitor_experiments.sh
```
Wait until tree saturation is complete (running count = 0).

---

### Step 1: Run Fat-Tree Tight Resources (Priority 1)
**Just run this single command:**
```bash
./run_fat_tree_tight.sh
```

**What it does:**
- Starts 12 experiments in background
- 4 algorithms (MIP, GA, MCTS, PL-Rank)
- 3 seeds each
- VNR: 2-10 nodes on fat-tree with tight resources (CPU 30-60, BW 100-200)

**Expected time:** ~2-3 hours total

**Monitor progress:**
```bash
./monitor_experiments.sh
```

**Wait for completion** before proceeding to Step 2.

---

### Step 2: Run Fat-Tree Complex VNRs (Priority 2)
**Just run this single command:**
```bash
./run_fat_tree_complex.sh
```

**What it does:**
- Starts 9 experiments in background
- 3 algorithms (MIP, GA, MCTS) - only these work on complex VNRs
- 3 seeds each
- VNR: 8-20 nodes on fat-tree (large VNRs)

**Expected time:** ~3-4 hours total

**Monitor progress:**
```bash
./monitor_experiments.sh
```

**Wait for completion** before proceeding to Step 3.

---

### Step 3: Run Fat-Tree High Load (Priority 3)
**Just run this single command:**
```bash
./run_fat_tree_high_load.sh
```

**What it does:**
- Starts 15 experiments in background
- 5 algorithms (MIP, GA, MCTS, PL-Rank, SA)
- 3 seeds each
- VNR: 5-15 nodes, high arrival rate λ=0.08

**Expected time:** ~2-3 hours total

---

## That's It!

After these 3 steps, you'll have:
- ✅ 12 tight resource experiments
- ✅ 9 complex VNR experiments  
- ✅ 15 high load experiments
- **Total: 36 new fat-tree experiments**

## Optional: Fat-Tree Saturation

If you want to also run saturation on fat-tree (VNR 15-30 nodes):

```bash
# Create the script
cat > run_fat_tree_saturation.sh << 'SCRIPT'
#!/bin/bash
echo "Fat-Tree SATURATION - VNR 15-30 nodes"
python main_tree_saturation_mip.py --config-name=main_fat_tree_saturation experiment.seed=0 &
sleep 2
python main_tree_saturation_mip.py --config-name=main_fat_tree_saturation experiment.seed=1 &
sleep 2
python main_tree_saturation_mip.py --config-name=main_fat_tree_saturation experiment.seed=2 &
python main_tree_saturation_ga.py --config-name=main_fat_tree_saturation experiment.seed=0 &
sleep 2
python main_tree_saturation_ga.py --config-name=main_fat_tree_saturation experiment.seed=1 &
sleep 2
python main_tree_saturation_ga.py --config-name=main_fat_tree_saturation experiment.seed=2 &
python main_tree_saturation_mcts.py --config-name=main_fat_tree_saturation experiment.seed=0 &
sleep 2
python main_tree_saturation_mcts.py --config-name=main_fat_tree_saturation experiment.seed=1 &
sleep 2
python main_tree_saturation_mcts.py --config-name=main_fat_tree_saturation experiment.seed=2 &
echo "9 saturation experiments started"
SCRIPT

chmod +x run_fat_tree_saturation.sh
./run_fat_tree_saturation.sh
```

---

## Quick Reference

| Step | Command | Experiments | Time |
|------|---------|-------------|------|
| 0 | `./monitor_experiments.sh` | Check status | - |
| 1 | `./run_fat_tree_tight.sh` | 12 (tight resources) | 2-3h |
| 2 | `./run_fat_tree_complex.sh` | 9 (complex VNRs) | 3-4h |
| 3 | `./run_fat_tree_high_load.sh` | 15 (high load) | 2-3h |

**Total time:** ~8-10 hours for all experiments

**Total experiments added:** 36 fat-tree runs (or 45 with saturation)

---

## Final Dataset

After completion:
- Tree experiments: 154 runs
- Fat-tree experiments: 61-70 runs (depending on saturation)
- **Total: 215-224 experiments**
- **Balance: 70% tree, 30% fat-tree** ✓

Perfect for training your XGBoost VNE algorithm selector!

