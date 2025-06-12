#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur automatique de documentation Sphinx pour les Agents IA.

Ce module automatise la génération de documentation à partir des docstrings
présentes dans le code source des agents Python et n8n + API.

Fonctionnalités principales :
- Scan automatique de tous les modules Python
- Extraction des docstrings avec style Google/NumPy
- Génération de fichiers RST pour Sphinx
- Configuration automatique de Sphinx
- Build HTML/PDF de la documentation
- Support des extensions avancées (autodoc, napoleon, etc.)
- Génération d'index et de tables des matières
- Intégration avec les diagrammes UML

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: 03/06/2025
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import importlib.util
import ast

# Ajouter le module de logging commun
sys.path.insert(0, str(Path(__file__).parent))
try:
    from logger_config import get_logger
except ImportError:
    import logging
    def get_logger(name: str, **kwargs):
        """Fallback logger en cas d'import impossible."""
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

# Initialiser le logger
logger = get_logger(__name__, log_file="sphinx_doc_generator.log")


class SphinxDocGenerator:
    """
    Générateur de documentation Sphinx pour le projet IA.

    Cette classe automatise complètement la génération de documentation :
    - Découverte automatique des modules Python
    - Extraction et parsing des docstrings
    - Génération des fichiers de configuration Sphinx
    - Build de la documentation en plusieurs formats

    Attributes:
        project_root (Path): Racine du projet
        docs_dir (Path): Répertoire de documentation
        source_dirs (List[Path]): Répertoires contenant le code source
        output_formats (List[str]): Formats de sortie supportés
        sphinx_config (Dict): Configuration Sphinx personnalisée
    """

    def __init__(self,
                 project_root: Optional[Path] = None,
                 docs_output_dir: str = "docs_generated"):
        """
        Initialise le générateur de documentation.

        Args:
            project_root: Racine du projet (auto-détectée si None)
            docs_output_dir: Nom du répertoire de sortie de la documentation
        """
        self.project_root = self._find_project_root(project_root)
        self.docs_dir = self.project_root / docs_output_dir
        self.source_dirs = self._discover_source_directories()
        self.output_formats = ['html', 'epub', 'latex']
        self.sphinx_config = self._get_default_sphinx_config()

        logger.info(f"SphinxDocGenerator initialisé pour: {self.project_root}")
        logger.debug(f"Répertoires source détectés: {[str(d) for d in self.source_dirs]}")

    def _find_project_root(self, project_root: Optional[Path] = None) -> Path:
        """
        Trouve automatiquement la racine du projet.

        Args:
            project_root: Chemin spécifié par l'utilisateur

        Returns:
            Path: Chemin vers la racine du projet
        """
        if project_root:
            return Path(project_root).resolve()

        # Recherche automatique basée sur les marqueurs de projet
        current = Path(__file__).resolve()

        # Rechercher vers le haut jusqu'à trouver des marqueurs
        for parent in current.parents:
            markers = [
                parent / "README.md",
                parent / "agent_python",
                parent / "agent_n8n",
                parent / ".git"
            ]

            if any(marker.exists() for marker in markers):
                logger.debug(f"Racine du projet détectée: {parent}")
                return parent

        # Fallback : répertoire parent du script
        fallback = current.parent.parent.parent
        logger.warning(f"Racine du projet non détectée, utilisation de: {fallback}")
        return fallback

    def _discover_source_directories(self) -> List[Path]:
        """
        Découvre automatiquement les répertoires contenant du code source.

        Returns:
            List[Path]: Liste des répertoires source trouvés
        """
        source_dirs = []

        # Répertoires à analyser
        candidate_dirs = [
            self.project_root / "agent_python" / "src",
            self.project_root / "agent_n8n" / "api",
            self.project_root / "shared" / "scripts",
            self.project_root / "tests"
        ]

        for dir_path in candidate_dirs:
            if dir_path.exists() and any(dir_path.glob("*.py")):
                source_dirs.append(dir_path)
                logger.debug(f"Répertoire source ajouté: {dir_path}")

        if not source_dirs:
            logger.warning("Aucun répertoire source détecté !")

        return source_dirs

    def _get_default_sphinx_config(self) -> Dict[str, Any]:
        """
        Configuration par défaut pour Sphinx.

        Returns:
            Dict: Configuration Sphinx complète
        """
        return {
            'project': 'Agent IA - Recherche Offres',
            'author': 'desmedt.franck@iaproject.fr',
            'version': '1.0',
            'release': '1.0.0',
            'copyright': f'{datetime.now().year}, Franck Desmedt',
            'language': 'fr',
            'extensions': [
                'sphinx.ext.autodoc',
                'sphinx.ext.napoleon',
                'sphinx.ext.viewcode',
                'sphinx.ext.githubpages',
                'sphinx.ext.intersphinx',
                'sphinx.ext.todo',
                'sphinx.ext.coverage',
                'sphinx.ext.imgmath',
                'sphinx.ext.graphviz'
            ],
            'templates_path': ['_templates'],
            'exclude_patterns': ['_build', 'Thumbs.db', '.DS_Store'],
            'html_theme': 'sphinx_rtd_theme',
            'html_static_path': ['_static'],
            'todo_include_todos': True,
            'napoleon_google_docstring': True,
            'napoleon_numpy_docstring': True,
            'napoleon_include_init_with_doc': False,
            'napoleon_include_private_with_doc': False,
            'autodoc_default_options': {
                'members': True,
                'undoc-members': True,
                'show-inheritance': True,
                'special-members': '__init__',
            },
            'intersphinx_mapping': {
                'python': ('https://docs.python.org/3/', None),
                'requests': ('https://requests.readthedocs.io/en/latest/', None),
                'pandas': ('https://pandas.pydata.org/docs/', None),
            }
        }

    def analyze_module(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyse un module Python pour extraire ses métadonnées.

        Args:
            file_path: Chemin vers le fichier Python

        Returns:
            Dict: Métadonnées du module (classes, fonctions, docstrings, etc.)
        """
        logger.debug(f"Analyse du module: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            module_info = {
                'file_path': str(file_path),
                'module_name': file_path.stem,
                'docstring': ast.get_docstring(tree),
                'classes': [],
                'functions': [],
                'imports': []
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node),
                        'methods': []
                    }

                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append({
                                'name': item.name,
                                'docstring': ast.get_docstring(item),
                                'args': [arg.arg for arg in item.args.args]
                            })

                    module_info['classes'].append(class_info)

                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    # Fonctions au niveau module (pas dans une classe)
                    module_info['functions'].append({
                        'name': node.name,
                        'docstring': ast.get_docstring(node),
                        'args': [arg.arg for arg in node.args.args]
                    })

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_info['imports'].append(ast.dump(node))

            return module_info

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {file_path}: {e}")
            return {
                'file_path': str(file_path),
                'module_name': file_path.stem,
                'error': str(e)
            }

    def generate_rst_files(self) -> List[Path]:
        """
        Génère les fichiers RST pour tous les modules trouvés.

        Returns:
            List[Path]: Liste des fichiers RST générés
        """
        logger.info("Génération des fichiers RST...")

        rst_files = []
        rst_dir = self.docs_dir / "source"
        rst_dir.mkdir(parents=True, exist_ok=True)

        # Générer un fichier RST pour chaque répertoire source
        for source_dir in self.source_dirs:
            logger.debug(f"Traitement du répertoire: {source_dir}")

            # Nom du module basé sur le répertoire
            module_name = self._get_module_name(source_dir)
            rst_file = rst_dir / f"{module_name}.rst"

            # Collecter tous les fichiers Python
            python_files = list(source_dir.rglob("*.py"))
            if not python_files:
                continue

            # Générer le contenu RST
            rst_content = self._generate_rst_content(module_name, source_dir, python_files)

            # Écrire le fichier RST
            with open(rst_file, 'w', encoding='utf-8') as f:
                f.write(rst_content)

            rst_files.append(rst_file)
            logger.debug(f"Fichier RST généré: {rst_file}")

        # Générer l'index principal
        self._generate_main_index(rst_dir, rst_files)

        logger.info(f"✅ {len(rst_files)} fichiers RST générés")
        return rst_files

    def _get_module_name(self, source_dir: Path) -> str:
        """
        Détermine le nom du module basé sur le répertoire.

        Args:
            source_dir: Répertoire source

        Returns:
            str: Nom du module
        """
        # Extraire le nom basé sur la structure
        relative_path = source_dir.relative_to(self.project_root)
        return "_".join(relative_path.parts).replace("-", "_")

    def _generate_rst_content(self, module_name: str, source_dir: Path, python_files: List[Path]) -> str:
        """
        Génère le contenu RST pour un module.

        Args:
            module_name: Nom du module
            source_dir: Répertoire source
            python_files: Liste des fichiers Python

        Returns:
            str: Contenu RST formaté
        """
        title = f"Module {module_name.replace('_', ' ').title()}"
        rst_content = f"""
{title}
{'=' * len(title)}

Ce module contient les composants suivants :

"""

        # Analyser chaque fichier Python
        for py_file in python_files:
            if py_file.name.startswith('__'):
                continue  # Ignorer __init__.py, __pycache__, etc.

            module_info = self.analyze_module(py_file)
            relative_path = py_file.relative_to(self.project_root)
            module_path = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')

            rst_content += f"""
{py_file.stem}
{'-' * len(py_file.stem)}

.. automodule:: {module_path}
   :members:
   :undoc-members:
   :show-inheritance:

"""

            # Ajouter des détails si docstring disponible
            if module_info.get('docstring'):
                rst_content += f"""
Description
^^^^^^^^^^^

{module_info['docstring']}

"""

            # Lister les classes principales
            if module_info.get('classes'):
                rst_content += """
Classes principales
^^^^^^^^^^^^^^^^^^^

"""
                for class_info in module_info['classes']:
                    rst_content += f"* :class:`{module_path}.{class_info['name']}`\n"
                rst_content += "\n"

            # Lister les fonctions principales
            if module_info.get('functions'):
                rst_content += """
Fonctions principales
^^^^^^^^^^^^^^^^^^^^^

"""
                for func_info in module_info['functions']:
                    if not func_info['name'].startswith('_'):  # Fonctions publiques seulement
                        rst_content += f"* :func:`{module_path}.{func_info['name']}`\n"
                rst_content += "\n"

        return rst_content

    def _generate_main_index(self, rst_dir: Path, rst_files: List[Path]) -> None:
        """
        Génère le fichier index.rst principal.

        Args:
            rst_dir: Répertoire des fichiers RST
            rst_files: Liste des fichiers RST générés
        """
        index_content = f"""
Agent IA - Documentation Technique
==================================

Documentation générée automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}.

Cette documentation couvre l'ensemble des composants des agents IA pour la recherche d'offres d'alternance en cybersécurité.

Architecture du projet
======================

Le projet est organisé en deux agents principaux :

* **Agent Python Standalone** : Solution autonome pour le scraping et l'analyse
* **Agent n8n + API** : Solution d'orchestration avancée avec interface graphique

Modules disponibles
==================

.. toctree::
   :maxdepth: 2
   :caption: Documentation des modules:

"""

        # Ajouter chaque fichier RST à la table des matières
        for rst_file in rst_files:
            module_name = rst_file.stem
            index_content += f"   {module_name}\n"

        index_content += """

Indices et tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

À propos
========

:Auteur: desmedt.franck@iaproject.fr
:Version: 1.0
:Date: 03/06/2025
:Licence: MIT

Cette documentation est générée automatiquement à partir des docstrings présentes dans le code source.
"""

        index_file = rst_dir / "index.rst"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

        logger.debug(f"Index principal généré: {index_file}")

    def create_sphinx_config(self) -> None:
        """
        Crée les fichiers de configuration Sphinx.
        """
        logger.info("Création de la configuration Sphinx...")

        source_dir = self.docs_dir / "source"
        source_dir.mkdir(parents=True, exist_ok=True)

        # Générer conf.py
        conf_content = f'''# Configuration file for the Sphinx documentation builder.
# This file was auto-generated by sphinx_doc_generator.py

import os
import sys
sys.path.insert(0, os.path.abspath('{self.project_root}'))

# -- Project information -----------------------------------------------------

project = '{self.sphinx_config["project"]}'
copyright = '{self.sphinx_config["copyright"]}'
author = '{self.sphinx_config["author"]}'
version = '{self.sphinx_config["version"]}'
release = '{self.sphinx_config["release"]}'

# -- General configuration ---------------------------------------------------

extensions = {self.sphinx_config["extensions"]}

templates_path = {self.sphinx_config["templates_path"]}
language = '{self.sphinx_config["language"]}'
exclude_patterns = {self.sphinx_config["exclude_patterns"]}

# -- Options for HTML output -------------------------------------------------

html_theme = '{self.sphinx_config["html_theme"]}'
html_static_path = {self.sphinx_config["html_static_path"]}

# -- Extension configuration -------------------------------------------------

# Napoleon settings
napoleon_google_docstring = {self.sphinx_config["napoleon_google_docstring"]}
napoleon_numpy_docstring = {self.sphinx_config["napoleon_numpy_docstring"]}
napoleon_include_init_with_doc = {self.sphinx_config["napoleon_include_init_with_doc"]}
napoleon_include_private_with_doc = {self.sphinx_config["napoleon_include_private_with_doc"]}

# Autodoc settings
autodoc_default_options = {self.sphinx_config["autodoc_default_options"]}

# Todo settings
todo_include_todos = {self.sphinx_config["todo_include_todos"]}

# Intersphinx settings
intersphinx_mapping = {self.sphinx_config["intersphinx_mapping"]}
'''

        conf_file = source_dir / "conf.py"
        with open(conf_file, 'w', encoding='utf-8') as f:
            f.write(conf_content)

        # Créer les répertoires nécessaires
        (source_dir / "_static").mkdir(exist_ok=True)
        (source_dir / "_templates").mkdir(exist_ok=True)

        logger.debug(f"Configuration Sphinx créée: {conf_file}")

    def install_sphinx_dependencies(self) -> bool:
        """
        Installe les dépendances Sphinx nécessaires.

        Returns:
            bool: True si l'installation réussit
        """
        logger.info("Vérification des dépendances Sphinx...")

        required_packages = [
            'sphinx',
            'sphinx-rtd-theme',
            'sphinx-autodoc-typehints'
        ]

        try:
            for package in required_packages:
                logger.debug(f"Vérification de {package}...")
                try:
                    __import__(package.replace('-', '_'))
                    logger.debug(f"✅ {package} déjà installé")
                except ImportError:
                    logger.info(f"Installation de {package}...")
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install', package
                    ], capture_output=True)
                    logger.debug(f"✅ {package} installé")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de l'installation des dépendances: {e}")
            return False

    def build_documentation(self, formats: Optional[List[str]] = None) -> Dict[str, Path]:
        """
        Construit la documentation dans les formats spécifiés.

        Args:
            formats: Liste des formats à générer (html, epub, latex)

        Returns:
            Dict[str, Path]: Mapping format -> chemin de sortie
        """
        if formats is None:
            formats = ['html']

        logger.info(f"Construction de la documentation - Formats: {formats}")

        source_dir = self.docs_dir / "source"
        build_results = {}

        for fmt in formats:
            build_dir = self.docs_dir / f"_build" / fmt
            build_dir.mkdir(parents=True, exist_ok=True)

            logger.debug(f"Construction du format {fmt}...")

            try:
                cmd = [
                    'sphinx-build',
                    '-b', fmt,
                    str(source_dir),
                    str(build_dir)
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.docs_dir
                )

                if result.returncode == 0:
                    build_results[fmt] = build_dir
                    logger.info(f"✅ Documentation {fmt} générée: {build_dir}")
                else:
                    logger.error(f"❌ Erreur lors de la génération {fmt}: {result.stderr}")

            except FileNotFoundError:
                logger.error(f"❌ sphinx-build non trouvé. Installez Sphinx avec: pip install sphinx")

        return build_results

    def generate_full_documentation(self, formats: Optional[List[str]] = None) -> Dict[str, Path]:
        """
        Génère la documentation complète (processus complet).

        Args:
            formats: Formats de sortie souhaités

        Returns:
            Dict[str, Path]: Résultats de la génération
        """
        logger.info("🚀 Génération complète de la documentation...")

        try:
            # 1. Installer les dépendances
            if not self.install_sphinx_dependencies():
                raise RuntimeError("Impossible d'installer les dépendances Sphinx")

            # 2. Créer la configuration Sphinx
            self.create_sphinx_config()

            # 3. Générer les fichiers RST
            rst_files = self.generate_rst_files()

            # 4. Construire la documentation
            build_results = self.build_documentation(formats)

            logger.info("🎉 Documentation générée avec succès !")

            # Afficher les résultats
            for fmt, path in build_results.items():
                if fmt == 'html':
                    index_file = path / "index.html"
                    if index_file.exists():
                        logger.info(f"📖 Documentation HTML: file://{index_file}")

                logger.info(f"📁 {fmt.upper()}: {path}")

            return build_results

        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération: {e}")
            raise


def main():
    """
    Fonction principale du générateur de documentation.

    Peut être utilisée en ligne de commande avec différents arguments
    pour personnaliser la génération.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Générateur automatique de documentation Sphinx"
    )

    parser.add_argument(
        '--project-root',
        type=str,
        help="Racine du projet (auto-détectée si non spécifié)"
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default="docs_generated",
        help="Répertoire de sortie de la documentation"
    )

    parser.add_argument(
        '--formats',
        nargs='+',
        choices=['html', 'epub', 'latex'],
        default=['html'],
        help="Formats de documentation à générer"
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help="Niveau de logging"
    )

    args = parser.parse_args()

    # Configurer le logging
    import logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    try:
        # Créer le générateur
        project_root = Path(args.project_root) if args.project_root else None
        generator = SphinxDocGenerator(
            project_root=project_root,
            docs_output_dir=args.output_dir
        )

        # Générer la documentation
        results = generator.generate_full_documentation(args.formats)

        print("\n🎉 Documentation générée avec succès !")
        for fmt, path in results.items():
            print(f"📁 {fmt.upper()}: {path}")

    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()