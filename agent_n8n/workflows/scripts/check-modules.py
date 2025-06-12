#!/opt/venv/bin/python3
"""
Script de vérification des modules Python pour N8N à integrer dans le workflow de n8n
"""

# Script Python pour N8N - Sans subprocess (compatible Emscripten)
import sys
import pkgutil

# Liste des modules attendus avec leurs noms d'import alternatifs
modules_to_check = [('requests', ['requests']),
                    ('beautifulsoup4', ['bs4', 'BeautifulSoup4']),
                    ('python-dotenv', ['dotenv', 'python_dotenv']),
                    ('urllib3', ['urllib3']), ('pandas', ['pandas']),
                    ('datetime', ['datetime']), ('uuid', ['uuid']),
                    ('hashlib', ['hashlib']),
                    ('xml.etree.ElementTree', ['xml.etree.ElementTree']),
                    ('csv', ['csv']), ('numpy', ['numpy']), ('lxml', ['lxml'])]


def check_module(module_display_name, import_names):
    """Teste plusieurs noms d'import possibles pour un module"""
    for import_name in import_names:
        try:
            if '.' in import_name:
                # Pour les modules avec des sous-modules comme xml.etree.ElementTree
                parts = import_name.split('.')
                module = __import__(import_name)
                for part in parts[1:]:
                    module = getattr(module, part)
            else:
                __import__(import_name)
            return True, f"Module {module_display_name} importé via '{import_name}'"
        except ImportError:
            continue
        except Exception as e:
            return False, f"Erreur lors de l'import de {import_name}: {str(e)}"

    return False, f"Module {module_display_name} non trouvé (essayé: {', '.join(import_names)})"


def list_available_modules():
    """Liste les modules disponibles (sans subprocess)"""
    try:
        available = []
        for importer, modname, ispkg in pkgutil.iter_modules():
            available.append(modname)
        return available[:20]  # Limite à 20 pour éviter une liste trop longue
    except:
        return []


# Test des modules
items = []

# Vérification des modules attendus
for module_name, import_names in modules_to_check:
    is_installed, message = check_module(module_name, import_names)
    items.append({
        'json': {
            'module': module_name,
            'status': 'installed' if is_installed else 'not installed',
            'message': message,
            'type': 'expected'
        }
    })

# Ajout des informations système
items.append({
    'json': {
        'module': 'PYTHON_INFO',
        'status': 'info',
        'message': f'Python {sys.version}',
        'type': 'system'
    }
})

items.append({
    'json': {
        'module': 'PYTHON_PATH',
        'status': 'info',
        'message': f'Chemins: {len(sys.path)} entrées',
        'type': 'system'
    }
})

# Liste quelques modules disponibles
available_modules = list_available_modules()
if available_modules:
    items.append({
        'json': {
            'module': 'AVAILABLE_MODULES',
            'status': 'info',
            'message':
            f'Modules détectés: {", ".join(available_modules[:10])}...',
            'type': 'debug'
        }
    })

return items
