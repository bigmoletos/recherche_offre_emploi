#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Scraper pour n8n - Module d'Interface REST.

Ce module fournit une API Flask pour exposer les fonctionnalités de scraping
d'offres d'alternance à n8n et autres systèmes d'orchestration.

Fonctionnalités principales :
- API REST avec endpoints sécurisés pour scraping
- Intégration complète avec le système de logging commun
- Configuration hybride avec .env locaux et globaux
- Gestion d'erreurs robuste avec réponses JSON standardisées
- Support CORS pour intégration n8n/frontend
- Endpoints de monitoring et de santé
- Documentation API automatique via docstrings

Architecture :
- Flask comme serveur web léger
- ScraperOffresReelles pour la collecte de données
- Système de logging centralisé avec rotation
- Configuration via variables d'environnement
- Réponses JSON structurées pour n8n

Usage :
    python api/api_scraper_pour_n8n.py              # Démarrage standard sur port 5555
    python api/api_scraper_pour_n8n.py --port 3000  # Port personnalisé
    curl http://localhost:5555/health                # Test de santé

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: 03/06/2025
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Ajouter le module de logging commun
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "shared" / "scripts"))
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "agent_python" / "src"))

try:
    from logger_config import get_logger, set_global_log_level
    logger = get_logger(__name__, log_file="api_scraper_n8n.log")
except ImportError:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')
    logger = logging.getLogger(__name__)
    logger.warning(
        "Module logger_config non disponible, utilisation du logging standard")

# Import des modules de scraping
try:
    from scraper_offres_reelles import ScraperOffresReelles
    logger.info("Module ScraperOffresReelles importé avec succès")
except ImportError as e:
    logger.error(f"Impossible d'importer ScraperOffresReelles: {e}")
    logger.info("Fonctionnement en mode dégradé avec données de test")
    ScraperOffresReelles = None


def load_config() -> Dict[str, Any]:
    """
    Charge la configuration selon l'architecture hybride.

    Cette fonction implémente l'ordre de priorité des configurations :
    1. Configuration locale agent_n8n/config/.env (priorité haute)
    2. Configuration globale .env à la racine (priorité basse)
    3. Variables d'environnement système (fallback)
    4. Valeurs par défaut (dernier recours)

    Returns:
        Dict[str, Any]: Configuration chargée avec clés:
            - mistral_api_key: Clé API pour l'IA (optionnelle pour l'API)
            - log_level: Niveau de logging
            - api_port: Port d'écoute de l'API
            - api_host: Host d'écoute
            - api_debug: Mode debug Flask
            - max_offres_default: Nombre max d'offres par défaut
    """
    from dotenv import load_dotenv

    # Déterminer les chemins des fichiers de configuration (ordre de priorité)
    project_root = Path(__file__).parent.parent.parent  # racine du projet
    config_dir = Path(
        __file__).parent.parent / "config"  # config local agent_n8n

    # Fichiers de configuration par ordre de priorité (local d'abord, puis global)
    config_files = [
        config_dir / ".env",  # 1. Configuration locale agent_n8n
        project_root / ".env",  # 2. Configuration globale du projet
        config_dir / ".env.example"  # 3. Template de référence
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
        logger.info(
            "Utilisation des variables d'environnement et valeurs par défaut")

    # Extraire la configuration avec valeurs par défaut
    config = {
        'mistral_api_key': os.getenv('MISTRAL_API_KEY'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'api_port': int(os.getenv('API_PORT', 5555)),
        'api_host': os.getenv('API_HOST', '127.0.0.1'),
        'api_debug': os.getenv('API_DEBUG', 'true').lower() == 'true',
        'max_offres_default': int(os.getenv('MAX_OFFRES_DEFAULT', 10)),
        'cors_enabled': os.getenv('CORS_ENABLED', 'true').lower() == 'true',
        'api_secret_key': os.getenv('API_SECRET_KEY'),
        'rate_limit': int(os.getenv('API_RATE_LIMIT', 100))
    }

    # Validation et logging de la configuration
    logger.debug("Configuration API chargée:")
    for key, value in config.items():
        if 'api_key' in key.lower() or 'secret' in key.lower():
            if value:
                masked_value = f"{value[:8]}...{value[-4:]}" if len(
                    str(value)) > 12 else "***"
                logger.debug(f"  {key}: {masked_value}")
            else:
                logger.debug(f"  {key}: Non configuré")
        else:
            logger.debug(f"  {key}: {value}")

    # Avertissements sur la configuration
    if not config['mistral_api_key']:
        logger.info(
            "MISTRAL_API_KEY non configurée - l'analyse IA ne sera pas disponible"
        )

    if not config['api_secret_key']:
        logger.warning("API_SECRET_KEY non configurée - API non sécurisée")

    return config


class ScraperAPI:
    """
    Classe principale de l'API Flask pour le scraping d'offres.

    Cette classe encapsule toute la logique de l'API REST, incluant
    la configuration, les routes, la gestion d'erreurs et le logging.

    Attributes:
        app (Flask): Instance de l'application Flask
        config (Dict): Configuration chargée
        scraper (ScraperOffresReelles): Instance du scraper
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialise l'API avec la configuration fournie.

        Args:
            config: Configuration chargée via load_config()
        """
        self.config = config
        self.app = Flask(__name__)

        # Configuration CORS si activée
        if config['cors_enabled']:
            CORS(self.app)
            logger.info("CORS activé pour intégration n8n/frontend")

        # Configuration Flask
        self.app.config['SECRET_KEY'] = config.get('api_secret_key',
                                                   'dev-key-change-me')
        self.app.config['DEBUG'] = config['api_debug']

        # Initialiser le scraper si disponible
        if ScraperOffresReelles:
            try:
                self.scraper = ScraperOffresReelles()
                logger.info("ScraperOffresReelles initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur initialisation scraper: {e}")
                self.scraper = None
        else:
            self.scraper = None
            logger.warning("Scraper non disponible - mode test seulement")

        # Enregistrer les routes
        self._register_routes()

        logger.info("API Scraper pour n8n initialisée")

    def _register_routes(self):
        """
        Enregistre toutes les routes de l'API.
        """
        # Route de santé
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """
            Endpoint de vérification de santé de l'API.

            Returns:
                JSON: Statut de santé avec informations système
            """
            logger.debug("Vérification de santé demandée")

            health_status = {
                "status":
                "healthy",
                "timestamp":
                datetime.now().isoformat(),
                "service":
                "API Scraper Offres pour n8n",
                "version":
                "1.0",
                "scraper_available":
                self.scraper is not None,
                "endpoints": [
                    "/health", "/scrape-offres", "/scrape-pole-emploi",
                    "/test-offres", "/config"
                ]
            }

            return jsonify(health_status)

        # Route principale de scraping
        @self.app.route('/scrape-offres', methods=['POST'])
        def scraper_offres():
            """
            Endpoint principal pour scraper les offres d'alternance.

            Body JSON attendu:
            {
                "termes": ["alternance cybersécurité", "apprentissage sécurité"],
                "max_offres": 10,
                "sources": ["pole_emploi", "apec"]  // optionnel
            }

            Returns:
                JSON: Résultats du scraping avec métadonnées
            """
            try:
                # Récupération et validation des paramètres
                data = request.get_json() or {}
                termes = data.get('termes', ['alternance cybersécurité'])
                max_offres = min(
                    data.get('max_offres', self.config['max_offres_default']),
                    100)  # Limite sécurité
                sources = data.get('sources', ['pole_emploi', 'apec'])

                logger.info(
                    f"🔍 Scraping demandé - Termes: {termes}, Max: {max_offres}, Sources: {sources}"
                )

                # Vérifier disponibilité du scraper
                if not self.scraper:
                    logger.warning(
                        "Scraper non disponible - retour de données de test")
                    return self._get_test_response(termes, max_offres)

                # Configuration du scraper
                self.scraper.max_offres_par_site = max_offres
                self.scraper.termes_cybersecurite = termes

                # Collecte des offres
                logger.debug("Début de la collecte des offres...")
                offres = self.scraper.collecter_toutes_offres()

                # Préparation de la réponse pour n8n
                response = {
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "request_params": {
                        "termes": termes,
                        "max_offres": max_offres,
                        "sources": sources
                    },
                    "results": {
                        "total_offres": len(offres),
                        "offres": offres
                    },
                    "metadata": {
                        "sources_utilisees": sources,
                        "scraping_duration":
                        "calculé_par_scraper",  # TODO: implémenter timing
                        "api_version": "1.0"
                    }
                }

                logger.info(
                    f"✅ Scraping terminé avec succès - {len(offres)} offres trouvées"
                )
                return jsonify(response)

            except Exception as e:
                logger.error(f"❌ Erreur lors du scraping: {e}")
                logger.exception("Détails de l'erreur:")

                error_response = {
                    "success": False,
                    "error": {
                        "message": str(e),
                        "type": type(e).__name__,
                        "timestamp": datetime.now().isoformat()
                    },
                    "results": {
                        "total_offres": 0,
                        "offres": []
                    }
                }

                return jsonify(error_response), 500

        # Route spécifique Pôle Emploi
        @self.app.route('/scrape-pole-emploi', methods=['POST'])
        def scraper_pole_emploi_seul():
            """
            Endpoint spécifique pour scraper uniquement Pôle Emploi.

            Body JSON attendu:
            {
                "terme": "alternance cybersécurité",
                "max_offres": 5
            }

            Returns:
                JSON: Offres trouvées sur Pôle Emploi uniquement
            """
            try:
                data = request.get_json() or {}
                terme = data.get('terme', 'alternance cybersécurité')
                max_offres = min(data.get('max_offres', 5),
                                 50)  # Limite pour Pôle Emploi

                logger.info(
                    f"🔍 Scraping Pôle Emploi exclusivement - Terme: {terme}")

                if not self.scraper:
                    return self._get_test_response([terme], max_offres,
                                                   "pole_emploi")

                # Scraping Pôle Emploi uniquement
                offres = self.scraper.scraper_pole_emploi(terme)

                response = {
                    "success": True,
                    "source": "pole_emploi",
                    "timestamp": datetime.now().isoformat(),
                    "request_params": {
                        "terme": terme,
                        "max_offres": max_offres
                    },
                    "results": {
                        "total_offres": len(offres),
                        "offres": offres
                    }
                }

                logger.info(
                    f"✅ Pôle Emploi scraping terminé - {len(offres)} offres trouvées"
                )
                return jsonify(response)

            except Exception as e:
                logger.error(f"❌ Erreur Pôle Emploi scraping: {e}")

                return jsonify({
                    "success": False,
                    "error": {
                        "message": str(e),
                        "type": type(e).__name__,
                        "timestamp": datetime.now().isoformat()
                    },
                    "results": {
                        "total_offres": 0,
                        "offres": []
                    }
                }), 500

        # Route de test
        @self.app.route('/test-offres', methods=['GET'])
        def test_offres():
            """
            Endpoint de test avec offres d'exemple pour développement/debug.

            Returns:
                JSON: Offres de test formatées pour n8n
            """
            logger.debug("Endpoint de test appelé")
            return self._get_test_response()

        # Route de configuration (pour debug)
        @self.app.route('/config', methods=['GET'])
        def get_config():
            """
            Endpoint pour obtenir la configuration actuelle (debug).

            Returns:
                JSON: Configuration non-sensible de l'API
            """
            logger.debug("Configuration demandée")

            safe_config = {
                "api_port": self.config['api_port'],
                "api_host": self.config['api_host'],
                "api_debug": self.config['api_debug'],
                "max_offres_default": self.config['max_offres_default'],
                "cors_enabled": self.config['cors_enabled'],
                "scraper_available": self.scraper is not None,
                "has_mistral_api": bool(self.config['mistral_api_key']),
                "has_api_secret": bool(self.config['api_secret_key'])
            }

            return jsonify(safe_config)

    def _get_test_response(self,
                           termes: List[str] = None,
                           max_offres: int = 2,
                           source: str = "test") -> Dict:
        """
        Génère une réponse de test avec des offres fictives.

        Args:
            termes: Termes de recherche (pour cohérence)
            max_offres: Nombre d'offres à générer
            source: Source simulée

        Returns:
            Dict: Réponse JSON avec offres de test
        """
        if termes is None:
            termes = ['alternance cybersécurité']

        offres_test = [{
            "title": "Alternance Cybersécurité - Analyste SOC",
            "company": "TechSecure Corp",
            "location": "Paris (75)",
            "url": "https://candidat.pole-emploi.fr/offres/test1",
            "description":
            "Recherche alternant pour rejoindre notre équipe SOC. Formation sur les outils SIEM, analyse de logs et réponse aux incidents.",
            "scraper_source": source,
            "search_term": termes[0] if termes else "test",
            "scraped_at": datetime.now().isoformat(),
            "is_valid": None,
            "ai_response": None
        }, {
            "title": "Apprenti Ingénieur Sécurité Informatique",
            "company": "SecureIT Solutions",
            "location": "Lyon (69)",
            "url": "https://candidat.pole-emploi.fr/offres/test2",
            "description":
            "Formation en alternance dans le domaine de la sécurité IT. Missions : audit sécurité, tests d'intrusion, gestion des vulnérabilités.",
            "scraper_source": source,
            "search_term": termes[0] if termes else "test",
            "scraped_at": datetime.now().isoformat(),
            "is_valid": None,
            "ai_response": None
        }]

        # Limiter au nombre demandé
        offres_test = offres_test[:max_offres]

        return jsonify({
            "success": True,
            "test_mode": True,
            "timestamp": datetime.now().isoformat(),
            "request_params": {
                "termes": termes,
                "max_offres": max_offres
            },
            "results": {
                "total_offres": len(offres_test),
                "offres": offres_test
            },
            "metadata": {
                "source": source,
                "api_version": "1.0"
            }
        })

    def run(self):
        """
        Lance le serveur Flask avec la configuration chargée.
        """
        logger.info("🚀 Démarrage de l'API Scraper pour n8n")
        logger.info("📡 Endpoints disponibles:")
        logger.info("   - GET  /health : Vérification santé")
        logger.info(
            "   - POST /scrape-offres : Scraping complet multi-sources")
        logger.info(
            "   - POST /scrape-pole-emploi : Pôle Emploi exclusivement")
        logger.info("   - GET  /test-offres : Données de test")
        logger.info("   - GET  /config : Configuration actuelle")
        logger.info(
            f"🌐 Serveur accessible sur: http://{self.config['api_host']}:{self.config['api_port']}"
        )

        try:
            logger.debug(f"Tentative de démarrage du serveur Flask avec host={self.config['api_host']}, port={self.config['api_port']}, debug={self.config['api_debug']}")
            self.app.run(host=self.config['api_host'],
                         port=self.config['api_port'],
                         debug=self.config['api_debug'],
                         threaded=True)
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage du serveur: {e}")
            raise


def main():
    """
    Fonction principale avec support des arguments CLI.
    """
    parser = argparse.ArgumentParser(
        description="API Flask pour scraping d'offres d'alternance",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--port',
                        type=int,
                        help="Port d'écoute (override de la config)")

    parser.add_argument('--host',
                        type=str,
                        default='0.0.0.0',
                        help="Host d'écoute (défaut: 0.0.0.0)")

    parser.add_argument('--debug',
                        action='store_true',
                        help="Activer le mode debug Flask")

    parser.add_argument('--log-level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help="Niveau de logging (override de la config)")

    args = parser.parse_args()

    # --- Début de l'ajout pour diagnostic ---
    print(f"[DIAGNOSTIC] Valeur de args.log_level avant toute configuration: {args.log_level}")
    # --- Fin de l'ajout pour diagnostic ---

    try:
        # Configurer le niveau de logging le plus tôt possible
        # pour affecter tous les messages suivants, y compris ceux de load_config.
        initial_log_level = args.log_level or os.getenv('LOG_LEVEL', 'INFO')
        if initial_log_level:
            set_global_log_level(initial_log_level.upper())
            logger.debug(f"Niveau de logger global appliqué via set_global_log_level : {initial_log_level.upper()}")
        else:
            # Fallback si initial_log_level est None ou vide, bien que argparse et getenv devraient fournir une valeur.
            logger.warning("Aucun niveau de log initial spécifié pour set_global_log_level.")

        # Charger la configuration
        config = load_config()

        # Override avec les arguments CLI
        if args.port:
            config['api_port'] = args.port
        if args.host:
            config['api_host'] = args.host
        if args.debug:
            config['api_debug'] = True

        logger.debug(f"Configuration finale avant initialisation de ScraperAPI : {config}")

        # Créer et lancer l'API
        api = ScraperAPI(config)
        api.run()

    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        logger.exception("Détails de l'erreur:")
        sys.exit(1)


if __name__ == '__main__':
    main()
