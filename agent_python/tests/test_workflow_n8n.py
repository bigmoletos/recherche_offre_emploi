#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test d'Intégration Workflow n8n - Module de Validation.

Ce module teste l'intégration complète entre l'API scraper et le workflow n8n,
en simulant un appel complet du processus d'automatisation.

Fonctionnalités testées :
- Santé de l'API (/health)
- Collecte d'offres via API (/scrape-offres)
- Format de données compatible avec n8n
- Structure JSON conforme aux attentes du workflow

Usage :
    python tests/test_workflow_n8n.py

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: 03/06/2025
"""

import requests
import json
import sys
import time
from typing import Dict, Any, List
from pathlib import Path

# Configuration de test
API_BASE_URL = "http://localhost:9555"
TIMEOUT = 30  # secondes

def test_api_health() -> bool:
    """
    Teste la santé de l'API.

    Returns:
        bool: True si l'API répond correctement
    """
    print("🔍 Test de santé de l'API...")

    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API opérationnelle - Service: {data.get('service')}")
            print(f"📡 Endpoints disponibles: {', '.join(data.get('endpoints', []))}")
            print(f"🔧 Scraper disponible: {data.get('scraper_available')}")
            return True
        else:
            print(f"❌ API non fonctionnelle - Status: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion à l'API: {e}")
        return False

def test_scrape_offres() -> Dict[str, Any]:
    """
    Teste l'endpoint de collecte d'offres.

    Returns:
        Dict: Réponse de l'API ou structure d'erreur
    """
    print("\n🔍 Test de collecte d'offres...")

    # Données de test pour n8n
    test_data = {
        "termes": ["alternance cybersécurité", "alternance sécurité informatique"],
        "max_offres": 5,
        "sources": ["pole_emploi"]
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/scrape-offres",
            json=test_data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Collecte réussie - Status: {data.get('success')}")

            results = data.get('results', {})
            total_offres = results.get('total_offres', 0)
            offres = results.get('offres', [])

            print(f"📊 Total offres collectées: {total_offres}")
            print(f"📋 Offres retournées: {len(offres)}")

            if offres:
                print(f"🔹 Première offre:")
                premiere_offre = offres[0]
                print(f"   Titre: {premiere_offre.get('title', 'N/A')}")
                print(f"   Entreprise: {premiere_offre.get('company', 'N/A')}")
                print(f"   Source: {premiere_offre.get('scraper_source', 'N/A')}")

            return data
        else:
            print(f"❌ Erreur collecte - Status: {response.status_code}")
            print(f"❌ Message: {response.text}")
            return {"error": f"HTTP {response.status_code}", "message": response.text}

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
        return {"error": "Connection error", "message": str(e)}

def validate_n8n_format(api_response: Dict[str, Any]) -> bool:
    """
    Valide que la réponse API est compatible avec le workflow n8n.

    Args:
        api_response: Réponse de l'API à valider

    Returns:
        bool: True si le format est compatible n8n
    """
    print("\n🔍 Validation du format n8n...")

    # Vérifications structure attendue par n8n
    validations = [
        ("success", "Champ success présent"),
        ("results", "Section results présente"),
        ("results.offres", "Liste d'offres présente"),
        ("results.total_offres", "Compteur total présent")
    ]

    is_valid = True

    for field_path, description in validations:
        try:
            # Navigation dans la structure JSON
            current = api_response
            for key in field_path.split('.'):
                current = current[key]
            print(f"✅ {description}")
        except (KeyError, TypeError):
            print(f"❌ {description} - MANQUANT")
            is_valid = False

    # Validation structure des offres individuelles
    results = api_response.get('results', {})
    offres = results.get('offres', [])

    if offres:
        print(f"\n🔍 Validation structure des offres ({len(offres)} trouvées)...")

        required_fields = ['title', 'company', 'location', 'url', 'scraper_source']
        premiere_offre = offres[0]

        for field in required_fields:
            if field in premiere_offre:
                print(f"✅ Champ '{field}' présent")
            else:
                print(f"❌ Champ '{field}' manquant")
                is_valid = False
    else:
        print("⚠️  Aucune offre à valider")

    if is_valid:
        print("\n✅ Format compatible avec n8n workflow")
    else:
        print("\n❌ Format NON compatible avec n8n workflow")

    return is_valid

def generate_test_report(health_ok: bool, api_response: Dict[str, Any], format_ok: bool):
    """
    Génère un rapport de test complet.

    Args:
        health_ok: Résultat du test de santé
        api_response: Réponse de l'API de collecte
        format_ok: Validation du format n8n
    """
    print("\n" + "="*60)
    print("📋 RAPPORT DE TEST WORKFLOW N8N")
    print("="*60)

    # Status global
    all_tests_ok = health_ok and format_ok and api_response.get('success', False)

    print(f"🏥 Test Santé API: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"📊 Test Collecte: {'✅ PASS' if api_response.get('success', False) else '❌ FAIL'}")
    print(f"🔧 Format n8n: {'✅ PASS' if format_ok else '❌ FAIL'}")
    print(f"🎯 Status Global: {'✅ TOUS TESTS PASSÉS' if all_tests_ok else '❌ CERTAINS TESTS ÉCHOUÉS'}")

    # Détails techniques
    if api_response.get('results'):
        results = api_response['results']
        print(f"\n📈 Métriques:")
        print(f"   - Offres collectées: {results.get('total_offres', 0)}")
        print(f"   - Sources utilisées: {', '.join(results.get('sources_utilisees', []))}")
        print(f"   - Temps de collecte: {results.get('temps_collecte', 'N/A')}")

    # Recommandations
    print(f"\n💡 Recommandations:")
    if not health_ok:
        print("   - Vérifier que l'API est démarrée sur le port 9555")
    if not format_ok:
        print("   - Corriger la structure JSON pour compatibilité n8n")
    if all_tests_ok:
        print("   - Le workflow n8n peut être déployé en production")

    print("="*60)

def main():
    """
    Fonction principale de test.
    """
    print("🚀 Démarrage des tests d'intégration n8n")
    print(f"🔗 URL API: {API_BASE_URL}")

    # Test 1: Santé API
    health_ok = test_api_health()

    if not health_ok:
        print("\n❌ Tests interrompus - API non accessible")
        print("💡 Suggestion: Démarrer l'API avec: python agent_n8n/api/api_scraper_pour_n8n.py --port 9555")
        sys.exit(1)

    # Test 2: Collecte d'offres
    api_response = test_scrape_offres()

    # Test 3: Validation format n8n
    format_ok = validate_n8n_format(api_response)

    # Génération du rapport final
    generate_test_report(health_ok, api_response, format_ok)

if __name__ == "__main__":
    main()