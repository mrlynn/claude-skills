---
name: technical-comparison-generator
description: Generate fair, accurate technical comparisons between MongoDB and competitors with feature matrices, use case fit analysis, and migration considerations
license: MIT
metadata:
  version: 1.0.0
  author: MongoDB Developer Relations
  category: competitive-analysis
  domain: technical-comparison
  updated: 2026-03-01
  python-tools: feature_analyzer.py, comparison_generator.py, use_case_matcher.py
  tech-stack: python, markdown
---

# technical-comparison-generator

## Trigger

Use this skill when creating competitive comparisons, responding to "MongoDB vs X" questions, or analyzing database fit for use cases.

**Trigger phrases:**
- "MongoDB vs PostgreSQL"
- "Compare MongoDB to [competitor]"
- "When to use MongoDB vs [competitor]"
- "Generate comparison matrix"
- "Database selection criteria"

## Overview

Technical comparisons should be **fair, accurate, and helpful** - not marketing fluff. This skill generates comparisons that:
- Acknowledge competitor strengths
- Highlight MongoDB strengths honestly
- Focus on use case fit (not "better/worse")
- Include migration considerations

**Not for:** Biased marketing content. This is about **helping developers choose the right tool**.

## How to Use

### Quick Start

1. **Analyze features:**
   ```bash
   python scripts/feature_analyzer.py --competitor postgres --output features.json
   ```

2. **Generate comparison:**
   ```bash
   python scripts/comparison_generator.py features.json --output comparison.md
   ```

3. **Match use cases:**
   ```bash
   python scripts/use_case_matcher.py --use-case "real-time analytics" --output fit.md
   ```

### Python Tools
- `scripts/feature_analyzer.py` — Compare feature sets
- `scripts/comparison_generator.py` — Generate comparison matrix
- `scripts/use_case_matcher.py` — Analyze use case fit

### Reference Docs
- `references/comparison-framework.md` — How to write fair comparisons
- `references/migration-patterns.md` — Common migration paths

### Templates & Assets
- `assets/feature-matrix-template.md` — Comparison table structure
- `assets/use-case-template.md` — Use case analysis format

## Comparison Framework

### Principle 1: Be Fair

**Don't:**
- Cherry-pick features
- Use outdated competitor info
- Exaggerate weaknesses
- Ignore competitor strengths

**Do:**
- Acknowledge what they do well
- Use current versions
- Focus on factual differences
- Cite sources

### Principle 2: Focus on Use Case Fit

**Not:** "MongoDB is better"
**Instead:** "MongoDB fits better for [use case] because [specific reasons]"

### Principle 3: Be Specific

**Vague:** "MongoDB is more scalable"
**Specific:** "MongoDB horizontal scaling via sharding handles 100k+ writes/sec across commodity hardware. PostgreSQL vertical scaling requires expensive hardware upgrades."

## Common Comparisons

### MongoDB vs PostgreSQL

**PostgreSQL strengths:**
- ✅ ACID transactions (long history)
- ✅ Complex joins (relational queries)
- ✅ Mature tooling ecosystem
- ✅ Strong SQL compliance
- ✅ Extensions (PostGIS, etc.)

**MongoDB strengths:**
- ✅ Horizontal scaling (sharding built-in)
- ✅ Flexible schema (rapid iteration)
- ✅ Document model (maps to objects)
- ✅ Vector Search (AI/ML integration)
- ✅ Time Series (native optimization)

**Use case fit:**
- **PostgreSQL:** Traditional OLTP, complex joins, strict schema
- **MongoDB:** Rapid development, scale-out, hierarchical data, AI/ML

**Migration considerations:**
- PostgreSQL → MongoDB: Map tables to collections, denormalize joins
- MongoDB → PostgreSQL: Flatten documents, create relational schema

### MongoDB vs DynamoDB

**DynamoDB strengths:**
- ✅ Fully managed (no ops)
- ✅ AWS integration
- ✅ Predictable pricing (on-demand)
- ✅ Global tables (multi-region)

**MongoDB strengths:**
- ✅ Rich query language (vs key-value)
- ✅ Aggregation framework
- ✅ Transactions (multi-document)
- ✅ Flexible indexes
- ✅ No vendor lock-in (portable)

**Use case fit:**
- **DynamoDB:** Simple key-value, AWS-only, predictable traffic
- **MongoDB:** Complex queries, aggregations, multi-cloud, flexible data

### MongoDB vs Cassandra

**Cassandra strengths:**
- ✅ Write-optimized (high throughput)
- ✅ Multi-datacenter replication
- ✅ Tunable consistency
- ✅ Linear scalability

**MongoDB strengths:**
- ✅ Easier operations (vs Cassandra complexity)
- ✅ Rich queries (vs CQL limitations)
- ✅ Transactions (vs eventual consistency)
- ✅ Change streams (real-time)

**Use case fit:**
- **Cassandra:** Write-heavy time series, multi-DC replication
- **MongoDB:** Balanced read/write, complex queries, operational simplicity

### MongoDB vs Elasticsearch

**Elasticsearch strengths:**
- ✅ Full-text search (best-in-class)
- ✅ Search analytics (Kibana)
- ✅ Log aggregation
- ✅ Search relevance tuning

**MongoDB strengths:**
- ✅ General-purpose database (not just search)
- ✅ Transactions (vs search index)
- ✅ Atlas Search (integrated search)
- ✅ Simpler architecture (one database)

**Use case fit:**
- **Elasticsearch:** Search-first applications, log analytics
- **MongoDB:** App database + search, unified data platform

### MongoDB vs Redis

**Redis strengths:**
- ✅ In-memory speed (microsecond latency)
- ✅ Caching (LRU eviction)
- ✅ Pub/sub messaging
- ✅ Simple data structures

**MongoDB strengths:**
- ✅ Persistent storage (vs in-memory)
- ✅ Complex queries (vs key-value)
- ✅ Rich data types
- ✅ Larger datasets (disk-backed)

**Use case fit:**
- **Redis:** Caching, session store, real-time leaderboards
- **MongoDB:** Primary database, complex queries, persistent data

## Feature Matrix Template

| Feature | MongoDB | PostgreSQL | Notes |
|---------|---------|------------|-------|
| **Data Model** | Document | Relational | MongoDB: flexible schema; Postgres: strict schema |
| **Query Language** | MQL | SQL | MongoDB: JSON-like; Postgres: ANSI SQL |
| **Transactions** | Multi-doc | ACID | Both support transactions |
| **Scaling** | Horizontal (sharding) | Vertical | MongoDB: built-in sharding; Postgres: extensions |
| **Joins** | $lookup (limited) | Full SQL joins | Postgres: optimized joins; MongoDB: denormalize |
| **Indexes** | B-tree, text, geo, vector | B-tree, GiST, GIN | MongoDB: more index types |
| **Replication** | Replica sets | Streaming replication | Both support HA |
| **Vector Search** | Native (Atlas) | pgvector extension | MongoDB: integrated; Postgres: extension |

## Use Case Analysis Framework

### Step 1: Identify Requirements

**Data model:**
- Hierarchical/nested? → MongoDB
- Highly relational? → PostgreSQL
- Key-value? → DynamoDB/Redis

**Query patterns:**
- Complex aggregations? → MongoDB
- Complex joins? → PostgreSQL
- Simple lookups? → DynamoDB

**Scale requirements:**
- Horizontal (many nodes)? → MongoDB, Cassandra
- Vertical (big machine)? → PostgreSQL
- Unlimited (serverless)? → DynamoDB

**Consistency:**
- Strong consistency? → PostgreSQL, MongoDB
- Eventual consistency OK? → Cassandra, DynamoDB

### Step 2: Score Fit (0-10)

MongoDB fit for "Real-time analytics on IoT sensor data":
- **Data model:** 9/10 (time series collections, nested sensor readings)
- **Query patterns:** 9/10 (aggregation framework, $group, $bucket)
- **Scale:** 9/10 (sharding handles 100k+ writes/sec)
- **Consistency:** 8/10 (tunable read/write concern)
- **Operations:** 8/10 (Atlas managed service)
- **Total:** 43/50 → **Strong fit**

PostgreSQL fit for same use case:
- **Data model:** 6/10 (can use JSONB, but not optimized for time series)
- **Query patterns:** 7/10 (window functions, but slower on large data)
- **Scale:** 4/10 (vertical scaling only, expensive)
- **Consistency:** 10/10 (full ACID)
- **Operations:** 7/10 (mature tooling)
- **Total:** 34/50 → **Moderate fit**

**Recommendation:** MongoDB for this use case (IoT time series at scale)

## Migration Patterns

### PostgreSQL → MongoDB

**Common reasons:**
- Need horizontal scaling
- Schema too rigid
- Adding real-time features
- Integrating AI/ML (vector search)

**Process:**
1. **Map schema:** Tables → collections, rows → documents
2. **Denormalize joins:** Embed related data
3. **Migrate data:** Use mongoimport or ETL tools
4. **Rewrite queries:** SQL → MQL
5. **Test thoroughly:** Verify data integrity

**Example:**
```sql
-- PostgreSQL
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status = 'completed';
```

```javascript
// MongoDB (denormalized)
db.orders.find(
  { status: 'completed' },
  { userName: 1, total: 1 }
);
```

### MongoDB → PostgreSQL

**Common reasons:**
- Need complex joins
- Strict schema required (compliance)
- Existing PostgreSQL expertise
- BI tool integration (SQL-first)

**Process:**
1. **Flatten documents:** Nested → relational tables
2. **Create foreign keys:** References → joins
3. **Define schema:** JSON → SQL DDL
4. **Migrate data:** Use mongoexport + custom ETL
5. **Rewrite queries:** MQL → SQL

## Python Tool Details

### 1. Feature Analyzer

**Input:** Competitor name

**Output:** Feature comparison
```json
{
  "competitor": "postgres",
  "features": {
    "data_model": {
      "mongodb": "Document (flexible schema)",
      "postgres": "Relational (strict schema)"
    },
    "scaling": {
      "mongodb": "Horizontal (sharding)",
      "postgres": "Vertical (larger machines)"
    },
    "transactions": {
      "mongodb": "Multi-document ACID",
      "postgres": "Full ACID"
    }
  }
}
```

### 2. Comparison Generator

**Input:** Features JSON

**Output:** Markdown comparison matrix

### 3. Use Case Matcher

**Input:** Use case description

**Output:** Database fit analysis with scoring

## Writing Guidelines

### DO:

✅ **Acknowledge competitor strengths**
> "PostgreSQL has excellent support for complex joins and a mature ecosystem of tools."

✅ **Be specific about tradeoffs**
> "MongoDB's flexible schema enables rapid iteration, but requires discipline to avoid data inconsistency."

✅ **Focus on use case fit**
> "For this IoT use case with 100k writes/sec, MongoDB's horizontal scaling via sharding is better suited than PostgreSQL's vertical scaling approach."

✅ **Cite sources**
> "According to the MongoDB 7.0 documentation..."

✅ **Use current versions**
> "As of PostgreSQL 16 and MongoDB 7.0..."

### DON'T:

❌ **Cherry-pick features**
> "MongoDB has more features than PostgreSQL."

❌ **Use outdated info**
> "PostgreSQL doesn't support JSON." (Wrong - has JSONB since 9.4)

❌ **Exaggerate**
> "MongoDB is 10x faster." (Context matters!)

❌ **Ignore context**
> "Always use MongoDB." (Wrong - depends on use case)

## Quality Checklist

Before publishing comparison:
- [ ] Both databases at current versions
- [ ] Competitor strengths acknowledged
- [ ] Specific use case context provided
- [ ] Tradeoffs explained honestly
- [ ] Sources cited
- [ ] No marketing fluff
- [ ] Technical accuracy verified
- [ ] Migration path included (if relevant)

## When to Use vs. Other Tools

| Use `technical-comparison-generator` | Use other tools |
|--------------------------------------|-----------------|
| Competitive comparisons | Marketing copy |
| Database selection guidance | Sales pitch |
| Use case fit analysis | Product documentation |
| Migration planning | Performance benchmarking |

## References

- Comparison Framework: `references/comparison-framework.md`
- Migration Patterns: `references/migration-patterns.md`
- MongoDB docs: https://docs.mongodb.com
- Competitor docs: PostgreSQL, DynamoDB, etc.

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)

---

**Principle:** Help developers choose the **right tool for their use case**, even if it's not MongoDB.
