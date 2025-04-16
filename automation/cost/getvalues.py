import requests
import json

# Fetch data from OpenCost API
url = "http://10.255.32.113:32079/model/allocation?window=7d&aggregate=pod"
response = requests.get(url)
data = response.json()

# Extract pods starting with "knative-fn4-"
knative_pods = {}
for pod_name, pod_data in data["data"][0].items():  # Assumes data[0] contains all pods
    if pod_name.startswith("knative-fn4-"):
        knative_pods[pod_name] = pod_data

# Print the result
print(json.dumps(knative_pods, indent=2))
