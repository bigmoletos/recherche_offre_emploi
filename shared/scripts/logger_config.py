#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de configuration du logging pour les Agents IA Recherche Offres

Ce module fournit une configuration standardisée du système de logging
pour les agents Python Standalone et n8n + API.

Fonctionnalités :
- Configuration automatique des loggers
- Rotation des fichiers de logs
- Formatage uniforme des messages
- Niveaux de log configurables
- Support multi-environnement

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: 03/06/2025
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Union


class ColoredFormatter(logging.Formatter):
    """
    Formateur de logs avec couleurs pour la console.

    Ajoute des codes ANSI pour colorer les messages selon leur niveau,
    améliorant la lisibilité des logs dans le terminal.
    """

    # Codes couleurs ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Vert
        'WARNING': '\033[33m',    # Jaune
        'ERROR': '\033[31m',      # Rouge
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        """
        Formate un enregistrement de log avec des couleurs.

        Args:
            record: Enregistrement de log à formater

        Returns:
            str: Message formaté avec couleurs
        """
        # Formatage de base
        formatted = super().format(record)

        # Ajout des couleurs si supportées
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            level_color = self.COLORS.get(record.levelname, '')
            reset_color = self.COLORS['RESET']
            return f"{level_color}{formatted}{reset_color}"

        return formatted


class IAProjectLogger:
    """
    Gestionnaire de logging centralisé pour le projet IA.

    Cette classe configure et gère tous les aspects du logging :
    - Création des répertoires de logs
    - Configuration des handlers (fichier + console)
    - Rotation automatique des fichiers
    - Formatage uniforme des messages

    Attributes:
        log_dir (Path): Répertoire de stockage des logs
        log_level (str): Niveau de logging actuel
        max_bytes (int): Taille max des fichiers de log
        backup_count (int): Nombre de fichiers de sauvegarde
    """

    def __init__(self,
                 log_dir: Optional[Union[str, Path]] = None,
                 log_level: str = "INFO",
                 max_bytes: int = 10 * 1024 * 1024,  # 10 MB
                 backup_count: int = 5):
        """
        Initialise le gestionnaire de logging.

        Args:
            log_dir: Répertoire pour les fichiers de log (auto-détecté si None)
            log_level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Taille maximale des fichiers de log en bytes
            backup_count: Nombre de fichiers de sauvegarde à conserver
        """
        self.log_dir = self._resolve_log_directory(log_dir)
        self.log_level = log_level.upper()
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Créer le répertoire de logs si nécessaire
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Cache des loggers créés
        self._loggers = {}

    def _resolve_log_directory(self, log_dir: Optional[Union[str, Path]]) -> Path:
        """
        Détermine le répertoire de logs à utiliser.

        Args:
            log_dir: Répertoire spécifié par l'utilisateur

        Returns:
            Path: Chemin vers le répertoire de logs
        """
        if log_dir:
            return Path(log_dir)

        # Auto-détection basée sur la structure du projet
        current_file = Path(__file__).resolve()

        # Chercher le répertoire agent_python ou agent_n8n
        for parent in current_file.parents:
            if parent.name in ['agent_python', 'agent_n8n']:
                return parent / 'logs'

        # Fallback : créer un dossier logs à côté du script appelant
        caller_file = Path(sys.argv[0]).resolve() if sys.argv else current_file
        return caller_file.parent / 'logs'

    def get_logger(self,
                   name: str,
                   log_file: Optional[str] = None,
                   console_output: bool = True) -> logging.Logger:
        """
        Obtient ou crée un logger configuré.

        Args:
            name: Nom du logger (généralement __name__ du module)
            log_file: Nom du fichier de log (auto-généré si None)
            console_output: Activer la sortie console

        Returns:
            logging.Logger: Logger configuré et prêt à utiliser
        """
        # Vérifier le cache
        cache_key = f"{name}_{log_file}_{console_output}"
        if cache_key in self._loggers:
            return self._loggers[cache_key]

        # Créer le logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.log_level))

        # Éviter les handlers dupliqués
        logger.handlers.clear()

        # Configuration du formateur
        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_formatter = ColoredFormatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # Handler pour fichier avec rotation
        if log_file is None:
            # Générer un nom de fichier basé sur le nom du logger
            safe_name = "".join(c for c in name if c.isalnum() or c in "._-")
            log_file = f"{safe_name}_{datetime.now().strftime('%Y%m%d')}.log"

        file_path = self.log_dir / log_file
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(getattr(logging, self.log_level))
        logger.addHandler(file_handler)

        # Handler pour console
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(getattr(logging, self.log_level))
            logger.addHandler(console_handler)

        # Ajouter au cache
        self._loggers[cache_key] = logger

        # Log de démarrage
        logger.debug(f"Logger '{name}' initialisé - Niveau: {self.log_level} - Fichier: {file_path}")

        return logger

    def set_level(self, level: str):
        """
        Change le niveau de logging pour tous les loggers.

        Args:
            level: Nouveau niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = level.upper()

        # Mettre à jour tous les loggers existants
        for logger in self._loggers.values():
            logger.setLevel(getattr(logging, self.log_level))
            for handler in logger.handlers:
                handler.setLevel(getattr(logging, self.log_level))

    def get_stats(self) -> dict:
        """
        Retourne des statistiques sur le système de logging.

        Returns:
            dict: Statistiques incluant nombre de loggers, taille des fichiers, etc.
        """
        stats = {
            'loggers_count': len(self._loggers),
            'log_directory': str(self.log_dir),
            'log_level': self.log_level,
            'log_files': []
        }

        # Informations sur les fichiers de log
        for log_file in self.log_dir.glob('*.log'):
            try:
                stats['log_files'].append({
                    'name': log_file.name,
                    'size': log_file.stat().st_size,
                    'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                })
            except OSError:
                pass

        return stats


# Instance globale pour faciliter l'utilisation
_global_logger_manager = None


def get_logger(name: str,
               log_dir: Optional[Union[str, Path]] = None,
               log_level: str = "INFO",
               log_file: Optional[str] = None,
               console_output: bool = True) -> logging.Logger:
    """
    Fonction utilitaire pour obtenir un logger configuré.

    Cette fonction simplifie l'utilisation du système de logging en créant
    automatiquement un gestionnaire global s'il n'existe pas.

    Args:
        name: Nom du logger (généralement __name__)
        log_dir: Répertoire des logs (auto-détecté si None)
        log_level: Niveau de logging
        log_file: Nom du fichier de log
        console_output: Activer la sortie console

    Returns:
        logging.Logger: Logger configuré

    Example:
        >>> from shared.scripts.logger_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Message d'information")
        >>> logger.error("Message d'erreur")
    """
    global _global_logger_manager

    if _global_logger_manager is None:
        _global_logger_manager = IAProjectLogger(
            log_dir=log_dir,
            log_level=log_level
        )

    return _global_logger_manager.get_logger(
        name=name,
        log_file=log_file,
        console_output=console_output
    )


def set_global_log_level(level: str):
    """
    Change le niveau de logging global.

    Args:
        level: Nouveau niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global _global_logger_manager

    if _global_logger_manager is not None:
        _global_logger_manager.set_level(level)


def get_logging_stats() -> dict:
    """
    Retourne les statistiques du système de logging.

    Returns:
        dict: Statistiques détaillées
    """
    global _global_logger_manager

    if _global_logger_manager is not None:
        return _global_logger_manager.get_stats()

    return {'error': 'Gestionnaire de logging non initialisé'}


# Configuration par défaut au niveau module
def configure_default_logging():
    """Configure le logging par défaut pour les scripts simples."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )


if __name__ == "__main__":
    # Tests et démonstration
    print("🧪 Test du module de logging")

    # Test basique
    logger = get_logger(__name__)
    logger.info("Test du logger - niveau INFO")
    logger.debug("Test du logger - niveau DEBUG (non visible)")
    logger.warning("Test du logger - niveau WARNING")
    logger.error("Test du logger - niveau ERROR")

    # Test changement de niveau
    set_global_log_level("DEBUG")
    logger.debug("Test du logger - niveau DEBUG (maintenant visible)")

    # Affichage des statistiques
    stats = get_logging_stats()
    print(f"\n📊 Statistiques: {stats}")

    print("\n✅ Tests terminés")