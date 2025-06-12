#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur et validateur de docstrings pour les Agents IA.

Ce module analyse la qualité et la conformité des docstrings présentes
dans le code source, et génère des rapports détaillés sur :
- La couverture de documentation
- La conformité aux standards (Google/NumPy style)
- Les éléments manquants ou incorrects
- Des suggestions d'amélioration

Fonctionnalités principales :
- Scan automatique de tous les modules Python
- Validation syntaxique des docstrings
- Analyse de conformité aux standards
- Génération de rapports HTML/JSON
- Suggestions d'amélioration automatiques
- Intégration avec les outils de CI/CD

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: 03/06/2025
"""

import ast
import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, NamedTuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

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
logger = get_logger(__name__, log_file="docstring_analyzer.log")


class DocstringStyle(Enum):
    """Styles de docstrings supportés."""
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    UNKNOWN = "unknown"


@dataclass
class DocstringIssue:
    """
    Représente un problème détecté dans une docstring.

    Attributes:
        severity: Niveau de gravité (error, warning, info)
        category: Catégorie du problème (missing, format, content)
        message: Description du problème
        suggestion: Suggestion de correction
        line_number: Numéro de ligne où le problème a été détecté
    """
    severity: str
    category: str
    message: str
    suggestion: str = ""
    line_number: int = 0


@dataclass
class DocstringAnalysis:
    """
    Résultat de l'analyse d'une docstring.

    Attributes:
        has_docstring: Présence d'une docstring
        style: Style détecté (Google, NumPy, etc.)
        content: Contenu de la docstring
        sections: Sections détectées (Args, Returns, etc.)
        issues: Liste des problèmes détectés
        quality_score: Score de qualité (0-100)
    """
    has_docstring: bool
    style: DocstringStyle
    content: str = ""
    sections: Dict[str, str] = None
    issues: List[DocstringIssue] = None
    quality_score: int = 0

    def __post_init__(self):
        if self.sections is None:
            self.sections = {}
        if self.issues is None:
            self.issues = []


@dataclass
class ModuleAnalysis:
    """
    Résultat de l'analyse d'un module complet.

    Attributes:
        file_path: Chemin du fichier analysé
        module_docstring: Analyse de la docstring du module
        classes: Analyse des classes et leurs méthodes
        functions: Analyse des fonctions du module
        coverage: Pourcentage de couverture de documentation
        overall_score: Score global de qualité
    """
    file_path: str
    module_docstring: DocstringAnalysis
    classes: Dict[str, Dict[str, DocstringAnalysis]] = None
    functions: Dict[str, DocstringAnalysis] = None
    coverage: float = 0.0
    overall_score: int = 0

    def __post_init__(self):
        if self.classes is None:
            self.classes = {}
        if self.functions is None:
            self.functions = {}


class DocstringAnalyzer:
    """
    Analyseur principal de docstrings pour le projet IA.

    Cette classe fournit des outils complets pour analyser, valider
    et améliorer la documentation du code source.

    Attributes:
        project_root (Path): Racine du projet à analyser
        source_dirs (List[Path]): Répertoires contenant le code source
        standards (Dict): Règles et standards de documentation
        ignore_patterns (List[str]): Patterns de fichiers à ignorer
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialise l'analyseur de docstrings.

        Args:
            project_root: Racine du projet (auto-détectée si None)
        """
        self.project_root = self._find_project_root(project_root)
        self.source_dirs = self._discover_source_directories()
        self.standards = self._load_documentation_standards()
        self.ignore_patterns = [
            "__pycache__",
            ".pyc",
            "__init__.py",
            "test_*.py",
            "*_test.py"
        ]

        logger.info(f"DocstringAnalyzer initialisé pour: {self.project_root}")
        logger.debug(f"Répertoires source: {[str(d) for d in self.source_dirs]}")

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

    def _discover_source_directories(self) -> List[Path]:
        """
        Découvre automatiquement les répertoires contenant du code source.

        Returns:
            List[Path]: Liste des répertoires source trouvés
        """
        source_dirs = []

        candidate_dirs = [
            self.project_root / "agent_python" / "src",
            self.project_root / "agent_n8n" / "api",
            self.project_root / "shared" / "scripts"
        ]

        for dir_path in candidate_dirs:
            if dir_path.exists() and any(dir_path.glob("*.py")):
                source_dirs.append(dir_path)
                logger.debug(f"Répertoire source ajouté: {dir_path}")

        return source_dirs

    def _load_documentation_standards(self) -> Dict[str, Any]:
        """
        Charge les standards de documentation du projet.

        Returns:
            Dict: Standards et règles de documentation
        """
        return {
            'required_sections': {
                'module': ['description', 'author', 'version', 'date'],
                'class': ['description', 'attributes'],
                'function': ['description', 'args', 'returns'],
                'method': ['description', 'args', 'returns']
            },
            'google_style': {
                'sections': ['Args', 'Returns', 'Yields', 'Raises', 'Example', 'Note'],
                'patterns': {
                    'args': r'^\s*Args:\s*$',
                    'returns': r'^\s*Returns:\s*$',
                    'raises': r'^\s*Raises:\s*$'
                }
            },
            'quality_weights': {
                'has_docstring': 30,
                'has_description': 25,
                'has_args': 20,
                'has_returns': 15,
                'has_examples': 10
            },
            'min_description_words': 5,
            'author_pattern': r'Auteur:\s*(.+)',
            'version_pattern': r'Version:\s*(.+)',
            'date_pattern': r'Date:\s*(.+)'
        }

    def _should_ignore_file(self, file_path: Path) -> bool:
        """
        Détermine si un fichier doit être ignoré.

        Args:
            file_path: Chemin du fichier à vérifier

        Returns:
            bool: True si le fichier doit être ignoré
        """
        file_name = file_path.name
        return any(
            pattern in file_name or file_name.startswith(pattern.replace('*', ''))
            for pattern in self.ignore_patterns
        )

    def detect_docstring_style(self, docstring: str) -> DocstringStyle:
        """
        Détecte le style d'une docstring.

        Args:
            docstring: Contenu de la docstring

        Returns:
            DocstringStyle: Style détecté
        """
        if not docstring:
            return DocstringStyle.UNKNOWN

        # Patterns pour détecter le style Google
        google_patterns = [
            r'^\s*Args:\s*$',
            r'^\s*Returns:\s*$',
            r'^\s*Raises:\s*$',
            r'^\s*Example:\s*$',
            r'^\s*Note:\s*$'
        ]

        # Patterns pour détecter le style NumPy
        numpy_patterns = [
            r'^\s*Parameters\s*$',
            r'^\s*Returns\s*$',
            r'^\s*Raises\s*$',
            r'^\s*Examples\s*$',
            r'^\s*Notes\s*$'
        ]

        lines = docstring.split('\n')

        google_score = sum(1 for line in lines if any(re.match(p, line, re.MULTILINE) for p in google_patterns))
        numpy_score = sum(1 for line in lines if any(re.match(p, line, re.MULTILINE) for p in numpy_patterns))

        if google_score > numpy_score:
            return DocstringStyle.GOOGLE
        elif numpy_score > 0:
            return DocstringStyle.NUMPY
        else:
            return DocstringStyle.UNKNOWN

    def parse_google_docstring(self, docstring: str) -> Dict[str, str]:
        """
        Parse une docstring style Google.

        Args:
            docstring: Contenu de la docstring

        Returns:
            Dict[str, str]: Sections parsées
        """
        sections = {}
        current_section = "description"
        current_content = []

        lines = docstring.split('\n')

        for line in lines:
            # Détecter les sections Google
            if re.match(r'^\s*(Args|Arguments):\s*$', line):
                sections[current_section] = '\n'.join(current_content).strip()
                current_section = "args"
                current_content = []
            elif re.match(r'^\s*Returns:\s*$', line):
                sections[current_section] = '\n'.join(current_content).strip()
                current_section = "returns"
                current_content = []
            elif re.match(r'^\s*Raises:\s*$', line):
                sections[current_section] = '\n'.join(current_content).strip()
                current_section = "raises"
                current_content = []
            elif re.match(r'^\s*Example[s]?:\s*$', line):
                sections[current_section] = '\n'.join(current_content).strip()
                current_section = "examples"
                current_content = []
            elif re.match(r'^\s*Note[s]?:\s*$', line):
                sections[current_section] = '\n'.join(current_content).strip()
                current_section = "notes"
                current_content = []
            else:
                current_content.append(line)

        # Ajouter la dernière section
        sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def validate_docstring_content(self, docstring: str, element_type: str) -> List[DocstringIssue]:
        """
        Valide le contenu d'une docstring.

        Args:
            docstring: Contenu de la docstring
            element_type: Type d'élément (module, class, function, method)

        Returns:
            List[DocstringIssue]: Liste des problèmes détectés
        """
        issues = []

        if not docstring or len(docstring.strip()) == 0:
            issues.append(DocstringIssue(
                severity="error",
                category="missing",
                message=f"Docstring manquante pour {element_type}",
                suggestion="Ajoutez une docstring décrivant le but et l'utilisation"
            ))
            return issues

        # Analyser les sections
        style = self.detect_docstring_style(docstring)
        sections = self.parse_google_docstring(docstring) if style == DocstringStyle.GOOGLE else {}

        # Vérifier la description
        description = sections.get('description', '').strip()
        if not description:
            issues.append(DocstringIssue(
                severity="error",
                category="content",
                message="Description manquante",
                suggestion="Ajoutez une description claire du but et du fonctionnement"
            ))
        elif len(description.split()) < self.standards['min_description_words']:
            issues.append(DocstringIssue(
                severity="warning",
                category="content",
                message="Description trop courte",
                suggestion=f"Étoffez la description (minimum {self.standards['min_description_words']} mots)"
            ))

        # Vérifications spécifiques par type
        if element_type == 'module':
            self._validate_module_docstring(docstring, sections, issues)
        elif element_type in ['function', 'method']:
            self._validate_function_docstring(docstring, sections, issues)
        elif element_type == 'class':
            self._validate_class_docstring(docstring, sections, issues)

        return issues

    def _validate_module_docstring(self, docstring: str, sections: Dict[str, str], issues: List[DocstringIssue]):
        """
        Valide spécifiquement une docstring de module.

        Args:
            docstring: Contenu de la docstring
            sections: Sections parsées
            issues: Liste des problèmes à compléter
        """
        # Vérifier la présence des métadonnées obligatoires
        required_metadata = ['Auteur:', 'Version:', 'Date:']

        for metadata in required_metadata:
            if metadata not in docstring:
                issues.append(DocstringIssue(
                    severity="warning",
                    category="content",
                    message=f"Métadonnée manquante: {metadata}",
                    suggestion=f"Ajoutez '{metadata} votre_valeur'"
                ))

        # Vérifier le format de l'auteur
        author_match = re.search(self.standards['author_pattern'], docstring)
        if author_match and 'desmedt.franck@iaproject.fr' not in author_match.group(1):
            issues.append(DocstringIssue(
                severity="info",
                category="format",
                message="Format d'auteur non conforme au standard du projet",
                suggestion="Utilisez: Auteur: desmedt.franck@iaproject.fr"
            ))

    def _validate_function_docstring(self, docstring: str, sections: Dict[str, str], issues: List[DocstringIssue]):
        """
        Valide spécifiquement une docstring de fonction.

        Args:
            docstring: Contenu de la docstring
            sections: Sections parsées
            issues: Liste des problèmes à compléter
        """
        # Vérifier la section Args si la fonction semble avoir des paramètres
        if 'args' not in sections or not sections['args'].strip():
            issues.append(DocstringIssue(
                severity="warning",
                category="content",
                message="Section Args manquante ou vide",
                suggestion="Documentez tous les paramètres avec leur type et description"
            ))

        # Vérifier la section Returns
        if 'returns' not in sections or not sections['returns'].strip():
            issues.append(DocstringIssue(
                severity="warning",
                category="content",
                message="Section Returns manquante ou vide",
                suggestion="Documentez la valeur de retour avec son type et sa description"
            ))

    def _validate_class_docstring(self, docstring: str, sections: Dict[str, str], issues: List[DocstringIssue]):
        """
        Valide spécifiquement une docstring de classe.

        Args:
            docstring: Contenu de la docstring
            sections: Sections parsées
            issues: Liste des problèmes à compléter
        """
        # Vérifier la section Attributes
        if 'Attributes:' not in docstring and 'attributes' not in sections:
            issues.append(DocstringIssue(
                severity="info",
                category="content",
                message="Section Attributes manquante",
                suggestion="Documentez les attributs principaux de la classe"
            ))

    def calculate_quality_score(self, analysis: DocstringAnalysis) -> int:
        """
        Calcule un score de qualité pour une docstring.

        Args:
            analysis: Analyse de la docstring

        Returns:
            int: Score de qualité (0-100)
        """
        if not analysis.has_docstring:
            return 0

        score = 0
        weights = self.standards['quality_weights']

        # Points pour avoir une docstring
        score += weights['has_docstring']

        # Points pour la description
        if analysis.sections.get('description', '').strip():
            score += weights['has_description']

        # Points pour la documentation des arguments
        if analysis.sections.get('args', '').strip():
            score += weights['has_args']

        # Points pour la documentation du retour
        if analysis.sections.get('returns', '').strip():
            score += weights['has_returns']

        # Points pour les exemples
        if analysis.sections.get('examples', '').strip():
            score += weights['has_examples']

        # Malus pour les problèmes
        error_count = sum(1 for issue in analysis.issues if issue.severity == 'error')
        warning_count = sum(1 for issue in analysis.issues if issue.severity == 'warning')

        score -= error_count * 10
        score -= warning_count * 5

        return max(0, min(100, score))

    def analyze_docstring(self, docstring: str, element_type: str) -> DocstringAnalysis:
        """
        Analyse complète d'une docstring.

        Args:
            docstring: Contenu de la docstring
            element_type: Type d'élément (module, class, function, method)

        Returns:
            DocstringAnalysis: Résultat de l'analyse
        """
        has_docstring = bool(docstring and docstring.strip())

        analysis = DocstringAnalysis(
            has_docstring=has_docstring,
            style=self.detect_docstring_style(docstring) if has_docstring else DocstringStyle.UNKNOWN,
            content=docstring or ""
        )

        if has_docstring:
            analysis.sections = self.parse_google_docstring(docstring)
            analysis.issues = self.validate_docstring_content(docstring, element_type)

        analysis.quality_score = self.calculate_quality_score(analysis)

        return analysis

    def analyze_module(self, file_path: Path) -> ModuleAnalysis:
        """
        Analyse complète d'un module Python.

        Args:
            file_path: Chemin vers le fichier Python

        Returns:
            ModuleAnalysis: Résultat de l'analyse du module
        """
        logger.debug(f"Analyse du module: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Analyse de la docstring du module
            module_docstring = ast.get_docstring(tree)
            module_analysis = self.analyze_docstring(module_docstring, 'module')

            # Initialiser l'analyse du module
            analysis = ModuleAnalysis(
                file_path=str(file_path),
                module_docstring=module_analysis
            )

            # Analyser les classes et leurs méthodes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_docstring = ast.get_docstring(node)
                    class_analysis = self.analyze_docstring(class_docstring, 'class')

                    # Analyser les méthodes de la classe
                    methods = {}
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_docstring = ast.get_docstring(item)
                            method_analysis = self.analyze_docstring(method_docstring, 'method')
                            methods[item.name] = method_analysis

                    analysis.classes[node.name] = {
                        'class': class_analysis,
                        'methods': methods
                    }

                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    # Fonctions au niveau module
                    function_docstring = ast.get_docstring(node)
                    function_analysis = self.analyze_docstring(function_docstring, 'function')
                    analysis.functions[node.name] = function_analysis

            # Calculer les métriques globales
            self._calculate_module_metrics(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {file_path}: {e}")
            # Retourner une analyse avec erreur
            return ModuleAnalysis(
                file_path=str(file_path),
                module_docstring=DocstringAnalysis(has_docstring=False, style=DocstringStyle.UNKNOWN)
            )

    def _calculate_module_metrics(self, analysis: ModuleAnalysis):
        """
        Calcule les métriques globales d'un module.

        Args:
            analysis: Analyse du module à compléter
        """
        # Compter les éléments documentés
        total_elements = 1  # Module lui-même
        documented_elements = 1 if analysis.module_docstring.has_docstring else 0

        # Ajouter les fonctions
        total_elements += len(analysis.functions)
        documented_elements += sum(1 for func in analysis.functions.values() if func.has_docstring)

        # Ajouter les classes et leurs méthodes
        for class_name, class_data in analysis.classes.items():
            total_elements += 1  # La classe elle-même
            if class_data['class'].has_docstring:
                documented_elements += 1

            # Méthodes de la classe
            methods = class_data.get('methods', {})
            total_elements += len(methods)
            documented_elements += sum(1 for method in methods.values() if method.has_docstring)

        # Calculer la couverture
        analysis.coverage = (documented_elements / total_elements * 100) if total_elements > 0 else 0

        # Calculer le score global (moyenne pondérée)
        scores = [analysis.module_docstring.quality_score]
        scores.extend(func.quality_score for func in analysis.functions.values())

        for class_data in analysis.classes.values():
            scores.append(class_data['class'].quality_score)
            scores.extend(method.quality_score for method in class_data.get('methods', {}).values())

        analysis.overall_score = int(sum(scores) / len(scores)) if scores else 0

    def analyze_project(self) -> Dict[str, ModuleAnalysis]:
        """
        Analyse complète du projet.

        Returns:
            Dict[str, ModuleAnalysis]: Résultats d'analyse par module
        """
        logger.info("🔍 Analyse complète du projet...")

        results = {}
        total_files = 0

        for source_dir in self.source_dirs:
            logger.debug(f"Analyse du répertoire: {source_dir}")

            for py_file in source_dir.rglob("*.py"):
                if self._should_ignore_file(py_file):
                    logger.debug(f"Fichier ignoré: {py_file}")
                    continue

                total_files += 1
                relative_path = str(py_file.relative_to(self.project_root))
                results[relative_path] = self.analyze_module(py_file)

        logger.info(f"✅ Analyse terminée - {total_files} fichiers traités")
        return results

    def generate_report(self, results: Dict[str, ModuleAnalysis], output_format: str = 'html') -> Path:
        """
        Génère un rapport d'analyse.

        Args:
            results: Résultats d'analyse
            output_format: Format de sortie (html, json, text)

        Returns:
            Path: Chemin vers le fichier de rapport généré
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = self.project_root / "docs_generated" / "docstring_analysis"
        output_dir.mkdir(parents=True, exist_ok=True)

        if output_format == 'html':
            return self._generate_html_report(results, output_dir, timestamp)
        elif output_format == 'json':
            return self._generate_json_report(results, output_dir, timestamp)
        else:
            return self._generate_text_report(results, output_dir, timestamp)

    def _generate_html_report(self, results: Dict[str, ModuleAnalysis], output_dir: Path, timestamp: str) -> Path:
        """
        Génère un rapport HTML détaillé.

        Args:
            results: Résultats d'analyse
            output_dir: Répertoire de sortie
            timestamp: Horodatage pour le nom du fichier

        Returns:
            Path: Chemin vers le rapport HTML généré
        """
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Analyse des Docstrings - Agent IA</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .metric-label {{ color: #7f8c8d; margin-top: 5px; }}
        .module {{ margin: 20px 0; padding: 20px; border: 1px solid #bdc3c7; border-radius: 8px; }}
        .module-header {{ background: #34495e; color: white; padding: 10px; margin: -20px -20px 20px -20px; border-radius: 8px 8px 0 0; }}
        .score {{ padding: 5px 10px; border-radius: 20px; color: white; font-weight: bold; }}
        .score-high {{ background: #27ae60; }}
        .score-medium {{ background: #f39c12; }}
        .score-low {{ background: #e74c3c; }}
        .issues {{ margin-top: 15px; }}
        .issue {{ margin: 5px 0; padding: 10px; border-radius: 5px; }}
        .issue-error {{ background: #ffe6e6; border-left: 4px solid #e74c3c; }}
        .issue-warning {{ background: #fff3cd; border-left: 4px solid #f39c12; }}
        .issue-info {{ background: #e6f3ff; border-left: 4px solid #3498db; }}
        .navigation {{ margin: 20px 0; }}
        .nav-button {{ display: inline-block; padding: 10px 20px; margin: 5px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }}
        .nav-button:hover {{ background: #2980b9; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Rapport d'Analyse des Docstrings</h1>
        <p><strong>Généré le:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
        <p><strong>Projet:</strong> Agent IA - Recherche Offres</p>
"""

        # Calculer les statistiques globales
        total_modules = len(results)
        total_coverage = sum(r.coverage for r in results.values()) / total_modules if total_modules > 0 else 0
        avg_score = sum(r.overall_score for r in results.values()) / total_modules if total_modules > 0 else 0
        total_issues = sum(len(r.module_docstring.issues) for r in results.values())

        html_content += f"""
        <div class="summary">
            <div class="metric">
                <div class="metric-value">{total_modules}</div>
                <div class="metric-label">Modules analysés</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_coverage:.1f}%</div>
                <div class="metric-label">Couverture moyenne</div>
            </div>
            <div class="metric">
                <div class="metric-value">{avg_score:.0f}</div>
                <div class="metric-label">Score qualité moyen</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_issues}</div>
                <div class="metric-label">Problèmes détectés</div>
            </div>
        </div>

        <div class="navigation">
            <a href="#summary" class="nav-button">Résumé</a>
            <a href="#modules" class="nav-button">Modules détaillés</a>
            <a href="#recommendations" class="nav-button">Recommandations</a>
        </div>

        <h2 id="modules">📂 Analyse par Module</h2>
"""

        # Détails par module
        for module_path, analysis in results.items():
            score_class = 'score-high' if analysis.overall_score >= 80 else 'score-medium' if analysis.overall_score >= 60 else 'score-low'

            html_content += f"""
        <div class="module">
            <div class="module-header">
                <h3>{module_path}</h3>
                <span class="score {score_class}">Score: {analysis.overall_score}/100</span>
                <span class="score score-medium">Couverture: {analysis.coverage:.1f}%</span>
            </div>
"""

            # Problèmes du module
            if analysis.module_docstring.issues:
                html_content += "<div class='issues'><h4>Problèmes détectés:</h4>"
                for issue in analysis.module_docstring.issues:
                    issue_class = f"issue-{issue.severity}"
                    html_content += f"""
                <div class="issue {issue_class}">
                    <strong>{issue.severity.title()}:</strong> {issue.message}
                    {f'<br><em>Suggestion:</em> {issue.suggestion}' if issue.suggestion else ''}
                </div>"""
                html_content += "</div>"

            html_content += "</div>"

        # Recommandations
        html_content += """
        <h2 id="recommendations">💡 Recommandations</h2>
        <div class="recommendations">
            <h3>Améliorations prioritaires:</h3>
            <ul>
                <li>Ajoutez des docstrings aux éléments non documentés</li>
                <li>Complétez les sections Args et Returns pour les fonctions</li>
                <li>Ajoutez les métadonnées obligatoires (Auteur, Version, Date) aux modules</li>
                <li>Utilisez le style Google de façon cohérente</li>
                <li>Ajoutez des exemples d'utilisation pour les fonctions complexes</li>
            </ul>
        </div>
    </div>
</body>
</html>"""

        report_file = output_dir / f"docstring_report_{timestamp}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"📊 Rapport HTML généré: {report_file}")
        return report_file

    def _generate_json_report(self, results: Dict[str, ModuleAnalysis], output_dir: Path, timestamp: str) -> Path:
        """
        Génère un rapport JSON pour intégration CI/CD.

        Args:
            results: Résultats d'analyse
            output_dir: Répertoire de sortie
            timestamp: Horodatage pour le nom du fichier

        Returns:
            Path: Chemin vers le rapport JSON généré
        """
        # Convertir les résultats en format JSON-friendly
        json_data = {
            'generated_at': datetime.now().isoformat(),
            'project': 'Agent IA - Recherche Offres',
            'summary': {
                'total_modules': len(results),
                'average_coverage': sum(r.coverage for r in results.values()) / len(results) if results else 0,
                'average_score': sum(r.overall_score for r in results.values()) / len(results) if results else 0,
                'total_issues': sum(len(r.module_docstring.issues) for r in results.values())
            },
            'modules': {}
        }

        for module_path, analysis in results.items():
            json_data['modules'][module_path] = {
                'coverage': analysis.coverage,
                'overall_score': analysis.overall_score,
                'module_docstring': {
                    'has_docstring': analysis.module_docstring.has_docstring,
                    'style': analysis.module_docstring.style.value,
                    'quality_score': analysis.module_docstring.quality_score,
                    'issues': [
                        {
                            'severity': issue.severity,
                            'category': issue.category,
                            'message': issue.message,
                            'suggestion': issue.suggestion
                        }
                        for issue in analysis.module_docstring.issues
                    ]
                }
            }

        report_file = output_dir / f"docstring_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Rapport JSON généré: {report_file}")
        return report_file

    def _generate_text_report(self, results: Dict[str, ModuleAnalysis], output_dir: Path, timestamp: str) -> Path:
        """
        Génère un rapport texte simple.

        Args:
            results: Résultats d'analyse
            output_dir: Répertoire de sortie
            timestamp: Horodatage pour le nom du fichier

        Returns:
            Path: Chemin vers le rapport texte généré
        """
        report_content = f"""
RAPPORT D'ANALYSE DES DOCSTRINGS
===============================

Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
Projet: Agent IA - Recherche Offres

RÉSUMÉ EXÉCUTIF
===============
Modules analysés: {len(results)}
Couverture moyenne: {sum(r.coverage for r in results.values()) / len(results) if results else 0:.1f}%
Score qualité moyen: {sum(r.overall_score for r in results.values()) / len(results) if results else 0:.0f}/100
Problèmes détectés: {sum(len(r.module_docstring.issues) for r in results.values())}

DÉTAILS PAR MODULE
==================
"""

        for module_path, analysis in results.items():
            report_content += f"""
{module_path}
{'-' * len(module_path)}
Score: {analysis.overall_score}/100
Couverture: {analysis.coverage:.1f}%
Problèmes: {len(analysis.module_docstring.issues)}

"""

            if analysis.module_docstring.issues:
                for issue in analysis.module_docstring.issues:
                    report_content += f"  • {issue.severity.upper()}: {issue.message}\n"
                    if issue.suggestion:
                        report_content += f"    Suggestion: {issue.suggestion}\n"
                report_content += "\n"

        report_file = output_dir / f"docstring_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"📊 Rapport texte généré: {report_file}")
        return report_file


def main():
    """
    Fonction principale pour l'exécution en ligne de commande.

    Permet de lancer l'analyse des docstrings avec différents paramètres
    et de générer des rapports dans différents formats.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyseur de docstrings pour les Agents IA",
        epilog="""
Exemples d'utilisation:
  %(prog)s                                    # Analyse complète avec rapport HTML
  %(prog)s --format json                      # Rapport JSON pour CI/CD
  %(prog)s --project-root /path/to/project    # Projet spécifique
  %(prog)s --log-level DEBUG                  # Mode debug détaillé
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--project-root',
        type=str,
        help="Racine du projet à analyser (auto-détectée si non spécifié)"
    )

    parser.add_argument(
        '--format',
        choices=['html', 'json', 'text'],
        default='html',
        help="Format du rapport de sortie (défaut: html)"
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help="Niveau de logging (défaut: INFO)"
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        help="Répertoire de sortie pour les rapports (défaut: docs_generated/docstring_analysis)"
    )

    args = parser.parse_args()

    # Configurer le logging
    import logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    try:
        # Créer l'analyseur
        project_root = Path(args.project_root) if args.project_root else None
        analyzer = DocstringAnalyzer(project_root=project_root)

        # Analyser le projet
        results = analyzer.analyze_project()

        # Générer le rapport
        report_file = analyzer.generate_report(results, args.format)

        # Afficher les résultats
        total_modules = len(results)
        avg_coverage = sum(r.coverage for r in results.values()) / total_modules if total_modules > 0 else 0
        avg_score = sum(r.overall_score for r in results.values()) / total_modules if total_modules > 0 else 0

        print(f"\n🎉 Analyse terminée !")
        print(f"📁 Modules analysés: {total_modules}")
        print(f"📊 Couverture moyenne: {avg_coverage:.1f}%")
        print(f"⭐ Score qualité moyen: {avg_score:.0f}/100")
        print(f"📋 Rapport généré: {report_file}")

        if args.format == 'html':
            print(f"🌐 Ouvrir le rapport: file://{report_file}")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()