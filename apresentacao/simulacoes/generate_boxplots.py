#!/usr/bin/env python3
"""
Generate boxplots comparing all VNE algorithms
Reads from summary.csv files in each algorithm directory
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

def extract_summary_data():
    """Extract summary metrics from all algorithm runs"""

    algorithms = ['ga_meta', 'mip', 'mcts', 'sa_meta', 'pso_meta', 'pl_rank', 'rw_rank_bfs', 'd_round']
    all_data = []

    print("Extracting summary data from all algorithms...")
    print()

    for algo in algorithms:
        pattern = f"{algo}/**/summary.csv"
        files = glob.glob(pattern, recursive=True)

        if not files:
            print(f"  ⚠️  No summary files found for {algo}")
            continue

        print(f"  Processing {algo}: found {len(files)} summary files")

        for summary_file in files:
            try:
                df = pd.read_csv(summary_file)

                # Get final metrics (last row)
                if len(df) > 0:
                    final_row = df.iloc[-1]

                    # Extract topology from path
                    if 'tree' in summary_file.lower() and 'fat' not in summary_file.lower():
                        topology = 'tree'
                    elif 'fat' in summary_file.lower():
                        topology = 'fat_tree'
                    else:
                        topology = 'unknown'

                    # Calculate average time per VNR
                    total_time = final_row.get('clock_running_time', 0)
                    num_requests = 200
                    avg_time_per_vnr = total_time / num_requests if num_requests > 0 else 0

                    record = {
                        'algorithm': algo,
                        'topology': topology,
                        'acceptance_rate': final_row.get('acceptance_rate', 0),
                        'revenue': final_row.get('total_revenue', 0),
                        'r2c_ratio': final_row.get('long_term_r2c_ratio', 0),
                        'num_accepted': final_row.get('success_count', 0),
                        'num_requests': num_requests,
                        'total_time': total_time,
                        'avg_time_per_vnr': avg_time_per_vnr,
                    }

                    all_data.append(record)

            except Exception as e:
                print(f"    ✗ Error reading {summary_file}: {e}")
                continue

    if len(all_data) == 0:
        print("\n❌ ERROR: No data extracted!")
        return pd.DataFrame()

    df = pd.DataFrame(all_data)

    print(f"\n{'='*80}")
    print(f"Total simulations extracted: {len(df)}")
    print(f"Algorithms: {df['algorithm'].nunique()} ({sorted(df['algorithm'].unique())})")
    print(f"Topologies: {df['topology'].nunique()} ({sorted(df['topology'].unique())})")
    print(f"\nRecords per algorithm:")
    print(df['algorithm'].value_counts().sort_index())
    print(f"\nMean acceptance rate per algorithm:")
    print(df.groupby('algorithm')['acceptance_rate'].mean().sort_values(ascending=False))
    print(f"{'='*80}\n")

    return df


def generate_boxplots(df, output_path='results_boxplots.png'):
    """Generate comprehensive boxplots for all metrics"""

    if len(df) == 0:
        print("❌ No data to plot!")
        return

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('VNE Algorithm Comparison - All Metrics', fontsize=16, fontweight='bold')

    # Algorithm name mapping for better display
    algo_names = {
        'ga_meta': 'GA',
        'mip': 'MIP',
        'mcts': 'MCTS',
        'sa_meta': 'SA',
        'pso_meta': 'PSO',
        'pl_rank': 'PL-Rank',
        'rw_rank_bfs': 'RW-Rank-BFS',
        'd_round': 'D-Round'
    }

    df['algo_display'] = df['algorithm'].map(algo_names)

    # Sort algorithms by mean acceptance rate for consistent ordering
    algo_order = df.groupby('algo_display')['acceptance_rate'].mean().sort_values(ascending=False).index.tolist()

    # Colors for each algorithm
    colors = sns.color_palette("husl", len(algo_order))

    # 1. Acceptance Rate
    ax1 = axes[0, 0]
    sns.boxplot(data=df, x='algo_display', y='acceptance_rate', order=algo_order,
                palette=colors, ax=ax1)
    ax1.set_title('Acceptance Rate', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Algorithm', fontsize=12)
    ax1.set_ylabel('Acceptance Rate (%)', fontsize=12)
    ax1.set_ylim(0, 1.0)
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)

    # Add mean values as text
    for i, algo in enumerate(algo_order):
        mean_val = df[df['algo_display'] == algo]['acceptance_rate'].mean()
        ax1.text(i, mean_val + 0.03, f'{mean_val:.2f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    # 2. Total Revenue
    ax2 = axes[0, 1]
    sns.boxplot(data=df, x='algo_display', y='revenue', order=algo_order,
                palette=colors, ax=ax2)
    ax2.set_title('Total Revenue', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Algorithm', fontsize=12)
    ax2.set_ylabel('Revenue', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)

    # 3. Revenue-to-Cost Ratio
    ax3 = axes[1, 0]
    sns.boxplot(data=df, x='algo_display', y='r2c_ratio', order=algo_order,
                palette=colors, ax=ax3)
    ax3.set_title('Revenue-to-Cost Ratio', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Algorithm', fontsize=12)
    ax3.set_ylabel('R2C Ratio', fontsize=12)
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)

    # 4. Average Time per VNR
    ax4 = axes[1, 1]
    sns.boxplot(data=df, x='algo_display', y='avg_time_per_vnr', order=algo_order,
                palette=colors, ax=ax4)
    ax4.set_title('Average Time per VNR', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Algorithm', fontsize=12)
    ax4.set_ylabel('Time (seconds)', fontsize=12)
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)

    # Add mean values as text
    for i, algo in enumerate(algo_order):
        mean_val = df[df['algo_display'] == algo]['avg_time_per_vnr'].mean()
        ax4.text(i, ax4.get_ylim()[1] * 0.95, f'{mean_val:.2f}s',
                ha='center', va='top', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Boxplots saved to: {output_path}")
    print(f"  Size: {os.path.getsize(output_path) / 1024:.1f} KB")

    # Also create a summary table
    summary = df.groupby('algo_display').agg({
        'acceptance_rate': ['mean', 'std', 'min', 'max'],
        'revenue': ['mean', 'std'],
        'r2c_ratio': ['mean', 'std'],
        'avg_time_per_vnr': ['mean', 'std', 'min', 'max']
    }).round(3)

    summary_path = 'results_summary_table.csv'
    summary.to_csv(summary_path)
    print(f"✓ Summary table saved to: {summary_path}")

    return fig


if __name__ == '__main__':
    # Extract data
    df = extract_summary_data()

    if len(df) > 0:
        # Generate boxplots
        generate_boxplots(df)

        print("\n" + "="*80)
        print("SUMMARY STATISTICS BY ALGORITHM")
        print("="*80)
        print(df.groupby('algorithm')[['acceptance_rate', 'revenue', 'r2c_ratio', 'avg_time_per_vnr']].describe())
    else:
        print("\n❌ No data to visualize. Check simulation results.")
