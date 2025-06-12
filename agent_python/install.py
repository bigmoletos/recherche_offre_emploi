#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'installation automatique pour l'Agent Python Standalone
Crée l'environnement virtuel, installe les dépendances et configure l'environnement

Usage:
    python install.py
    python install.py --upgrade  # Mise à jour des dépendances
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Exécuter une commande et afficher la sortie"""
    print(f"🔧 Exécution: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de {' '.join(cmd)}")
        print(f"Code de sortie: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        raise

def check_python_version():
    """Vérifier que Python 3.8+ est installé"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ requis. Version actuelle: {version.major}.{version.minor}")
        return False

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} détecté")
    return True

def create_virtual_environment(base_dir, force=False):
    """Créer l'environnement virtuel"""
    venv_path = base_dir / "venv"

    if venv_path.exists():
        if not force:
            print(f"✅ Environnement virtuel déjà existant: {venv_path}")
            return venv_path
        else:
            print(f"🗑️ Suppression de l'ancien environnement: {venv_path}")
            import shutil
            shutil.rmtree(venv_path)

    print(f"🔨 Création de l'environnement virtuel: {venv_path}")
    run_command([sys.executable, "-m", "venv", str(venv_path)])

    return venv_path

def get_python_executable(venv_path):
    """Obtenir l'exécutable Python de l'environnement virtuel"""
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "python.exe"
    else:  # Linux/Mac
        return venv_path / "bin" / "python"

def install_dependencies(venv_path, base_dir, upgrade=False):
    """Installer les dépendances Python"""
    python_exe = get_python_executable(venv_path)
    requirements_file = base_dir / "requirements.txt"

    if not requirements_file.exists():
        print(f"❌ Fichier requirements.txt non trouvé: {requirements_file}")
        return False

    print(f"📦 Installation des dépendances depuis {requirements_file}")

    # Mettre à jour pip
    run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])

    # Installer les dépendances
    cmd = [str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)]
    if upgrade:
        cmd.append("--upgrade")

    run_command(cmd)
    return True

def setup_configuration(base_dir):
    """Configurer les fichiers de configuration"""
    config_dir = base_dir / "config"
    config_dir.mkdir(exist_ok=True)

    env_example = config_dir / ".env.example"
    env_file = config_dir / ".env"

    if not env_file.exists() and env_example.exists():
        print(f"📝 Copie du template de configuration: {env_example} -> {env_file}")
        import shutil
        shutil.copy2(env_example, env_file)

        print("\n⚠️  IMPORTANT: Éditez le fichier config/.env avec vos clés API !")
        print("   Notamment MISTRAL_API_KEY pour l'analyse IA")

    # Créer les dossiers nécessaires
    for folder in ["logs", "outputs"]:
        folder_path = base_dir / folder
        folder_path.mkdir(exist_ok=True)
        print(f"📁 Dossier créé: {folder_path}")

def test_installation(venv_path, base_dir):
    """Tester l'installation"""
    python_exe = get_python_executable(venv_path)

    print("\n🧪 Test de l'installation...")

    # Test d'import des modules principaux
    test_script = '''
import sys
try:
    import requests
    import pandas
    import openpyxl
    from dotenv import load_dotenv
    print("✅ Tous les modules principaux sont installés")
except ImportError as e:
    print(f"❌ Module manquant: {e}")
    sys.exit(1)
'''

    try:
        result = subprocess.run(
            [str(python_exe), "-c", test_script],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Test d'installation échoué: {e.stderr}")
        return False

def create_activation_scripts(venv_path, base_dir):
    """Créer des scripts d'activation pratiques"""

    # Script pour Windows
    activate_bat = base_dir / "activate.bat"
    with open(activate_bat, 'w') as f:
        f.write(f"""@echo off
echo 🐍 Activation de l'environnement Agent Python...
call "{venv_path}\\Scripts\\activate.bat"
echo ✅ Environnement activé !
echo.
echo 🚀 Pour lancer l'agent:
echo    python src/main_scraper.py
echo.
""")

    # Script pour Linux/Mac
    activate_sh = base_dir / "activate.sh"
    with open(activate_sh, 'w') as f:
        f.write(f"""#!/bin/bash
echo "🐍 Activation de l'environnement Agent Python..."
source "{venv_path}/bin/activate"
echo "✅ Environnement activé !"
echo ""
echo "🚀 Pour lancer l'agent:"
echo "   python src/main_scraper.py"
echo ""
""")

    # Rendre exécutable sur Linux/Mac
    if os.name != 'nt':
        os.chmod(activate_sh, 0o755)

    print(f"📜 Scripts d'activation créés:")
    print(f"   Windows: {activate_bat}")
    print(f"   Linux/Mac: {activate_sh}")

def main():
    """Fonction principale d'installation"""
    parser = argparse.ArgumentParser(
        description="Installation de l'Agent Python Standalone"
    )
    parser.add_argument(
        '--upgrade',
        action='store_true',
        help="Mettre à jour les dépendances existantes"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help="Recréer l'environnement virtuel"
    )

    args = parser.parse_args()

    print("🎯 Installation de l'Agent Python Standalone")
    print("=" * 50)

    # Répertoire de base
    base_dir = Path(__file__).parent
    print(f"📁 Répertoire: {base_dir}")

    try:
        # 1. Vérifier Python
        if not check_python_version():
            return 1

        # 2. Créer l'environnement virtuel
        venv_path = create_virtual_environment(base_dir, args.force)

        # 3. Installer les dépendances
        if not install_dependencies(venv_path, base_dir, args.upgrade):
            return 1

        # 4. Configuration
        setup_configuration(base_dir)

        # 5. Test de l'installation
        if not test_installation(venv_path, base_dir):
            return 1

        # 6. Scripts d'activation
        create_activation_scripts(venv_path, base_dir)

        print("\n" + "=" * 50)
        print("🎉 Installation terminée avec succès !")
        print("\n📋 Prochaines étapes:")
        print("1. Éditer config/.env avec votre clé MISTRAL_API_KEY")
        print("2. Activer l'environnement:")
        if os.name == 'nt':
            print("   activate.bat")
        else:
            print("   source activate.sh")
        print("3. Lancer l'agent:")
        print("   python src/main_scraper.py")

        return 0

    except Exception as e:
        print(f"\n❌ Erreur durant l'installation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())