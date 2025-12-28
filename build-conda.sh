#!/bin/bash
# Build and test Docker container with Conda

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

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

IMAGE_NAME="vne-ml-apresentacao-conda"

print_header "Building Docker Container with Conda"
print_info "This may take 10-15 minutes (downloading conda packages)..."

docker build -f Dockerfile.apresentacao.conda -t $IMAGE_NAME .

print_success "Container built!"

echo ""
print_header "Testing imports..."

docker run --rm $IMAGE_NAME /bin/bash -c "source activate virne && python -c 'import virne; import torch; import xgboost; print(\"✓ All imports successful!\")'"

print_success "All tests passed!"

echo ""
print_info "To run simulations:"
echo "  docker run --rm -v \$(pwd)/apresentacao:/app/apresentacao $IMAGE_NAME \\"
echo "    /bin/bash -c 'source activate virne && python /app/apresentacao/algoritmos/main_tree_ga.py experiment.seed=0'"

echo ""
print_info "To start Jupyter Lab:"
echo "  docker run -p 8888:8888 -v \$(pwd)/apresentacao:/app/apresentacao $IMAGE_NAME"
