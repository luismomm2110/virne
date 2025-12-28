#!/bin/bash

# Simple WX500 monitoring script
# Run this periodically to check progress

echo "=========================================="
echo "WX500 SIMULATION PROGRESS"
echo "=========================================="
echo ""
echo "Timestamp: $(date)"
echo ""

# Count completed
COMPLETED=$(find virne -name "summary.csv" 2>/dev/null | wc -l)
echo "Summary files completed: $COMPLETED"
echo ""

# Disk usage
echo "Disk usage: $(du -sh virne/ 2>/dev/null)"
echo ""

# Running processes
RUNNING=$(ps aux | grep main_wx500 | grep -v grep | wc -l)
echo "Active processes: $RUNNING"

if [ $RUNNING -gt 0 ]; then
    echo ""
    ps aux | grep main_wx500 | grep -v grep | awk '{print $NF}' | head -3
fi

echo ""
echo "=========================================="

if [ $COMPLETED -eq 40 ]; then
    echo "✓ ALL SIMULATIONS COMPLETE!"
    echo "Next: python extract_wx500_results.py"
else
    REMAINING=$((40 - COMPLETED + 130))  # 170 existing + new
    echo "Status: Running..."
    echo "Estimated remaining: 3-5 days"
fi

echo "=========================================="
