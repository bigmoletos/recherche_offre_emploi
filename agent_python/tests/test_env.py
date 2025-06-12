#!/usr/bin/env python3
"""
Test de lecture des variables d'environnement
"""

import os
from dotenv import load_dotenv

def test_env_vars():
    """Teste la lecture des variables d'environnement."""
    print("🔍 Test des variables d'environnement")
    print("=" * 40)

    # Charger le fichier .env
    env_loaded = load_dotenv()
    print(f"Fichier .env chargé: {'✅ OUI' if env_loaded else '❌ NON'}")

    # Variables à tester
    test_vars = [
        'LOGIN_N8N',
        'PASSWORD_N8N',
        'N8N_HOST',
        'N8N_PORT',
        'OPENAI_API_KEY',
        'SLACK_BOT_TOKEN',
        'SMTP_USER'
    ]

    print("\n📋 Variables d'environnement:")
    for var in test_vars:
        value = os.getenv(var)
        if value:
            # Masquer les mots de passe
            if 'PASSWORD' in var or 'KEY' in var or 'TOKEN' in var:
                display_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: NON DÉFINI")

    return any(os.getenv(var) for var in test_vars)

if __name__ == "__main__":
    test_env_vars()