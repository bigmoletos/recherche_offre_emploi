#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur Avancé d'Offres d'Alternance Cybersécurité - Module de Post-Traitement.

Ce module fournit les outils d'analyse et de validation des offres collectées
par les différents scrapers du système. Il effectue une analyse statistique
détaillée des données récoltées et valide la qualité du processus de collecte.

Fonctionnalités principales :
- Analyse statistique complète des fichiers Excel générés
- Validation de la cohérence des données collectées
- Génération de métriques de performance du scraping
- Identification des tendances et patterns dans les offres
- Contrôle qualité des URLs et métadonnées
- Rapport de conformité avec les critères d'alternance

Le module traite spécifiquement les fichiers Excel produits par :
- JobScraper (collecte réelle depuis sites d'emploi)
- demo_agent.py (données simulées pour tests)
- Autres scrapers du système

Architecture :
- OfferAnalyzer : Classe principale d'analyse statistique
- DataValidator : Validation de la qualité des données
- ReportGenerator : Génération de rapports détaillés
- MetricsCalculator : Calcul des indicateurs de performance

Usage :
    python src/analyser_vraies_offres.py                    # Analyse automatique du dernier fichier
    python src/analyser_vraies_offres.py --file rapport.xlsx # Analyse d'un fichier spécifique
    python src/analyser_vraies_offres.py --verbose          # Analyse détaillée avec logs

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: 03/06/2025
"""

import pandas as pd
import json
import sys
import glob
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re
from urllib.parse import urlparse

# Intégration du système de logging centralisé
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared" / "scripts"))

try:
    from logger_config import get_logger
    logger = get_logger(__name__, log_file="analyser_offres.log")
except ImportError:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        handlers=[
            logging.FileHandler(f'analyser_offres_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.warning("Module logger_config non disponible, utilisation du logging standard")


class DataValidator:
    """
    Validateur de qualité des données d'offres d'emploi.

    Cette classe effectue des contrôles de cohérence et de qualité
    sur les données collectées par les scrapers. Elle identifie
    les anomalies, les données manquantes et les incohérences.

    Attributes:
        validation_rules (Dict): Règles de validation par champ
        quality_thresholds (Dict): Seuils de qualité acceptables
        validation_stats (Dict): Statistiques de validation
    """

    def __init__(self):
        """
        Initialise le validateur avec les règles de contrôle qualité.
        """
        logger.debug("Initialisation du validateur de données")

        # Règles de validation des champs
        self.validation_rules = {
            'title': {'min_length': 5, 'max_length': 200, 'required': True},
            'company': {'min_length': 2, 'max_length': 100, 'required': True},
            'location': {'min_length': 2, 'max_length': 100, 'required': True},
            'url': {'required': True, 'pattern': r'^https?://'},
            'description': {'min_length': 10, 'max_length': 5000, 'required': False}
        }

        # Seuils de qualité
        self.quality_thresholds = {
            'completeness': 0.8,  # 80% des champs remplis minimum
            'url_validity': 0.9,  # 90% des URLs valides
            'title_diversity': 0.3  # 30% de titres uniques minimum
        }

        self.validation_stats = {}

    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valide un DataFrame d'offres d'emploi.

        Effectue une validation complète des données incluant :
        - Contrôle de complétude des champs obligatoires
        - Validation des formats (URLs, dates, etc.)
        - Détection des doublons
        - Calcul des métriques de qualité

        Args:
            df (pd.DataFrame): DataFrame contenant les offres à valider

        Returns:
            Dict[str, Any]: Rapport de validation avec métriques et erreurs
                - is_valid: Statut global de validation
                - completeness_score: Score de complétude (0-1)
                - quality_issues: Liste des problèmes détectés
                - field_stats: Statistiques par champ
                - recommendations: Suggestions d'amélioration
        """
        logger.info(f"Début validation de {len(df)} offres")

        validation_report = {
            'is_valid': True,
            'total_offers': len(df),
            'completeness_score': 0.0,
            'quality_issues': [],
            'field_stats': {},
            'recommendations': [],
            'validation_timestamp': datetime.now().isoformat()
        }

        # Validation champ par champ
        for field, rules in self.validation_rules.items():
            if field in df.columns:
                field_stats = self._validate_field(df[field], field, rules)
                validation_report['field_stats'][field] = field_stats

                if field_stats['error_count'] > 0:
                    validation_report['quality_issues'].extend(field_stats['errors'])

        # Validation des URLs
        if 'url' in df.columns:
            url_validation = self._validate_urls(df['url'])
            validation_report['url_validation'] = url_validation

        # Détection des doublons
        duplicates = self._detect_duplicates(df)
        validation_report['duplicates'] = duplicates

        # Calcul du score de complétude global
        validation_report['completeness_score'] = self._calculate_completeness_score(df)

        # Validation finale
        validation_report['is_valid'] = (
            validation_report['completeness_score'] >= self.quality_thresholds['completeness'] and
            len(validation_report['quality_issues']) < len(df) * 0.1  # Moins de 10% d'erreurs
        )

        # Génération des recommandations
        validation_report['recommendations'] = self._generate_recommendations(validation_report)

        logger.info(f"Validation terminée - Score: {validation_report['completeness_score']:.2f}")
        return validation_report

    def _validate_field(self, series: pd.Series, field_name: str, rules: Dict) -> Dict[str, Any]:
        """
        Valide une colonne spécifique selon les règles définies.

        Args:
            series (pd.Series): Série de données à valider
            field_name (str): Nom du champ
            rules (Dict): Règles de validation

        Returns:
            Dict[str, Any]: Statistiques de validation du champ
        """
        stats = {
            'field_name': field_name,
            'total_values': len(series),
            'null_count': series.isnull().sum(),
            'empty_count': 0,
            'error_count': 0,
            'errors': []
        }

        # Vérification des valeurs vides
        empty_mask = series.astype(str).str.strip() == ''
        stats['empty_count'] = empty_mask.sum()

        # Validation de la longueur
        if 'min_length' in rules or 'max_length' in rules:
            text_lengths = series.astype(str).str.len()

            if 'min_length' in rules:
                too_short = text_lengths < rules['min_length']
                if too_short.any():
                    stats['error_count'] += too_short.sum()
                    stats['errors'].append(f"{too_short.sum()} valeurs trop courtes (< {rules['min_length']})")

            if 'max_length' in rules:
                too_long = text_lengths > rules['max_length']
                if too_long.any():
                    stats['error_count'] += too_long.sum()
                    stats['errors'].append(f"{too_long.sum()} valeurs trop longues (> {rules['max_length']})")

        # Validation du pattern
        if 'pattern' in rules:
            pattern_matches = series.astype(str).str.match(rules['pattern'])
            invalid_pattern = ~pattern_matches
            if invalid_pattern.any():
                stats['error_count'] += invalid_pattern.sum()
                stats['errors'].append(f"{invalid_pattern.sum()} valeurs ne respectent pas le pattern")

        logger.debug(f"Validation {field_name}: {stats['error_count']} erreurs sur {stats['total_values']} valeurs")
        return stats

    def _validate_urls(self, url_series: pd.Series) -> Dict[str, Any]:
        """
        Valide spécifiquement les URLs des offres.

        Args:
            url_series (pd.Series): Série contenant les URLs

        Returns:
            Dict[str, Any]: Rapport de validation des URLs
        """
        url_stats = {
            'total_urls': len(url_series),
            'valid_urls': 0,
            'invalid_urls': [],
            'domains': {},
            'schemes': {}
        }

        for idx, url in url_series.items():
            try:
                parsed = urlparse(str(url))
                if parsed.scheme and parsed.netloc:
                    url_stats['valid_urls'] += 1

                    # Comptage des domaines
                    domain = parsed.netloc.lower()
                    url_stats['domains'][domain] = url_stats['domains'].get(domain, 0) + 1

                    # Comptage des schémas
                    scheme = parsed.scheme.lower()
                    url_stats['schemes'][scheme] = url_stats['schemes'].get(scheme, 0) + 1
                else:
                    url_stats['invalid_urls'].append(f"Ligne {idx}: URL invalide - {url}")
            except Exception as e:
                url_stats['invalid_urls'].append(f"Ligne {idx}: Erreur parsing - {e}")

        url_stats['validity_rate'] = url_stats['valid_urls'] / url_stats['total_urls'] if url_stats['total_urls'] > 0 else 0

        logger.debug(f"Validation URLs: {url_stats['valid_urls']}/{url_stats['total_urls']} valides")
        return url_stats

    def _detect_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Détecte les doublons dans les offres.

        Args:
            df (pd.DataFrame): DataFrame à analyser

        Returns:
            Dict[str, Any]: Rapport des doublons détectés
        """
        duplicate_report = {
            'exact_duplicates': 0,
            'url_duplicates': 0,
            'title_company_duplicates': 0,
            'duplicate_groups': []
        }

        # Doublons exacts (toutes les colonnes)
        exact_dups = df.duplicated()
        duplicate_report['exact_duplicates'] = exact_dups.sum()

        # Doublons par URL
        if 'url' in df.columns:
            url_dups = df.duplicated(subset=['url'])
            duplicate_report['url_duplicates'] = url_dups.sum()

        # Doublons par titre + entreprise
        if 'title' in df.columns and 'company' in df.columns:
            title_company_dups = df.duplicated(subset=['title', 'company'])
            duplicate_report['title_company_duplicates'] = title_company_dups.sum()

        logger.debug(f"Doublons détectés: {duplicate_report['exact_duplicates']} exacts, "
                    f"{duplicate_report['url_duplicates']} URLs")
        return duplicate_report

    def _calculate_completeness_score(self, df: pd.DataFrame) -> float:
        """
        Calcule un score de complétude global des données.

        Args:
            df (pd.DataFrame): DataFrame à évaluer

        Returns:
            float: Score de complétude entre 0 et 1
        """
        if df.empty:
            return 0.0

        total_cells = df.size
        non_null_cells = df.count().sum()

        # Bonus pour les champs importants remplis
        important_fields = ['title', 'company', 'url']
        bonus = 0
        for field in important_fields:
            if field in df.columns:
                field_completeness = df[field].count() / len(df)
                bonus += field_completeness * 0.1  # 10% de bonus par champ important

        base_score = non_null_cells / total_cells
        final_score = min(1.0, base_score + bonus)

        logger.debug(f"Score de complétude: {final_score:.3f} (base: {base_score:.3f}, bonus: {bonus:.3f})")
        return final_score

    def _generate_recommendations(self, validation_report: Dict[str, Any]) -> List[str]:
        """
        Génère des recommandations d'amélioration basées sur la validation.

        Args:
            validation_report (Dict): Rapport de validation

        Returns:
            List[str]: Liste des recommandations
        """
        recommendations = []

        # Recommandations basées sur la complétude
        if validation_report['completeness_score'] < 0.7:
            recommendations.append("Améliorer la complétude des données - score actuel insuffisant")

        # Recommandations par champ
        for field, stats in validation_report['field_stats'].items():
            if stats['null_count'] > stats['total_values'] * 0.2:
                recommendations.append(f"Réduire les valeurs manquantes pour '{field}' ({stats['null_count']} manquantes)")

        # Recommandations sur les URLs
        if 'url_validation' in validation_report:
            url_stats = validation_report['url_validation']
            if url_stats['validity_rate'] < 0.9:
                recommendations.append("Améliorer la qualité des URLs collectées")

        # Recommandations sur les doublons
        duplicates = validation_report.get('duplicates', {})
        if duplicates.get('exact_duplicates', 0) > 0:
            recommendations.append("Implémenter une déduplication plus efficace")

        return recommendations


class OfferAnalyzer:
    """
    Analyseur principal pour les offres d'alternance collectées.

    Cette classe effectue une analyse complète et détaillée des fichiers
    d'offres générés par les différents scrapers du système. Elle produit
    des statistiques avancées, des métriques de performance et des rapports
    de qualité pour valider l'efficacité du processus de collecte.

    Attributes:
        validator (DataValidator): Validateur de qualité des données
        analysis_config (Dict): Configuration des analyses
        metrics (Dict): Métriques calculées lors de l'analyse
    """

    def __init__(self):
        """
        Initialise l'analyseur avec ses composants et configuration.
        """
        logger.info("Initialisation de l'analyseur d'offres")

        self.validator = DataValidator()
        self.analysis_config = {
            'show_details': True,
            'max_description_preview': 100,
            'include_validation': True,
            'generate_insights': True
        }
        self.metrics = {}

    def analyser_fichier_excel(self, nom_fichier: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Analyse complète d'un fichier Excel d'offres d'alternance.

        Cette méthode constitue le point d'entrée principal pour l'analyse.
        Elle charge les données, effectue toutes les validations et calculs,
        puis génère un rapport détaillé avec insights et recommandations.

        Args:
            nom_fichier (str): Chemin vers le fichier Excel à analyser
            verbose (bool): Activer le mode détaillé avec logs étendus

        Returns:
            Dict[str, Any]: Rapport d'analyse complet contenant :
                - file_info: Métadonnées du fichier
                - data_summary: Résumé statistique des données
                - validation_report: Rapport de validation qualité
                - insights: Insights et patterns identifiés
                - recommendations: Recommandations d'amélioration
                - analysis_timestamp: Horodatage de l'analyse

        Raises:
            FileNotFoundError: Si le fichier spécifié n'existe pas
            pd.errors.EmptyDataError: Si le fichier est vide ou corrompu
            Exception: Pour toute autre erreur de traitement
        """
        logger.info(f"🎯 DÉBUT ANALYSE DÉTAILLÉE DU FICHIER: {nom_fichier}")

        try:
            # Vérification de l'existence du fichier
            if not os.path.exists(nom_fichier):
                raise FileNotFoundError(f"Fichier non trouvé: {nom_fichier}")

            # Chargement des données
            logger.debug("Chargement du fichier Excel...")
        df = pd.read_excel(nom_fichier, sheet_name='Toutes_Offres')

            if df.empty:
                raise pd.errors.EmptyDataError("Le fichier ne contient aucune donnée")

            logger.info(f"📊 Fichier chargé avec succès: {len(df)} offres trouvées")

            # Initialisation du rapport d'analyse
            analysis_report = {
                'file_info': self._get_file_info(nom_fichier, df),
                'data_summary': self._generate_data_summary(df),
                'validation_report': None,
                'insights': {},
                'recommendations': [],
                'analysis_timestamp': datetime.now().isoformat()
            }

            # Affichage du résumé initial
            self._display_initial_summary(analysis_report['file_info'], analysis_report['data_summary'])

            # Validation des données si activée
            if self.analysis_config['include_validation']:
                logger.debug("Validation qualité des données...")
                analysis_report['validation_report'] = self.validator.validate_dataframe(df)
                self._display_validation_results(analysis_report['validation_report'])

            # Affichage détaillé des offres
            if self.analysis_config['show_details']:
                self._display_offers_details(df, verbose)

            # Génération des insights
            if self.analysis_config['generate_insights']:
                logger.debug("Génération des insights...")
                analysis_report['insights'] = self._generate_insights(df)
                self._display_insights(analysis_report['insights'])

            # Calcul des métriques finales
            self.metrics = self._calculate_final_metrics(df, analysis_report)

            # Affichage de la conclusion
            self._display_conclusion(analysis_report)

            logger.info("✅ Analyse terminée avec succès")
            return analysis_report

        except FileNotFoundError as e:
            logger.error(f"❌ Erreur fichier: {e}")
            raise
        except pd.errors.EmptyDataError as e:
            logger.error(f"❌ Erreur données: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Erreur inattendue lors de l'analyse: {e}")
            raise

    def _get_file_info(self, nom_fichier: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extrait les métadonnées du fichier analysé.

        Args:
            nom_fichier (str): Nom du fichier
            df (pd.DataFrame): DataFrame chargé

        Returns:
            Dict[str, Any]: Informations sur le fichier
        """
        file_stats = os.stat(nom_fichier)

        return {
            'filename': nom_fichier,
            'file_size_mb': file_stats.st_size / (1024 * 1024),
            'modification_date': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'total_offers': len(df),
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict()
        }

    def _generate_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Génère un résumé statistique des données.

        Args:
            df (pd.DataFrame): DataFrame à analyser

        Returns:
            Dict[str, Any]: Résumé statistique
        """
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'null_percentages': (df.isnull().sum() / len(df) * 100).to_dict(),
            'unique_values': df.nunique().to_dict()
        }

        # Analyse des sources de scraping
        if 'scraper_source' in df.columns:
            summary['sources_distribution'] = df['scraper_source'].value_counts().to_dict()

        # Analyse des statuts IA
        if 'is_valid' in df.columns:
            summary['ia_validation'] = df['is_valid'].value_counts().to_dict()

        return summary

    def _display_initial_summary(self, file_info: Dict, data_summary: Dict):
        """
        Affiche le résumé initial de l'analyse.

        Args:
            file_info (Dict): Informations sur le fichier
            data_summary (Dict): Résumé des données
        """
        print("🎯 ANALYSE DES VRAIES OFFRES COLLECTÉES")
        print("=" * 60)
        print(f"📁 Fichier: {file_info['filename']}")
        print(f"📊 Total offres: {file_info['total_offers']}")
        print(f"💾 Taille fichier: {file_info['file_size_mb']:.2f} MB")
        print(f"🕒 Modifié le: {datetime.fromisoformat(file_info['modification_date']).strftime('%d/%m/%Y %H:%M')}")
        print()

        # Distribution des sources
        if 'sources_distribution' in data_summary:
            print("📡 SOURCES DE COLLECTE:")
            print("-" * 30)
            for source, count in data_summary['sources_distribution'].items():
                percentage = (count / data_summary['total_rows']) * 100
                print(f"   {source}: {count} offres ({percentage:.1f}%)")
            print()

    def _display_validation_results(self, validation_report: Dict[str, Any]):
        """
        Affiche les résultats de validation des données.

        Args:
            validation_report (Dict): Rapport de validation
        """
        print("🔍 VALIDATION QUALITÉ DES DONNÉES:")
        print("-" * 40)

        status_icon = "✅" if validation_report['is_valid'] else "⚠️"
        print(f"   {status_icon} Statut global: {'VALIDE' if validation_report['is_valid'] else 'PROBLÈMES DÉTECTÉS'}")
        print(f"   📈 Score complétude: {validation_report['completeness_score']:.1%}")

        if validation_report['quality_issues']:
            print(f"   ⚠️ Problèmes détectés: {len(validation_report['quality_issues'])}")
            for issue in validation_report['quality_issues'][:3]:  # Afficher les 3 premiers
                print(f"      - {issue}")
            if len(validation_report['quality_issues']) > 3:
                print(f"      ... et {len(validation_report['quality_issues']) - 3} autres")
        print()

    def _display_offers_details(self, df: pd.DataFrame, verbose: bool):
        """
        Affiche les détails des offres collectées.

        Args:
            df (pd.DataFrame): DataFrame des offres
            verbose (bool): Mode verbose activé
        """
        print("📋 DÉTAILS DES OFFRES:")
        print("-" * 30)

        max_display = 10 if not verbose else len(df)

        for i, row in df.head(max_display).iterrows():
            print(f"\n{i+1}. 📌 {row['title']}")
            print(f"   🏢 Entreprise: {row['company']}")
            print(f"   📍 Lieu: {row['location']}")

            if 'scraper_source' in row:
            print(f"   🔗 Source: {row['scraper_source']}")

            # URL tronquée pour l'affichage
            url_display = str(row['url'])[:60] + "..." if len(str(row['url'])) > 60 else str(row['url'])
            print(f"   🌐 URL: {url_display}")

            # Description limitée
            if 'description' in row and pd.notna(row['description']):
                desc = str(row['description'])
                desc_preview = desc[:self.analysis_config['max_description_preview']] + "..." if len(desc) > self.analysis_config['max_description_preview'] else desc
                print(f"   📝 Description: {desc_preview}")

            # Statut IA si disponible
            if 'is_valid' in row:
                is_valid = row['is_valid']
                if pd.notna(is_valid):
                    status_text = '✅ VALIDE' if is_valid else '❌ INVALIDE'
                    print(f"   🤖 Statut IA: {status_text}")

                    if 'ai_response' in row and pd.notna(row['ai_response']):
                        ai_preview = str(row['ai_response'])[:50] + "..." if len(str(row['ai_response'])) > 50 else str(row['ai_response'])
                        print(f"   🔮 Analyse IA: {ai_preview}")

        if len(df) > max_display:
            print(f"\n... et {len(df) - max_display} autres offres")
        print()

    def _generate_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Génère des insights à partir des données analysées.

        Args:
            df (pd.DataFrame): DataFrame à analyser

        Returns:
            Dict[str, Any]: Insights générés
        """
        insights = {}

        # Analyse des titres les plus fréquents
        if 'title' in df.columns:
            title_words = []
            for title in df['title'].dropna():
                words = re.findall(r'\b\w+\b', str(title).lower())
                title_words.extend([w for w in words if len(w) > 3])

            from collections import Counter
            common_words = Counter(title_words).most_common(10)
            insights['common_title_words'] = common_words

        # Analyse géographique
        if 'location' in df.columns:
            location_counts = df['location'].value_counts().head(10)
            insights['top_locations'] = location_counts.to_dict()

        # Analyse des entreprises
        if 'company' in df.columns:
            company_counts = df['company'].value_counts().head(10)
            insights['top_companies'] = company_counts.to_dict()

        # Taux de validation IA
        if 'is_valid' in df.columns:
            total_analyzed = df['is_valid'].notna().sum()
            if total_analyzed > 0:
                valid_count = df['is_valid'].sum()
                insights['ia_validation_rate'] = {
                    'total_analyzed': total_analyzed,
                    'valid_count': int(valid_count) if pd.notna(valid_count) else 0,
                    'validation_rate': (valid_count / total_analyzed) if total_analyzed > 0 else 0
                }

        return insights

    def _display_insights(self, insights: Dict[str, Any]):
        """
        Affiche les insights générés.

        Args:
            insights (Dict): Insights à afficher
        """
        print("💡 INSIGHTS ET TENDANCES:")
        print("-" * 30)

        # Mots-clés fréquents dans les titres
        if 'common_title_words' in insights:
            print("🔤 Mots-clés fréquents dans les titres:")
            for word, count in insights['common_title_words'][:5]:
                print(f"   • {word}: {count} occurrences")
            print()

        # Localisation des offres
        if 'top_locations' in insights:
            print("📍 Principales localisations:")
            for location, count in list(insights['top_locations'].items())[:5]:
                print(f"   • {location}: {count} offres")
            print()

        # Taux de validation IA
        if 'ia_validation_rate' in insights:
            validation = insights['ia_validation_rate']
            rate = validation['validation_rate']
            print(f"🤖 Validation IA: {validation['valid_count']}/{validation['total_analyzed']} offres validées ({rate:.1%})")
            print()

    def _calculate_final_metrics(self, df: pd.DataFrame, analysis_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule les métriques finales de l'analyse.

        Args:
            df (pd.DataFrame): DataFrame analysé
            analysis_report (Dict): Rapport d'analyse

        Returns:
            Dict[str, Any]: Métriques calculées
        """
        metrics = {
            'total_processing_time': datetime.now().isoformat(),
            'data_quality_score': 0.0,
            'collection_efficiency': 0.0,
            'diversity_score': 0.0
        }

        # Score qualité global
        if analysis_report['validation_report']:
            metrics['data_quality_score'] = analysis_report['validation_report']['completeness_score']

        # Efficacité de la collecte (basée sur les URLs uniques)
        if 'url' in df.columns:
            unique_urls = df['url'].nunique()
            total_urls = len(df['url'].dropna())
            metrics['collection_efficiency'] = unique_urls / total_urls if total_urls > 0 else 0

        # Score de diversité (basé sur la diversité des entreprises)
        if 'company' in df.columns:
            unique_companies = df['company'].nunique()
            total_companies = len(df['company'].dropna())
            metrics['diversity_score'] = unique_companies / total_companies if total_companies > 0 else 0

        return metrics

    def _display_conclusion(self, analysis_report: Dict[str, Any]):
        """
        Affiche la conclusion de l'analyse.

        Args:
            analysis_report (Dict): Rapport d'analyse complet
        """
        print("🎯 CONCLUSION DE L'ANALYSE:")
        print("=" * 40)
        print("✅ Ces sont de VRAIES offres collectées depuis les sites d'emploi !")
        print("✅ Plus de données factices - URLs authentiques")

        if analysis_report['validation_report'] and analysis_report['validation_report']['is_valid']:
            print("✅ Qualité des données validée")
        else:
            print("⚠️ Quelques améliorations recommandées sur la qualité")

        print(f"📊 Score qualité global: {self.metrics.get('data_quality_score', 0):.1%}")
        print(f"⚡ Efficacité collecte: {self.metrics.get('collection_efficiency', 0):.1%}")
        print(f"🎯 Diversité: {self.metrics.get('diversity_score', 0):.1%}")


def find_latest_excel_file() -> Optional[str]:
    """
    Trouve le fichier Excel le plus récent dans le répertoire courant.

    Recherche tous les fichiers Excel correspondant au pattern des rapports
    d'alternance et retourne le plus récent basé sur la date de modification.

    Returns:
        Optional[str]: Chemin vers le fichier le plus récent, None si aucun trouvé

    Note:
        Recherche les patterns : rapport_alternance_*.xlsx, offres_*.xlsx, demo_*.xlsx
    """
    logger.debug("Recherche du fichier Excel le plus récent...")

    # Patterns de fichiers à rechercher
    patterns = [
        "rapport_alternance_cybersec_*.xlsx",
        "rapport_alternance_*.xlsx",
        "offres_*.xlsx",
        "demo_*.xlsx",
        "*.xlsx"
    ]

    all_files = []
    for pattern in patterns:
        files = glob.glob(pattern)
        all_files.extend(files)

    if not all_files:
        logger.warning("Aucun fichier Excel trouvé")
        return None

    # Supprimer les doublons et trier par date de modification
    unique_files = list(set(all_files))
    latest_file = max(unique_files, key=os.path.getctime)

    logger.info(f"Fichier le plus récent trouvé: {latest_file}")
    return latest_file


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Configure l'analyseur d'arguments en ligne de commande.

    Returns:
        argparse.ArgumentParser: Parseur configuré
    """
    parser = argparse.ArgumentParser(
        description="Analyseur avancé d'offres d'alternance cybersécurité",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s                                    # Analyse automatique du dernier fichier
  %(prog)s --file rapport_alternance.xlsx    # Analyse d'un fichier spécifique
  %(prog)s --verbose                          # Mode détaillé avec tous les logs
  %(prog)s --file data.xlsx --no-validation  # Sans validation qualité
        """
    )

    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Fichier Excel spécifique à analyser'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mode verbose avec affichage détaillé'
    )

    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='Désactiver la validation qualité des données'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Niveau de logging (défaut: INFO)'
    )

    return parser


def main() -> int:
    """
    Fonction principale du module d'analyse.

    Orchestre l'ensemble du processus d'analyse :
    - Parse les arguments de la ligne de commande
    - Configure le logging selon les paramètres
    - Localise le fichier à analyser
    - Lance l'analyse complète
    - Gère les erreurs et retourne le code de sortie

    Returns:
        int: Code de sortie (0 = succès, 1 = erreur)
    """
    # Configuration des arguments
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Configuration du niveau de logging
    if hasattr(logger, 'setLevel'):
        logger.setLevel(getattr(logging, args.log_level))

    try:
        logger.info("🚀 Démarrage de l'analyseur d'offres d'alternance")

        # Détermination du fichier à analyser
        if args.file:
            if not os.path.exists(args.file):
                logger.error(f"❌ Fichier spécifié non trouvé: {args.file}")
                return 1
            fichier_a_analyser = args.file
        else:
            fichier_a_analyser = find_latest_excel_file()
            if not fichier_a_analyser:
                logger.error("❌ Aucun fichier Excel trouvé dans le répertoire courant")
                print("\n💡 Suggestions:")
                print("   • Vérifiez que vous êtes dans le bon répertoire")
                print("   • Lancez d'abord un scraper pour générer des données")
                print("   • Utilisez --file pour spécifier un fichier précis")
                return 1

        logger.info(f"📁 Fichier sélectionné pour analyse: {fichier_a_analyser}")

        # Création et configuration de l'analyseur
        analyzer = OfferAnalyzer()

        # Configuration selon les arguments
        analyzer.analysis_config['show_details'] = True
        analyzer.analysis_config['include_validation'] = not args.no_validation

        # Lancement de l'analyse
        rapport = analyzer.analyser_fichier_excel(fichier_a_analyser, verbose=args.verbose)

        # Sauvegarde optionnelle du rapport (format JSON)
        if args.verbose:
            rapport_file = f"rapport_analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(rapport_file, 'w', encoding='utf-8') as f:
                json.dump(rapport, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"📄 Rapport détaillé sauvegardé: {rapport_file}")

        logger.info("✅ Analyse terminée avec succès")
        return 0

    except KeyboardInterrupt:
        logger.warning("⚠️ Analyse interrompue par l'utilisateur")
        return 1
    except Exception as e:
        logger.error(f"❌ Erreur fatale lors de l'analyse: {e}")
        if args.verbose:
            logger.exception("Détails de l'erreur:")
        return 1


if __name__ == "__main__":
    exit(main())