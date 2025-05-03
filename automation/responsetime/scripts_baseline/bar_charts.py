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
    
    # Titulo
    ax.set_title("Response Time Distribution - Baseline", fontsize=16, pad=15)
    
    # median
    median = np.median(response_times)
    
    # Baseline-specific parameters
    y_limit = response_times.max() * 1.05
    bins = 20
    
    # Create histogram with full range
    n, bins, patches = ax.hist(response_times, bins=bins, color='tab:blue', 
                             alpha=0.7, edgecolor='white', label='Response Times')
    
    # Add median line
    ax.axvline(median, color='red', linestyle='dashed', linewidth=2, 
              label=f'Median: {median:.3f}s')
    
    # Axes styling
    ax.set_xlabel('Response Time [s]')
    ax.set_ylabel('Frequency')
    ax.set_xlim(0, y_limit)
    
    # Set y-axis with headroom
    ax.set_ylim(0, ax.get_ylim()[1] * 1.1)
    
    # Add grid and legend
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    fig.tight_layout(pad=1.0)
    
    # Save with fixed filename
    fig.savefig('images/response_baseline_histogram.png', dpi=300, bbox_inches='tight')
    print(f"Saved histogram to {output_filename}")

if __name__ == '__main__':
    args = parse_arguments()
    timestamps, response_times = read_data(args.filename)
    
    if len(response_times) == 0:
        print("No valid data found")
        exit(1)
        
    # Use static output filename
    create_histogram(response_times, 'baseline_histogram.png')