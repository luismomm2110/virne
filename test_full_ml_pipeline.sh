#!/bin/bash
# Test Full ML Pipeline in Docker
# This script tests the complete workflow:
# 1. Run simulations with different algorithms
# 2. Extract VNR data
# 3. Train XGBoost model
# 4. Evaluate and compare

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

IMAGE_NAME="vne-ml-apresentacao"

# Step 1: Build container
print_header "Step 1: Building Docker Container"
docker build -f Dockerfile.apresentacao -t $IMAGE_NAME .
print_success "Container built successfully!"

echo ""
print_header "Step 2: Run Quick Simulations (Sample)"
print_info "Running 2 algorithms on Tree topology for testing..."

# Run GA on Tree (quick test with 10 VNRs)
docker run --rm \
    -v "$(pwd)/apresentacao:/app/apresentacao" \
    $IMAGE_NAME \
    python /app/apresentacao/algoritmos/main_tree_ga.py \
    experiment.seed=0 \
    v_sim_setting.num_v_nets=10
print_success "GA simulation completed!"

# Run MIP on Tree (quick test with 10 VNRs)
docker run --rm \
    -v "$(pwd)/apresentacao:/app/apresentacao" \
    $IMAGE_NAME \
    python /app/apresentacao/algoritmos/main_tree_mip.py \
    experiment.seed=0 \
    v_sim_setting.num_v_nets=10
print_success "MIP simulation completed!"

echo ""
print_header "Step 3: Extract VNR Data"
docker run --rm \
    -v "$(pwd)/apresentacao:/app/apresentacao" \
    $IMAGE_NAME \
    python /app/apresentacao/machine_learning/1_extract_vnr_data.py
print_success "Data extraction completed!"

echo ""
print_header "Step 4: Prepare Dataset"
docker run --rm \
    -v "$(pwd)/apresentacao:/app/apresentacao" \
    $IMAGE_NAME \
    python /app/apresentacao/machine_learning/2_prepare_dataset.py
print_success "Dataset prepared!"

echo ""
print_header "Step 5: Train XGBoost Model"
docker run --rm \
    -v "$(pwd)/apresentacao:/app/apresentacao" \
    $IMAGE_NAME \
    python /app/apresentacao/machine_learning/3_train_xgboost.py
print_success "Model trained!"

echo ""
print_header "Step 6: Evaluate Model"
docker run --rm \
    -v "$(pwd)/apresentacao:/app/apresentacao" \
    $IMAGE_NAME \
    python /app/apresentacao/machine_learning/5_simple_evaluation.py
print_success "Evaluation completed!"

echo ""
print_header "Step 7: Generate Comparison Plots"
docker run --rm \
    -v "$(pwd)/apresentacao:/app/apresentacao" \
    $IMAGE_NAME \
    python /app/apresentacao/machine_learning/6_create_comparison_plots.py
print_success "Plots generated!"

echo ""
print_header "✅ Full ML Pipeline Test Completed!"

echo ""
print_info "Generated files:"
echo "  📊 Datasets: apresentacao/machine_learning/datasets/"
echo "  🤖 Model: apresentacao/machine_learning/models/"
echo "  📈 Results: apresentacao/machine_learning/results/"

echo ""
print_info "To see results:"
echo "  ls -lh apresentacao/machine_learning/results/"