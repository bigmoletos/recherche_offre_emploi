#!/usr/bin/env python3
"""
🚀 PATCH WORKFLOW N8N - SAUVEGARDE RÉELLE DE FICHIERS
======================================================

Ce script remplace les nœuds de log console par des nœuds HTTP Request
qui envoient les données à un serveur local Python pour sauvegarde physique.

Requirements:
    1. Lancer d'abord: python server_save_outputs.py
    2. Puis: python patch_workflow_real_file_save.py

Le serveur doit être en cours d'exécution sur http://localhost:8765
"""

import json
import re
from pathlib import Path

def create_http_save_node(original_node, filename):
    """
    Crée un nœud HTTP Request pour sauvegarder via le serveur local

    Args:
        original_node: Le nœud original à remplacer
        filename: Nom du fichier de sortie (sans extension)

    Returns:
        dict: Nouveau nœud HTTP Request
    """
    # Extraction du nom du nœud principal connecté
    node_name_clean = original_node["name"].replace("💾 Save ", "").replace(" Output", "")

    return {
        "parameters": {
            "method": "POST",
            "url": f"http://localhost:8765/save/{filename}",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {
                        "name": "Content-Type",
                        "value": "application/json"
                    }
                ]
            },
            "sendBody": True,
            "bodyParameters": {
                "parameters": []
            },
            "jsonBody": "={{ JSON.stringify($input.item.json) }}",
            "options": {
                "timeout": 10000,
                "redirect": {},
                "response": {
                    "response": {
                        "neverError": True,
                        "responseFormat": "json"
                    }
                }
            }
        },
        "id": original_node["id"],
        "name": f"💾 Save {node_name_clean} Output",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": original_node["position"],
        "alwaysOutputData": True,
        "onError": "continueErrorOutput"
    }


def patch_workflow_with_real_save():
    """Remplace les nœuds de log par des nœuds de sauvegarde HTTP réelle"""

    print("🚀 === PATCH WORKFLOW N8N POUR SAUVEGARDE RÉELLE ===")

    # Lecture du workflow avec logs
    input_file = Path("workflow_hellowork_scraper_complet_LOG_SAVE.json")
    if not input_file.exists():
        print(f"❌ Fichier source non trouvé: {input_file}")
        return False

    print("📖 Chargement du workflow avec logs...")
    with open(input_file, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    # Mapping des nœuds à patcher avec leurs noms de fichier
    save_nodes_mapping = {
        "💾 Save Config HelloWork Output": "config_hellowork_output",
        "💾 Save Fetch Page Output": "fetch_page_output",
        "💾 Save Extraire Conteneur Output": "extraire_conteneur_offres_output",
        "💾 Save Scraper Liste Offres Output": "scraper_liste_offres_output",
        "💾 Save Filtrer Offres Valides Output": "filtrer_offres_valides_output",
        "💾 Save Fetch Detail Offre Output": "fetch_detail_offre_output",
        "💾 Save Scraper Detail Offre Output": "scraper_detail_offre_output",
        "💾 Save Preparer Mistral Output": "preparer_mistral_output",
        "💾 Save API Mistral Output": "api_mistral_output",
        "💾 Save Stocker Offre Finale Output": "stocker_offre_finale_output",
        "💾 Save Gérer Erreurs Output": "gerer_erreurs_output",
        "💾 Save Fin de Boucle Output": "fin_de_boucle_output"
    }

    nodes_patched = 0

    # Parcours et remplacement des nœuds
    for i, node in enumerate(workflow["nodes"]):
        node_name = node.get("name", "")

        if node_name in save_nodes_mapping:
            filename = save_nodes_mapping[node_name]

            # Création du nouveau nœud HTTP Request
            new_node = create_http_save_node(node, filename)
            workflow["nodes"][i] = new_node

            nodes_patched += 1
            print(f"✅ Remplacé {node_name} par HTTP Request")
            print(f"   📁 URL: http://localhost:8765/save/{filename}")

    if nodes_patched == 0:
        print("⚠️ Aucun nœud de sauvegarde trouvé à remplacer")
        return False

    # Sauvegarde du workflow patché
    output_file = Path("workflow_hellowork_scraper_complet_REAL_SAVE.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"💾 Sauvegarde du workflow patché vers {output_file}")
    print(f"🎉 Workflow patché avec succès !")
    print(f"📁 Nouveau fichier : {output_file}")
    print(f"🔄 {nodes_patched} nœuds de log remplacés par HTTP Request")
    print()
    print("📋 Instructions d'utilisation :")
    print("   1️⃣ Démarrez le serveur : python server_save_outputs.py")
    print("   2️⃣ Importez le workflow : workflow_hellowork_scraper_complet_REAL_SAVE.json")
    print("   3️⃣ Exécutez le workflow dans n8n")
    print("   4️⃣ Vérifiez les fichiers dans : outputs/")
    print()
    print("🌐 Le serveur doit être accessible sur http://localhost:8765")
    print("📂 Les fichiers seront sauvegardés physiquement dans outputs/")

    return True


if __name__ == "__main__":
    success = patch_workflow_with_real_save()
    if success:
        print("✅ Patch terminé avec succès !")
        print("👉 N'oubliez pas de démarrer le serveur avant d'utiliser le workflow")
    else:
        print("❌ Échec du patch")
        exit(1)