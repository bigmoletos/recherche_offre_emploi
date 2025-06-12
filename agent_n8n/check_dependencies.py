#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification et réparation des dépendances pour l'agent n8n.

Ce script vérifie que toutes les dépendances sont correctement installées
et propose de les réparer automatiquement si nécessaire.

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: 03/06/2025
"""

import sys
import os
import subprocess
from pathlib import Path
import importlib.util

def get_python_executable():
    """Obtenir l'exécutable Python de l'environnement virtuel local."""
    current_dir = Path(__file__).parent
    venv_dir = current_dir / "venv"

    if os.name == 'nt':  # Windows
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:  # Linux/Mac
        python_exe = venv_dir / "bin" / "python"

    return python_exe, venv_dir

def check_virtual_env():
    """Vérifier l'existence de l'environnement virtuel."""
    python_exe, venv_dir = get_python_executable()

    print("🔍 Vérification de l'environnement virtuel...")
    print(f"📁 Répertoire venv: {venv_dir}")
    print(f"🐍 Python attendu: {python_exe}")

    if not venv_dir.exists():
        print("❌ Environnement virtuel non trouvé!")
        return False, None

    if not python_exe.exists():
        print("❌ Exécutable Python non trouvé dans l'environnement virtuel!")
        return False, None

    print("✅ Environnement virtuel trouvé")
    return True, python_exe

def get_installed_packages(python_exe):
    """Obtenir la liste des packages installés."""
    try:
        result = subprocess.run(
            [str(python_exe), "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            check=True
        )
        packages = {}
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                name, version = line.split('==')
                packages[name.lower()] = version
        return packages
    except subprocess.CalledProcessError:
        return {}

def check_critical_imports(python_exe):
    """Tester les imports critiques."""
    print("\n🧪 Test des imports critiques...")

    critical_modules = [
        ('flask', 'Flask'),
        ('flask_cors', 'CORS'),
        ('bs4', 'BeautifulSoup'),
        ('requests', 'requests'),
        ('pandas', 'pandas'),
        ('lxml', 'lxml'),
        ('dotenv', 'python-dotenv'),
    ]

    failed_imports = []

    for module_name, package_name in critical_modules:
        try:
            # Test d'import via subprocess pour utiliser le bon environnement
            result = subprocess.run(
                [str(python_exe), "-c", f"import {module_name}; print('OK')"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"✅ {module_name} ({package_name})")
            else:
                print(f"❌ {module_name} ({package_name}) - {result.stderr.strip()}")
                failed_imports.append((module_name, package_name))

        except subprocess.TimeoutExpired:
            print(f"⏰ {module_name} ({package_name}) - Timeout")
            failed_imports.append((module_name, package_name))
        except Exception as e:
            print(f"❌ {module_name} ({package_name}) - {e}")
            failed_imports.append((module_name, package_name))

    return failed_imports

def repair_dependencies(python_exe, force_reinstall=False):
    """Réparer les dépendances manquantes."""
    current_dir = Path(__file__).parent
    requirements_file = current_dir / "requirements.txt"

    if not requirements_file.exists():
        print(f"❌ Fichier requirements.txt non trouvé: {requirements_file}")
        return False

    print(f"\n🔧 Réparation des dépendances depuis {requirements_file}")

    try:
        # Mettre à jour pip
        print("📦 Mise à jour de pip...")
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            timeout=120
        )

        # Installer/réinstaller les dépendances
        cmd = [str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)]

        if force_reinstall:
            cmd.extend(["--force-reinstall", "--no-cache-dir"])
            print("🔄 Réinstallation forcée...")
        else:
            print("📦 Installation des dépendances...")

        subprocess.run(cmd, check=True, timeout=300)
        print("✅ Dépendances réparées avec succès")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la réparation: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("⏰ Timeout lors de l'installation")
        return False

def test_api_startup(python_exe):
    """Tester le démarrage de l'API."""
    current_dir = Path(__file__).parent
    api_script = current_dir / "api" / "api_scraper_pour_n8n.py"

    if not api_script.exists():
        print(f"❌ Script API non trouvé: {api_script}")
        return False

    print("\n🧪 Test de démarrage de l'API...")

    try:
        # Test d'import du module API
        result = subprocess.run([
            str(python_exe), "-c",
            f"import sys; sys.path.insert(0, '{current_dir}'); "
            "from api.api_scraper_pour_n8n import load_config; "
            "config = load_config(); "
            "print('Configuration chargée:', len(config), 'paramètres')"
        ], capture_output=True, text=True, timeout=30, cwd=current_dir)

        if result.returncode == 0:
            print("✅ Module API chargeable")
            print(f"📋 {result.stdout.strip()}")
            return True
        else:
            print("❌ Erreur lors du chargement de l'API:")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Timeout lors du test de l'API")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale de vérification."""
    print("🔍 === Vérification des dépendances agent n8n ===\n")

    # 1. Vérifier l'environnement virtuel
    venv_ok, python_exe = check_virtual_env()
    if not venv_ok:
        print("\n❌ Environnement virtuel manquant!")
        print("🔧 Lancez: python install.py")
        return 1

    # 2. Vérifier les packages installés
    print(f"\n📦 Vérification des packages installés...")
    packages = get_installed_packages(python_exe)
    print(f"📊 {len(packages)} packages installés")

    # 3. Tester les imports critiques
    failed_imports = check_critical_imports(python_exe)

    # 4. Réparer si nécessaire
    if failed_imports:
        print(f"\n⚠️  {len(failed_imports)} module(s) problématique(s) détecté(s)")
        print("Modules en échec:")
        for module, package in failed_imports:
            print(f"  - {module} ({package})")

        response = input("\n🔧 Réparer automatiquement ? (o/N): ").lower()
        if response in ['o', 'oui', 'y', 'yes']:
            force = input("🔄 Forcer la réinstallation ? (o/N): ").lower()
            force_reinstall = force in ['o', 'oui', 'y', 'yes']

            if repair_dependencies(python_exe, force_reinstall):
                print("\n🔄 Re-test après réparation...")
                failed_imports = check_critical_imports(python_exe)

                if not failed_imports:
                    print("✅ Tous les modules fonctionnent maintenant!")
                else:
                    print(f"❌ {len(failed_imports)} module(s) encore en échec")
            else:
                print("❌ Échec de la réparation")
                return 1
    else:
        print("✅ Tous les modules critiques fonctionnent")

    # 5. Test de l'API
    if not failed_imports:
        api_ok = test_api_startup(python_exe)
        if api_ok:
            print("\n🎉 Tout fonctionne correctement!")
            print("🚀 Vous pouvez lancer l'API avec:")
            print("   python start_api.py")
            print("   ou: start_api.bat")
            return 0
        else:
            print("\n❌ Problème avec l'API")
            return 1
    else:
        print(f"\n❌ {len(failed_imports)} module(s) encore problématique(s)")
        return 1

if __name__ == "__main__":
    sys.exit(main())