# ADR-0004: Playwright Headless Engine for Stealth News Scraping

## Context & Problem Statement
Many target news portals use dynamic JavaScript hydration (React/Next.js) or anti-bot protections (Cloudflare turnstile, Imperva) that render traditional HTTP requests (`requests`/`httpx`) ineffective for extracting article text and lead photographs.

## Decision Drivers
- Ability to execute full JavaScript render pipelines in a real browser context.
- Headless Chromium speed and stealth fingerprint customization via `playwright-stealth`.
- Async Python API compatible with FastAPI and asyncio worker event loops.

## Considered Options
1. **Playwright (Python Async)**
2. **Selenium WebDriver**
3. **Scrapy + Splash**

## Decision Outcome
**Chosen Option**: **Playwright**.
Playwright provides superior speed, modern headless browser protocol support, automatic wait conditions, and reliable DOM element extraction compared to Selenium.

### Positive Consequences
- Bypasses client-side rendering bottlenecks on SPA news websites.
- Extracts clean OpenGraph metadata and high-resolution lead images.

### Negative Consequences
- Higher RAM footprint per Chromium instance (~150MB per worker thread). Scraper queues must be resource-budgeted.
