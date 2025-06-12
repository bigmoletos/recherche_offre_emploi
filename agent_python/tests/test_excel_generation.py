#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test - Génération Excel pour Agent Alternance
Teste la création d'un fichier Excel identique à celui de n8n
"""

import pandas as pd
import logging
from datetime import datetime
import os
from typing import Dict, List, Any


def setup_logging() -> None:
    """Configuration du système de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('excel_generation.log'),
            logging.StreamHandler()
        ]
    )


def generate_test_data() -> List[Dict[str, Any]]:
    """
    Génère les données de test identiques à celles du workflow n8n.

    Returns:
        List[Dict]: Liste des offres d'alternance avec métadonnées
    """
    offers = [
        {
            "title": "Alternance Cybersécurité - Analyste SOC H/F",
            "company": "SecureTech Solutions",
            "location": "Paris (75)",
            "duration": "24 mois",
            "start_date": "septembre 2025",
            "description": "Recherchons alternant pour poste d'analyste SOC. Formation cybersécurité Master 1/2. Missions: monitoring sécurité, analyse incidents, reporting.",
            "url": "https://pole-emploi.fr/candidat/offres/recherche/detail/123456",
            "scraper_source": "pole_emploi",
            "ai_response": "VALIDE",
            "is_valid": True,
            "status": "✅ VALIDÉE",
            "processed_at": datetime.now().isoformat()
        },
        {
            "title": "Formation Cybersécurité - École Supérieure",
            "company": "École Supérieure Informatique",
            "location": "Lyon (69)",
            "duration": "3 ans",
            "start_date": "septembre 2025",
            "description": "Formation diplômante en cybersécurité. Programme complet théorique avec stages en entreprise.",
            "url": "https://indeed.fr/formation/cybersecurite-123",
            "scraper_source": "indeed",
            "ai_response": "INVALIDE: Formation d'école",
            "is_valid": False,
            "status": "❌ REJETÉE",
            "processed_at": datetime.now().isoformat()
        },
        {
            "title": "Alternance DevSecOps - Infrastructure Sécurisée",
            "company": "TechCorp Enterprise",
            "location": "Marseille (13)",
            "duration": "18 mois",
            "start_date": "septembre 2025",
            "description": "Poste d'alternant DevSecOps. Mission: automatisation sécurité, CI/CD sécurisé, audit infrastructure.",
            "url": "https://apec.fr/candidat/recherche-emploi/detail/123789",
            "scraper_source": "apec",
            "ai_response": "VALIDE",
            "is_valid": True,
            "status": "✅ VALIDÉE",
            "processed_at": datetime.now().isoformat()
        },
        {
            "title": "Alternance Pentester Junior - Audit Sécurité",
            "company": "CyberSec Consulting",
            "location": "Toulouse (31)",
            "duration": "24 mois",
            "start_date": "octobre 2025",
            "description": "Alternance pentesting et audit sécurité. Formation sur tests d'intrusion, analyse vulnérabilités.",
            "url": "https://linkedin.com/jobs/view/987654321",
            "scraper_source": "linkedin",
            "ai_response": "VALIDE",
            "is_valid": True,
            "status": "✅ VALIDÉE",
            "processed_at": datetime.now().isoformat()
        },
        {
            "title": "Alternance RSSI Junior - Gouvernance Sécurité",
            "company": "Digital Security Corp",
            "location": "Nantes (44)",
            "duration": "24 mois",
            "start_date": "janvier 2026",
            "description": "Alternance en gouvernance sécurité. Missions: politique sécurité, conformité RGPD, formation utilisateurs.",
            "url": "https://monster.fr/emploi/alternance-rssi-123456",
            "scraper_source": "monster",
            "ai_response": "VALIDE",
            "is_valid": True,
            "status": "✅ VALIDÉE",
            "processed_at": datetime.now().isoformat()
        }
    ]

    logging.info(f"📋 Génération de {len(offers)} offres pour Excel")
    logging.info(f"✅ Offres validées: {len([o for o in offers if o['is_valid']])}")
    logging.info(f"❌ Offres rejetées: {len([o for o in offers if not o['is_valid']])}")

    return offers


def filter_and_format_data(offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtre les offres validées et les formate pour Excel.

    Args:
        offers: Liste des offres brutes

    Returns:
        List[Dict]: Offres formatées pour Excel
    """
    valid_offers = [offer for offer in offers if offer.get('is_valid', False)]

    excel_data = []
    for idx, offer in enumerate(valid_offers, 1):
        excel_row = {
            'N°': idx,
            'Titre': offer.get('title', 'N/A'),
            'Entreprise': offer.get('company', 'N/A'),
            'Localisation': offer.get('location', 'N/A'),
            'Durée': offer.get('duration', 'N/A'),
            'Date de début': offer.get('start_date', 'N/A'),
            'Site source': offer.get('scraper_source', 'N/A'),
            'Lien direct': offer.get('url', 'N/A'),
            'Validation IA': offer.get('ai_response', 'VALIDE'),
            'Statut': offer.get('status', '✅ VALIDÉE'),
            'Date traitement': datetime.fromisoformat(offer['processed_at']).strftime('%d/%m/%Y'),
            'Description': (offer.get('description', '')[:200] + '...' if len(offer.get('description', '')) > 200 else offer.get('description', ''))
        }
        excel_data.append(excel_row)
        logging.info(f"📊 Formatage Excel: {excel_row['Titre']}")

    return excel_data


def generate_statistics(excel_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Génère les statistiques pour l'onglet séparé.

    Args:
        excel_data: Données des offres validées

    Returns:
        List[Dict]: Statistiques formatées
    """
    sites_scrapes = list(set([offer['Site source'] for offer in excel_data]))

    stats_data = [
        {'Métrique': 'Total offres validées', 'Valeur': len(excel_data)},
        {'Métrique': 'Sites scrapés', 'Valeur': len(sites_scrapes)},
        {'Métrique': 'Moteur IA', 'Valeur': 'Mistral Large'},
        {'Métrique': 'Date génération', 'Valeur': datetime.now().strftime('%d/%m/%Y')},
        {'Métrique': 'Heure génération', 'Valeur': datetime.now().strftime('%H:%M:%S')}
    ]

    return stats_data


def generate_locations_data(excel_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Génère les données de localisation pour l'onglet séparé.

    Args:
        excel_data: Données des offres validées

    Returns:
        List[Dict]: Données de localisation formatées
    """
    # Extraction des villes (avant la parenthèse du département)
    locations = {}
    for offer in excel_data:
        ville = offer['Localisation'].split('(')[0].strip()
        locations[ville] = locations.get(ville, 0) + 1

    # Tri par nombre d'offres décroissant
    sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)

    total_offres = len(excel_data)
    locations_data = []
    for ville, count in sorted_locations:
        locations_data.append({
            'Ville': ville,
            'Nombre d\'offres': count,
            'Pourcentage': f"{round((count / total_offres) * 100)}%"
        })

    return locations_data


def create_excel_file(excel_data: List[Dict[str, Any]], stats_data: List[Dict[str, Any]],
                     locations_data: List[Dict[str, Any]]) -> str:
    """
    Crée le fichier Excel avec les trois onglets.

    Args:
        excel_data: Données des offres
        stats_data: Données statistiques
        locations_data: Données de localisation

    Returns:
        str: Nom du fichier créé
    """
    # Génération du nom de fichier avec timestamp
    timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    filename = f'alternance_cybersecurite_{timestamp}.xlsx'

    logging.info(f"\n🎯 ====== GÉNÉRATION FICHIER EXCEL ====== 🎯")
    logging.info(f"📅 Date: {datetime.now().strftime('%d/%m/%Y')} à {datetime.now().strftime('%H:%M:%S')}")
    logging.info(f"📄 Fichier: {filename}")
    logging.info(f"✅ Total offres: {len(excel_data)}")
    logging.info(f"🤖 Moteur IA: Mistral Large")

    try:
        # Création du writer Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Onglet 1: Offres d'alternance
            df_offres = pd.DataFrame(excel_data)
            df_offres.to_excel(writer, sheet_name='Offres_Alternance', index=False)

            # Onglet 2: Statistiques
            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='Statistiques', index=False)

            # Onglet 3: Localisations
            df_locations = pd.DataFrame(locations_data)
            df_locations.to_excel(writer, sheet_name='Localisations', index=False)

            logging.info(f"📑 Onglet 1: Offres_Alternance ({len(excel_data)} lignes)")
            logging.info(f"📊 Onglet 2: Statistiques ({len(stats_data)} métriques)")
            logging.info(f"🏆 Onglet 3: Localisations ({len(locations_data)} villes)")

        logging.info(f"\n✅ ====== FICHIER EXCEL GÉNÉRÉ ====== ✅")
        logging.info(f"📄 Nom du fichier: {filename}")
        logging.info(f"📊 Taille du fichier: {os.path.getsize(filename)} bytes")
        logging.info(f"💾 Emplacement: {os.path.abspath(filename)}")
        logging.info(f"✅ ====== SUCCÈS ====== ✅")

        return filename

    except Exception as e:
        logging.error(f"❌ Erreur lors de la création du fichier Excel: {e}")
        raise


def main():
    """Fonction principale d'exécution du script."""
    try:
        # Configuration du logging
        setup_logging()

        logging.info("🚀 Démarrage du test de génération Excel")

        # Génération des données de test
        offers = generate_test_data()

        # Filtrage et formatage
        excel_data = filter_and_format_data(offers)

        # Génération des statistiques
        stats_data = generate_statistics(excel_data)

        # Génération des données de localisation
        locations_data = generate_locations_data(excel_data)

        # Création du fichier Excel
        filename = create_excel_file(excel_data, stats_data, locations_data)

        # Affichage du résumé
        print(f"\n🎯 RÉSUMÉ DE L'EXÉCUTION:")
        print(f"✅ Fichier Excel créé: {filename}")
        print(f"📊 Total offres validées: {len(excel_data)}")
        print(f"🏆 Villes représentées: {len(locations_data)}")
        print(f"📍 Emplacement: {os.path.abspath(filename)}")
        print(f"\n💡 INSTRUCTIONS:")
        print(f"1. Ouvrez le fichier Excel: {filename}")
        print(f"2. Consultez les 3 onglets")
        print(f"3. Comparez avec le fichier généré par n8n")

    except Exception as e:
        logging.error(f"❌ Erreur fatale: {e}")
        print(f"❌ Erreur lors de l'exécution: {e}")


if __name__ == "__main__":
    main()