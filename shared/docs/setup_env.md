# Configuration Environnement Agent Alternance

## 🐍 Installation Python 3.10

### Windows (Recommandé)
```bash
# 1. Télécharger Python 3.10 depuis python.org
# https://www.python.org/downloads/release/python-31011/

# 2. Vérifier l'installation
python --version
# Doit afficher: Python 3.10.x

# 3. Vérifier pip
pip --version
```

### Alternative avec pyenv (Avancé)
```bash
# Installation pyenv pour Windows
git clone https://github.com/pyenv-win/pyenv-win.git %USERPROFILE%/.pyenv

# Installation Python 3.10
pyenv install 3.10.11
pyenv global 3.10.11
```

## 🌍 Création Environnement Virtuel

### Méthode 1 : venv (Recommandée)
```bash
# Se placer dans le dossier du projet
cd plateformes_Freelance

# Créer l'environnement virtuel
python -m venv venv_alternance

# Activer l'environnement (Windows)
venv_alternance\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv_alternance/bin/activate

# Vérifier l'activation (le prompt doit changer)
# (venv_alternance) C:\path\to\plateformes_Freelance>
```

### Méthode 2 : conda (Alternative)
```bash
# Créer environnement avec conda
conda create -n alternance_agent python=3.10
conda activate alternance_agent
```

## 📦 Installation des Dépendances

### Installation Optimisée
```bash
# Mise à jour pip
python -m pip install --upgrade pip

# Installation des dépendances de base (sans IA d'abord)
pip install requests beautifulsoup4 openpyxl pandas python-dateutil

# Test rapide
python -c "import requests, bs4, openpyxl, pandas; print('✅ Dépendances de base OK')"

# Installation dépendances IA (plus lourdes)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install transformers openai

# Installation complète depuis requirements.txt
pip install -r requirements.txt
```

### Vérification Installation
```bash
# Test des imports critiques
python -c "
import requests
import bs4
import openpyxl
import pandas as pd
from datetime import datetime
import logging
print('✅ Toutes les dépendances principales sont installées')
"
```

## 🚀 Test de l'Agent

### Test Version Simplifiée (Sans IA)
```bash
# Créer un fichier de test simple
python -c "
import sys
sys.path.append('.')
from agent_alternance_starter import MockScraper, ExcelReportBuilder
print('✅ Import réussi - Agent prêt')
"
```

### Test Complet
```bash
# Lancer l'agent de démonstration
python agent_alternance_starter.py
```

## 🔧 Dépendances par Catégorie

### Essentielles (Toujours nécessaires)
```bash
pip install requests beautifulsoup4 openpyxl pandas python-dateutil
```

### IA/Classification (Optionnelles pour le test)
```bash
pip install openai anthropic transformers torch
```

### Scraping Avancé (Optionnelles)
```bash
pip install selenium webdriver-manager scrapy fake-useragent
```

### Développement (Optionnelles)
```bash
pip install pytest black flake8 rich loguru
```

## 📝 Fichier requirements-minimal.txt

Pour un démarrage rapide, créer `requirements-minimal.txt` :
```txt
# Version minimaliste pour tests
requests==2.31.0
beautifulsoup4==4.12.2
openpyxl==3.1.2
pandas==2.1.1
python-dateutil==2.8.2
```

## 🐛 Résolution Problèmes Courants

### Erreur "Microsoft Visual C++ required"
```bash
# Installer Microsoft C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Alternative : versions pré-compilées
pip install --only-binary=all torch torchvision
```

### Erreur SSL/Certificats
```bash
# Windows : mise à jour certificats
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Mémoire insuffisante (PyTorch)
```bash
# Version CPU uniquement (plus légère)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Ou ignorer PyTorch temporairement
pip install -r requirements.txt --ignore-installed torch torchvision
```

## ✅ Validation Finale

### Script de Validation
```python
# validation_env.py
import sys

def check_python_version():
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor >= 9:
        print("✅ Version Python compatible")
        return True
    else:
        print("❌ Python 3.9+ requis")
        return False

def check_dependencies():
    try:
        import requests, bs4, openpyxl, pandas
        print("✅ Dépendances de base installées")

        # Test optionnel IA
        try:
            import openai
            print("✅ Dépendances IA disponibles")
        except ImportError:
            print("⚠️ Dépendances IA non installées (optionnelles)")

        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Validation environnement Agent Alternance")
    print("=" * 50)

    python_ok = check_python_version()
    deps_ok = check_dependencies()

    if python_ok and deps_ok:
        print("\n🎉 Environnement prêt pour l'agent alternance !")
    else:
        print("\n⚠️ Configuration à corriger avant utilisation")
```

### Commandes de Validation
```bash
# Valider l'environnement
python validation_env.py

# Tester l'agent
python agent_alternance_starter.py
```

## 🔄 Commandes Utiles

### Gestion Environnement
```bash
# Lister les packages installés
pip list

# Sauvegarder l'environnement actuel
pip freeze > requirements_current.txt

# Désactiver l'environnement
deactivate

# Réactiver l'environnement
venv_alternance\Scripts\activate  # Windows
source venv_alternance/bin/activate  # Linux/Mac

# Supprimer l'environnement
rmdir /s venv_alternance  # Windows
rm -rf venv_alternance    # Linux/Mac
```

## 🎯 Prêt pour n8n ?

Une fois l'environnement Python configuré, vous pourrez :

1. **Tester l'agent standalone** avec `python agent_alternance_starter.py`
2. **Installer n8n** avec `npm install -g n8n`
3. **Importer le workflow** depuis `workflow_n8n_alternance.json`
4. **Connecter Python et n8n** via les scripts de scraping

L'environnement Python 3.10 avec les dépendances installées sera parfaitement compatible avec l'orchestration n8n !