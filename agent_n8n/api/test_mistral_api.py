#!/usr/bin/env python3
"""
Script de test pour diagnostiquer les problèmes avec l'API Mistral
Utilisation: python test_mistral_api.py
"""

import requests
import json
import logging
from datetime import datetime

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mistral_api():
    """
    Teste l'API Mistral avec différentes configurations pour identifier le problème
    """

    # Configuration de base
    api_key = "fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95"
    base_url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Test 1: Configuration minimale
    logger.info("🧪 Test 1: Configuration minimale")
    payload_minimal = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "user",
                "content": "Dis bonjour"
            }
        ]
    }

    test_request(base_url, headers, payload_minimal, "Test minimal")

    # Test 2: Configuration avec système
    logger.info("🧪 Test 2: Configuration avec message système")
    payload_system = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "system",
                "content": "Tu es un assistant IA."
            },
            {
                "role": "user",
                "content": "Dis bonjour"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    test_request(base_url, headers, payload_system, "Test avec système")

    # Test 3: Configuration complexe comme dans N8N
    logger.info("🧪 Test 3: Configuration complexe (comme N8N)")
    payload_complex = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "system",
                "content": "Tu es un expert RH avec 15 ans d'expérience en cybersécurité et alternance."
            },
            {
                "role": "user",
                "content": "Analyse cette offre: Contrat d'apprentissage - Analyste Cybersécurité SOC. Réponds par VALIDE ou INVALIDE."
            }
        ],
        "temperature": 0.05,
        "max_tokens": 300
    }

    test_request(base_url, headers, payload_complex, "Test complexe")

def test_request(url, headers, payload, test_name):
    """
    Effectue une requête de test et affiche les résultats
    """
    try:
        logger.info(f"📤 {test_name}: Envoi de la requête...")
        logger.info(f"🔗 URL: {url}")
        logger.info(f"📋 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        logger.info(f"📥 Status Code: {response.status_code}")
        logger.info(f"📥 Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ {test_name}: SUCCESS")
            logger.info(f"📝 Réponse: {result.get('choices', [{}])[0].get('message', {}).get('content', 'Pas de contenu')[:100]}...")
            logger.info(f"🔧 Modèle utilisé: {result.get('model', 'N/A')}")
            logger.info(f"📊 Usage: {result.get('usage', {})}")
        else:
            logger.error(f"❌ {test_name}: FAILED")
            logger.error(f"💬 Response Text: {response.text}")

            try:
                error_data = response.json()
                logger.error(f"📋 Error Data: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                logger.error("❌ Impossible de parser la réponse d'erreur en JSON")

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ {test_name}: Erreur de connexion: {e}")
    except Exception as e:
        logger.error(f"❌ {test_name}: Erreur inattendue: {e}")

    logger.info("=" * 80)

if __name__ == "__main__":
    logger.info("🚀 === DÉMARRAGE DES TESTS API MISTRAL ===")
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")

    test_mistral_api()

    logger.info("🏁 === FIN DES TESTS ===")