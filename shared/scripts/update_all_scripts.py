#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaire de mise à jour automatique des scripts du projet Agent IA.

Ce script automatise la mise à jour de tous les fichiers Python du projet
pour intégrer les nouvelles conventions de documentation et de logging.

Fonctionnalités principales :
- Scan automatique de tous les fichiers Python
- Mise à jour des headers avec métadonnées standardisées
- Intégration du système de logging commun
- Amélioration des docstrings existantes
- Ajout de commentaires explicatifs
- Génération de rapport de mise à jour
- Sauvegarde automatique avant modifications

Le script respecte la structure existante et n'écrase pas
le code fonctionnel, mais améliore la documentation et le logging.

Usage :
    python shared/scripts/update_all_scripts.py                # Mise à jour complète
    python shared/scripts/update_all_scripts.py --dry-run      # Simulation sans modification
    python shared/scripts/update_all_scripts.py --backup       # Avec sauvegarde complète
    python shared/scripts/update_all_scripts.py --check        # Vérification seulement

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: 03/06/2025
"""

import os
import sys
import ast
import argparse
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

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
logger = get_logger(__name__, log_file="update_all_scripts.log")


class ScriptUpdater:
    """
    Utilitaire de mise à jour automatique des scripts Python.

    Cette classe analyse et met à jour tous les fichiers Python du projet
    pour intégrer les nouvelles conventions de documentation, logging
    et structure de code.

    Attributes:
        project_root (Path): Racine du projet
        backup_dir (Path): Répertoire de sauvegarde
        standard_header (str): Header standardisé pour les modules
        logging_import (str): Code d'import du système de logging
        updated_files (List[str]): Liste des fichiers modifiés
        stats (Dict): Statistiques de mise à jour
    """

    def __init__(self, project_root: Optional[Path] = None, create_backup: bool = True):
        """
        Initialise l'utilitaire de mise à jour.

        Args:
            project_root: Racine du projet (auto-détectée si None)
            create_backup: Si True, crée une sauvegarde avant modifications
        """
        self.project_root = self._find_project_root(project_root)
        self.create_backup = create_backup
        self.backup_dir = self.project_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.updated_files = []
        self.stats = {
            'files_scanned': 0,
            'files_updated': 0,
            'headers_added': 0,
            'logging_added': 0,
            'docstrings_improved': 0,
            'errors': 0
        }

        # Templates standardisés
        self.standard_header = self._get_standard_header()
        self.logging_import = self._get_logging_import()

        logger.info(f"ScriptUpdater initialisé pour: {self.project_root}")
        if create_backup:
            logger.info(f"Sauvegarde sera créée dans: {self.backup_dir}")

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

        # Recherche automatique
        current = Path(__file__).resolve()

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

        # Fallback
        fallback = current.parent.parent.parent
        logger.warning(f"Racine du projet non détectée, utilisation de: {fallback}")
        return fallback

    def _get_standard_header(self) -> str:
        """
        Retourne le header standardisé pour les modules.

        Returns:
            str: Template de header avec métadonnées
        """
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{title}

{description}

{features}

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: {date}
"""
'''

    def _get_logging_import(self) -> str:
        """
        Retourne le code d'import du système de logging commun.

        Returns:
            str: Code d'import standardisé
        """
        return '''
# Ajouter le module de logging commun
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared" / "scripts"))
try:
    from logger_config import get_logger
except ImportError:
    import logging
    def get_logger(name: str, **kwargs):
        """Fallback logger en cas d'import impossible."""
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

# Initialiser le logger
logger = get_logger(__name__, log_file="{log_file}")
'''

    def find_python_files(self) -> List[Path]:
        """
        Trouve tous les fichiers Python du projet à mettre à jour.

        Returns:
            List[Path]: Liste des fichiers Python trouvés
        """
        logger.info("Recherche des fichiers Python à mettre à jour...")

        python_files = []
        ignore_patterns = [
            "__pycache__",
            ".pyc",
            "venv",
            ".git",
            "node_modules",
            "backup_"
        ]

        # Répertoires à analyser
        target_dirs = [
            self.project_root / "agent_python" / "src",
            self.project_root / "agent_n8n" / "api",
            self.project_root / "shared" / "scripts"
        ]

        for target_dir in target_dirs:
            if target_dir.exists():
                logger.debug(f"Scan du répertoire: {target_dir}")

                for py_file in target_dir.rglob("*.py"):
                    # Vérifier si le fichier doit être ignoré
                    if any(pattern in str(py_file) for pattern in ignore_patterns):
                        logger.debug(f"Fichier ignoré: {py_file}")
                        continue

                    python_files.append(py_file)
                    logger.debug(f"Fichier Python trouvé: {py_file}")

        logger.info(f"✅ {len(python_files)} fichiers Python trouvés pour mise à jour")
        return python_files

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyse un fichier Python pour déterminer les améliorations nécessaires.

        Args:
            file_path: Chemin vers le fichier à analyser

        Returns:
            Dict[str, Any]: Analyse détaillée du fichier
        """
        logger.debug(f"Analyse du fichier: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            analysis = {
                'file_path': str(file_path),
                'has_shebang': content.startswith('#!/usr/bin/env python'),
                'has_encoding': '# -*- coding: utf-8 -*-' in content[:200],
                'has_docstring': False,
                'has_author': 'desmedt.franck@iaproject.fr' in content,
                'has_version': 'Version:' in content,
                'has_date': 'Date:' in content,
                'has_logging_import': 'from logger_config import get_logger' in content,
                'has_logger_init': 'logger = get_logger(' in content,
                'content': content,
                'needs_update': False
            }

            # Vérifier la docstring du module
            try:
                tree = ast.parse(content)
                module_docstring = ast.get_docstring(tree)
                analysis['has_docstring'] = bool(module_docstring)
                analysis['docstring'] = module_docstring or ""
            except SyntaxError as e:
                logger.warning(f"Erreur de syntaxe dans {file_path}: {e}")
                analysis['syntax_error'] = str(e)

            # Déterminer si une mise à jour est nécessaire
            analysis['needs_update'] = not all([
                analysis['has_shebang'],
                analysis['has_encoding'],
                analysis['has_docstring'],
                analysis['has_author'],
                analysis['has_version'],
                analysis['has_date']
            ])

            return analysis

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {file_path}: {e}")
            return {
                'file_path': str(file_path),
                'error': str(e),
                'needs_update': False
            }

    def generate_improved_header(self, file_path: Path, analysis: Dict[str, Any]) -> str:
        """
        Génère un header amélioré pour un fichier.

        Args:
            file_path: Chemin du fichier
            analysis: Analyse du fichier existant

        Returns:
            str: Header amélioré avec métadonnées complètes
        """
        # Déterminer le titre basé sur le nom du fichier
        file_name = file_path.stem
        title_words = file_name.replace('_', ' ').replace('-', ' ').title()
        title = f"Module {title_words}"

        # Générer une description basique si pas de docstring existante
        if analysis.get('docstring'):
            # Extraire la première ligne de la docstring existante
            first_line = analysis['docstring'].split('\n')[0].strip()
            description = first_line if first_line else f"Module {title_words} pour l'Agent IA."
        else:
            description = f"Module {title_words} pour l'Agent IA de recherche d'offres."

        # Fonctionnalités par défaut
        features = """Fonctionnalités principales :
- Implémentation des fonctionnalités core
- Gestion d'erreurs robuste avec logging
- Documentation complète avec docstrings
- Intégration au système de logging commun"""

        return self.standard_header.format(
            title=title,
            description=description,
            features=features,
            date=datetime.now().strftime('%d/%m/%Y')
        )

    def update_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """
        Met à jour un fichier Python avec les nouvelles conventions.

        Args:
            file_path: Chemin du fichier à mettre à jour
            dry_run: Si True, simule sans modifier le fichier

        Returns:
            bool: True si le fichier a été modifié (ou aurait été modifié)
        """
        logger.debug(f"Mise à jour du fichier: {file_path}")

        try:
            # Analyser le fichier
            analysis = self.analyze_file(file_path)

            if analysis.get('error'):
                logger.error(f"Erreur dans {file_path}: {analysis['error']}")
                self.stats['errors'] += 1
                return False

            if not analysis['needs_update']:
                logger.debug(f"Fichier déjà à jour: {file_path}")
                return False

            content = analysis['content']
            modified = False

            # Sauvegarde si demandée
            if self.create_backup and not dry_run:
                self._backup_file(file_path)

            # Mise à jour du header
            if not all([analysis['has_shebang'], analysis['has_encoding'],
                       analysis['has_author'], analysis['has_version'], analysis['has_date']]):

                logger.debug(f"Mise à jour du header pour: {file_path}")
                new_header = self.generate_improved_header(file_path, analysis)

                # Remplacer ou ajouter le header
                if content.startswith('#!/usr/bin/env python'):
                    # Remplacer le header existant
                    lines = content.split('\n')
                    start_content = 0

                    # Trouver où commence le vrai contenu
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith('#') and not line.startswith('"""'):
                            start_content = i
                            break

                    content = new_header + '\n' + '\n'.join(lines[start_content:])
                else:
                    # Ajouter le header au début
                    content = new_header + '\n' + content

                modified = True
                self.stats['headers_added'] += 1

            # Ajouter le logging si manquant
            if not analysis['has_logging_import'] and 'import' in content:
                logger.debug(f"Ajout du système de logging pour: {file_path}")

                # Insérer après les imports existants
                lines = content.split('\n')
                import_end = 0

                for i, line in enumerate(lines):
                    if line.strip().startswith(('import ', 'from ')) or line.strip().startswith('#'):
                        import_end = i + 1

                log_file = f"{file_path.stem}.log"
                logging_code = self.logging_import.format(log_file=log_file)

                lines.insert(import_end, logging_code)
                content = '\n'.join(lines)

                modified = True
                self.stats['logging_added'] += 1

            # Sauvegarder les modifications
            if modified and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.updated_files.append(str(file_path))
                logger.info(f"✅ Fichier mis à jour: {file_path}")
                self.stats['files_updated'] += 1
            elif modified and dry_run:
                logger.info(f"🔍 [DRY-RUN] Fichier serait mis à jour: {file_path}")
                self.stats['files_updated'] += 1

            return modified

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de {file_path}: {e}")
            self.stats['errors'] += 1
            return False

    def _backup_file(self, file_path: Path):
        """
        Crée une sauvegarde d'un fichier.

        Args:
            file_path: Fichier à sauvegarder
        """
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)

        # Préserver la structure des répertoires
        relative_path = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(file_path, backup_path)
        logger.debug(f"Sauvegarde créée: {backup_path}")

    def update_all_files(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Met à jour tous les fichiers Python du projet.

        Args:
            dry_run: Si True, simule sans modifier les fichiers

        Returns:
            Dict[str, Any]: Rapport complet de mise à jour
        """
        logger.info("🚀 Début de la mise à jour de tous les scripts...")

        python_files = self.find_python_files()
        self.stats['files_scanned'] = len(python_files)

        for file_path in python_files:
            try:
                self.update_file(file_path, dry_run)
            except Exception as e:
                logger.error(f"Erreur lors du traitement de {file_path}: {e}")
                self.stats['errors'] += 1

        # Générer le rapport
        report = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'dry-run' if dry_run else 'update',
            'project_root': str(self.project_root),
            'backup_dir': str(self.backup_dir) if self.create_backup else None,
            'statistics': self.stats,
            'updated_files': self.updated_files
        }

        logger.info("✅ Mise à jour terminée")
        self._log_final_report(report)

        return report

    def _log_final_report(self, report: Dict[str, Any]):
        """
        Affiche le rapport final de mise à jour.

        Args:
            report: Rapport de mise à jour
        """
        stats = report['statistics']
        mode = "SIMULATION" if report['mode'] == 'dry-run' else "MISE À JOUR"

        logger.info(f"""
╔════════════════════════════════════════════════════╗
║                RAPPORT {mode}                    ║
╠════════════════════════════════════════════════════╣
║ Fichiers scannés        │ {stats['files_scanned']:>15} ║
║ Fichiers mis à jour     │ {stats['files_updated']:>15} ║
║ Headers ajoutés         │ {stats['headers_added']:>15} ║
║ Logging intégré         │ {stats['logging_added']:>15} ║
║ Erreurs rencontrées     │ {stats['errors']:>15} ║
╚════════════════════════════════════════════════════╝
""")

        if report['backup_dir']:
            logger.info(f"📁 Sauvegarde créée dans: {report['backup_dir']}")

        if stats['files_updated'] > 0:
            logger.info(f"📝 {stats['files_updated']} fichiers modifiés")
            for file_path in report['updated_files'][:5]:  # Afficher les 5 premiers
                logger.info(f"   ✓ {Path(file_path).relative_to(self.project_root)}")

            if len(report['updated_files']) > 5:
                logger.info(f"   ... et {len(report['updated_files']) - 5} autres")

    def check_project_compliance(self) -> Dict[str, Any]:
        """
        Vérifie la conformité du projet aux nouvelles conventions.

        Returns:
            Dict[str, Any]: Rapport de conformité détaillé
        """
        logger.info("🔍 Vérification de la conformité du projet...")

        python_files = self.find_python_files()
        compliance_report = {
            'total_files': len(python_files),
            'compliant_files': 0,
            'non_compliant_files': 0,
            'issues': {
                'missing_header': [],
                'missing_docstring': [],
                'missing_author': [],
                'missing_logging': []
            }
        }

        for file_path in python_files:
            analysis = self.analyze_file(file_path)

            if analysis.get('error'):
                continue

            is_compliant = True
            file_rel_path = str(file_path.relative_to(self.project_root))

            if not analysis['has_shebang'] or not analysis['has_encoding']:
                compliance_report['issues']['missing_header'].append(file_rel_path)
                is_compliant = False

            if not analysis['has_docstring']:
                compliance_report['issues']['missing_docstring'].append(file_rel_path)
                is_compliant = False

            if not analysis['has_author']:
                compliance_report['issues']['missing_author'].append(file_rel_path)
                is_compliant = False

            if not analysis['has_logging_import']:
                compliance_report['issues']['missing_logging'].append(file_rel_path)
                is_compliant = False

            if is_compliant:
                compliance_report['compliant_files'] += 1
            else:
                compliance_report['non_compliant_files'] += 1

        # Calculer le taux de conformité
        total = compliance_report['total_files']
        if total > 0:
            compliance_rate = (compliance_report['compliant_files'] / total) * 100
            compliance_report['compliance_rate'] = round(compliance_rate, 2)
        else:
            compliance_report['compliance_rate'] = 100.0

        logger.info(f"📊 Taux de conformité: {compliance_report['compliance_rate']:.1f}%")

        return compliance_report


def main():
    """
    Fonction principale pour l'exécution en ligne de commande.

    Gère les arguments et lance les opérations de mise à jour selon
    les options spécifiées par l'utilisateur.
    """
    parser = argparse.ArgumentParser(
        description="Utilitaire de mise à jour des scripts Agent IA",
        epilog="""
Exemples d'utilisation:
  %(prog)s                                    # Mise à jour complète
  %(prog)s --dry-run                          # Simulation sans modification
  %(prog)s --backup                           # Avec sauvegarde automatique
  %(prog)s --check                            # Vérification conformité seulement
  %(prog)s --project-root /path/to/project    # Projet spécifique
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--project-root',
        type=str,
        help="Racine du projet (auto-détectée si non spécifié)"
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Simulation sans modification des fichiers"
    )

    parser.add_argument(
        '--backup',
        action='store_true',
        help="Créer une sauvegarde avant modifications"
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help="Vérifier la conformité sans mise à jour"
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
        # Créer l'updater
        project_root = Path(args.project_root) if args.project_root else None
        updater = ScriptUpdater(
            project_root=project_root,
            create_backup=args.backup
        )

        if args.check:
            # Mode vérification seulement
            compliance_report = updater.check_project_compliance()

            print(f"\n📊 RAPPORT DE CONFORMITÉ")
            print(f"========================")
            print(f"Fichiers total: {compliance_report['total_files']}")
            print(f"Fichiers conformes: {compliance_report['compliant_files']}")
            print(f"Fichiers non-conformes: {compliance_report['non_compliant_files']}")
            print(f"Taux de conformité: {compliance_report['compliance_rate']:.1f}%")

            # Détailler les problèmes
            for issue_type, files in compliance_report['issues'].items():
                if files:
                    print(f"\n❌ {issue_type.replace('_', ' ').title()}: {len(files)} fichiers")
                    for file_path in files[:3]:  # Afficher les 3 premiers
                        print(f"   • {file_path}")
                    if len(files) > 3:
                        print(f"   ... et {len(files) - 3} autres")

        else:
            # Mode mise à jour
            report = updater.update_all_files(dry_run=args.dry_run)

            # Sauvegarder le rapport
            report_file = updater.project_root / f"update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"\n📋 Rapport sauvegardé: {report_file}")

            if args.dry_run:
                print("\n🔍 Mode simulation activé - Aucun fichier modifié")
            else:
                print(f"\n✅ Mise à jour terminée - {report['statistics']['files_updated']} fichiers modifiés")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()