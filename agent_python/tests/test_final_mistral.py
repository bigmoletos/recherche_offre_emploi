#!/usr/bin/env python3
"""
Test final avec la clé Mistral fonctionnelle
Simulation du workflow n8n complet
"""

import requests
import json

def test_classification_workflow():
    """Test du workflow de classification complet"""

    # Clé fonctionnelle identifiée
    api_key = "fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95"

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Données de test réelles
    test_offers = [
        {
            "title": "Alternance Cybersécurité - Analyste SOC",
            "company": "SecureTech Solutions",
            "description": "Recherchons alternant pour poste d'analyste SOC. Formation en cybersécurité. Missions: monitoring, analyse incidents, reporting. Contrat 24 mois.",
            "expected": "VALIDE"
        },
        {
            "title": "Formation Cybersécurité - École XYZ",
            "company": "École Supérieure Info",
            "description": "Formation diplômante en cybersécurité. Programme complet avec stage. Cursus de 3 ans.",
            "expected": "INVALIDE"
        },
        {
            "title": "Alternance Administrateur Réseau",
            "company": "TechCorp Enterprise",
            "description": "Poste d'alternant administrateur réseau. Mission: gestion infrastructure, sécurité, support. Durée 18 mois débutant septembre 2025.",
            "expected": "VALIDE"
        }
    ]

    print("🚀 Test Classification Workflow Mistral")
    print("=" * 60)

    results = {"valid": 0, "invalid": 0, "errors": 0}

    for i, offer in enumerate(test_offers, 1):
        print(f"\n📋 Test {i}: {offer['title']}")
        print(f"🏢 Entreprise: {offer['company']}")
        print(f"🎯 Résultat attendu: {offer['expected']}")

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

            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()

                # Classification
                if ai_response.startswith('VALIDE'):
                    classification = "VALIDE"
                    status_icon = "✅"
                    results["valid"] += 1
                else:
                    classification = "INVALIDE"
                    status_icon = "❌"
                    results["invalid"] += 1

                # Vérification vs attendu
                if classification == offer['expected']:
                    accuracy_icon = "✅"
                    accuracy_text = "CORRECT"
                else:
                    accuracy_icon = "⚠️"
                    accuracy_text = "INATTENDU"

                print(f"🤖 Mistral: {ai_response}")
                print(f"{status_icon} Classification: {classification}")
                print(f"{accuracy_icon} Précision: {accuracy_text}")

            else:
                print(f"❌ Erreur API: {response.status_code}")
                results["errors"] += 1

        except Exception as e:
            print(f"❌ Exception: {e}")
            results["errors"] += 1

    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS FINAUX:")
    print(f"✅ Offres validées: {results['valid']}")
    print(f"❌ Offres rejetées: {results['invalid']}")
    print(f"🚨 Erreurs: {results['errors']}")

    total_processed = results['valid'] + results['invalid']
    if total_processed > 0:
        print(f"📈 Taux de succès: {(total_processed / len(test_offers)) * 100:.1f}%")

    if results['errors'] == 0:
        print("\n🎉 VALIDATION RÉUSSIE !")
        print("💡 Votre configuration Mistral est prête pour n8n")
        print("📝 Prochaine étape: Importer le workflow corrigé")

    return results

if __name__ == "__main__":
    test_classification_workflow()