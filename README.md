# EdiScan

Application d'extraction de texte depuis des images avec EasyOCR.

[![Demo](https://img.shields.io/badge/🚀_Demo_Live-Hugging_Face-yellow)](https://huggingface.co/spaces/IyedM/ediscan)
[![Docker](https://img.shields.io/badge/Docker-Hub-blue)](https://hub.docker.com/r/iyedmed/ediscan)
[![CI/CD](https://github.com/iyedM/EdiScan/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/iyedM/EdiScan/actions)

## Demo

**App en ligne :** https://huggingface.co/spaces/IyedM/ediscan

## Fonctionnalités

- Upload d'images par drag & drop ou Ctrl+V
- OCR multi-langues (Français, Anglais)
- Mode rapide pour captures d'écran
- Traitement par lot (plusieurs images)
- Historique des extractions
- Cache intelligent
- Export en .txt

## Installation rapide

### Avec Docker

```bash
docker run -p 5000:5000 iyedmed/ediscan
```

Ouvrir http://localhost:5000

### Sans Docker

```bash
git clone https://github.com/iyedM/EdiScan.git
cd EdiScan
pip install -r server/requirements.txt
python server/app.py
```

## Structure

```
EdiScan/
├── server/          # Backend Flask
├── web/             # Frontend
├── k8s/             # Kubernetes manifests
├── helm/            # Helm Chart
├── terraform/       # Infrastructure GCP
├── monitoring/      # Prometheus + Grafana
└── huggingface/     # Deploy HuggingFace
```

## Stack technique

| Catégorie | Technologies |
|-----------|--------------|
| Backend | Python, Flask, EasyOCR |
| Frontend | HTML, CSS, JavaScript |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Orchestration | Kubernetes, Helm |
| IaC | Terraform (GCP) |
| Monitoring | Prometheus, Grafana |
| Hosting | Hugging Face Spaces |

## Deploiement

### Docker Hub

```bash
docker pull iyedmed/ediscan:latest
docker run -p 5000:5000 iyedmed/ediscan
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

### Helm

```bash
helm install ediscan ./helm/ediscan
```

### Terraform (GCP)

```bash
cd terraform
terraform init
terraform apply
```

## Utilisation

1. Ouvrir l'app
2. Glisser une image ou coller avec Ctrl+V
3. Cliquer "Analyser" ou "Rapide"
4. Copier le texte extrait

## Raccourcis

| Raccourci | Action |
|-----------|--------|
| Ctrl+V | Coller une image |
| Ctrl+Shift+C | Copier le texte |

## API

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET/POST | Page principale |
| `/history` | GET | Historique |
| `/api/ocr` | POST | OCR une image |

## Liens

- **Demo** : https://huggingface.co/spaces/IyedM/ediscan
- **Docker Hub** : https://hub.docker.com/r/iyedmed/ediscan
- **GitHub** : https://github.com/iyedM/EdiScan

## Auteur

**Iyed Mohamed** - Cloud Computing & DevOps

## Licence

MIT
