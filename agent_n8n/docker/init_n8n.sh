#!/bin/bash
# Script d'initialisation N8N - Configuration automatique
set -e

echo "🚀 === INITIALISATION N8N AUTOMATIQUE ==="

# Variables
N8N_URL="${N8N_URL:-http://localhost:5678}"
MAX_WAIT_TIME=60
SETUP_SCRIPT="/app/setup_n8n_credentials.py"

# Fonction d'attente N8N
wait_for_n8n() {
    echo "🔄 Attente de N8N sur $N8N_URL..."

    for i in $(seq 1 $MAX_WAIT_TIME); do
        if curl -s "$N8N_URL/healthz" >/dev/null 2>&1; then
            echo "✅ N8N est disponible !"
            return 0
        fi
        echo "⏳ Tentative $i/$MAX_WAIT_TIME..."
        sleep 2
    done

    echo "❌ Timeout: N8N non disponible après ${MAX_WAIT_TIME}s"
    return 1
}

# Fonction de vérification des variables
check_environment() {
    echo "🌍 Vérification des variables d'environnement..."

    local required_vars=(
        "mistral_key_site_emploi"
        "MISTRAL_API_KEY_CURSOR_MCP_SERVER"
        "LOGIN_N8N"
        "PASSWORD_N8N"
    )

    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        else
            echo "  ✅ $var: définie"
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo "⚠️ Variables manquantes: ${missing_vars[*]}"
        return 1
    fi

    echo "✅ Toutes les variables requises sont définies"
    return 0
}

# Fonction d'exécution du script Python
run_python_setup() {
    echo "🐍 Exécution du script de configuration Python..."

    if [ -f "$SETUP_SCRIPT" ]; then
        python3 "$SETUP_SCRIPT"
        return $?
    else
        echo "❌ Script de configuration non trouvé: $SETUP_SCRIPT"
        return 1
    fi
}

# Fonction de création d'un fichier de statut
create_status_file() {
    local status=$1
    local status_file="/app/init_status.json"

    cat > "$status_file" << EOF
{
    "initialization_status": "$status",
    "timestamp": "$(date -Iseconds)",
    "n8n_url": "$N8N_URL",
    "environment_check": "$(check_environment >/dev/null 2>&1 && echo 'passed' || echo 'failed')"
}
EOF

    echo "📄 Statut sauvegardé dans $status_file"
}

# Fonction principale
main() {
    echo "Démarrage à $(date)"

    # Étape 1: Vérifier les variables d'environnement
    if ! check_environment; then
        echo "⚠️ Poursuite malgré les variables manquantes..."
    fi

    # Étape 2: Attendre N8N
    if ! wait_for_n8n; then
        echo "❌ Impossible de joindre N8N, arrêt de l'initialisation"
        create_status_file "failed_n8n_unavailable"
        exit 1
    fi

    # Étape 3: Petite pause pour s'assurer que N8N est complètement prêt
    echo "⏳ Pause de stabilisation..."
    sleep 5

    # Étape 4: Exécuter la configuration Python
    if run_python_setup; then
        echo "🎉 Configuration automatique terminée avec succès !"
        create_status_file "success"
    else
        echo "⚠️ Configuration terminée avec des erreurs"
        create_status_file "completed_with_errors"
    fi

    echo "✅ Initialisation N8N terminée à $(date)"
}

# Point d'entrée
main "$@"