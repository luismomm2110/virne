#!/bin/bash
#
# Run all algorithm simulations with seeds for apresentacao
# 8 algorithms × 2 topologies × 3 seeds = 48 simulations
#

echo "======================================================================="
echo "         Running Simulations for Apresentacao with Seeds"
echo "======================================================================="
echo ""
echo "Algorithms: ga_meta, mip, mcts, sa_meta, pso_meta, pl_rank, rw_rank_bfs, d_round"
echo "Topologies: tree, fat_tree"
echo "Seeds: 0, 1, 2"
echo "Total: 48 simulations"
echo ""
echo "======================================================================="
echo ""

# Counter
total=48
current=0

# Function to run a simulation
run_sim() {
    local algo=$1
    local topo=$2
    local seed=$3

    current=$((current + 1))

    echo ""
    echo "[$current/$total] Running: $algo on $topo with seed=$seed"
    echo "-----------------------------------------------------------------------"

    script="main_${topo}_${algo}.py"

    if [ ! -f "$script" ]; then
        echo "⚠️  SKIP: $script not found"
        return 1
    fi

    timeout 600 python3 "$script" experiment.seed=$seed 2>&1 | tail -10

    if [ $? -eq 0 ]; then
        echo "✅ SUCCESS"
    elif [ $? -eq 124 ]; then
        echo "⏱️  TIMEOUT (>10 min)"
    else
        echo "❌ FAILED"
    fi
}

# Run all simulations
for seed in 0 1 2; do
    for topo in tree fat_tree; do
        for algo in ga_meta mip mcts sa_meta pso_meta pl_rank rw_rank_bfs d_round; do
            run_sim "$algo" "$topo" "$seed"
        done
    done
done

echo ""
echo "======================================================================="
echo "                    All simulations completed!"
echo "======================================================================="
echo ""
echo "Results saved in: virne/<algorithm>/<run_id>/records/"
echo ""
