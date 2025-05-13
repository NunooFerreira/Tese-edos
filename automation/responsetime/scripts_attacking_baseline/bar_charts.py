import matplotlib.pyplot as plt
import datetime
import argparse
import os
import numpy as np
import matplotlib.dates as mdates

plt.rcParams.update({'font.size': 14})  # Increased font size to match previous code

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

def create_histogram(response_times, output_filename, filepath):
    fig, ax = plt.subplots(figsize=(12, 6))  # Match the figure size from previous code
    
    # Determine if this is a yoyo attack file
    is_yoyo = 'yoyo' in filepath.lower()
    title = "Response Time Distribution - Yoyo Attack" if is_yoyo else "Response Time Distribution - Baseline"
    ax.set_title(title, fontsize=16, pad=15)
    
    # Calculate stats for smart bin selection
    median = np.median(response_times)
    p85 = np.percentile(response_times, 85)
    
    # Create histogram with more controlled bins
    if is_yoyo:
        # For yoyo, we want to capture the distribution's shape while handling outliers
        y_limit = max(median * 2, p85)
        # Clip data for binning but show the range in stats
        binned_data = np.clip(response_times, 0, y_limit)
        bins = np.linspace(0, y_limit, 20)
    else:
        # For baseline, use the full range
        y_limit = response_times.max() * 1.05
        binned_data = response_times
        bins = 20
    
    n, bins, patches = ax.hist(binned_data, bins=bins, color='tab:blue', 
                               alpha=0.7, edgecolor='white', label='Response Times')
    
    # Add a vertical line for the median
    ax.axvline(median, color='red', linestyle='dashed', linewidth=2, 
              label=f'Median: {median:.3f}s')
    
    # Axes styling to match previous plot
    ax.set_xlabel('Response Time [s]')
    ax.set_ylabel('Frequency')
    
    # Set ylim with a bit of headroom
    ax.set_ylim(0, ax.get_ylim()[1] * 1.1)
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    ax.legend()
    
    # Print statistics to help with debugging - matching previous format
    if is_yoyo:
        print(f"\nStatistics for {filepath}:")
        print(f"Median response time: {median:.3f}s")
        print(f"85th percentile: {p85:.3f}s")
        print(f"Maximum value: {np.max(response_times):.3f}s")
        print(f"Plotting limit set to: {y_limit:.3f}s")
    
    fig.tight_layout(pad=1.0)
    
    # Dynamic output filename based on input
    fig.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Saved histogram to {output_filename}")

if __name__ == '__main__':
    args = parse_arguments()
    timestamps, response_times = read_data(args.filename)
    
    if len(response_times) == 0:
        print("No valid data found")
        exit(1)
        
    base_name = os.path.splitext(args.filename)[0]
    output_filename = f"images/{base_name}_histogram_mitigation.png"
    create_histogram(response_times, output_filename, args.filename)