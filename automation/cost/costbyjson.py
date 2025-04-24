import json
import sys

def calculate_cost(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    total_cost = 0.0
    
    for entry in data["data"]:
        for pod_name, pod_data in entry.items():
            if "knative-fn4" in pod_name:
                total_cost += pod_data.get("totalCost", 0.0)
    
    print(f"Total cost for knative-fn4 function: ${total_cost:.5f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    calculate_cost(json_file)