# ContentPilot AI - Data Lifecycle & Retention Architecture

## Document Metadata

| Attribute | Value |
| :--- | :--- |
| **Document ID** | `DOC-31-DATA-LIFECYCLE` |
| **Author** | Principal Software Architect |
| **Status** | Approved / Enterprise Specification |
| **Current Version** | `1.0.0` |
| **Last Updated** | `2026-07-31` |

### Version History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | 2026-07-31 | Data Lead | Data retention, archival, and purging lifecycle policy baseline. |

---

## 1. Master Data Retention & Lifecycle Matrix

| Entity / Asset Category | Active Retention | Archive Retention | Hard Deletion / Purge | Purge Trigger Job |
| :--- | :--- | :--- | :--- | :--- |
| **Scraped News Articles** | 30 Days | 90 Days (Glacier) | 120 Days | Celery Daily Cron (`purge_old_articles`) |
| **Generated Social Posts** | Indefinite | 365 Days | User Request Only | Manual / Tenant Deletion |
| **Generated AI Artwork (S3)**| 90 Days (S3 Standard)| 365 Days (Glacier) | 730 Days | S3 Lifecycle Policy |
| **System Audit Logs** | 180 Days | 730 Days | 730 Days | Partition Drop Script |
| **Analytics Snapshots** | 180 Days | 365 Days | 365 Days | Partition Drop Script |
| **User Notifications** | 30 Days | N/A | 60 Days | Celery Weekly Cron (`purge_notifications`) |

---

## 2. Automated Purging Celery Jobs

```python
from app.workers.celery_app import celery_app
from datetime import datetime, timedelta
from sqlalchemy import delete
from app.infrastructure.database.models import ArticleModel
from app.infrastructure.database.base import async_session_factory

@celery_app.task(name="tasks.purge_old_articles", queue="scraper_queue")
async def purge_old_articles():
    """Purges scraped articles older than 120 days that were never posted."""
    cutoff_date = datetime.utcnow() - timedelta(days=120)
    async with async_session_factory() as session:
        stmt = delete(ArticleModel).where(
            ArticleModel.scraped_at < cutoff_date,
            ArticleModel.status.in_(["DUPLICATE", "FAILED"])
        )
        result = await session.execute(stmt)
        await session.commit()
        return {"purged_row_count": result.rowcount}
```

---

## Document Cross-References
- Storage Architecture: [19_Storage.md](file:///d:/Projects/ContentPilot/docs/19_Storage.md)
- Legal & Privacy Compliance: [27_LegalCompliance.md](file:///d:/Projects/ContentPilot/docs/27_LegalCompliance.md)
- Database Design & Partitions: [Database.md](file:///d:/Projects/ContentPilot/docs/Database.md)
