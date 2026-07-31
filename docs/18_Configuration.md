# ContentPilot AI - Configuration & Feature Flag Management

## Document Metadata

| Attribute | Value |
| :--- | :--- |
| **Document ID** | `DOC-18-CONFIGURATION-MANAGEMENT` |
| **Author** | Principal Software Architect |
| **Status** | Approved / Enterprise Specification |
| **Current Version** | `1.0.0` |
| **Last Updated** | `2026-07-31` |

### Version History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | 2026-07-31 | Lead Architect | Initial environment configuration and feature flag baseline specification. |

---

## 1. Environment Variable Matrix

The application uses **Pydantic BaseSettings** (`app/core/config.py`) to validate environment variables at startup.

| Variable Name | Type | Dev Default | Prod Requirement | Description |
| :--- | :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | `string` | `development` | `production` | Active runtime environment (`development`, `staging`, `production`) |
| `DATABASE_URL` | `string` | `postgresql+asyncpg://...` | `REQUIRED` | PostgreSQL 16 connection string |
| `REDIS_URL` | `string` | `redis://localhost:6379/0` | `REQUIRED` | Redis connection URL for caching & Celery broker |
| `JWT_SECRET_KEY` | `string` | `dev-secret-32-chars` | `REQUIRED` | Secret key for signing JWT tokens |
| `JWT_ALGORITHM` | `string` | `HS256` | `HS256` | JWT signing algorithm |
| `OPENAI_API_KEY` | `string` | `sk-dev-...` | `REQUIRED` | Upstream OpenAI API Key |
| `GEMINI_API_KEY` | `string` | `AIzaSy...` | `REQUIRED` | Upstream Google Gemini API Key |
| `STORAGE_PROVIDER` | `string` | `LOCAL` | `S3` | Target object storage provider (`LOCAL`, `S3`, `GCS`) |
| `AWS_S3_BUCKET` | `string` | `contentpilot-dev` | `REQUIRED` | Production AWS S3 bucket name |
| `LOG_LEVEL` | `string` | `DEBUG` | `INFO` | Structlog logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## 2. Feature Flags System

Feature flags are dynamically evaluated per request and tenant using **PostHog** or **Unleash** integration:

```json
{
  "feature_flags": {
    "enable_local_ollama_models": false,
    "enable_flux_dev_generator": true,
    "enable_telegram_publisher": true,
    "enable_automated_brand_watermark": true,
    "enable_ai_fact_checking_step": false
  }
}
```

---

## 3. Rate Limiting Quota Matrix

Rate limits are enforced at the API gateway and application controller levels using Redis bucket counters:

| Plan Tier | Max News Sources | AI Image Generation Quota | API Rate Limit (Req/Min) |
| :--- | :---: | :---: | :---: |
| **STARTER** | 5 Feeds | 100 Images / Month | 60 req/min |
| **PRO** | 25 Feeds | 1,000 Images / Month | 300 req/min |
| **ENTERPRISE** | Unlimited | 10,000+ Images / Month | 1,200 req/min |

---

## Document Cross-References
- Global System Blueprint: [00_MasterBlueprint.md](file:///d:/Projects/ContentPilot/docs/00_MasterBlueprint.md)
- Infrastructure & Deployment: [Deployment.md](file:///d:/Projects/ContentPilot/docs/Deployment.md)
- AI Model Abstraction: [AI.md](file:///d:/Projects/ContentPilot/docs/AI.md)
