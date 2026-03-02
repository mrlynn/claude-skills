# Chunking Strategies for RAG Pipelines

## Overview

Chunking is the process of splitting documents into smaller units for embedding and retrieval. The strategy you choose dramatically impacts retrieval quality, cost, and user experience.

## The Core Tradeoff

- **Larger chunks:** More context per retrieval, fewer chunks (cheaper), but lower precision
- **Smaller chunks:** Higher precision, more chunks (expensive), but may lose context

**Sweet spot for most use cases:** 800-1200 tokens with 150-200 token overlap.

## Strategy Comparison

| Strategy | Best For | Chunk Size | Overlap | Pros | Cons |
|----------|----------|------------|---------|------|------|
| **Recursive** | Prose, articles, docs | 1000 tokens | 200 | Preserves paragraphs, good context | May split mid-thought |
| **Semantic** | Long-form content | Variable (by paragraph) | None | Natural boundaries | Uneven chunk sizes |
| **Function-boundary** | Code | Variable (per function) | None | Keeps code units intact | Requires AST parsing |
| **Sentence** | Short content, FAQs | ~100 tokens | None | High precision | Loses context |
| **Fixed-size** | Uniform content | 512/1024 tokens | 50-100 | Simple, predictable | Ignores structure |

## Recommended Strategies by Content Type

### Prose & Articles (Recursive)

**Configuration:**
```javascript
{
  strategy: 'recursive',
  chunkSize: 1000,
  overlap: 200,
  separators: ['\n\n', '\n', '. ', ' ', '']
}
```

**Why:** Recursive splitting tries paragraph boundaries first, then sentences, then words. This preserves natural document structure.

**Example:**
```
Input: 2500-token article
Output: 3 chunks
  - Chunk 1: tokens 1-1000 (intro + section 1)
  - Chunk 2: tokens 800-1800 (section 1 overlap + section 2)
  - Chunk 3: tokens 1600-2500 (section 2 overlap + conclusion)
```

### Code (Function-Boundary)

**Configuration:**
```javascript
{
  strategy: 'function-boundary',
  language: 'python', // or 'javascript', 'typescript', etc.
  includeDocstrings: true,
  maxSize: 2000 // fallback if function is huge
}
```

**Why:** Code semantics are tied to function boundaries. Splitting mid-function breaks context.

**Example:**
```python
# Input
def authenticate_user(email, password):
    """Verify user credentials."""
    # ... 50 lines
    return user

def send_welcome_email(user):
    """Send onboarding email."""
    # ... 30 lines
```

**Output:** 2 chunks (one per function, each with docstring)

### API Documentation (Endpoint-Based)

**Configuration:**
```javascript
{
  strategy: 'endpoint-based',
  splitOn: /^##\s+(GET|POST|PUT|DELETE)/m,
  includeSharedIntro: true
}
```

**Why:** Each endpoint is self-contained. Users searching "how to create a user" need the POST /users endpoint, not fragments.

### Structured Documents (Section-Based)

**Configuration:**
```javascript
{
  strategy: 'section',
  headingLevels: ['#', '##', '###'],
  preserveHierarchy: true
}
```

**Why:** Markdown/HTML documents have semantic structure. Splitting on headings keeps related content together.

## Overlap Strategy

Overlap prevents information loss at chunk boundaries.

**Example without overlap:**
```
Chunk 1: "...the benefits of vector search include speed"
Chunk 2: "and accuracy. MongoDB Atlas provides..."
```
Query: "What are the benefits of vector search?"
❌ No single chunk contains the full answer.

**Example with 200-token overlap:**
```
Chunk 1: "...the benefits of vector search include speed and accuracy. MongoDB Atlas provides..."
Chunk 2: "...vector search include speed and accuracy. MongoDB Atlas provides built-in vector search..."
```
Query: "What are the benefits of vector search?"
✅ Chunk 1 contains the full answer.

**Recommended overlap:** 15-20% of chunk size.

## Advanced: Hybrid Chunking

For mixed content (docs with code examples), use a two-pass approach:

1. **First pass:** Detect code blocks vs prose
2. **Second pass:** Apply function-boundary to code, recursive to prose
3. **Metadata:** Tag each chunk with content type

```javascript
{
  type: 'prose',
  chunk: '...explanation of the API...',
  embedding: [...]
}
{
  type: 'code',
  chunk: 'def example():\n    ...',
  embedding: [...]
}
```

Then boost code chunks for queries like "show me an example" and prose chunks for "explain how this works".

## Cost Implications

| Strategy | Avg Chunks per 1000 Docs | Embedding Cost (Voyage-3) |
|----------|---------------------------|---------------------------|
| Recursive (1000/200) | 2,400 | $0.048 |
| Semantic (avg 800) | 2,000 | $0.040 |
| Function-boundary | 1,800 | $0.036 |
| Sentence (~100) | 12,000 | $0.240 |

**Takeaway:** Sentence-level chunking is 5x more expensive for marginal quality improvement.

## Testing Your Strategy

Use the chunking analyzer:
```bash
python scripts/chunking_strategy_analyzer.py docs/ --output report.json
```

Then validate with sample queries:
1. Chunk your docs
2. Embed and ingest
3. Run 10-20 test queries
4. Measure MRR and Precision@5
5. Iterate on chunk size/overlap if quality is low

## References

- LangChain Text Splitters: https://python.langchain.com/docs/modules/data_connection/document_transformers/
- Pinecone Chunking Guide: https://www.pinecone.io/learn/chunking-strategies/
- OpenAI Embeddings Best Practices: https://platform.openai.com/docs/guides/embeddings/use-cases
