# 🔄 Agent n8n + API - Recherche Offres Alternance

> ⚠️ **IMPORTANT :** Suite à un conflit de port Windows, l'interface N8N est maintenant accessible sur le port **7080** au lieu de 8080. Voir [CHANGEMENT_PORT_N8N.md](docs/CHANGEMENT_PORT_N8N.md) pour plus de détails.

## Si déja installé
```bash
 cd .\recherche_offre_emploi\agent_n8n\docker\ ;
..\venv\Scripts\activate ;
 docker up -d
# puis aller dans  http://localhost:7080/ pour ouvrir n8n
```

## 📋 Description

Solution complète avec orchestration visuelle n8n, API Flask et interface de monitoring pour automatiser la recherche d'offres d'alternance en cybersécurité.

## 🚀 Installation Rapide

### Prérequis
- Docker et Docker Compose
- Python 3.8+
- Port 7080 (interface web) et 5000 (API) disponibles

### Installation

```bash
# Aller dans le dossier
cd agent_n8n

# Démarrer les services
docker-compose -f docker/docker-compose.yml up -d

# Installer les dépendances Python pour l'API
pip install -r requirements.txt

# Configuration
cp config/.env.example config/.env
# Éditer config/.env avec vos clés API
```

## ⚙️ Configuration

### Fichier `config/.env`

```env
# Clés API (obligatoire)
MISTRAL_API_KEY=votre_cle_mistral

# Configuration n8n
N8N_PORT=5678
N8N_HOST=localhost

# Configuration API Flask
FLASK_PORT=5000
FLASK_HOST=0.0.0.0

# Configuration Email (optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=votre_email@gmail.com
EMAIL_PASS=votre_mot_de_passe_app
```

### Configuration n8n

```bash
# Setup automatique de n8n
python config/config_setup_mistral.py

# Accès interface n8n
# http://localhost:7080
```

## 🎯 Utilisation

### 1. Interface n8n

```bash
# Ouvrir l'interface
http://localhost:7080

# Importer un workflow
# Aller dans Menu > Import
# Sélectionner un fichier .json depuis workflows/
```

### 2. API Flask

```bash
# Démarrer l'API
cd api/
python api_scraper_pour_n8n.py

# Endpoints disponibles
GET  /health              # Status de l'API
POST /search_jobs         # Recherche d'offres
POST /analyze_jobs        # Analyse IA
GET  /results/<job_id>    # Récupérer résultats
```

### 3. Workflows Disponibles

| Workflow | Description | Fonctionnalités |
|----------|-------------|----------------|
| `workflow_n8n_ultra_simple.json` | Basique | Scraping + Excel |
| `workflow_n8n_final_avec_email.json` | Complet | Scraping + IA + Email |
| `workflow_n8n_mistral_alternance.json` | Avancé | Analyse Mistral complète |

## 📁 Structure

```
agent_n8n/
├── api/                        # API Flask
│   └── api_scraper_pour_n8n.py # Serveur API principal
├── workflows/                  # Workflows n8n (JSON)
│   ├── workflow_n8n_ultra_simple.json
│   ├── workflow_n8n_final_avec_email.json
│   └── workflow_n8n_mistral_alternance.json
├── config/                     # Configuration
│   ├── .env.example           # Template configuration
│   └── config_setup_mistral.py # Setup automatique
├── docker/                     # Docker setup
│   └── docker-compose.yml     # Services Docker
├── requirements.txt           # Dépendances Python
└── README.md                  # Ce fichier
```

## ✅ Fonctionnalités

- ✅ **Interface graphique** n8n intuitive
- ✅ **API REST** pour intégrations
- ✅ **Orchestration visuelle** des workflows
- ✅ **Monitoring en temps réel**
- ✅ **Notifications email/Slack**
- ✅ **Webhooks** pour intégrations
- ✅ **Scheduling** automatique
- ✅ **Logs centralisés**

## 🔄 Workflows

### Workflow Simple

1. **Trigger** : Cron ou manuel
2. **Scraping** : API Pôle Emploi
3. **Filtrage** : Critères métier
4. **Export** : Excel/CSV
5. **Notification** : Email

### Workflow Avancé

1. **Trigger** : Multiple sources
2. **Scraping** : Multi-plateformes
3. **Analyse IA** : Mistral scoring
4. **Enrichissement** : Données entreprise
5. **Distribution** : Multi-canaux

## 🖥️ Interface API

### Endpoints

```bash
# Recherche d'offres
curl -X POST http://localhost:5000/search_jobs \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["cybersécurité", "alternance"],
    "location": "Paris",
    "max_results": 20
  }'

# Analyse IA
curl -X POST http://localhost:5000/analyze_jobs \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [...],
    "analysis_type": "full"
  }'
```

### Réponses

```json
{
  "status": "success",
  "job_id": "job_123",
  "results": {
    "total_jobs": 15,
    "analyzed_jobs": 12,
    "excel_file": "/outputs/report_123.xlsx"
  }
}
```

## 📊 Monitoring

### Interface n8n

- **Executions** : Historique des exécutions
- **Logs** : Logs détaillés par étape
- **Performance** : Métriques de performance
- **Webhooks** : Monitoring des webhooks

### Métriques Clés

- ⏱️ **Temps d'exécution** : < 5 minutes
- 🎯 **Taux de succès** : > 95%
- 📊 **Offres trouvées** : 10-50 par recherche
- 🔍 **Pertinence IA** : Score > 0.7

## 🔧 Maintenance

### Logs

```bash
# Logs n8n
docker-compose -f docker/docker-compose.yml logs n8n

# Logs API Flask
tail -f api/logs/flask.log

# Logs workflows
# Disponibles dans l'interface n8n
```

### Sauvegarde

```bash
# Export workflows
# Interface n8n > Menu > Export

# Sauvegarde base de données
docker exec n8n-db pg_dump > backup.sql
```

## 🚨 Résolution de Problèmes

### n8n ne démarre pas

```bash
# Vérifier les ports
netstat -an | findstr 5678

# Logs Docker
docker-compose -f docker/docker-compose.yml logs
```

### API Flask erreur

```bash
# Test de l'API
curl http://localhost:5000/health

# Logs détaillés
python api/api_scraper_pour_n8n.py --debug
```

### Workflow échoue

1. Vérifier les credentials dans n8n
2. Tester chaque noeud individuellement
3. Consulter les logs d'exécution

## 📚 Documentation

- 📖 [Guide complet n8n](/shared/docs/guide_n8n_api_complet.md)
- ⚙️ [Configuration email](/shared/docs/config_email_n8n.md)
- 🐛 [Debug guide](/shared/docs/debug_mistral_n8n.md)

---

*Agent n8n v2.0 - Orchestration professionnelle* 🚀