#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour patcher automatiquement le workflow n8n en remplaçant les nœuds Write Binary File
par des nœuds Code qui sauvegardent directement les JSON avec fs.writeFileSync.
"""

import json
import uuid
from pathlib import Path

def generate_uuid():
    """Génère un UUID unique pour les nouveaux nœuds."""
    return str(uuid.uuid4())

def create_direct_json_save_node(node_id, name, file_path, position):
    """Crée un nœud Code qui sauvegarde directement le JSON."""

    # Échapper les backslashes pour le chemin Windows
    escaped_path = file_path.replace('\\', '\\\\')

    js_code = f"""// Sauvegarde directe JSON - {name}
const fs = require('fs');
const path = require('path');

try {{
  const outputPath = '{escaped_path}';
  const jsonData = JSON.stringify($input.item.json, null, 2);

  // Créer le dossier si il n'existe pas
  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) {{
    fs.mkdirSync(dir, {{ recursive: true }});
  }}

  // Écrire le fichier JSON
  fs.writeFileSync(outputPath, jsonData, 'utf8');

  console.log(`✅ JSON sauvegardé: ${{outputPath}}`);
  console.log(`📊 Taille: ${{jsonData.length}} caractères`);

  return $input.all();
}} catch (error) {{
  console.error(`❌ Erreur sauvegarde {name}: ${{error.message}}`);
  return $input.all();
}}"""

    return {
        "parameters": {
            "jsCode": js_code
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": position
    }

def patch_workflow():
    """Patch le workflow pour remplacer Write Binary File par des sauvegardes JSON directes."""

    # Chemin du workflow
    workflow_path = Path("workflow_hellowork_scraper_complet_with_saved_output.json")

    if not workflow_path.exists():
        print(f"❌ Fichier workflow non trouvé : {workflow_path}")
        return False

    # Charger le workflow
    print("📖 Chargement du workflow...")
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    # Identifier tous les nœuds Write Binary File (sauvegarde)
    save_nodes_to_replace = []
    for i, node in enumerate(workflow["nodes"]):
        if (node.get("type") == "n8n-nodes-base.writeBinaryFile" and
            node.get("name", "").startswith("💾 Save")):
            save_nodes_to_replace.append((i, node))

    print(f"🔍 Trouvé {len(save_nodes_to_replace)} nœuds Write Binary File à remplacer")

    # Remplacer chaque nœud Write Binary File par un nœud Code
    nodes_replaced = 0
    for index, (node_index, old_node) in enumerate(save_nodes_to_replace):
        old_name = old_node["name"]
        old_id = old_node["id"]
        old_position = old_node["position"]

        # Extraire le chemin du fichier depuis les paramètres
        file_path = old_node.get("parameters", {}).get("filePath", "")
        if not file_path:
            print(f"⚠️ Pas de filePath trouvé pour {old_name}")
            continue

        # Créer le nouveau nœud Code de sauvegarde directe
        new_node_id = generate_uuid()
        new_node_name = old_name  # Garder le même nom

        new_node = create_direct_json_save_node(
            new_node_id,
            new_node_name,
            file_path,
            old_position
        )

        # Remplacer l'ancien nœud
        workflow["nodes"][node_index] = new_node

        # Mettre à jour les connexions qui pointaient vers l'ancien ID
        for source_name, connections in workflow["connections"].items():
            for output_list in connections.get("main", []):
                for connection in output_list:
                    if connection.get("node") == old_name:
                        # Le nom reste le même, pas besoin de changer
                        pass

        print(f"✅ Remplacé {old_name}")
        print(f"   📁 Fichier: {file_path}")
        nodes_replaced += 1

    # Sauvegarder le workflow patché
    output_path = workflow_path.parent / "workflow_hellowork_scraper_complet_DIRECT_SAVE.json"
    print(f"💾 Sauvegarde du workflow patché vers {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"🎉 Workflow patché avec succès !")
    print(f"📁 Nouveau fichier : {output_path}")
    print(f"🔄 {nodes_replaced} nœuds Write Binary File remplacés par des sauvegardes JSON directes")

    # Afficher la liste des fichiers qui seront créés
    print(f"\n📋 Fichiers JSON qui seront créés lors de l'exécution :")
    for i, (node_index, old_node) in enumerate(save_nodes_to_replace):
        file_path = old_node.get("parameters", {}).get("filePath", "")
        if file_path:
            filename = Path(file_path).name
            print(f"   📄 {filename}")

    return True

if __name__ == "__main__":
    print("🚀 === PATCH WORKFLOW N8N POUR SAUVEGARDES JSON DIRECTES ===")
    success = patch_workflow()
    if success:
        print("\n✅ Patch terminé avec succès !")
        print("👉 Importez le fichier workflow_hellowork_scraper_complet_DIRECT_SAVE.json dans n8n")
        print("🎯 Les sauvegardes JSON se feront maintenant directement sans conversion binaire")
    else:
        print("\n❌ Erreur lors du patch")