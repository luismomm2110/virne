#!/bin/bash
#
# Run complete ML pipeline for VNE algorithm selection
#

set -e  # Exit on error

echo "=============================================================================="
echo "COMPLETE ML PIPELINE FOR VNE ALGORITHM SELECTION"
echo "=============================================================================="
echo ""

# Change to ML directory
cd "$(dirname "$0")"

# Step 1: Extract VNR data
echo "STEP 1/5: Extracting VNR data from simulations..."
echo "------------------------------------------------------------------------------"
python 1_extract_vnr_data.py
echo ""

# Step 2: Prepare dataset
echo "STEP 2/5: Feature engineering and dataset preparation..."
echo "------------------------------------------------------------------------------"
python 2_prepare_dataset.py
echo ""

# Step 3: Train XGBoost
echo "STEP 3/5: Training XGBoost with cross-validation..."
echo "------------------------------------------------------------------------------"
python 3_train_xgboost.py
echo ""

# Step 4: Online simulation (optional - may take long)
read -p "Run online simulations with NEW seeds? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "STEP 4/5: Running online simulations (seeds 100-104)..."
    echo "------------------------------------------------------------------------------"
    echo "NOTE: Using NEW seeds (100-104) to avoid data leakage"
    echo "      Training used seeds 0-4, so online uses different seeds"
    echo ""
    ./run_online_simulations.sh
    echo ""
else
    echo "Skipping online simulation."
    echo "To run later: ./run_online_simulations.sh"
    echo ""
fi

# Step 5: Comparison (if results exist)
if [ -f "results/online_sim_dynamic_seed_100.csv" ]; then
    echo "STEP 5/5: Comparing with baselines..."
    echo "------------------------------------------------------------------------------"
    python 6_compare_with_baselines.py
    echo ""
else
    echo "STEP 5/5: Skipping comparison (no simulation results found)"
    echo "To run simulations: ./run_online_simulations.sh"
    echo ""
fi

echo "=============================================================================="
echo "PIPELINE COMPLETE!"
echo "=============================================================================="
echo ""
echo "Generated files:"
echo "  - datasets/vnr_raw_data.csv       (~14,000 VNR records)"
echo "  - datasets/vnr_features.csv       (with engineered features)"
echo "  - datasets/train.csv, val.csv, test.csv"
echo "  - models/xgb_best_overall_model.pkl"
echo "  - results/confusion_matrix.png"
echo "  - results/feature_importance.png"
echo "  - results/cv_scores.png"
if [ -f "results/online_sim_dynamic_seed_0.csv" ]; then
echo "  - results/online_sim_dynamic_seed_0.csv"
echo "  - results/comparison_boxplots.png"
echo "  - results/comparison_summary.csv"
fi
echo ""
echo "Next steps:"
echo "  1. Review model performance in results/"
echo "  2. Run online simulations for multiple seeds"
echo "  3. Compare Dynamic vs Fixed algorithms"
echo ""
