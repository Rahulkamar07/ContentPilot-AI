# ContentPilot AI - REST API Specification

## 1. Global API Standards

- **Base URL**: `https://api.contentpilot.ai/api/v1`
- **Protocol**: HTTPS / WSS
- **Content Type**: `application/json`
- **Authentication**: `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Tenant Context Header**: `X-Workspace-ID: <WORKSPACE_UUID>`

### Standard Response Envelope
All API endpoints return responses wrapped in a consistent JSON structure:

```json
{
  "success": true,
  "code": "OK",
  "message": "Operation completed successfully",
  "data": {},
  "meta": {
    "timestamp": "2026-07-31T19:40:00Z",
    "request_id": "req_8f9a2b1c4d"
  }
}
```

### Standard Error Response Format

```json
{
  "success": false,
  "code": "RESOURCE_NOT_FOUND",
  "message": "Article with ID 3fa85f64-5717-4562-b3fc-2c963f66afa6 not found",
  "errors": [
    {
      "field": "article_id",
      "issue": "No matching record exists for the current workspace"
    }
  ],
  "meta": {
    "timestamp": "2026-07-31T19:40:00Z",
    "request_id": "req_8f9a2b1c4d"
  }
}
```

---

## 2. API Endpoints Catalog

### 2.1 Authentication & User Management

#### `POST /auth/register`
Register a new user account.

**Request Body**:
```json
{
  "email": "alex.engineer@contentpilot.ai",
  "password": "SecurePassword123!",
  "full_name": "Alex Engineer",
  "workspace_name": "Tech News Digest"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "code": "CREATED",
  "message": "User and workspace created successfully",
  "data": {
    "user": {
      "id": "11111111-1111-1111-1111-111111111111",
      "email": "alex.engineer@contentpilot.ai",
      "full_name": "Alex Engineer",
      "role": "USER"
    },
    "workspace": {
      "id": "22222222-2222-2222-2222-222222222222",
      "name": "Tech News Digest",
      "slug": "tech-news-digest"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "refresh_token": "d9a8f2e7c1...",
      "token_type": "Bearer",
      "expires_in": 3600
    }
  }
}
```

#### `POST /auth/login`
Authenticate user credentials and acquire JWT tokens.

**Request Body**:
```json
{
  "email": "alex.engineer@contentpilot.ai",
  "password": "SecurePassword123!"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "refresh_token": "d9a8f2e7c1...",
    "expires_in": 3600
  }
}
```

---

### 2.2 Workspace Management

#### `GET /workspaces`
List all workspaces accessible to the authenticated user.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "22222222-2222-2222-2222-222222222222",
      "name": "Tech News Digest",
      "slug": "tech-news-digest",
      "plan_tier": "PRO",
      "role": "OWNER"
    }
  ]
}
```

---

### 2.3 News Sources & Article Storage

#### `POST /news-sources`
Add a new RSS or Web Portal source for scraper ingestion.

**Headers**: `X-Workspace-ID: 22222222-2222-2222-2222-222222222222`

**Request Body**:
```json
{
  "name": "TechCrunch AI Feed",
  "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
  "feed_type": "RSS",
  "category": "Technology",
  "scrape_interval_minutes": 15
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "id": "33333333-3333-3333-3333-333333333333",
    "name": "TechCrunch AI Feed",
    "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "feed_type": "RSS",
    "category": "Technology",
    "is_active": true,
    "scrape_interval_minutes": 15,
    "last_scraped_at": null
  }
}
```

#### `GET /articles`
Fetch articles ingested by scrapers.

**Query Parameters**:
- `status`: `PENDING_AI` | `PROCESSED` | `DUPLICATE`
- `category`: `Technology` | `Business` | `Science`
- `page`: `1`
- `limit`: `20`

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "44444444-4444-4444-4444-444444444444",
      "title": "Breakthrough in AI Chip Efficiency Announced",
      "url": "https://example.com/news/ai-chip-breakthrough",
      "category": "Technology",
      "top_image_url": "https://images.example.com/source-chip.jpg",
      "status": "PENDING_AI",
      "scraped_at": "2026-07-31T19:15:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total_count": 142,
    "total_pages": 8
  }
}
```

---

### 2.4 AI Synthesis Engine

#### `POST /ai/process-article`
Trigger complete AI pipeline processing for an ingested article (summarization, vision scene analysis, caption, and editorial image generation).

**Request Body**:
```json
{
  "article_id": "44444444-4444-4444-4444-444444444444",
  "brand_tone": "Professional yet Engaging",
  "target_platforms": ["INSTAGRAM", "X"]
}
```

**Response (202 Accepted)**:
```json
{
  "success": true,
  "code": "TASK_ENQUEUED",
  "message": "Article AI processing pipeline queued",
  "data": {
    "task_id": "celery_task_89a1f2e",
    "article_id": "44444444-4444-4444-4444-444444444444",
    "estimated_completion_seconds": 12
  }
}
```

#### `POST /ai/generate-editorial-image`
Direct execution endpoint for generating a copyright-free editorial image using Vision scene description prompt transformation.

**Request Body**:
```json
{
  "source_image_url": "https://images.example.com/source-chip.jpg",
  "article_summary": "Engineers build custom 3nm microchip optimized for transformer LLMs.",
  "aspect_ratio": "1:1",
  "model_engine": "FLUX_1_DEV"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "vision_scene_description": "Close-up macro of a futuristic silicon wafer glowing with neon blue micro-circuits inside a high-tech cleanroom laboratory.",
    "generated_prompt": "Editorial news illustration, macro view of glowing silicon neural processor chip, futuristic cyan and violet lighting, cleanroom aesthetic, highly detailed 8k photography style, hyper-realistic, photorealistic editorial art.",
    "storage_url": "https://cdn.contentpilot.ai/images/generated/chip_editorial_98f12.webp",
    "aspect_ratio": "1:1"
  }
}
```

---

### 2.5 Queue & Manual Approval System

#### `GET /posts/queue`
Retrieve posts waiting in the queue for manual review.

**Query Parameters**:
- `status`: `PENDING_APPROVAL` | `APPROVED` | `SCHEDULED`

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "55555555-5555-5555-5555-555555555555",
      "article_id": "44444444-4444-4444-4444-444444444444",
      "caption": "🚀 Massive step forward in AI hardware! Engineers unveiled a 3nm processor designed specifically for next-gen neural networks. Expect faster inference and 40% lower power consumption.",
      "hashtags": ["#AI", "#TechNews", "#Hardware", "#Innovation", "#FutureTech"],
      "image_url": "https://cdn.contentpilot.ai/images/generated/chip_editorial_98f12.webp",
      "target_platforms": ["INSTAGRAM"],
      "status": "PENDING_APPROVAL",
      "scheduled_for": "2026-08-01T14:00:00Z"
    }
  ]
}
```

#### `POST /posts/{id}/approve`
Approve a post and transition it into the scheduler queue.

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Post approved successfully and scheduled for publication",
  "data": {
    "id": "55555555-5555-5555-5555-555555555555",
    "status": "SCHEDULED",
    "approved_by": "Alex Engineer",
    "scheduled_for": "2026-08-01T14:00:00Z"
  }
}
```

---

### 2.6 Publishing Engine

#### `POST /publish/trigger-post/{id}`
Immediately publish an approved post across its designated platform adapters.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "post_id": "55555555-5555-5555-5555-555555555555",
    "results": [
      {
        "platform": "INSTAGRAM",
        "account_id": "66666666-6666-6666-6666-666666666666",
        "status": "SUCCESS",
        "platform_post_id": "1803482910394829",
        "post_url": "https://www.instagram.com/p/C-X8192aF/"
      }
    ]
  }
}
```

---

### 2.7 Analytics Dashboard

#### `GET /analytics/overview`
Get aggregate engagement metrics for published posts.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "total_published_posts": 284,
    "aggregate_metrics": {
      "impressions": 482900,
      "reach": 312000,
      "likes": 24910,
      "comments": 1820,
      "shares": 3410
    },
    "top_performing_category": "Technology"
  }
}
```

---

## 3. Error Codes & Taxonomy

| Code | HTTP Status | Meaning / Trigger |
| :--- | :--- | :--- |
| `UNAUTHORIZED` | `401` | Missing, invalid, or expired Bearer token |
| `FORBIDDEN` | `403` | User role lacks permissions in workspace |
| `RESOURCE_NOT_FOUND` | `404` | Target entity ID does not exist |
| `RATE_LIMIT_EXCEEDED` | `429` | Workspace exceeded hourly API request quota |
| `AI_PROVIDER_ERROR` | `502` | Upstream AI Provider (OpenAI/Gemini) failed |
| `PUBLISH_FAILED` | `500` | Social platform API rejected post payload |

---

## 4. API Versioning, Deprecation & Migration Strategy

### 4.1 URI Versioning Policy
- All REST API endpoints include an explicit major version prefix in the URL path (`/api/v1/...`).
- Backward-compatible additions (new endpoints, new optional JSON fields) are introduced within the current major version without incrementing the version prefix.
- Breaking changes (field removals, type alterations, mandatory header additions) trigger a major version bump (`/api/v2/...`).

### 4.2 Deprecation Lifecycle & Sunset Headers
When an API version or endpoint is scheduled for sunset:
1. **Minimum Deprecation Window**: 6 months prior notice before endpoint retirement.
2. **HTTP Sunset Headers**: Deprecated endpoints return RFC 8594 response headers:
   ```http
   Deprecation: @1785542400
   Sunset: Sun, 01 Feb 2027 00:00:00 GMT
   Link: <https://api.contentpilot.ai/docs/migration-v2>; rel="deprecation"
   ```
3. **Backward Compatibility Safeguard**: Deprecated endpoints forward requests to legacy transformation adapters during the 6-month deprecation grace period.

