# ContentPilot AI - Engineering Standards & Testing Strategy

## 1. Python Code Standards (Backend)

The Python backend adheres strictly to **PEP 8**, enforcing type annotations, static analysis, and async-first design patterns.

### 1.1 Tooling & Formatting Rules
- **Linter & Formatter**: `ruff` and `black` configured with a 100-character line length limit.
- **Type Checking**: `mypy` running in strict mode (`strict = true`).
- **Data Validation**: **Pydantic v2** (`BaseModel`, `Field`, `ConfigDict`).

### 1.2 Python Naming Conventions
- **Modules / Files**: `snake_case` (e.g., `ai_pipeline_service.py`, `article_repository.py`).
- **Classes**: `PascalCase` (e.g., `ArticleRepository`, `AIPipelineService`).
- **Functions / Methods**: `snake_case` (e.g., `get_pending_ai_processing()`, `generate_social_caption()`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_ATTEMPTS = 5`).
- **Interfaces / ABCs**: Suffix with `Interface` or `ABC` (e.g., `ArticleRepositoryInterface`).

### 1.3 FastAPI Controller Example

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Sequence
from uuid import UUID

from app.api.v1.dependencies import get_current_user, get_article_use_case
from app.api.schemas.article import ArticleResponseSchema
from app.domain.entities.user import User

router = APIRouter(prefix="/articles", tags=["Articles"])

@router.get("/{article_id}", response_model=ArticleResponseSchema, status_code=status.HTTP_200_OK)
async def get_article_by_id(
    article_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case = Depends(get_article_use_case),
) -> ArticleResponseSchema:
    """Retrieve an ingested article by its unique UUID."""
    article = await use_case.execute(article_id=article_id, workspace_id=current_user.active_workspace_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found",
        )
    return ArticleResponseSchema.from_entity(article)
```

---

## 2. TypeScript & React Standards (Frontend)

The Next.js frontend enforces strict TypeScript type safety, modular React functional components, and custom hook encapsulation.

### 2.1 Tooling & Formatting Rules
- **Linter & Formatter**: ESLint (`@typescript-eslint/recommended`) + Prettier.
- **Strict Mode**: `"strict": true` in `tsconfig.json`. No usage of `any`.

### 2.2 TypeScript Naming Conventions
- **Component Files**: `PascalCase.tsx` (e.g., `QueueCard.tsx`, `WorkspaceSwitcher.tsx`).
- **Hook Files**: `camelCase.ts` starting with `use` (e.g., `useQueuePosts.ts`, `useAuth.ts`).
- **Types / Interfaces**: `PascalCase` (e.g., `ArticleEntity`, `SocialPostResponse`).
- **Enums**: `PascalCase` (e.g., `PlatformType.INSTAGRAM`).

---

## 3. Custom Error Hierarchy & Structured Logging

### 3.1 Domain Exception Hierarchy (`app/core/exceptions.py`)

```python
class ContentPilotBaseException(Exception):
    """Base domain exception for ContentPilot AI."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)

class EntityNotFoundException(ContentPilotBaseException):
    def __init__(self, entity_name: str, entity_id: str) -> None:
        super().__init__(
            message=f"{entity_name} with ID {entity_id} was not found.",
            code="RESOURCE_NOT_FOUND"
        )

class AIProviderException(ContentPilotBaseException):
    def __init__(self, provider_name: str, details: str) -> None:
        super().__init__(
            message=f"Upstream AI Provider {provider_name} failed: {details}",
            code="AI_PROVIDER_ERROR"
        )
```

---

## 4. Comprehensive Testing Strategy

ContentPilot AI enforces a multi-layered testing pyramid to guarantee platform reliability before deployment.

```
                  /\
                 /  \     End-to-End Tests (Playwright)
                /    \    Load Tests (Locust)
               /------\
              /        \   Integration & API Tests (Pytest / Vitest)
             /----------\
            /            \ Unit Tests (Pytest Mocks / React Testing Library)
           /--------------\
```

### 4.1 Unit Testing (Pytest) Example (`tests/unit/test_ai_pipeline.py`)

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.ai_pipeline_service import AIPipelineService
from app.domain.entities.article import Article

@pytest.mark.asyncio
async def test_process_article_success():
    # Arrange
    mock_article_repo = AsyncMock()
    mock_post_repo = AsyncMock()
    mock_ai_provider = AsyncMock()

    article_id = uuid4()
    workspace_id = uuid4()
    
    mock_article = Article(
        id=article_id,
        title="Test Headline",
        content="Test content length over 50 words...",
        category="Technology",
        top_image_url="https://example.com/test.jpg"
    )
    mock_article_repo.get_by_id.return_value = mock_article
    mock_ai_provider.summarize_text.return_value = "Concise summary"
    mock_ai_provider.generate_social_caption.return_value = {
        "caption": "Social caption hook",
        "hashtags": ["#Tech", "#AI"]
    }
    mock_ai_provider.analyze_image_vision.return_value = "Glowing processor chip scene"
    mock_ai_provider.build_editorial_image_prompt.return_value = "Editorial prompt text"
    mock_ai_provider.generate_editorial_image.return_value = "https://cdn.example.com/art.webp"

    service = AIPipelineService(
        article_repo=mock_article_repo,
        post_repo=mock_post_repo,
        ai_provider=mock_ai_provider
    )

    # Act
    result = await service.process_article_to_post(
        article_id=article_id,
        workspace_id=workspace_id,
        brand_tone="Professional"
    )

    # Assert
    assert mock_article_repo.get_by_id.called
    assert mock_ai_provider.summarize_text.called
    assert mock_post_repo.save.called
```

---

### 4.2 Load Testing Blueprint (Locust) (`tests/load/locustfile.py`)

```python
from locust import HttpUser, task, between

class ContentPilotUserBehavior(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Authenticate and obtain JWT
        res = self.client.post("/api/v1/auth/login", json={
            "email": "test.user@contentpilot.ai",
            "password": "LoadTestPassword123!"
        })
        token = res.json()["data"]["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}

    @task(3)
    def view_approval_queue(self):
        self.client.get("/api/v1/posts/queue", headers=self.headers)

    @task(1)
    def fetch_analytics(self):
        self.client.get("/api/v1/analytics/overview", headers=self.headers)
```

---

## 5. Git Commit & Branching Conventions

### Conventional Commits Format
Commits must follow the **Conventional Commits** specification:
`<type>(<scope>): <short summary>`

#### Allowed Types:
- `feat`: A new feature added to the codebase.
- `fix`: A bug fix.
- `docs`: Documentation updates only.
- `style`: Code style changes (formatting, missing semi-colons).
- `refactor`: Code change that neither fixes a bug nor adds a feature.
- `test`: Adding missing tests or refactoring existing tests.
- `chore`: Build process, dependency updates, or tool configurations.

#### Examples:
- `feat(ai): add FLUX.1 image generator adapter`
- `fix(publisher): handle Instagram API token expiration error`
- `docs(api): update OpenAPI schemas for queue endpoints`
