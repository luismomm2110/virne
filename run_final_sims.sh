#!/bin/bash
# Simple simulation runner

echo "Starting 48 simulations..."
echo ""

total=48
current=0
success=0

run() {
    algo=$1
    topo=$2
    seed=$3
    
    current=$((current + 1))
    echo "[$current/$total] $algo-$topo-seed$seed"
    
    # Map algo names to script files
    case "$algo" in
        "ga_meta") script_algo="ga" ;;
        "sa_meta") script_algo="sa" ;;
        "pso_meta") script_algo="pso_meta" ;;
        *) script_algo="$algo" ;;
    esac
    
    script="main_${topo}_${script_algo}.py"
    
    if [ ! -f "$script" ]; then
        echo "  ⚠️  SKIP: $script not found"
        return
    fi
    
    timeout 600 python3 "$script" experiment.seed=$seed >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "  ✅ SUCCESS"
        success=$((success + 1))
    else
        echo "  ❌ FAILED"
    fi
}

# Run all combinations
for seed in 0 1 2; do
    for algo in ga_meta mip mcts sa_meta pso_meta pl_rank rw_rank_bfs d_round; do
        run "$algo" "tree" "$seed"
        run "$algo" "fat_tree" "$seed"
    done
done

echo ""
echo "============================"
echo "Completed: $success/$total"
echo "============================"
