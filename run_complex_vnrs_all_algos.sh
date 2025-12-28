#!/bin/bash

# Run all algorithms on COMPLEX-VNRs scenario
# Larger VNRs (8-20 nodes), higher demands, longer lifetime
# This should favor meta-heuristics and exact methods

echo "============================================"
echo "COMPLEX-VNRs Scenario - All Algorithms"
echo "============================================"
echo "Config: tree topology + complex VNRs"
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
            --config-name=main_tree_complex \
            solver.solver_name=$algo \
            experiment.seed=$seed \
            experiment.run_id="${algo}_complex_seed_$seed"

        if [ $? -eq 0 ]; then
            echo "  ✓ Seed $seed completed"
        else
            echo "  ✗ Seed $seed failed!"
        fi
    done

    echo ""
done

echo "============================================"
echo "COMPLEX-VNRs scenario complete!"
echo "============================================"
echo ""
echo "Results saved in virne/<algorithm>/<algo>_complex_seed_*/"
echo ""
