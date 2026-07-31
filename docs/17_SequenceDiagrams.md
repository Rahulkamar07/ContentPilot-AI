# ContentPilot AI - Sequence Diagrams & State Machines

## Document Metadata

| Attribute | Value |
| :--- | :--- |
| **Document ID** | `DOC-17-SEQUENCE-STATE-DIAGRAMS` |
| **Author** | Principal Software Architect |
| **Status** | Approved / Enterprise Specification |
| **Current Version** | `1.0.0` |
| **Last Updated** | `2026-07-31` |

### Version History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | 2026-07-31 | Lead Architect | Comprehensive sequence diagrams and state machine specifications. |

---

## 1. System State Machine Diagrams

### 1.1 Article Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> NEW: Feed Discovered
    NEW --> SCRAPED: Ingestion Completed
    SCRAPED --> DUPLICATE: Embedding Similarity Match >= 0.85
    SCRAPED --> PENDING_AI: Unique Article Confirmed
    PENDING_AI --> PROCESSED: AI Synthesis Successful
    PENDING_AI --> FAILED: LLM/Vision Worker Error
    DUPLICATE --> [*]
    PROCESSED --> [*]
    FAILED --> PENDING_AI: Admin Manual Retry
```

---

### 1.2 Social Post Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> DRAFT: AI Synthesis Created
    DRAFT --> PENDING_APPROVAL: Enqueued to Workspace Board
    PENDING_APPROVAL --> APPROVED: User Clicked Approve
    PENDING_APPROVAL --> FAILED: Rejected by User
    APPROVED --> SCHEDULED: Time Slot Assigned
    SCHEDULED --> PUBLISHING: Celery Beat Triggered Slot
    PUBLISHING --> PUBLISHED: Social Platform API 200 OK
    PUBLISHING --> FAILED: API Error / Token Expired
    FAILED --> SCHEDULED: Retry Execution
    PUBLISHED --> [*]
```

---

### 1.3 Social Account Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> CONNECTED: OAuth 2.0 Flow Authorized
    CONNECTED --> EXPIRED: Token Expiry Date Reached
    EXPIRED --> CONNECTED: Token Worker Refresh Successful
    EXPIRED --> DISCONNECTED: OAuth Refresh Revoked
    DISCONNECTED --> CONNECTED: User Re-Authorizes Account
```

---

### 1.4 Worker Job State Machine

```mermaid
stateDiagram-v2
    [*] --> QUEUED: Task Enqueued to Redis
    QUEUED --> RUNNING: Celery Worker Picked Up Task
    RUNNING --> SUCCESS: Function Executed Successfully
    RUNNING --> RETRYING: Network Error / Soft Limit Timeout
    RETRYING --> RUNNING: Exponential Backoff Elapsed
    RETRYING --> FAILED: Max Retries (5) Exceeded (Sent to DLQ)
    SUCCESS --> [*]
    FAILED --> [*]
```

---

## 2. Core Sequence Diagrams

### 2.1 User Registration Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Client as Next.js Web Client
    participant API as FastAPI Gateway
    participant DB as PostgreSQL DB
    participant Auth as JWT Auth Module

    User->>Client: Input email, password, workspace_name
    Client->>API: POST /api/v1/auth/register
    API->>DB: Check if user email exists
    DB-->>API: Email available
    API->>Auth: Hash password (Argon2id)
    API->>DB: Insert User record
    API->>DB: Insert Workspace record (slugified)
    API->>DB: Insert WorkspaceMember (role='OWNER')
    API->>Auth: Generate Access (1h) & Refresh Token (30d)
    API-->>Client: 201 Created {user, workspace, tokens}
    Client-->>User: Redirect to /overview dashboard
```

---

### 2.2 User Login & Token Renewal Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Client as Next.js Web Client
    participant API as FastAPI Gateway
    participant Auth as JWT Auth Module

    User->>Client: Submit login form
    Client->>API: POST /api/v1/auth/login
    API->>Auth: Verify password hash
    Auth-->>API: Password valid
    API->>Auth: Mint JWT Tokens
    API-->>Client: 200 OK {access_token, refresh_token}
    
    note over Client, API: 55 minutes later (Access Token Expiry)
    Client->>API: POST /api/v1/auth/refresh {refresh_token}
    API->>Auth: Validate Refresh Token Signature & DB Session
    Auth-->>API: Refresh valid
    API-->>Client: 200 OK {new_access_token}
```

---

### 2.3 News Scraping Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Beat as Celery Beat
    participant Worker as Scraper Worker
    participant DB as PostgreSQL DB
    participant Web as Target News Portal

    Beat->>Worker: Trigger scrape_news_source(source_id)
    Worker->>DB: Fetch source configuration & URL
    Worker->>Web: Fetch webpage HTML / RSS XML
    Web-->>Worker: Return document content
    Worker->>Worker: Extract title, body, top_image_url
    Worker->>Worker: Hash URL (SHA-256)
    Worker->>DB: Query Article by url_hash
    alt Hash Matches Existing Row
        Worker->>DB: Log duplicate skip
    else Unique Hash
        Worker->>Worker: Generate 1536-d text embedding
        Worker->>DB: Save Article (status='PENDING_AI')
    end
```

---

### 2.4 AI Processing Pipeline Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Worker as AI Pipeline Worker
    participant DB as PostgreSQL DB
    participant LLM as OpenAI / Gemini Provider
    participant S3 as S3 Object Storage

    Worker->>DB: Lock next Article (status='PENDING_AI')
    Worker->>LLM: Summarize text (gpt-4o-mini)
    LLM-->>Worker: Return factual summary
    Worker->>LLM: Generate social caption & hashtags
    LLM-->>Worker: Return JSON {caption, hashtags}
    Worker->>LLM: Vision scene analysis on top_image_url
    LLM-->>Worker: Return descriptive visual scene prompt
    Worker->>LLM: Synthesize image render (FLUX.1-Dev / SDXL)
    LLM-->>Worker: Return image binary
    Worker->>Worker: Apply workspace visual logo watermark
    Worker->>S3: Upload branded WEBP image
    S3-->>Worker: Return S3 URL
    Worker->>DB: Insert SocialPost (status='PENDING_APPROVAL')
    Worker->>DB: Update Article (status='PROCESSED')
```

---

### 2.5 Image Generation & Branding Overlay Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Engine as Image Engine
    participant Vision as Multimodal Vision LLM
    participant Diff as Generative Model (FLUX/SDXL)
    participant Brand as Pillow/Canvas Overlay Engine
    participant S3 as S3 Storage

    Engine->>Vision: Send raw source image URL
    Vision-->>Engine: Return text scene description
    Engine->>Engine: Build optimized editorial prompt & negative prompt
    Engine->>Diff: Generate image (1024x1024 / 1080x1350)
    Diff-->>Engine: Raw PNG buffer
    Engine->>Brand: Apply workspace SVG logo at bottom-right corner
    Brand-->>Engine: Watermarked image buffer
    Engine->>Engine: Compress to WEBP (quality=85)
    Engine->>S3: Upload object to s3://contentpilot-media/generated/
    S3-->>Engine: Return public CDN storage URL
```

---

### 2.6 Queue Approval Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Editor
    participant UI as Next.js Queue Page
    participant API as FastAPI Gateway
    participant DB as PostgreSQL DB

    Editor->>UI: View /queue card
    Editor->>UI: Edit caption / hashtags & click "Approve"
    UI->>API: POST /api/v1/posts/{id}/approve
    API->>DB: Check workspace permissions (EDITOR+)
    API->>DB: Update SocialPost (status='APPROVED', scheduled_for=timestamp)
    API-->>UI: 200 OK {status: 'SCHEDULED'}
    UI-->>Editor: Animate card to scheduled tab
```

---

### 2.7 Scheduler Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Beat as Celery Beat
    participant Scheduler as Scheduler Engine
    participant DB as PostgreSQL DB
    participant Queue as Publisher Task Queue

    Beat->>Scheduler: Trigger check_scheduled_posts() every 1 min
    Scheduler->>DB: Select SocialPost where status='APPROVED' AND scheduled_for <= NOW()
    loop For each due post
        Scheduler->>DB: Update post status = 'PUBLISHING'
        Scheduler->>Queue: Enqueue publish_post_task(post_id)
    end
```

---

### 2.8 Publishing Engine Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Worker as Publisher Worker
    participant DB as PostgreSQL DB
    participant Adapter as Instagram Platform Adapter
    participant Meta as Meta Graph API

    Worker->>DB: Fetch SocialPost & decrypted SocialAccount tokens
    Worker->>Adapter: publish_post(post, tokens)
    Adapter->>Meta: POST /v20.0/{ig_user_id}/media (Create Container)
    Meta-->>Adapter: Container ID
    Adapter->>Meta: POST /v20.0/{ig_user_id}/media_publish
    Meta-->>Adapter: Media Post ID
    Adapter-->>Worker: Return SUCCESS {platform_post_id}
    Worker->>DB: Update SocialPost (status='PUBLISHED')
    Worker->>DB: Insert PublishedPostLog (status='SUCCESS')
```

---

### 2.9 Analytics Collection Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Beat as Celery Beat
    participant Worker as Analytics Worker
    participant Meta as Instagram Graph API
    participant DB as PostgreSQL DB

    Beat->>Worker: Trigger collect_analytics_task() every 6 hrs
    Worker->>DB: Fetch published posts from last 30 days
    loop For each post log
        Worker->>Meta: GET /v20.0/{media_id}/insights
        Meta-->>Worker: Metrics JSON {impressions, reach, engagement}
        Worker->>DB: Insert AnalyticsMetrics partition row
    end
```

---

### 2.10 Multi-Channel Notification Flow Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Dispatcher as Notification Dispatcher
    participant DB as PostgreSQL DB
    participant Email as SendGrid API
    participant Slack as Slack Webhook
    participant UI as WebSocket Server

    Dispatcher->>DB: Post publish failed or queue item pending approval
    Dispatcher->>DB: Fetch workspace user notification preferences
    par Send Email
        Dispatcher->>Email: Send failure alert template
    and Trigger Slack
        Dispatcher->>Slack: Post webhook alert JSON
    and Real-Time WebSockets
        Dispatcher->>UI: Emit event 'notification:new'
    end
```

---

## Document Cross-References
- Global System Blueprint: [00_MasterBlueprint.md](file:///d:/Projects/ContentPilot/docs/00_MasterBlueprint.md)
- Core System Architecture: [Architecture.md](file:///d:/Projects/ContentPilot/docs/Architecture.md)
- Database Design & ERD: [Database.md](file:///d:/Projects/ContentPilot/docs/Database.md)
- REST API Specification: [API.md](file:///d:/Projects/ContentPilot/docs/API.md)
