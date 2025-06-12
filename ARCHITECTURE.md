# 🏗️ Architecture du Projet - Agents IA Recherche Offres

## 📋 Vue d'Ensemble

Le projet a été restructuré en **architecture modulaire** avec deux agents distincts, chacun ayant son propre environnement virtuel et ses propres scripts d'installation.

## 🔧 Principes d'Architecture

### ✅ Séparation des Responsabilités
- **Agent Python** : Solution autonome et simple
- **Agent n8n** : Solution d'orchestration avancée
- **Ressources partagées** : Documentation et utilitaires communs

### ✅ Environnements Isolés
- Chaque agent a son propre `venv/`
- Dépendances spécifiques à chaque cas d'usage
- Pas de conflits entre les versions

### ✅ Installation Automatisée
- Scripts d'installation intelligents
- Vérification des prérequis
- Configuration automatique

## 📁 Structure Détaillée

```
recherche_offre_emploi/
├── README.md                    # 📋 Documentation principale
├── QUICK_START.md               # 🚀 Guide de démarrage rapide
├── ARCHITECTURE.md              # 🏗️ Ce document
├── install.py                   # ⚙️ Installation globale avec choix
├── .gitignore                   # 🚫 Fichiers à ignorer
│
├── agent_python/                # 🐍 AGENT PYTHON STANDALONE
│   ├── README.md                # Documentation spécifique
│   ├── install.py               # Installation automatique
│   ├── activate.bat/sh          # Scripts d'activation env
│   ├── requirements.txt         # Dépendances Python
│   ├── venv/                    # Environnement virtuel Python
│   ├── src/                     # Code source
│   │   ├── main_scraper.py      # Point d'entrée principal
│   │   ├── demo_agent.py        # Script de démonstration
│   │   ├── scraper_offres_reelles.py # Moteur de scraping
│   │   └── analyser_vraies_offres.py # Analyseur IA
│   ├── tests/                   # Tests unitaires
│   │   ├── test_*.py            # Fichiers de test
│   ├── config/                  # Configuration
│   │   ├── .env.example         # Template configuration
│   │   └── .env                 # Configuration locale (généré)
│   ├── outputs/                 # Rapports générés
│   │   └── *.xlsx               # Fichiers Excel
│   └── logs/                    # Logs d'exécution
│       └── *.log                # Fichiers de logs
│
├── agent_n8n/                   # 🔄 AGENT N8N + API
│   ├── README.md                # Documentation spécifique
│   ├── install.py               # Installation automatique
│   ├── start_agent.bat/sh       # Scripts de démarrage complet
│   ├── requirements.txt         # Dépendances Flask/API
│   ├── venv/                    # Environnement virtuel API
│   ├── api/                     # API Flask
│   │   └── api_scraper_pour_n8n.py # Serveur API principal
│   ├── workflows/               # Workflows n8n
│   │   ├── workflow_n8n_ultra_simple.json
│   │   ├── workflow_n8n_final_avec_email.json
│   │   └── workflow_n8n_mistral_alternance.json
│   ├── config/                  # Configuration
│   │   ├── .env.example         # Template configuration
│   │   ├── .env                 # Configuration locale (généré)
│   │   └── config_setup_mistral.py # Setup automatique n8n
│   └── docker/                  # Services Docker
│       └── docker-compose.yml   # Configuration Docker
│
└── shared/                      # 📚 RESSOURCES PARTAGÉES
    ├── docs/                    # Documentation complète
    │   ├── guide_*.md           # Guides spécialisés
    │   ├── config_*.md          # Guides de configuration
    │   └── debug_*.md           # Guides de débogage
    ├── data/                    # Données de test/exemple
    └── scripts/                 # Scripts utilitaires
```

## 🔄 Flux d'Installation

### 1. Installation Globale
```bash
python install.py
```
- Choix interactif entre les agents
- Vérification des prérequis
- Redirection vers les installations spécifiques

### 2. Installation Agent Python
```bash
cd agent_python
python install.py
```
- Création `venv/` local
- Installation des dépendances
- Configuration `.env`
- Scripts d'activation
- Tests de validation

### 3. Installation Agent n8n
```bash
cd agent_n8n
python install.py
```
- Vérification Docker
- Création `venv/` local pour l'API
- Installation dépendances Flask
- Démarrage services Docker
- Scripts de démarrage complets

## 🎯 Cas d'Usage par Agent

### 🐍 Agent Python Standalone

**Idéal pour :**
- ✅ Premiers tests du projet
- ✅ Utilisation ponctuelle
- ✅ Développement et debug
- ✅ Intégration dans d'autres scripts
- ✅ Environnements sans Docker

**Workflow typique :**
1. `cd agent_python`
2. `python install.py` (une seule fois)
3. `activate.bat` (à chaque session)
4. `python src/main_scraper.py`
5. Récupération rapport dans `outputs/`

### 🔄 Agent n8n + API

**Idéal pour :**
- ✅ Automatisation continue
- ✅ Interface utilisateur
- ✅ Monitoring temps réel
- ✅ Intégrations complexes
- ✅ Notifications multi-canaux

**Workflow typique :**
1. `cd agent_n8n`
2. `python install.py` (une seule fois)
3. `start_agent.bat` (démarrage complet)
4. Interface sur http://localhost:5678
5. Import/création de workflows
6. Monitoring et logs centralisés

## 🔧 Environnements Virtuels

### Séparation claire :
- **`agent_python/venv/`** : Modules de scraping et analyse IA
- **`agent_n8n/venv/`** : Flask, API et intégrations n8n
- **Aucun conflit** entre les versions de dépendances

### Avantages :
- ✅ **Isolation** : Pas d'interférence entre les agents
- ✅ **Maintenance** : Mise à jour indépendante
- ✅ **Déployment** : Conteneurisation facilitée
- ✅ **Développement** : Tests parallèles possibles

## 🚀 Scripts d'Automatisation

### Agent Python
- **`install.py`** : Installation complète automatique
- **`activate.bat/sh`** : Activation environnement
- **`src/main_scraper.py`** : Point d'entrée avec arguments

### Agent n8n
- **`install.py`** : Installation + Docker automatique
- **`start_agent.bat/sh`** : Démarrage services complets
- **`config/config_setup_mistral.py`** : Configuration n8n

## 📊 Monitoring et Logs

### Agent Python
- **Logs** : `agent_python/logs/`
- **Rapports** : `agent_python/outputs/`
- **Monitoring** : Via logs structurés

### Agent n8n
- **Interface** : http://localhost:5678
- **Logs** : Interface n8n + Docker logs
- **API** : http://localhost:5000/health
- **Monitoring** : Temps réel dans l'interface

## 🔄 Migration depuis l'Ancienne Version

### Changements principaux :
1. **Suppression** de `venv_alternance/` global
2. **Création** de `agent_python/venv/` et `agent_n8n/venv/`
3. **Réorganisation** des fichiers par agent
4. **Scripts** d'installation automatisés

### Procédure de migration :
1. Sauvegarder la configuration `.env` existante
2. Lancer `python install.py`
3. Choisir les agents à installer
4. Reporter la configuration dans les nouveaux `.env`

## 🎯 Recommandations d'Utilisation

### Pour débutants :
1. Commencer par **Agent Python Standalone**
2. Tester avec `python install.py --agent python`
3. Se familiariser avec les résultats
4. Passer à n8n si automatisation nécessaire

### Pour utilisateurs avancés :
1. Installer **les deux agents** avec `python install.py --both`
2. Utiliser Python pour le développement/debug
3. Utiliser n8n pour la production/monitoring
4. Intégrer les deux selon les besoins

### Pour la production :
1. **Agent n8n** recommandé
2. Monitoring continu
3. Notifications automatiques
4. Workflows versionnés

---

*Architecture v2.0 - Modulaire, robuste et évolutive* 🚀