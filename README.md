# 📄 EdiScan - OCR Intelligent

Application web d'extraction de texte à partir d'images utilisant l'intelligence artificielle (EasyOCR).

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)
![EasyOCR](https://img.shields.io/badge/EasyOCR-1.6-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)
![CI/CD](https://github.com/iyedM/EdiScan/actions/workflows/ci-cd.yml/badge.svg)

## ✨ Fonctionnalités

- 🔍 **OCR intelligent** - Extraction de texte (Français + Anglais)
- ⚡ **Mode rapide** - Optimisé pour captures terminal/bash
- 📁 **Multi-images** - Traitement par lot
- 📚 **Historique** - Sauvegarde automatique des extractions
- 📋 **Copie rapide** - Un clic ou `Ctrl+Shift+C`
- 📋 **Ctrl+V** - Coller directement depuis le presse-papier
- 💾 **Cache intelligent** - Évite de re-traiter les mêmes images
- 🧹 **Nettoyage auto** - Suppression des fichiers > 24h
- 🎯 **Détections visuelles** - Boîtes colorées selon confiance
- 💾 **Export** - Téléchargement en .txt
- 🐳 **Docker Ready** - Déploiement containerisé

## 📋 Prérequis

- **Python 3.10+** ([Télécharger](https://www.python.org/downloads/))
- **pip** (inclus avec Python)
- **~3 GB d'espace disque** (pour les modèles IA)
- **~2 GB de RAM** minimum

### Optionnel (pour accélération GPU)
- Carte graphique NVIDIA avec CUDA
- [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/EdiScan.git
cd EdiScan
```

### 2. Créer l'environnement virtuel

**Windows (PowerShell):**
```powershell
python -m venv ediscan-env
.\ediscan-env\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv ediscan-env
ediscan-env\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv ediscan-env
source ediscan-env/bin/activate
```

### 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r server/requirements.txt
```

> ⏱️ **Note:** L'installation peut prendre 5-10 minutes (PyTorch ~2GB)

### 4. Premier lancement

Les modèles EasyOCR (~300 MB) seront téléchargés automatiquement au premier lancement.

```bash
python server/app.py
```

Ou sur Windows, double-cliquez sur `launch_ediscan.bat`

### 5. Accéder à l'application

Ouvrez votre navigateur : **http://127.0.0.1:5000**

---

## 🐳 Installation avec Docker

### Option 1: Docker Compose (Recommandé)

```bash
# Cloner le projet
git clone https://github.com/iyedM/EdiScan.git
cd EdiScan

# Lancer avec Docker Compose
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

L'application sera disponible sur **http://localhost:5000**

### Option 2: Docker seul

```bash
# Construire l'image
docker build -t ediscan .

# Lancer le conteneur
docker run -d \
  --name ediscan \
  -p 5000:5000 \
  -v ediscan-uploads:/app/uploads \
  -v ediscan-models:/app/models \
  ediscan
```

### Commandes utiles

```bash
# Arrêter
docker-compose down

# Reconstruire après modifications
docker-compose up -d --build

# Voir les logs en temps réel
docker-compose logs -f ediscan

# Accéder au conteneur
docker exec -it ediscan-app bash

# Supprimer tout (conteneurs + volumes)
docker-compose down -v
```

### Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `PORT` | 5000 | Port du serveur |
| `HOST` | 0.0.0.0 | Hôte |
| `FLASK_ENV` | development | `production` pour prod |
| `MAX_FILE_AGE_HOURS` | 24 | Durée avant nettoyage |
| `DATABASE_FILE` | ediscan.db | Chemin BDD |

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Le projet inclut un pipeline CI/CD automatisé :

### Pipeline automatique (sur push/PR)

```
📥 Push/PR → 🧪 Lint & Test → 🐳 Build Docker → 📤 Push Docker Hub → 🚀 Release
```

| Étape | Description | Déclencheur |
|-------|-------------|-------------|
| **Lint & Test** | Vérification du code Python | Push/PR |
| **Build Docker** | Construction de l'image | Push/PR |
| **Push Docker Hub** | Publication de l'image | Push sur `main` ou tag `v*` |
| **Release** | Création release GitHub | Tag `v*` |

### Configuration requise

Pour activer le push sur Docker Hub, ajoutez ces secrets dans GitHub :

1. Allez dans **Settings** → **Secrets and variables** → **Actions**
2. Ajoutez :
   - `DOCKERHUB_USERNAME` : Votre username Docker Hub
   - `DOCKERHUB_TOKEN` : Token d'accès Docker Hub

### Créer une release

```bash
# Créer un tag de version
git tag v1.0.0
git push origin v1.0.0

# → Déclenche automatiquement:
#   - Build Docker
#   - Push sur Docker Hub (tag v1.0.0 + latest)
#   - Création release GitHub
```

### Workflow manuel

Vous pouvez aussi déclencher manuellement un build :
1. Allez dans **Actions** → **Docker Publish (Manual)**
2. Cliquez **Run workflow**
3. Entrez le tag souhaité

---

## 📁 Structure du projet

```
EdiScan/
├── server/
│   ├── app.py              # Backend Flask
│   └── requirements.txt    # Dépendances Python
├── web/
│   ├── index.html          # Page principale
│   ├── history.html        # Page historique
│   ├── css/
│   │   └── style.css       # Styles
│   └── js/
│       └── app.js          # JavaScript
├── uploads/                # Images uploadées (auto-généré)
├── processed/              # Images traitées (auto-généré)
├── models/                 # Modèles EasyOCR (auto-téléchargé)
├── ediscan.db              # Base de données SQLite (auto-généré)
├── .github/
│   └── workflows/
│       ├── ci-cd.yml           # 🔄 Pipeline CI/CD
│       └── docker-publish.yml  # 🐳 Publish manuel
├── Dockerfile              # 🐳 Image Docker
├── docker-compose.yml      # 🐳 Orchestration
├── .dockerignore           # 🐳 Fichiers ignorés
├── launch_ediscan.bat      # Script de lancement Windows
├── .gitignore
└── README.md
```

## 🎮 Utilisation

### Mode Normal
1. Glissez-déposez une image (ou cliquez pour parcourir)
2. Cliquez **🔍 Analyser**
3. Le texte extrait apparaît à droite
4. Cliquez **📋 Copier** ou utilisez `Ctrl+Shift+C`

### Mode Rapide ⚡
- Idéal pour les **captures de terminal/bash**
- Cliquez **⚡ Rapide** au lieu d'Analyser
- 2-3x plus rapide, parfait pour texte clair

### Multi-images
1. Sélectionnez plusieurs fichiers (`Ctrl+clic`)
2. Ou glissez plusieurs images d'un coup
3. Cliquez Analyser
4. Naviguez entre les résultats

### Paramètres
| Option | Description |
|--------|-------------|
| **Confiance min.** | Filtrer les détections peu fiables (0-100%) |
| **Prétraitement** | Améliore la qualité (plus lent) |
| **Copie auto** | Copie automatiquement après OCR |

## ⌨️ Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+Shift+C` | Copie rapide du texte |

## 🔧 Configuration avancée

### Variables dans `server/app.py`

```python
MAX_FILE_AGE_HOURS = 24      # Durée avant suppression auto
CLEANUP_INTERVAL_SECONDS = 3600  # Intervalle de nettoyage
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Taille max upload (16MB)
```

### Ajouter une langue

Modifiez la ligne dans `app.py`:
```python
reader = easyocr.Reader(['fr', 'en', 'de'])  # Ajouter allemand
```

Langues disponibles: [Liste complète](https://www.jaided.ai/easyocr/)

## 🐛 Dépannage

### "Module not found"
```bash
pip install -r server/requirements.txt
```

### "CUDA out of memory"
L'application fonctionne en mode CPU par défaut. Pour forcer le CPU:
```python
reader = easyocr.Reader(['fr', 'en'], gpu=False)
```

### Modèles ne se téléchargent pas
Téléchargez manuellement depuis [EasyOCR Models](https://github.com/JaidedAI/EasyOCR/releases) et placez dans `models/`

### Port 5000 déjà utilisé
```bash
python server/app.py --port 5001
```
Ou modifiez dans `app.py`:
```python
app.run(port=5001)
```

## 📊 API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET/POST | Page principale + upload |
| `/history` | GET | Page historique |
| `/api/ocr` | POST | OCR une image (JSON) |
| `/api/batch` | POST | OCR plusieurs images |
| `/api/history` | GET | Liste historique |
| `/api/history/<id>` | DELETE | Supprimer entrée |
| `/api/history/clear` | POST | Vider historique |
| `/api/cleanup` | POST | Forcer nettoyage fichiers |

## 🛠️ Technologies utilisées

- **Backend:** Python, Flask
- **OCR:** EasyOCR (PyTorch)
- **Traitement image:** OpenCV, Pillow
- **Base de données:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)

## 📝 Licence

MIT License - Libre d'utilisation et modification.

## 👤 Auteur

Créé avec ❤️ pour faciliter l'extraction de texte.

---

**⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile !**

