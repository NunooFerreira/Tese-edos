# Knative Function Autoscaling Analysis Toolkit

A comprehensive toolkit for analyzing, testing, and visualizing Knative Function autoscaling behavior. This project focuses on understanding autoscaling patterns, detecting potential attacks, and implementing mitigation strategies, while monitoring performance and costs.

## Core Features

- **Load Testing Suite**: Multiple testing patterns from baseline to high-concurrency scenarios
- **Autoscaling Analysis**: Real-time monitoring and visualization of pod scaling behavior
- **Cost Tracking**: Integration with OpenCost API for detailed resource usage analysis
- **Security**: Yo-Yo attack simulation and mitigation implementation
- **Performance Monitoring**: CPU utilization and response time analysis

## Architecture Overview

### Main Service (`app4.py`)
- FastAPI-based service implementing Fibonacci calculation
- Serves as the test subject for autoscaling analysis
- Configurable through Knative service parameters

### Load Testing Framework (`automation/attack/`)
- **Baseline Testing** (`baseline.py`)
  - Single-user load simulation
  - Establishes performance benchmarks
  - 12-hour continuous testing window

- **Concurrency Testing** (`concurrency.py`)
  - Medium load with 49 concurrent connections
  - Evaluates normal scaling behavior

- **High Load Testing** (`attack.py`)
  - Stress testing with 149 concurrent requests
  - Tests scaling limits and response under pressure

- **Yo-Yo Attack Simulation** (`yo-yoattack.py`)
  - Simulates oscillating traffic patterns
  - 245 concurrent requests during attack phase
  - 160-second attack windows with 200-second gaps

### Monitoring System (`automation/graph/`)
- **Pod Scaling Visualization** (`pods.py`, `pods20minutes.py`)
  - Real-time pod count tracking
  - Graphical representation of scaling events
  - Customizable time windows (20-minute and 12-hour views)

- **Cost Analysis** (`delta_cost.py`)
  - Integration with OpenCost API
  - Cost variation tracking
  - Resource usage optimization insights

- **CPU Monitoring** (`cpu_graph.py`)
  - CPU utilization patterns
  - Performance bottleneck identification
  - 12-hour monitoring window

### Security Implementation (`mitigation-yo-yo.py`)
- **Attack Detection**
  - Monitors pod scaling patterns
  - Threshold-based detection (300% increase trigger)
  - 20-second check intervals

- **Mitigation Strategy**
  - Dynamic autoscaling target adjustment
  - Random target selection (60-85 range)
  - 120-second cool-down period

## Configuration Details

### Knative Service (`knative-service4.yaml`)
```yaml
autoscaling.knative.dev/max-scale: '10'
autoscaling.knative.dev/min-scale: '0'
autoscaling.knative.dev/target: '50'
autoscaling.knative.dev/target-utilization-percentage: '100'
```

### Monitoring Windows
- CPU Analysis: 12 hours
- Pod Scaling: 12 hours
- Cost Analysis: 7 days
- Attack Detection: 20-second intervals

## Technical Requirements

### Core Dependencies
- Python 3.9+
- FastAPI & Uvicorn
- Matplotlib
- aiohttp
- NumPy & SciPy

### Infrastructure
- Kubernetes cluster with Knative
- OpenCost API access
- kubectl CLI tool

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Deploy the Knative service:
   ```bash
   kubectl apply -f knative-service4.yaml
   ```

## Project Structure
```
.
├── app4.py                    # Main FastAPI service
├── automation/
│   ├── attack/               # Load testing suite
│   ├── cost/                 # Cost analysis tools
│   ├── graph/                # Visualization tools
│   └── results/              # Analysis data
├── Dockerfile                # Container configuration
├── knative-service4.yaml     # Knative configuration
└── mitigation-yo-yo.py       # Attack mitigation
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes
- Feature enhancements
- Documentation improvements
- Testing scenarios
