# Quick Time Measurement Implementation

## Minimal Changes to Add Algorithm Timing

### Step 1: Verify Solution Class Supports Time Field

Check if `Solution` class is dictionary-based:

```bash
grep -n "class Solution" virne/core/solution.py | head -5
```

If it's a dict subclass, you can directly add fields in the solver.

### Step 2: Add Timing to One Solver (Test Case)

**File: `virne/solver/heuristic/pl_rank.py`** (or your heuristic solver)

```python
import time  # ADD THIS IMPORT AT TOP

class PLRankSolver(Solver):
    def solve(self, instance: dict) -> Solution:
        """Solve using performance-based link ranking with timing."""

        # START TIMER
        solve_start_time = time.perf_counter()

        # Your existing solve logic
        v_net = instance['v_net']
        p_net = instance['p_net']
        solution = Solution(instance=instance)

        # ... all the solve logic ...
        # (node ranking, node mapping, link routing, etc.)

        # END TIMER - STORE IN MILLISECONDS
        solve_elapsed_ms = (time.perf_counter() - solve_start_time) * 1000
        solution['v_net_solve_time'] = solve_elapsed_ms

        return solution
```

### Step 3: Add Timing to MIP Solver

**File: `virne/solver/exact/mip.py`** (if it exists)

```python
import time  # ADD THIS IMPORT

class MIPSolver(Solver):
    def solve(self, instance: dict) -> Solution:
        """Solve using Mixed Integer Programming with timing."""

        solve_start_time = time.perf_counter()

        v_net = instance['v_net']
        p_net = instance['p_net']
        solution = Solution(instance=instance)

        # Create and solve MIP model
        # ... model formulation ...
        # ... solve ...

        # CRITICAL: Capture solve time BEFORE any post-processing
        # (unless post-processing is part of your algorithm)
        mip_solve_time_ms = (time.perf_counter() - solve_start_time) * 1000

        # Extract solution
        if model_solved_successfully:
            solution['result'] = True
            # ... extract node slots, link paths ...
        else:
            solution['result'] = False

        # Store final solve time
        solution['v_net_solve_time'] = mip_solve_time_ms

        return solution
```

### Step 4: Update Data Collection (Optional but Recommended)

Add these fields to counter summary to see timing stats:

**File: `virne/core/counter.py` - Update summary_records() method**

Find this section:
```python
def summary_records(self, records: Union[list, pd.DataFrame]):
    # ... existing code ...
    summary_info['avg_r2c_ratio'] = records.loc[records['event_type']==1, 'v_net_r2c_ratio'].mean()
```

Add after it:
```python
    # Add timing metrics
    arrival_records = records[records['event_type']==1]  # Only embedding attempts
    if 'v_net_solve_time' in arrival_records.columns:
        summary_info['avg_solve_time_ms'] = arrival_records['v_net_solve_time'].mean()
        summary_info['p95_solve_time_ms'] = arrival_records['v_net_solve_time'].quantile(0.95)
    else:
        summary_info['avg_solve_time_ms'] = 0
        summary_info['p95_solve_time_ms'] = 0
```

### Step 5: Test with Quick Run

Run just ONE algorithm with ONE seed:

```bash
# Test PL-RANK with Waxman 16, seed 0
python main_waxman_16_pl_rank.py \
  --experiment.seed=0 \
  --solver.solver_name=pl_rank
```

### Step 6: Check Results

```bash
# Find the summary file
ls -lht apresentacao/simulacoes/pl_rank/ | head -5

# Check if v_net_solve_time is in the CSV
head -1 apresentacao/simulacoes/pl_rank/pl_rank-*-summary.csv
# Should contain columns with something like:
# ...,avg_solve_time_ms,p95_solve_time_ms,...
```

### Step 7: Analyze Timing Results

```python
import pandas as pd

# Read the summary
df = pd.read_csv('apresentacao/simulacoes/pl_rank/pl_rank-reward_*-summary.csv')

print("PL-RANK Timing:")
print(f"  Average solve time: {df['avg_solve_time_ms'].values[0]:.1f} ms")
print(f"  95th percentile: {df['p95_solve_time_ms'].values[0]:.1f} ms")

# Compare with detailed records
detailed = pd.read_csv('apresentacao/simulacoes/pl_rank/*/records.csv')
print(f"\nDetailed statistics:")
print(detailed['v_net_solve_time'].describe())
```

---

## Expected Output After Implementation

### Before (Misleading):
```
Algorithm | "Time per Success" | Interpretation
────────────────────────────────────────────────
MIP       | 35.9 seconds      | WRONG: this is simulator time
D-Round   | 70.5 seconds      | WRONG: this is simulator time
```

### After (Accurate):
```
Algorithm | Avg Solve Time | P95 Solve Time | Interpretation
────────────────────────────────────────────────────────────
MIP       | 250.5 ms       | 1843.2 ms      | Exact solver - slower
D-Round   | 8.3 ms         | 12.1 ms        | Greedy - very fast
GA-Meta   | 120.5 ms       | 245.3 ms       | Meta-heuristic - medium
```

This tells the true story!

---

## Full Example: PL-RANK Solver

Here's a complete minimal example showing the timing addition:

```python
# virne/solver/heuristic/pl_rank.py
import time  # NEW IMPORT
from virne.core import Solution

class PLRankSolver(Solver):
    def solve(self, instance: dict) -> Solution:
        """
        Solve virtual network embedding using performance-based link ranking.
        Now with execution time measurement.
        """
        # START TIMING
        solve_start_time = time.perf_counter()

        v_net = instance['v_net']
        p_net = instance['p_net']
        solution = Solution(instance=instance)

        # Step 1: Rank virtual nodes by performance
        node_rank = self.rank_nodes(v_net, p_net)

        # Step 2: Node mapping (place virtual nodes)
        node_slots = self.map_nodes(v_net, p_net, node_rank)
        if not node_slots:
            solution['result'] = False
            solution['v_net_solve_time'] = (time.perf_counter() - solve_start_time) * 1000
            return solution

        # Step 3: Link mapping (route virtual links)
        link_paths, link_paths_info = self.map_links(
            v_net, p_net, node_slots
        )

        # Build solution
        solution['result'] = True
        solution['node_slots'] = node_slots
        solution['link_paths'] = link_paths
        solution['link_paths_info'] = link_paths_info

        # RECORD TIME IN MILLISECONDS
        solution['v_net_solve_time'] = (time.perf_counter() - solve_start_time) * 1000

        return solution
```

---

## Time Measurement Best Practices

### DO:
- ✅ Measure entire solve operation (all algorithm steps)
- ✅ Use `time.perf_counter()` (more accurate than `time.time()`)
- ✅ Store time in milliseconds (more readable than seconds)
- ✅ Measure on actual problem instances you care about
- ✅ Run multiple seeds to get statistical distribution

### DON'T:
- ❌ Time only one part of algorithm (measure total)
- ❌ Include unrelated overhead (I/O, network, etc.)
- ❌ Mix different hardware/conditions
- ❌ Optimize code for timing experiments (use realistic code)
- ❌ Forget to include failed attempts in average

---

## Integration with Cost Function

Once you have real times, use them in your decision tree:

```python
def algorithm_cost(acceptance_rate, solve_time_ms, scenario_type='balanced'):
    """
    Cost function for algorithm selection.

    Different scenarios have different priorities:
    - 'quality': prioritize acceptance rate
    - 'speed': prioritize fast execution
    - 'balanced': mix of both
    """
    quality_score = acceptance_rate  # 0.0 to 1.0

    # Normalize time: assume max acceptable is 500ms
    max_time_ms = 500
    time_score = min(1.0, solve_time_ms / max_time_ms)  # 0.0 to 1.0

    if scenario_type == 'quality':
        weight_quality = 0.9
        weight_speed = 0.1
    elif scenario_type == 'speed':
        weight_quality = 0.3
        weight_speed = 0.7
    else:  # balanced
        weight_quality = 0.6
        weight_speed = 0.4

    # Lower cost is better
    cost = (1.0 - quality_score) * weight_quality + time_score * weight_speed
    return cost
```

Then your decision tree learns:
- Use MIP when `(network_congestion > 0.8 AND quality_critical == True)`
- Use D-Round when `(latency_requirement < 50ms)`
- Use GA-Meta when `(network_medium_congestion AND balanced_requirements)`

This is much more meaningful!

---

## Verification Script

After implementation, run this to verify timing is working:

```python
#!/usr/bin/env python3
import pandas as pd
import numpy as np

# Load one test run
results = pd.read_csv('apresentacao/simulacoes/waxman_16_analysis/waxman_16_detailed_results.csv')

print("═" * 80)
print("ALGORITHM TIMING VERIFICATION")
print("═" * 80)

for algo in results['algorithm'].unique():
    algo_data = results[results['algorithm'] == algo]

    if 'v_net_solve_time' in algo_data.columns or 'avg_solve_time_ms' in algo_data.columns:
        # Try new column first
        if 'avg_solve_time_ms' in algo_data.columns:
            times = algo_data['avg_solve_time_ms']
        else:
            times = algo_data.get('v_net_solve_time', [0])

        print(f"\n{algo.upper()}:")
        print(f"  Average:      {times.mean():.1f} ms")
        print(f"  Min:          {times.min():.1f} ms")
        print(f"  Max:          {times.max():.1f} ms")
        print(f"  Std Dev:      {times.std():.1f} ms")
    else:
        print(f"\n{algo.upper()}: ❌ No timing data found")

print("\n" + "═" * 80)
```

Run it:
```bash
python verify_timing.py
```

You should see realistic millisecond ranges, NOT seconds!
