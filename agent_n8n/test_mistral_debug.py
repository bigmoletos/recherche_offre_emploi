#!/usr/bin/env python3
"""
Script de diagnostic pour l'API Mistral et N8N
Teste l'API directement pour identifier les problèmes de configuration
"""

import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

def load_environment():
    """Charge les variables d'environnement depuis différents emplacements possibles"""
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

    print("⚠️  Aucun fichier .env trouvé. Variables d'environnement système utilisées.")
    return False

def test_mistral_api():
    """Test direct de l'API Mistral avec logs détaillés"""

    print("🧪 === TEST DIRECT API MISTRAL ===")

    # Récupérer la clé API
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("❌ MISTRAL_API_KEY non trouvée dans .env")
        print("💡 Ajoutez MISTRAL_API_KEY=votre_cle dans le fichier .env")
        return False

    print(f"🔑 API Key: {'✅ Configurée (' + api_key[:8] + '...)' if api_key else '❌ Manquante'}")

    # Données de test exactement comme dans N8N
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
    print(f"URL: https://api.mistral.ai/v1/chat/completions")
    print(f"Model: {payload['model']}")
    print(f"Max tokens: {payload['max_tokens']}")
    print(f"Prompt: {payload['messages'][0]['content'][:50]}...")

    try:
        # Requête vers l'API Mistral
        response = requests.post(
            'https://api.mistral.ai/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n📥 Réponse reçue:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès ! Réponse API:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(f"\n🎯 Réponse Mistral: '{content}'")
                print(f"🔍 Classification: {'VALIDE' if 'VALIDE' in content.upper() else 'INVALIDE'}")
                return True
            else:
                print("❌ Structure de réponse inattendue")
                return False

        elif response.status_code == 401:
            print("❌ Erreur 401 - Clé API invalide")
            print("💡 Vérifiez votre clé API Mistral")
            print(f"Response: {response.text}")
            return False

        elif response.status_code == 422:
            print("❌ Erreur 422 - Données de requête invalides")
            print("💡 Problème avec le format des données")
            print(f"Response: {response.text}")
            return False

        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def generate_n8n_fixes():
    """Génère les corrections pour les workflows N8N"""

    print("\n🔧 === CORRECTIONS POUR N8N ===")

    print("\n1️⃣ **Configuration du Credential Mistral:**")
    print("   - Nom: 'MistralApi' (exactement)")
    print("   - Type: 'Mistral Cloud account'")
    print("   - API Key: votre clé Mistral")

    print("\n2️⃣ **Configuration du nœud HTTP Request:**")
    print("   - URL: https://api.mistral.ai/v1/chat/completions")
    print("   - Method: POST")
    print("   - Authentication: predefinedCredentialType")
    print("   - nodeCredentialType: mistralCloudApi")

    print("\n3️⃣ **Format du Body (Option A - Raw JSON):**")
    print("   - contentType: 'raw'")
    print("   - rawBody: Utiliser l'expression JSON.stringify()")

    print("\n4️⃣ **Format du Body (Option B - JSON Body):**")
    print("   - contentType: 'json'")
    print("   - jsonBody: Utiliser directement l'objet JSON")

    print("\n5️⃣ **Structure JSON Mistral:**")
    mistral_example = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": "Test"}],
        "temperature": 0.1,
        "max_tokens": 10
    }
    print(json.dumps(mistral_example, indent=2))

def check_n8n_status():
    """Vérifie si N8N est accessible"""

    print("\n🔌 === VÉRIFICATION N8N ===")

    n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')

    try:
        response = requests.get(f"{n8n_url}/rest/active", timeout=5)
        if response.status_code == 200:
            print(f"✅ N8N accessible sur {n8n_url}")
            return True
        else:
            print(f"⚠️  N8N répond mais statut: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"❌ N8N non accessible sur {n8n_url}")
        print("💡 Vérifiez que N8N est démarré")
        return False

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC MISTRAL + N8N - VERSION 2.0")
    print("=" * 60)

    # Chargement de l'environnement
    load_environment()

    # Test 1: N8N
    print("\n1️⃣ Vérification N8N...")
    n8n_ok = check_n8n_status()

    # Test 2: API Mistral
    print("\n2️⃣ Test API Mistral...")
    mistral_ok = test_mistral_api()

    # Génération des corrections
    generate_n8n_fixes()

    # Nouvelles recommendations
    print("\n🆕 === NOUVEAUX WORKFLOWS DISPONIBLES ===")
    print("\n1️⃣ test_mistral_ultra_simple.json")
    print("   - ✅ Utilise jsonBody au lieu de rawBody")
    print("   - ✅ Payload préparé en entier dans Function")
    print("   - ✅ Pas de JSON.parse() dans les expressions")
    print("   - 🎯 RECOMMANDÉ pour résoudre l'erreur 422")

    print("\n2️⃣ test_mistral_code_direct.json")
    print("   - ✅ Utilise un nœud Code avec fetch()")
    print("   - ✅ Bypass complet du nœud HTTP Request")
    print("   - ✅ Contrôle total de l'appel API")
    print("   - ⚠️ Nécessite de remplacer la clé API dans le code")

    # Résumé
    print("\n📋 === RÉSUMÉ ===")
    print(f"N8N: {'✅ OK' if n8n_ok else '❌ Problème'}")
    print(f"Mistral API: {'✅ OK' if mistral_ok else '❌ Problème'}")

    if mistral_ok:
        print("\n🎉 API Mistral fonctionnelle !")
        print("📝 Prochaines étapes:")
        print("   1. Testez d'abord: test_mistral_ultra_simple.json")
        print("   2. Si ça échoue encore: test_mistral_code_direct.json")
        print("   3. Vérifiez la configuration du credential 'MistralApi'")
        print("\n💡 L'erreur 422 'Field required' vient des expressions N8N")
        print("💡 Les nouveaux workflows évitent ce problème")
    else:
        print("\n🔧 Problème détecté avec l'API Mistral")
        print("💡 Vérifiez la clé API dans votre fichier .env")