#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement de l'API n8n avec gestion automatique de l'environnement.

Ce script garantit que l'API est lancée avec le bon environnement virtuel
et toutes les dépendances nécessaires installées.

Auteur: desmedt.franck@iaproject.fr
Version: 1.0
Date: 03/06/2025
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Lance l'API avec l'environnement virtuel approprié."""

    # Déterminer les chemins
    current_dir = Path(__file__).parent
    venv_dir = current_dir / "venv"
    api_script = current_dir / "api" / "api_scraper_pour_n8n.py"

    # Vérifier l'existence de l'environnement virtuel
    if not venv_dir.exists():
        print("❌ Environnement virtuel non trouvé!")
        print(f"📁 Cherché dans: {venv_dir}")
        print("🔧 Lancez d'abord: python install.py")
        return 1

    # Déterminer l'exécutable Python dans le venv (Windows/Linux)
    if os.name == 'nt':  # Windows
        python_exe = venv_dir / "Scripts" / "python.exe"
        activate_script = venv_dir / "Scripts" / "activate.bat"
    else:  # Linux/Mac
        python_exe = venv_dir / "bin" / "python"
        activate_script = venv_dir / "bin" / "activate"

    if not python_exe.exists():
        print("❌ Python non trouvé dans l'environnement virtuel!")
        print(f"📁 Cherché: {python_exe}")
        return 1

    if not api_script.exists():
        print("❌ Script API non trouvé!")
        print(f"📁 Cherché: {api_script}")
        return 1

    print("🚀 Lancement de l'API Scraper n8n...")
    print(f"🐍 Python: {python_exe}")
    print(f"📜 Script: {api_script}")
    print(f"📁 Répertoire: {current_dir}")
    print()

    try:
        # Changer de répertoire pour que les imports relatifs fonctionnent
        os.chdir(current_dir)

        # Lancer l'API avec l'environnement virtuel
        cmd = [str(python_exe), str(api_script)]

        # Ajouter les arguments passés au script
        if len(sys.argv) > 1:
            cmd.extend(sys.argv[1:])

        print(f"🎯 Commande: {' '.join(cmd)}")
        print("=" * 50)

        # Exécuter la commande
        result = subprocess.run(cmd, cwd=current_dir)
        return result.returncode

    except KeyboardInterrupt:
        print("\n⚠️  Arrêt demandé par l'utilisateur")
        return 0
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())