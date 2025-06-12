# Configuration n8n avec Credentials
# ==================================

## 📋 Variables d'Environnement Requises

Votre fichier `.env` doit contenir :

```bash
# === CONFIGURATION N8N ===
LOGIN_N8N=votre_login_n8n
PASSWORD_N8N=votre_password_n8n
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http

# Sécurité n8n
N8N_ENCRYPTION_KEY=your_32_character_encryption_key_here
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=${LOGIN_N8N}
N8N_BASIC_AUTH_PASSWORD=${PASSWORD_N8N}

# === APIS IA ===
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_MODEL=gpt-4

# === NOTIFICATIONS ===
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SMTP_USER=votre_email@gmail.com
SMTP_PASSWORD=votre_app_password

# === CONFIGURATION AGENT ===
DEFAULT_KEYWORDS=alternance cybersécurité,apprentissage cyber
DEFAULT_LEVEL=Master 1
DEFAULT_START_DATE=septembre 2025
```

## 🚀 Démarrage n8n avec Credentials

### Option 1 : Via Docker (Recommandé)
```bash
# Créer docker-compose.yml
version: '3.8'

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${LOGIN_N8N}
      - N8N_BASIC_AUTH_PASSWORD=${PASSWORD_N8N}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=http://localhost:5678/
    volumes:
      - n8n_data:/home/node/.n8n
      - ./python_scrapers:/app/scrapers:ro
      - ./outputs:/app/outputs
    env_file:
      - .env

volumes:
  n8n_data:
```

### Option 2 : Installation Locale
```bash
# Installation n8n
npm install -g n8n

# Démarrage avec variables d'environnement
export N8N_BASIC_AUTH_ACTIVE=true
export N8N_BASIC_AUTH_USER=$LOGIN_N8N
export N8N_BASIC_AUTH_PASSWORD=$PASSWORD_N8N
n8n start
```

## 🔐 Configuration des Credentials dans n8n

### 1. Accès à l'Interface
```
URL: http://localhost:5678
Login: $LOGIN_N8N
Password: $PASSWORD_N8N
```

### 2. Configuration OpenAI
```json
{
  "name": "OpenAI API Key",
  "type": "openAiApi",
  "data": {
    "apiKey": "${OPENAI_API_KEY}"
  }
}
```

### 3. Configuration Slack
```json
{
  "name": "Slack Bot Token",
  "type": "slackApi",
  "data": {
    "accessToken": "${SLACK_BOT_TOKEN}"
  }
}
```

### 4. Configuration Email SMTP
```json
{
  "name": "SMTP Email",
  "type": "smtp",
  "data": {
    "user": "${SMTP_USER}",
    "password": "${SMTP_PASSWORD}",
    "host": "smtp.gmail.com",
    "port": 587,
    "secure": false
  }
}
```

## 📦 Import du Workflow

### Via Interface n8n
1. Se connecter à http://localhost:5678
2. Aller dans **Workflows** → **Import from file**
3. Sélectionner `workflow_n8n_alternance.json`
4. Configurer les credentials manquants

### Via API
```bash
# Import automatique du workflow
curl -X POST http://${LOGIN_N8N}:${PASSWORD_N8N}@localhost:5678/api/v1/workflows/import \
  -H "Content-Type: application/json" \
  -d @workflow_n8n_alternance.json
```

## 🔧 Script de Configuration Automatique

### config_setup.py
```python
#!/usr/bin/env python3
"""
Script de configuration automatique pour l'agent alternance + n8n
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

class N8nConfigurator:
    def __init__(self):
        load_dotenv()
        self.login = os.getenv('LOGIN_N8N')
        self.password = os.getenv('PASSWORD_N8N')
        self.host = os.getenv('N8N_HOST', 'localhost')
        self.port = os.getenv('N8N_PORT', '5678')
        self.base_url = f"http://{self.host}:{self.port}"

    def test_connection(self):
        """Teste la connexion à n8n"""
        try:
            response = requests.get(
                f"{self.base_url}/healthz",
                auth=(self.login, self.password),
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def create_credentials(self):
        """Crée les credentials nécessaires"""
        credentials = [
            {
                "name": "OpenAI API Key",
                "type": "openAiApi",
                "data": {
                    "apiKey": os.getenv('OPENAI_API_KEY')
                }
            },
            {
                "name": "Slack Bot Token",
                "type": "slackApi",
                "data": {
                    "accessToken": os.getenv('SLACK_BOT_TOKEN')
                }
            },
            {
                "name": "SMTP Email",
                "type": "smtp",
                "data": {
                    "user": os.getenv('SMTP_USER'),
                    "password": os.getenv('SMTP_PASSWORD'),
                    "host": "smtp.gmail.com",
                    "port": 587,
                    "secure": False
                }
            }
        ]

        for cred in credentials:
            if cred['data'].get('apiKey') or cred['data'].get('accessToken') or cred['data'].get('user'):
                try:
                    response = requests.post(
                        f"{self.base_url}/api/v1/credentials",
                        json=cred,
                        auth=(self.login, self.password)
                    )
                    if response.status_code == 200:
                        print(f"✅ Credential '{cred['name']}' créé")
                    else:
                        print(f"⚠️ Erreur création '{cred['name']}': {response.text}")
                except Exception as e:
                    print(f"❌ Erreur '{cred['name']}': {e}")

    def import_workflow(self):
        """Importe le workflow principal"""
        workflow_path = Path("workflow_n8n_alternance.json")
        if workflow_path.exists():
            try:
                with open(workflow_path, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)

                response = requests.post(
                    f"{self.base_url}/api/v1/workflows/import",
                    json=workflow_data,
                    auth=(self.login, self.password)
                )

                if response.status_code == 200:
                    print("✅ Workflow importé avec succès")
                else:
                    print(f"⚠️ Erreur import workflow: {response.text}")
            except Exception as e:
                print(f"❌ Erreur import workflow: {e}")
        else:
            print("❌ Fichier workflow_n8n_alternance.json non trouvé")

def main():
    print("🔧 Configuration automatique Agent Alternance + n8n")
    print("=" * 55)

    configurator = N8nConfigurator()

    # Test connexion
    print("🔍 Test connexion n8n...")
    if configurator.test_connection():
        print("✅ Connexion n8n OK")
    else:
        print("❌ Connexion n8n échouée")
        print("Vérifiez que n8n est démarré et les credentials sont corrects")
        return

    # Création credentials
    print("\n🔐 Création des credentials...")
    configurator.create_credentials()

    # Import workflow
    print("\n📦 Import du workflow...")
    configurator.import_workflow()

    print("\n🎉 Configuration terminée !")
    print(f"🌐 Interface n8n: {configurator.base_url}")
    print(f"👤 Login: {configurator.login}")

if __name__ == "__main__":
    main()
```

## 🔄 Commandes de Gestion

### Démarrage Complet
```bash
# 1. Activer l'environnement Python
cd plateformes_Freelance
venv_alternance\Scripts\activate

# 2. Démarrer n8n avec credentials
docker-compose up -d n8n
# OU
n8n start

# 3. Configuration automatique
python config_setup.py

# 4. Test de l'agent
python agent_alternance_starter.py
```

### Vérification Status
```bash
# Status n8n
curl -u $LOGIN_N8N:$PASSWORD_N8N http://localhost:5678/healthz

# Liste des workflows
curl -u $LOGIN_N8N:$PASSWORD_N8N http://localhost:5678/api/v1/workflows

# Test webhook manuel
curl -X POST http://localhost:5678/webhook/alternance-manual-trigger \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

## 🔒 Sécurité

### Bonnes Pratiques
1. **Jamais de credentials en dur** dans le code
2. **Fichier .env** dans .gitignore
3. **Rotation régulière** des API keys
4. **HTTPS en production** (pas HTTP)
5. **Firewall** sur le port 5678 en production

### Génération Clé Encryption
```python
# Générer une clé d'encryption sécurisée
import secrets
encryption_key = secrets.token_urlsafe(32)
print(f"N8N_ENCRYPTION_KEY={encryption_key}")
```

## 🎯 Prêt pour l'Automatisation !

Une fois configuré, votre agent sera capable de :
- ✅ Scraper automatiquement les sites d'emploi
- ✅ Classifier avec l'IA (GPT-4)
- ✅ Générer des rapports Excel
- ✅ Envoyer des notifications Slack/Email
- ✅ Stocker l'historique
- ✅ Monitoring et logs centralisés