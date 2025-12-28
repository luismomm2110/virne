#!/bin/bash

# Quick test to validate topology scaling hypothesis
# Runs ONE algorithm (GA) across all topology sizes with ONE seed
# This lets you quickly see if GA performance improves on larger topologies

set -e

SEED=0

echo "=========================================="
echo "TOPOLOGY SCALING TEST - GA"
echo "=========================================="
echo "Testing hypothesis: GA performs better on larger topologies"
echo ""

# Small Tree (16 hosts) - BASELINE
echo "1/6: Small Tree (16 hosts)..."
python main.py \
    --config-name=main_tree_ga \
    experiment.seed="${SEED}" \
    experiment.run_id="ga_small_tree_test"
echo ""

# Medium Tree (64 hosts)
echo "2/6: Medium Tree (64 hosts)..."
python main.py \
    --config-name=main_medium_tree_ga \
    experiment.seed="${SEED}" \
    experiment.run_id="ga_medium_tree_test"
echo ""

# Large Tree (128 hosts)
echo "3/6: Large Tree (128 hosts)..."
python main.py \
    --config-name=main_large_tree_ga \
    experiment.seed="${SEED}" \
    experiment.run_id="ga_large_tree_test"
echo ""

# Small Fat-Tree (k=4, 16 hosts) - BASELINE
echo "4/6: Small Fat-Tree k=4 (16 hosts)..."
python main.py \
    --config-name=main_fat_tree_ga \
    experiment.seed="${SEED}" \
    experiment.run_id="ga_small_fat_tree_test"
echo ""

# Medium Fat-Tree (k=6, 54 hosts)
echo "5/6: Medium Fat-Tree k=6 (54 hosts)..."
python main.py \
    --config-name=main_medium_fat_tree_ga \
    experiment.seed="${SEED}" \
    experiment.run_id="ga_medium_fat_tree_test"
echo ""

# Large Fat-Tree (k=8, 128 hosts)
echo "6/6: Large Fat-Tree k=8 (128 hosts)..."
python main.py \
    --config-name=main_large_fat_tree_ga \
    experiment.seed="${SEED}" \
    experiment.run_id="ga_large_fat_tree_test"
echo ""

echo "=========================================="
echo "Scaling test complete!"
echo "=========================================="
echo ""
echo "Compare results:"
echo "  - Acceptance rate: Should stay similar or improve on larger topologies"
echo "  - Solution time: Will increase, but less than exponentially"
echo "  - R2C ratio: May improve (more placement options)"
echo ""
echo "Check summary files in virne/ga_meta/ for each test"
echo ""
echo "If GA shows good scalability, run full experiment suite"
