# ADR-0001: Selection of FastAPI as Core Backend Framework

## Context & Problem Statement
ContentPilot AI requires an asynchronous, high-performance Python web backend framework capable of handling concurrent REST API requests, processing heavy AI payloads, serving OpenAPI specifications, and integrating seamlessly with async database drivers (`asyncpg`, SQLAlchemy 2.0).

## Decision Drivers
- High concurrency and low latency requirement for API gateway endpoints.
- Native support for Python 3.12 `async` / `await` event loops.
- Automatic request payload validation via Pydantic v2.
- Auto-generation of OpenAPI 3.0 / Swagger documentation.
- Minimal overhead compared to monolithic frameworks (e.g., Django).

## Considered Options
1. **FastAPI** (Python 3.12 + Starlette + Pydantic v2)
2. **Django REST Framework (DRF)** (Python)
3. **Express.js / NestJS** (Node.js / TypeScript)

## Decision Outcome
**Chosen Option**: **FastAPI**.
FastAPI provides native asynchronous execution, strict Pydantic type validation, and seamless integration with Python's AI/ML ecosystem (OpenAI SDK, Google Gemini SDK, PyTorch, Diffusers).

### Positive Consequences
- Exceptional throughput performance approaching Node.js and Go benchmarks.
- Automatic interactive API documentation generated at `/docs`.
- Clean dependency injection model (`fastapi.Depends`).

### Negative Consequences
- Developer must manually structure ORM models, migrations, and admin interfaces (unlike Django's built-in batteries-included admin).
