import matplotlib.pyplot as plt
import datetime
import argparse
import os
import numpy as np

plt.rcParams.update({'font.size': 12})

def parse_arguments():
    parser = argparse.ArgumentParser(description='Plot response time histogram')
    parser.add_argument('filename', help='Path to response time data file')
    return parser.parse_args()

def read_data(filepath):
    timestamps = []
    response_times = []
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            try:
                dt = datetime.datetime.strptime(parts[0], "%Y-%m-%dT%H:%M:%S.%f")
                rt = float(parts[1])
                timestamps.append(dt)
                response_times.append(rt)
            except (ValueError, IndexError):
                continue
    return timestamps, np.array(response_times)

def create_histogram(response_times, output_filename):
    plt.figure(figsize=(10, 6))
    
    # Create histogram
    n, bins, patches = plt.hist(response_times, bins=20, color='tab:blue', 
                               alpha=0.7, edgecolor='white')
    
    plt.xlabel('Response Time (s)')
    plt.ylabel('Frequency')
    plt.title('Response Time Distribution')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    args = parse_arguments()
    timestamps, response_times = read_data(args.filename)
    
    if len(response_times) == 0:
        print("No valid data found")
        exit(1)
        
    base_name = os.path.splitext(args.filename)[0]
    output_filename = f"{base_name}_histogram.png"
    create_histogram(response_times, output_filename)