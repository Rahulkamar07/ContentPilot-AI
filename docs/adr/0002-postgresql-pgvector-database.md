# ADR-0002: PostgreSQL 16 with pgvector Extension for Data Persistence

## Context & Problem Statement
The platform requires a reliable relational database for multi-tenant accounts, RBAC, workspaces, social credentials, and post queue metadata. Additionally, news deduplication requires fast vector similarity search (1536-dimensional OpenAI embeddings) to detect duplicate articles across distinct RSS feeds.

## Decision Drivers
- Strong ACID compliance for workspace metadata and financial billing tiers.
- Ability to perform vector similarity search (cosine distance, HNSW indexes) without adding a separate vector database (e.g., Pinecone, Qdrant).
- Rich JSONB query support for OAuth token storage and dynamic analytics payloads.
- Declarative monthly range partitioning.

## Considered Options
1. **PostgreSQL 16 + pgvector**
2. **PostgreSQL + External Vector DB (Pinecone / Qdrant)**
3. **MongoDB + Atlas Vector Search**

## Decision Outcome
**Chosen Option**: **PostgreSQL 16 + pgvector**.
`pgvector` allows storing relational metadata and vector embeddings within the same database engine, eliminating dual-write sync issues and simplifying Docker / Cloud infrastructure operations.

### Positive Consequences
- Single source of truth for all application data.
- Standard SQL queries combining relational joins and vector similarity (`ORDER BY embedding <=> query_vector LIMIT 5`).
- Substantial infrastructure cost reduction.

### Negative Consequences
- Extremely large embedding datasets (100M+ vectors) may require upgrading to dedicated vector search clusters in Phase 3.
