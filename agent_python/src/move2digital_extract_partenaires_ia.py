#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracteur de Partenaires IA Move2Digital - Version Corrigée.

Ce module permet d'extraire automatiquement la liste des partenaires et solutions IA
référencés dans le catalogue Move2Digital de la région SUD. Il utilise l'API Airtable
pour récupérer les données structurées des entreprises et leurs spécialisations.

Version corrigée avec le mapping exact des champs Move2Digital :
- "Nom de l'entreprise" : Nom commercial
- "Descriptif" : Description des activités
- "Catégorie d'usage" : Liste des cas d'usage
- "Catégorie technologique" : Liste des technologies IA
- "Secteur d'activité" : Liste des secteurs cibles

Auteur: desmedt.franck@iaproject.fr
Version: 1.1 (Corrigée)
Date: 03/06/2025
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import logging
import os
import sys
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import time
import random
from urllib.parse import urljoin, urlparse

# Intégration du système de logging centralisé
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts"))

try:
    from logger_config import get_logger
    logger = get_logger(__name__, log_file="move2digital_extract.log")
except ImportError:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        handlers=[
            logging.FileHandler(
                f'move2digital_extract_{datetime.now().strftime("%Y%m%d")}.log'
            ),
            logging.StreamHandler()
        ])
    logger = logging.getLogger(__name__)
    logger.warning(
        "Module logger_config non disponible, utilisation du logging standard")


@dataclass
class CompanyInfo:
    """
    Structure de données représentant une entreprise partenaire IA.
    """
    name: str
    description: str = ""
    category: str = ""
    sector: str = ""
    location: str = ""
    website: str = ""
    contact_info: Dict[str, Any] = field(default_factory=dict)
    technologies: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    creation_date: str = ""
    last_update: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour sérialisation JSON."""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'sector': self.sector,
            'location': self.location,
            'website': self.website,
            'contact_info': self.contact_info,
            'technologies': self.technologies,
            'services': self.services,
            'creation_date': self.creation_date,
            'last_update': self.last_update
        }


class APIKeyExtractor:
    """Extracteur de clés API depuis les pages web Move2Digital."""

    def __init__(
        self,
        target_url:
        str = "https://move2digital.eu/nos-services/catalogue-des-acteurs-ia/"
    ):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language':
            'fr-FR,fr;q=0.9,en;q=0.8',
        })

        self.extraction_patterns = [
            r'const\s+API_KEY\s*=\s*["\']([^"\']+)["\']',
            r'API_KEY\s*[:=]\s*["\']([^"\']+)["\']',
            r'apiKey\s*[:=]\s*["\']([^"\']+)["\']',
            r'Bearer\s+([A-Za-z0-9_\-\.]+)',
        ]

    def extract_api_key(self, max_retries: int = 3) -> Optional[str]:
        """Extrait la clé API depuis la page web Move2Digital."""
        logger.info(f"🔍 Extraction de la clé API depuis {self.target_url}")

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    time.sleep(random.uniform(2, 5))

                response = self.session.get(self.target_url, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # Recherche dans les scripts inline
                scripts = soup.find_all('script', src=False)
                for script in scripts:
                    if script.string:
                        for pattern in self.extraction_patterns:
                            matches = re.findall(pattern, script.string,
                                                 re.IGNORECASE)
                            if matches:
                                for match in matches:
                                    if self._is_valid_api_key(match):
                                        logger.info(
                                            f"✅ Clé API trouvée: {match[:10]}..."
                                        )
                                        return match

                logger.warning(
                    f"Tentative {attempt + 1} échouée - Aucune clé API trouvée"
                )

            except Exception as e:
                logger.error(f"Erreur tentative {attempt + 1}: {e}")

        logger.error(
            "❌ Impossible d'extraire la clé API après toutes les tentatives")
        return None

    def _is_valid_api_key(self, key: str) -> bool:
        """Valide qu'une chaîne ressemble à une clé API Airtable valide."""
        if not key or len(key) < 10:
            return False

        airtable_patterns = [
            r'^key[A-Za-z0-9]{14}$', r'^pat[A-Za-z0-9._-]+$',
            r'^[A-Za-z0-9._-]{17,}$'
        ]

        for pattern in airtable_patterns:
            if re.match(pattern, key):
                return True

        invalid_values = ['undefined', 'null', 'none', 'test', 'example']
        if key.lower() in invalid_values:
            return False

        return len(key) >= 15 and re.match(r'^[A-Za-z0-9._-]+$', key)


class Move2DigitalScraper:
    """Scraper principal pour l'extraction des partenaires IA Move2Digital."""

    def __init__(self):
        logger.info("Initialisation du scraper Move2Digital")
        self.api_extractor = APIKeyExtractor()
        self.base_api_url = "https://api.airtable.com/v0/app7913ETHqajipme/solutionsIA"
        self.companies_data = []
        self.extraction_stats = {
            'total_extracted': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'api_calls_made': 0,
            'extraction_duration': 0
        }

        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Move2Digital-Extractor/1.1'
        })

    def extract_all_partners(self, page_size: int = 100) -> List[CompanyInfo]:
        """Extrait tous les partenaires IA du catalogue Move2Digital."""
        start_time = time.time()
        logger.info("🚀 Début de l'extraction complète des partenaires IA")

        try:
            # Étape 1: Extraction de la clé API
            logger.info("📡 Étape 1: Extraction de la clé API...")
            api_key = self.api_extractor.extract_api_key()

            if not api_key:
                raise RuntimeError(
                    "Impossible d'extraire la clé API Move2Digital")

            logger.info(f"✅ Clé API récupérée: {api_key[:10]}...")
            self.session.headers['Authorization'] = f'Bearer {api_key}'

            # Étape 2: Extraction des données via l'API
            logger.info("📊 Étape 2: Extraction des données Airtable...")
            raw_data = self._fetch_all_records(page_size)
            logger.info(f"✅ {len(raw_data)} enregistrements récupérés")

            # Étape 3: Traitement et normalisation
            logger.info("🔄 Étape 3: Traitement des données...")
            self.companies_data = self._process_raw_data(raw_data)

            # Statistiques finales
            self.extraction_stats['total_extracted'] = len(raw_data)
            self.extraction_stats['successful_extractions'] = len(
                self.companies_data)
            self.extraction_stats['failed_extractions'] = len(raw_data) - len(
                self.companies_data)
            self.extraction_stats['extraction_duration'] = time.time(
            ) - start_time

            logger.info(
                f"✅ Extraction terminée: {len(self.companies_data)} entreprises traitées"
            )
            logger.info(
                f"⏱️ Durée totale: {self.extraction_stats['extraction_duration']:.2f}s"
            )

            return self.companies_data

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction: {e}")
            raise

    def _fetch_all_records(self, page_size: int) -> List[Dict[str, Any]]:
        """Récupère tous les enregistrements via pagination de l'API Airtable."""
        all_records = []
        offset = None
        page_num = 1

        while True:
            logger.debug(f"Récupération page {page_num} (offset: {offset})")

            params = {'pageSize': min(page_size, 100)}
            if offset:
                params['offset'] = offset

            try:
                response = self.session.get(self.base_api_url,
                                            params=params,
                                            timeout=30)
                response.raise_for_status()

                data = response.json()
                self.extraction_stats['api_calls_made'] += 1

                records = data.get('records', [])
                all_records.extend(records)

                logger.debug(
                    f"Page {page_num}: {len(records)} enregistrements récupérés"
                )

                offset = data.get('offset')
                if not offset:
                    break

                page_num += 1
                time.sleep(0.2)

            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur API page {page_num}: {e}")
                raise

        logger.info(
            f"📦 Total: {len(all_records)} enregistrements récupérés en {page_num} pages"
        )
        return all_records

    def _process_raw_data(self,
                          raw_data: List[Dict[str, Any]]) -> List[CompanyInfo]:
        """Traite et normalise les données brutes de l'API Airtable."""
        processed_companies = []

        for record in raw_data:
            try:
                company = self._create_company_from_record(record)
                if company:
                    processed_companies.append(company)
                    logger.debug(f"Entreprise traitée: {company.name}")
                else:
                    logger.warning(
                        f"Échec traitement enregistrement: {record.get('id', 'ID_INCONNU')}"
                    )

            except Exception as e:
                logger.error(
                    f"Erreur traitement enregistrement {record.get('id', 'ID_INCONNU')}: {e}"
                )

        logger.info(
            f"🔄 Traitement terminé: {len(processed_companies)}/{len(raw_data)} entreprises valides"
        )
        return processed_companies

    def _create_company_from_record(
            self, record: Dict[str, Any]) -> Optional[CompanyInfo]:
        """
        Crée un objet CompanyInfo à partir d'un enregistrement Airtable Move2Digital.

        Mapping des champs Move2Digital :
        - "Nom de l'entreprise" -> name
        - "Descriptif" -> description
        - "Catégorie d'usage" -> services (liste)
        - "Catégorie technologique" -> technologies (liste) + category
        - "Secteur d'activité" -> sector (liste)
        """
        try:
            fields = record.get('fields', {})

            # Debug: afficher la structure des champs disponibles
            if logger.level <= 10:  # DEBUG level
                logger.debug(f"Champs disponibles: {list(fields.keys())}")

            # Extraction du nom d'entreprise (champ exact Move2Digital)
            name = fields.get("Nom de l'entreprise", "").strip()

            if not name:
                logger.warning(
                    f"Enregistrement sans nom d'entreprise ignoré - ID: {record.get('id', 'INCONNU')}"
                )
                return None

            # Extraction de la description
            description = fields.get("Descriptif", "").strip()

            # Fonction helper pour traiter les listes Airtable
            def process_airtable_list(field_data):
                if isinstance(field_data, list):
                    return [
                        item.strip() for item in field_data
                        if item and str(item).strip()
                    ]
                elif isinstance(field_data, str):
                    return [field_data.strip()] if field_data.strip() else []
                else:
                    return []

            # Traitement des catégories Move2Digital
            usage_categories = process_airtable_list(
                fields.get("Catégorie d'usage", []))
            tech_categories = process_airtable_list(
                fields.get("Catégorie technologique", []))
            activity_sectors = process_airtable_list(
                fields.get("Secteur d'activité", []))

            # Combinaison des catégories pour le champ category
            all_categories = tech_categories + usage_categories
            category = ", ".join(all_categories) if all_categories else ""

            # Secteurs d'activité
            sector = ", ".join(activity_sectors) if activity_sectors else ""

            # Création de l'objet CompanyInfo
            company = CompanyInfo(
                name=name,
                description=description,
                category=category,
                sector=sector,
                location="",  # Pas de localisation dans les données Move2Digital
                website="",  # Pas de site web dans les données Move2Digital
                creation_date=record.get('createdTime', ''),
                last_update=record.get('createdTime', ''))

            # Utiliser les catégories technologiques comme technologies
            company.technologies = tech_categories

            # Utiliser les catégories d'usage comme services
            company.services = usage_categories

            logger.debug(f"✅ Entreprise créée: {company.name}")
            logger.debug(f"   - Description: {len(description)} caractères")
            logger.debug(f"   - Technologies: {len(tech_categories)} items")
            logger.debug(f"   - Services: {len(usage_categories)} items")
            logger.debug(f"   - Secteurs: {len(activity_sectors)} items")

            return company

        except Exception as e:
            logger.error(f"Erreur création CompanyInfo: {e}")
            logger.debug(f"Données de l'enregistrement: {record}")
            return None

    def export_to_json(self, filename: str = None) -> str:
        """Exporte les données des entreprises au format JSON."""
        if not self.companies_data:
            logger.warning("Aucune donnée d'entreprise à exporter")
            return None

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"partenaires_ia_move2digital_{timestamp}.json"

        # Création du répertoire de sortie
        output_dir = Path(__file__).parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        full_path = output_dir / filename

        try:
            # Préparer les données pour l'export
            export_data = {
                'metadata': {
                    'source': 'Move2Digital - Catalogue des acteurs IA',
                    'extraction_date': datetime.now().isoformat(),
                    'total_companies': len(self.companies_data),
                    'extraction_stats': self.extraction_stats
                },
                'companies':
                [company.to_dict() for company in self.companies_data]
            }

            # Sauvegarder le fichier JSON avec formatage lisible
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(export_data,
                          f,
                          indent=2,
                          ensure_ascii=False,
                          default=str)

            logger.info(f"✅ Données exportées vers: {full_path}")
            logger.info(
                f"📊 {len(self.companies_data)} entreprises sauvegardées")

            # Afficher un résumé des catégories
            self._log_export_summary()

            return str(full_path)

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'export JSON: {e}")
            raise

    def _log_export_summary(self):
        """Affiche un résumé des données exportées."""
        if not self.companies_data:
            return

        # Statistiques par catégorie
        technologies = {}
        services = {}
        sectors = {}

        for company in self.companies_data:
            # Technologies
            for tech in company.technologies:
                technologies[tech] = technologies.get(tech, 0) + 1

            # Services
            for service in company.services:
                services[service] = services.get(service, 0) + 1

            # Secteurs
            for sector in company.sector.split(', ') if company.sector else []:
                sectors[sector] = sectors.get(sector, 0) + 1

        logger.info("\n📈 RÉSUMÉ DES DONNÉES EXPORTÉES:")
        logger.info(f"   📁 Total entreprises: {len(self.companies_data)}")

        # Top 5 technologies
        if technologies:
            top_tech = sorted(technologies.items(),
                              key=lambda x: x[1],
                              reverse=True)[:5]
            logger.info(
                f"   🔧 Top technologies: {', '.join([f'{tech} ({nb})' for tech, nb in top_tech])}"
            )

        # Top 5 services
        if services:
            top_services = sorted(services.items(),
                                  key=lambda x: x[1],
                                  reverse=True)[:5]
            logger.info(
                f"   💼 Top services: {', '.join([f'{service} ({nb})' for service, nb in top_services])}"
            )

        # Top 5 secteurs
        if sectors:
            top_sectors = sorted(sectors.items(),
                                 key=lambda x: x[1],
                                 reverse=True)[:5]
            logger.info(
                f"   🏭 Top secteurs: {', '.join([f'{sector} ({nb})' for sector, nb in top_sectors])}"
            )


def main() -> int:
    """Fonction principale du script."""
    parser = argparse.ArgumentParser(
        description=
        "Extracteur de partenaires IA Move2Digital (Version Corrigée)")

    parser.add_argument('--output',
                        '-o',
                        type=str,
                        help='Nom du fichier JSON de sortie')
    parser.add_argument('--page-size',
                        type=int,
                        default=100,
                        help='Taille des pages API')
    parser.add_argument('--verbose',
                        '-v',
                        action='store_true',
                        help='Mode verbose')
    parser.add_argument('--log-level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='INFO')
    parser.add_argument('--dry-run', action='store_true', help='Mode test')

    args = parser.parse_args()

    # Configuration du logging
    if hasattr(logger, 'setLevel'):
        logger.setLevel(getattr(logging, args.log_level))

    try:
        logger.info(
            "🚀 Démarrage de l'extracteur Move2Digital (Version Corrigée)")

        if args.dry_run:
            logger.info("🧪 Mode test - validation de la configuration")
            extractor = APIKeyExtractor()
            api_key = extractor.extract_api_key()
            if api_key:
                logger.info(
                    f"✅ Test réussi - Clé API récupérée: {api_key[:10]}...")
                return 0
            else:
                logger.error(
                    "❌ Test échoué - Impossible de récupérer la clé API")
                return 1

        # Création et exécution du scraper
        scraper = Move2DigitalScraper()
        companies = scraper.extract_all_partners(page_size=args.page_size)

        if not companies:
            logger.warning("⚠️ Aucune entreprise partenaire trouvée")
            return 1

        # Export des données
        output_file = scraper.export_to_json(args.output)

        if output_file:
            logger.info(f"✅ Extraction terminée avec succès")
            logger.info(f"📄 Fichier généré: {output_file}")
            return 0
        else:
            logger.error("❌ Erreur lors de l'export des données")
            return 1

    except KeyboardInterrupt:
        logger.warning("⚠️ Extraction interrompue par l'utilisateur")
        return 1
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        if args.verbose:
            logger.exception("Détails de l'erreur:")
        return 1


if __name__ == "__main__":
    exit(main())
