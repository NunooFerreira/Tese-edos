# Knative Function Autoscaling Analysis Toolkit

A comprehensive toolkit for analyzing, testing, and visualizing Knative Function autoscaling behavior. This project focuses on understanding autoscaling patterns, detecting potential attacks, and implementing mitigation strategies, while monitoring performance and costs.

## Architecture Overview

### Infrastructure Stack

- **Virtualization Layer**: Proxmox VE hosting Ubuntu VM
- **Container Orchestration**: Kubernetes (K3s) lightweight distribution
- **Serverless Platform**: Knative Serving with Kourier ingress
- **Application Runtime**: Docker containers based on Python 3.9-slim
- **Service Mesh**: Kourier for traffic routing and load balancing
- **Monitoring**: Prometheus (10.255.32.113:31752) and OpenCost API

### Main Components

#### FastAPI Service (`app4.py`)
- Fibonacci calculation endpoint exposed via Knative
- Containerized with Docker and deployed as a Knative service
- Accessible via `http://knative-fn4.default.127.0.0.1.nip.io/fib`

#### Load Testing Framework (`automation/attack/`)
- **Baseline Testing** (`baseline.py`): Single-user load simulation
- **Concurrency Testing** (`concurrency.py`): Medium load (49 concurrent connections)
- **High Load Testing** (`attack.py`): Stress testing (149 concurrent requests)
- **Yo-Yo Attack Simulation** (`yo-yoattack.py`): Oscillating traffic patterns (265 concurrent requests)

#### Monitoring System (`automation/graph/`)
- **Pod Scaling Visualization**: Real-time pod count tracking
- **Cost Analysis**: Integration with OpenCost API
- **CPU Monitoring**: Utilization patterns and bottleneck identification

#### Security Implementation (`mitigation-yo-yo.py`)
- **Attack Detection**: Monitors pod scaling patterns
- **Mitigation Strategy**: Dynamic autoscaling target adjustment

## Knative Configuration

The service is configured with the following autoscaling parameters:

```yaml
autoscaling.knative.dev/max-scale: '10'
autoscaling.knative.dev/min-scale: '0'
autoscaling.knative.dev/target: '50'
autoscaling.knative.dev/target-utilization-percentage: '100'
```

This means:
- A single pod handles up to 50 concurrent requests before scaling
- Kourier ingress distributes traffic evenly across available pods
- The service can scale to 0 when idle and up to 10 pods under load

## Installation

### Prerequisites
- Proxmox VE or similar virtualization platform
- Ubuntu VM with at least 8GB RAM and 4 CPU cores
- Docker and kubectl installed

### Setup Steps

1. Install K3s on Ubuntu:
   ```bash
   curl -sfL https://get.k3s.io | sh -
   ```

2. Install Knative Serving with Kourier:
   ```bash
   kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-crds.yaml
   kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-core.yaml
   kubectl apply -f https://github.com/knative/net-kourier/releases/download/knative-v1.12.0/kourier.yaml
   ```

3. Configure Knative to use Kourier:
   ```bash
   kubectl patch configmap/config-network \
     --namespace knative-serving \
     --type merge \
     --patch '{"data":{"ingress.class":"kourier.ingress.networking.knative.dev"}}'
   ```

4. Deploy the Knative service:
   ```bash
   kubectl apply -f knative-service4.yaml
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running Tests

1. Start baseline testing:
   ```bash
   python automation/attack/baseline.py
   ```

2. Simulate Yo-Yo attack:
   ```bash
   python automation/attack/yo-yoattack.py
   ```

3. Run mitigation strategy:
   ```bash
   python mitigation-yo-yo.py
   ```

### Monitoring

1. Generate pod scaling visualization:
   ```bash
   python automation/prometheus/podsprometheus.py
   ```

2. Monitor CPU usage:
   ```bash
   python automation/prometheus/cpu_usage.py
   ```

### Cost Analysis

Access the cost analysis for your Knative function:

```bash
python automation/cost/cost.py
```

This will calculate and display the total cost of running the Knative function over a 12-hour period. You can also access cost data through the API endpoint:

```
http://10.255.32.113:32079/model/allocation?window=12h&aggregate=pod
```

For a visual representation of cost over time:

```bash
python automation/prometheus/delta_costprometheus.py
```

This generates a cost rate graph showing the per-minute cost of your function as it scales up and down.

### Metrics Collection

View comprehensive metrics for all pods that ran during the test period:

```bash
python automation/metrics/metricas.py --input pods.json --output summary.txt
```

The metrics include:
- **Resource Usage**: CPU cores, RAM bytes, network transfer
- **Efficiency Metrics**: CPU and RAM efficiency percentages
- **Cost Breakdown**: CPU cost, RAM cost, total cost
- **Utilization Averages**: CPU core usage average, RAM byte usage average
- **Runtime Statistics**: Total minutes, resource hours

You can also access the raw metrics data through:

```
http://10.255.32.113:31752/api/v1/query?query=kube_pod_container_resource_requests
```

## Project Structure
```
.
├── app4.py                    # Main FastAPI service
├── automation/
│   ├── attack/                # Load testing suite
│   ├── cost/                  # Cost analysis tools
│   ├── graph/                 # Visualization tools
│   ├── metrics/               # Metrics collection
│   ├── prometheus/            # Prometheus integration
│   └── results/               # Analysis data
├── Dockerfile                 # Container configuration
├── knative-service4.yaml      # Knative configuration
└── mitigation-yo-yo.py        # Attack mitigation
```

## License

[MIT License](LICENSE)
