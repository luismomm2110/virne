#!/bin/bash
#
# Run online simulations with NEW seeds to avoid data leakage
#
# Training used seeds 0-4, so online evaluation uses 100-104
#

set -e

cd "$(dirname "$0")"

echo "=============================================================================="
echo "ONLINE SIMULATIONS (NO DATA LEAKAGE)"
echo "=============================================================================="
echo ""
echo "Training used seeds 0-4 (existing simulation data)"
echo "Online evaluation uses seeds 100-104 (NEW VNRs, never seen by model)"
echo ""

# Seeds for online evaluation (DIFFERENT from training)
ONLINE_SEEDS=(100 101 102 103 104)

# Algorithms to compare
ALGORITHMS=("ga_meta" "mip" "mcts" "sa_meta")

# Check if model exists
if [ ! -f "models/xgb_best_overall_model.pkl" ]; then
    echo "ERROR: Model not found!"
    echo "Please train the model first: python 3_train_xgboost.py"
    exit 1
fi

echo "Found trained model: models/xgb_best_overall_model.pkl"
echo ""

# Create results directory
mkdir -p results

# Counter
TOTAL=$((${#ONLINE_SEEDS[@]} * (1 + ${#ALGORITHMS[@]})))
CURRENT=0

echo "=============================================================================="
echo "PHASE 1: Dynamic Selector Simulations"
echo "=============================================================================="
echo ""

for seed in "${ONLINE_SEEDS[@]}"; do
    ((CURRENT++))
    echo "[$CURRENT/$TOTAL] Running Dynamic Selector (seed $seed)..."

    python 5_online_simulator.py \
        method=dynamic \
        online_seed=$seed \
        topology=tree \
        > "results/online_sim_dynamic_seed_${seed}.log" 2>&1

    if [ $? -eq 0 ]; then
        echo "  ✓ Success: results/online_sim_dynamic_seed_${seed}.csv"
    else
        echo "  ✗ Failed: Check results/online_sim_dynamic_seed_${seed}.log"
    fi
done

echo ""
echo "=============================================================================="
echo "PHASE 2: Fixed Algorithm Baselines"
echo "=============================================================================="
echo ""

for algo in "${ALGORITHMS[@]}"; do
    for seed in "${ONLINE_SEEDS[@]}"; do
        ((CURRENT++))
        echo "[$CURRENT/$TOTAL] Running $algo (seed $seed)..."

        python 5_online_simulator.py \
            method=fixed \
            algorithm=$algo \
            online_seed=$seed \
            topology=tree \
            > "results/online_sim_${algo}_seed_${seed}.log" 2>&1

        if [ $? -eq 0 ]; then
            echo "  ✓ Success: results/online_sim_${algo}_seed_${seed}.csv"
        else
            echo "  ✗ Failed: Check results/online_sim_${algo}_seed_${seed}.log"
        fi
    done
done

echo ""
echo "=============================================================================="
echo "SIMULATIONS COMPLETE"
echo "=============================================================================="
echo ""
echo "Results saved in results/"
echo ""

# Count successful simulations
DYNAMIC_COUNT=$(ls results/online_sim_dynamic_seed_*.csv 2>/dev/null | wc -l)
FIXED_COUNT=$(ls results/online_sim_*_seed_*.csv 2>/dev/null | grep -v dynamic | wc -l)

echo "Successful simulations:"
echo "  - Dynamic Selector: $DYNAMIC_COUNT / ${#ONLINE_SEEDS[@]}"
echo "  - Fixed Algorithms: $FIXED_COUNT / $((${#ONLINE_SEEDS[@]} * ${#ALGORITHMS[@]}))"
echo ""

if [ "$DYNAMIC_COUNT" -gt 0 ] && [ "$FIXED_COUNT" -gt 0 ]; then
    echo "✓ Ready for comparison!"
    echo ""
    echo "Next step:"
    echo "  python 6_compare_with_baselines.py"
else
    echo "⚠️  Some simulations failed. Check log files in results/"
fi

echo ""
