# RAG Pipeline Builder

RAG is one of those things where the demo takes 20 minutes and production takes 2 months. I've built enough of these pipelines — chunking strategies, embedding cost surprises, retrieval that returns garbage because your chunk boundaries landed mid-sentence — that I finally sat down and codified what actually works. This is the stuff I wish someone handed me the first time.

## Quick Start

1. **Analyze your documents:**
   ```bash
   python scripts/chunking_strategy_analyzer.py docs/ --output report.json
   ```

2. **Estimate costs:**
   ```bash
   python scripts/rag_cost_estimator.py --docs 1000 --queries-per-month 5000
   ```

3. **Set up environment:**
   ```bash
   cp assets/.env.example .env
   # Edit .env with your credentials
   ```

4. **Create vector index:**
   Use `assets/vector-index-config.json` in MongoDB Atlas UI

5. **Ingest documents:**
   ```bash
   node assets/ingest-pipeline.js
   ```

6. **Validate:**
   ```bash
   python scripts/pipeline_validator.py config.json --test-queries assets/sample-queries.json
   ```

## Python Tools

- `chunking_strategy_analyzer.py` - Recommends chunking strategy per file type
- `rag_cost_estimator.py` - Estimates embedding, storage, query costs
- `pipeline_validator.py` - Validates config and tests retrieval quality

## Templates

- `ingest-pipeline.js` - Document ingestion with content hashing
- `vector-index-config.json` - Atlas Vector Search index definition
- `retrieval-api.js` - Search API with score boosting
- `chat-endpoint.js` - Streaming chat endpoint
- `sample-queries.json` - Test queries for validation

## Reference Documentation

- `references/chunking-strategies.md` - Deep dive on chunking approaches
- `references/rag-patterns.md` - Production patterns from real deployments

## Cost Example

For 1,000 documents (2M tokens total), 5,000 queries/month:
- Initial embedding: $0.04 (one-time)
- Monthly updates: $0.004 (10% churn)
- Storage: $0.14/month
- Queries: $0.10/month
- **Total: ~$0.26/month**

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)
