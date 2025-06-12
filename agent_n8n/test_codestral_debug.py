#!/usr/bin/env python3
"""
Test spécifique pour l'API Codestral
Utilise le bon endpoint et la bonne clé API
"""

import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

def load_environment():
    """Charge les variables d'environnement"""
    env_files = [
        'config/.env',
        '.env',
        '../.env',
        '../../.env'
    ]

    for env_file in env_files:
        if Path(env_file).exists():
            load_dotenv(env_file)
            print(f"✅ Fichier .env chargé: {env_file}")
            return True

    print("⚠️  Aucun fichier .env trouvé")
    return False

def test_codestral_api():
    """Test direct de l'API Codestral avec les bons paramètres"""

    print("🧪 === TEST API CODESTRAL ===")

    # Récupération des paramètres Codestral
    api_key = os.getenv('MISTRAL_API_KEY_CODESTRAL')
    endpoint = os.getenv('MISTRAL_CHAT_ENDPOINT', 'https://codestral.mistral.ai/v1/chat/completions')

    if not api_key:
        print("❌ MISTRAL_API_KEY_CODESTRAL non trouvée dans .env")
        return False

    print(f"🔑 Codestral API Key: {'✅ Configurée (' + api_key[:8] + '...)' if api_key else '❌ Manquante'}")
    print(f"🌐 Endpoint: {endpoint}")

    # Payload de test pour Codestral
    payload = {
        "model": "codestral-latest",  # Modèle Codestral
        "messages": [
            {
                "role": "user",
                "content": "Analyse cette offre d'emploi : Titre: Alternance Cybersécurité chez TechCorp à Paris. Cette offre correspond-elle à une alternance en cybersécurité ? Réponds uniquement par: VALIDE ou INVALIDE"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 50  # Un peu plus pour Codestral
    }

    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    print(f"\n📤 Test Codestral...")
    print(f"Model: {payload['model']}")
    print(f"Max tokens: {payload['max_tokens']}")
    print(f"Prompt: {payload['messages'][0]['content'][:50]}...")

    try:
        # Requête vers l'API Codestral
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n📥 Réponse reçue:")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès ! Réponse Codestral:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(f"\n🎯 Réponse Codestral: '{content}'")
                print(f"🔍 Classification: {'VALIDE' if 'VALIDE' in content.upper() else 'INVALIDE'}")
                return True, data
            else:
                print("❌ Structure de réponse inattendue")
                return False, data

        elif response.status_code == 401:
            print("❌ Erreur 401 - Clé API Codestral invalide")
            print(f"Response: {response.text}")
            return False, None

        elif response.status_code == 422:
            print("❌ Erreur 422 - Données de requête invalides pour Codestral")
            print(f"Response: {response.text}")
            return False, None

        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Response: {response.text}")
            return False, None

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False, None

def test_standard_mistral_api():
    """Test de l'API Mistral standard pour comparaison"""

    print("\n🧪 === TEST API MISTRAL STANDARD ===")

    # Test avec les autres clés disponibles
    api_keys = [
        ('MISTRAL_API_KEY', os.getenv('MISTRAL_API_KEY')),
        ('MISTRAL_API_KEY_CURSOR_MCP_SERVER', os.getenv('MISTRAL_API_KEY_CURSOR_MCP_SERVER'))
    ]

    for key_name, api_key in api_keys:
        if not api_key or api_key == "votre-clé-api-mistral":
            print(f"⏭️  {key_name}: non configurée ou valeur par défaut")
            continue

        print(f"\n🔑 Test avec {key_name}: {api_key[:8]}...")

        payload = {
            "model": "mistral-small-latest",
            "messages": [
                {
                    "role": "user",
                    "content": "Test de connexion"
                }
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        try:
            response = requests.post(
                'https://api.mistral.ai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=15
            )

            print(f"📥 Status: {response.status_code}")

            if response.status_code == 200:
                print(f"✅ {key_name} fonctionne!")
                return True, key_name, api_key
            else:
                print(f"❌ {key_name} erreur: {response.status_code}")

        except Exception as e:
            print(f"❌ {key_name} connexion échouée: {str(e)[:50]}...")

    return False, None, None

def generate_n8n_config(working_api_key, endpoint, model):
    """Génère la configuration N8N avec la bonne API"""

    print(f"\n🔧 === CONFIGURATION N8N POUR {model.upper()} ===")

    print(f"\n1️⃣ **Credential Configuration:**")
    print(f"   - Nom: 'CodestralApi' (exactement)")
    print(f"   - Type: 'HTTP Header Auth'")
    print(f"   - Header Name: 'Authorization'")
    print(f"   - Header Value: 'Bearer {working_api_key}'")

    print(f"\n2️⃣ **HTTP Request Node:**")
    print(f"   - URL: {endpoint}")
    print(f"   - Method: POST")
    print(f"   - Authentication: predefinedCredentialType")
    print(f"   - nodeCredentialType: httpHeaderAuth")

    print(f"\n3️⃣ **JSON Body:**")
    example_payload = {
        "model": model,
        "messages": [{"role": "user", "content": "{{ $json.prompt }}"}],
        "temperature": 0.1,
        "max_tokens": 50
    }
    print(json.dumps(example_payload, indent=2))

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC CODESTRAL + MISTRAL APIs")
    print("=" * 60)

    # Chargement de l'environnement
    load_environment()

    # Test 1: API Codestral
    print("\n1️⃣ Test API Codestral...")
    codestral_success, codestral_data = test_codestral_api()

    # Test 2: API Mistral standard
    print("\n2️⃣ Test API Mistral standard...")
    mistral_success, working_key_name, working_key = test_standard_mistral_api()

    # Résumé et recommendations
    print("\n📋 === RÉSUMÉ ===")
    print(f"Codestral API: {'✅ OK' if codestral_success else '❌ Problème'}")
    print(f"Mistral Standard: {'✅ OK' if mistral_success else '❌ Problème'}")

    if codestral_success:
        print("\n🎉 Codestral fonctionnel !")
        print("📝 Recommandation: Utilisez Codestral pour de meilleures performances")
        generate_n8n_config(
            os.getenv('MISTRAL_API_KEY_CODESTRAL'),
            os.getenv('MISTRAL_CHAT_ENDPOINT', 'https://codestral.mistral.ai/v1/chat/completions'),
            'codestral-latest'
        )
    elif mistral_success:
        print(f"\n🎉 Mistral standard fonctionnel avec {working_key_name}!")
        generate_n8n_config(
            working_key,
            'https://api.mistral.ai/v1/chat/completions',
            'mistral-small-latest'
        )
    else:
        print("\n🔧 Aucune API ne fonctionne")
        print("💡 Vérifiez vos clés API dans le fichier .env")
        print("💡 Contactez le support Mistral si nécessaire")