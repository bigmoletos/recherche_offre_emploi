#!/usr/bin/env python3
"""
Test direct de la clé API Mistral
"""
import requests
import json

def test_mistral_key():
    """Test de la clé API Mistral"""

    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": "Bearer iISnB6RgjwRnpAF09peyjNjDS6HaUUvr",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "user",
                "content": "Test simple"
            }
        ],
        "max_tokens": 50
    }

    try:
        print("🔍 Test de la clé API Mistral...")
        print(f"URL: {url}")
        print(f"Authorization: Bearer {headers['Authorization'][7:17]}...") # Masquer la clé

        response = requests.post(url, headers=headers, json=data)

        print(f"\n📊 Statut HTTP: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCÈS ! Clé API valide")
            print(f"Modèle: {result.get('model', 'N/A')}")
            print(f"Contenu: {result['choices'][0]['message']['content']}")
            print(f"Tokens: {result['usage']['total_tokens']}")
            return True
        else:
            print("❌ ERREUR !")
            print(f"Status: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    test_mistral_key()