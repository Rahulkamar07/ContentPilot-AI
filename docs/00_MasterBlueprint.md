# ContentPilot AI - Master Architectural Blueprint

## Document Metadata

| Attribute | Value |
| :--- | :--- |
| **Document ID** | `DOC-00-MASTER-BLUEPRINT` |
| **Author** | Principal Software Architect & Engineering Team |
| **Status** | Approved / Production Blueprint |
| **Current Version** | `1.0.0` |
| **Last Updated** | `2026-07-31` |

### Version History
| Version | Date | Author | Description of Changes |
| :--- | :--- | :--- | :--- |
| `1.0.0` | 2026-07-31 | Lead Architect | Initial commercial SaaS enterprise Master Blueprint synthesis. |

### Document Assumptions
- The application will operate as a multi-tenant B2B/B2C SaaS platform deployed on AWS cloud infrastructure.
- High-volume data persistence relies on PostgreSQL 16 with the `pgvector` extension for semantic embedding similarity.
- Asynchronous task processing is orchestrated via Celery and Redis worker pools.

### Document Limitations
- Real-time video generation (YouTube Shorts, TikTok) is scoped for Phase 3 enterprise expansion.
- Initial social platform publishing natively supports Instagram Graph API, with modular adapters prepared for X, LinkedIn, Facebook, Threads, and Telegram.

### Future Improvements
- Migration of CPU/GPU intensive background workers into independent Kubernetes microservices.
- Integration of custom fine-tuned open-weight local vision LLMs and FLUX TensorRT instances.

---

## 1. Executive Vision & Business Goals

**ContentPilot AI** is an autonomous, AI-powered social media publishing and content synthesis platform. The system ingests raw news from diverse global sources, performs AI-driven summarization, extracts visual scenes using Multimodal Vision models, synthesizes copyright-safe editorial artwork, applies brand watermarks, manages human-in-the-loop approval queues, and automatically publishes posts across multi-platform social networks according to timezone-aware schedules.

### Core Business Objectives:
1. **Automation Efficiency**: Reduce social media content creation overhead by 90% for media publishers and agencies.
2. **Copyright Safety**: Guarantee 100% original visual content through Vision Model scene breakdown and Generative AI prompt transformation (eliminating direct source image reposting).
3. **Multi-Platform Scalability**: Provide a unified platform adapter engine capable of dispatching content to Instagram, X, LinkedIn, Facebook, Threads, and Telegram without core code refactoring.
4. **Enterprise Multi-Tenancy**: Support role-based workspace isolation, custom brand tone tuning, and audit log compliance.

---

## 2. Global Master System Map

```mermaid
graph TB
    subgraph Client & Edge Gateway Layer
        WebClient["Next.js 14 Web Portal<br/>(TypeScript / Tailwind / Shadcn)"]
        CDN["Cloudflare WAF & CDN"]
        NginxGateway["Nginx Reverse Proxy & API Gateway"]
    end

    subgraph Application Core (FastAPI Modular Monolith)
        REST_API["FastAPI Engine<br/>(Async / OpenAPI)"]
        CleanArch["Clean Architecture Service Layer<br/>(Domain Entities, Repositories, Use Cases)"]
        PluginRegistry["Plugin Engine Registry<br/>(Platforms, AI, Scrapers, Storage)"]
    end

    subgraph Asynchronous Task Worker Layer
        ScraperWorker["Playwright / HTTPX Scraper Workers"]
        AIWorker["LLM / Vision / FLUX AI Workers"]
        PublisherWorker["Social Platform Publisher Workers"]
        SchedulerBeat["Celery Beat Periodic Schedulers"]
    end

    subgraph Data & Storage Layer
        Postgres[("PostgreSQL 16 + pgvector<br/>(Primary Multi-Tenant DB)")]
        RedisCache[("Redis 7<br/>(Cache, Rate Limits, Celery Broker)")]
        ObjectStorage[("S3 / Cloud Storage<br/>(Branded Images, Logos, Media)")]
    end

    subgraph External Provider Ecosystem
        AI_Cloud["Cloud AI (OpenAI / Gemini / Anthropic)"]
        AI_Local["Local AI (Ollama / ComfyUI / FLUX)"]
        Social_APIs["Social APIs (Instagram, X, LinkedIn, FB, Telegram)"]
    end

    WebClient --> CDN --> NginxGateway --> REST_API
    REST_API --> CleanArch --> PluginRegistry
    CleanArch --> Postgres
    CleanArch --> RedisCache

    PluginRegistry -->|Enqueue Tasks| RedisCache
    SchedulerBeat --> RedisCache

    RedisCache --> ScraperWorker
    RedisCache --> AIWorker
    RedisCache --> PublisherWorker

    ScraperWorker --> Postgres
    AIWorker --> AI_Cloud
    AIWorker --> AI_Local
    AIWorker --> ObjectStorage
    PublisherWorker --> Social_APIs
```

---

## 3. Comprehensive Technical Documentation Index

Every component of ContentPilot AI is documented across specialized specification files in the `docs/` repository:

| Document ID | Title & Location | Primary Architectural Scope |
| :--- | :--- | :--- |
| `DOC-00` | [00_MasterBlueprint.md](file:///d:/Projects/ContentPilot/docs/00_MasterBlueprint.md) | Central reference blueprint, global architecture map, ADR log index. |
| `DOC-01` | [Architecture.md](file:///d:/Projects/ContentPilot/docs/Architecture.md) | Clean Architecture, C4 diagrams, Repository Pattern, Plugin Architecture, Domain Events. |
| `DOC-02` | [Database.md](file:///d:/Projects/ContentPilot/docs/Database.md) | PostgreSQL 16 + pgvector schema, ERD, monthly partitioning, Audit System tables. |
| `DOC-03` | [API.md](file:///d:/Projects/ContentPilot/docs/API.md) | REST API endpoints, schemas, JSON response wrappers, API Versioning & Deprecation strategy. |
| `DOC-04` | [Roadmap.md](file:///d:/Projects/ContentPilot/docs/Roadmap.md) | 3-Phase strategy, 12-week sprint-by-sprint development plan, milestone matrix. |
| `DOC-05` | [Features.md](file:///d:/Projects/ContentPilot/docs/Features.md) | Catalog of 15+ Core Features, user flow state machines, Gherkin acceptance criteria. |
| `DOC-06` | [Deployment.md](file:///d:/Projects/ContentPilot/docs/Deployment.md) | Multi-stage Dockerfiles, Docker Compose, GitHub Actions CI/CD, Observability & GPU metrics. |
| `DOC-07` | [UI_UX.md](file:///d:/Projects/ContentPilot/docs/UI_UX.md) | HSL dark design system, wireframe blueprints, Shadcn UI components, Super-Admin Panel. |
| `DOC-08` | [AI.md](file:///d:/Projects/ContentPilot/docs/AI.md) | AI pipeline, 10-step Vision-to-Image generation workflow, Provider Abstraction Layer (PAL). |
| `DOC-09` | [Automation.md](file:///d:/Projects/ContentPilot/docs/Automation.md) | Celery task queues, Playwright stealth scrapers, Platform Adapters, Retry Policies & DLQ. |
| `DOC-10` | [CodingStandards.md](file:///d:/Projects/ContentPilot/docs/CodingStandards.md) | PEP 8 / Ruff Python rules, strict TypeScript rules, testing strategy (Pytest/Locust). |
| `DOC-16` | [16_FunctionalRequirements.md](file:///d:/Projects/ContentPilot/docs/16_FunctionalRequirements.md) | Comprehensive functional specs, User Stories, Business Rules, Edge Cases, RBAC Permissions. |
| `DOC-17` | [17_SequenceDiagrams.md](file:///d:/Projects/ContentPilot/docs/17_SequenceDiagrams.md) | 10 Mermaid sequence diagrams and complete State Machine specifications. |
| `DOC-18` | [18_Configuration.md](file:///d:/Projects/ContentPilot/docs/18_Configuration.md) | Environment matrices (Dev/Staging/Prod), Feature Flags, AI/Storage provider switches. |
| `DOC-19` | [19_Storage.md](file:///d:/Projects/ContentPilot/docs/19_Storage.md) | Storage hierarchy, S3 directory trees, brand assets, logs, video assets, retention policies. |
| `DOC-20` | [20_PromptLibrary.md](file:///d:/Projects/ContentPilot/docs/20_PromptLibrary.md) | Production LLM system prompts, Vision prompts, Negative prompts, JSON schemas, Versioning. |
| `DOC-21` | [21_CostOptimization.md](file:///d:/Projects/ContentPilot/docs/21_CostOptimization.md) | Token budgeting, Redis caching, embedding reuse, fallback cascades, Local vs Cloud costs. |
| `DOC-22` | [22_NewsRanking.md](file:///d:/Projects/ContentPilot/docs/22_NewsRanking.md) | Multi-factor article scoring algorithm, trending engine, breaking news detection. |
| `DOC-23` | [23_BrandSystem.md](file:///d:/Projects/ContentPilot/docs/23_BrandSystem.md) | Brand colors, typography, watermarks, caption styles, CTA templates, image presets. |
| `DOC-24` | [24_Scheduler.md](file:///d:/Projects/ContentPilot/docs/24_Scheduler.md) | Posting scheduler algorithm, priority queue, timezone handling, channel collision protection. |
| `DOC-25` | [25_Notifications.md](file:///d:/Projects/ContentPilot/docs/25_Notifications.md) | Multi-channel notification engine (Email, In-App, Slack, Discord, Webhooks, Telegram, Push). |
| `DOC-26` | [26_DisasterRecovery.md](file:///d:/Projects/ContentPilot/docs/26_DisasterRecovery.md) | BCP & Disaster recovery, PostgreSQL PITR, Redis snapshotting, RPO (< 5 min) & RTO (< 15 min). |
| `DOC-27` | [27_LegalCompliance.md](file:///d:/Projects/ContentPilot/docs/27_LegalCompliance.md) | Copyright Fair Use, Robots.txt compliance, ToS, GDPR/CCPA privacy, AI content review. |
| `DOC-28` | [28_ThreatModel.md](file:///d:/Projects/ContentPilot/docs/28_ThreatModel.md) | STRIDE Threat Model, attack surface breakdown, trust boundaries, security controls. |
| `DOC-29` | [29_PerformanceTargets.md](file:///d:/Projects/ContentPilot/docs/29_PerformanceTargets.md) | Latency SLAs, processing time targets, throughput quotas, hardware scalability goals. |
| `DOC-30` | [30_ErrorCatalog.md](file:///d:/Projects/ContentPilot/docs/30_ErrorCatalog.md) | Standard error catalog, HTTP status mappings, root causes, operational runbooks. |
| `DOC-31` | [31_DataLifecycle.md](file:///d:/Projects/ContentPilot/docs/31_DataLifecycle.md) | Data retention, archival & deletion policy for articles, posts, images, and audit logs. |
| `DOC-32` | [32_TestMatrix.md](file:///d:/Projects/ContentPilot/docs/32_TestMatrix.md) | Comprehensive test matrix (Unit, Integration, E2E, Load, Security, Chaos testing). |
| `DOC-33` | [33_AIGuidelines.md](file:///d:/Projects/ContentPilot/docs/33_AIGuidelines.md) | AI safety guidelines, prompt versioning, hallucination guardrails, cost limits. |
| `DOC-34` | [34_Releases.md](file:///d:/Projects/ContentPilot/docs/34_Releases.md) | Semantic Versioning, release process, feature flags, canary deployment, rollback strategy. |
| `DOC-35` | [35_DevelopmentWorkflow.md](file:///d:/Projects/ContentPilot/docs/35_DevelopmentWorkflow.md) | End-to-End SDLC (Requirements → Documentation → Implementation → Testing → Deployment). |

---

## 4. Architecture Decision Records (ADRs) Log

The technical decisions governing ContentPilot AI are codified in formal Architecture Decision Records located in `docs/adr/`:

- **[ADR-0001: FastAPI Framework Selection](file:///d:/Projects/ContentPilot/docs/adr/0001-fastapi-backend-framework.md)**: Chose FastAPI for Python 3.12 async native performance, strict Pydantic v2 validation, OpenAPI auto-generation, and lightweight dependency injection.
- **[ADR-0002: PostgreSQL 16 + pgvector Persistence](file:///d:/Projects/ContentPilot/docs/adr/0002-postgresql-pgvector-database.md)**: Selected PostgreSQL 16 with `pgvector` to unify relational ACID metadata and 1536-dimensional semantic article embeddings within a single database instance.
- **[ADR-0003: Celery & Redis Task Queue Orchestration](file:///d:/Projects/ContentPilot/docs/adr/0003-celery-redis-task-queue.md)**: Implemented Celery 5.4 backed by Redis 7 for queue isolation (`scraper_queue`, `ai_queue`, `publisher_queue`), periodic Beat scheduling, and exponential backoff retry handling.
- **[ADR-0004: Playwright Headless Scraping Engine](file:///d:/Projects/ContentPilot/docs/adr/0004-playwright-stealth-scraping.md)**: Adopted Playwright with stealth browser context overrides to bypass anti-bot challenges on dynamic news portals lacking RSS feeds.
- **[ADR-0005: Next.js 14 & Shadcn UI Frontend](file:///d:/Projects/ContentPilot/docs/adr/0005-nextjs-shadcn-frontend.md)**: Standardized on Next.js 14 App Router, TypeScript, TailwindCSS, Shadcn UI primitives, Zustand, and TanStack Query for a dark-mode glassmorphic client interface.
- **[ADR-0006: Clean Architecture & Repository Pattern](file:///d:/Projects/ContentPilot/docs/adr/0006-clean-architecture-repository-pattern.md)**: Enforced strict boundary separation between pure domain entities (`app/domain`), use case logic (`app/use_cases`), and external infrastructure/ORMs (`app/infrastructure`).
