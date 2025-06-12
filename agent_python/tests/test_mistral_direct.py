#!/usr/bin/env python3
"""
Script de test direct de l'API Mistral
Valide les credentials et teste la classification d'offres
"""

import requests
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_mistral_api():
    """Test direct de l'API Mistral pour validation"""

    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("❌ ERREUR: MISTRAL_API_KEY non trouvée dans .env")
        return False

    print(f"🔑 Utilisation de la clé: {api_key[:20]}...")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Données de test - même structure que n8n
    test_offers = [
        {
            "title": "Alternance Cybersécurité - Analyste SOC",
            "company": "SecureTech Solutions",
            "description": "Recherchons alternant pour poste d'analyste SOC. Formation en cybersécurité. Missions: monitoring, analyse incidents, reporting."
        },
        {
            "title": "Formation Cybersécurité - École XYZ",
            "company": "École Supérieure Info",
            "description": "Formation diplômante en cybersécurité. Programme complet avec stage."
        }
    ]

    print("🚀 Test de l'API Mistral...")
    print("=" * 60)

    for i, offer in enumerate(test_offers, 1):
        print(f"\n📋 Test {i}: {offer['title']}")

        data = {
            "model": "mistral-large-latest",
            "messages": [
                {
                    "role": "system",
                    "content": "Tu es un expert en filtrage d'offres d'emploi. Détermine si une offre est VALIDE (vraie alternance cybersécurité/réseaux en entreprise) ou INVALIDE (formation/école/stage court). Réponds UNIQUEMENT par 'VALIDE' ou 'INVALIDE: raison'."
                },
                {
                    "role": "user",
                    "content": f"Analyse: Titre: {offer['title']} - Entreprise: {offer['company']} - Description: {offer['description']}"
                }
            ],
            "temperature": 0.1,
            "max_tokens": 100
        }

        try:
            response = requests.post(
                'https://api.mistral.ai/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )

            print(f"📡 Status HTTP: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']

                if ai_response.startswith('VALIDE'):
                    status = "✅ VALIDÉE"
                else:
                    status = "❌ REJETÉE"

                print(f"🤖 Réponse Mistral: {ai_response}")
                print(f"🎯 Classification: {status}")

            else:
                print(f"❌ Erreur API: {response.status_code}")
                print(f"📝 Détails: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur connexion: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return False

    print("\n" + "=" * 60)
    print("✅ Tests Mistral terminés avec succès!")
    print("💡 Votre credential Mistral fonctionne correctement")
    return True

def check_n8n_status():
    """Vérifier si n8n est accessible"""
    try:
        response = requests.get('http://localhost:5678/rest/login', timeout=5)
        if response.status_code in [200, 401]:  # 401 = pas connecté mais n8n fonctionne
            print("✅ n8n est accessible sur http://localhost:5678")
            return True
    except:
        pass

    print("❌ n8n non accessible - vérifiez Docker")
    return False

if __name__ == "__main__":
    print("🔧 Test de Configuration Mistral + n8n")
    print("=" * 60)

    # Test 1: n8n
    print("\n1️⃣ Vérification n8n...")
    check_n8n_status()

    # Test 2: API Mistral
    print("\n2️⃣ Test API Mistral...")
    success = test_mistral_api()

    if success:
        print("\n🎉 Configuration prête ! Vous pouvez importer le workflow dans n8n")
        print("📝 Prochaine étape: Importer workflow_n8n_mistral_corrected.json")
    else:
        print("\n🔧 Problème détecté - vérifiez les credentials Mistral")