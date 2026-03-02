---
name: rag-pipeline-builder
description: Build production-ready RAG (Retrieval-Augmented Generation) pipelines from scratch with MongoDB Atlas Vector Search, Voyage AI embeddings, and proven chunking strategies
license: MIT
metadata:
  version: 1.0.0
  author: MongoDB Developer Relations
  category: ai-engineering
  domain: retrieval-augmented-generation
  updated: 2026-03-01
  python-tools: chunking_strategy_analyzer.py, rag_cost_estimator.py, pipeline_validator.py
  tech-stack: mongodb, atlas-vector-search, voyage-ai, nodejs, python
---

# rag-pipeline-builder

## Trigger

Use this skill when building a RAG system from scratch, creating document chatbots, implementing semantic search, or setting up knowledge base retrieval for AI applications.

**Trigger phrases:**
- "Build a RAG pipeline"
- "Document chatbot"
- "Semantic search over my docs"
- "Ingest and search"
- "Knowledge base retrieval"

## Overview

Every production RAG pipeline follows the same flow: ingest documents → chunk intelligently → embed with quality models → store in vector database → retrieve relevant context → generate responses. This skill generates the complete pipeline with battle-tested patterns from real deployments (AA Companion, VAI workflows, Developer Day demos).

This is **not** about adding AI to an existing app (that's `mongodb-ai-features`). This is about **building a RAG system from the ground up**.

## How to Use

### Quick Start
1. Analyze your documents: `python scripts/chunking_strategy_analyzer.py docs/`
2. Estimate costs: `python scripts/rag_cost_estimator.py --docs 1000 --queries-per-month 5000`
3. Generate pipeline from templates in `assets/`
4. Validate: `python scripts/pipeline_validator.py config.json`

### Python Tools
- `scripts/chunking_strategy_analyzer.py` — Analyze documents and recommend optimal chunking strategy
- `scripts/rag_cost_estimator.py` — Estimate embedding, storage, and query costs
- `scripts/pipeline_validator.py` — Validate pipeline config and test retrieval quality

### Reference Docs
- `references/chunking-strategies.md` — Deep dive on chunking approaches
- `references/rag-patterns.md` — Production patterns from real deployments

### Templates & Assets
- `assets/ingest-pipeline.js` — Complete ingestion with content hashing
- `assets/vector-index-config.json` — Atlas Vector Search index definition
- `assets/retrieval-api.js` — Retrieval API with score boosting
- `assets/chat-endpoint.js` — Streaming chat endpoint
- `assets/sample-queries.json` — Test queries for validation

## Architecture Decisions

### Why Voyage AI for Embeddings
- **Quality:** Voyage-3 outperforms OpenAI on retrieval benchmarks
- **Cost:** ~$0.02 per 1M tokens (10x cheaper than text-embedding-3-large)
- **Speed:** Fast batch processing (128 documents per batch)
- **Integration:** Seamless with MongoDB Atlas Vector Search

### Content Hashing for Incremental Ingestion
Reprocessing entire corpus on every update is wasteful. Content hashing (SHA-256) enables incremental updates:
- Hash each document before embedding
- Store hash in metadata
- On re-ingestion, skip documents with matching hashes
- Only process new/changed documents

**Result:** 90%+ cost reduction after initial ingestion.

### Chunking Strategy Selection

| Content Type | Strategy | Chunk Size | Overlap | Why |
|--------------|----------|------------|---------|-----|
| Prose/articles | Recursive | 1000 tokens | 200 | Preserves paragraph boundaries |
| Code | Function-boundary | Variable | None | Keeps functions intact |
| Structured docs | Paragraph | Variable | None | Respects document structure |
| API docs | Endpoint-based | Variable | None | Self-contained endpoints |
| Conversations | Turn-boundary | Variable | None | Keeps Q&A pairs together |

### Category-Based Score Boosting
Not all results are equal. Boost by document category:
```javascript
const boostedScore = baseScore * (doc.category === 'ui' ? 1.5 : 1.0);
```

### Fire-and-Forget Usage Logging
Don't block responses to log usage:
```javascript
logUsage(query, results).catch(err => console.error('Log failed:', err));
return results; // Return immediately
```

## Generated Pipeline Structure

```
my-rag-app/
├── ingest/
│   ├── ingest.js              # Main ingestion pipeline
│   ├── chunkers/
│   │   ├── recursive.js       # Recursive text splitting
│   │   ├── semantic.js        # Paragraph-based
│   │   └── code.js            # Function-boundary
│   └── utils/
│       ├── content-hash.js    # SHA-256 hashing
│       └── batch-embed.js     # Voyage AI batching
├── index/
│   ├── create-index.js        # Atlas Vector Search setup
│   └── index-config.json      # Index definition
├── api/
│   ├── search.js              # Retrieval API
│   ├── chat.js                # Chat endpoint
│   └── middleware/
│       └── usage-logger.js    # Fire-and-forget logging
├── lib/
│   ├── voyage-client.js       # Voyage AI wrapper
│   ├── atlas-client.js        # MongoDB connection
│   └── score-booster.js       # Category boosting
├── tests/
│   ├── retrieval-quality.test.js
│   └── fixtures/
│       └── sample-queries.json
├── .env.example
└── README.md
```

## When to Use vs. `mongodb-ai-features`

| Use `rag-pipeline-builder` | Use `mongodb-ai-features` |
|-----------------------------|---------------------------|
| Building RAG from scratch | Adding AI to existing app |
| Document chatbot | Project summarization |
| Knowledge base search | Feedback analysis |
| Semantic docs search | AI-generated content |
| No existing schema | App has MongoDB models |

## Environment Variables

```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/rag-db

# Voyage AI
VOYAGE_API_KEY=pa-xxx...

# Optional: LLM for generation
OPENAI_API_KEY=sk-xxx...

# Configuration
VECTOR_INDEX_NAME=vector_index
COLLECTION_NAME=documents
EMBEDDING_DIMENSIONS=1024
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Production Checklist

- [ ] Chunking strategy validated with analyzer
- [ ] Cost estimation completed
- [ ] Vector index created (correct dimensions)
- [ ] Retrieval quality tested (MRR > 0.7)
- [ ] Incremental ingestion implemented
- [ ] Score boosting configured
- [ ] Usage logging implemented
- [ ] Error handling on embed failures
- [ ] Rate limiting configured
- [ ] Monitoring for latency/errors

## References

- Voyage AI: https://voyage.ai/pricing
- Atlas Vector Search: https://mongodb.com/docs/atlas/atlas-vector-search/
- Chunking strategies: `references/chunking-strategies.md`
- RAG patterns: `references/rag-patterns.md`

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)
