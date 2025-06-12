#!/usr/bin/env python3
"""
Test direct du workflow sans webhook
Simule exactement le comportement du workflow n8n
"""

import requests
import json
from datetime import datetime

def simulate_n8n_workflow():
    """Simulation complète du workflow n8n en Python"""

    print("🔧 Simulation du Workflow n8n Agent Alternance")
    print("=" * 60)

    # Étape 1: Configuration des paramètres de recherche
    print("\n1️⃣ Configuration Recherche...")
    search_config = {
        "search_keywords": "alternance cybersécurité,apprentissage cyber,alternant sécurité informatique",
        "target_level": "Master 1"
    }
    print(f"✅ Mots-clés: {search_config['search_keywords']}")
    print(f"✅ Niveau: {search_config['target_level']}")

    # Étape 2: Génération de données de test (remplace les scrapers)
    print("\n2️⃣ Génération des Données Test...")
    test_offers = [
        {
            "title": "Alternance Cybersécurité - Analyste SOC",
            "company": "SecureTech Solutions",
            "location": "Paris (75)",
            "duration": "24 mois",
            "start_date": "septembre 2025",
            "description": "Recherchons alternant pour poste d'analyste SOC. Formation en cybersécurité. Missions: monitoring, analyse incidents, reporting.",
            "url": "https://example.com/offer1",
            "scraper_source": "test",
            "scraped_at": datetime.now().isoformat()
        },
        {
            "title": "Formation Cybersécurité - École XYZ",
            "company": "École Supérieure Info",
            "location": "Lyon (69)",
            "duration": "3 ans",
            "start_date": "septembre 2025",
            "description": "Formation diplômante en cybersécurité. Programme complet avec stage.",
            "url": "https://example.com/formation1",
            "scraper_source": "test",
            "scraped_at": datetime.now().isoformat()
        }
    ]
    print(f"✅ {len(test_offers)} offres générées pour test")

    # Étape 3: Classification avec Mistral
    print("\n3️⃣ Classification IA avec Mistral...")
    api_key = "fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95"

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    classified_offers = []

    for i, offer in enumerate(test_offers, 1):
        print(f"\n📋 Classification {i}: {offer['title']}")

        # Requête Mistral (exactement comme dans n8n)
        mistral_data = {
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
                json=mistral_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()

                # Enrichir l'offre avec la classification
                offer['ai_response'] = ai_response
                offer['original_title'] = offer['title']
                offer['original_company'] = offer['company']

                print(f"🤖 Mistral: {ai_response}")

                # Filtrage (comme le nœud IF dans n8n)
                if ai_response.startswith('VALIDE'):
                    offer['status'] = "✅ Offre validée par Mistral"
                    classified_offers.append(offer)
                    print(f"✅ → VALIDÉE")
                else:
                    offer['status'] = "❌ Offre rejetée"
                    print(f"❌ → REJETÉE: {ai_response}")

            else:
                print(f"❌ Erreur API Mistral: {response.status_code}")

        except Exception as e:
            print(f"❌ Exception: {e}")

    # Étape 4: Agrégation des résultats
    print(f"\n4️⃣ Agrégation des Résultats...")
    print(f"✅ Offres validées: {len(classified_offers)}")
    print(f"❌ Offres rejetées: {len(test_offers) - len(classified_offers)}")

    # Étape 5: Génération du rapport (simulation)
    print(f"\n5️⃣ Génération du Rapport Excel...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rapport_filename = f"rapport_alternance_cybersecurite_mistral_{timestamp}.xlsx"

    rapport_stats = {
        "total_offres": len(classified_offers),
        "sites_scrapes": list(set(offer['scraper_source'] for offer in classified_offers)),
        "top_locations": {},
        "rapport_path": f"/app/outputs/{rapport_filename}",
        "generation_date": datetime.now().isoformat(),
        "ai_engine": "Mistral Large"
    }

    print(f"📄 Rapport simulé: {rapport_filename}")
    print(f"🤖 IA utilisée: {rapport_stats['ai_engine']}")
    print(f"📊 Statistiques: {rapport_stats}")

    print("\n" + "=" * 60)
    print("🎉 SIMULATION DE WORKFLOW TERMINÉE !")
    print("💡 Le workflow n8n devrait fonctionner de la même manière")
    print("🔧 Vérifiez que le workflow est ACTIVÉ dans n8n")

    return classified_offers, rapport_stats

if __name__ == "__main__":
    simulate_n8n_workflow()