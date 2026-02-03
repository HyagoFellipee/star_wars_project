# Guia de Deploy no Google Cloud Platform (GCP)

Este guia detalha o processo completo para fazer deploy da aplicação Star Wars API no GCP.

## Arquitetura Proposta

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│   Usuário   │────▶│ API Gateway  │────▶│  Cloud Run  │────▶│  SWAPI   │
│             │     │  (opcional)  │     │  (FastAPI)  │     │ (externo)│
└─────────────┘     └──────────────┘     └─────────────┘     └──────────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │   Secret    │
                                         │   Manager   │
                                         └─────────────┘
```

**Opções de deploy:**
- **Cloud Run** (recomendado para FastAPI) - Container Docker gerenciado
- **Cloud Functions** - Melhor para funções simples, não ideal para FastAPI
- **API Gateway** - Camada de segurança e rate limiting (opcional)

---

## Pré-requisitos

### 1. Instalar Google Cloud CLI

```bash
# Linux (Debian/Ubuntu)
curl https://sdk.cloud.google.com | bash

# Reiniciar o terminal ou executar:
exec -l $SHELL

# Verificar instalação
gcloud --version
```

### 2. Autenticar no GCP

```bash
# Login interativo (abre navegador)
gcloud auth login

# Configurar Application Default Credentials (para SDKs)
gcloud auth application-default login
```

### 3. Criar ou Selecionar Projeto

```bash
# Listar projetos existentes
gcloud projects list

# Criar novo projeto (escolha um ID único)
gcloud projects create swapi-project --name="Star Wars API"

# Selecionar o projeto
gcloud config set project swapi-project

# Verificar projeto atual
gcloud config get-value project
```

### 4. Configurar Billing (Obrigatório)

```bash
# Listar contas de billing
gcloud billing accounts list

# Vincular billing ao projeto (substitua BILLING_ACCOUNT_ID)
gcloud billing projects link swapi-project \
  --billing-account=BILLING_ACCOUNT_ID
```

> **Nota:** Sem billing vinculado, os serviços não funcionam. O free tier do GCP é generoso para testes.

---

## Parte 1: Deploy do Backend (Cloud Run)

### 1.1 Habilitar APIs Necessárias

```bash
# Habilitar APIs do Cloud Run, Container Registry e Secret Manager
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com
```

### 1.2 Criar Repositório no Artifact Registry

```bash
# Criar repositório para imagens Docker
gcloud artifacts repositories create swapi-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Star Wars API Docker images"

# Configurar Docker para usar Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 1.3 Criar Secrets no Secret Manager

```bash
# Criar secret para API Key (substitua pelo seu valor)
echo -n "sua-api-key-segura-aqui" | gcloud secrets create api-key \
  --replication-policy="automatic" \
  --data-file=-

# Verificar que foi criado
gcloud secrets list
```

### 1.4 Build e Push da Imagem Docker

```bash
# Navegar para o diretório da API
cd /home/hyago/GitRepos/Pessoal/star_wars_project/api

# Definir variáveis
PROJECT_ID=$(gcloud config get-value project)
REGION=us-central1
IMAGE_NAME=swapi-api

# Build da imagem
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/swapi-repo/${IMAGE_NAME}:latest .

# Push para Artifact Registry
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/swapi-repo/${IMAGE_NAME}:latest
```

**Alternativa: Build direto no Cloud Build**

```bash
# Build usando Cloud Build (sem Docker local)
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/swapi-repo/${IMAGE_NAME}:latest
```

### 1.5 Deploy no Cloud Run

```bash
# Deploy com configurações
gcloud run deploy swapi-api \
  --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/swapi-repo/${IMAGE_NAME}:latest \
  --region=${REGION} \
  --platform=managed \
  --allow-unauthenticated \
  --port=8000 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --set-env-vars="SWAPI_BASE_URL=https://swapi.dev/api,LOG_LEVEL=INFO,CACHE_TTL_SECONDS=300" \
  --set-secrets="API_KEY=api-key:latest"

# Obter URL do serviço
gcloud run services describe swapi-api --region=${REGION} --format='value(status.url)'
```

### 1.6 Testar o Deploy

```bash
# Obter URL
SERVICE_URL=$(gcloud run services describe swapi-api --region=${REGION} --format='value(status.url)')

# Testar health check
curl ${SERVICE_URL}/health

# Testar endpoint de characters (com API key)
curl -H "X-API-Key: sua-api-key-segura-aqui" ${SERVICE_URL}/characters/
```

---

## Parte 2: API Gateway (Opcional, mas recomendado)

O API Gateway adiciona:
- Rate limiting
- Autenticação centralizada
- Métricas e logging
- Versionamento de API

### 2.1 Habilitar API Gateway

```bash
gcloud services enable \
  apigateway.googleapis.com \
  servicemanagement.googleapis.com \
  servicecontrol.googleapis.com
```

### 2.2 Criar Especificação OpenAPI

Criar arquivo `api-gateway-config.yaml`:

```yaml
# api-gateway-config.yaml
swagger: '2.0'
info:
  title: Star Wars API Gateway
  description: API Gateway for Star Wars API
  version: '1.0.0'
schemes:
  - https
produces:
  - application/json
x-google-backend:
  address: https://swapi-api-HASH-uc.a.run.app  # Substituir pela URL do Cloud Run
  protocol: h2
securityDefinitions:
  api_key:
    type: apiKey
    name: X-API-Key
    in: header
security:
  - api_key: []
paths:
  /characters:
    get:
      summary: List characters
      operationId: listCharacters
      responses:
        '200':
          description: Success
  /characters/{id}:
    get:
      summary: Get character by ID
      operationId: getCharacter
      parameters:
        - name: id
          in: path
          required: true
          type: integer
      responses:
        '200':
          description: Success
  /planets:
    get:
      summary: List planets
      operationId: listPlanets
      responses:
        '200':
          description: Success
  /planets/{id}:
    get:
      summary: Get planet by ID
      operationId: getPlanet
      parameters:
        - name: id
          in: path
          required: true
          type: integer
      responses:
        '200':
          description: Success
  /starships:
    get:
      summary: List starships
      operationId: listStarships
      responses:
        '200':
          description: Success
  /starships/{id}:
    get:
      summary: Get starship by ID
      operationId: getStarship
      parameters:
        - name: id
          in: path
          required: true
          type: integer
      responses:
        '200':
          description: Success
  /films:
    get:
      summary: List films
      operationId: listFilms
      responses:
        '200':
          description: Success
  /films/{id}:
    get:
      summary: Get film by ID
      operationId: getFilm
      parameters:
        - name: id
          in: path
          required: true
          type: integer
      responses:
        '200':
          description: Success
```

### 2.3 Criar API Config e Gateway

```bash
# Criar API
gcloud api-gateway apis create swapi-gateway \
  --display-name="Star Wars API Gateway"

# Criar API Config
gcloud api-gateway api-configs create swapi-config-v1 \
  --api=swapi-gateway \
  --openapi-spec=api-gateway-config.yaml \
  --display-name="SWAPI Config v1"

# Criar Gateway
gcloud api-gateway gateways create swapi-gw \
  --api=swapi-gateway \
  --api-config=swapi-config-v1 \
  --location=${REGION} \
  --display-name="Star Wars API Gateway"

# Obter URL do Gateway
gcloud api-gateway gateways describe swapi-gw \
  --location=${REGION} \
  --format='value(defaultHostname)'
```

---

## Parte 3: Deploy do Frontend (Cloud Storage + CDN)

### 3.1 Build do Frontend

```bash
cd /home/hyago/GitRepos/Pessoal/star_wars_project/web

# Configurar URL da API para produção
echo "VITE_API_URL=https://swapi-api-HASH-uc.a.run.app" > .env.production
echo "VITE_API_KEY=sua-api-key-segura-aqui" >> .env.production

# Build
npm run build
```

### 3.2 Criar Bucket e Upload

```bash
# Criar bucket (nome deve ser único globalmente)
BUCKET_NAME=swapi-frontend
gsutil mb -l ${REGION} gs://${BUCKET_NAME}

# Configurar como website
gsutil web set -m index.html -e index.html gs://${BUCKET_NAME}

# Upload dos arquivos
gsutil -m cp -r dist/* gs://${BUCKET_NAME}/

# Tornar público
gsutil iam ch allUsers:objectViewer gs://${BUCKET_NAME}
```

### 3.3 Configurar Load Balancer + CDN (Produção)

```bash
# Criar backend bucket
gcloud compute backend-buckets create swapi-frontend-backend \
  --gcs-bucket-name=${BUCKET_NAME} \
  --enable-cdn

# Criar URL map
gcloud compute url-maps create swapi-frontend-lb \
  --default-backend-bucket=swapi-frontend-backend

# Criar proxy HTTPS
gcloud compute target-http-proxies create swapi-frontend-proxy \
  --url-map=swapi-frontend-lb

# Criar forwarding rule
gcloud compute forwarding-rules create swapi-frontend-rule \
  --global \
  --target-http-proxy=swapi-frontend-proxy \
  --ports=80
```

---

## Parte 4: CI/CD com Cloud Build (Opcional)

### 4.1 Criar cloudbuild.yaml

```yaml
# cloudbuild.yaml (na raiz do projeto)
steps:
  # Build e push da imagem Docker
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/swapi-repo/swapi-api:$COMMIT_SHA'
      - '-t'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/swapi-repo/swapi-api:latest'
      - './api'

  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '--all-tags'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/swapi-repo/swapi-api'

  # Deploy no Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'swapi-api'
      - '--image=${_REGION}-docker.pkg.dev/$PROJECT_ID/swapi-repo/swapi-api:$COMMIT_SHA'
      - '--region=${_REGION}'
      - '--platform=managed'

substitutions:
  _REGION: us-central1

images:
  - '${_REGION}-docker.pkg.dev/$PROJECT_ID/swapi-repo/swapi-api:$COMMIT_SHA'
  - '${_REGION}-docker.pkg.dev/$PROJECT_ID/swapi-repo/swapi-api:latest'
```

### 4.2 Configurar Trigger

```bash
# Conectar repositório GitHub
gcloud builds repositories create swapi-repo-github \
  --remote-uri=https://github.com/SEU_USUARIO/star_wars_project \
  --connection=github-connection \
  --region=${REGION}

# Criar trigger para branch main
gcloud builds triggers create github \
  --name="deploy-on-push" \
  --repository=projects/${PROJECT_ID}/locations/${REGION}/connections/github-connection/repositories/swapi-repo-github \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml"
```

---

## Custos Estimados (Free Tier)

| Serviço | Free Tier | Custo Além |
|---------|-----------|------------|
| Cloud Run | 2M requests/mês, 360k vCPU-sec | ~$0.00002/request |
| Artifact Registry | 500MB | $0.10/GB/mês |
| Cloud Storage | 5GB | $0.026/GB/mês |
| API Gateway | 2M calls/mês | $3.00/milhão |
| Cloud Build | 120 min/dia | $0.003/min |

**Estimativa mensal para projeto de teste: $0 - $5**

---

## Comandos Úteis

```bash
# Ver logs do Cloud Run
gcloud run services logs read swapi-api --region=${REGION}

# Ver logs em tempo real
gcloud run services logs tail swapi-api --region=${REGION}

# Listar revisões
gcloud run revisions list --service=swapi-api --region=${REGION}

# Rollback para revisão anterior
gcloud run services update-traffic swapi-api \
  --to-revisions=swapi-api-REVISION=100 \
  --region=${REGION}

# Deletar serviço
gcloud run services delete swapi-api --region=${REGION}

# Ver métricas
gcloud monitoring dashboards list
```

---

## Checklist de Deploy

- [ ] Projeto GCP criado e billing configurado
- [ ] APIs habilitadas (Cloud Run, Artifact Registry, etc.)
- [ ] Secret Manager com API_KEY configurado
- [ ] Imagem Docker buildada e pushed
- [ ] Cloud Run deployed e funcionando
- [ ] (Opcional) API Gateway configurado
- [ ] (Opcional) Frontend deployed no Cloud Storage
- [ ] Testes de endpoint funcionando
- [ ] CORS configurado para domínio do frontend

---

## Troubleshooting

### Erro: "Permission denied"
```bash
# Verificar IAM roles
gcloud projects get-iam-policy ${PROJECT_ID}

# Adicionar role necessária
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="user:seu-email@gmail.com" \
  --role="roles/run.admin"
```

### Erro: "Container failed to start"
```bash
# Ver logs detalhados
gcloud run services logs read swapi-api --region=${REGION} --limit=50

# Testar container localmente
docker run -p 8000:8000 -e API_KEY=test ${IMAGE}
```

### Erro: "CORS blocked"
Verificar variável `CORS_ORIGINS` no Cloud Run:
```bash
gcloud run services update swapi-api \
  --region=${REGION} \
  --set-env-vars="CORS_ORIGINS=[\"https://seu-frontend.com\"]"
```
