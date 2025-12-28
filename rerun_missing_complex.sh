#!/bin/bash

# Re-run missing experiments from COMPLEX-VNRs scenario
# Missing: SA (seeds 0-4) and MIP (seed 4)

echo "============================================"
echo "Re-running Missing COMPLEX-VNRs Experiments"
echo "============================================"
echo ""

# Run SA for all seeds (0-4)
echo "--------------------------------------------"
echo "Running algorithm: sa_meta (all seeds)"
echo "--------------------------------------------"

for seed in 0 1 2 3 4
do
    echo "  Seed $seed..."

    python main_tree_sa.py \
        --config-name=main_tree_complex \
        solver.solver_name=sa_meta \
        experiment.seed=$seed \
        experiment.run_id="sa_meta_complex_seed_$seed"

    if [ $? -eq 0 ]; then
        echo "  ✓ SA seed $seed completed"
    else
        echo "  ✗ SA seed $seed failed!"
    fi
done

echo ""

# Run MIP for seed 4 only
echo "--------------------------------------------"
echo "Running algorithm: mip (seed 4 only)"
echo "--------------------------------------------"
echo "  Seed 4..."

python main_tree_sa.py \
    --config-name=main_tree_complex \
    solver.solver_name=mip \
    experiment.seed=4 \
    experiment.run_id="mip_complex_seed_4"

if [ $? -eq 0 ]; then
    echo "  ✓ MIP seed 4 completed"
else
    echo "  ✗ MIP seed 4 failed!"
fi

echo ""
echo "============================================"
echo "Missing experiments re-run complete!"
echo "============================================"
echo ""
echo "Verify results:"
echo "  SA: virne/sa_meta/sa_meta_complex_seed_{0..4}/"
echo "  MIP: virne/mip/mip_complex_seed_4/"
echo ""
