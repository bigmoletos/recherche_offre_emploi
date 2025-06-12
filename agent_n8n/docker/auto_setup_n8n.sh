#!/bin/bash
# Script de lancement automatique de la configuration N8N
set -e

echo "🚀 === SETUP AUTOMATIQUE N8N ==="

# Variables
DOCKER_COMPOSE_FILE="docker-compose-custom.yml"
CONTAINER_NAME="n8n_alternance_agent_custom"

# Fonction de vérification des prérequis
check_prerequisites() {
    echo "🔍 Vérification des prérequis..."

    # Vérifier Docker
    if ! command -v docker >/dev/null 2>&1; then
        echo "❌ Docker n'est pas installé"
        exit 1
    fi

    # Vérifier docker-compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        echo "❌ docker-compose n'est pas installé"
        exit 1
    fi

    # Vérifier le fichier docker-compose
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        echo "❌ Fichier docker-compose non trouvé: $DOCKER_COMPOSE_FILE"
        exit 1
    fi

    echo "✅ Prérequis vérifiés"
}

# Fonction de démarrage des conteneurs
start_containers() {
    echo "🐳 Démarrage des conteneurs..."

    # Arrêter les conteneurs existants
    echo "⏹️ Arrêt des conteneurs existants..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down || true

    # Rebuild si nécessaire
    if [ "$1" = "--rebuild" ]; then
        echo "🔨 Rebuild des images..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    fi

    # Démarrer les conteneurs
    echo "▶️ Démarrage des conteneurs..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

    echo "✅ Conteneurs démarrés"
}

# Fonction d'attente des conteneurs
wait_for_containers() {
    echo "⏳ Attente de la disponibilité des conteneurs..."

    local max_wait=60
    local count=0

    while [ $count -lt $max_wait ]; do
        if docker ps | grep -q "$CONTAINER_NAME"; then
            echo "✅ Conteneur N8N démarré"
            break
        fi

        echo "⏳ Attente... ($count/$max_wait)"
        sleep 2
        count=$((count + 1))
    done

    if [ $count -eq $max_wait ]; then
        echo "❌ Timeout: conteneur non démarré après ${max_wait}s"
        return 1
    fi

    # Attendre que N8N soit complètement prêt
    echo "⏳ Attente de N8N (stabilisation)..."
    sleep 10
}

# Fonction d'exécution de la configuration automatique
run_auto_config() {
    echo "🔧 Exécution de la configuration automatique..."

    # Vérifier si l'auto-config est activée
    if [ "${ENABLE_AUTO_CONFIG:-true}" != "true" ]; then
        echo "ℹ️ Auto-configuration désactivée (ENABLE_AUTO_CONFIG != true)"
        return 0
    fi

    # Exécuter le script d'initialisation dans le conteneur
    echo "🐍 Lancement du script de configuration..."
    docker exec "$CONTAINER_NAME" /app/init_n8n.sh

    if [ $? -eq 0 ]; then
        echo "✅ Configuration automatique terminée avec succès"

        # Afficher le statut
        echo "📄 Statut de la configuration:"
        docker exec "$CONTAINER_NAME" cat /app/init_status.json 2>/dev/null || echo "Fichier de statut non trouvé"
    else
        echo "⚠️ Configuration automatique terminée avec des erreurs"
    fi
}

# Fonction d'affichage des informations post-démarrage
show_info() {
    echo "📊 === INFORMATIONS N8N ==="
    echo "🌐 Interface N8N: http://localhost:7080"
    echo "🔐 Authentification: Voir variables LOGIN_N8N / PASSWORD_N8N"
    echo "📁 Logs: docker logs $CONTAINER_NAME"
    echo "🔧 Configuration: docker exec -it $CONTAINER_NAME /app/setup_n8n_credentials.py"
    echo ""
    echo "🛠️ Commandes utiles:"
    echo "  - Voir les logs: docker logs -f $CONTAINER_NAME"
    echo "  - Re-configurer: docker exec $CONTAINER_NAME /app/init_n8n.sh"
    echo "  - Arrêter: docker-compose -f $DOCKER_COMPOSE_FILE down"
}

# Fonction de vérification de la santé
health_check() {
    echo "🩺 Vérification de la santé..."

    # Vérifier le healthcheck Docker
    health_status=$(docker inspect "$CONTAINER_NAME" --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-healthcheck")
    echo "Docker Health: $health_status"

    # Tester l'endpoint N8N
    if curl -s http://localhost:7080/healthz >/dev/null 2>&1; then
        echo "✅ N8N API accessible"
    else
        echo "❌ N8N API non accessible"
    fi
}

# Fonction principale
main() {
    echo "Démarrage du setup automatique N8N à $(date)"

    local rebuild_flag=""
    if [ "$1" = "--rebuild" ]; then
        rebuild_flag="--rebuild"
    fi

    # Étapes du setup
    check_prerequisites
    start_containers "$rebuild_flag"
    wait_for_containers
    run_auto_config
    health_check
    show_info

    echo "🎉 Setup automatique N8N terminé avec succès !"
}

# Point d'entrée avec gestion des arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--rebuild] [--help]"
        echo ""
        echo "Options:"
        echo "  --rebuild    Rebuild les images Docker avant démarrage"
        echo "  --help       Affiche cette aide"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac