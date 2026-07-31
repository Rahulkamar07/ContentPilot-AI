# ContentPilot AI - Backup & Disaster Recovery Blueprint

## Document Metadata

| Attribute | Value |
| :--- | :--- |
| **Document ID** | `DOC-26-DISASTER-RECOVERY` |
| **Author** | Principal Software Architect & DevOps Lead |
| **Status** | Approved / Enterprise Specification |
| **Current Version** | `1.0.0` |
| **Last Updated** | `2026-07-31` |

### Version History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | 2026-07-31 | Infrastructure Lead | Business continuity & disaster recovery specification. |

---

## 1. Key Recovery Metrics (RPO & RTO)

| Service Target | Recovery Point Objective (RPO) | Recovery Time Objective (RTO) | Strategy |
| :--- | :--- | :--- | :--- |
| **PostgreSQL Database** | **< 5 Minutes** | **< 15 Minutes** | AWS RDS Multi-AZ Automatic Failover + WAL Archiving (PITR) |
| **Redis Cache / State** | **< 1 Hour** | **< 10 Minutes** | ElastiCache Multi-AZ + Hourly RDB Snapshots |
| **S3 Media Storage** | **< 1 Minute** | **< 5 Minutes** | S3 Cross-Region Replication (CRR) to secondary region |
| **FastAPI Backend Server**| **0 Minutes (Zero Downtime)**| **< 3 Minutes** | ECS Auto-Scaling Multi-AZ Tasks behind Application Load Balancer |

---

## 2. Disaster Recovery & Backup Architecture

```mermaid
graph TB
    subgraph Primary AWS Region (us-east-1)
        RDS_Primary[("RDS PostgreSQL Primary<br/>(Multi-AZ Master)")]
        Redis_Primary[("Redis Master Instance")]
        S3_Primary[("S3 Primary Media Bucket<br/>s3://contentpilot-media-prod")]
        WAL_Archiver[WAL Archiver / pgBackRest]
    end

    subgraph Disaster Backup Storage (S3 & Secondary Region)
        S3_CRR[("S3 Secondary Bucket (us-west-2)<br/>(Cross-Region Replication)")]
        S3_Glacier[("S3 Glacier Cold Storage<br/>(WAL Archives & Daily Dumps)")]
    end

    RDS_Primary -->|Sync Replication| RDS_Standby[("RDS Standby Node")]
    RDS_Primary --> WAL_Archiver --> S3_Glacier
    S3_Primary -->|Async Replication (CRR)| S3_CRR
```

---

## 3. Recovery Runbooks

### 3.1 Scenario: Primary PostgreSQL Instance Failure
1. **Detection**: AWS RDS Multi-AZ health check detects master failure.
2. **Automated Action**: RDS automatically promotes Standby replica to Master in under 60 seconds; DNS endpoint updates seamlessly.
3. **Verification**: FastAPI connection pool (`asyncpg`) re-establishes connections automatically.

### 3.2 Scenario: Data Corruption / Accidental Table Deletion
1. **Point-In-Time-Recovery (PITR)**: Initiate RDS restore to a timestamp 1 minute prior to corruption event using WAL logs.
2. **Data Reconciliation**: Export recovered table delta and merge into production via pgBackRest.

---

## Document Cross-References
- Global System Blueprint: [00_MasterBlueprint.md](file:///d:/Projects/ContentPilot/docs/00_MasterBlueprint.md)
- Storage Architecture: [19_Storage.md](file:///d:/Projects/ContentPilot/docs/19_Storage.md)
- Infrastructure Deployment: [Deployment.md](file:///d:/Projects/ContentPilot/docs/Deployment.md)
