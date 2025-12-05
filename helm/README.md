# Helm Chart - EdiScan

## Installation

```bash
# Add to your cluster
helm install ediscan ./ediscan -n ediscan --create-namespace

# With custom values
helm install ediscan ./ediscan -n ediscan --create-namespace \
  --set ingress.hosts[0].host=myapp.example.com \
  --set image.tag=v1.0.0
```

## Upgrade

```bash
helm upgrade ediscan ./ediscan -n ediscan
```

## Uninstall

```bash
helm uninstall ediscan -n ediscan
```

## Configuration

See `values.yaml` for all available options.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `image.repository` | Image repository | `iyedmed/ediscan` |
| `image.tag` | Image tag | `latest` |
| `ingress.enabled` | Enable ingress | `true` |
| `autoscaling.enabled` | Enable HPA | `true` |

