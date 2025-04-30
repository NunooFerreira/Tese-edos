import sys
import os

def compute_average_latency(log_path):
    """
    Reads a log file where each line is:
      timestamp,req-<id>,<duration>,HTTP <status>
    or
      timestamp,req-<id>,<duration>,ERROR,<error>
    Returns the average of all <duration> values.
    """
    total = 0.0
    count = 0

    with open(log_path, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            # Ensure we have at least 3 parts and the third is a float
            if len(parts) >= 3:
                try:
                    dur = float(parts[2])
                    total += dur
                    count += 1
                except ValueError:
                    # skip lines that don't parse (e.g. headers or malformed)
                    continue

    if count == 0:
        return None
    return total / count

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <log1> [<log2> ...]")
        sys.exit(1)

    for path in sys.argv[1:]:
        if not os.path.isfile(path):
            print(f"[!] File not found: {path}")
            continue

        avg = compute_average_latency(path)
        if avg is None:
            print(f"{path}: no valid request entries found.")
        else:
            print(f"{path}: average latency = {avg:.3f} seconds over all requests")

if __name__ == "__main__":
    main()
