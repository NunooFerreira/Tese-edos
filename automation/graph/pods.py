import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter

# API do OpenCost
url = "http://10.255.32.113:32079/model/allocation?window=3h&aggregate=pod"
response = requests.get(url)
data = response.json()

# Filtra pods cujo nome começa com "knative-fn4-"
knative_pods = {}
for pod_name, pod_data in data["data"][0].items():
    if pod_name.startswith("knative-fn4-"):
        knative_pods[pod_name] = pod_data

# Extrai apenas os timestamps de start e end
pod_intervals = []
for pod_name, pod_data in knative_pods.items():
    start = datetime.fromisoformat(pod_data["start"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(pod_data["end"].replace("Z", "+00:00"))
    pod_intervals.append((start, end))

# Obtém todos os pontos de tempo únicos (início e fim)
time_points = sorted(set([interval[0] for interval in pod_intervals] + 
                         [interval[1] for interval in pod_intervals]))

# Para cada ponto de tempo, conta quantos pods estão ativos
x_values = []
pod_counts = []
for t in time_points:
    count = sum(1 for interval in pod_intervals if interval[0] <= t < interval[1])
    x_values.append(t)
    pod_counts.append(count)

# Plota o gráfico do número de pods ativos
plt.figure(figsize=(12, 6))
plt.step(x_values, pod_counts, where='post', color='purple')
plt.xlabel('Time')
plt.ylabel('Número de Pods Ativos')
plt.title('Comportamento do Autoscaler: Número de Pods Ativos (knative-fn4)')
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
plt.gcf().autofmt_xdate()
plt.grid(True)

# Definir valores discretos para o eixo Y
plt.yticks(range(0, max(pod_counts)+1))

plt.tight_layout()
plt.savefig('images/pod_count.png')
plt.close()
print("Gráfico 'pod_count.png' salvo.")
