# ContentPilot AI

> **Autonomous AI-Powered Multi-Platform Social Media Publishing System**

ContentPilot AI is an enterprise-grade, multi-tenant SaaS platform that automates the entire content creation and publishing lifecycle: ingesting news from global feeds, performing AI factual summarization, generating copyright-safe editorial imagery via Vision-to-Prompt models, applying workspace branding watermarks, managing human-in-the-loop review queues, and publishing content automatically across social networks.

---

## 🚀 Key Features

- **Automated News Ingestion**: Stealth Playwright scrapers and RSS parser for 11+ content categories.
- **Copyright-Safe AI Visuals**: 5-step visual scene breakdown converting news photographs into original FLUX / SDXL artwork (100% Fair Use compliant).
- **Multi-Platform Publishing Engine**: Modular adapters for Instagram Graph API, X (Twitter), LinkedIn, Facebook, Threads, and Telegram.
- **Timezone-Aware Scheduling**: Priority queues preventing channel collisions and balancing category distribution.
- **Human-in-the-Loop Queue Board**: Sleek glassmorphic Kanban interface for one-click approval and inline caption editing.
- **Multi-Tenant Workspaces & RBAC**: Workspace isolation with role-based access (`OWNER`, `ADMIN`, `EDITOR`, `VIEWER`).
- **AI Cost Optimization**: Caching, embedding reuse via PostgreSQL `pgvector`, and local model fallback cascades.

---

## 🛠 Tech Stack

### Backend
- **Core Engine**: Python 3.12, FastAPI, Pydantic v2
- **ORM & DB**: SQLAlchemy 2.0 (Async), Alembic, PostgreSQL 16 + `pgvector`
- **Task Orchestration**: Celery 5.4, Redis 7 Broker, Celery Beat
- **Scraper Engine**: Playwright Stealth, BeautifulSoup4, HTTPX
- **AI Models**: OpenAI (GPT-4o / DALL-E 3), Google Gemini 1.5, Ollama (Llama 3 / Qwen 2), FLUX.1-Dev / SDXL

### Frontend
- **Framework**: Next.js 14 (App Router), React 18, TypeScript
- **Styling & UI**: TailwindCSS, Shadcn UI, Radix UI Primitives, Lucide Icons, Framer Motion
- **State Management**: Zustand (UI State), TanStack Query v5 (Server Cache)

---

## 📂 Project Structure

```
ContentPilot/
├── backend/                  # FastAPI Application Core
│   ├── app/                  # Clean Architecture (domain, use_cases, infrastructure)
│   ├── alembic/              # Database Migration Scripts
│   ├── tests/                # Pytest Unit & Integration Suite
│   └── Dockerfile
├── frontend/                 # Next.js 14 Web Portal
│   ├── src/                  # App Router Pages, Components, Store & Hooks
│   └── Dockerfile
├── docker/                   # Production Nginx & Docker Infrastructure Configs
├── docs/                     # 30+ Enterprise Technical Specifications & PRD
│   ├── adr/                  # Architecture Decision Records (ADRs)
│   ├── 00_MasterBlueprint.md # Central Reference Architecture Blueprint
│   └── 01_PRD.md             # Product Requirements Document
├── scripts/                  # Seed Data & Maintenance Scripts
├── docker-compose.yml        # Orchestration Config
├── README.md
└── LICENSE
```

---

## 📋 Prerequisites

- **Docker & Docker Compose**: v24.0+
- **Python**: v3.12+
- **Node.js**: v20+
- **PostgreSQL**: v16+ (with `pgvector` extension)
- **Redis**: v7+

---

## 💻 Local Setup Instructions

### 1. Clone & Configure Environment
```bash
git clone https://github.com/contentpilot/ContentPilot-AI.git
cd ContentPilot-AI
```

### 2. Run Containerized Infrastructure
```bash
docker-compose up -d postgres redis
```

### 3. Setup & Run Backend API Server
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 4. Run Celery Background Workers
```bash
# In a separate terminal session
cd backend
celery -A app.workers.celery_app worker -Q scraper_queue,ai_queue,publisher_queue -l info
```

### 5. Run Next.js Frontend Development Server
```bash
cd frontend
npm ci
npm run dev
```
Navigate to `http://localhost:3000` to access the application dashboard.

---

## 📚 Technical Documentation Index

All architectural and business decisions are fully documented in the [`docs/`](file:///d:/Projects/ContentPilot/docs) directory:

- **[00_MasterBlueprint.md](file:///d:/Projects/ContentPilot/docs/00_MasterBlueprint.md)**: Central Reference Blueprint & Global C4 System Map
- **[01_PRD.md](file:///d:/Projects/ContentPilot/docs/01_PRD.md)**: Product Requirements Document (Business & Product Strategy)
- **[Architecture.md](file:///d:/Projects/ContentPilot/docs/Architecture.md)**: Clean Architecture, Plugin Engine & Domain Events
- **[Database.md](file:///d:/Projects/ContentPilot/docs/Database.md)**: Complete Database Design, ERD & Audit Logging
- **[API.md](file:///d:/Projects/ContentPilot/docs/API.md)**: REST API Specification & Versioning Strategy
- **[Roadmap.md](file:///d:/Projects/ContentPilot/docs/Roadmap.md)**: Multi-Phase Product Strategy & 12-Week Sprint Plan
- **[AI.md](file:///d:/Projects/ContentPilot/docs/AI.md)**: AI Pipeline & 10-Step Image Generation Workflow
- **[Automation.md](file:///d:/Projects/ContentPilot/docs/Automation.md)**: Task Orchestration, Stealth Scraping & Retry Matrix
- **[Architecture Decision Records](file:///d:/Projects/ContentPilot/docs/adr)**: ADRs 0001 through 0006

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
