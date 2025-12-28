#!/bin/bash
# Run all algorithm simulations with seeds

echo "======================================================================="
echo "         Running Simulations for Apresentacao with Seeds"
echo "======================================================================="

# Map algorithm names to script names
declare -A tree_scripts
tree_scripts["ga_meta"]="main_tree_ga.py"
tree_scripts["mip"]="main_tree_mip.py"
tree_scripts["mcts"]="main_tree_mcts.py"
tree_scripts["sa_meta"]="main_tree_sa.py"
tree_scripts["pso_meta"]="main_tree_pso_meta.py"
tree_scripts["pl_rank"]="main_tree_pl_rank.py"
tree_scripts["rw_rank_bfs"]="main_tree_rw_rank_bfs.py"
tree_scripts["d_round"]="main_tree_d_round.py"

declare -A fat_tree_scripts
fat_tree_scripts["ga_meta"]="main_fat_tree_ga.py"
fat_tree_scripts["mip"]="main_fat_tree_mip.py"
fat_tree_scripts["mcts"]="main_fat_tree_mcts.py"
fat_tree_scripts["sa_meta"]="main_fat_tree_sa.py"
fat_tree_scripts["pso_meta"]="main_fat_tree_pso_meta.py"
fat_tree_scripts["pl_rank"]="main_fat_tree_pl_rank.py"
fat_tree_scripts["rw_rank_bfs"]="main_fat_tree_rw_rank_bfs.py"
fat_tree_scripts["d_round"]="main_fat_tree_d_round.py"

total=48
current=0
success=0
failed=0
skipped=0

run_sim() {
    local algo=$1
    local topo=$2
    local seed=$3
    
    current=$((current + 1))
    
    echo ""
    echo "[$current/$total] $algo on $topo with seed=$seed"
    echo "-----------------------------------------------------------------------"
    
    # Get correct script name
    if [ "$topo" = "tree" ]; then
        script="${tree_scripts[$algo]}"
    else
        script="${fat_tree_scripts[$algo]}"
    fi
    
    if [ -z "$script" ] || [ ! -f "$script" ]; then
        echo "⚠️  SKIP: $script not found"
        skipped=$((skipped + 1))
        return 1
    fi
    
    timeout 600 python3 "$script" experiment.seed=$seed 2>&1 | tail -5
    
    local status=$?
    if [ $status -eq 0 ]; then
        echo "✅ SUCCESS"
        success=$((success + 1))
    elif [ $status -eq 124 ]; then
        echo "⏱️  TIMEOUT"
        failed=$((failed + 1))
    else
        echo "❌ FAILED"
        failed=$((failed + 1))
    fi
}

# Run simulations
for seed in 0 1 2; do
    for algo in ga_meta mip mcts sa_meta pso_meta pl_rank rw_rank_bfs d_round; do
        run_sim "$algo" "tree" "$seed"
        run_sim "$algo" "fat_tree" "$seed"
    done
done

echo ""
echo "======================================================================="
echo "                         SUMMARY"
echo "======================================================================="
echo "✅ Success: $success/$total"
echo "❌ Failed: $failed/$total"
echo "⚠️  Skipped: $skipped/$total"
echo "======================================================================="
