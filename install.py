#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'installation global pour les Agents de Recherche d'Offres
Permet de choisir et installer l'agent Python Standalone ou l'agent n8n + API

Usage:
    python install.py
    python install.py --agent python
    python install.py --agent n8n
    python install.py --both
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def print_banner():
    """Afficher la bannière d'installation"""
    print("🎯" + "=" * 60 + "🎯")
    print("   AGENT IA - RECHERCHE OFFRES ALTERNANCE CYBERSÉCURITÉ")
    print("                   INSTALLATION AUTOMATIQUE")
    print("🎯" + "=" * 60 + "🎯")
    print()

def print_agent_comparison():
    """Afficher la comparaison des agents"""
    print("📊 COMPARAISON DES AGENTS:")
    print("=" * 50)
    print()

    comparison = [
        ["Critère", "Python Standalone", "n8n + API"],
        ["━━━━━━━", "━━━━━━━━━━━━━━━━", "━━━━━━━━━"],
        ["Simplicité", "⭐⭐⭐⭐⭐", "⭐⭐⭐"],
        ["Interface graphique", "❌", "⭐⭐⭐⭐⭐"],
        ["Automatisation", "⭐⭐", "⭐⭐⭐⭐⭐"],
        ["Monitoring", "⭐⭐", "⭐⭐⭐⭐⭐"],
        ["Temps d'installation", "2 minutes", "5 minutes"],
        ["Prérequis", "Python seulement", "Python + Docker"],
        ["Recommandé pour", "Débutants", "Utilisateurs avancés"]
    ]

    for row in comparison:
        print(f"{row[0]:<20} | {row[1]:<16} | {row[2]}")

    print()

def get_user_choice():
    """Demander à l'utilisateur quel agent installer"""
    print("🤔 QUEL AGENT SOUHAITEZ-VOUS INSTALLER ?")
    print()
    print("1. 🐍 Agent Python Standalone (Recommandé pour débuter)")
    print("   ✅ Simple et rapide")
    print("   ✅ Fonctionne immédiatement")
    print("   ✅ Aucune dépendance complexe")
    print()
    print("2. 🔄 Agent n8n + API (Pour l'automatisation avancée)")
    print("   ✅ Interface graphique")
    print("   ✅ Orchestration visuelle")
    print("   ✅ Monitoring en temps réel")
    print()
    print("3. 🚀 Les deux agents (Installation complète)")
    print("   ✅ Maximum de flexibilité")
    print("   ✅ Tous les cas d'usage couverts")
    print()

    while True:
        choice = input("Votre choix (1/2/3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")

def run_installation_script(script_path, agent_name):
    """Exécuter un script d'installation"""
    print(f"\n🔧 Installation de {agent_name}...")
    print("=" * 50)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent,
            check=True
        )
        print(f"✅ {agent_name} installé avec succès !")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation de {agent_name}")
        print(f"Code de sortie: {e.returncode}")
        return False

def install_python_agent():
    """Installer l'agent Python standalone"""
    script_path = Path(__file__).parent / "agent_python" / "install.py"
    return run_installation_script(script_path, "Agent Python Standalone")

def install_n8n_agent():
    """Installer l'agent n8n + API"""
    script_path = Path(__file__).parent / "agent_n8n" / "install.py"
    return run_installation_script(script_path, "Agent n8n + API")

def show_final_instructions(installed_agents):
    """Afficher les instructions finales"""
    print("\n" + "🎉" + "=" * 58 + "🎉")
    print("               INSTALLATION TERMINÉE !")
    print("🎉" + "=" * 58 + "🎉")
    print()

    if "python" in installed_agents:
        print("🐍 AGENT PYTHON STANDALONE:")
        print("   📁 Répertoire: agent_python/")
        print("   🚀 Démarrage: cd agent_python && python src/main_scraper.py")
        print("   📖 Documentation: agent_python/README.md")
        print()

    if "n8n" in installed_agents:
        print("🔄 AGENT N8N + API:")
        print("   📁 Répertoire: agent_n8n/")
        print("   🚀 Démarrage: cd agent_n8n && start_agent.bat (Windows)")
        print("   🌐 Interface: http://localhost:5678")
        print("   📖 Documentation: agent_n8n/README.md")
        print()

    print("📚 RESSOURCES UTILES:")
    print("   📋 Guide de démarrage rapide: QUICK_START.md")
    print("   📖 Documentation complète: shared/docs/")
    print("   🆘 Support et exemples: shared/docs/guide_*.md")
    print()

    print("⚠️  N'OUBLIEZ PAS:")
    print("   🔑 Configurer vos clés API dans les fichiers .env")
    print("   🧪 Tester l'installation avant utilisation")
    print()

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Installation des Agents de Recherche d'Offres"
    )
    parser.add_argument(
        '--agent',
        choices=['python', 'n8n'],
        help="Agent spécifique à installer"
    )
    parser.add_argument(
        '--both',
        action='store_true',
        help="Installer les deux agents"
    )

    args = parser.parse_args()

    print_banner()

    # Déterminer quels agents installer
    if args.both:
        choice = '3'
    elif args.agent == 'python':
        choice = '1'
    elif args.agent == 'n8n':
        choice = '2'
    else:
        print_agent_comparison()
        choice = get_user_choice()

    installed_agents = []
    success = True

    try:
        if choice == '1':
            # Agent Python seulement
            if install_python_agent():
                installed_agents.append("python")
            else:
                success = False

        elif choice == '2':
            # Agent n8n seulement
            if install_n8n_agent():
                installed_agents.append("n8n")
            else:
                success = False

        elif choice == '3':
            # Les deux agents
            print("\n🚀 Installation des deux agents...")

            # Agent Python d'abord (plus simple)
            if install_python_agent():
                installed_agents.append("python")
            else:
                success = False

            # Puis agent n8n
            if install_n8n_agent():
                installed_agents.append("n8n")
            else:
                success = False

        # Instructions finales
        if installed_agents:
            show_final_instructions(installed_agents)

        if success:
            print("🎯 Installation globale réussie !")
            return 0
        else:
            print("⚠️ Installation partiellement réussie - vérifiez les erreurs ci-dessus")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️ Installation interrompue par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur durant l'installation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())