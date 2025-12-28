#!/bin/bash

# Monitor WX500 simulation progress
# Shows which simulations have completed and estimates time remaining

echo "=========================================="
echo "WX500 SIMULATION PROGRESS MONITOR"
echo "=========================================="
echo ""

ALGORITHMS=("mip" "ga_meta" "pso_meta" "sa_meta" "pl_rank" "rw_rank_bfs" "mcts" "d_round")
TOTAL_EXPECTED=$((${#ALGORITHMS[@]} * 5))  # 8 algorithms × 5 seeds

COMPLETED=0
FAILED=0

for algo in "${ALGORITHMS[@]}"; do
    echo "Checking $algo..."
    for seed in 0 1 2 3 4; do
        if [ -f "virne/$algo/*/records/summary.csv" ]; then
            echo "  ✓ Seed $seed: COMPLETED"
            ((COMPLETED++))
        else
            echo "  ⏳ Seed $seed: RUNNING or PENDING"
        fi
    done
done

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Completed: $COMPLETED / $TOTAL_EXPECTED"
echo "Remaining: $((TOTAL_EXPECTED - COMPLETED))"
echo ""

if [ $COMPLETED -eq $TOTAL_EXPECTED ]; then
    echo "✓ All simulations completed!"
    echo "Next step: python extract_wx500_results.py"
else
    PERCENT=$((100 * COMPLETED / TOTAL_EXPECTED))
    echo "Progress: $PERCENT%"
    echo "Estimated: Still running..."
fi

# Show which simulations are currently running
echo ""
echo "=========================================="
echo "CURRENTLY RUNNING"
echo "=========================================="
ps aux | grep "main_wx500" | grep -v grep | while read line; do
    echo "✓ $line" | awk '{print $(NF-1), $(NF)}'
done
