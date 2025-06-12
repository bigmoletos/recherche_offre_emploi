#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal de l'Agent Python Standalone pour la recherche d'offres d'alternance.

Ce module constitue le point d'entrée principal de l'agent Python autonome.
Il orchestre les différents composants pour :
- Collecter des offres d'emploi depuis Pôle Emploi
- Analyser les offres avec l'IA Mistral
- Générer des rapports Excel détaillés
- Gérer les logs et la configuration

Le script supporte plusieurs modes d'exécution :
- Mode complet : scraping + analyse IA + rapport
- Mode scraping seul : collecte sans analyse IA
- Mode personnalisé : avec paramètres spécifiques

Fonctionnalités principales :
- Interface en ligne de commande intuitive
- Configuration via fichiers .env
- Logging avancé avec rotation
- Gestion d'erreurs robuste
- Validation des prérequis

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: 03/06/2025

Usage:
    python src/main_scraper.py
    python src/main_scraper.py --max-offres 20 --keywords "cybersécurité,alternance"
    python src/main_scraper.py --no-analysis --log-level DEBUG
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ajouter les répertoires nécessaires au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared" / "scripts"))

# Import du système de logging commun
try:
    from logger_config import get_logger
except ImportError:
    # Fallback si le module de logging n'est pas disponible
    def get_logger(name: str, **kwargs):
        """Fallback logger en cas d'import impossible."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        )
        return logging.getLogger(name)

# Import des modules locaux
from scraper_offres_reelles import JobScraper
from analyser_vraies_offres import JobAnalyzer

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure le système de logging pour l'application.

    Cette fonction initialise le logger principal en utilisant le système
    de logging centralisé du projet. Elle configure :
    - La rotation automatique des fichiers de log
    - Le formatage uniforme des messages
    - La sortie console avec couleurs
    - Le niveau de logging approprié

    Args:
        log_level (str): Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Logger configuré et prêt à utiliser

    Raises:
        ValueError: Si le niveau de logging est invalide
    """
    # Validation du niveau de logging
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level.upper() not in valid_levels:
        raise ValueError(f"Niveau de logging invalide: {log_level}. Utilisez: {', '.join(valid_levels)}")

    # Utilisation du système de logging centralisé
    logger = get_logger(
        name=__name__,
        log_level=log_level,
        log_file="main_scraper.log",
        console_output=True
    )

    logger.info(f"Système de logging initialisé - Niveau: {log_level}")
    logger.debug(f"Logger configuré avec fichier de log dans: {Path(__file__).parent.parent / 'logs'}")

    return logger


def load_config() -> Dict[str, Any]:
    """
    Charge la configuration depuis le fichier .env et les variables d'environnement.

    Cette fonction recherche et charge la configuration depuis :
    1. Le fichier .env local (priorité haute)
    2. Les variables d'environnement système (priorité basse)
    3. Les valeurs par défaut (fallback)

    La configuration inclut :
    - Clé API Mistral pour l'analyse IA
    - Paramètres de logging
    - Format de sortie des rapports
    - Limites de traitement

    Returns:
        Dict[str, Any]: Configuration chargée avec clés:
            - mistral_api_key: Clé API Mistral (obligatoire pour l'IA)
            - log_level: Niveau de logging
            - output_format: Format de sortie (excel, csv, json)
            - max_offres: Nombre maximum d'offres à traiter

    Note:
        Si le fichier .env n'existe pas, utilise .env.example comme référence
        et affiche des instructions pour la configuration.
    """
    from dotenv import load_dotenv

    # Déterminer les chemins des fichiers de configuration (ordre de priorité)
    project_root = Path(__file__).parent.parent.parent  # racine du projet recherche_offre_emploi
    config_dir = Path(__file__).parent.parent / "config"  # config local agent_python

    # Fichiers de configuration par ordre de priorité (local d'abord, puis global)
    config_files = [
        config_dir / ".env",          # 1. Configuration locale agent_python
        project_root / ".env",        # 2. Configuration globale du projet
        config_dir / ".env.example"   # 3. Template de référence
    ]

    # Charger la configuration (premier fichier trouvé)
    config_loaded = False
    for env_file in config_files:
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Configuration chargée depuis {env_file}")
            config_loaded = True
            break

    if not config_loaded:
        logger.warning("Aucun fichier de configuration trouvé")
        logger.info("Fichiers recherchés:")
        for env_file in config_files:
            logger.info(f"  - {env_file}")
        logger.info("Utilisation des variables d'environnement et valeurs par défaut")

    # Informations pour l'utilisateur
    if not (config_dir / ".env").exists() and (project_root / ".env").exists():
        logger.info("💡 Conseil: Créez agent_python/config/.env pour une configuration spécifique à cet agent")
    elif not any(f.exists() for f in config_files[:2]):
        logger.info("💡 Conseil: Créez .env à la racine du projet ou dans agent_python/config/")

    # Extraire la configuration avec valeurs par défaut
    config = {
        'mistral_api_key': os.getenv('MISTRAL_API_KEY'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'output_format': os.getenv('OUTPUT_FORMAT', 'excel'),
        'max_offres': int(os.getenv('MAX_OFFRES', 50))
    }

    # Validation et logging de la configuration
    logger.debug("Configuration chargée:")
    for key, value in config.items():
        if 'api_key' in key.lower() and value:
            # Masquer les clés API dans les logs
            masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            logger.debug(f"  {key}: {masked_value}")
        else:
            logger.debug(f"  {key}: {value}")

    # Avertissements sur la configuration
    if not config['mistral_api_key']:
        logger.warning("MISTRAL_API_KEY non configurée - l'analyse IA sera désactivée")

    return config

def validate_keywords(keywords: str) -> List[str]:
    """
    Valide et nettoie la liste des mots-clés de recherche.

    Args:
        keywords (str): Mots-clés séparés par des virgules

    Returns:
        List[str]: Liste des mots-clés nettoyés et validés

    Raises:
        ValueError: Si aucun mot-clé valide n'est fourni
    """
    if not keywords:
        raise ValueError("Au moins un mot-clé doit être fourni")

    # Nettoyer et filtrer les mots-clés
    cleaned_keywords = []
    for keyword in keywords.split(','):
        cleaned = keyword.strip()
        if cleaned and len(cleaned) >= 2:  # Mot-clé minimum 2 caractères
            cleaned_keywords.append(cleaned)

    if not cleaned_keywords:
        raise ValueError("Aucun mot-clé valide trouvé après nettoyage")

    logger.debug(f"Mots-clés validés: {cleaned_keywords}")
    return cleaned_keywords


def validate_configuration(config: Dict[str, Any], no_analysis: bool = False) -> bool:
    """
    Valide la configuration avant l'exécution.

    Args:
        config (Dict[str, Any]): Configuration à valider
        no_analysis (bool): True si l'analyse IA est désactivée

    Returns:
        bool: True si la configuration est valide

    Raises:
        ValueError: Si la configuration est invalide
    """
    logger.debug("Validation de la configuration...")

    # Vérification de la clé API Mistral si analyse activée
    if not no_analysis and not config.get('mistral_api_key'):
        logger.error("MISTRAL_API_KEY requise pour l'analyse IA")
        logger.info("Solutions possibles:")
        logger.info("1. Configurez MISTRAL_API_KEY dans config/.env")
        logger.info("2. Utilisez --no-analysis pour désactiver l'IA")
        return False

    # Vérification du format de sortie
    valid_formats = ['excel', 'csv', 'json']
    if config.get('output_format') not in valid_formats:
        logger.warning(f"Format de sortie invalide: {config.get('output_format')}")
        logger.info(f"Formats supportés: {', '.join(valid_formats)}")
        config['output_format'] = 'excel'  # Fallback

    # Vérification du nombre maximum d'offres
    max_offres = config.get('max_offres', 50)
    if not isinstance(max_offres, int) or max_offres <= 0:
        logger.warning(f"Nombre max d'offres invalide: {max_offres}")
        config['max_offres'] = 50  # Fallback
    elif max_offres > 200:
        logger.warning(f"Nombre max d'offres élevé: {max_offres} (recommandé: <= 200)")

    logger.info("Configuration validée avec succès")
    return True


def main() -> int:
    """
    Fonction principale du script.

    Cette fonction orchestre l'ensemble du processus :
    1. Parse les arguments de ligne de commande
    2. Configure le logging et charge la configuration
    3. Valide les paramètres d'entrée
    4. Exécute le scraping des offres
    5. Effectue l'analyse IA (si activée)
    6. Génère les rapports de sortie
    7. Affiche les statistiques finales

    Le processus est robuste avec gestion d'erreurs complète et
    logging détaillé à chaque étape.

    Returns:
        int: Code de sortie (0 = succès, 1 = erreur)

    Raises:
        SystemExit: En cas d'interruption utilisateur ou d'erreur critique
    """
    # Configuration de l'analyseur d'arguments avec descriptions détaillées
    parser = argparse.ArgumentParser(
        description="Agent Python - Recherche Offres Alternance Cybersécurité",
        epilog="""
Exemples d'utilisation:
  %(prog)s                                    # Exécution standard
  %(prog)s --max-offres 20                    # Limite à 20 offres
  %(prog)s --keywords "python,django"         # Mots-clés spécifiques
  %(prog)s --no-analysis --log-level DEBUG   # Scraping seul en mode debug
  %(prog)s --location "Paris" --max-offres 10 # Recherche localisée
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Arguments de contrôle du comportement
    parser.add_argument(
        '--max-offres',
        type=int,
        default=None,
        metavar='N',
        help="Nombre maximum d'offres à traiter (défaut: depuis config/.env, recommandé: <= 200)"
    )

    parser.add_argument(
        '--keywords',
        type=str,
        default="cybersécurité,alternance,sécurité informatique",
        metavar='MOTS',
        help="Mots-clés de recherche séparés par des virgules (défaut: cybersécurité,alternance,sécurité informatique)"
    )

    parser.add_argument(
        '--location',
        type=str,
        default="France",
        metavar='LIEU',
        help="Localisation de recherche (ex: Paris, Lyon, Île-de-France, France)"
    )

    # Arguments de configuration
    parser.add_argument(
        '--log-level',
        type=str,
        default="INFO",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Niveau de logging détaillé (défaut: INFO)"
    )

    parser.add_argument(
        '--no-analysis',
        action='store_true',
        help="Désactiver l'analyse IA Mistral (scraping seulement)"
    )

    parser.add_argument(
        '--output-format',
        type=str,
        choices=['excel', 'csv', 'json'],
        default=None,
        help="Format de sortie du rapport (défaut: depuis config/.env ou excel)"
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Mode test : valider la configuration sans exécuter"
    )

    args = parser.parse_args()

    # Configuration
    config = load_config()
    log_level = args.log_level or config['log_level']

    # Setup logging
    global logger
    logger = setup_logging(log_level)

    logger.info("🎯 Démarrage de l'Agent Python Standalone")
    logger.info(f"Configuration: {config}")

    try:
        # Validation de la configuration
        if not config['mistral_api_key'] and not args.no_analysis:
            logger.error("❌ MISTRAL_API_KEY non configurée !")
            logger.info("Exécution en mode scraping seulement (--no-analysis)")
            args.no_analysis = True

        # Paramètres de recherche
        keywords = [k.strip() for k in args.keywords.split(',')]
        max_offres = args.max_offres or config['max_offres']

        logger.info(f"🔍 Recherche avec mots-clés: {keywords}")
        logger.info(f"📊 Maximum d'offres: {max_offres}")
        logger.info(f"📍 Localisation: {args.location}")

        # Étape 1: Scraping des offres
        logger.info("\n🕷️ ÉTAPE 1: Scraping des offres...")
        scraper = JobScraper()

        offres = scraper.search_jobs(
            keywords=keywords,
            location=args.location,
            max_results=max_offres
        )

        logger.info(f"✅ {len(offres)} offres collectées")

        if not offres:
            logger.warning("⚠️ Aucune offre trouvée avec ces critères")
            return

        # Étape 2: Analyse IA (optionnelle)
        if not args.no_analysis:
            logger.info("\n🤖 ÉTAPE 2: Analyse IA avec Mistral...")
            analyzer = JobAnalyzer(api_key=config['mistral_api_key'])

            offres_analysees = analyzer.analyze_jobs(offres)
            logger.info(f"✅ {len(offres_analysees)} offres analysées par IA")
        else:
            logger.info("\n⏭️ ÉTAPE 2: Analyse IA ignorée (--no-analysis)")
            offres_analysees = offres

        # Étape 3: Génération du rapport
        logger.info("\n📄 ÉTAPE 3: Génération du rapport...")

        output_dir = Path(__file__).parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True)

        if config['output_format'] == 'excel':
            # Import ici pour éviter les dépendances si pas utilisé
            from test_excel_generation import generate_excel_report

            output_file = output_dir / f"offres_alternance_{len(offres_analysees)}_resultats.xlsx"
            generate_excel_report(offres_analysees, str(output_file))

            logger.info(f"✅ Rapport Excel généré: {output_file}")

        # Statistiques finales
        logger.info("\n📊 RÉSULTATS FINAUX:")
        logger.info(f"   • Offres collectées: {len(offres)}")
        logger.info(f"   • Offres analysées: {len(offres_analysees)}")

        if not args.no_analysis:
            # Calcul des scores moyens
            scores = [o.get('score_ia', 0) for o in offres_analysees if o.get('score_ia')]
            if scores:
                score_moyen = sum(scores) / len(scores)
                logger.info(f"   • Score IA moyen: {score_moyen:.2f}")

        logger.info(f"   • Fichier de sortie: {output_file if 'output_file' in locals() else 'N/A'}")
        logger.info("\n🎉 Traitement terminé avec succès !")

    except KeyboardInterrupt:
        logger.info("\n⏹️ Traitement interrompu par l'utilisateur")

    except Exception as e:
        logger.error(f"\n❌ Erreur durant l'exécution: {e}")
        logger.debug("Détails de l'erreur:", exc_info=True)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())