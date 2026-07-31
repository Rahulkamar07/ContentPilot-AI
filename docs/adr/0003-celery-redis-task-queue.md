# ADR-0003: Celery 5.4 and Redis 7 for Asynchronous Orchestration

## Context & Problem Statement
Scraping news sites, executing multi-turn LLM prompts, generating FLUX/SDXL images, and dispatching posts to social APIs are long-running operations that cannot be handled synchronously within HTTP request cycles.

## Decision Drivers
- High task throughput with support for isolated worker queues (`scraper_queue`, `ai_queue`, `publisher_queue`).
- Robust periodic task scheduler (Celery Beat) for cron-like scraper and publishing triggers.
- Native Python integration and automatic retry policies with exponential backoff.
- In-memory speed of Redis for message brokering and caching.

## Considered Options
1. **Celery + Redis 7**
2. **ARQ (Async Redis Queue)**
3. **AWS SQS + Lambda**

## Decision Outcome
**Chosen Option**: **Celery 5.4 + Redis 7**.
Celery is the industry standard for distributed Python background task processing, offering mature worker management, rate limiting, and Beat scheduling.

### Positive Consequences
- Dynamic queue allocation (scale AI GPU workers independently from HTTP scraper workers).
- Dead-letter queue support for unrecoverable failures.
- Native integration with FastAPI and SQLAlchemy async sessions.
