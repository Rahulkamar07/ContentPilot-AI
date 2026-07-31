# ADR-0006: Clean Architecture & Repository Pattern Adoption

## Context & Problem Statement
To build an enterprise SaaS product that scales across multiple social networks, AI models, and database providers, the core business domain logic must remain independent of external frameworks, ORMs, and third-party APIs.

## Decision Drivers
- Need to swap AI providers (OpenAI → Gemini → Local Ollama) without modifying business logic.
- Ability to test domain use cases in isolation without mocking database instances or HTTP networks.
- Enforcing strict boundaries between DB models (`SQLAlchemy`) and pure domain entities (`Pydantic` / Python dataclasses).

## Considered Options
1. **Clean Architecture + Repository Pattern**
2. **Standard Layered MVC (Model-View-Controller)**
3. **Active Record Pattern (Django / Rails style)**

## Decision Outcome
**Chosen Option**: **Clean Architecture + Repository Pattern**.
All domain entities (`Article`, `SocialPost`, `Workspace`) and interface contracts reside in pure Python layers (`app/domain`). Database ORM models and API clients are encapsulated in `app/infrastructure`.

### Positive Consequences
- Exceptional maintainability and unit testability (90%+ code coverage capability).
- Future platform expansion (e.g., adding TikTok or YouTube Shorts adapters) requires zero core domain refactoring.
