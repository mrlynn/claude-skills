---
name: document-model-advisor
description: MongoDB schema design advisor focusing on embed vs reference decisions, relationship modeling, and performance optimization patterns
license: MIT
metadata:
  version: 1.0.0
  author: MongoDB Developer Relations
  category: database-design
  domain: data-modeling
  updated: 2026-03-01
  python-tools: relationship_analyzer.py, schema_optimizer.py, migration_planner.py
  tech-stack: mongodb, json-schema, python
---

# document-model-advisor

## Trigger

Use this skill when designing MongoDB schemas, migrating from relational databases, or optimizing existing document structures.

**Trigger phrases:**
- "Should I embed or reference?"
- "Design MongoDB schema for [domain]"
- "Migrate SQL schema to MongoDB"
- "Optimize MongoDB schema"
- "Model [relationship] in MongoDB"

## Overview

The most common MongoDB question: **"Should I embed or reference?"** This skill analyzes your data relationships and provides concrete recommendations based on access patterns, data size, update frequency, and consistency requirements.

**Not for:** Generating boilerplate code. This is about **design decisions**, not code generation.

## How to Use

### Quick Start
1. **Analyze relationships:**
   ```bash
   python scripts/relationship_analyzer.py entities.json --output analysis.json
   ```

2. **Get schema recommendations:**
   ```bash
   python scripts/schema_optimizer.py analysis.json --output schema.json
   ```

3. **Plan migration (if from SQL):**
   ```bash
   python scripts/migration_planner.py sql-schema.sql --output migration-plan.json
   ```

### Python Tools
- `scripts/relationship_analyzer.py` — Analyze entity relationships and access patterns
- `scripts/schema_optimizer.py` — Recommend embed vs reference strategies
- `scripts/migration_planner.py` — Plan SQL → MongoDB schema migration

### Reference Docs
- `references/embed-vs-reference-guide.md` — The classic MongoDB design question
- `references/schema-patterns.md` — Proven MongoDB schema patterns

### Templates & Assets
- `assets/entity-definition-template.json` — Define entities and relationships
- `assets/schema-examples.json` — Sample schemas for common domains

## Architecture Decisions

### The Embed vs Reference Decision Tree

```
Is the data always accessed together?
├─ YES → Consider embedding
│   ├─ Is the embedded data unbounded?
│   │   ├─ YES → Reference instead (16MB doc limit)
│   │   └─ NO → Embed
│   └─ Is the embedded data updated frequently?
│       ├─ YES → Reference (avoid large doc rewrites)
│       └─ NO → Embed
└─ NO → Consider referencing
    ├─ Is the data used in multiple contexts?
    │   ├─ YES → Reference (avoid duplication)
    │   └─ NO → Could embed
    └─ Do you need atomic updates across entities?
        ├─ YES → Embed (single doc transactions are atomic)
        └─ NO → Reference is fine
```

### The 6 Factors

**1. Access Patterns** (most important)
- Read together → Embed
- Read separately → Reference

**2. Data Size**
- Small, bounded → Embed
- Large or unbounded → Reference

**3. Update Frequency**
- Rarely updated → Embed
- Frequently updated → Reference

**4. Data Lifecycle**
- Same lifecycle → Embed
- Independent lifecycle → Reference

**5. Consistency Requirements**
- Need atomicity → Embed
- Eventual consistency OK → Reference

**6. Duplication Tolerance**
- OK with duplication → Can embed
- Must avoid duplication → Reference

### Classic Examples

#### One-to-Few (Embed)
**Example:** User addresses (1-3 addresses per user)
```json
{
  "_id": "user123",
  "name": "John Doe",
  "addresses": [
    { "type": "home", "street": "123 Main St", "city": "NYC" },
    { "type": "work", "street": "456 Park Ave", "city": "NYC" }
  ]
}
```

**Why embed:** Few addresses, always accessed with user, same lifecycle.

#### One-to-Many (Reference)
**Example:** Blog posts and comments (potentially thousands of comments)
```json
// Post
{ "_id": "post123", "title": "...", "author": "user123" }

// Comments (separate collection)
{ "_id": "comment1", "postId": "post123", "text": "...", "author": "user456" }
{ "_id": "comment2", "postId": "post123", "text": "...", "author": "user789" }
```

**Why reference:** Unbounded comments, separate access patterns, independent updates.

#### Many-to-Many (Reference Both Sides)
**Example:** Students and courses
```json
// Student
{ "_id": "student123", "name": "Alice", "courseIds": ["course1", "course2"] }

// Course
{ "_id": "course1", "name": "MongoDB 101", "studentIds": ["student123", "student456"] }
```

**Why reference:** Many-to-many, independent lifecycles, queried from both directions.

### Anti-Patterns to Avoid

**❌ Unbounded Arrays**
```json
{
  "_id": "post123",
  "comments": [/* thousands of comments */]  // Will hit 16MB limit
}
```

**❌ Massive Duplication**
```json
// Duplicating full user object in every post
{
  "_id": "post123",
  "author": {
    "id": "user123",
    "name": "John",
    "email": "john@example.com",
    "bio": "...",  // Duplicated everywhere
    "preferences": {...}
  }
}
```

**❌ Deep Nesting**
```json
{
  "order": {
    "customer": {
      "address": {
        "country": {
          "region": {
            "subregion": {...}  // Too deep
          }
        }
      }
    }
  }
}
```

### Hybrid Patterns

#### Extended Reference
Reference with denormalized frequently-accessed fields:
```json
{
  "_id": "post123",
  "authorId": "user123",  // Reference
  "authorName": "John Doe",  // Denormalized for display
  "authorAvatar": "https://..."  // Denormalized for display
}
```

**Use when:** Need reference for main data, but want to avoid lookup for display.

#### Subset Pattern
Embed a subset, reference for full data:
```json
{
  "_id": "product123",
  "reviews": [
    { "rating": 5, "text": "Great!", "author": "Alice" },  // Recent 10
    { "rating": 4, "text": "Good", "author": "Bob" }
  ],
  "totalReviews": 1547  // Total count, full reviews in separate collection
}
```

**Use when:** Want preview data embedded, full data on demand.

#### Bucketing Pattern
Group unbounded data into buckets:
```json
// Time-series data bucketed by hour
{
  "_id": "sensor123_2024-03-01-14",
  "sensorId": "sensor123",
  "hour": "2024-03-01T14:00:00Z",
  "readings": [
    { "time": "14:00:00", "value": 72.3 },
    { "time": "14:01:00", "value": 72.5 },
    // ... up to 60 readings
  ]
}
```

**Use when:** Unbounded time-series or event data.

## Python Tool Details

### 1. Relationship Analyzer

**Purpose:** Analyze entity relationships and recommend embed vs reference.

**Input:** Entity definitions
```json
{
  "entities": [
    {
      "name": "User",
      "fields": ["id", "name", "email"],
      "relationships": [
        {
          "to": "Post",
          "type": "one-to-many",
          "accessPattern": "separate",
          "typical_count": "unbounded"
        }
      ]
    },
    {
      "name": "Post",
      "fields": ["id", "title", "content"],
      "relationships": [
        {
          "to": "User",
          "type": "many-to-one",
          "accessPattern": "together",
          "typical_count": 1
        }
      ]
    }
  ]
}
```

**Usage:**
```bash
python scripts/relationship_analyzer.py entities.json --output analysis.json
```

**Output:**
```json
{
  "recommendations": [
    {
      "relationship": "User → Post",
      "decision": "reference",
      "reasoning": [
        "Unbounded (typical_count: unbounded)",
        "Separate access pattern",
        "Independent lifecycle"
      ],
      "confidence": 0.95
    },
    {
      "relationship": "Post → User",
      "decision": "reference_with_denormalization",
      "reasoning": [
        "Always accessed together",
        "Small, bounded (1 user per post)",
        "Recommend: Store userId + authorName for display"
      ],
      "confidence": 0.85
    }
  ]
}
```

### 2. Schema Optimizer

**Purpose:** Generate optimized MongoDB schema from analysis.

**Usage:**
```bash
python scripts/schema_optimizer.py analysis.json --output schema.json
```

**Output:**
```json
{
  "collections": [
    {
      "name": "users",
      "schema": {
        "_id": "ObjectId",
        "name": "string",
        "email": "string"
      },
      "indexes": [
        { "fields": ["email"], "unique": true }
      ]
    },
    {
      "name": "posts",
      "schema": {
        "_id": "ObjectId",
        "title": "string",
        "content": "string",
        "authorId": "ObjectId",  // Reference
        "authorName": "string"  // Denormalized
      },
      "indexes": [
        { "fields": ["authorId"] }
      ]
    }
  ],
  "denormalization_rules": [
    {
      "from": "users.name",
      "to": "posts.authorName",
      "sync_strategy": "on_write",
      "note": "Update posts when user.name changes"
    }
  ]
}
```

### 3. Migration Planner

**Purpose:** Plan SQL → MongoDB schema migration.

**Input:** SQL schema
```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE
);

CREATE TABLE posts (
  id INT PRIMARY KEY,
  title VARCHAR(200),
  content TEXT,
  user_id INT REFERENCES users(id)
);
```

**Usage:**
```bash
python scripts/migration_planner.py schema.sql --output migration-plan.json
```

**Output:**
```json
{
  "tables_to_collections": {
    "users": "users",
    "posts": "posts"
  },
  "relationship_mappings": [
    {
      "sql_fk": "posts.user_id → users.id",
      "mongodb_approach": "reference",
      "field": "posts.userId",
      "reasoning": "One-to-many, typical SQL pattern maps to reference"
    }
  ],
  "migration_steps": [
    "1. Export users table to JSON",
    "2. Import to users collection",
    "3. Export posts table to JSON",
    "4. Transform posts.user_id → posts.userId",
    "5. Import to posts collection",
    "6. Create index on posts.userId"
  ],
  "considerations": [
    "Original SQL join: SELECT posts.*, users.name FROM posts JOIN users",
    "MongoDB equivalent: Aggregation with $lookup or denormalize users.name into posts"
  ]
}
```

## Common Patterns

### Pattern 1: User Profiles
```json
{
  "_id": "user123",
  "name": "John Doe",
  "email": "john@example.com",
  "profile": {  // Embed (always accessed together)
    "bio": "...",
    "avatar": "...",
    "preferences": {...}
  },
  "addresses": [  // Embed (few, bounded)
    { "type": "home", "street": "..." }
  ]
}
```

### Pattern 2: E-commerce Orders
```json
{
  "_id": "order123",
  "customerId": "user123",  // Reference
  "customerName": "John Doe",  // Denormalized
  "items": [  // Embed (part of order)
    {
      "productId": "prod456",  // Reference
      "productName": "Widget",  // Denormalized
      "quantity": 2,
      "price": 29.99
    }
  ],
  "total": 59.98,
  "status": "shipped"
}
```

**Why:** Order items are embedded (part of order), but product/customer are referenced (independent entities).

### Pattern 3: Blog Platform
```json
// Post document
{
  "_id": "post123",
  "title": "MongoDB Schema Design",
  "content": "...",
  "authorId": "user123",  // Reference
  "authorName": "John Doe",  // Denormalized
  "tags": ["mongodb", "schema"],  // Embed (small, bounded)
  "commentCount": 47,  // Derived field
  "recentComments": [  // Embed subset
    { "author": "Alice", "text": "Great post!" }
  ]
}

// Comments collection (separate)
{
  "_id": "comment1",
  "postId": "post123",
  "author": "Alice",
  "text": "Great post!",
  "createdAt": ISODate("...")
}
```

## Decision Framework

### When to Embed

✅ **Embed when:**
- Data is always accessed together
- 1:few relationships (not unbounded)
- Data rarely updated independently
- Need atomic updates
- OK with some duplication

**Examples:**
- User addresses
- Product specifications
- Order line items
- Document metadata

### When to Reference

✅ **Reference when:**
- Data accessed separately
- 1:many or many:many relationships
- Unbounded arrays
- Data updated frequently
- Shared across entities
- Need to avoid duplication

**Examples:**
- Blog posts → comments
- Users → orders
- Products → reviews (if many)
- Students ↔ courses

### When to Denormalize

✅ **Denormalize when:**
- Need to avoid joins for display
- Read-heavy, write-light
- Can tolerate eventual consistency
- Trade storage for performance

**Pattern:** Reference + denormalized fields
```json
{
  "postId": "post123",
  "authorId": "user123",  // Reference
  "authorName": "John",  // Denormalized
  "authorAvatar": "..."  // Denormalized
}
```

## Migration Strategies

### From SQL

**1. Identify relationships:**
- Foreign keys → References (usually)
- Lookup tables → Arrays or references
- 1:1 relationships → Embed (usually)

**2. Consider access patterns:**
- SQL joins → Might embed in MongoDB
- Separate queries → Keep as references

**3. Denormalize strategically:**
- Frequently joined fields → Denormalize
- Less frequently → Keep normalized

### Example: Blog Migration

**SQL Schema:**
```sql
users (id, name, email)
posts (id, title, content, user_id)
comments (id, post_id, user_id, text)
tags (id, name)
post_tags (post_id, tag_id)
```

**MongoDB Schema:**
```json
// users collection
{ "_id": ObjectId, "name": "...", "email": "..." }

// posts collection
{
  "_id": ObjectId,
  "title": "...",
  "content": "...",
  "authorId": ObjectId,  // Reference to users
  "authorName": "...",  // Denormalized
  "tags": ["mongodb", "schema"],  // Embedded (from post_tags join table)
  "commentCount": 47
}

// comments collection
{
  "_id": ObjectId,
  "postId": ObjectId,
  "authorId": ObjectId,
  "authorName": "...",  // Denormalized
  "text": "..."
}
```

## Performance Considerations

### Embed for Performance
- **Faster reads:** One query instead of joins
- **Atomic updates:** Single document transaction
- **Locality:** Related data stored together

### Reference for Scalability
- **Smaller documents:** Faster updates
- **Avoid 16MB limit:** Large or unbounded data
- **Flexibility:** Independent scaling

### Indexes Matter

**Embedded:**
```json
{ "user.addresses.city": 1 }  // Can index embedded fields
```

**Referenced:**
```json
{ "userId": 1 }  // Need index on foreign key
```

## Quality Checklist

Before finalizing schema:
- [ ] Access patterns identified
- [ ] Embed/reference decisions documented
- [ ] Unbounded arrays avoided
- [ ] Denormalization strategy clear
- [ ] Indexes planned
- [ ] 16MB document limit considered
- [ ] Update patterns analyzed
- [ ] Consistency requirements defined

## When to Use vs. Other Tools

| Use `document-model-advisor` | Use other tools |
|------------------------------|-----------------|
| Schema design decisions | Code generation |
| Embed vs reference questions | ORM setup |
| SQL → MongoDB migration planning | Query optimization |
| Relationship modeling | Index tuning |

## References

- MongoDB Data Modeling: `references/embed-vs-reference-guide.md`
- Schema Patterns: `references/schema-patterns.md`
- Official docs: https://docs.mongodb.com/manual/core/data-modeling-introduction/
- Schema design patterns: https://www.mongodb.com/blog/post/building-with-patterns-a-summary

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)

---

**Next steps after schema design:**
1. Validate with sample data
2. Test access patterns
3. Plan indexes
4. Implement with schema validation
5. Monitor document sizes
