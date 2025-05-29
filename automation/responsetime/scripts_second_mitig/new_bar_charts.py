import matplotlib.pyplot as plt
import datetime
import argparse
import os
import numpy as np

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

    ax.set_title("Response Time Distribution - Baseline", fontsize=16, pad=15)

    # Median
    median = np.median(response_times)

    # Ensure output folder exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Histogram settings
    bin_width = 0.0005
    bins = np.arange(0.00, 0.014 + bin_width, bin_width)

    # Plot with thicker blue bars, no edge
    n, bin_edges, patches = ax.hist(
        response_times, 
        bins=bins,
        color='steelblue',      # richer blue
        edgecolor='none',       # no white border
        label='Response Times'
    )

    # Median line with only 3 decimals
    ax.axvline(median, color='red', linestyle='--', linewidth=2,
               label=f'Median: {median:.3f}s')

    # Axes and grid styling
    ax.set_xlabel('Response Time [s]')
    ax.set_ylabel('Frequency')
    ax.set_xlim(0.00, 0.014)
    ax.set_ylim(0, max(n) * 1.1)

    # X-axis ticks every 0.002
    xticks = np.arange(0.00, 0.014 + 0.002, 0.002)
    ax.set_xticks(xticks)
    ax.tick_params(axis='x', rotation=45)

    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()

    fig.tight_layout(pad=1.0)

    # Save figure
    fig.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Saved histogram to {output_filename}")

if __name__ == '__main__':
    args = parse_arguments()
    timestamps, response_times = read_data(args.filename)

    if len(response_times) == 0:
        print("No valid data found")
        exit(1)

    create_histogram(response_times, 'images/barchart_baseline_histogram_this_one.png')
