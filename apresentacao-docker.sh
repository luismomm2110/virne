#!/bin/bash
# Script para gerenciar o container de apresentação VNE-ML

set -e

IMAGE_NAME="vne-ml-apresentacao"
CONTAINER_NAME="vne-ml-apresentacao"
COMPOSE_FILE="docker-compose.apresentacao.yml"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
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

# Comandos
cmd_build() {
    print_header "Building VNE ML Apresentacao Container"
    docker build -f Dockerfile.apresentacao -t $IMAGE_NAME .
    print_success "Container built successfully!"
}

cmd_start() {
    print_header "Starting Jupyter Lab"
    print_info "Jupyter Lab will be available at: http://localhost:8888"
    docker run -it --rm \
        --name $CONTAINER_NAME \
        -p 8888:8888 \
        -v "$(pwd)/apresentacao:/app/apresentacao" \
        $IMAGE_NAME
}

cmd_compose_up() {
    print_header "Starting with Docker Compose"
    print_info "Jupyter Lab will be available at: http://localhost:8888"
    docker-compose -f $COMPOSE_FILE up
}

cmd_compose_down() {
    print_header "Stopping Docker Compose"
    docker-compose -f $COMPOSE_FILE down
}

cmd_bash() {
    print_header "Opening Bash Shell in Container"
    docker run -it --rm \
        -v "$(pwd)/apresentacao:/app/apresentacao" \
        $IMAGE_NAME \
        /bin/bash
}

cmd_train() {
    print_header "Training XGBoost Model"
    docker run --rm \
        -v "$(pwd)/apresentacao:/app/apresentacao" \
        $IMAGE_NAME \
        python /app/apresentacao/machine_learning/3_train_xgboost.py
    print_success "Training completed!"
}

cmd_evaluate() {
    print_header "Evaluating Model"
    docker run --rm \
        -v "$(pwd)/apresentacao:/app/apresentacao" \
        $IMAGE_NAME \
        python /app/apresentacao/machine_learning/5_simple_evaluation.py
    print_success "Evaluation completed!"
}

cmd_plots() {
    print_header "Generating Comparison Plots"
    docker run --rm \
        -v "$(pwd)/apresentacao:/app/apresentacao" \
        $IMAGE_NAME \
        python /app/apresentacao/machine_learning/6_create_comparison_plots.py
    print_success "Plots generated!"
}

cmd_pipeline() {
    print_header "Running Full ML Pipeline"
    docker run --rm \
        -v "$(pwd)/apresentacao:/app/apresentacao" \
        $IMAGE_NAME \
        bash -c "cd /app/apresentacao/machine_learning && ./run_full_pipeline.sh"
    print_success "Pipeline completed!"
}

cmd_simulate() {
    print_header "Running Simulations"
    local algo="${1:-ga_meta}"
    local topo="${2:-tree}"
    local seed="${3:-0}"

    print_info "Algorithm: $algo, Topology: $topo, Seed: $seed"

    docker run --rm \
        -v "$(pwd)/apresentacao:/app/apresentacao" \
        $IMAGE_NAME \
        python /app/apresentacao/algoritmos/main_${topo}_${algo}.py \
        experiment.seed=$seed

    print_success "Simulation completed!"
}

cmd_test_full() {
    print_header "Testing Full ML Pipeline"
    ./test_full_ml_pipeline.sh
}

cmd_results() {
    print_header "Showing Results"
    if [ -d "apresentacao/machine_learning/results" ]; then
        ls -lh apresentacao/machine_learning/results/
        print_success "Results directory listed above"
    else
        print_error "Results directory not found"
    fi
}

cmd_clean() {
    print_header "Cleaning Up"

    # Stop and remove container
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true

    # Stop compose
    docker-compose -f $COMPOSE_FILE down 2>/dev/null || true

    print_success "Cleanup completed!"
}

cmd_help() {
    cat <<EOF
${BLUE}VNE ML Apresentacao - Docker Manager${NC}

Usage: $0 <command>

${GREEN}Container Management:${NC}
  build         Build the Docker image
  start         Start Jupyter Lab (interactive)
  bash          Open bash shell in container
  clean         Stop and remove containers

${GREEN}Docker Compose:${NC}
  up            Start services with docker-compose
  down          Stop services with docker-compose

${GREEN}ML Pipeline:${NC}
  train         Train XGBoost model
  evaluate      Evaluate trained model
  plots         Generate comparison plots
  pipeline      Run full ML pipeline
  results       Show generated results

${GREEN}Examples:${NC}
  $0 build            # Build the image
  $0 start            # Start Jupyter Lab
  $0 train            # Train model
  $0 bash             # Interactive shell

${YELLOW}Quick Start:${NC}
  1. $0 build
  2. $0 start
  3. Open: http://localhost:8888

EOF
}

# Main
case "${1:-}" in
    build)
        cmd_build
        ;;
    start)
        cmd_start
        ;;
    up)
        cmd_compose_up
        ;;
    down)
        cmd_compose_down
        ;;
    bash|shell)
        cmd_bash
        ;;
    train)
        cmd_train
        ;;
    evaluate|eval)
        cmd_evaluate
        ;;
    plots|graphs)
        cmd_plots
        ;;
    pipeline|full)
        cmd_pipeline
        ;;
    results|show)
        cmd_results
        ;;
    clean|cleanup)
        cmd_clean
        ;;
    help|--help|-h|"")
        cmd_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        cmd_help
        exit 1
        ;;
esac