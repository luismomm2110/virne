#!/bin/bash

# Update VNR counts from various values to 700 for optimized experiments
# This applies to edge case and heterogeneity scenarios

set -e

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "UPDATING VNR COUNTS TO 700"
echo "=========================================="
echo ""

# Files to update
FILES=(
    "settings/v_sim_setting/v_sim_ultra_tight.yaml"
    "settings/v_sim_setting/v_sim_massive.yaml"
    "settings/v_sim_setting/v_sim_realtime.yaml"
    "settings/v_sim_setting/v_sim_tiny_optimal.yaml"
    "settings/v_sim_setting/v_sim_meta_heuristic_sweet_spot.yaml"
    "settings/v_sim_setting/v_sim_sparse_congested.yaml"
    "settings/v_sim_setting/v_sim_extreme_heterogeneous.yaml"
    "settings/v_sim_setting/v_sim_bimodal_demands.yaml"
    "settings/v_sim_setting/v_sim_uniform_homogeneous.yaml"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        # Get current value
        current=$(grep "^num_v_nets:" "$file" | awk '{print $2}')

        if [ -n "$current" ]; then
            echo -e "${YELLOW}Updating:${NC} $file"
            echo -e "  Current: ${current} → New: ${GREEN}700${NC}"

            # Update the file (macOS-compatible sed)
            sed -i '' 's/^num_v_nets:.*/num_v_nets: 700/' "$file"

            # Verify
            new=$(grep "^num_v_nets:" "$file" | awk '{print $2}')
            if [ "$new" = "700" ]; then
                echo -e "  ${GREEN}✓ Updated successfully${NC}"
            else
                echo -e "  ${RED}✗ Update failed${NC}"
            fi
        else
            echo -e "${YELLOW}Adding:${NC} num_v_nets: 700 to $file"
            # Add after first line (assuming YAML header comment)
            sed -i '' '1a\
num_v_nets: 700\
' "$file"
        fi
    else
        echo -e "${YELLOW}Not found:${NC} $file (will be created by scripts if needed)"
    fi
    echo ""
done

echo "=========================================="
echo -e "${GREEN}VNR count updates complete!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  All edge case and heterogeneity scenarios now use 700 VNRs"
echo "  This saves ~30% time compared to 1000 VNRs"
echo ""
echo "You can now run:"
echo "  ./run_edge_case_experiments_optimized.sh"
echo "  ./run_large_topology_experiments_optimized.sh"
echo "  ./run_heterogeneity_experiments_optimized.sh"
echo ""
