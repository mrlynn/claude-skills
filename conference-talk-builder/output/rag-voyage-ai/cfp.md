# Building Production RAG Systems with Voyage AI and MongoDB Atlas

## Abstract

You've seen the RAG demo. You've embedded "hello world" into a vector database. Now what? The gap between a RAG tutorial and a production retrieval system is enormous — and most developers are stuck in that gap, overpaying for embeddings, ignoring retrieval quality, and wondering why their AI app hallucinates.

In this talk, I'll take you from zero to production RAG using voyageai-cli (vaicli.com), an open-source toolkit I built that wraps the entire RAG pipeline into composable CLI commands. We'll start with chunking strategies (and why the wrong one kills your retrieval), move through Voyage AI's shared embedding space — where you can embed documents with a large model and query with a lite model for 83% cost savings — and end with two-stage retrieval (vector search + reranking) that dramatically improves result quality.

This isn't slides-only. We'll build a working RAG system live, measure it with real metrics (MRR, nDCG@K, Recall@K), and compose multi-step workflows that can be exposed as MCP tools for AI agents.

**You'll learn to:**
- Build a complete RAG pipeline from the CLI: chunk, embed, store, search, rerank — in one command
- Leverage Voyage AI's shared embedding space for asymmetric retrieval (83% query cost reduction)
- Measure retrieval quality with MRR, nDCG@K, and Recall@K — not just vibes
- Choose the right chunking strategy and embedding model for your domain (code, legal, finance)
- Compose multi-step RAG workflows and expose them as MCP tools for AI agents

**Target audience:** Backend and full-stack developers building AI-powered applications who want to move beyond toy RAG examples to production-grade retrieval systems

**Speaker experience:** Principal Staff Developer Advocate at MongoDB. Built voyageai-cli (vaicli.com) — an open-source RAG toolkit with 22+ commands, 312+ tests, workflow composition, and MCP server integration. Hands-on experience building and deploying RAG systems with MongoDB Atlas Vector Search.
