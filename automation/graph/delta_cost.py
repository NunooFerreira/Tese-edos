import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter

# The script analyzes cost trends for Knative pods. 
# It queries the OpenCost API to fetch pod cost data, extracts timestamps and costs for active pods, 
# calculates the rate of cost change (delta) between consecutive time intervals, and generates a step graph showing how the cost fluctuates over time. 
# Negative values on the graph indicate cost reductions (e.g., pods scaling down), while positive values reflect cost increases (e.g., pods scaling up). 


# Consulta a API do OpenCost (1 dia; ajustar se necessário)
url = "http://10.255.32.113:32079/model/allocation?window=12h&aggregate=pod"
response = requests.get(url)
data = response.json()

# Filtra pods cujo nome começa com "knative-fn4-"
knative_pods = {}
for pod_name, pod_data in data["data"][0].items():
    if pod_name.startswith("knative-fn4-"):
        knative_pods[pod_name] = pod_data

# Extrai dados: start, end e totalCost
pod_intervals = []
for pod_name, pod_data in knative_pods.items():
    start_str = pod_data["start"]
    end_str = pod_data["end"]
    start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
    total_cost = pod_data["totalCost"]
    pod_intervals.append((start, end, total_cost))

# Obtém todos os pontos de tempo únicos (início e fim) e ordena os
time_points = sorted(set([interval[0] for interval in pod_intervals] + 
                           [interval[1] for interval in pod_intervals]))

# Para cada ponto de tempo, soma o totalCost dos pods ativos naquele instante
x_values = []
cost_sums = []
for t in time_points:
    active_cost = sum(interval[2] for interval in pod_intervals if interval[0] <= t < interval[1])
    x_values.append(t)
    cost_sums.append(active_cost)

# Calcula a variação (delta) de custo por minuto entre pontos consecutivos
x_delta = []
cost_rate = []
for i in range(len(x_values) - 1):
    t1 = x_values[i]
    t2 = x_values[i + 1]
    dt_minutes = (t2 - t1).total_seconds() / 60.0
    delta_cost = cost_sums[i + 1] - cost_sums[i]
    rate = delta_cost / dt_minutes if dt_minutes > 0 else 0
    x_delta.append(t1)
    cost_rate.append(rate)

# Plota o gráfico como um gráfico em "steps"
plt.figure(figsize=(12, 6))
plt.step(x_delta, cost_rate, where='post', color='red')
plt.xlabel('Time')
plt.ylabel('Cost Rate ($/min)')
plt.title('Variação do Custo (Delta do totalCost) ao Longo do Tempo para knative-fn4')
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
plt.gcf().autofmt_xdate()
plt.grid(True)
plt.tight_layout()
plt.savefig('images/cost_rate.png')
plt.close()
print("Gráfico 'cost_rate.png' salvo.")
