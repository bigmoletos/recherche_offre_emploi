# 🐍 Agent Python Standalone - Recherche Offres Alternance

## 📋 Description

Agent Python autonome pour la recherche et l'analyse d'offres d'alternance en cybersécurité. Fonctionne de manière indépendante sans dépendances externes complexes.

## 🚀 Installation Rapide

```bash
# Cloner le projet et aller dans le dossier
cd agent_python

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp config/.env.example config/.env
# Éditer config/.env avec vos clés API
```

## ⚙️ Configuration

Créer le fichier `config/.env` avec :

```env
# Clé API Mistral (obligatoire)
MISTRAL_API_KEY=votre_cle_mistral

# Configuration optionnelle
LOG_LEVEL=INFO
OUTPUT_FORMAT=excel
MAX_OFFRES=50
```

## 🎯 Utilisation

### Exécution Basique

```bash
# Recherche et analyse automatique
python src/demo_agent.py

# Scraping seulement
python src/scraper_offres_reelles.py

# Analyse de données existantes
python src/analyser_vraies_offres.py
```

### Utilisation Avancée

```python
from src.scraper_offres_reelles import JobScraper
from src.analyser_vraies_offres import JobAnalyzer

# Initialiser le scraper
scraper = JobScraper()

# Rechercher des offres
offres = scraper.search_jobs(
    keywords=["cybersécurité", "alternance"],
    max_results=20
)

# Analyser avec IA
analyzer = JobAnalyzer()
analyses = analyzer.analyze_jobs(offres)
```

## 📁 Structure

```
agent_python/
├── src/                        # Code source
│   ├── demo_agent.py           # Script de démonstration principal
│   ├── scraper_offres_reelles.py # Moteur de scraping
│   └── analyser_vraies_offres.py # Analyseur IA
├── tests/                      # Tests unitaires
├── config/                     # Configuration
│   └── .env.example           # Template de configuration
├── outputs/                    # Rapports générés
├── logs/                      # Fichiers de logs
├── requirements.txt           # Dépendances Python
└── README.md                  # Ce fichier
```

## ✅ Fonctionnalités

- ✅ **Scraping automatique** depuis Pôle Emploi
- ✅ **Analyse IA** avec Mistral
- ✅ **Rapports Excel** professionnels
- ✅ **Logs détaillés** pour le debugging
- ✅ **Configuration flexible** via .env
- ✅ **Gestion d'erreurs** robuste
- ✅ **Tests unitaires** inclus

## 📊 Résultats

**Format de sortie Excel :**
- Titre et description du poste
- Entreprise et localisation
- Salaire (si disponible)
- Score de pertinence IA
- Analyse détaillée des compétences
- URL de candidature

## 🔧 Tests

```bash
# Lancer tous les tests
python -m pytest tests/

# Test spécifique
python tests/test_excel_generation.py
python tests/test_mistral_direct.py
```

## 📈 Performance

- ⏱️ **Exécution** : 2-3 minutes
- 🎯 **Résultats** : 3-5 offres validées par IA
- 📄 **Format** : Excel professionnel
- 🔍 **Précision** : Vraies entreprises avec URLs

## 🛠️ Dépendances

- `requests` - Requêtes HTTP
- `beautifulsoup4` - Parsing HTML
- `pandas` - Manipulation de données
- `openpyxl` - Génération Excel
- `python-dotenv` - Gestion configuration
- `mistralai` - API IA

## 🚨 Résolution de Problèmes

### Erreur d'API Mistral
```bash
# Vérifier la clé API
python tests/test_env.py
```

### Problème de scraping
```bash
# Test de connectivité
python tests/test_workflow_direct.py
```

### Génération Excel échoue
```bash
# Test du générateur
python tests/test_excel_generation.py
```

## 📚 Documentation

Voir le dossier `/shared/docs/` pour une documentation complète.

---

*Agent Python v2.0 - Autonome et efficace* 🚀