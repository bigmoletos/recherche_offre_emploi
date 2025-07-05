#!/usr/bin/env python3
"""
🚀 SERVEUR DE SAUVEGARDE OUTPUTS N8N
=======================================

Serveur HTTP simple pour recevoir et sauvegarder les outputs des workflows n8n.
Écoute sur le port 8765 et sauvegarde dans le dossier outputs/

Usage:
    python server_save_outputs.py

Endpoints:
    POST /save/{filename} - Sauvegarde le JSON reçu dans outputs/{filename}
"""

import json
import logging
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

# Configuration
SERVER_PORT = 8765
OUTPUT_DIR = Path(__file__).parent / "outputs"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server_save_outputs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SaveHandler(BaseHTTPRequestHandler):
    """Gestionnaire des requêtes de sauvegarde"""

    def log_message(self, format, *args):
        """Désactive les logs automatiques du serveur HTTP"""
        pass

    def do_POST(self):
        """Traite les requêtes POST pour sauvegarder les fichiers"""
        try:
            # Parse de l'URL pour extraire le nom du fichier
            path = urlparse(self.path).path
            if not path.startswith('/save/'):
                self.send_error(404, "Endpoint not found. Use /save/{filename}")
                return

            filename = path[6:]  # Retire '/save/'
            if not filename.endswith('.json'):
                filename += '.json'

            # Lecture du contenu
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)

            try:
                # Validation JSON
                json_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.send_error(400, f"Invalid JSON: {e}")
                return

            # Création du dossier de sortie
            OUTPUT_DIR.mkdir(exist_ok=True)

            # Sauvegarde du fichier
            output_path = OUTPUT_DIR / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            # Réponse de succès
            response = {
                "status": "success",
                "filename": filename,
                "path": str(output_path.absolute()),
                "size": len(post_data),
                "timestamp": datetime.now().isoformat()
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))

            logger.info(f"✅ Sauvegardé: {filename} ({len(post_data)} bytes)")

        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            self.send_error(500, f"Server error: {e}")

    def do_OPTIONS(self):
        """Gestion des requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def run_server():
    """Lance le serveur de sauvegarde"""
    server_address = ('', SERVER_PORT)
    httpd = HTTPServer(server_address, SaveHandler)

    logger.info(f"🚀 Serveur de sauvegarde démarré sur http://localhost:{SERVER_PORT}")
    logger.info(f"📁 Dossier de sortie: {OUTPUT_DIR.absolute()}")
    logger.info("📋 Endpoints disponibles:")
    logger.info(f"   POST http://localhost:{SERVER_PORT}/save/{{filename}}")
    logger.info("🛑 Appuyez sur Ctrl+C pour arrêter")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du serveur demandé")
        httpd.shutdown()
        logger.info("✅ Serveur arrêté")


if __name__ == "__main__":
    run_server()