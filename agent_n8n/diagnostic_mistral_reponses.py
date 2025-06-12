#!/usr/bin/env python3
"""
Script de diagnostic pour analyser les réponses de Mistral
et comprendre pourquoi toutes les offres sont invalidées
"""

import requests
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
API_KEY = "fe8GdBIIBwYk8Dj1GvclASPE3j0Zbt95"
API_URL = "https://api.mistral.ai/v1/chat/completions"

# Offres de test
offres_test = [
    {
        "id": "test-valide-1",
        "title": "Contrat d'apprentissage - Analyste Cybersécurité SOC",
        "company": "Orange Cyberdefense",
        "description": "Nous proposons un contrat d'apprentissage de 24 mois pour former un analyste cybersécurité au sein de notre SOC (Security Operations Center). Missions : surveillance des systèmes d'information, analyse des incidents de sécurité, réponse aux alertes SIEM, veille technologique. Formation : Master 2 cybersécurité en alternance. Rythme : 3 semaines en entreprise / 1 semaine à l'école.",
        "contract_type": "Contrat d'apprentissage",
        "keywords": ["apprentissage", "cybersécurité", "SOC", "alternance"],
        "attendu": "VALIDE"
    },
    {
        "id": "test-invalide-1",
        "title": "Stage - Marketing Digital et Communication",
        "company": "AgenceComm",
        "description": "Stage de 6 mois en marketing digital. Missions : gestion des réseaux sociaux, création de contenu, campagnes publicitaires, analyse des performances. Recherche étudiant en Master Marketing. Stage non rémunéré avec convention obligatoire.",
        "contract_type": "Stage",
        "keywords": ["stage", "marketing", "digital", "communication"],
        "attendu": "INVALIDE"
    }
]

def test_prompt_simple(offre):
    """Test avec un prompt très simple et direct"""
    prompt = f"""Analysez cette offre d'emploi :

TITRE: {offre['title']}
ENTREPRISE: {offre['company']}
TYPE: {offre['contract_type']}
DESCRIPTION: {offre['description'][:200]}...

QUESTION SIMPLE: Cette offre est-elle une ALTERNANCE en CYBERSÉCURITÉ ?

Répondez uniquement par :
- VALIDE si c'est une alternance/apprentissage en cybersécurité
- INVALIDE sinon

RÉPONSE:"""

    return prompt

def test_prompt_structure(offre):
    """Test avec un prompt structuré comme dans N8N"""
    prompt = f"""Tu es un expert RH spécialisé en cybersécurité et contrats d'alternance.

🎯 **MISSION**: Analyser si cette offre correspond EXACTEMENT à une ALTERNANCE en CYBERSÉCURITÉ.

📋 **OFFRE À ANALYSER**:
• **Titre**: {offre['title']}
• **Entreprise**: {offre['company']}
• **Description**: {offre['description']}
• **Type de contrat**: {offre['contract_type']}
• **Mots-clés**: {', '.join(offre['keywords'])}

🔍 **CRITÈRES OBLIGATOIRES**:

**1. TYPE DE CONTRAT (CRITIQUE)**:
✅ ALTERNANCE: "alternance", "apprentissage", "contrat pro", "contrat de professionnalisation"
❌ AUTRES: "stage", "CDI", "CDD", "freelance", "mission"

**2. DOMAINE CYBERSÉCURITÉ (CRITIQUE)**:
✅ CYBER: "cybersécurité", "sécurité informatique", "sécurité des SI"
✅ SPÉCIALITÉS: "SOC", "SIEM", "pentest", "audit sécurité", "GRC", "forensic"
❌ AUTRES: "sécurité physique", "sécurité bâtiment", "surveillance", "marketing"

📝 **FORMAT DE RÉPONSE OBLIGATOIRE**:
**CLASSIFICATION**: VALIDE ou INVALIDE
**JUSTIFICATION**: [Explique en 1-2 phrases pourquoi]

Analyse maintenant cette offre."""

    return prompt

def appel_mistral(prompt, model="mistral-large-latest"):
    """Appeler l'API Mistral avec le prompt donné"""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Tu es un expert RH avec 15 ans d'expérience en cybersécurité et alternance. Tu analyses les offres avec précision."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.05,
        "max_tokens": 300
    }

    try:
        response = requests.post(
            API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            return f"ERREUR API {response.status_code}: {response.text}"

        data = response.json()
        if data and "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return "ERREUR: Structure réponse invalide"

    except Exception as e:
        return f"ERREUR RÉSEAU: {str(e)}"

def analyser_reponse(reponse):
    """Analyser la réponse pour extraire la classification"""
    if "ERREUR" in reponse:
        return "ERREUR", reponse

    reponse_upper = reponse.upper()

    if "VALIDE" in reponse_upper and "INVALIDE" not in reponse_upper:
        return "VALIDE", reponse
    elif "INVALIDE" in reponse_upper:
        return "INVALIDE", reponse
    else:
        return "INCERTAIN", reponse

def main():
    print("🔍 === DIAGNOSTIC MISTRAL LARGE ===\n")

    resultats = []

    for i, offre in enumerate(offres_test, 1):
        print(f"📄 TEST {i}/2: {offre['title']}")
        print(f"🎯 Résultat attendu: {offre['attendu']}")
        print("-" * 60)

        # Test 1: Prompt simple
        print("🧪 Test avec prompt SIMPLE...")
        prompt_simple = test_prompt_simple(offre)
        reponse_simple = appel_mistral(prompt_simple)
        classif_simple, _ = analyser_reponse(reponse_simple)

        print(f"📝 Réponse prompt simple: {reponse_simple[:150]}...")
        print(f"🏷️  Classification simple: {classif_simple}")

        # Test 2: Prompt structuré
        print("\n🧪 Test avec prompt STRUCTURÉ...")
        prompt_structure = test_prompt_structure(offre)
        reponse_structure = appel_mistral(prompt_structure)
        classif_structure, _ = analyser_reponse(reponse_structure)

        print(f"📝 Réponse prompt structuré: {reponse_structure[:150]}...")
        print(f"🏷️  Classification structurée: {classif_structure}")

        # Analyse
        correct_simple = classif_simple == offre['attendu']
        correct_structure = classif_structure == offre['attendu']

        print(f"\n✅ Prompt simple correct: {correct_simple}")
        print(f"✅ Prompt structuré correct: {correct_structure}")

        resultats.append({
            'offre_id': offre['id'],
            'attendu': offre['attendu'],
            'simple': classif_simple,
            'structure': classif_structure,
            'correct_simple': correct_simple,
            'correct_structure': correct_structure,
            'reponse_complete_structure': reponse_structure
        })

        print("=" * 80)
        print()

    # Résumé
    print("📊 === RÉSUMÉ DIAGNOSTIC ===")
    correct_simple_count = sum(1 for r in resultats if r['correct_simple'])
    correct_structure_count = sum(1 for r in resultats if r['correct_structure'])

    print(f"📈 Prompt simple: {correct_simple_count}/{len(resultats)} corrects")
    print(f"📈 Prompt structuré: {correct_structure_count}/{len(resultats)} corrects")

    # Détails des erreurs
    print("\n🔍 DÉTAIL DES PROBLÈMES:")
    for r in resultats:
        if not r['correct_structure']:
            print(f"❌ {r['offre_id']}: Attendu {r['attendu']}, Obtenu {r['structure']}")
            print(f"   Réponse complète: {r['reponse_complete_structure'][:200]}...")
            print()

    print("🏁 Diagnostic terminé !")

if __name__ == "__main__":
    main()