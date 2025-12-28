#!/bin/bash

# Run Randomized Rounding (r_round) on all 3 scenarios
# This adds the approximation algorithm to complement d_round

echo "============================================"
echo "Running r_round on ALL scenarios"
echo "============================================"
echo ""

SEEDS=(0 1 2 3 4)
SCENARIOS=("high_load" "tight" "complex")
CONFIG_NAMES=("main_tree_high_load" "main_tree_tight" "main_tree_complex")

for i in "${!SCENARIOS[@]}"
do
    scenario="${SCENARIOS[$i]}"
    config="${CONFIG_NAMES[$i]}"

    echo "============================================"
    echo "Scenario: $scenario"
    echo "============================================"

    for seed in "${SEEDS[@]}"
    do
        echo "  Seed $seed..."

        python main_tree_sa.py \
            --config-name=$config \
            solver.solver_name=r_round \
            experiment.seed=$seed \
            experiment.run_id="r_round_${scenario}_seed_$seed"

        if [ $? -eq 0 ]; then
            echo "  ✓ Seed $seed completed"
        else
            echo "  ✗ Seed $seed failed!"
        fi
    done

    echo ""
done

echo "============================================"
echo "r_round experiments complete!"
echo "============================================"
echo ""
echo "Results saved in virne/r_round/r_round_*_seed_*/"
echo ""
echo "Total: 15 experiments (3 scenarios × 5 seeds)"
echo ""
