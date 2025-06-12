#!/usr/bin/env python3
"""
Test de la structure des données de l'API scraper
"""

import requests
import json

def test_api_structure():
    """Test la structure des données retournées par l'API"""

    url = "http://localhost:9555/scrape-offres"
    data = {
        "termes": ["alternance cybersécurité"],
        "max_offres": 2,
        "sources": ["pole_emploi"]
    }

    print("🔍 Test de la structure API...")
    print(f"URL: {url}")
    print(f"Données envoyées: {json.dumps(data, indent=2)}")
    print("=" * 50)

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()

        result = response.json()

        print("✅ Réponse reçue avec succès")
        print("📊 Structure complète:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        print("\n" + "=" * 50)
        print("🔍 Analyse de la structure:")
        print(f"Type racine: {type(result)}")
        print(f"Clés niveau 1: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")

        # Test des chemins possibles pour les offres
        chemins_test = [
            ("results.offres", result.get("results", {}).get("offres")),
            ("offres", result.get("offres")),
            ("data.offres", result.get("data", {}).get("offres")),
            ("response.offres", result.get("response", {}).get("offres"))
        ]

        print("\n📋 Test des chemins pour les offres:")
        for nom_chemin, valeur in chemins_test:
            if valeur is not None:
                if isinstance(valeur, list):
                    print(f"✅ {nom_chemin}: {len(valeur)} offres trouvées")
                    if valeur:
                        premiere_offre = valeur[0]
                        print(f"   Première offre - Titre: {premiere_offre.get('title', 'MANQUANT')}")
                        print(f"   Première offre - Entreprise: {premiere_offre.get('company', 'MANQUANT')}")
                        print(f"   Première offre - Lieu: {premiere_offre.get('location', 'MANQUANT')}")
                else:
                    print(f"⚠️ {nom_chemin}: trouvé mais pas une liste (type: {type(valeur)})")
            else:
                print(f"❌ {nom_chemin}: non trouvé")

        print("\n" + "=" * 50)
        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la requête: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erreur lors du décodage JSON: {e}")
        return None

if __name__ == "__main__":
    test_api_structure()