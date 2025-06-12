# 🚀 Guide de Démarrage Rapide

Choisissez votre approche en fonction de vos besoins :

## 🐍 Agent Python Standalone (Recommandé pour débuter)

**Prérequis :** Python 3.8+

```bash
# 1. Installation automatique
cd agent_python
python install.py

# 2. Activation de l'environnement
activate.bat  # Windows
# ou
source activate.sh  # Linux/Mac

# 3. Exécution
python src/main_scraper.py
```

**Résultat :** Fichier Excel avec 3-5 offres analysées dans `outputs/`

---

## 🔄 Agent n8n + API (Pour l'automatisation avancée)

**Prérequis :** Docker, Python 3.8+

```bash
# 1. Installation automatique
cd agent_n8n
python install.py

# 2. Démarrage des services
start_agent.bat  # Windows
# ou
./start_agent.sh  # Linux/Mac

# 3. Interface
# Ouvrir http://localhost:5678
# Importer workflow depuis workflows/
```

**Résultat :** Interface graphique + API + Monitoring

---

## ⚡ Installation Ultra-Rapide

### Option 1: Installation Automatique Guidée

```bash
# Installation avec choix interactif
python install.py
```

### Option 2: Installation Directe

```bash
# Agent Python seulement
python install.py --agent python

# Agent n8n seulement
python install.py --agent n8n

# Les deux agents
python install.py --both
```

### Test Immédiat

```bash
# Agent Python
cd agent_python && python src/main_scraper.py --max-offres 5

# Agent n8n
cd agent_n8n && start_agent.bat
# Puis ouvrir http://localhost:5678
```

---

## 🎯 Choix de l'Agent

| Critère | Python Standalone | n8n Agent |
|---------|-------------------|-----------|
| **Simplicité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Interface** | ❌ | ⭐⭐⭐⭐⭐ |
| **Automatisation** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Monitoring** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Temps de setup** | 2 minutes | 5 minutes |

---

## 🔑 Configuration Minimale

### Fichier `.env` requis

```env
# Obligatoire pour l'analyse IA
MISTRAL_API_KEY=votre_cle_mistral

# Optionnel
LOG_LEVEL=INFO
MAX_OFFRES=50
```

### Obtenir une clé Mistral

1. Aller sur https://console.mistral.ai/
2. Créer un compte gratuit
3. Générer une clé API
4. Copier dans le fichier `.env`

---

## 🆘 Aide Rapide

### Erreurs communes

```bash
# Clé API manquante
"MISTRAL_API_KEY non configurée"
→ Vérifier le fichier .env

# Dépendances manquantes
"ModuleNotFoundError"
→ pip install -r requirements.txt

# Port occupé (n8n)
"Port 5678 already in use"
→ docker-compose down puis up
```

### Support

- 📚 Documentation complète : `/shared/docs/`
- 🐛 Tests : `agent_python/tests/`
- 📊 Logs : `agent_python/logs/` ou interface n8n

---

*Démarrage en moins de 5 minutes ! 🎉*