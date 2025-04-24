import requests

# Fetch data from OpenCost API
url = "http://10.255.32.113:32079/model/allocation?window=2025-04-23T02:40:00Z,2025-04-23T14:40:00Z&aggregate=pod"
response = requests.get(url)
data = response.json()

total_cost = 0.0

# Iterate through each item in the list
for entry in data["data"]:
    for pod_name, pod_data in entry.items():
        if "knative-fn4" in pod_name:  # Mudar aqui os Pods se necessario
            total_cost += pod_data.get("totalCost", 0.0)

print(f"Total cost for knative-fn4 function: ${total_cost:.5f}")
