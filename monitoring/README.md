# Monitoring - Prometheus & Grafana

## Deploy

```bash
# Apply all monitoring resources
kubectl apply -f prometheus-config.yaml
kubectl apply -f prometheus-deployment.yaml
kubectl apply -f grafana-deployment.yaml
kubectl apply -f ediscan-dashboard.yaml
kubectl apply -f alerts.yaml
kubectl apply -f ingress.yaml
```

## Access

### Port Forward (local access)

```bash
# Prometheus
kubectl port-forward svc/prometheus -n monitoring 9090:9090

# Grafana
kubectl port-forward svc/grafana -n monitoring 3000:3000
```

### Grafana Login

- **URL**: http://localhost:3000
- **User**: admin
- **Password**: ediscan2025

## Dashboard

The EdiScan dashboard includes:
- CPU Usage gauge
- Memory Usage gauge
- Active Pods count
- Request Rate graph
- Response Time graph (p50, p95)

## Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| EdiScanDown | App unreachable > 1min | Critical |
| HighCPUUsage | CPU > 80% for 5min | Warning |
| HighMemoryUsage | Memory > 85% for 5min | Warning |
| HighResponseTime | p95 > 5s for 5min | Warning |
| PodRestartingTooMuch | > 5 restarts/hour | Warning |

