#!/usr/bin/env python3
"""
Script d'auto-configuration N8N - Création automatique des credentials
"""

import requests
import json
import os
import time
import base64
from typing import Dict, Any, Optional

class N8NCredentialsManager:
    """Gestionnaire automatique des credentials N8N"""

    def __init__(self, n8n_url: str = "http://localhost:5678",
                 username: str = None, password: str = None):
        """
        Initialise le gestionnaire N8N

        Args:
            n8n_url: URL de l'instance N8N
            username: Nom d'utilisateur N8N
            password: Mot de passe N8N
        """
        self.n8n_url = n8n_url.rstrip('/')
        self.session = requests.Session()

        # Configuration d'authentification
        if username and password:
            # Authentification Basic
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            self.session.headers.update({
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            })

        # Vérification de la disponibilité de N8N
        self.wait_for_n8n()

    def wait_for_n8n(self, max_attempts: int = 30, delay: int = 2):
        """Attend que N8N soit disponible"""
        print(f"🔄 Attente de N8N sur {self.n8n_url}...")

        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.n8n_url}/healthz", timeout=5)
                if response.status_code == 200:
                    print("✅ N8N est disponible !")
                    return True
            except requests.exceptions.RequestException:
                pass

            print(f"⏳ Tentative {attempt + 1}/{max_attempts}...")
            time.sleep(delay)

        raise Exception("❌ N8N non disponible après attente")

    def create_credential(self, name: str, type_name: str, data: Dict[str, Any]) -> Optional[str]:
        """
        Crée un credential N8N

        Args:
            name: Nom du credential
            type_name: Type de credential N8N
            data: Données du credential

        Returns:
            ID du credential créé ou None si erreur
        """
        credential_payload = {
            "name": name,
            "type": type_name,
            "data": data
        }

        try:
            # Vérifier si le credential existe déjà
            existing = self.get_credential_by_name(name)
            if existing:
                print(f"📋 Credential '{name}' existe déjà (ID: {existing['id']})")
                return existing['id']

            # Créer le nouveau credential
            response = self.session.post(
                f"{self.n8n_url}/rest/credentials",
                json=credential_payload
            )

            if response.status_code == 201:
                credential_id = response.json().get('id')
                print(f"✅ Credential '{name}' créé avec l'ID: {credential_id}")
                return credential_id
            else:
                print(f"❌ Erreur création credential '{name}': {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"❌ Exception lors de la création du credential '{name}': {str(e)}")
            return None

    def get_credential_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Récupère un credential par son nom"""
        try:
            response = self.session.get(f"{self.n8n_url}/rest/credentials")
            if response.status_code == 200:
                credentials = response.json().get('data', [])
                for cred in credentials:
                    if cred.get('name') == name:
                        return cred
            return None
        except Exception:
            return None

    def setup_mistral_credentials(self):
        """Configure les credentials Mistral"""
        print("\n🔐 Configuration des credentials Mistral...")

        # Récupération des clés depuis les variables d'environnement
        mistral_key_emploi = os.getenv('mistral_key_site_emploi')
        mistral_key_cursor = os.getenv('MISTRAL_API_KEY_CURSOR_MCP_SERVER')

        credentials_config = []

        if mistral_key_emploi:
            credentials_config.append({
                'name': 'Mistral_Site_Emploi',
                'type': 'httpHeaderAuth',
                'data': {
                    'name': 'Authorization',
                    'value': f'Bearer {mistral_key_emploi}'
                }
            })

        if mistral_key_cursor:
            credentials_config.append({
                'name': 'Mistral_Cursor_MCP',
                'type': 'httpHeaderAuth',
                'data': {
                    'name': 'Authorization',
                    'value': f'Bearer {mistral_key_cursor}'
                }
            })

        # Credential générique pour Mistral API
        if mistral_key_emploi:
            credentials_config.append({
                'name': 'Mistral_API_Generic',
                'type': 'genericCredentialType',
                'data': {
                    'api_key': mistral_key_emploi,
                    'base_url': 'https://api.mistral.ai/v1'
                }
            })

        # Création des credentials
        created_credentials = []
        for config in credentials_config:
            cred_id = self.create_credential(**config)
            if cred_id:
                created_credentials.append({
                    'name': config['name'],
                    'id': cred_id,
                    'type': config['type']
                })

        return created_credentials

    def setup_environment_variables(self):
        """Configuration des variables d'environnement pour les workflows"""
        print("\n🌍 Vérification des variables d'environnement...")

        required_vars = [
            'mistral_key_site_emploi',
            'MISTRAL_API_KEY_CURSOR_MCP_SERVER',
            'NODE_ENV',
            'N8N_LOG_LEVEL'
        ]

        env_status = []
        for var in required_vars:
            value = os.getenv(var)
            status = "✅ Définie" if value else "❌ Manquante"
            # Masquer les clés sensibles
            display_value = "***" if value and 'key' in var.lower() else value

            env_status.append({
                'variable': var,
                'status': status,
                'value': display_value
            })

            print(f"  {var}: {status}")

        return env_status

    def create_workflow_template(self) -> Optional[str]:
        """Crée un workflow template de test avec les credentials"""
        print("\n📝 Création d'un workflow template...")

        workflow_data = {
            "name": "Test_Credentials_Setup",
            "active": False,
            "nodes": [
                {
                    "parameters": {},
                    "type": "n8n-nodes-base.manualTrigger",
                    "typeVersion": 1,
                    "position": [520, 340],
                    "id": "manual-trigger",
                    "name": "Manual Trigger"
                },
                {
                    "parameters": {
                        "language": "python",
                        "pythonCode": "# Test des credentials automatiques\nimport os\n\n# Variables d'environnement\nenv_vars = ['mistral_key_site_emploi', 'NODE_ENV']\n\nitems = []\nfor var in env_vars:\n    value = os.environ.get(var, 'Non définie')\n    items.append({\n        'json': {\n            'variable': var,\n            'status': 'Définie' if value != 'Non définie' else 'Manquante',\n            'value': '***' if 'key' in var.lower() and value != 'Non définie' else value\n        }\n    })\n\nreturn items"
                    },
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [720, 340],
                    "id": "test-credentials",
                    "name": "Test Credentials"
                }
            ],
            "connections": {
                "Manual Trigger": {
                    "main": [
                        [
                            {
                                "node": "Test Credentials",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
        }

        try:
            response = self.session.post(
                f"{self.n8n_url}/rest/workflows",
                json=workflow_data
            )

            if response.status_code == 201:
                workflow_id = response.json().get('id')
                print(f"✅ Workflow template créé avec l'ID: {workflow_id}")
                return workflow_id
            else:
                print(f"❌ Erreur création workflow: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Exception création workflow: {str(e)}")
            return None

    def run_full_setup(self):
        """Lance la configuration complète"""
        print("🚀 === CONFIGURATION AUTOMATIQUE N8N ===\n")

        results = {
            'credentials': [],
            'environment': [],
            'workflow_id': None,
            'success': True
        }

        try:
            # 1. Configuration des credentials
            results['credentials'] = self.setup_mistral_credentials()

            # 2. Vérification des variables d'environnement
            results['environment'] = self.setup_environment_variables()

            # 3. Création du workflow de test
            results['workflow_id'] = self.create_workflow_template()

            # 4. Résumé
            print(f"\n📊 === RÉSUMÉ ===")
            print(f"Credentials créés: {len(results['credentials'])}")
            print(f"Variables vérifiées: {len(results['environment'])}")
            print(f"Workflow template: {'✅ Créé' if results['workflow_id'] else '❌ Échec'}")

            return results

        except Exception as e:
            print(f"❌ Erreur lors de la configuration: {str(e)}")
            results['success'] = False
            return results

def main():
    """Fonction principale"""
    # Configuration depuis les variables d'environnement
    n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')
    username = os.getenv('LOGIN_N8N', 'admin')
    password = os.getenv('PASSWORD_N8N', 'admin')

    print(f"🎯 Configuration N8N sur: {n8n_url}")

    try:
        # Initialisation du gestionnaire
        manager = N8NCredentialsManager(n8n_url, username, password)

        # Lancement de la configuration
        results = manager.run_full_setup()

        if results['success']:
            print("\n🎉 Configuration N8N terminée avec succès !")
        else:
            print("\n⚠️ Configuration N8N terminée avec des erreurs.")

    except Exception as e:
        print(f"💥 Erreur fatale: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())