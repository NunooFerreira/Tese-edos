from collections import defaultdict

def analyze_response_log(file_path):
    response_times = []
    status_counts = defaultdict(int)
    total_requests = 0

    with open(file_path, 'r') as f:
        for line in f:
            try:
                timestamp, response_time, status_code = line.strip().split(',')
                response_time = float(response_time)
                response_times.append(response_time)
                status_counts[status_code] += 1
                total_requests += 1
            except ValueError:
                print(f"Skipping malformed line: {line.strip()}")
                continue

    if not response_times:
        print("No valid data found.")
        return

    average_time = sum(response_times) / len(response_times)
    max_time = max(response_times)
    min_time = min(response_times)

    print(f"Average Response Time: {average_time:.6f} seconds")
    print(f"Maximum Response Time: {max_time:.6f} seconds")
    print(f"Minimum Response Time: {min_time:.6f} seconds")
    print("\nHTTP Status Code Distribution:")
    for code, count in status_counts.items():
        percentage = (count / total_requests) * 100
        print(f"{code}: {percentage:.2f}% ({count}/{total_requests})")

# Mudar o nome do ficheiro aqui:
analyze_response_log('baseline_metrics_enhanced.log')
