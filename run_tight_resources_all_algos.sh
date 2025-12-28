#!/bin/bash

# Run all algorithms on TIGHT-RESOURCES scenario
# Lower physical network resources (CPU 30-60, BW 100-200)
# This should favor algorithms that optimize carefully

echo "============================================"
echo "TIGHT-RESOURCES Scenario - All Algorithms"
echo "============================================"
echo "Config: tight tree topology + normal VNRs"
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
            --config-name=main_tree_tight \
            solver.solver_name=$algo \
            experiment.seed=$seed \
            experiment.run_id="${algo}_tight_seed_$seed"

        if [ $? -eq 0 ]; then
            echo "  ✓ Seed $seed completed"
        else
            echo "  ✗ Seed $seed failed!"
        fi
    done

    echo ""
done

echo "============================================"
echo "TIGHT-RESOURCES scenario complete!"
echo "============================================"
echo ""
echo "Results saved in virne/<algorithm>/<algo>_tight_seed_*/"
echo ""
