# ContentPilot AI - Automation, Scraping & Social Publisher Engine

## 1. Asynchronous Task Orchestration

ContentPilot AI relies on **Celery 5.4** backed by **Redis 7** for high-throughput background processing, periodic task scheduling, and queue isolation.

### Queue Architecture

```
                       +-------------------------+
                       |      Celery Beat        |
                       |  (Periodic Scheduler)   |
                       +------------+------------+
                                    |
                                    v
                       +-------------------------+
                       |       Redis Broker      |
                       +------------+------------+
                                    |
            +-----------------------+-----------------------+
            |                       |                       |
            v                       v                       v
  +------------------+    +------------------+    +-------------------+
  |  scraper_queue   |    |     ai_queue     |    |  publisher_queue  |
  +--------+---------+    +--------+---------+    +---------+---------+
           |                       |                        |
           v                       v                        v
+--------------------+   +-------------------+   +--------------------+
|  Scraper Workers   |   |    AI Workers     |   | Publisher Workers  |
| (Playwright/HTTPX) |   | (LLM/Vision/FLUX) |   | (Platform Adapters)|
+--------------------+   +-------------------+   +--------------------+
```

---

## 2. Playwright Stealth News Scraping Engine

For news web portals without valid RSS feeds, ContentPilot AI executes headless browser automation via **Playwright** with stealth patches (`playwright-stealth`) to bypass bot detection.

### 2.1 Playwright Scraper Implementation (`app/infrastructure/external/scrapers/playwright_scraper.py`)

```python
import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

class PlaywrightNewsScraper:
    """Stealth browser scraper extracting article content and lead imagery."""

    async def scrape_article(self, target_url: str) -> Optional[Dict[str, Any]]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()

            try:
                # Navigate and wait for content DOM
                await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_selector("article, main, body", timeout=10000)
                
                content_html = await page.content()
                soup = BeautifulSoup(content_html, "html.parser")

                # Extract headline
                title = soup.find("h1")
                headline = title.get_text().strip() if title else ""

                # Extract top lead image (OpenGraph or main image tag)
                og_image = soup.find("meta", property="og:image")
                image_url = og_image["content"] if og_image and og_image.get("content") else None

                # Extract main body text
                paragraphs = soup.find_all("p")
                body_text = "\n\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40])

                if not headline or len(body_text) < 100:
                    return None

                return {
                    "title": headline,
                    "content": body_text,
                    "top_image_url": image_url,
                    "url": target_url,
                }

            except Exception as e:
                return None
            finally:
                await browser.close()
```

---

## 3. Platform Adapter Pattern Architecture

To add future social platforms (*Threads, Facebook, LinkedIn, X, Telegram*) without breaking existing codebase logic, ContentPilot AI enforces the **Platform Adapter Pattern**.

### 3.1 Social Platform Abstract Interface (`app/domain/interfaces/social_platform.py`)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from app.domain.entities.post import GeneratedPost

class SocialPlatformAdapterInterface(ABC):
    """Abstract interface contract for all social network platform adapters."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Returns platform identifier (e.g. 'INSTAGRAM', 'X')."""
        pass

    @abstractmethod
    async def publish_post(
        self, post: GeneratedPost, credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Publishes post image and caption to platform API."""
        pass

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refreshes expired OAuth tokens."""
        pass
```

---

### 3.2 Instagram Graph API Platform Adapter (`app/infrastructure/external/social/instagram_adapter.py`)

```python
import httpx
from typing import Dict, Any
from app.domain.interfaces.social_platform import SocialPlatformAdapterInterface
from app.domain.entities.post import GeneratedPost

class InstagramPlatformAdapter(SocialPlatformAdapterInterface):
    """Instagram Graph API adapter using 2-step media container publishing."""

    @property
    def platform_name(self) -> str:
        return "INSTAGRAM"

    async def publish_post(self, post: GeneratedPost, credentials: Dict[str, Any]) -> Dict[str, Any]:
        access_token = credentials["access_token"]
        ig_user_id = credentials["platform_user_id"]
        full_caption = f"{post.caption}\n\n" + " ".join(post.hashtags)

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Create Media Item Container
            container_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media"
            container_payload = {
                "image_url": post.image_url,
                "caption": full_caption,
                "access_token": access_token
            }
            res1 = await client.post(container_url, data=container_payload)
            res1.raise_for_status()
            creation_id = res1.json()["id"]

            # Step 2: Publish Media Container
            publish_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": access_token
            }
            res2 = await client.post(publish_url, data=publish_payload)
            res2.raise_for_status()
            published_media_id = res2.json()["id"]

            return {
                "status": "SUCCESS",
                "platform_post_id": published_media_id,
                "post_url": f"https://www.instagram.com/p/{published_media_id}/"
            }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        # Implementation for refreshing Instagram long-lived page tokens
        pass
```

---

## 4. Failure Recovery, Retries & Dead-Letter Queue (DLQ)

### 4.1 Celery Task Retry Decorator with Exponential Backoff

```python
from app.workers.celery_app import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task(
    bind=True,
    name="tasks.publish_post_task",
    queue="publisher_queue",
    max_retries=5,
    default_retry_delay=60, # 1 min initial delay
    autoretry_for=(httpx.HTTPStatusError, httpx.RequestError),
    retry_backoff=True,     # Exponential backoff: 1m, 2m, 4m, 8m, 16m
    retry_backoff_max=1800, # Max 30 minutes
)
def publish_post_task(self, post_id: str, workspace_id: str):
    try:
        logger.info(f"Executing post publication task for post {post_id}")
        # Orchestrate execution via use case...
    except Exception as exc:
        if self.request.retries == self.max_retries:
            logger.error(f"Post {post_id} reached max retries. Routing to Dead-Letter Queue (DLQ).")
            # Push task metadata to DLQ PostgreSQL log table for manual admin review
        raise exc
```

### 4.2 Dead-Letter Queue (DLQ) Strategy
- When a task fails after 5 retries (e.g. invalid social token, API outage), the task state is set to `FAILED`.
- An entry is inserted into `PublishedPostLogs` with error details, and an in-app `UserNotification` is sent to the workspace admins.

---

## 5. Granular Subsystem Retry & Resilience Matrix

Every external subsystem integration implements custom retry policies and circuit breakers:

| Subsystem Component | Max Retries | Initial Delay | Backoff Strategy | Hard Timeout | Failure Resolution Protocol |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **HTTP / RSS Scrapers** | 3 | 15s | Exponential ($15\text{s}, 30\text{s}, 60\text{s}$) | 30s | Skip article ingestion; log domain warning |
| **Playwright Browser** | 2 | 5s | Linear ($5\text{s}, 10\text{s}$) | 45s | Fallback to HTTP text-only parser |
| **LLM Summarizer / Vision** | 3 | 2s | Exponential ($2\text{s}, 4\text{s}, 8\text{s}$) | 15s | Trigger Model Fallback Cascade (Cloud → Local) |
| **FLUX / SDXL Image Gen** | 2 | 5s | Linear ($5\text{s}, 10\text{s}$) | 30s | Fallback to Secondary Diffusion Engine / DALL-E 3 |
| **Instagram Graph API** | 5 | 60s | Exponential ($1\text{m}, 2\text{m}, 4\text{m}, 8\text{m}$) | 30s | Mark Post `FAILED`; routing to DLQ & alert admin |
| **PostgreSQL Database Pool**| 5 | 1s | Exponential ($1\text{s}, 2\text{s}, 4\text{s}$) | 10s | Re-establish `asyncpg` connection pool |
| **Redis Broker** | 10 | 2s | Exponential ($2\text{s}, 4\text{s}, 8\text{s}$) | 15s | Failover to secondary Redis replica node |
| **AWS S3 Object Storage** | 4 | 2s | Exponential ($2\text{s}, 4\text{s}, 8\text{s}$) | 15s | Retry S3 upload or write to local disk buffer |

