# Knative Function Autoscaling Analysis

A comprehensive toolkit for analyzing, testing, and visualizing Knative Function autoscaling behavior, with a focus on performance monitoring and cost analysis.

## Project Overview

This project provides tools to study Knative's autoscaling mechanisms through:
- Load testing with various concurrency patterns
- Real-time monitoring of pod scaling behavior
- CPU usage tracking and visualization
- Cost analysis integration with OpenCost API
- Yo-Yo attack simulation and mitigation strategies

## Project Structure

```
.
├── app4.py                    # FastAPI application implementing Fibonacci calculation
├── automation/
│   ├── attack/               # Load Testing Suite
│   │   ├── attack.py        # High-load test (149 concurrent requests)
│   │   ├── baseline.py      # Single-user baseline performance testing
│   │   ├── concurrency.py   # Medium load test (49 concurrent requests)
│   │   ├── hey.py          # Hey load testing implementation
│   │   └── yo-yoattack.py  # Yo-Yo attack simulation
│   ├── cost/                # Cost Analysis Tools
│   │   ├── cost.py         # OpenCost API cost tracking
│   │   └── getvalues.py    # Raw cost data extraction
│   ├── graph/               # Visualization Tools
│   │   ├── cpu_graph.py    # CPU utilization visualization
│   │   ├── delta_cost.py   # Cost variation analysis
│   │   └── pods.py         # Pod scaling behavior visualization
│   └── results/             # Analysis Results
│       ├── response_time/   # Response time analysis
│       └── scripts_baseline/# Baseline performance metrics
├── Dockerfile               # Container configuration
├── knative-service4.yaml    # Knative service definition
└── mitigation-yo-yo.py      # Yo-Yo attack mitigation implementation
```

## Key Components

### Function Implementation
- `app4.py`: FastAPI-based service implementing a Fibonacci calculation
- `Dockerfile`: Container configuration for the function
- `knative-service4.yaml`: Knative service configuration with autoscaling parameters

### Load Testing Tools
- **Baseline Testing** (`baseline.py`): Establishes baseline performance with single-user load
- **Concurrency Testing** (`concurrency.py`): Tests medium load with 49 concurrent connections
- **High Load Testing** (`attack.py`): Stress testing with 149 concurrent requests
- **Yo-Yo Attack** (`yo-yoattack.py`): Simulates oscillating load patterns to test autoscaling stability

### Monitoring and Analysis
- **CPU Monitoring** (`cpu_graph.py`): Tracks and visualizes CPU utilization patterns
- **Pod Scaling** (`pods.py`): Monitors and graphs pod count changes over time
- **Cost Analysis** (`cost.py`, `delta_cost.py`): Integrates with OpenCost API for resource usage costs
- **Response Time Analysis** (`response_time/`): Tools for analyzing and visualizing response latencies

### Security Features
- **Yo-Yo Attack Mitigation** (`mitigation-yo-yo.py`): Implements protective measures against Yo-Yo attacks by:
  - Monitoring pod scaling patterns
  - Detecting suspicious scaling behavior
  - Dynamically adjusting autoscaling parameters

## Configuration

### Knative Service Settings
```yaml
autoscaling.knative.dev/max-scale: '10'
autoscaling.knative.dev/min-scale: '0'
autoscaling.knative.dev/target: '50'
autoscaling.knative.dev/target-utilization-percentage: '100'
```

### Monitoring Parameters
- CPU usage tracking interval: 12 hours
- Pod scaling window: 12 hours
- Cost analysis window: 7 days

## Dependencies

- FastAPI & Uvicorn for service implementation
- Matplotlib for visualization
- Requests for API interactions
- NumPy & SciPy for data analysis
- aiohttp for async load testing

## Installation

```bash
pip install -r requirements.txt
kubectl apply -f knative-service4.yaml
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for improvements and bug fixes.
