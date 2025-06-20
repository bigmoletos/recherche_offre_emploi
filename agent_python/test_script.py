#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour valider move2digital_extract_partenaires_ia.py
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, 'src')

try:
    # Import du module pour vérifier la syntaxe
    print("🔍 Test d'import du module...")
    import move2digital_extract_partenaires_ia as extractor
    print("✅ Import réussi - Syntaxe correcte")

    # Test des classes principales
    print("\n🧪 Test des classes...")

    # Test APIKeyExtractor
    api_extractor = extractor.APIKeyExtractor()
    print("✅ APIKeyExtractor initialisé")

    # Test Move2DigitalScraper
    scraper = extractor.Move2DigitalScraper()
    print("✅ Move2DigitalScraper initialisé")

    # Test CompanyInfo
    company = extractor.CompanyInfo(name="Test Company",
                                    description="Test description",
                                    category="IA/ML")
    print("✅ CompanyInfo créé")

    # Test méthode to_dict
    company_dict = company.to_dict()
    print("✅ Conversion to_dict() réussie")

    print("\n🎉 Tous les tests de base sont passés !")
    print("📋 Structure du module:")
    print(
        f"   - Classes: {[name for name in dir(extractor) if name[0].isupper() and not name.startswith('__')]}"
    )

except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
except Exception as e:
    print(f"❌ Erreur lors des tests: {e}")
    import traceback
    traceback.print_exc()
