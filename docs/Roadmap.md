# ContentPilot AI - Product Roadmap & Development Blueprint

## 1. Executive Product Strategy

**ContentPilot AI** is built on an incremental, feature-driven commercial SaaS roadmap. The strategic objective is to launch an ultra-reliable MVP targeting Instagram publishing, followed rapidly by multi-platform expansions, custom AI image branding, local model integration, and enterprise multi-tenant team workflows.

---

## 2. Release Phase Breakdown

```mermaid
timeline
    title ContentPilot AI Multi-Phase Roadmap
    section Phase 1: MVP Core (Weeks 1-4)
        Core Infrastructure : Docker, PostgreSQL, FastAPI, Celery
        Scraper Engine : RSS Feeds & Article Normalization
        AI Pipeline : OpenAI / Gemini Summarization & Vision Prompting
        Instagram Publishing : Instagram Graph API Adapter
        Frontend Board : Next.js Approval Queue & Workspace Management
    section Phase 2: Platform Expansion & Automation (Weeks 5-8)
        Platform Adapters : X (Twitter), LinkedIn, Facebook, Threads, Telegram
        Image Branding : SVG Overlay & Watermark Engine
        Timezone Scheduler : Automated Timezone-Aware Queue Dispatcher
        Analytics Suite : Performance Analytics & Impression Metrics
    section Phase 3: Enterprise & Local AI (Weeks 9-12)
        Local AI Engine : Ollama, Llama 3, Qwen, Local FLUX / SDXL
        Advanced RBAC : Multi-member roles & audit logs
        Developer API : SaaS REST API & Webhooks
        Video Content : Shorts & TikTok AI Video Generator
```

---

## 3. Sprint-by-Sprint Development Blueprint (12 Weeks)

### Phase 1: MVP Platform Launch (Weeks 1–4)

#### **Sprint 1: System Foundation & Core Scraper**
- **Objectives**: Setup repository structure, database migrations, authentication, and news scraper worker.
- **Deliverables**:
  - Clean Architecture folder layout for `backend/` and `frontend/`.
  - Alembic migrations for `users`, `workspaces`, `news_sources`, and `articles`.
  - JWT Authentication & RBAC FastAPI endpoints (`/auth/register`, `/auth/login`).
  - RSS scraper task in Celery using `feedparser` and `httpx`.
  - Next.js base app with Shadcn UI, authentication screens, and dark theme layout.

#### **Sprint 2: AI Pipeline & Vision Prompt Engine**
- **Objectives**: Implement summarization, Vision model scene analysis, and initial image generation.
- **Deliverables**:
  - `AIProviderInterface` with implementations for OpenAI (`gpt-4o`, `dall-e-3`) and Google Gemini (`gemini-1.5-pro`).
  - Vision analysis pipeline (`analyze_image_vision`) for transforming news photographs into original scene descriptions.
  - Image generator adapter saving outputs to S3 / Local storage.
  - Basic AI processing endpoint (`POST /ai/process-article`).

#### **Sprint 3: Approval Queue & Instagram Publisher**
- **Objectives**: Build human-in-the-loop content queue and Instagram Graph API publishing adapter.
- **Deliverables**:
  - `SocialPosts` and `GeneratedImages` database models and repositories.
  - Next.js **Queue Approval Board** with caption editing, image preview, and one-click approve/reject actions.
  - `InstagramPlatformAdapter` supporting single image and carousel publishing.
  - Async publishing worker in Celery handling access token refresh and post dispatch.

#### **Sprint 4: MVP Integration & Hardening**
- **Objectives**: End-to-end integration, automated testing, and MVP deployment.
- **Deliverables**:
  - Full flow verification: News Source → Scraper → Article DB → AI Processing → Approval Queue → Instagram Publish.
  - Basic dashboard metrics overview.
  - Docker Compose setup for local production deployment testing.
  - **Milestone 1 Release: MVP Live Testing**.

---

### Phase 2: Multi-Platform & Automation (Weeks 5–8)

#### **Sprint 5: Social Platform Expansion Part 1**
- **Objectives**: Implement X (Twitter v2 API) and LinkedIn API publishing adapters.
- **Deliverables**:
  - `XPlatformAdapter` supporting text, images, and thread posting.
  - `LinkedInPlatformAdapter` supporting organization page and personal posts.
  - Multi-platform selection controls in Next.js approval queue UI.

#### **Sprint 6: Social Platform Expansion Part 2 & Telegram**
- **Objectives**: Implement Facebook Pages API, Threads API, and Telegram Bot API adapters.
- **Deliverables**:
  - `FacebookPlatformAdapter` and `TelegramBotAdapter`.
  - Modular `PlatformAdapterFactory` in backend to dynamically resolve target adapters.
  - Token refresh scheduler task executing hourly via Celery Beat.

#### **Sprint 7: Automated Scheduler & Image Branding Engine**
- **Objectives**: Timezone-aware automated scheduler and dynamic image branding watermarks.
- **Deliverables**:
  - Timezone-aware posting queue runner checking scheduled timestamps every minute.
  - Branding Engine overlaying custom workspace logos, watermarks, and editorial borders onto synthesized images using Pillow/Canvas.
  - Schedule configuration UI in Next.js.

#### **Sprint 8: Analytics Engine & Hardening**
- **Objectives**: Engagement tracking, analytics dashboard, and rate-limit guardrails.
- **Deliverables**:
  - Celery cron task scraping impressions, likes, shares, and comments from social APIs every 6 hours.
  - Next.js Analytics dashboard with TanStack Query and Recharts visualization.
  - Exponential backoff retry logic on failed platform HTTP requests.
  - **Milestone 2 Release: Multi-Platform Automation Platform**.

---

### Phase 3: Local AI & Enterprise SaaS (Weeks 9–12)

#### **Sprint 9: Local AI Models (Ollama & SDXL / FLUX)**
- **Objectives**: Integrate local LLMs and local diffusion image generation to eliminate cloud API costs.
- **Deliverables**:
  - `OllamaAIAdapter` for local Llama 3 and Qwen 2 execution.
  - Local GPU worker pool running ComfyUI / Stable Diffusion XL / FLUX.1 pipeline.
  - Fallback logic: Local Model → Cloud Provider (OpenAI/Gemini) if GPU is unavailable.

#### **Sprint 10: Multi-Tenant RBAC & Audit Trail**
- **Objectives**: Enterprise workspace membership management, roles, and security audit logs.
- **Deliverables**:
  - Invitation link system (`workspace_members` table).
  - RBAC permission enforcement (`OWNER`, `ADMIN`, `EDITOR`, `VIEWER`).
  - Structured audit log collector recording every user and system event (`SystemAuditLogs`).

#### **Sprint 11: Developer SaaS API & Webhooks**
- **Objectives**: External REST API tier for third-party developer integrations.
- **Deliverables**:
  - `UserAPIKey` management, rate limiting per API key.
  - Public developer documentation endpoints.
  - Webhook dispatcher notifying external URLs when posts are created or published.

#### **Sprint 12: Performance Optimization & Enterprise Launch**
- **Objectives**: Load testing, security auditing, and production launch.
- **Deliverables**:
  - Locust load test verifying 10,000 concurrent queue items and 100 scrapers.
  - PostgreSQL database query optimization and GIN index tuning.
  - **Milestone 3 Release: ContentPilot AI Enterprise SaaS Commercial Launch**.

---

## 4. Milestone Matrix & Risk Management

| Milestone | Target Week | Major Deliverable | Key Risk | Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **M1: MVP Launch** | Week 4 | End-to-end Instagram publishing from news feeds | Instagram Graph API rate limits | Implement API request bucket queues |
| **M2: Multi-Platform** | Week 8 | X, LinkedIn, FB, Threads, Telegram adapters + Branding | Token expiry & disconnection | Proactive token renewal cron worker |
| **M3: Enterprise SaaS** | Week 12 | Local AI models, RBAC, Webhooks, SaaS Billing | High GPU memory usage for SDXL | Dynamic queue batching & worker isolation |
