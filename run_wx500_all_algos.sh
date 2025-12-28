#!/bin/bash

# WX500 Simulation Runner
# Runs all 8 VNE algorithms on WX500 topology with 5 random seeds
# Total: 8 algorithms × 5 seeds = 40 simulations

echo "Starting WX500 simulations..."
echo "Target: 8 algorithms × 5 seeds = 40 total simulations"
echo ""

# Array of algorithms and their corresponding main scripts
declare -a ALGORITHMS=(
    "mip:main_wx500_mip.py"
    "ga_meta:main_wx500_ga.py"
    "pso_meta:main_wx500_pso.py"
    "sa_meta:main_wx500_sa.py"
    "pl_rank:main_wx500_pl_rank.py"
    "rw_rank_bfs:main_wx500_rw_rank_bfs.py"
    "mcts:main_wx500_mcts.py"
    "d_round:main_wx500_d_round.py"
)

# Seeds to test
SEEDS=(0 1 2 3 4)

# Track progress
TOTAL_SIMS=$((${#ALGORITHMS[@]} * ${#SEEDS[@]}))
COMPLETED=0

echo "Algorithms to test: ${#ALGORITHMS[@]}"
echo "Seeds per algorithm: ${#SEEDS[@]}"
echo ""

# Run simulations for each algorithm and seed
for algo_pair in "${ALGORITHMS[@]}"; do
    IFS=':' read -r ALGO_NAME SCRIPT_PATH <<< "$algo_pair"

    echo "=========================================="
    echo "Running $ALGO_NAME algorithm"
    echo "=========================================="

    for seed in "${SEEDS[@]}"; do
        COMPLETED=$((COMPLETED + 1))
        echo ""
        echo "[$COMPLETED/$TOTAL_SIMS] Running $ALGO_NAME with seed=$seed"
        echo "Command: python $SCRIPT_PATH experiment.seed=$seed"

        # Run the simulation
        python "$SCRIPT_PATH" experiment.seed=$seed

        if [ $? -eq 0 ]; then
            echo "✓ Completed: $ALGO_NAME seed=$seed"
        else
            echo "✗ FAILED: $ALGO_NAME seed=$seed"
        fi

        echo ""
    done
done

echo "=========================================="
echo "All WX500 simulations completed!"
echo "=========================================="
echo "Completed: $COMPLETED simulations"
echo "Expected: $TOTAL_SIMS simulations"
echo ""
echo "Results stored in virne/ directory:"
echo "  - mip/"
echo "  - ga_meta/"
echo "  - pso_meta/"
echo "  - sa_meta/"
echo "  - pl_rank/"
echo "  - rw_rank_bfs/"
echo "  - mcts/"
echo "  - d_round/"
echo ""
echo "Next step: Extract results using:"
echo "  python apresentacao/machine_learning/1_extract_vnr_data.py"
