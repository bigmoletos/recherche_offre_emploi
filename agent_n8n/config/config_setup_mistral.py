#!/usr/bin/env python3
"""
Script de configuration automatique pour l'agent alternance + n8n + Mistral AI
==============================================================================

Ce script configure automatiquement :
- Connexion à n8n avec credentials
- Configuration Mistral AI (au lieu d'OpenAI)
- Import du workflow principal
- Validation de la configuration

Auteur: Assistant IA
Version: 1.0 - Mistral Edition
"""

import os
import json
import requests
import secrets
from pathlib import Path
from dotenv import load_dotenv
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class N8nMistralConfigurator:
    """Configurateur automatique pour n8n et l'agent alternance avec Mistral."""

    def __init__(self):
        """Initialise le configurateur avec les variables d'environnement."""
        load_dotenv()

        self.login = os.getenv('LOGIN_N8N')
        self.password = os.getenv('PASSWORD_N8N')
        self.host = os.getenv('N8N_HOST', 'localhost')
        self.port = os.getenv('N8N_PORT', '5678')
        self.protocol = os.getenv('N8N_PROTOCOL', 'http')
        self.base_url = f"{self.protocol}://{self.host}:{self.port}"

        # Validation des credentials requis
        if not self.login or not self.password:
            raise ValueError("LOGIN_N8N et PASSWORD_N8N doivent être définis dans .env")

    def generate_encryption_key(self) -> str:
        """Génère une clé d'encryption sécurisée pour n8n."""
        return secrets.token_urlsafe(32)

    def test_connection(self) -> bool:
        """Teste la connexion à n8n."""
        try:
            logger.info(f"Test connexion à {self.base_url}")
            response = requests.get(
                f"{self.base_url}/healthz",
                auth=(self.login, self.password),
                timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur connexion n8n: {e}")
            return False

    def get_existing_credentials(self) -> dict:
        """Récupère la liste des credentials existants."""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/credentials",
                auth=(self.login, self.password)
            )
            if response.status_code == 200:
                existing = {cred['name']: cred['id'] for cred in response.json()}
                logger.info(f"Credentials existants: {list(existing.keys())}")
                return existing
            return {}
        except Exception as e:
            logger.error(f"Erreur récupération credentials: {e}")
            return {}

    def create_credentials(self) -> bool:
        """Crée les credentials nécessaires pour Mistral."""
        logger.info("Création des credentials API avec Mistral...")

        existing_creds = self.get_existing_credentials()
        success_count = 0

        # Configuration des credentials avec Mistral
        credentials_config = [
            {
                "name": "Mistral AI API Key",
                "type": "httpHeaderAuth",  # Credential générique pour Mistral
                "data": {
                    "name": "Authorization",
                    "value": f"Bearer {os.getenv('MISTRAL_API_KEY', '')}"
                },
                "required_env": "MISTRAL_API_KEY"
            },
            {
                "name": "Mistral Chat Endpoint",
                "type": "httpHeaderAuth",
                "data": {
                    "name": "Content-Type",
                    "value": "application/json"
                },
                "required_env": "MISTRAL_CHAT_ENDPOINT"
            }
        ]

        # Credentials optionnels
        optional_credentials = [
            {
                "name": "SMTP Email",
                "type": "smtp",
                "data": {
                    "user": os.getenv('SMTP_USER', ''),
                    "password": os.getenv('SMTP_PASSWORD', ''),
                    "host": os.getenv('SMTP_HOST', 'smtp.gmail.com'),
                    "port": int(os.getenv('SMTP_PORT', '587')),
                    "secure": os.getenv('SMTP_SECURE', 'false').lower() == 'true'
                },
                "required_env": "SMTP_USER"
            },
            {
                "name": "Slack Webhook",
                "type": "slackApi",
                "data": {
                    "accessToken": os.getenv('SLACK_BOT_TOKEN', ''),
                    "webhookUrl": os.getenv('SLACK_WEBHOOK_URL', '')
                },
                "required_env": "SLACK_WEBHOOK_URL"
            }
        ]

        # Combine les credentials obligatoires et optionnels
        all_credentials = credentials_config + optional_credentials

        for cred_config in all_credentials:
            cred_name = cred_config['name']
            required_env = cred_config['required_env']

            # Vérifier si la variable d'environnement est définie
            if not os.getenv(required_env):
                logger.warning(f"Variable {required_env} non définie, ignoré {cred_name}")
                continue

            # Vérifier si le credential existe déjà
            if cred_name in existing_creds:
                logger.info(f"Credential '{cred_name}' existe déjà")
                success_count += 1
                continue

            # Créer le credential
            try:
                credential_data = {
                    "name": cred_name,
                    "type": cred_config['type'],
                    "data": cred_config['data']
                }

                response = requests.post(
                    f"{self.base_url}/api/v1/credentials",
                    json=credential_data,
                    auth=(self.login, self.password)
                )

                if response.status_code in [200, 201]:
                    logger.info(f"✅ Credential '{cred_name}' créé avec succès")
                    success_count += 1
                else:
                    logger.error(f"⚠️ Erreur création '{cred_name}': {response.status_code} - {response.text}")

            except Exception as e:
                logger.error(f"❌ Exception création '{cred_name}': {e}")

        logger.info(f"Credentials créés: {success_count}")
        return success_count > 0

    def validate_environment(self) -> dict:
        """Valide les variables d'environnement pour Mistral."""
        validation_results = {
            'required': {},
            'optional': {},
            'missing_required': [],
            'missing_optional': []
        }

        # Variables requises pour n8n
        required_vars = {
            'LOGIN_N8N': 'Login n8n',
            'PASSWORD_N8N': 'Password n8n'
        }

        # Variables Mistral disponibles
        mistral_vars = {
            'MISTRAL_API_KEY': 'Mistral API Key principal',
            'MISTRAL_API_LOGIN': 'Mistral Login',
            'MISTRAL_API_KEY_CODESTRAL': 'Mistral Codestral Key',
            'MISTRAL_CHAT_ENDPOINT': 'Mistral Chat Endpoint',
            'MISTRAL_COMPLETION_ENDPOINT': 'Mistral Completion Endpoint',
            'MISTRAL_API_KEY_CURSOR_MCP_SERVER': 'Mistral Cursor MCP Key'
        }

        # Variables optionnelles
        optional_vars = {
            'N8N_ENCRYPTION_KEY': 'Clé encryption n8n',
            'SMTP_USER': 'Notifications email',
            'SMTP_PASSWORD': 'Password email',
            'SLACK_WEBHOOK_URL': 'Notifications Slack (optionnel)',
            'SLACK_BOT_TOKEN': 'Slack Bot Token (optionnel)'
        }

        # Vérification variables requises
        for var, desc in required_vars.items():
            value = os.getenv(var)
            if value:
                validation_results['required'][var] = f"✅ {desc}"
            else:
                validation_results['missing_required'].append(f"❌ {var}: {desc}")

        # Vérification variables Mistral
        for var, desc in mistral_vars.items():
            value = os.getenv(var)
            if value:
                validation_results['required'][var] = f"✅ {desc}"

        # Vérification variables optionnelles
        for var, desc in optional_vars.items():
            value = os.getenv(var)
            if value:
                validation_results['optional'][var] = f"✅ {desc}"
            else:
                validation_results['missing_optional'].append(f"⚠️ {var}: {desc}")

        return validation_results

    def print_configuration_summary(self):
        """Affiche un résumé de la configuration."""
        logger.info("📋 RÉSUMÉ DE LA CONFIGURATION - MISTRAL EDITION")
        logger.info("=" * 55)
        logger.info(f"n8n URL: {self.base_url}")
        logger.info(f"Login: {self.login}")
        logger.info(f"Interface: {self.base_url}")

        # Validation environnement
        validation = self.validate_environment()

        logger.info("\n🤖 CONFIGURATION MISTRAL AI:")
        mistral_count = 0
        for var, status in validation['required'].items():
            if 'MISTRAL' in var:
                logger.info(f"  {status}")
                mistral_count += 1

        logger.info(f"\n🔧 VARIABLES N8N:")
        for var, status in validation['required'].items():
            if 'N8N' in var or var in ['LOGIN_N8N', 'PASSWORD_N8N']:
                logger.info(f"  {status}")

        logger.info(f"\n📧 NOTIFICATIONS (OPTIONNELLES):")
        for var, status in validation['optional'].items():
            logger.info(f"  {status}")

        if validation['missing_required']:
            logger.warning("\n❌ VARIABLES REQUISES MANQUANTES:")
            for missing in validation['missing_required']:
                logger.warning(f"  {missing}")

        if validation['missing_optional']:
            logger.info("\n⚠️ VARIABLES OPTIONNELLES MANQUANTES:")
            for missing in validation['missing_optional']:
                logger.info(f"  {missing}")

        logger.info(f"\n🎯 Configuration Mistral: {mistral_count} variables trouvées")

def generate_missing_variables():
    """Génère les variables manquantes."""
    print("\n🔧 GÉNÉRATION DES VARIABLES MANQUANTES")
    print("=" * 50)

    # Générer clé encryption n8n
    if not os.getenv('N8N_ENCRYPTION_KEY'):
        encryption_key = secrets.token_urlsafe(32)
        print(f"N8N_ENCRYPTION_KEY={encryption_key}")
        print("👆 Ajouter cette ligne dans votre fichier .env")

    # Instructions SMTP
    if not os.getenv('SMTP_USER'):
        print("\n📧 CONFIGURATION EMAIL (Optionnelle)")
        print("Pour recevoir des notifications par email :")
        print("SMTP_USER=votre_email@gmail.com")
        print("SMTP_PASSWORD=votre_mot_de_passe_app_gmail")
        print("💡 Mot de passe d'app Gmail : Google > Compte > Sécurité > Mots de passe des applications")

    # Instructions Slack
    if not os.getenv('SLACK_WEBHOOK_URL'):
        print("\n💬 CONFIGURATION SLACK (Optionnelle)")
        print("Pour recevoir des notifications Slack :")
        print("1. Créer une app Slack : https://api.slack.com/apps")
        print("2. Activer Incoming Webhooks")
        print("3. Copier l'URL du webhook")
        print("SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...")

def main():
    """Point d'entrée principal."""
    print("🤖 Configuration automatique Agent Alternance + n8n + Mistral AI")
    print("=" * 70)

    try:
        # Génération des variables manquantes
        generate_missing_variables()

        # Initialisation
        configurator = N8nMistralConfigurator()
        configurator.print_configuration_summary()

        # Test connexion
        print("\n🔍 Test connexion n8n...")
        if not configurator.test_connection():
            print("❌ Connexion n8n échouée")
            print("Vérifications nécessaires :")
            print("  1. n8n est-il démarré ?")
            print("  2. Les credentials LOGIN_N8N/PASSWORD_N8N sont-ils corrects ?")
            print("  3. Le port 5678 est-il accessible ?")

            # Suggestion pour démarrer n8n
            print("\n🚀 Pour démarrer n8n :")
            print("  npm install -g n8n")
            print("  n8n start")
            print("  OU docker-compose up -d n8n")
            return False

        print("✅ Connexion n8n réussie")

        # Création credentials
        print("\n🔐 Configuration des credentials Mistral...")
        creds_success = configurator.create_credentials()

        # Résultats finaux
        print("\n" + "=" * 70)
        if creds_success:
            print("🎉 Configuration Mistral terminée avec succès !")
            print(f"🌐 Interface n8n: {configurator.base_url}")
            print(f"👤 Login: {configurator.login}")
            print("\n📝 Prochaines étapes :")
            print("  1. Démarrer n8n si pas encore fait")
            print("  2. Importer le workflow alternance")
            print("  3. Tester l'agent avec Mistral")
            print("  4. Lancer: python agent_alternance_starter.py")
        else:
            print("⚠️ Configuration partiellement réussie")
            print("Vérifiez les logs ci-dessus pour les détails")

        return True

    except ValueError as e:
        logger.error(f"Erreur configuration: {e}")
        print("\n❌ Configuration échouée")
        print("Vérifiez que LOGIN_N8N et PASSWORD_N8N sont définis dans .env")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        print(f"\n❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)