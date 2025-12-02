# SA and PSO Multiprocessing Fix

## Problem

SA and PSO simulations were failing with pickle errors:
```
TypeError: cannot pickle '_thread.lock' object
```

This happened because:
- **SA** used `threading.Thread` (line 53 in `simulated_annealing_solver.py`)
- **PSO** used `multiprocessing.Process` (line 82 in `particle_swarm_optimization_solver.py`)

Both created unpicklable thread locks that multiprocessing couldn't serialize.

## Solution

Created patched versions that use **sequential execution** instead of threading/multiprocessing:

### Files Created

1. **`apresentacao/algoritmos/main_tree_sa_no_mp.py`**
   - Patches SA to run individuals sequentially (no threading)

2. **`apresentacao/algoritmos/main_fat_tree_sa_no_mp.py`**
   - Same patch for fat-tree topology

3. **`apresentacao/algoritmos/main_tree_pso_no_mp.py`**
   - Patches PSO to run particles sequentially (no mp.Process)

4. **`apresentacao/algoritmos/main_fat_tree_pso_no_mp.py`**
   - Same patch for fat-tree topology

5. **`apresentacao/algoritmos/run_sa_pso_no_mp.sh`**
   - Shell script to run all 20 simulations (SA + PSO × tree + fat-tree × seeds 0-4)

### How the Patch Works

**SA Patch:**
```python
def patched_meta_run(self, v_net, p_net):
    """Sequential version without threading"""
    self.initialize(v_net, p_net)
    # Run individuals sequentially instead of with threads
    for individual in self.individuals:
        self.evolve(individual)
    self.update_best_individual(self.individuals)
    return self.best_individual.best_solution
```

**PSO Patch:**
```python
def patched_meta_run(self, v_net, p_net):
    """Sequential version without multiprocessing"""
    self.initialize(v_net, p_net)
    # Run iterations sequentially instead of with mp.Process
    for iteration_id in range(self.max_iteration):
        for particle in self.particles:
            self.evolve(particle)
        self.update_best_individual(self.particles)
    return self.best_individual.best_solution
```

The patch is applied BEFORE the solver is instantiated, so it affects the class definition itself.

## Running the Simulations

### Option 1: All at once (currently running)
```bash
cd /Users/luismomm/PycharmProjects/virne
nohup bash apresentacao/algoritmos/run_sa_pso_no_mp.sh > /tmp/sa_pso_all.log 2>&1 &
```

### Option 2: Individual simulations
```bash
# SA tree
PYTHONPATH=/Users/luismomm/PycharmProjects/virne \
python apresentacao/algoritmos/main_tree_sa_no_mp.py experiment.seed=0

# SA fat-tree
PYTHONPATH=/Users/luismomm/PycharmProjects/virne \
python apresentacao/algoritmos/main_fat_tree_sa_no_mp.py experiment.seed=0

# PSO tree
PYTHONPATH=/Users/luismomm/PycharmProjects/virne \
python apresentacao/algoritmos/main_tree_pso_no_mp.py experiment.seed=0

# PSO fat-tree
PYTHONPATH=/Users/luismomm/PycharmProjects/virne \
python apresentacao/algoritmos/main_fat_tree_pso_no_mp.py experiment.seed=0
```

## Expected Results

**Total simulations**: 20
- SA tree: 5 (seeds 0-4)
- SA fat-tree: 5 (seeds 0-4)
- PSO tree: 5 (seeds 0-4)
- PSO fat-tree: 5 (seeds 0-4)

**Output directories**:
- `virne/sa_meta/*/records/temp-*.csv`
- `virne/pso_meta/*/records/temp-*.csv`

**Performance**: Sequential execution is ~8x slower than parallel (8 individuals/particles), but avoids pickle errors.
- Estimated time per simulation: ~5-10 minutes
- Total time: ~2-3 hours for all 20

## Monitoring Progress

Check log files:
```bash
# Overall progress
tail -f /tmp/sa_pso_all.log

# Individual simulation logs
tail -f apresentacao/algoritmos/logs/tree_sa_seed0_no_mp.log
tail -f apresentacao/algoritmos/logs/fat_tree_sa_seed0_no_mp.log
tail -f apresentacao/algoritmos/logs/tree_pso_seed0_no_mp.log
tail -f apresentacao/algoritmos/logs/fat_tree_pso_seed0_no_mp.log
```

Count completed simulations:
```bash
find virne/sa_meta -name "temp-*.csv" -type f | wc -l  # Should be 10
find virne/pso_meta -name "temp-*.csv" -type f | wc -l # Should be 10
```

## Configuration Fix

Also fixed `apresentacao/algoritmos/settings/main_tree_sa.yaml`:
- Changed `solver_name: 'pso_meta'` → `solver_name: 'sa_meta'`
- Changed `experiment_name: pso_tree_experiment` → `experiment_name: sa_tree_experiment`

This was causing SA to instantiate PSO instead.

## Next Steps

After all simulations complete:

1. **Extract data** (includes SA and PSO now):
   ```bash
   cd apresentacao/machine_learning
   python 1_extract_vnr_data.py
   ```
   Expected: ~14,000 VNRs (was ~11,000 without SA/PSO)

2. **Continue ML pipeline**:
   ```bash
   python 2_prepare_dataset.py
   python 3_train_xgboost.py
   ./run_online_simulations.sh
   python 6_compare_with_baselines.py
   ```

## Status

- ✅ Patch created and tested
- ✅ Configuration fixed
- ✅ Shell script created
- 🔄 Running all 20 simulations (in progress)
- ⏳ Waiting for completion (~2-3 hours)

Last updated: 2025-11-24
