# ContentPilot AI - Deployment & Infrastructure Specification

## 1. Overview

ContentPilot AI is containerized using multi-stage Docker builds and orchestrated via Docker Compose for local environments, and Kubernetes / AWS ECS for enterprise cloud production deployments.

---

## 2. Multi-Stage Dockerfile Specifications

### 2.1 Backend Dockerfile (`backend/Dockerfile`)

```dockerfile
# Stage 1: Build & Dependency Installation
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final Production Runtime (with Playwright headless browser support)
FROM python:3.12-slim AS final

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/install/bin:${PATH}" \
    PYTHONPATH="/app"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /install
COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini

# Install Playwright Chromium binary for news scraper
RUN playwright install chromium --with-deps

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

### 2.2 Frontend Dockerfile (`frontend/Dockerfile`)

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000 HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

---

## 3. Production Docker Compose Configuration (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  postgres:
    image: ankane/pgvector:v0.7.0-pg16
    container_name: contentpilot_postgres
    restart: always
    environment:
      POSTGRES_DB: contentpilot_db
      POSTGRES_USER: contentpilot_user
      POSTGRES_PASSWORD: SecureDbPassword123!
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U contentpilot_user -d contentpilot_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7.2-alpine
    container_name: contentpilot_redis
    restart: always
    command: redis-server --requirepass SecureRedisPassword123!
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "SecureRedisPassword123!", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: contentpilot_backend
    restart: always
    environment:
      DATABASE_URL: postgresql+asyncpg://contentpilot_user:SecureDbPassword123!@postgres:5432/contentpilot_db
      REDIS_URL: redis://:SecureRedisPassword123!@redis:6379/0
      JWT_SECRET_KEY: super-secret-jwt-signing-key-32-chars-min
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery_worker_scraper:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: contentpilot_worker_scraper
    restart: always
    command: celery -A app.workers.celery_app worker -Q scraper_queue --concurrency=4 -l info
    environment:
      DATABASE_URL: postgresql+asyncpg://contentpilot_user:SecureDbPassword123!@postgres:5432/contentpilot_db
      REDIS_URL: redis://:SecureRedisPassword123!@redis:6379/0
    depends_on:
      - backend

  celery_worker_ai:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: contentpilot_worker_ai
    restart: always
    command: celery -A app.workers.celery_app worker -Q ai_queue --concurrency=2 -l info
    environment:
      DATABASE_URL: postgresql+asyncpg://contentpilot_user:SecureDbPassword123!@postgres:5432/contentpilot_db
      REDIS_URL: redis://:SecureRedisPassword123!@redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - backend

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: contentpilot_celery_beat
    restart: always
    command: celery -A app.workers.celery_app beat -l info
    depends_on:
      - backend

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: contentpilot_frontend
    restart: always
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

---

## 4. GitHub Actions CI/CD Pipeline (`.github/workflows/deploy.yml`)

```yaml
name: Continuous Integration & Production Deployment

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: ankane/pgvector:v0.7.0-pg16
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        ports: ['5432:5432']
      redis:
        image: redis:7-alpine
        ports: ['6379:6379']

    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Dependencies
        run: |
          cd backend
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run Pytest Suite
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_password@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install & Lint Frontend
        run: |
          cd frontend
          npm ci
          npm run lint
          npm run build

  deploy-production:
    needs: [backend-test, frontend-build]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and Push Docker Images
        run: |
          docker build -t ${{ steps.login-ecr.outputs.registry }}/contentpilot-backend:latest ./backend
          docker build -t ${{ steps.login-ecr.outputs.registry }}/contentpilot-frontend:latest ./frontend
          docker push ${{ steps.login-ecr.outputs.registry }}/contentpilot-backend:latest
          docker push ${{ steps.login-ecr.outputs.registry }}/contentpilot-frontend:latest

      - name: Deploy to AWS ECS Cluster (Zero Downtime Rolling Update)
        run: |
          aws ecs update-service --cluster contentpilot-prod --service backend-service --force-new-deployment
          aws ecs update-service --cluster contentpilot-prod --service frontend-service --force-new-deployment
```

---

## 5. Cloud Production Infrastructure Architecture (AWS/GCP)

```mermaid
graph TB
    subgraph Edge Layer
        CF["Cloudflare WAF / CDN / DNS"]
    end

    subgraph AWS VPC
        ALB["Application Load Balancer"]
        
        subgraph Public Subnets
            NAT["NAT Gateway"]
        end

        subgraph Private Application Subnets
            ECS_Backend["AWS ECS / EKS Backend Tasks<br/>(FastAPI Containers)"]
            ECS_Workers["AWS ECS Celery Workers<br/>(Scraper / AI / Publisher)"]
            ECS_Frontend["AWS ECS Frontend Next.js"]
        end

        subgraph Managed Data Subnets
            RDS[("AWS RDS PostgreSQL 16 + pgvector<br/>(Multi-AZ Failover)")]
            ElastiCache[("AWS ElastiCache Redis<br/>(Cluster Mode Enabled)")]
            S3[("AWS S3 Media Bucket<br/>(Encrypted Artwork & Static Assets)")]
        end
    end

    CF --> ALB
    ALB --> ECS_Frontend
    ALB --> ECS_Backend
    ECS_Backend --> RDS
    ECS_Backend --> ElastiCache
    ECS_Workers --> RDS
    ECS_Workers --> ElastiCache
    ECS_Workers --> S3
```

---

## 6. Observability, Monitoring & Logging

1. **Structured JSON Logging**: All FastAPI endpoints and Celery workers emit JSON logs via `structlog` containing `trace_id`, `workspace_id`, and `execution_time_ms`.
2. **APM & Error Tracking**: Integrated with **Sentry** for real-time unhandled exception alerts and frontend stack trace reporting.
3. **Metrics Collection**: **Prometheus** endpoints exposed on `/metrics` measuring:
   - Celery queue lag & task execution duration.
   - HTTP response latency percentiles (p50, p95, p99).
   - Upstream AI provider error rates and token consumption counts.
4. **Grafana Dashboards**: Real-time dashboards visualizing system health, worker load, and social media posting success rates.

---

## 7. Enterprise Observability & GPU Infrastructure Dashboards

To support deep system introspection across AI workers, database queries, and Celery queues, the platform exposes standardized health check endpoints and OpenTelemetry telemetry pipelines:

### 7.1 Application Health Check Endpoints
- **Liveness Probe** (`GET /health/live`): Returns `200 OK` if the FastAPI web server process is responsive.
- **Readiness Probe** (`GET /health/ready`): Returns `200 OK` if PostgreSQL database connections, Redis brokers, and S3 storage adapters pass health pings.

### 7.2 Celery Worker & GPU Metrics Monitoring
1. **Queue Backlog Metrics**: Prometheus tracks `celery_queue_depth{queue="ai_queue"}` to trigger auto-scaling when background AI synthesis tasks exceed 50 pending items.
2. **GPU VRAM & Compute Telemetry**: Local AI worker nodes export `nvidia_smi_memory_used_bytes` and `nvidia_smi_utilization_gpu` to Grafana dashboards to monitor FLUX / SDXL inference loads.
3. **OpenTelemetry Distributed Tracing**: Every API request and Celery task inherits a global `trace_id` header, visualizing span execution across scrapers, database queries, LLM calls, and social publishing adapters.

