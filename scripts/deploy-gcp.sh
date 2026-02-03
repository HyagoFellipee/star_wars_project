#!/bin/bash
# =============================================================================
# Script de Deploy para Google Cloud Platform
# Star Wars API
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (customize these)
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="swapi-api"
REPO_NAME="swapi-repo"
API_KEY="${API_KEY:-}"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 não está instalado. Por favor, instale antes de continuar."
    fi
}

# -----------------------------------------------------------------------------
# Pre-flight Checks
# -----------------------------------------------------------------------------

preflight_checks() {
    log_info "Verificando pré-requisitos..."

    check_command "gcloud"
    check_command "docker"

    if [ -z "$PROJECT_ID" ]; then
        log_error "GCP_PROJECT_ID não definido. Execute: export GCP_PROJECT_ID=seu-projeto"
    fi

    if [ -z "$API_KEY" ]; then
        log_warning "API_KEY não definido. Será gerada uma chave aleatória."
        API_KEY=$(openssl rand -hex 16)
        log_info "API_KEY gerada: $API_KEY"
    fi

    # Check gcloud auth
    if ! gcloud auth list 2>&1 | grep -q "ACTIVE"; then
        log_error "Não autenticado no gcloud. Execute: gcloud auth login"
    fi

    log_success "Pré-requisitos OK"
}

# -----------------------------------------------------------------------------
# Setup GCP Project
# -----------------------------------------------------------------------------

setup_project() {
    log_info "Configurando projeto GCP: $PROJECT_ID"

    gcloud config set project "$PROJECT_ID"

    log_info "Habilitando APIs necessárias..."
    gcloud services enable \
        run.googleapis.com \
        artifactregistry.googleapis.com \
        secretmanager.googleapis.com \
        cloudbuild.googleapis.com \
        --quiet

    log_success "Projeto configurado"
}

# -----------------------------------------------------------------------------
# Setup Artifact Registry
# -----------------------------------------------------------------------------

setup_artifact_registry() {
    log_info "Configurando Artifact Registry..."

    # Check if repo exists
    if ! gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" &> /dev/null; then
        gcloud artifacts repositories create "$REPO_NAME" \
            --repository-format=docker \
            --location="$REGION" \
            --description="Star Wars API Docker images"
        log_success "Repositório criado"
    else
        log_info "Repositório já existe"
    fi

    # Configure Docker auth
    gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

    log_success "Artifact Registry configurado"
}

# -----------------------------------------------------------------------------
# Setup Secrets
# -----------------------------------------------------------------------------

setup_secrets() {
    log_info "Configurando Secret Manager..."

    # Check if secret exists
    if ! gcloud secrets describe api-key &> /dev/null; then
        echo -n "$API_KEY" | gcloud secrets create api-key \
            --replication-policy="automatic" \
            --data-file=-
        log_success "Secret 'api-key' criado"
    else
        log_info "Secret 'api-key' já existe. Atualizando..."
        echo -n "$API_KEY" | gcloud secrets versions add api-key --data-file=-
        log_success "Secret atualizado"
    fi
}

# -----------------------------------------------------------------------------
# Build and Push Docker Image
# -----------------------------------------------------------------------------

build_and_push() {
    log_info "Buildando e fazendo push da imagem Docker..."

    IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

    # Navigate to api directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR/../api"

    # Build
    log_info "Building image..."
    docker build -t "${IMAGE_PATH}:latest" .

    # Push
    log_info "Pushing image..."
    docker push "${IMAGE_PATH}:latest"

    log_success "Imagem publicada: ${IMAGE_PATH}:latest"

    cd - > /dev/null
}

# -----------------------------------------------------------------------------
# Deploy to Cloud Run
# -----------------------------------------------------------------------------

deploy_cloud_run() {
    log_info "Fazendo deploy no Cloud Run..."

    IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

    gcloud run deploy "$SERVICE_NAME" \
        --image="${IMAGE_PATH}:latest" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --port=8000 \
        --memory=512Mi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=10 \
        --set-env-vars="SWAPI_BASE_URL=https://swapi.dev/api,LOG_LEVEL=INFO,CACHE_TTL_SECONDS=300,CORS_ORIGINS=[\"*\"]" \
        --set-secrets="API_KEY=api-key:latest" \
        --quiet

    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format='value(status.url)')

    log_success "Deploy concluído!"
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  DEPLOY REALIZADO COM SUCESSO!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "  ${BLUE}URL da API:${NC} $SERVICE_URL"
    echo -e "  ${BLUE}API Key:${NC}    $API_KEY"
    echo ""
    echo -e "  ${YELLOW}Teste com:${NC}"
    echo -e "  curl -H \"X-API-Key: $API_KEY\" $SERVICE_URL/characters/"
    echo ""
}

# -----------------------------------------------------------------------------
# Test Deployment
# -----------------------------------------------------------------------------

test_deployment() {
    log_info "Testando deployment..."

    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format='value(status.url)')

    # Test health endpoint
    log_info "Testando /health..."
    if curl -s "${SERVICE_URL}/health" | grep -q "ok"; then
        log_success "Health check OK"
    else
        log_warning "Health check falhou"
    fi

    # Test characters endpoint
    log_info "Testando /characters/..."
    RESPONSE=$(curl -s -H "X-API-Key: $API_KEY" "${SERVICE_URL}/characters/?page=1")
    if echo "$RESPONSE" | grep -q "results"; then
        log_success "Endpoint /characters/ OK"
    else
        log_warning "Endpoint /characters/ pode ter problemas"
        echo "$RESPONSE"
    fi
}

# -----------------------------------------------------------------------------
# Deploy Frontend to Cloud Storage
# -----------------------------------------------------------------------------

deploy_frontend() {
    log_info "Fazendo deploy do frontend no Cloud Storage..."

    BUCKET_NAME="${FRONTEND_BUCKET:-swapi-frontend-${PROJECT_ID}}"
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Get Cloud Run URL for .env.production
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format='value(status.url)' 2>/dev/null || echo "")

    if [ -z "$SERVICE_URL" ]; then
        log_error "Backend não está deployed. Execute 'deploy' primeiro."
    fi

    cd "$SCRIPT_DIR/../web"

    # Create .env.production
    log_info "Configurando variáveis de ambiente do frontend..."
    cat > .env.production << EOF
VITE_API_URL=${SERVICE_URL}
VITE_API_KEY=${API_KEY}
EOF

    # Build frontend
    log_info "Building frontend..."
    npm install
    npm run build

    # Create bucket if not exists
    if ! gsutil ls "gs://${BUCKET_NAME}" &> /dev/null; then
        log_info "Criando bucket ${BUCKET_NAME}..."
        gsutil mb -l "$REGION" "gs://${BUCKET_NAME}"
        gsutil web set -m index.html -e index.html "gs://${BUCKET_NAME}"
        gsutil iam ch allUsers:objectViewer "gs://${BUCKET_NAME}"
    fi

    # Upload files
    log_info "Uploading arquivos..."
    gsutil -h "Cache-Control:no-cache, max-age=0" -m cp -r dist/* "gs://${BUCKET_NAME}/"

    FRONTEND_URL="https://storage.googleapis.com/${BUCKET_NAME}/index.html"

    log_success "Frontend deployed!"
    echo ""
    echo -e "  ${BLUE}URL do Frontend:${NC} $FRONTEND_URL"
    echo ""

    cd - > /dev/null
}

# -----------------------------------------------------------------------------
# Cleanup (for development)
# -----------------------------------------------------------------------------

cleanup() {
    log_warning "Removendo recursos do GCP..."

    read -p "Tem certeza? Isso vai deletar o serviço Cloud Run. (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud run services delete "$SERVICE_NAME" --region="$REGION" --quiet || true
        gcloud secrets delete api-key --quiet || true
        log_success "Recursos removidos"
    else
        log_info "Operação cancelada"
    fi
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy    Full backend deployment (default)"
    echo "  frontend  Deploy frontend to Cloud Storage"
    echo "  all       Deploy backend + frontend"
    echo "  build     Only build and push Docker image"
    echo "  test      Test existing deployment"
    echo "  cleanup   Remove GCP resources"
    echo "  help      Show this help"
    echo ""
    echo "Environment variables:"
    echo "  GCP_PROJECT_ID  GCP Project ID (required)"
    echo "  GCP_REGION      GCP Region (default: us-central1)"
    echo "  API_KEY         API Key for authentication"
    echo ""
    echo "Example:"
    echo "  export GCP_PROJECT_ID=my-project"
    echo "  export API_KEY=my-secret-key"
    echo "  $0 deploy"
}

main() {
    case "${1:-deploy}" in
        deploy)
            preflight_checks
            setup_project
            setup_artifact_registry
            setup_secrets
            build_and_push
            deploy_cloud_run
            test_deployment
            ;;
        frontend)
            preflight_checks
            deploy_frontend
            ;;
        all)
            preflight_checks
            setup_project
            setup_artifact_registry
            setup_secrets
            build_and_push
            deploy_cloud_run
            test_deployment
            deploy_frontend
            ;;
        build)
            preflight_checks
            setup_artifact_registry
            build_and_push
            ;;
        test)
            preflight_checks
            test_deployment
            ;;
        cleanup)
            preflight_checks
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Comando desconhecido: $1"
            show_help
            ;;
    esac
}

main "$@"
