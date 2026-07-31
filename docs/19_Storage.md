# ContentPilot AI - Multi-Tier Storage Architecture Specification

## Document Metadata

| Attribute | Value |
| :--- | :--- |
| **Document ID** | `DOC-19-STORAGE-ARCHITECTURE` |
| **Author** | Principal Software Architect |
| **Status** | Approved / Enterprise Specification |
| **Current Version** | `1.0.0` |
| **Last Updated** | `2026-07-31` |

### Version History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | 2026-07-31 | Lead Architect | Multi-tier object storage architecture specification baseline. |

---

## 1. Storage Architecture Overview

ContentPilot AI categorizes binary assets into specialized storage tiers according to access frequency, size, privacy, and retention constraints.

```
AWS S3 / GCS Object Storage Bucket Hierarchy
├── s3://contentpilot-media-prod/
│   ├── workspace_assets/            # Private Brand Assets & Logos
│   │   └── {workspace_id}/
│   │       ├── logo_primary.svg
│   │       ├── logo_watermark.png
│   │       └── custom_fonts/
│   ├── generated_images/            # Synthesized AI Editorial Art (Public CDN)
│   │   └── {yyyy}/{mm}/{dd}/
│   │       ├── img_8f9a2b1c4d_1x1.webp
│   │       └── img_8f9a2b1c4d_4x5.webp
│   ├── source_news_cache/           # Raw Source News Images (Internal Cache)
│   │   └── {yyyy}/{mm}/{dd}/
│   │       └── source_e3b0c442.jpg
│   ├── generated_videos/            # Future Phase 3 Shorts / TikTok MP4s
│   │   └── {yyyy}/{mm}/{dd}/
│   │       └── vid_8f9a2b1c4d.mp4
│   ├── temp_scratch/                # Ephemeral Processing Buffers
│   └── database_backups/            # Encrypted WAL & Database Backups
```

---

## 2. Media Asset Lifecycle & Retention Matrix

| Asset Class | Format / Extension | Target Location | Storage Class | Lifecycle / Expiry Policy |
| :--- | :--- | :--- | :--- | :--- |
| **Generated AI Artwork** | `.webp` / `.png` | `generated_images/` | S3 Standard → Glacier | Standard for 90 days; Transition to Glacier after 365 days |
| **Workspace Brand Logos** | `.svg` / `.png` | `workspace_assets/` | S3 Standard | Retained indefinitely while workspace is active |
| **Source News Images** | `.jpg` / `.webp` | `source_news_cache/` | S3 Standard-IA | Auto-deleted after 14 days |
| **Ephemeral Temp Files** | `.tmp` / `.raw` | `temp_scratch/` | Local `/tmp` or S3 | Auto-deleted after 24 hours |
| **Database Backups** | `.tar.gz` / `.pgdump` | `database_backups/` | S3 Glacier Flexible | Retained for 90 days (daily backups) |
| **System Logs** | `.json` / `.log` | CloudWatch / S3 | S3 Standard-IA | Retained for 180 days for audit compliance |

---

## 3. Storage Security & Encryption Controls

1. **Encryption at Rest**: Server-Side Encryption with Amazon S3 Managed Keys (`SSE-S3`) or AWS KMS (`SSE-KMS`) enforced across all buckets.
2. **Access Control**:
   - `workspace_assets/` and `database_backups/`: **Private Bucket Access** only. Access granted via short-lived (15-minute expiration) AWS S3 Presigned URLs.
   - `generated_images/`: **Public Read** served exclusively via Cloudflare CDN caching layer (`https://cdn.contentpilot.ai/media/...`).
3. **CORS Policy**: Configured to restrict origin requests strictly to ContentPilot AI web client domains (`https://app.contentpilot.ai`).

---

## Document Cross-References
- Global System Blueprint: [00_MasterBlueprint.md](file:///d:/Projects/ContentPilot/docs/00_MasterBlueprint.md)
- Infrastructure Deployment: [Deployment.md](file:///d:/Projects/ContentPilot/docs/Deployment.md)
- Brand Visual System: [23_BrandSystem.md](file:///d:/Projects/ContentPilot/docs/23_BrandSystem.md)
- Disaster Recovery & BCP: [26_DisasterRecovery.md](file:///d:/Projects/ContentPilot/docs/26_DisasterRecovery.md)
