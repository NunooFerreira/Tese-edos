# Knative Function Autoscaling Analysis

This repository contains the implementation and analysis tools for evaluating Knative Function autoscaling behavior under different load conditions.

## Project Structure

```
.
├── app4.py                    # Main FastAPI application with Fibonacci function
├── automation/
│   ├── attack/               # Load testing scripts
│   │   ├── attack.py        # High concurrency test (149 concurrent requests)
│   │   ├── baseline.py      # Baseline performance test
│   │   ├── concurrency.py   # Concurrent request testing
│   │   └── hey.py          # Hey load testing tool implementation
│   ├── cost/                # Cost analysis tools
│   │   └── cost.py         # OpenCost API integration for cost tracking
│   └── graph/               # Visualization tools
│       ├── cpu_graph.py    # CPU usage visualization
│       ├── delta_cost.py   # Cost variation analysis
│       └── pods.py         # Pod scaling visualization
├── Dockerfile               # Container configuration
├── knative-service4.yaml    # Knative service configuration
└── requirements.txt         # Python dependencies
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Knative service:
```bash
kubectl apply -f knative-service4.yaml
```

## Features

- **Autoscaling Analysis**: Tools for monitoring and analyzing Knative's autoscaling behavior
- **Load Testing**: Various approaches to test function performance under load
- **Cost Tracking**: Integration with OpenCost API for resource usage monitoring
- **Visualization**: Graph generation for CPU usage, pod count, and cost analysis

## Load Testing Tools

- `baseline.py`: Basic performance testing
- `concurrency.py`: Tests with 49 concurrent connections
- `attack.py`: High-load testing with 149 concurrent requests
- `hey.py`: Alternative load testing using Hey tool

## Monitoring and Visualization

- CPU usage tracking
- Pod scaling behavior analysis
- Cost variation monitoring
- Resource utilization graphs

## Configuration

Key configurations in `knative-service4.yaml`:
- Min scale: 0
- Max scale: 10
- Target concurrency: 50
- Target utilization: 100%

## Usage

1. Run baseline test:
```bash
python automation/attack/baseline.py
```

2. Generate visualization:
```bash
python automation/graph/cpu_graph.py
```

3. Track costs:
```bash
python automation/cost/cost.py
```

## Dependencies

- FastAPI
- Uvicorn
- Requests
- Matplotlib
- Statistics