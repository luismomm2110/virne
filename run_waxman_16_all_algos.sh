#!/bin/bash

# Run all 7 major algorithms on Waxman 16-node random topology
# 5 seeds per algorithm = 35 total simulations

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║   WAXMAN 16-NODE CAMPAIGN - ALL ALGORITHMS (7) x 5 SEEDS         ║"
echo "║              Total: 35 simulations                                ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

run_algorithm() {
    local script=$1
    local algo=$2
    local seed=$3

    echo "🚀 Running: $algo - seed $seed"
    python "$script" experiment.seed=$seed 2>&1
    echo "   ✅ Completed: $algo - seed $seed"
    echo ""
}

# Algorithm configs
algorithms=(
    "main_waxman_16_pl_rank.py:pl_rank"
    "main_waxman_16_sa_meta.py:sa_meta"
    "main_waxman_16_ga_meta.py:ga_meta"
    "main_waxman_16_mcts.py:mcts"
    "main_waxman_16_rw_rank_bfs.py:rw_rank_bfs"
    "main_waxman_16_mip.py:mip"
    "main_waxman_16_d_round.py:d_round"
)

# Run each algorithm with seeds 0-4
for algo_pair in "${algorithms[@]}"; do
    IFS=':' read -r script algo <<< "$algo_pair"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Algorithm: $algo (5 seeds: 0-4)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    for seed in 0 1 2 3 4; do
        run_algorithm "$script" "$algo" "$seed"
    done
done

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           ✅ WAXMAN 16-NODE CAMPAIGN COMPLETED!                  ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "✓ PL-RANK:       5 seeds (0-4)"
echo "✓ SA-Meta:       5 seeds (0-4)"
echo "✓ GA-Meta:       5 seeds (0-4)"
echo "✓ MCTS:          5 seeds (0-4)"
echo "✓ RW-RANK-BFS:   5 seeds (0-4)"
echo "✓ MIP:           5 seeds (0-4)"
echo "✓ D-Round:       5 seeds (0-4)"
echo ""
echo "Total: 35 simulations completed"
echo ""
echo "Next: Extract and compare results across all algorithms"
