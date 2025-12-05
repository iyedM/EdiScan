# Kubernetes Deployment

## Quick Start

```bash
# Create namespace and apply all manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml
```

## Verify Deployment

```bash
kubectl get all -n ediscan
kubectl get ingress -n ediscan
```

## Scale Manually

```bash
kubectl scale deployment ediscan -n ediscan --replicas=5
```

## View Logs

```bash
kubectl logs -f deployment/ediscan -n ediscan
```

