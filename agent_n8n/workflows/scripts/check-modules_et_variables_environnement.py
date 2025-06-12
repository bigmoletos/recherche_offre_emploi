# Script final - Détection modules + variables d'environnement N8N
import sys
import os

# Variables d'environnement attendues dans N8N
expected_env_vars = {
    # Variables N8N
    'LOGIN_N8N': 'Identifiant N8N',
    'PASSWORD_N8N': 'Mot de passe N8N',
    'N8N_ENCRYPTION_KEY': 'Clé de chiffrement N8N',

    # Variables Mistral
    'mistral_key_site_emploi': 'Clé API Mistral pour scraping emploi',
    'MISTRAL_API_KEY_CURSOR_MCP_SERVER': 'Clé API Mistral pour serveur MCP',

    # Variables système
    'NODE_ENV': 'Environnement Node.js',
    'N8N_LOG_LEVEL': 'Niveau de logs N8N'
}

# Modules disponibles dans N8N Pyodide
core_modules = [
    ('requests', ['requests'], 'Requêtes HTTP'),
    ('beautifulsoup4', ['bs4', 'beautifulsoup4'], 'Parsing HTML/XML'),
    ('urllib3', ['urllib3'], 'HTTP client bas niveau'),
    ('pandas', ['pandas'], 'Manipulation données'),
    ('numpy', ['numpy'], 'Calculs numériques'),
    ('datetime', ['datetime'], 'Gestion dates/temps'),
    ('uuid', ['uuid'], 'Génération UUID'),
    ('hashlib', ['hashlib'], 'Fonctions de hachage'),
    ('xml.etree.ElementTree', ['xml.etree.ElementTree'], 'Parser XML'),
    ('csv', ['csv'], 'Lecture/écriture CSV'),
    ('json', ['json'], 'Manipulation JSON'),
    ('re', ['re'], 'Expressions régulières'),
    ('base64', ['base64'], 'Encodage base64'),
    ('urllib.parse', ['urllib.parse'], 'Parsing URLs')
]

def check_module_pyodide_advanced(module_display_name, import_names):
    """Test d'import ultra-avancé spécialement pour Pyodide N8N"""
    errors = []

    for import_name in import_names:
        try:
            # Méthode 1: Import avec exec pour Pyodide
            namespace = {}
            exec(f"import {import_name}", namespace)
            if import_name in namespace:
                return True, f"✅ {module_display_name} opérationnel (exec)"

        except Exception as e:
            errors.append(f"exec-{import_name}: {str(e)[:50]}")

        try:
            # Méthode 2: Import classique
            if '.' in import_name:
                parts = import_name.split('.')
                module = __import__(import_name)
                for part in parts[1:]:
                    module = getattr(module, part)
            else:
                module = __import__(import_name)

            # Test d'utilisation réelle du module
            if import_name == 'requests' and hasattr(module, 'get'):
                return True, f"✅ {module_display_name} opérationnel (import+test)"
            elif import_name in ['bs4', 'beautifulsoup4'] and (hasattr(module, 'BeautifulSoup') or hasattr(module, 'BeautifulSoup4')):
                return True, f"✅ {module_display_name} opérationnel (import+test)"
            elif import_name == 'pandas' and hasattr(module, 'DataFrame'):
                return True, f"✅ {module_display_name} opérationnel (import+test)"
            elif import_name == 'numpy' and hasattr(module, 'array'):
                return True, f"✅ {module_display_name} opérationnel (import+test)"
            elif import_name == 'urllib3' and hasattr(module, 'PoolManager'):
                return True, f"✅ {module_display_name} opérationnel (import+test)"
            elif import_name not in ['requests', 'bs4', 'beautifulsoup4', 'pandas', 'numpy', 'urllib3']:
                return True, f"✅ {module_display_name} opérationnel (import)"

        except Exception as e:
            errors.append(f"import-{import_name}: {str(e)[:50]}")

        try:
            # Méthode 3: Vérification via sys.modules avec patterns
            for module_key in sys.modules.keys():
                if import_name == module_key or module_key.startswith(f"{import_name}."):
                    return True, f"✅ {module_display_name} détecté (sys.modules: {module_key})"

        except Exception as e:
            errors.append(f"sys-{import_name}: {str(e)[:50]}")

    # Si toujours pas trouvé, afficher les erreurs pour debug
    error_summary = " | ".join(errors[:2])  # Limiter pour lisibilité
    return False, f"❌ {module_display_name} non disponible ({error_summary})"

def check_env_vars():
    """Vérification des variables d'environnement"""
    env_results = []

    for var_name, description in expected_env_vars.items():
        value = os.environ.get(var_name)

        if value:
            # Masquer les secrets pour la sécurité
            if 'key' in var_name.lower() or 'password' in var_name.lower():
                display_value = f"***{value[-4:]}" if len(value) > 4 else "***"
            else:
                display_value = value

            env_results.append({
                'name': var_name,
                'status': 'found',
                'message': f'✅ {description} définie',
                'value': display_value
            })
        else:
            env_results.append({
                'name': var_name,
                'status': 'missing',
                'message': f'❌ {description} manquante',
                'value': 'N/A'
            })

    return env_results

def create_dotenv_alternative():
    """Alternative dotenv avec accès aux variables N8N"""
    try:
        # Test d'accès aux variables d'environnement
        available_vars = [
            var for var in expected_env_vars.keys() if os.environ.get(var)
        ]

        if available_vars:
            return True, f"✅ Alternative dotenv: accès à {len(available_vars)} variables"
        else:
            return False, "❌ Aucune variable d'environnement accessible"
    except Exception as e:
        return False, f"❌ Erreur dotenv alternative: {str(e)}"

def get_pyodide_modules_info():
    """Informations détaillées sur les modules Pyodide chargés"""
    try:
        # Recherche de modules suspects
        pyodide_modules = []
        target_modules = ['requests', 'bs4', 'beautifulsoup4', 'urllib3', 'pandas', 'numpy', 'certifi', 'charset', 'idna']

        for module_name in sys.modules.keys():
            for target in target_modules:
                if target in module_name.lower():
                    pyodide_modules.append(module_name)
                    break

        # Information sur le total des modules chargés
        total_modules = len(sys.modules)

        if pyodide_modules:
            return True, f"✅ {len(pyodide_modules)} modules Pyodide: {', '.join(pyodide_modules[:3])}... (Total: {total_modules})"
        else:
            return False, f"❌ Aucun module Pyodide détecté sur {total_modules} modules système"
    except Exception as e:
        return False, f"❌ Erreur détection Pyodide: {str(e)}"

def test_direct_imports():
    """Test direct des imports critiques pour diagnostic"""
    test_results = []

    # Test requests direct
    try:
        import requests
        test_results.append("requests: ✅ OK")
    except Exception as e:
        test_results.append(f"requests: ❌ {str(e)[:30]}")

    # Test beautifulsoup4 direct
    try:
        from bs4 import BeautifulSoup
        test_results.append("bs4: ✅ OK")
    except Exception as e:
        test_results.append(f"bs4: ❌ {str(e)[:30]}")

    # Test pandas direct
    try:
        import pandas
        test_results.append("pandas: ✅ OK")
    except Exception as e:
        test_results.append(f"pandas: ❌ {str(e)[:30]}")

    return " | ".join(test_results[:3])

# Tests principaux - Exécution directe pour N8N
items = []

# 1. MODULES PYTHON
installed_count = 0
for module_name, import_names, description in core_modules:
    is_installed, message = check_module_pyodide_advanced(module_name, import_names)
    if is_installed:
        installed_count += 1

    items.append({
        'json': {
            'module': module_name,
            'status': 'installed' if is_installed else 'not installed',
            'message': message,
            'description': description,
            'type': 'module'
        }
    })

# 2. TEST DIRECT IMPORTS
direct_test_result = test_direct_imports()
items.append({
    'json': {
        'module': 'TEST_IMPORTS_DIRECT',
        'status': 'info',
        'message': direct_test_result,
        'description': 'Tests directs d\'import pour diagnostic',
        'type': 'diagnostic'
    }
})

# 3. ALTERNATIVE DOTENV
dotenv_success, dotenv_message = create_dotenv_alternative()
items.append({
    'json': {
        'module': 'python-dotenv (alternative)',
        'status': 'alternative_available' if dotenv_success else 'not available',
        'message': dotenv_message,
        'description': 'Gestion variables environnement',
        'type': 'alternative'
    }
})

# 4. INFORMATIONS PYODIDE
pyodide_success, pyodide_message = get_pyodide_modules_info()
items.append({
    'json': {
        'module': 'PYODIDE_MODULES',
        'status': 'info',
        'message': pyodide_message,
        'description': 'Modules chargés dans sys.modules',
        'type': 'pyodide'
    }
})

# 5. VARIABLES D'ENVIRONNEMENT
env_results = check_env_vars()
found_vars = sum(1 for result in env_results if result['status'] == 'found')

for result in env_results:
    items.append({
        'json': {
            'module': result['name'],
            'status': result['status'],
            'message': result['message'],
            'description': f"Valeur: {result['value']}",
            'type': 'environment'
        }
    })

# 6. RÉSUMÉ MODULES
items.append({
    'json': {
        'module': 'RÉSUMÉ_MODULES',
        'status': 'info',
        'message': f'Modules Python: {installed_count}/{len(core_modules)} disponibles',
        'description': 'Environnement N8N Pyodide optimisé',
        'type': 'summary'
    }
})

# 7. RÉSUMÉ VARIABLES
items.append({
    'json': {
        'module': 'RÉSUMÉ_ENVIRONNEMENT',
        'status': 'info',
        'message': f'Variables: {found_vars}/{len(expected_env_vars)} définies',
        'description': 'Configuration N8N et secrets',
        'type': 'summary'
    }
})

# 8. INFORMATIONS SYSTÈME
items.append({
    'json': {
        'module': 'SYSTÈME',
        'status': 'info',
        'message': f'Python {sys.version.split()[0]} - Pyodide WebAssembly',
        'description': 'Environnement d\'exécution N8N',
        'type': 'system'
    }
})

# 9. RECOMMANDATIONS
items.append({
    'json': {
        'module': 'RECOMMANDATION',
        'status': 'info',
        'message': 'Variables env: ${{$env.VARIABLE_NAME}} | Secrets: Credentials Store N8N',
        'description': 'Bonnes pratiques N8N',
        'type': 'tip'
    }
})

# Retour pour N8N - Variable globale items
return items
