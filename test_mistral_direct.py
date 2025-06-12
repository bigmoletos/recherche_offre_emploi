#!/usr/bin/env python3
"""
Test direct de l'API Mistral
Vérifie que l'API fonctionne correctement avant d'utiliser n8n
"""

import requests
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('agent_n8n/config/.env')

def test_mistral_api():
    """Test direct de l'API Mistral"""

    # Récupérer la clé API
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("❌ MISTRAL_API_KEY non trouvée dans .env")
        return False

    print("🧪 === TEST DIRECT API MISTRAL ===")
    print(f"🔑 API Key: {'✅ Configurée' if api_key else '❌ Manquante'}")

    # Données de test
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "user",
                "content": "Analyse cette offre d'emploi : Titre: Alternance Cybersécurité chez TechCorp à Paris. Cette offre correspond-elle à une alternance en cybersécurité ? Réponds uniquement par: VALIDE ou INVALIDE"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 10
    }

    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    print("\n📤 Envoi de la requête...")
    print(f"Model: {payload['model']}")
    print(f"Prompt: {payload['messages'][0]['content'][:50]}...")

    try:
        # Requête POST vers Mistral
        response = requests.post(
            'https://api.mistral.ai/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n📡 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            if 'choices' in result and len(result['choices']) > 0:
                ai_response = result['choices'][0]['message']['content']
                print(f"✅ Réponse Mistral: '{ai_response}'")
                print(f"✅ Classification: {'VALIDE' if 'VALIDE' in ai_response.upper() else 'INVALIDE'}")
                print("🎉 API Mistral fonctionne parfaitement !")
                return True
            else:
                print("❌ Réponse Mistral sans 'choices'")
                print(f"Réponse: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"Réponse: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_api_structure():
    """Test de la structure de l'API scraper"""
    print("\n🔍 === TEST STRUCTURE API SCRAPER ===")

    try:
        # Test de santé
        health_response = requests.get('http://localhost:9555/health', timeout=5)
        if health_response.status_code == 200:
            print("✅ API Scraper accessible")
        else:
            print(f"❌ API Scraper erreur: {health_response.status_code}")
            return False

        # Test de données
        payload = {
            "termes": ["alternance cybersécurité"],
            "max_offres": 2,
            "sources": ["pole_emploi"]
        }

        scrape_response = requests.post(
            'http://localhost:9555/scrape-offres',
            json=payload,
            timeout=30
        )

        if scrape_response.status_code == 200:
            result = scrape_response.json()
            print(f"✅ Scraping réussi: {result.get('success', False)}")

            if result.get('results', {}).get('offres'):
                offres = result['results']['offres']
                print(f"✅ Offres trouvées: {len(offres)}")

                if len(offres) > 0:
                    offre = offres[0]
                    print(f"✅ Structure offre: {list(offre.keys())}")
                    return True
            else:
                print("❌ Pas d'offres dans la réponse")
                return False
        else:
            print(f"❌ Erreur scraping: {scrape_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erreur API Scraper: {e}")
        return False

if __name__ == "__main__":
    print("🚀 === TESTS COMPLETS ===")

    # Test 1: API Scraper
    api_ok = test_api_structure()

    # Test 2: API Mistral
    mistral_ok = test_mistral_api()

    print("\n📊 === RÉSUMÉ ===")
    print(f"API Scraper: {'✅ OK' if api_ok else '❌ FAILED'}")
    print(f"API Mistral: {'✅ OK' if mistral_ok else '❌ FAILED'}")

    if api_ok and mistral_ok:
        print("🎉 Tous les tests passent ! Le problème vient de n8n.")
        print("\n💡 Solutions:")
        print("1. Supprimer MANUELLEMENT les bodyParameters dans n8n")
        print("2. Activer 'JSON Body' dans le node HTTP Request")
        print("3. Utiliser le workflow test_mistral_simple.json")
    else:
        print("❌ Il y a des problèmes à résoudre avant n8n")