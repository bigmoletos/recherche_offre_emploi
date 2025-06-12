#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de l'API Flask pour n8n
"""

import requests
import json
import time

def test_api():
    """Test complet de l'API Flask."""
    base_url = "http://localhost:5555"

    print("🧪 TEST DE L'API SCRAPER POUR N8N")
    print("=" * 50)

    # Test 1: Health check
    print("\n1️⃣ Test Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API en ligne - Status: {data['status']}")
            print(f"   Service: {data['service']}")
        else:
            print(f"❌ Health check échec - Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API")
        print("💡 Assurez-vous que l'API est démarrée avec: python api_scraper_pour_n8n.py")
        return False
    except Exception as e:
        print(f"❌ Erreur health check: {e}")
        return False

    # Test 2: Test offres d'exemple
    print("\n2️⃣ Test Offres d'Exemple...")
    try:
        response = requests.get(f"{base_url}/test-offres", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Données test récupérées - {data['total_offres']} offres")
            print(f"   Mode test: {data['test_mode']}")
            for i, offre in enumerate(data['offres'][:2]):
                print(f"   {i+1}. {offre['title']} - {offre['company']}")
        else:
            print(f"❌ Test offres échec - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test offres: {e}")

    # Test 3: Scraping Pôle Emploi
    print("\n3️⃣ Test Scraping Pôle Emploi...")
    try:
        payload = {"terme": "alternance cybersécurité"}
        response = requests.post(
            f"{base_url}/scrape-pole-emploi",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scraping Pôle Emploi réussi - {data['total_offres']} offres")
            print(f"   Source: {data['source']}")
            if data['offres']:
                print(f"   Première offre: {data['offres'][0]['title']}")
        else:
            print(f"❌ Scraping Pôle Emploi échec - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur scraping Pôle Emploi: {e}")

    # Test 4: Scraping complet
    print("\n4️⃣ Test Scraping Complet...")
    try:
        payload = {
            "termes": ["alternance cybersécurité"],
            "max_offres": 3
        }
        response = requests.post(
            f"{base_url}/scrape-offres",
            json=payload,
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scraping complet réussi - {data['total_offres']} offres")
            print(f"   Sources: {', '.join(data['sources_utilisees'])}")
            if data['offres']:
                print(f"   Exemple: {data['offres'][0]['title']}")
                print(f"   URL: {data['offres'][0]['url']}")
        else:
            print(f"❌ Scraping complet échec - Status: {response.status_code}")
            print(f"   Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur scraping complet: {e}")

    print("\n" + "=" * 50)
    print("🎯 TESTS TERMINÉS")
    print("💡 Si tous les tests passent, l'API est prête pour n8n !")
    return True

if __name__ == "__main__":
    test_api()