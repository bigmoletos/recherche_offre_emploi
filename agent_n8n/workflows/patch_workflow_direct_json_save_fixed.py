#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour patcher automatiquement le workflow n8n en remplaçant les nœuds Write Binary File
par des nœuds Code compatibles avec l'environnement n8n (sans fs).
"""

import json
import uuid
from pathlib import Path

def generate_uuid():
    """Génère un UUID unique pour les nouveaux nœuds."""
    return str(uuid.uuid4())

def create_n8n_compatible_save_node(node_id, name, file_path, position):
    """Crée un nœud Code compatible avec n8n pour sauvegarder le JSON."""

    # Échapper les backslashes pour le chemin Windows
    escaped_path = file_path.replace('\\', '\\\\')

    js_code = f"""// Sauvegarde JSON compatible n8n - {name}
try {{
  const outputPath = '{escaped_path}';
  const jsonData = JSON.stringify($input.item.json, null, 2);

  // Utilisation de l'API n8n pour écrire le fichier
  const {{ writeFileSync }} = require('fs');
  const {{ dirname }} = require('path');

  // Alternative compatible n8n : utiliser $binary
  const binaryData = Buffer.from(jsonData, 'utf8').toString('base64');

  // Retourner les données avec un signal de sauvegarde
  console.log(`✅ Données préparées pour sauvegarde: ${{outputPath}}`);
  console.log(`📊 Taille JSON: ${{jsonData.length}} caractères`);

  return [{{
    json: {{
      ...$input.item.json,
      _save_info: {{
        file_path: outputPath,
        size: jsonData.length,
        saved_at: new Date().toISOString()
      }}
    }},
    binary: {{
      data: {{
        data: binaryData,
        mimeType: 'application/json',
        fileName: outputPath.split('\\\\').pop()
      }}
    }}
  }}];
}} catch (error) {{
  console.error(`❌ Erreur préparation sauvegarde {name}: ${{error.message}}`);
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

def create_simple_log_save_node(node_id, name, file_path, position):
    """Crée un nœud Code simple qui log les données pour débogage."""

    js_code = f"""// Sauvegarde simple avec log - {name}
try {{
  const outputPath = '{file_path}';
  const jsonData = JSON.stringify($input.item.json, null, 2);

  // Log des données pour débogage
  console.log(`📄 === SAUVEGARDE {name} ===`);
  console.log(`📁 Chemin: ${{outputPath}}`);
  console.log(`📊 Taille: ${{jsonData.length}} caractères`);
  console.log(`🕒 Timestamp: ${{new Date().toISOString()}}`);

  // Log d'un extrait des données
  const preview = jsonData.length > 500 ? jsonData.substring(0, 500) + '...' : jsonData;
  console.log(`📋 Aperçu données:`);
  console.log(preview);

  // Retourner les données originales avec info de sauvegarde
  return [{{
    json: {{
      ...$input.item.json,
      _debug_save: {{
        intended_path: outputPath,
        data_size: jsonData.length,
        logged_at: new Date().toISOString()
      }}
    }}
  }}];
}} catch (error) {{
  console.error(`❌ Erreur log sauvegarde {name}: ${{error.message}}`);
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
    """Patch le workflow pour remplacer Write Binary File par des logs de débogage."""

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

    # Remplacer chaque nœud Write Binary File par un nœud Code de log
    nodes_replaced = 0
    for index, (node_index, old_node) in enumerate(save_nodes_to_replace):
        old_name = old_node["name"]
        old_position = old_node["position"]

        # Extraire le chemin du fichier depuis les paramètres
        file_path = old_node.get("parameters", {}).get("filePath", "")
        if not file_path:
            print(f"⚠️ Pas de filePath trouvé pour {old_name}")
            continue

        # Créer le nouveau nœud Code de log
        new_node_id = generate_uuid()
        new_node_name = old_name  # Garder le même nom

        # Utiliser la version simple avec logs
        new_node = create_simple_log_save_node(
            new_node_id,
            new_node_name,
            file_path,
            old_position
        )

        # Remplacer l'ancien nœud
        workflow["nodes"][node_index] = new_node

        print(f"✅ Remplacé {old_name} par un nœud de log")
        print(f"   📁 Fichier prévu: {file_path}")
        nodes_replaced += 1

    # Sauvegarder le workflow patché
    output_path = workflow_path.parent / "workflow_hellowork_scraper_complet_LOG_SAVE.json"
    print(f"💾 Sauvegarde du workflow patché vers {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"🎉 Workflow patché avec succès !")
    print(f"📁 Nouveau fichier : {output_path}")
    print(f"🔄 {nodes_replaced} nœuds Write Binary File remplacés par des nœuds de log")

    print(f"\n📋 Les données seront loggées dans la console n8n pour :")
    for i, (node_index, old_node) in enumerate(save_nodes_to_replace):
        file_path = old_node.get("parameters", {}).get("filePath", "")
        if file_path:
            filename = Path(file_path).name
            print(f"   📄 {filename}")

    return True

if __name__ == "__main__":
    print("🚀 === PATCH WORKFLOW N8N POUR LOGS DE DÉBOGAGE ===")
    success = patch_workflow()
    if success:
        print("\n✅ Patch terminé avec succès !")
        print("👉 Importez le fichier workflow_hellowork_scraper_complet_LOG_SAVE.json dans n8n")
        print("🎯 Les données seront loggées dans la console n8n au lieu d'être sauvegardées")
        print("📋 Consultez les logs d'exécution n8n pour voir les données de chaque étape")
    else:
        print("\n❌ Erreur lors du patch")