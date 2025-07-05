#!/usr/bin/env python3
"""
🔧 PATCH WORKFLOW - SAUVEGARDE NATIVE N8N
==========================================

Script pour ajouter des nœuds de sauvegarde native utilisant Write Binary File
avec conversion JSON vers Buffer correcte.

Usage:
    python patch_workflow_native_save.py
"""

import json
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_save_node(node_name: str, input_node: str, position: tuple, save_filename: str) -> dict:
    """
    Crée un nœud de sauvegarde utilisant Write Binary File avec conversion JSON correcte

    Args:
        node_name: Nom du nœud de sauvegarde
        input_node: Nom du nœud d'entrée
        position: Tuple (x, y) pour la position
        save_filename: Nom du fichier à sauvegarder

    Returns:
        dict: Configuration du nœud de sauvegarde
    """
    return {
        "parameters": {
            "fileName": f"outputs/{save_filename}",
            "options": {}
        },
        "id": f"save_{node_name.lower().replace(' ', '_')}",
        "name": f"Save {node_name}",
        "type": "n8n-nodes-base.writeBinaryFile",
        "typeVersion": 1,
        "position": list(position),
        "executeOnce": False
    }

def create_json_to_buffer_node(node_name: str, input_node: str, position: tuple) -> dict:
    """
    Crée un nœud Code pour convertir JSON en Buffer pour Write Binary File

    Args:
        node_name: Nom du nœud
        input_node: Nom du nœud d'entrée
        position: Tuple (x, y) pour la position

    Returns:
        dict: Configuration du nœud de conversion
    """
    conversion_code = '''
// Conversion JSON vers Buffer pour sauvegarde
const data = $input.all();
const jsonString = JSON.stringify(data, null, 2);
const buffer = Buffer.from(jsonString, 'utf8');

return [{
  binary: {
    data: {
      data: buffer.toString('base64'),
      mimeType: 'application/json',
      fileName: 'output.json'
    }
  }
}];
'''

    return {
        "parameters": {
            "jsCode": conversion_code
        },
        "id": f"convert_{node_name.lower().replace(' ', '_')}",
        "name": f"Convert {node_name}",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": list(position),
        "executeOnce": False
    }

def add_save_nodes_to_workflow(workflow_path: str) -> bool:
    """
    Ajoute les nœuds de sauvegarde au workflow

    Args:
        workflow_path: Chemin vers le fichier workflow

    Returns:
        bool: True si succès, False sinon
    """
    try:
        # Lecture du workflow
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        logger.info(f"📖 Workflow chargé: {len(workflow.get('nodes', []))} nœuds")

        # Configuration des nœuds à sauvegarder
        save_configs = [
            # (nom_noeud_source, nom_affichage, filename, position_convert, position_save)
            ("Config HelloWork", "Config HelloWork", "01_config_hellowork.json", (880, 240), (1080, 240)),
            ("Fetch Page", "Fetch Page", "02_fetch_page.json", (880, 340), (1080, 340)),
            ("Extraire Conteneur", "Extraire Conteneur", "03_extraire_conteneur.json", (880, 440), (1080, 440)),
            ("Scraper Liste Offres", "Scraper Liste Offres", "04_scraper_liste_offres.json", (880, 540), (1080, 540)),
            ("Filtrer Offres Valides", "Filtrer Offres Valides", "05_filtrer_offres_valides.json", (880, 640), (1080, 640)),
            ("Fetch Detail Offre", "Fetch Detail Offre", "06_fetch_detail_offre.json", (880, 740), (1080, 740)),
            ("Scraper Detail Offre", "Scraper Detail Offre", "07_scraper_detail_offre.json", (880, 840), (1080, 840)),
            ("Preparer Mistral", "Preparer Mistral", "08_preparer_mistral.json", (880, 940), (1080, 940)),
            ("API Mistral", "API Mistral", "09_api_mistral.json", (880, 1040), (1080, 1040)),
            ("Stocker Offre Finale", "Stocker Offre Finale", "10_stocker_offre_finale.json", (880, 1140), (1080, 1140)),
            ("Gérer Erreurs", "Gérer Erreurs", "11_gerer_erreurs.json", (880, 1240), (1080, 1240)),
            ("Fin de Boucle", "Fin de Boucle", "12_fin_de_boucle.json", (880, 1340), (1080, 1340))
        ]

        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', {})

        # Recherche des nœuds existants
        existing_nodes = {node['name']: node for node in nodes}

        logger.info(f"🔍 Nœuds existants: {list(existing_nodes.keys())}")

        # Ajout des nouveaux nœuds
        new_nodes_added = 0

        for source_name, display_name, filename, convert_pos, save_pos in save_configs:
            if source_name in existing_nodes:
                # Créer le nœud de conversion JSON vers Buffer
                convert_node = create_json_to_buffer_node(display_name, source_name, convert_pos)

                # Créer le nœud de sauvegarde
                save_node = create_save_node(display_name, convert_node['id'], save_pos, filename)

                # Ajouter les nœuds
                nodes.append(convert_node)
                nodes.append(save_node)

                # Créer les connexions
                source_node_id = existing_nodes[source_name]['id']

                # Connexion: source -> convert
                if source_node_id not in connections:
                    connections[source_node_id] = {}
                if 'main' not in connections[source_node_id]:
                    connections[source_node_id]['main'] = [[]]

                # Ajouter la connexion vers le convertisseur
                connections[source_node_id]['main'][0].append({
                    "node": convert_node['id'],
                    "type": "main",
                    "index": 0
                })

                # Connexion: convert -> save
                connections[convert_node['id']] = {
                    "main": [[{
                        "node": save_node['id'],
                        "type": "main",
                        "index": 0
                    }]]
                }

                new_nodes_added += 2
                logger.info(f"✅ Ajouté sauvegarde pour: {source_name}")
            else:
                logger.warning(f"⚠️  Nœud non trouvé: {source_name}")

        # Mise à jour du workflow
        workflow['nodes'] = nodes
        workflow['connections'] = connections

        # Sauvegarde du workflow modifié
        output_path = workflow_path.replace('.json', '_NATIVE_SAVE.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)

        logger.info(f"🎉 Workflow modifié sauvegardé: {output_path}")
        logger.info(f"📊 {new_nodes_added} nouveaux nœuds ajoutés")

        # Création du dossier outputs
        outputs_dir = Path(workflow_path).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Dossier outputs créé: {outputs_dir}")

        return True

    except Exception as e:
        logger.error(f"❌ Erreur lors de la modification: {e}")
        return False

def main():
    """Fonction principale"""
    workflow_path = "workflow_hellowork_scraper_complet.json"

    if not Path(workflow_path).exists():
        logger.error(f"❌ Fichier workflow non trouvé: {workflow_path}")
        return False

    logger.info("🚀 Début de l'ajout des nœuds de sauvegarde native...")

    success = add_save_nodes_to_workflow(workflow_path)

    if success:
        logger.info("✅ Modification terminée avec succès!")
        logger.info("📋 Prochaines étapes:")
        logger.info("   1. Importer le nouveau workflow dans n8n")
        logger.info("   2. Activer le workflow")
        logger.info("   3. Exécuter et vérifier les sauvegardes dans outputs/")
    else:
        logger.error("❌ Échec de la modification")

    return success

if __name__ == "__main__":
    main()