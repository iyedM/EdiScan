# 📄 EdiScan - OCR Intelligent

Application web d'extraction de texte à partir d'images utilisant l'intelligence artificielle (EasyOCR).

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)
![EasyOCR](https://img.shields.io/badge/EasyOCR-1.6-orange.svg)

## ✨ Fonctionnalités

- 🔍 **OCR intelligent** - Extraction de texte (Français + Anglais)
- ⚡ **Mode rapide** - Optimisé pour captures terminal/bash
- 📁 **Multi-images** - Traitement par lot
- 📚 **Historique** - Sauvegarde automatique des extractions
- 📋 **Copie rapide** - Un clic ou `Ctrl+Shift+C`
- 🧹 **Nettoyage auto** - Suppression des fichiers > 24h
- 🎯 **Détections visuelles** - Boîtes colorées selon confiance
- 💾 **Export** - Téléchargement en .txt

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

