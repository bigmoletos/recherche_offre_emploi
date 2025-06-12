#!/usr/bin/env python3
"""
Test direct de la clé Mistral en local
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_mistral_api():
    """Test direct de l'API Mistral"""

    print("🔑 === TEST MISTRAL API EN LOCAL ===")

    # Charger les variables d'environnement
    load_dotenv('./config/.env')

    # Récupérer la clé
    mistral_key = os.getenv('mistral_key_site_emploi')

    if not mistral_key:
        print("❌ ERREUR: Variable mistral_key_site_emploi non trouvée")
        return False

    print(f"✅ Clé trouvée: {mistral_key[:8]}...")
    print(f"📏 Longueur: {len(mistral_key)} caractères")

    # Configuration de la requête
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {mistral_key}",
        "Content-Type": "application/json",
        "User-Agent": "test-local-python/1.0"
    }

    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "system",
                "content": "Tu es un expert en classification d'offres d'alternance cybersécurité."
            },
            {
                "role": "user",
                "content": """ANALYSE OFFRE ALTERNANCE CYBERSÉCURITÉ:

TITRE: Contrat d'apprentissage - Analyste Cybersécurité SOC
ENTREPRISE: Orange Cyberdefense
CONTRAT: Contrat d'apprentissage
DESCRIPTION: Formation alternance 24 mois analyste cybersécurité SOC.

CRITÈRES VALIDATION:
✅ CONTRAT = apprentissage OU alternance OU contrat pro
✅ DOMAINE = cybersécurité OU sécurité informatique
❌ EXCLURE = stage, CDI, CDD, commercial, marketing

RÉPONDS EXACTEMENT:
CLASSIFICATION: VALIDE ou INVALIDE
JUSTIFICATION: [raison courte]"""
            }
        ],
        "temperature": 0.05,
        "max_tokens": 150
    }

    try:
        print("🌐 Envoi requête à Mistral...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"📊 Code réponse: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']

            print("✅ === SUCCÈS MISTRAL ===")
            print(f"📝 Réponse: {content}")
            print(f"🎯 Modèle: {data.get('model', 'N/A')}")
            print(f"💰 Tokens: {data.get('usage', {})}")
            return True

        elif response.status_code == 401:
            print("❌ === ERREUR 401: UNAUTHORIZED ===")
            print("🔑 Clé API invalide ou expirée")
            print(f"📋 Réponse: {response.text}")
            return False

        else:
            print(f"❌ === ERREUR {response.status_code} ===")
            print(f"📋 Réponse: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ === ERREUR RÉSEAU ===")
        print(f"📋 Erreur: {e}")
        return False

def test_toutes_les_cles():
    """Test toutes les clés Mistral disponibles"""

    print("🔍 === TEST TOUTES LES CLÉS MISTRAL ===")

    load_dotenv('./config/.env')

    # Liste des variables à tester
    cles_a_tester = [
        'mistral_key_site_emploi',
        'MISTRAL_API_KEY',
        'MISTRAL_API_KEY_CURSOR_MCP_SERVER',
        'MISTRAL_API_KEY_CODESTRAL'
    ]

    resultats = {}

    for var_name in cles_a_tester:
        cle = os.getenv(var_name)
        if cle:
            print(f"\n🧪 Test {var_name}: {cle[:8]}...")

            # Test rapide
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {cle}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "mistral-large-latest",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 10
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {var_name}: FONCTIONNELLE")
                    resultats[var_name] = "OK"
                else:
                    print(f"❌ {var_name}: ERREUR {response.status_code}")
                    resultats[var_name] = f"ERREUR_{response.status_code}"
            except Exception as e:
                print(f"❌ {var_name}: EXCEPTION {e}")
                resultats[var_name] = "EXCEPTION"
        else:
            print(f"⚠️ {var_name}: NON TROUVÉE")
            resultats[var_name] = "MISSING"

    print("\n📊 === RÉSUMÉ ===")
    for var, status in resultats.items():
        print(f"{var}: {status}")

    return resultats

if __name__ == "__main__":
    print("🚀 Démarrage test Mistral local...")

    # Test complet
    resultats = test_toutes_les_cles()

    # Test détaillé si au moins une clé fonctionne
    cles_ok = [k for k, v in resultats.items() if v == "OK"]
    if cles_ok:
        print(f"\n🎯 Test détaillé avec {cles_ok[0]}...")
        test_mistral_api()
    else:
        print("\n❌ Aucune clé Mistral fonctionnelle trouvée")