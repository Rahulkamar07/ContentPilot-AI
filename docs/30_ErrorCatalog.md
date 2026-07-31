# ContentPilot AI - Standard Error Catalog & Resolution Runbooks

## Document Metadata

| Attribute | Value |
| :--- | :--- |
| **Document ID** | `DOC-30-ERROR-CATALOG` |
| **Author** | Principal Support & Operations Architect |
| **Status** | Approved / Enterprise Specification |
| **Current Version** | `1.0.0` |
| **Last Updated** | `2026-07-31` |

### Version History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | 2026-07-31 | Operations Lead | Initial operational error catalog & runbook specification. |

---

## 1. Master System Error Catalog

| Error Code | HTTP Status | Root Cause | Operational Resolution Runbook |
| :--- | :---: | :--- | :--- |
| `UNAUTHORIZED` | `401` | Missing, expired, or invalid JWT Bearer token | Client app must refresh token via `/auth/refresh` or re-login user. |
| `FORBIDDEN_ROLE` | `403` | User RBAC role lacks privilege for requested workspace operation | Verify user role in `workspace_members`; grant `ADMIN` or `OWNER` if appropriate. |
| `RESOURCE_NOT_FOUND` | `404` | Entity UUID does not exist or does not belong to active workspace | Verify UUID path parameter and workspace tenant header (`X-Workspace-ID`). |
| `RATE_LIMIT_EXCEEDED` | `429` | Workspace exceeded hourly API request or image generation quota | Check workspace subscription tier in `workspaces` table; request client upgrade to `PRO`/`ENTERPRISE`. |
| `SCRAPER_PARSING_FAILED` | `502` | Target RSS feed or HTML portal DOM structure changed | Update Playwright DOM selectors in `playwright_scraper.py` or check if target site blocked IP. |
| `AI_PROVIDER_TIMEOUT` | `504` | Upstream OpenAI/Gemini/Ollama model API timed out (> 15s) | System automatically triggers model fallback cascade (Switch to `gpt-4o-mini` or Local Ollama). |
| `AI_JSON_PARSE_ERROR` | `422` | LLM output failed Pydantic output schema validation | Trigger automated prompt retry with structured JSON repair system prompt. |
| `INSTAGRAM_TOKEN_EXPIRED` | `400` | Instagram Graph API long-lived user token revoked or expired | Send in-app & email notification asking workspace admin to re-authorize Instagram account. |
| `PUBLISH_COLLISION` | `409` | Scheduled post violates 120-minute channel collision rule | Scheduler automatically defers post to the next open timezone slot. |

---

## 2. Support Engineer Operational Runbook

### Runbook: Handling `INSTAGRAM_TOKEN_EXPIRED` Alerts
1. Query `social_accounts` table: `SELECT * FROM social_accounts WHERE status = 'EXPIRED';`
2. Trigger automated token renewal background task: `celery -A app.workers.celery_app call tasks.refresh_social_tokens`.
3. If refresh fails (OAuth grant revoked), update status to `DISCONNECTED` and dispatch `OAUTH_TOKEN_EXPIRING` notification to workspace owner.

---

## Document Cross-References
- REST API Specification: [API.md](file:///d:/Projects/ContentPilot/docs/API.md)
- Multi-Channel Notifications: [25_Notifications.md](file:///d:/Projects/ContentPilot/docs/25_Notifications.md)
- Threat Model & Controls: [28_ThreatModel.md](file:///d:/Projects/ContentPilot/docs/28_ThreatModel.md)
