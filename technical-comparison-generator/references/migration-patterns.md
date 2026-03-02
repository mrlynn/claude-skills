# Migration Patterns

## PostgreSQL → MongoDB

**Common triggers:**
- Need horizontal scaling
- Schema too rigid
- Adding real-time features

**Process:**
1. Map tables → collections
2. Denormalize joins
3. Migrate data (mongoimport)
4. Rewrite queries (SQL → MQL)

**Example:**
```sql
-- SQL
SELECT * FROM users WHERE age > 25;
```
```javascript
// MQL
db.users.find({ age: { $gt: 25 } });
```

## MongoDB → PostgreSQL

**Common triggers:**
- Need complex joins
- Strict schema required
- SQL tooling preference

**Process:**
1. Flatten documents → tables
2. Create foreign keys
3. Define schema (DDL)
4. Migrate data (mongoexport + ETL)

## DynamoDB → MongoDB

**Common triggers:**
- Richer query language needed
- Avoid vendor lock-in

**Process:**
1. Key-value → document model
2. Add indexes for queries
3. Use MongoDB Atlas (managed)
