# Embedding Model Comparison Reference

Comparison of embedding models used in the MongoDB DevRel platform. The platform uses a two-provider strategy: Voyage AI for embeddings (retrieval-optimized) and OpenAI for text generation.

## Voyage AI Models

Voyage AI models are the recommended choice for embeddings in this platform. They produce higher-quality embeddings for retrieval tasks and support separate document/query input types.

### voyage-4-large

| Property           | Value                              |
|--------------------|------------------------------------|
| **Dimensions**     | 1024                               |
| **Max Tokens**     | 32,000                             |
| **Pricing**        | $0.12 per million tokens           |
| **Input Types**    | `document` and `query` (separate)  |
| **Best For**       | Production RAG, high-quality retrieval, document ingestion |

The default model for all document embeddings in the platform. Provides the highest retrieval quality among Voyage models. Used for both document ingestion (`input_type: "document"`) and query embedding (`input_type: "query"`).

### voyage-4

| Property           | Value                              |
|--------------------|------------------------------------|
| **Dimensions**     | 1024                               |
| **Max Tokens**     | 32,000                             |
| **Pricing**        | $0.10 per million tokens           |
| **Input Types**    | `document` and `query` (separate)  |
| **Best For**       | Cost-sensitive production, general retrieval |

Slightly lower quality than voyage-4-large but 17% cheaper. Same embedding space -- you can embed documents with voyage-4-large and queries with voyage-4 (or vice versa) without re-indexing. Good for high-volume query workloads where cost matters more than marginal quality.

### voyage-4-lite

| Property           | Value                              |
|--------------------|------------------------------------|
| **Dimensions**     | 1024                               |
| **Max Tokens**     | 32,000                             |
| **Pricing**        | $0.05 per million tokens           |
| **Input Types**    | `document` and `query` (separate)  |
| **Best For**       | Development, testing, high-volume low-stakes retrieval |

The most cost-effective Voyage model. 58% cheaper than voyage-4-large. Same 1024-dimension embedding space, so it is interchangeable with the other Voyage models. Quality is lower but adequate for many use cases.

### Voyage AI Key Feature: Document vs Query Input Types

Voyage AI models produce different embeddings depending on the `input_type` parameter:

- **`document`**: Used when embedding content for storage. Optimized for being found.
- **`query`**: Used when embedding a search query. Optimized for finding relevant documents.

Using the correct input type improves retrieval quality by 5-15% compared to using the same type for both. This is a key differentiator from OpenAI models, which do not have this distinction.

```typescript
// Ingestion: use "document"
await callVoyageAPI(chunks, "document", "voyage-4-large");

// Search: use "query"
await callVoyageAPI([userQuery], "query", "voyage-4-large");
```

### Voyage Model Interchangeability

All three Voyage models (voyage-4-large, voyage-4, voyage-4-lite) produce embeddings in the same 1024-dimensional space. This means:

- You can embed documents with voyage-4-large and search with voyage-4-lite
- You do NOT need to re-index when switching between Voyage models
- This enables a cost optimization strategy: use the best model for ingestion (one-time cost) and a cheaper model for queries (recurring cost)

---

## OpenAI Models

OpenAI embedding models are available as alternatives. The platform uses OpenAI primarily for text generation, not embeddings, but these models can serve as fallbacks.

### text-embedding-3-small

| Property           | Value                              |
|--------------------|------------------------------------|
| **Dimensions**     | 1536 (default), configurable down to 256 |
| **Max Tokens**     | 8,191                              |
| **Pricing**        | $0.02 per million tokens           |
| **Input Types**    | Single (no document/query distinction) |
| **Best For**       | Cost-sensitive applications, classification, clustering |

The cheapest embedding model available. Supports Matryoshka dimensionality reduction -- you can request fewer dimensions (256, 512, 1024) for smaller storage with modest quality loss. No document/query input type distinction.

### text-embedding-3-large

| Property           | Value                              |
|--------------------|------------------------------------|
| **Dimensions**     | 3072 (default), configurable down to 256 |
| **Max Tokens**     | 8,191                              |
| **Pricing**        | $0.13 per million tokens           |
| **Input Types**    | Single (no document/query distinction) |
| **Best For**       | Maximum embedding quality from OpenAI, multilingual |

OpenAI's most capable embedding model. Higher dimensions (3072) mean larger storage requirements and slightly slower vector search. Supports Matryoshka reduction. No document/query distinction.

---

## Comparison Table

| Model                      | Dims  | $/M tokens | Doc/Query Types | Max Tokens | Relative Quality |
|---------------------------|-------|-----------|:---------------:|-----------|:----------------:|
| **voyage-4-large**         | 1024  | $0.12     |       Yes       | 32,000    |     Highest      |
| **voyage-4**               | 1024  | $0.10     |       Yes       | 32,000    |      High        |
| **voyage-4-lite**          | 1024  | $0.05     |       Yes       | 32,000    |      Good        |
| text-embedding-3-large     | 3072  | $0.13     |       No        | 8,191     |      High        |
| text-embedding-3-small     | 1536  | $0.02     |       No        | 8,191     |     Medium       |

## When to Use Which

### Use voyage-4-large (default recommendation)

- Production RAG pipelines with Atlas Vector Search
- Document ingestion where retrieval quality matters
- When the 1024-dimension space is preferred for index size
- When you need the document/query input type optimization

### Use voyage-4

- Same use cases as voyage-4-large but with tighter budget
- High-volume query embedding (saves 17% on query costs)
- Can mix with voyage-4-large documents (same embedding space)

### Use voyage-4-lite

- Development and testing environments
- Prototype RAG pipelines
- Very high-volume, low-stakes retrieval
- When cost is the primary concern

### Use text-embedding-3-small

- When you only need OpenAI and do not want a second provider
- Classification or clustering tasks (not retrieval)
- Extremely budget-constrained scenarios ($0.02/M vs $0.12/M)

### Use text-embedding-3-large

- When maximum OpenAI quality is required
- Multilingual applications (OpenAI has broader language support)
- When you need more than 1024 dimensions for fine-grained similarity

## Platform Defaults

The platform is configured to use:

- **Document embedding**: `voyage-4-large` with `input_type: "document"`
- **Query embedding**: `voyage-4-large` with `input_type: "query"` (can be swapped to voyage-4 or voyage-4-lite)
- **Vector search index**: 1024 dimensions, cosine similarity
- **Text generation**: OpenAI GPT-4-turbo for structured outputs, GPT-4o for chat

## Cost Estimation

The AI usage logger tracks costs using these rates per million tokens:

```typescript
const MODEL_COST_PER_MILLION: Record<string, number> = {
  "gpt-4o": 7.5,
  "gpt-4-turbo": 20,
  "text-embedding-3-small": 0.02,
  "voyage-4-large": 0.12,
  "voyage-4": 0.1,
  "voyage-4-lite": 0.05,
};
```

### Example: Ingesting 1,000 Documents

Assuming average 500 tokens per chunk, 5 chunks per document:
- Total tokens: 2,500,000
- voyage-4-large: $0.30
- voyage-4-lite: $0.125
- text-embedding-3-small: $0.05

### Example: 10,000 Queries per Month

Assuming average 20 tokens per query:
- Total tokens: 200,000
- voyage-4-large: $0.024
- voyage-4-lite: $0.01
- text-embedding-3-small: $0.004

At typical query volumes, embedding costs are negligible. The ingestion cost dominates.
