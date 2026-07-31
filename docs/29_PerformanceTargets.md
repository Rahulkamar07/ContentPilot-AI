# ContentPilot AI - Performance Targets, SLAs & Scalability Goals

## Document Metadata

| Attribute | Value |
| :--- | :--- |
| **Document ID** | `DOC-29-PERFORMANCE-TARGETS` |
| **Author** | Principal Performance Architect |
| **Status** | Approved / Enterprise Specification |
| **Current Version** | `1.0.0` |
| **Last Updated** | `2026-07-31` |

### Version History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | 2026-07-31 | Performance Lead | Initial latency SLAs, throughput targets, and resource budgets. |

---

## 1. REST API Latency Service Level Agreements (SLAs)

All REST API endpoints are monitored via OpenTelemetry metrics against target latency percentiles:

| Endpoint Category | p50 SLA | p95 SLA | p99 SLA | Availability Target |
| :--- | :--- | :--- | :--- | :--- |
| **Auth & User Management** (`/auth/*`) | **< 40ms** | **< 120ms** | **< 300ms** | 99.99% |
| **Queue Board Read** (`/posts/queue`) | **< 50ms** | **< 150ms** | **< 400ms** | 99.9% |
| **Post Approval Mutation** (`/posts/{id}/approve`) | **< 60ms** | **< 200ms** | **< 500ms** | 99.9% |
| **Analytics Overview** (`/analytics/overview`) | **< 80ms** | **< 250ms** | **< 600ms** | 99.5% |

---

## 2. Background Task & AI Pipeline Processing Times

| Subsystem Task | Target Processing Time | Max Timeout Limit | Concurrency Target |
| :--- | :--- | :--- | :--- |
| **RSS Article Scraping & Deduplication** | **< 1.5 seconds** / feed | 30 seconds | 50 concurrent feeds |
| **Playwright Stealth Page Scrape** | **< 4.5 seconds** / page | 45 seconds | 10 browser contexts |
| **Article Summarization (LLM)** | **< 2.0 seconds** | 10 seconds | 20 async tasks |
| **Vision Scene Analysis (Multimodal LLM)**| **< 3.5 seconds** | 15 seconds | 15 async tasks |
| **FLUX / SDXL Image Synthesis** | **< 6.5 seconds** / image | 30 seconds | 4 GPU worker threads |
| **Social Publishing Execution** | **< 2.5 seconds** / post | 20 seconds | 30 async tasks |

---

## 3. Database & System Scalability Goals

- **Database Query Latency**: B-tree index queries execute in $< 5\text{ms}$; `pgvector` HNSW cosine similarity search executes in $< 35\text{ms}$ across 1,000,000 stored vectors.
- **Concurrent System Capacity (Phase 1 Baseline)**:
  - **10,000** Active Tenant Workspaces.
  - **500,000** Ingested Articles / Day.
  - **50,000** AI Generated Social Posts / Day.
  - **1,000** Concurrent Web App User Sessions.

---

## Document Cross-References
- Global System Blueprint: [00_MasterBlueprint.md](file:///d:/Projects/ContentPilot/docs/00_MasterBlueprint.md)
- Observability & Monitoring: [Deployment.md](file:///d:/Projects/ContentPilot/docs/Deployment.md)
- Testing Matrix & Locust Load Tests: [32_TestMatrix.md](file:///d:/Projects/ContentPilot/docs/32_TestMatrix.md)
