# Building Production RAG Systems with Voyage AI and MongoDB Atlas — 45 min

## 1. Introduction: The RAG Gap (5 min) — 5 slides

- **Slide 1: Title slide** — "Building Production RAG Systems with Voyage AI and MongoDB Atlas"
- **Slide 2: The promise vs reality** — Every RAG tutorial: embed → search → done. Production: chunking, cost, quality, scale, evaluation, composition
- **Slide 3: The gap** — Show the complexity cliff between "hello world RAG" and production. Stats: what breaks when you go from 100 docs to 10M
- **Slide 4: What we're building today** — End-to-end RAG pipeline using voyageai-cli (vaicli.com). Open source, 22+ commands, composable
- **Slide 5: Agenda overview** — Chunking → Embedding → Retrieval → Evaluation → Composition

## 2. Foundations: Chunking & Embedding (12 min) — 10 slides

- **Slide 6: Why chunking matters** — Wrong chunk size = wrong retrieval. Too small: no context. Too large: noise drowns signal
- **Slide 7: 5 chunking strategies** — Fixed, sentence, paragraph, recursive (default), markdown. Code: `src/lib/chunker.js`
- **Slide 8: Live demo — chunking** — `vai chunk ./docs/sample.md --strategy recursive --size 512` — show output, count chunks
- **Slide 9: Voyage AI model family** — voyage-4-large (MoE, RTEB #1), voyage-4, voyage-4-lite, voyage-4-nano. Domain: code-3, finance-2, law-2
- **Slide 10: The shared embedding space** — Key insight: all voyage-4 models share the same vector space. Embed with large, query with lite
- **Slide 11: Asymmetric retrieval diagram** — Documents → voyage-4-large ($0.12/1M). Queries → voyage-4-lite ($0.02/1M). Same space, 83% savings
- **Slide 12: Cost estimation** — `vai estimate --docs 10M --queries 100M --months 12` — show symmetric vs asymmetric costs
- **Slide 13: Matryoshka dimensions** — 256, 512, 1024, 2048 dims. Tradeoff: storage/speed vs quality. Show benchmark comparison
- **Slide 14: Live demo — embedding** — `vai embed "What is vector search?"` — show vector output, dimensions, model info
- **Slide 15: MongoDB Atlas Vector Search** — $vectorSearch aggregation, automatic index creation, pre-filter support

## 3. Two-Stage Retrieval: Search + Rerank (10 min) — 8 slides

- **Slide 16: Why single-stage retrieval isn't enough** — Vector similarity is good but not great. Reranking closes the quality gap
- **Slide 17: Two-stage architecture** — Stage 1: Fast vector search (retrieve 50 candidates). Stage 2: Reranker scores and reorders (return top 10)
- **Slide 18: Voyage rerankers** — rerank-2.5 (accurate) vs rerank-2.5-lite (fast). Cross-encoder architecture
- **Slide 19: Live demo — full query pipeline** — `vai query "How does vector search work?" --rerank` — show results with relevance scores
- **Slide 20: The one-command pipeline** — `vai pipeline ./docs/ --collection my-kb` — chunk → embed → store in one shot
- **Slide 21: Live demo — pipeline** — Ingest a real document set, show progress, query immediately after
- **Slide 22: vai chat** — Conversational RAG: `vai chat --collection my-kb` — multi-turn retrieval with context
- **Slide 23: Pre-filtering** — Combine metadata filters with vector search: `{ "metadata.type": "api-doc" }`. Narrow before you search

## 4. Measuring Quality: Evaluation (8 min) — 7 slides

- **Slide 24: "It works" is not a metric** — Vibes-based evaluation vs quantitative retrieval metrics
- **Slide 25: Key metrics explained** — MRR (Mean Reciprocal Rank), nDCG@K, Recall@K, Precision@K, MAP — what each tells you
- **Slide 26: Building a test set** — JSONL format: query + expected relevant documents. The investment that pays off
- **Slide 27: Live demo — evaluation** — `vai eval --test-set test.jsonl --save baseline.json` — show metric outputs
- **Slide 28: A/B comparison** — `vai eval compare --configs baseline.json,experiment.json` — compare chunking strategies, models, parameters
- **Slide 29: Benchmarking models** — `vai benchmark embed --models voyage-4-large,voyage-4,voyage-4-lite --rounds 5` — latency, throughput, quality on YOUR data
- **Slide 30: Benchmark: shared space validation** — `vai benchmark space` — empirically prove asymmetric retrieval works

## 5. Composition: Workflows & MCP (5 min) — 5 slides

- **Slide 31: Beyond single queries** — Real RAG systems need multi-step pipelines: decompose → search multiple collections → merge → rerank → generate
- **Slide 32: Workflow system** — JSON-defined pipelines with step dependencies, conditional logic, template expressions
- **Slide 33: Example workflow** — Multi-collection search + rerank: show the JSON, explain data flow between steps
- **Slide 34: MCP server integration** — `vai mcp install claude-code` — expose vai tools to AI agents. 11 tools available. RAG as infrastructure
- **Slide 35: The agent loop** — AI agent → MCP → vai → MongoDB Atlas → results. Agents don't need to know CLI commands

## 6. Wrap-up (5 min) — 3 slides

- **Slide 36: What we built** — Complete production RAG: chunking → embedding → two-stage retrieval → evaluation → workflow composition → agent integration
- **Slide 37: Key takeaways** — (1) Asymmetric retrieval saves 83% on queries (2) Always rerank (3) Measure with MRR/nDCG, not vibes (4) Compose workflows, don't hardcode pipelines (5) Expose RAG as MCP tools for agents
- **Slide 38: Get started** — vaicli.com | `npx vai` | github.com/mrlynn/voyageai-cli | MCP: `vai mcp install claude-code`

---

**Total slides:** 38
**Total time:** 45 minutes
**Pace:** 0.84 slides/min (comfortable for technical talk with demos)
**Buffer:** ~2 min built into demo sections
**Demo segments:** 6 live demos throughout (chunking, embedding, query, pipeline, eval, benchmark)
