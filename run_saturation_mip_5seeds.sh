#!/bin/bash
# Quick test: Run MIP on saturation scenario with 5 seeds

echo "========================================"
echo "VNE SATURATION - MIP ONLY (5 seeds)"
echo "VNR Size: 15-30 nodes"
echo "Expected acceptance: <5%"
echo "========================================"

for seed in 0 1 2 3 4; do
    echo "Running MIP with seed $seed..."
    python main_tree_saturation_mip.py experiment.seed=$seed
done

echo "MIP saturation experiments complete!"