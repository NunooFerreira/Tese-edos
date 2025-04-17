import json

def calculate_total_cost(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            total = 0.0
            
            # Iterate through each pod entry
            for pod_name, pod_data in data.items():
                if isinstance(pod_data, dict) and 'totalCost' in pod_data:
                    if pod_name.startswith('knative-fn2'):  # Only count knative function pods
                        cost = float(pod_data['totalCost'])
                        print(f"Pod: {pod_name}, Cost: {cost:.5f}")  # Debug print
                        total += cost
            
            return total
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in the file: {e}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate total cost of knative functions from JSON file')
    parser.add_argument('file_path', type=str, help='Path to the JSON file containing the logs')
    
    args = parser.parse_args()
    
    total_cost = calculate_total_cost(args.file_path)
    if total_cost is not None:
        print(f"\nTotal cost of all knative functions: {total_cost:.5f}")
