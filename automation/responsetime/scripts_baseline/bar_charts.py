import matplotlib.pyplot as plt
import datetime
import argparse
import os
import numpy as np
import matplotlib.dates as mdates

plt.rcParams.update({'font.size': 14})

def parse_arguments():
    parser = argparse.ArgumentParser(description='Plot response time histogram')
    parser.add_argument('filename', help='Path to response time data file')
    return parser.parse_args()

def read_data(filepath):
    timestamps = []
    response_times = []
    with open(filepath, 'r') as f:
        for line in f:
            if not line.strip(): continue
            parts = line.strip().split(',')
            try:
                dt = datetime.datetime.fromisoformat(parts[0])
                rt = float(parts[1])
                timestamps.append(dt)
                response_times.append(rt)
            except (ValueError, IndexError):
                continue
    return timestamps, np.array(response_times)

def create_histogram(response_times, output_filename):
    fig, ax = plt.subplots(figsize=(12, 6))

    # Title
    ax.set_title("Response Time Distribution - Baseline", fontsize=16, pad=15)

    # Median
    median = np.median(response_times)

    # Ensure output folder exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Plot histogram
    bin_width = 0.02  # 0.02 seconds per bin
    bins = np.arange(response_times.min(), response_times.max() + bin_width, bin_width)
    
    n, bin_edges, patches = ax.hist(response_times, bins=bins, color='tab:blue',
                                    alpha=0.7, edgecolor='white', label='Response Times')

    # Add median line
    ax.axvline(median, color='red', linestyle='dashed', linewidth=2,
               label=f'Median: {median:.3f}s')

    # Axes styling
    ax.set_xlabel('Response Time [s]')
    ax.set_ylabel('Frequency')

    # Set x limits with margin
    margin = 0.05 * (response_times.max() - response_times.min())
    ax.set_xlim(response_times.min() - margin, response_times.max() + margin)

    # Set y limits
    ax.set_ylim(0, max(n) * 1.1)

    # Set X ticks every 0.02 seconds
    xticks = np.arange(response_times.min() - margin, response_times.max() + margin, 0.02)
    ax.set_xticks(xticks)

    # Make grid and legend
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()

    fig.tight_layout(pad=1.0)

    # Save the figure
    fig.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Saved histogram to {output_filename}")


if __name__ == '__main__':
    args = parse_arguments()
    timestamps, response_times = read_data(args.filename)
    
    if len(response_times) == 0:
        print("No valid data found")
        exit(1)
        
    # Use static output filename
    create_histogram(response_times, 'barchart_baseline_histogram.png')