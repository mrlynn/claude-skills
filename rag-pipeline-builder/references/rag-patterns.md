# Production RAG Patterns

Battle-tested patterns from real RAG deployments: AA Companion, VAI workflows, Developer Day demos, and customer engagements.

## Pattern 1: Incremental Ingestion with Content Hashing

**Problem:** Re-embedding the entire corpus on every update is wasteful.

**Solution:** Hash document content and skip unchanged documents.

```javascript
const crypto = require('crypto');

async function ingestDocument(doc) {
  // Hash content
  const hash = crypto.createHash('sha256').update(doc.text).digest('hex');
  
  // Check if already ingested
  const existing = await db.collection('documents').findOne({ 
    source: doc.id, 
    content_hash: hash 
  });
  
  if (existing) {
    console.log(`Skipping unchanged: ${doc.id}`);
    return;
  }
  
  // Embed only if new or changed
  const embedding = await voyageClient.embed(doc.text);
  
  await db.collection('documents').insertOne({
    text: doc.text,
    embedding,
    source: doc.id,
    content_hash: hash,
    ingested_at: new Date()
  });
}
```

**Result:** 90%+ cost reduction after initial ingestion.

---

## Pattern 2: Category-Based Score Boosting

**Problem:** Not all search results are equally useful. UI docs are more helpful than API reference for chat.

**Solution:** Boost scores by document category.

```javascript
function boostResults(results, boostConfig) {
  return results.map(r => ({
    ...r,
    boosted_score: r.score * (boostConfig[r.category] || 1.0)
  })).sort((a, b) => b.boosted_score - a.boosted_score);
}

// Usage
const boosted = boostResults(results, {
  'ui-docs': 1.5,
  'tutorials': 1.3,
  'api-reference': 1.0,
  'examples': 1.2
});
```

**Example from MongoHacks platform:** UI docs boosted 1.5x over API docs in RAG chat, resulting in 40% better user satisfaction.

---

## Pattern 3: Fire-and-Forget Usage Logging

**Problem:** Logging slows down responses and can fail, blocking the user.

**Solution:** Log asynchronously without awaiting.

```javascript
async function handleQuery(req, res) {
  const { query } = req.body;
  
  const results = await vectorSearch(query);
  const response = await generate(query, results);
  
  // Fire and forget - don't await
  logUsage({ query, results, response })
    .catch(err => console.error('Usage logging failed:', err));
  
  // Return immediately
  res.json({ response });
}
```

**Benefit:** Zero impact on response latency. If logging fails, user still gets their answer.

---

## Pattern 4: Batch Embedding for Speed

**Problem:** Embedding documents one-by-one is slow.

**Solution:** Batch into groups of 128 (Voyage's recommended batch size).

```javascript
async function batchEmbed(documents, batchSize = 128) {
  const embeddings = [];
  
  for (let i = 0; i < documents.length; i += batchSize) {
    const batch = documents.slice(i, i + batchSize);
    const batchEmbeddings = await voyageClient.embedBatch(
      batch.map(d => d.text)
    );
    embeddings.push(...batchEmbeddings);
    
    // Rate limiting: pause between batches
    if (i + batchSize < documents.length) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }
  
  return embeddings;
}
```

**Result:** 10x faster ingestion than one-at-a-time.

---

## Pattern 5: Hybrid Search (Vector + Keyword)

**Problem:** Vector search misses exact matches (e.g., product IDs, error codes).

**Solution:** Combine vector search with text search, merge results.

```javascript
async function hybridSearch(query, limit = 10) {
  // Run both searches in parallel
  const [vectorResults, textResults] = await Promise.all([
    vectorSearch(query, limit),
    textSearch(query, limit)
  ]);
  
  // Merge and deduplicate
  const merged = new Map();
  
  for (const result of vectorResults) {
    merged.set(result.id, { ...result, vector_score: result.score });
  }
  
  for (const result of textResults) {
    if (merged.has(result.id)) {
      merged.get(result.id).text_score = result.score;
    } else {
      merged.set(result.id, { ...result, text_score: result.score });
    }
  }
  
  // Combined score: 70% vector, 30% text
  return Array.from(merged.values())
    .map(r => ({
      ...r,
      combined_score: (r.vector_score || 0) * 0.7 + (r.text_score || 0) * 0.3
    }))
    .sort((a, b) => b.combined_score - a.combined_score)
    .slice(0, limit);
}
```

**Use case:** Technical documentation where users search for exact error codes but also semantic concepts.

---

## Pattern 6: Context Assembly with Source Citations

**Problem:** LLMs hallucinate when context is unclear.

**Solution:** Assemble context with clear source attribution.

```javascript
function assembleContext(results) {
  const context = results.map((r, i) => 
    `[Source ${i+1}: ${r.source}]\n${r.text}`
  ).join('\n\n---\n\n');
  
  return context;
}

// Then in prompt:
const prompt = `
Answer the question using ONLY the context below. Cite sources using [Source N].

Context:
${assembleContext(results)}

Question: ${query}
Answer:
`;
```

**Benefit:** Users can verify answers, and hallucinations are easier to spot.

---

## Pattern 7: Query Rewriting for Better Retrieval

**Problem:** User queries are often ambiguous or poorly phrased.

**Solution:** Rewrite the query before embedding.

```javascript
async function rewriteQuery(userQuery) {
  const prompt = `
Rewrite this user query to be more specific and search-friendly.
Remove filler words, expand acronyms, and clarify intent.

User query: "${userQuery}"
Rewritten query:`;

  const rewritten = await llm.generate(prompt, { max_tokens: 50 });
  
  console.log(`Original: ${userQuery}`);
  console.log(`Rewritten: ${rewritten}`);
  
  return rewritten;
}

// Usage
const rewrittenQuery = await rewriteQuery(userQuery);
const results = await vectorSearch(rewrittenQuery);
```

**Example:**
- User: "how do i make it faster"
- Rewritten: "how to optimize MongoDB query performance"
- Better retrieval ✓

---

## Pattern 8: Metadata Filtering

**Problem:** Retrieving from the entire corpus is inefficient when user specifies a subset.

**Solution:** Use Atlas Vector Search filters.

```javascript
const results = await db.collection('documents').aggregate([
  {
    $vectorSearch: {
      index: 'vector_index',
      path: 'embedding',
      queryVector: embedding,
      numCandidates: 100,
      limit: 10,
      filter: {
        category: 'ui-docs',        // Only UI docs
        version: { $gte: '7.0' }    // Version 7.0+
      }
    }
  }
]);
```

**Use case:** "Show me examples from the Python driver" → filter to language: 'python'

---

## Pattern 9: Feedback Loop for Continuous Improvement

**Problem:** You don't know if retrieval quality is degrading.

**Solution:** Track thumbs-up/down, log failed retrievals.

```javascript
// User rates response
await db.collection('feedback').insertOne({
  query,
  results: results.map(r => r.id),
  response,
  rating: 'thumbs_up', // or 'thumbs_down'
  timestamp: new Date()
});

// Weekly review
const badResults = await db.collection('feedback').find({
  rating: 'thumbs_down',
  timestamp: { $gte: lastWeek }
}).toArray();

// Identify gaps in your corpus
```

---

## Pattern 10: Graceful Degradation

**Problem:** Voyage API outage breaks your app.

**Solution:** Fall back to keyword search or cached responses.

```javascript
async function robustSearch(query) {
  try {
    const embedding = await voyageClient.embed(query, { timeout: 2000 });
    return await vectorSearch(embedding);
  } catch (err) {
    console.warn('Vector search failed, falling back to text search', err);
    return await textSearch(query);
  }
}
```

**Benefit:** Degraded experience > broken experience.

---

## Cost Optimization Patterns

### Pattern 11: Lazy Embedding (Embed on First Query)

For user-generated content with unknown demand:

```javascript
async function getOrCreateEmbedding(doc) {
  if (doc.embedding) return doc.embedding;
  
  // First time this doc is queried
  const embedding = await voyageClient.embed(doc.text);
  
  await db.collection('documents').updateOne(
    { _id: doc._id },
    { $set: { embedding, embedded_at: new Date() } }
  );
  
  return embedding;
}
```

**Use case:** User-uploaded documents where 80% are never searched.

### Pattern 12: TTL for Old Embeddings

If your corpus changes frequently, expire old embeddings:

```javascript
// MongoDB TTL index
db.collection('documents').createIndex(
  { embedded_at: 1 },
  { expireAfterSeconds: 30 * 24 * 60 * 60 } // 30 days
);
```

**Benefit:** Auto-cleanup prevents stale results and saves storage costs.

---

## Quality Metrics

Track these to measure RAG performance:

| Metric | Formula | Target |
|--------|---------|--------|
| **MRR** | 1 / rank of first relevant result | > 0.7 |
| **Precision@5** | Relevant results in top 5 / 5 | > 0.6 |
| **Recall@10** | Relevant results found / total relevant | > 0.8 |
| **Latency (p95)** | 95th percentile query time | < 500ms |
| **Thumbs-up rate** | Positive feedback / total feedback | > 70% |

---

## Deployment Checklist

Before going to production:

- [ ] Incremental ingestion implemented (content hashing)
- [ ] Category-based score boosting configured
- [ ] Usage logging is fire-and-forget
- [ ] Batch embedding for ingestion
- [ ] Metadata filters for scoped search
- [ ] Feedback collection in place
- [ ] Graceful degradation on API failures
- [ ] Monitoring for MRR, Precision@5, latency
- [ ] Cost alerts configured (embeddings + storage)
- [ ] Documentation for future maintainers

---

## References

- MongoDB Atlas Vector Search: https://mongodb.com/docs/atlas/atlas-vector-search/
- Voyage AI Batching: https://docs.voyage.ai/embeddings/
- RAG Quality Metrics: https://arxiv.org/abs/2404.10198
