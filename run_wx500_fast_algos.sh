#!/bin/bash

# WX500 Simulation Runner - FAST ALGORITHMS ONLY (skip MIP)
# Runs 7 algorithms × 5 seeds = 35 simulations
# Estimated time: 20-30 hours (vs 50+ hours with MIP)

echo "=========================================="
echo "Starting WX500 simulations - FAST ALGOS"
echo "=========================================="
echo ""

# Array of FAST algorithms (skip MIP which takes ~23 hours per seed)
declare -a ALGORITHMS=(
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

echo "Target: ${#ALGORITHMS[@]} algorithms × ${#SEEDS[@]} seeds = $TOTAL_SIMS total simulations"
echo "Skipped: MIP (would take ~115 hours total)"
echo "Estimated time: 20-30 hours"
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
echo "WX500 Fast Algorithms Complete!"
echo "=========================================="
echo "Completed: $COMPLETED simulations"
echo "Expected: $TOTAL_SIMS simulations"
echo ""
echo "Results stored in virne/ directory:"
for algo_pair in "${ALGORITHMS[@]}"; do
    IFS=':' read -r ALGO_NAME SCRIPT_PATH <<< "$algo_pair"
    echo "  - $ALGO_NAME/"
done
echo ""
echo "Next steps:"
echo "1. python extract_wx500_results.py"
echo "2. python apresentacao/machine_learning/1_extract_vnr_data.py"
echo "3. python apresentacao/machine_learning/2_prepare_dataset.py"
echo "4. python train_multiple_objective_trees.py"
echo "5. python inference_option2.py --test"
