import json

"""
This script reads the OpenCost JSON logs from 'mylogs.json',
filters the entries for pods whose names start with a given prefix,
and writes the filtered output to 'knative_fn4_logs.json'.

Usage:
    python filter_knative_logs.py
"""

def filter_logs(input_path: str, output_path: str, prefix: str) -> None:
    # Load the full JSON log
    with open(input_path, 'r') as f:
        data = json.load(f)

    # The 'data' key holds a list; take the first element which is a dict of pods
    pod_entries = data.get('data', [])
    if not pod_entries:
        print("No pod data found in input.")
        return
    pods = pod_entries[0]

    # Filter pods by the given prefix
    filtered = {name: details for name, details in pods.items() if name.startswith(prefix)}

    # Reconstruct a similar structure for output
    output = {
        "code": data.get("code"),
        "status": data.get("status"),
        "data": [filtered]
    }

    # Write the filtered logs
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Filtered logs written to {output_path}.")

if __name__ == "__main__":
    filter_logs('mylogs.json', 'knative_fn4_logs.json', 'knative-fn4')
