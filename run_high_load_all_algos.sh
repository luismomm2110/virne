#!/bin/bash

# Run all algorithms on HIGH-LOAD scenario
# Higher arrival rate (0.08), larger VNRs (5-15), higher demands
# This should favor algorithms with better success rates

echo "============================================"
echo "HIGH-LOAD Scenario - All Algorithms"
echo "============================================"
echo "Config: tree topology + high load VNRs"
echo ""

SEEDS=(0 1 2 3 4)
ALGORITHMS=("rw_rank_bfs" "pl_rank" "mcts" "ga_meta" "mip" "sa_meta")

for algo in "${ALGORITHMS[@]}"
do
    echo "--------------------------------------------"
    echo "Running algorithm: $algo"
    echo "--------------------------------------------"

    for seed in "${SEEDS[@]}"
    do
        echo "  Seed $seed..."

        python main_tree_sa.py \
            --config-name=main_tree_high_load \
            solver.solver_name=$algo \
            experiment.seed=$seed \
            experiment.run_id="${algo}_high_load_seed_$seed"

        if [ $? -eq 0 ]; then
            echo "  ✓ Seed $seed completed"
        else
            echo "  ✗ Seed $seed failed!"
        fi
    done

    echo ""
done

echo "============================================"
echo "HIGH-LOAD scenario complete!"
echo "============================================"
echo ""
echo "Results saved in virne/<algorithm>/<algo>_high_load_seed_*/"
echo ""
