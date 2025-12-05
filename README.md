# EdiScan

Suite d'outils intelligents pour l'extraction et le traitement de documents.

[![Demo](https://img.shields.io/badge/🚀_Demo_Live-Hugging_Face-yellow)](https://huggingface.co/spaces/IyedM/ediscan)
[![Docker](https://img.shields.io/badge/Docker-Hub-blue)](https://hub.docker.com/r/iyedmed/ediscan)
[![CI/CD](https://github.com/iyedM/EdiScan/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/iyedM/EdiScan/actions)

## Demo

**App en ligne :** https://huggingface.co/spaces/IyedM/ediscan

## Fonctionnalites

### OCR (Image vers Texte)
- Upload d'images par drag & drop ou Ctrl+V
- OCR multi-langues (Francais, Anglais)
- Mode rapide pour captures d'ecran
- Traitement par lot (plusieurs images)
- Historique des extractions
- Cache intelligent
- Export en .txt

### Suite d'Outils
| Outil | Description |
|-------|-------------|
| 📄 PDF > Texte | Extraire le texte d'un fichier PDF |
| 📝 Word > Texte | Extraire le texte d'un document Word |
| 🌐 Traduction | Traduire vers 12+ langues |
| 🔍 Detection de langue | Identifier la langue d'un texte |
| 🎤 Audio > Texte | Transcrire avec Whisper AI |
| 🔊 Texte > Audio | Convertir en parole (TTS) |
| 📋 Resume automatique | Resumer un texte |
| 🔎 Extraction d'infos | Emails, telephones, URLs, dates |
| 📱 Scanner QR Code | Lire les QR codes |
| ⬛ Generer QR Code | Creer des QR codes |
| 📊 Statistiques | Mots, phrases, caracteres |

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
│   ├── app.py       # Application principale (OCR)
│   ├── features.py  # Outils additionnels
│   └── routes.py    # Routes des outils
├── web/             # Frontend
│   ├── index.html   # Page OCR
│   ├── tools.html   # Liste des outils
│   └── tool.html    # Template outil
├── k8s/             # Kubernetes manifests
├── helm/            # Helm Chart
├── terraform/       # Infrastructure GCP
├── monitoring/      # Prometheus + Grafana
└── huggingface/     # Deploy HuggingFace
```

## Stack technique

| Categorie | Technologies |
|-----------|--------------|
| Backend | Python, Flask, EasyOCR, Whisper |
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

### OCR
1. Ouvrir l'app
2. Glisser une image ou coller avec Ctrl+V
3. Cliquer "Analyser" ou "Rapide"
4. Copier le texte extrait

### Outils
1. Cliquer sur "Outils" dans le header
2. Choisir un outil
3. Importer fichier ou entrer texte
4. Obtenir le resultat

## Raccourcis

| Raccourci | Action |
|-----------|--------|
| Ctrl+V | Coller une image |
| Ctrl+Shift+C | Copier le texte |

## API

| Route | Methode | Description |
|-------|---------|-------------|
| `/` | GET/POST | Page principale OCR |
| `/tools` | GET | Liste des outils |
| `/tool/<id>` | GET/POST | Utiliser un outil |
| `/history` | GET | Historique |
| `/api/ocr` | POST | API OCR |
| `/api/features` | GET | Outils disponibles |

## Dependencies

### Core
- Flask
- EasyOCR
- OpenCV
- Pillow

### Outils additionnels
- PyPDF2, pdfplumber (PDF)
- python-docx (Word)
- deep-translator (Traduction)
- openai-whisper (Audio)
- gTTS (TTS)
- pyzbar, qrcode (QR)
- sumy (Resume)

## Liens

- **Demo** : https://huggingface.co/spaces/IyedM/ediscan
- **Docker Hub** : https://hub.docker.com/r/iyedmed/ediscan
- **GitHub** : https://github.com/iyedM/EdiScan

## Auteur

**Iyed Mohamed** - Cloud Computing & DevOps

## Licence

MIT
