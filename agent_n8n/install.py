#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'installation automatique pour l'Agent n8n + API
Installe Docker, n8n, API Flask et configure l'environnement

Usage:
    python install.py
    python install.py --docker-only  # Configuration Docker seulement
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

def run_command(cmd, cwd=None, check=True, timeout=300):
    """Exécuter une commande et afficher la sortie"""
    print(f"🔧 Exécution: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True,
            timeout=timeout
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
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout de {timeout}s atteint pour la commande")
        raise

def check_docker():
    """Vérifier que Docker est installé et fonctionne"""
    try:
        result = run_command(["docker", "--version"], check=False)
        if result.returncode == 0:
            print("✅ Docker détecté")

            # Vérifier que Docker fonctionne
            result = run_command(["docker", "ps"], check=False)
            if result.returncode == 0:
                print("✅ Docker fonctionne correctement")
                return True
            else:
                print("❌ Docker installé mais ne fonctionne pas")
                print("   Assurez-vous que Docker Desktop est démarré")
                return False
        else:
            print("❌ Docker non installé")
            print("   Installez Docker Desktop depuis https://docker.com/products/docker-desktop")
            return False
    except FileNotFoundError:
        print("❌ Docker non trouvé dans le PATH")
        return False

def check_docker_compose():
    """Vérifier Docker Compose"""
    try:
        result = run_command(["docker-compose", "--version"], check=False)
        if result.returncode == 0:
            print("✅ Docker Compose détecté")
            return True
        else:
            # Essayer avec docker compose (nouvelle syntaxe)
            result = run_command(["docker", "compose", "version"], check=False)
            if result.returncode == 0:
                print("✅ Docker Compose (nouvelle syntaxe) détecté")
                return True
            else:
                print("❌ Docker Compose non disponible")
                return False
    except FileNotFoundError:
        print("❌ Docker Compose non trouvé")
        return False

def create_virtual_environment(base_dir, force=False):
    """Créer l'environnement virtuel pour l'API Flask"""
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

def install_python_dependencies(venv_path, base_dir, upgrade=False):
    """Installer les dépendances Python pour l'API"""
    python_exe = get_python_executable(venv_path)
    requirements_file = base_dir / "requirements.txt"

    if not requirements_file.exists():
        print(f"❌ Fichier requirements.txt non trouvé: {requirements_file}")
        return False

    print(f"📦 Installation des dépendances API depuis {requirements_file}")

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

def start_docker_services(base_dir):
    """Démarrer les services Docker"""
    docker_dir = base_dir / "docker"
    docker_compose_file = docker_dir / "docker-compose.yml"

    if not docker_compose_file.exists():
        print(f"❌ Fichier docker-compose.yml non trouvé: {docker_compose_file}")
        return False

    print("🐳 Démarrage des services Docker...")

    # Arrêter d'abord les services existants
    run_command([
        "docker-compose", "-f", str(docker_compose_file), "down"
    ], check=False)

    # Démarrer les services
    run_command([
        "docker-compose", "-f", str(docker_compose_file), "up", "-d"
    ], timeout=600)  # 10 minutes de timeout

    # Attendre que les services démarrent
    print("⏳ Attente du démarrage des services...")
    time.sleep(10)

    return True

def check_services_health(base_dir):
    """Vérifier que les services sont en fonctionnement"""
    print("🩺 Vérification de l'état des services...")

    # Vérifier n8n
    try:
        import requests
        response = requests.get("http://localhost:5678", timeout=10)
        if response.status_code == 200:
            print("✅ n8n démarré sur http://localhost:5678")
        else:
            print(f"⚠️ n8n répond mais code: {response.status_code}")
    except Exception as e:
        print(f"❌ n8n non accessible: {e}")
        return False

    return True

def test_api_installation(venv_path, base_dir):
    """Tester l'installation de l'API"""
    python_exe = get_python_executable(venv_path)

    print("\n🧪 Test de l'API Flask...")

    # Test d'import des modules API
    test_script = '''
import sys
try:
    import flask
    import requests
    import pandas
    from dotenv import load_dotenv
    print("✅ Modules API installés correctement")
except ImportError as e:
    print(f"❌ Module API manquant: {e}")
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
        print(f"❌ Test API échoué: {e.stderr}")
        return False

def create_startup_scripts(venv_path, base_dir):
    """Créer des scripts de démarrage"""

    # Script de démarrage complet Windows
    startup_bat = base_dir / "start_agent.bat"
    with open(startup_bat, 'w') as f:
        f.write(f"""@echo off
echo 🔄 Démarrage de l'Agent n8n + API...
echo.

echo 🐳 Démarrage des services Docker...
cd docker
docker-compose up -d
cd ..

echo ⏳ Attente du démarrage des services...
timeout /t 15 /nobreak > nul

echo 🐍 Activation de l'environnement Python...
call "{venv_path}\\Scripts\\activate.bat"

echo 🚀 Démarrage de l'API Flask...
cd api
start python api_scraper_pour_n8n.py
cd ..

echo.
echo ✅ Services démarrés !
echo    n8n Interface: http://localhost:5678
echo    API Flask: http://localhost:5000
echo.
pause
""")

    # Script de démarrage Linux/Mac
    startup_sh = base_dir / "start_agent.sh"
    with open(startup_sh, 'w') as f:
        f.write(f"""#!/bin/bash
echo "🔄 Démarrage de l'Agent n8n + API..."
echo ""

echo "🐳 Démarrage des services Docker..."
cd docker
docker-compose up -d
cd ..

echo "⏳ Attente du démarrage des services..."
sleep 15

echo "🐍 Activation de l'environnement Python..."
source "{venv_path}/bin/activate"

echo "🚀 Démarrage de l'API Flask..."
cd api
python api_scraper_pour_n8n.py &
cd ..

echo ""
echo "✅ Services démarrés !"
echo "   n8n Interface: http://localhost:5678"
echo "   API Flask: http://localhost:5000"
echo ""
""")

    # Rendre exécutable sur Linux/Mac
    if os.name != 'nt':
        os.chmod(startup_sh, 0o755)

    print(f"📜 Scripts de démarrage créés:")
    print(f"   Windows: {startup_bat}")
    print(f"   Linux/Mac: {startup_sh}")

def main():
    """Fonction principale d'installation"""
    parser = argparse.ArgumentParser(
        description="Installation de l'Agent n8n + API"
    )
    parser.add_argument(
        '--docker-only',
        action='store_true',
        help="Configuration Docker seulement"
    )
    parser.add_argument(
        '--upgrade',
        action='store_true',
        help="Mettre à jour les dépendances"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help="Recréer l'environnement virtuel"
    )

    args = parser.parse_args()

    print("🔄 Installation de l'Agent n8n + API")
    print("=" * 50)

    # Répertoire de base
    base_dir = Path(__file__).parent
    print(f"📁 Répertoire: {base_dir}")

    try:
        # 1. Vérifier Docker
        if not check_docker():
            print("\n❌ Installation interrompue - Docker requis")
            return 1

        if not check_docker_compose():
            print("\n❌ Installation interrompue - Docker Compose requis")
            return 1

        # 2. Configuration
        setup_configuration(base_dir)

        # 3. Démarrer les services Docker
        if not start_docker_services(base_dir):
            print("\n❌ Échec du démarrage des services Docker")
            return 1

        if args.docker_only:
            print("\n✅ Services Docker configurés !")
            print("   n8n Interface: http://localhost:5678")
            return 0

        # 4. Environnement Python pour l'API
        venv_path = create_virtual_environment(base_dir, args.force)

        # 5. Installer les dépendances Python
        if not install_python_dependencies(venv_path, base_dir, args.upgrade):
            return 1

        # 6. Vérifier les services
        if not check_services_health(base_dir):
            print("\n⚠️ Services partiellement démarrés")

        # 7. Test de l'API
        if not test_api_installation(venv_path, base_dir):
            return 1

        # 8. Scripts de démarrage
        create_startup_scripts(venv_path, base_dir)

        print("\n" + "=" * 50)
        print("🎉 Installation terminée avec succès !")
        print("\n📋 Services disponibles:")
        print("   🌐 n8n Interface: http://localhost:5678")
        print("   🔗 API Flask: http://localhost:5000/health")
        print("\n📋 Prochaines étapes:")
        print("1. Éditer config/.env avec vos clés API")
        print("2. Configurer n8n:")
        print("   python config/config_setup_mistral.py")
        print("3. Démarrer l'agent complet:")
        if os.name == 'nt':
            print("   start_agent.bat")
        else:
            print("   ./start_agent.sh")

        return 0

    except Exception as e:
        print(f"\n❌ Erreur durant l'installation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())