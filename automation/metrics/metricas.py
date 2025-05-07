#!/usr/bin/env python3
"""
extract_knative_summary.py

Usage:
    python extract_knative_summary.py \
        --input pods.json \
        --output summary.txt
"""

import json
import argparse
import pandas as pd

# The metrics we care about
METRIC_KEYS = [
    "minutes",
    "cpuCores",
    "cpuCoreRequestAverage",
    "cpuCoreUsageAverage",
    "cpuCoreHours",
    "cpuCost",
    "cpuEfficiency",
    "networkTransferBytes",
    "networkReceiveBytes",
    "ramBytes",
    "ramByteUsageAverage",
    "ramByteHours",
    "ramCost",
    "ramEfficiency",
    "totalCost",
    "totalEfficiency",
]

def load_and_filter(json_path: str) -> pd.DataFrame:
    with open(json_path, "r") as f:
        payload = json.load(f)

    records = []
    for entry in payload.get("data", []):
        for pod_name, details in entry.items():
            if pod_name.startswith("knative-fn4"):
                rec = {key: details.get(key, 0.0) for key in METRIC_KEYS}
                records.append(rec)

    if not records:
        raise RuntimeError("No pods found with prefix 'knative-fn4'")

    return pd.DataFrame.from_records(records)

def compute_averages(df: pd.DataFrame) -> pd.Series:
    # Compute the mean for each metric
    return df.mean()

def write_summary(avgs: pd.Series, pod_count: int, out_path: str):
    with open(out_path, "w") as f:
        f.write(f"Knative-fn4 Pods Summary\n")
        f.write(f"Total pods processed: {pod_count}\n\n")
        f.write("Average metrics across all pods:\n")
        for metric, value in avgs.items():
            f.write(f"  {metric}: {value:.6f}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Summarize averaged metrics for knative-fn4 pods"
    )
    parser.add_argument("--input", "-i", required=True,
                        help="OpenCost JSON file")
    parser.add_argument("--output", "-o", required=True,
                        help="Path to output .txt summary")
    args = parser.parse_args()

    df = load_and_filter(args.input)
    avgs = compute_averages(df)
    write_summary(avgs, len(df), args.output)
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
