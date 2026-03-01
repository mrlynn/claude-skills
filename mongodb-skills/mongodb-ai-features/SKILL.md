---
name: mongodb-ai-features
description: Add AI capabilities to a MongoDB app including LLM summarization, structured generation, RAG pipeline with Atlas Vector Search, Voyage AI embeddings, and usage tracking with cost estimation
license: MIT
metadata:
  version: 1.0.0
  author: MongoDB Developer Relations
  category: mongodb-devrel
  domain: artificial-intelligence
  updated: 2026-03-01
  python-tools: embedding_cost_estimator.py, chunk_size_analyzer.py
  tech-stack: openai, voyage-ai, atlas-vector-search, mongoose
---

# mongodb-ai-features

## Trigger

Use this skill when adding AI capabilities to a MongoDB-backed app: LLM summarization, structured generation, RAG pipeline (ingest/embed/retrieve/chat), or AI usage tracking with cost estimation.

## Overview

Every DevRel demo and sample app includes AI features. This skill provides tested, MongoDB-native AI integration patterns — especially RAG with Atlas Vector Search. It includes a provider-agnostic usage logger, singleton client patterns, and a complete ingest-embed-retrieve-chat pipeline using Voyage AI for embeddings and OpenAI for generation.

## How to Use

### Quick Start
Invoke with `/mongodb-ai-features` or let Claude auto-activate when adding AI/RAG capabilities.

### Python Tools
- `scripts/embedding_cost_estimator.py` — Estimate Voyage/OpenAI costs for doc count + query volume
- `scripts/chunk_size_analyzer.py` — Analyze markdown files, recommend optimal chunk sizes

### Reference Docs
- `references/model-comparison.md` — Voyage vs OpenAI embedding models: cost, dimensions, quality
- `references/vector-search-setup.md` — Step-by-step Atlas Vector Search index creation

### Templates & Samples
- `assets/vector-search-index.json` — Copy-paste Atlas vector search index definition
- `assets/sample_rag_document.json` — Example RagDocument with embedding

## Architecture Decisions

- **Singleton AI clients**: Like the DB connection, OpenAI and Voyage clients are lazy-initialized singletons to avoid re-creating them per request.
- **Fire-and-forget usage logging**: AI usage is logged to MongoDB for cost monitoring, but the logger never throws — it silently catches errors so it never impacts the user-facing flow.
- **Voyage AI for embeddings, OpenAI for generation**: Voyage's `voyage-4-large` produces higher-quality embeddings for retrieval. OpenAI handles chat/generation. This is a deliberate two-provider strategy.
- **Document vs Query input types**: Voyage AI embeddings have separate modes for documents (being stored) and queries (being searched). Using the correct mode improves retrieval quality.
- **Category-based score boosting**: After vector search, results are re-ranked by category relevance. This prevents API docs from drowning out user-facing content unless explicitly requested.
- **Content hashing for incremental ingestion**: Documents are hashed before ingestion. On re-index, only changed files are re-embedded, saving API costs.

## File Structure

```
src/lib/
├── ai/
│   ├── usage-logger.ts         # Fire-and-forget logging with cost estimation
│   ├── summary-service.ts      # LLM summarization
│   ├── feedback-service.ts     # Multi-source feedback synthesis
│   ├── project-suggestion.ts   # Structured idea generation
│   └── embedding-service.ts    # OpenAI embeddings (for non-RAG use cases)
├── rag/
│   ├── types.ts                # IRagDocument, IRagIngestionRun, ChatMessage interfaces
│   ├── embeddings.ts           # Voyage AI embeddings (document + query)
│   ├── ingestion.ts            # Markdown → chunks → embeddings pipeline
│   ├── chunker.ts              # Document parsing and chunking
│   ├── retrieval.ts            # $vectorSearch + category boosting
│   ├── chat.ts                 # Streaming chat with context injection
│   └── rate-limit.ts           # Request throttling
└── db/models/
    ├── AiUsageLog.ts           # Usage tracking model
    ├── RagDocument.ts           # Document + embedding storage
    ├── RagIngestionRun.ts       # Ingestion run tracking
    └── RagConversation.ts       # Chat session history
```

## Code Patterns

### Pattern 1: AI Usage Logger (Fire-and-Forget)

```typescript
// src/lib/ai/usage-logger.ts
import { AiUsageLogModel } from "@/lib/db/models/AiUsageLog";
import { connectToDatabase } from "@/lib/db/connection";

const MODEL_COST_PER_MILLION: Record<string, number> = {
  "gpt-4o": 7.5,
  "gpt-4-turbo": 20,
  "text-embedding-3-small": 0.02,
  "voyage-4-large": 0.12,
  "voyage-4": 0.1,
  "voyage-4-lite": 0.05,
};

function estimateCost(model: string, tokens: number): number {
  const rate = MODEL_COST_PER_MILLION[model] ?? 5;
  return (tokens / 1_000_000) * rate;
}

interface LogAiUsageParams {
  category: string;    // "project_summaries" | "judge_feedback" | "rag_chat" | "rag_embeddings" | etc.
  provider: string;    // "openai" | "voyage"
  model: string;
  operation: string;   // "chat_completion" | "embedding" | "streaming"
  tokensUsed: number;
  promptTokens?: number;
  completionTokens?: number;
  durationMs: number;
  userId?: string;
  eventId?: string;
  metadata?: Record<string, unknown>;
  error?: boolean;
}

/**
 * Fire-and-forget. NEVER throws.
 */
export function logAiUsage(params: LogAiUsageParams): void {
  const cost = estimateCost(params.model, params.tokensUsed);
  connectToDatabase()
    .then(() => AiUsageLogModel.create({
      ...params,
      estimatedCost: cost,
      error: params.error ?? false,
    }))
    .catch((err) => console.error("[AI Usage Logger] Failed:", err.message));
}
```

### Pattern 2: Singleton OpenAI Client + Summarization

```typescript
// src/lib/ai/summary-service.ts
import OpenAI from "openai";
import { logAiUsage } from "./usage-logger";

let openai: OpenAI | null = null;

function getOpenAIClient(): OpenAI {
  if (!openai) {
    openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  }
  return openai;
}

export async function generateProjectSummary(project: {
  name: string; description: string; technologies: string[]; innovations?: string;
}): Promise<string> {
  const client = getOpenAIClient();
  const startTime = Date.now();

  const response = await client.chat.completions.create({
    model: "gpt-4-turbo",
    messages: [
      {
        role: "system",
        content: "You are summarizing hackathon projects for judges. Write exactly 2-3 sentences. Focus on what the project does, key technology, and what makes it novel.",
      },
      {
        role: "user",
        content: `Project: ${project.name}\nDescription: ${project.description}\nTech: ${project.technologies.join(", ")}${project.innovations ? `\nInnovations: ${project.innovations}` : ""}`,
      },
    ],
    max_tokens: 150,
    temperature: 0.6,
  });

  logAiUsage({
    category: "project_summaries", provider: "openai", model: response.model,
    operation: "chat_completion", tokensUsed: response.usage?.total_tokens || 0,
    promptTokens: response.usage?.prompt_tokens, completionTokens: response.usage?.completion_tokens,
    durationMs: Date.now() - startTime,
  });

  return response.choices[0].message.content?.trim() || "";
}
```

### Pattern 3: Voyage AI Embeddings (Document + Query)

```typescript
// src/lib/rag/embeddings.ts
import { logAiUsage } from "@/lib/ai/usage-logger";

const VOYAGE_API_URL = "https://api.voyageai.com/v1/embeddings";
const VOYAGE_BATCH_SIZE = 128;
const DOCUMENT_MODEL = "voyage-4-large";
const QUERY_MODEL = "voyage-4-large"; // Can downgrade to voyage-4 or voyage-4-lite (same embedding space)

async function callVoyageAPI(texts: string[], inputType: "document" | "query", model: string) {
  const response = await fetch(VOYAGE_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.VOYAGE_API_KEY}`,
    },
    body: JSON.stringify({ input: texts, model, input_type: inputType }),
  });
  if (!response.ok) throw new Error(`Voyage API error (${response.status}): ${await response.text()}`);
  return response.json();
}

/** Embed document chunks for storage. Handles batching automatically. */
export async function embedDocuments(texts: string[]): Promise<{ embeddings: number[][]; totalTokens: number }> {
  if (texts.length === 0) return { embeddings: [], totalTokens: 0 };

  const allEmbeddings: number[][] = [];
  let totalTokens = 0;
  const startTime = Date.now();

  for (let i = 0; i < texts.length; i += VOYAGE_BATCH_SIZE) {
    const batch = texts.slice(i, i + VOYAGE_BATCH_SIZE);
    const response = await callVoyageAPI(batch, "document", DOCUMENT_MODEL);
    const sorted = response.data.sort((a: { index: number }, b: { index: number }) => a.index - b.index);
    allEmbeddings.push(...sorted.map((d: { embedding: number[] }) => d.embedding));
    totalTokens += response.usage.total_tokens;
  }

  logAiUsage({
    category: "rag_embeddings", provider: "voyage", model: DOCUMENT_MODEL,
    operation: "embedding", tokensUsed: totalTokens, durationMs: Date.now() - startTime,
    metadata: { batchSize: texts.length, inputType: "document" },
  });

  return { embeddings: allEmbeddings, totalTokens };
}

/** Embed a user query for search. */
export async function embedQuery(text: string): Promise<number[]> {
  const startTime = Date.now();
  const response = await callVoyageAPI([text], "query", QUERY_MODEL);

  logAiUsage({
    category: "rag_embeddings", provider: "voyage", model: QUERY_MODEL,
    operation: "embedding", tokensUsed: response.usage.total_tokens,
    durationMs: Date.now() - startTime, metadata: { inputType: "query" },
  });

  return response.data[0].embedding;
}
```

### Pattern 4: Vector Search with Category Boosting

```typescript
// src/lib/rag/retrieval.ts
import { connectToDatabase } from "@/lib/db/connection";
import { RagDocumentModel } from "@/lib/db/models/RagDocument";
import { embedQuery } from "./embeddings";

const CATEGORY_BOOST: Record<string, number> = {
  events: 1.6, admin: 1.5, "getting-started": 1.4,
  features: 1.2, ai: 1.1, docs: 1.0, api: 0.3,
};

export async function retrieveContext(
  query: string,
  options: { isAuthenticated: boolean; topK?: number; scoreThreshold?: number }
) {
  await connectToDatabase();
  const topK = options.topK ?? 5;
  const queryEmbedding = await embedQuery(query);

  const filter: Record<string, unknown> = {};
  if (!options.isAuthenticated) filter["accessLevel"] = "public";

  // $vectorSearch is an Atlas-specific aggregation stage
  const pipeline = [
    {
      $vectorSearch: {
        index: "rag_document_vector",
        path: "embedding",
        queryVector: queryEmbedding,
        numCandidates: topK * 30,
        limit: topK * 3,
        ...(Object.keys(filter).length > 0 ? { filter } : {}),
      },
    },
    { $project: { content: 1, source: 1, score: { $meta: "vectorSearchScore" } } },
  ];

  const results = await RagDocumentModel.aggregate(pipeline);

  // Apply category boosting and re-sort
  const boosted = results.map((chunk) => ({
    ...chunk,
    score: chunk.score * (CATEGORY_BOOST[chunk.source.category.toLowerCase()] ?? 1.0),
  }));
  boosted.sort((a, b) => b.score - a.score);

  const topResults = boosted.slice(0, topK).filter((r) => r.score >= (options.scoreThreshold ?? 0.7));

  return {
    content: topResults.map((c, i) => `[Source ${i + 1}: ${c.source.title}]\n${c.content}`).join("\n\n---\n\n"),
    sources: topResults.map((c) => ({ title: c.source.title, url: c.source.url, section: c.source.section, relevanceScore: c.score })),
  };
}
```

### Pattern 5: RAG Type System

```typescript
// src/lib/rag/types.ts
import { Types } from "mongoose";

export interface IRagDocument {
  content: string;
  contentHash: string;
  accessLevel: "public" | "authenticated";
  source: { filePath: string; title: string; section: string; category: string; url: string; type: "docs" | "event" | "project" | "platform" };
  chunk: { index: number; totalChunks: number; tokens: number };
  embedding: number[];
  ingestion: { runId: string; ingestedAt: Date; ingestedBy: Types.ObjectId; version: number };
}

export interface IRagIngestionRun {
  runId: string;
  status: "running" | "completed" | "failed" | "cancelled";
  stats: {
    filesProcessed: number; filesSkipped: number;
    chunksCreated: number; chunksDeleted: number;
    embeddingsGenerated: number; totalTokens: number;
    errors: Array<{ file: string; error: string }>;
  };
  startedAt: Date; completedAt: Date | null; durationMs: number | null;
  triggeredBy: Types.ObjectId;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: { title: string; url: string; section: string; relevanceScore: number }[];
  feedback?: "up" | "down";
  createdAt: Date;
}

export interface IRagConversation {
  sessionId: string;
  userId?: Types.ObjectId;
  messages: ChatMessage[];
  metadata: { page: string; userAgent: string };
}

export type VoyageInputType = "document" | "query";
export interface EmbeddingResult { embeddings: number[][]; totalTokens: number }
export interface IngestionOptions { forceReindex?: boolean; docsPath?: string; triggeredBy: Types.ObjectId }
```

### Pattern 6: Atlas Vector Search Index

Create this index on the `ragdocuments` collection in Atlas:

```json
{
  "name": "rag_document_vector",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 1024,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "accessLevel"
      },
      {
        "type": "filter",
        "path": "source.category"
      }
    ]
  }
}
```

## Environment Variables

```bash
OPENAI_API_KEY=sk-...
VOYAGE_API_KEY=pa-...
```

## Dependencies

```bash
npm install openai
```

## Common Pitfalls

- **Use `input_type: "document"` for ingestion and `input_type: "query"` for search.** Mixing these degrades retrieval quality.
- **Never let the usage logger throw.** It's fire-and-forget. Wrap everything in `.catch()`.
- **Create the Atlas Vector Search index before querying.** `$vectorSearch` fails silently with zero results if the index doesn't exist.
- **Hash content before re-embedding.** Compare `contentHash` to avoid re-embedding unchanged documents.
- **Fetch more candidates than you need, then re-rank.** Use `numCandidates: topK * 30` and `limit: topK * 3` to get enough candidates for category boosting to be effective.
- **Don't store embeddings in `select: false` if you need them for search.** But DO exclude them from regular queries with `select('-embedding')` to avoid transferring large vectors.
