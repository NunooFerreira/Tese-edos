#!/usr/bin/env python3
import argparse
from datetime import datetime
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(
        description='Plot response times as an area graph and save as PNG'
    )
    parser.add_argument(
        'input_file',
        help='Path to the baseline_responsetime.txt log file'
    )
    parser.add_argument(
        '-o', '--output',
        default='response_times.png',
        help='Filename for the output PNG (default: response_times.png)'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    timestamps = []
    response_times = []

    with open(args.input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith('baseline run started'):
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 3:
                continue
            ts_str, rt_str, _ = parts[:3]
            try:
                ts = datetime.fromisoformat(ts_str)
                rt = float(rt_str)
            except ValueError:
                continue
            timestamps.append(ts)
            response_times.append(rt)

    if not timestamps:
        print("No data to plot.")
        return

    # Plot filled area
    plt.figure(figsize=(10, 6))
    plt.fill_between(timestamps, response_times, alpha=0.5, color='mediumpurple')
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(args.output)
    print(f"Graph saved as {args.output}")

if __name__ == '__main__':
    main()
