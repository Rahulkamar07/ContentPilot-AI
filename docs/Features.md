# ContentPilot AI - Core Features & System Capabilities

## 1. Core Feature Matrix

ContentPilot AI provides an end-to-end automated platform for discovering news, synthesizing original media, reviewing content, scheduling, and publishing across multi-platform social networks.

---

## 2. Feature Specifications

### 2.1 News Source Management & Scraping Engine

#### **Description**
Allows users to configure RSS feeds, Web Portals, and News APIs across 11 standard content categories (*Technology, Business, Sports, Anime, Gaming, Finance, Science, Space, Entertainment, Politics, Health*).

#### **User Flow**
1. User clicks **"Add News Source"** in the workspace dashboard.
2. Selects source type (`RSS`, `HTML_PLAYWRIGHT`, or `REST_API`), inputs the feed URL, category, and scraping interval (e.g., 15 minutes).
3. The backend validates the RSS XML structure or executes a test Playwright render.
4. Background Celery worker fetches articles periodically, generates SHA-256 URL hashes, computes vector embeddings, and stores non-duplicate articles in PostgreSQL.

#### **Acceptance Criteria (Gherkin)**
```gherkin
Feature: News Source Ingestion
  Scenario: Successfully adding a valid RSS Feed
    Given the workspace user is on the "News Sources" configuration page
    When the user submits a valid RSS feed URL "https://techcrunch.com/feed/" with category "Technology"
    Then the system validates the feed content
    And creates a active "NewsSource" record with a 15-minute polling interval
    And triggers an initial async scrape task in Celery

  Scenario: Filtering out duplicate news articles
    Given an ingested article with URL hash "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    When the scraper encounters an article with the identical URL hash
    Then the article status is marked as "DUPLICATE"
    And no duplicate row is processed by the AI Pipeline
```

---

### 2.2 Vision-Driven AI Image Synthesis Engine

#### **Description**
Transforms news source imagery into original, copyright-free editorial artwork. Rather than direct image cloning or unauthorized reposting, the system uses a Multimodal Vision model (`gpt-4o` or `gemini-1.5-pro`) to analyze the visual scene, constructs a descriptive image prompt, and synthesizes a fresh editorial illustration using FLUX or Stable Diffusion XL.

#### **User Flow**
```
Source Article Image
        │
        ▼
[Vision Model] --> Generates: "Macro shot of futuristic glowing quantum computer chip in cleanroom"
        │
        ▼
[Prompt Synthesizer] --> Appends style tokens: "Editorial 8k photorealistic illustration, neon cyan accent, cinematic light"
        │
        ▼
[Generative Diffusion Engine] --> Renders 1024x1024 / 1080x1350 WEBP artwork
        │
        ▼
[Branding Engine] --> Overlays workspace logo watermark in bottom-right corner
```

#### **Acceptance Criteria (Gherkin)**
```gherkin
Feature: Copyright-Safe AI Image Generation
  Scenario: Converting a news photograph into an original editorial render
    Given an article containing top source image "https://example.com/photo.jpg"
    When the AI worker executes the vision analysis step
    Then a detailed text scene description is extracted
    And a generative prompt is constructed without copying original pixels
    And FLUX generates a unique 1:1 aspect ratio editorial image stored in S3
```

---

### 2.3 AI Caption & Hashtag Synthesis Engine

#### **Description**
Generates platform-optimized captions tailored to the specified workspace brand tone (*Professional, Casual, Hype, Analytical, Satirical*) alongside relevant, non-spammy hashtags.

#### **Functional Requirements**:
- Generates tailored post variations per platform (e.g., concise for X with < 280 chars; rich paragraph structure with call-to-action for Instagram).
- Generates 5 to 15 relevant hashtags per post based on category and current trending keywords.

---

### 2.4 Human-in-the-Loop Content Approval Queue

#### **Description**
Provides a visual Kanban board and card queue where team members can review AI-generated posts before public distribution.

#### **Features**:
- **One-Click Actions**: `Approve`, `Reject`, `Regenerate Caption`, `Regenerate Image`.
- **Inline Editing**: Real-time text field editing for captions and hashtags prior to approval.
- **Bulk Operations**: Bulk approve selected queued posts for weekend scheduling.

#### **Acceptance Criteria (Gherkin)**
```gherkin
Feature: Queue Approval Workflow
  Scenario: User approves a pending post for Instagram
    Given a social post with status "PENDING_APPROVAL"
    When the user clicks "Approve Post" on the queue card
    Then the status transitions to "SCHEDULED"
    And the scheduled timestamp is locked into the Celery publisher queue
```

---

### 2.5 Timezone-Aware Automated Scheduler

#### **Description**
Distributes approved posts evenly across configurable daily posting slots based on target audience timezones (e.g., 9:00 AM EST, 2:00 PM EST, 7:00 PM EST).

#### **Features**:
- Supports multiple posts per category daily.
- Automatically prevents channel collision (e.g., minimum 2-hour delay between consecutive posts on the same Instagram account).

---

### 2.6 Multi-Platform Publisher Engine

#### **Description**
Publishes approved content across supported platform adapters (*Version 1: Instagram Graph API; Future: X, LinkedIn, Facebook, Threads, Telegram*).

#### **Features**:
- **Automated Access Token Renewal**: OAuth refresh worker refreshes tokens 7 days prior to expiry.
- **Stealth Fallback Scraper/Publisher**: Uses Playwright headless sessions if official APIs undergo temporary outages.
- **Idempotency Safeguard**: Ensures no post is published twice by checking `published_post_logs`.

---

### 2.7 Multi-Tenant Workspace & RBAC Management

#### **Description**
Allows agency clients and media teams to manage multiple distinct client workspaces with role-based access permissions.

#### **Role Matrix**:

| Feature / Action | OWNER | ADMIN | EDITOR | VIEWER |
| :--- | :---: | :---: | :---: | :---: |
| Manage Workspace & Billing | Yes | No | No | No |
| Connect Social Accounts | Yes | Yes | No | No |
| Configure News Sources | Yes | Yes | Yes | No |
| Approve / Reject Queue Posts | Yes | Yes | Yes | No |
| View Dashboard & Analytics | Yes | Yes | Yes | Yes |

---

### 2.8 Engagement Analytics Dashboard

#### **Description**
Tracks performance metrics across connected social platforms to measure reach and optimize AI content generation parameters.

#### **Tracked Metrics**:
- Impressions, Reach, Likes, Comments, Shares, Link Clicks.
- Top-performing content category analysis.
- Best posting time recommendations based on historic engagement.
