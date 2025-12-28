#!/bin/bash

# Automatic WX500 post-processing pipeline
# Runs when all WX500 simulations are complete

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           WX500 POST-PROCESSING PIPELINE                          ║"
echo "║          Starting automated data extraction & retraining           ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if WX500 simulations are complete
echo "📋 Step 0: Verifying WX500 simulations are complete..."
expected_runs=35
actual_runs=$(find virne -type d -name "*Luisas-MacBook*202512*" 2>/dev/null | wc -l)
echo "   Expected: $expected_runs runs"
echo "   Found: $actual_runs directories"

if [ $actual_runs -lt 35 ]; then
    echo "   ⚠️  WARNING: Not all 35 runs completed yet!"
    echo "   Current: $actual_runs/35"
    echo "   Continuing anyway..."
fi
echo ""

# Step 1: Extract WX500 results
echo "📊 Step 1: Extracting WX500 results..."
python extract_wx500_results.py
echo "   ✅ WX500 results extracted"
echo ""

# Step 2: Extract VNR data
echo "📈 Step 2: Extracting individual VNR data..."
python apresentacao/machine_learning/1_extract_vnr_data.py
echo "   ✅ VNR data extracted"
echo ""

# Step 3: Prepare combined dataset
echo "🔄 Step 3: Preparing combined dataset (tree + fat_tree + WX500)..."
python apresentacao/machine_learning/2_prepare_dataset.py
echo "   ✅ Combined dataset prepared"
echo ""

# Step 4: Retrain decision trees
echo "🌳 Step 4: Retraining decision trees with expanded data..."
python train_multiple_objective_trees.py
echo "   ✅ Decision trees retrained"
echo ""

# Step 5: Test improvements
echo "✅ Step 5: Testing improvements..."
python inference_option2.py --test
echo "   ✅ Inference test completed"
echo ""

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║              ✅ PIPELINE COMPLETE!                                ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "✓ WX500 simulations processed"
echo "✓ Results combined with tree + fat_tree"
echo "✓ Decision trees retrained on expanded dataset"
echo "✓ Improvements validated"
echo ""
echo "Next: Review the results in apresentacao/machine_learning/"
