#!/usr/bin/env python3
"""
Test de toutes les clés API Mistral disponibles
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_mistral_key(key_name, api_key, endpoint="https://api.mistral.ai/v1/chat/completions"):
    """Test une clé API Mistral spécifique"""

    if not api_key:
        print(f"❌ {key_name}: Clé non trouvée")
        return False

    print(f"\n🔑 Test {key_name}: {api_key[:15]}...")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "user", "content": "Test simple"}
        ],
        "max_tokens": 10
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=10)

        print(f"📡 Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ {key_name}: FONCTIONNE!")
            print(f"🤖 Réponse: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ {key_name}: Erreur {response.status_code}")
            print(f"📝 Détails: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ {key_name}: Exception - {e}")
        return False

def main():
    print("🔧 Test de Toutes les Clés Mistral")
    print("=" * 50)

    # Toutes les clés Mistral trouvées dans .env
    keys_to_test = [
        ("MISTRAL_API_KEY", os.getenv('MISTRAL_API_KEY')),
        ("MISTRAL_API_KEY_CURSOR_MCP_SERVER", os.getenv('MISTRAL_API_KEY_CURSOR_MCP_SERVER')),
        ("MISTRAL_API_KEY_CODESTRAL", os.getenv('MISTRAL_API_KEY_CODESTRAL')),
    ]

    working_keys = []

    for key_name, key_value in keys_to_test:
        if test_mistral_key(key_name, key_value):
            working_keys.append(key_name)

    print("\n" + "=" * 50)
    print("📋 RÉSULTATS:")

    if working_keys:
        print(f"✅ Clés fonctionnelles: {', '.join(working_keys)}")
        print(f"💡 Recommandation: Utiliser {working_keys[0]} dans n8n")

        # Mettre à jour le .env si nécessaire
        if 'MISTRAL_API_KEY_CURSOR_MCP_SERVER' in working_keys:
            correct_key = os.getenv('MISTRAL_API_KEY_CURSOR_MCP_SERVER')
            print(f"\n🔧 Configurez n8n avec cette clé: {correct_key}")

    else:
        print("❌ Aucune clé fonctionnelle trouvée")
        print("🔧 Vérifiez vos credentials sur platform.mistral.ai")

if __name__ == "__main__":
    main()