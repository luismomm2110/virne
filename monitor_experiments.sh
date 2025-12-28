#!/bin/bash
# Monitor running experiments

echo "======================================"
echo "VNE Experiments Status Monitor"
echo "======================================"
echo ""

# Count running processes
RUNNING=$(ps aux | grep -E "main_tree.*\.py" | grep -v grep | grep python | wc -l | tr -d ' ')

echo "Running experiments: $RUNNING"
echo ""

if [ "$RUNNING" -gt 0 ]; then
    echo "Active processes:"
    ps aux | grep -E "main_tree.*\.py" | grep -v grep | grep python | awk '{print "  -", $11, $12, $13, $14, $15}'
    echo ""
fi

# Check completed saturation experiments
echo "Completed saturation runs:"
ls -d virne/mip_saturation_seed_* 2>/dev/null | wc -l | xargs echo "  Tree MIP saturation:"
ls -d virne/*_fat_tree_*_seed_* 2>/dev/null | wc -l | xargs echo "  Fat-tree experiments:"
echo ""

# Show recent completions
echo "Recent experiment directories:"
ls -lt virne/ | grep "^d" | head -5 | awk '{print "  ", $9}'

