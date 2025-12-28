#!/bin/bash

# Monitor WX500 simulations in real-time

while true; do
    clear
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║         WX500 LIVE MONITOR - $(date '+%Y-%m-%d %H:%M:%S')              ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Current process
    echo "🔄 RUNNING NOW:"
    ps aux | grep "main_wx500" | grep -v grep | awk '{print "   Process: " $11 " " $12}'
    echo ""
    
    # Count results
    echo "📊 RESULTS COLLECTED:"
    for algo in ga_meta pso_meta sa_meta pl_rank rw_rank_bfs mcts d_round; do
        count=$(find virne/$algo -type d -name "*Luisas-MacBook*202512*" 2>/dev/null | wc -l)
        if [ $count -gt 0 ]; then
            echo "   ✅ $algo: $count runs"
        fi
    done
    echo ""
    
    # VNR processing
    echo "📈 VNR PROCESSING (latest ga_meta seed 0):"
    latest_ga=$(find virne/ga_meta -type d -name "*20251221T09*" 2>/dev/null | head -1)
    if [ ! -z "$latest_ga" ]; then
        vnr_count=$(wc -l < "$latest_ga/records/temp-0.csv" 2>/dev/null || echo "0")
        progress=$(( (vnr_count - 1) * 100 / 1000 ))
        printf "   VNRs: %d/1000 [" $((vnr_count - 1))
        for ((i=0; i<progress/5; i++)); do printf "█"; done
        for ((i=progress/5; i<20; i++)); do printf "░"; done
        printf "] %d%%\n" $progress
    fi
    echo ""
    
    # Disk usage
    echo "💾 DISK USAGE:"
    du -sh virne/ 2>/dev/null | awk '{print "   virne/: " $1}'
    echo ""
    
    echo "⏳ Next update in 30 seconds... (Ctrl+C to stop)"
    sleep 30
done
