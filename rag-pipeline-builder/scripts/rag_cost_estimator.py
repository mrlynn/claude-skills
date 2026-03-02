#!/usr/bin/env python3
"""
Estimate RAG pipeline costs (embedding, storage, queries).
Usage: python rag_cost_estimator.py --docs 1000 --avg-doc-length 2000 --queries-per-month 5000
"""

import argparse

def estimate_chunks(total_tokens, chunk_size=1000, overlap=200):
    """Estimate number of chunks with overlap."""
    return int(total_tokens / (chunk_size - overlap))

def estimate_embedding_cost(tokens, model='voyage-3'):
    """Estimate embedding cost."""
    # Pricing per 1M tokens
    pricing = {
        'voyage-3': 0.02,
        'voyage-3-large': 0.08,
        'text-embedding-3-small': 0.02,
        'text-embedding-3-large': 0.13
    }
    
    cost_per_million = pricing.get(model, 0.02)
    return (tokens / 1_000_000) * cost_per_million

def estimate_storage_cost(num_chunks, dimensions=1024):
    """Estimate MongoDB storage cost."""
    # Vector storage: 4 bytes per dimension
    vector_bytes = num_chunks * dimensions * 4
    
    # Metadata overhead (rough estimate: 200 bytes per doc)
    metadata_bytes = num_chunks * 200
    
    total_gb = (vector_bytes + metadata_bytes) / (1024**3)
    
    # MongoDB Atlas storage: ~$0.25/GB/month (rough average)
    storage_cost = total_gb * 0.25
    
    return storage_cost, total_gb

def main():
    parser = argparse.ArgumentParser(description='Estimate RAG pipeline costs')
    parser.add_argument('--docs', type=int, required=True, help='Number of documents')
    parser.add_argument('--avg-doc-length', type=int, default=2000, help='Average tokens per document')
    parser.add_argument('--queries-per-month', type=int, default=1000, help='Expected queries per month')
    parser.add_argument('--model', default='voyage-3', choices=['voyage-3', 'voyage-3-large', 'text-embedding-3-small', 'text-embedding-3-large'])
    parser.add_argument('--chunk-size', type=int, default=1000, help='Chunk size in tokens')
    parser.add_argument('--overlap', type=int, default=200, help='Chunk overlap in tokens')
    parser.add_argument('--dimensions', type=int, default=1024, help='Embedding dimensions')
    parser.add_argument('--monthly-churn', type=float, default=0.10, help='Monthly doc churn rate (default 10%)')
    parser.add_argument('--avg-query-tokens', type=int, default=20, help='Average query length in tokens')
    
    args = parser.parse_args()
    
    # Calculate totals
    total_tokens = args.docs * args.avg_doc_length
    num_chunks = estimate_chunks(total_tokens, args.chunk_size, args.overlap)
    
    # Embedding costs
    initial_embed_cost = estimate_embedding_cost(total_tokens, args.model)
    monthly_update_tokens = total_tokens * args.monthly_churn
    monthly_update_cost = estimate_embedding_cost(monthly_update_tokens, args.model)
    
    # Storage costs
    storage_cost, storage_gb = estimate_storage_cost(num_chunks, args.dimensions)
    
    # Query costs
    query_tokens_per_month = args.queries_per_month * args.avg_query_tokens
    monthly_query_cost = estimate_embedding_cost(query_tokens_per_month, args.model)
    
    # Total monthly cost
    total_monthly = monthly_update_cost + storage_cost + monthly_query_cost
    annual_cost = total_monthly * 12
    cost_per_1k_queries = (monthly_query_cost / args.queries_per_month) * 1000 if args.queries_per_month > 0 else 0
    
    # Output
    print("="*60)
    print("RAG PIPELINE COST ESTIMATION")
    print("="*60)
    
    print(f"\nInput Documents: {args.docs:,}")
    print(f"Average Length: {args.avg_doc_length:,} tokens")
    print(f"Total Corpus: {total_tokens:,} tokens")
    
    print(f"\nChunking Strategy: {args.chunk_size} tokens, {args.overlap} overlap")
    print(f"Estimated Chunks: {num_chunks:,}")
    print(f"Embedding Model: {args.model}")
    print(f"Dimensions: {args.dimensions}")
    
    print("\n" + "-"*60)
    print("COSTS")
    print("-"*60)
    
    print(f"\nEmbedding Costs:")
    print(f"  Initial Ingestion: ${initial_embed_cost:.4f} (one-time)")
    print(f"  Monthly Updates ({args.monthly_churn*100:.0f}% churn): ${monthly_update_cost:.4f}")
    
    print(f"\nStorage Costs:")
    print(f"  Vector Storage: ${storage_cost:.2f}/month ({storage_gb:.2f} GB)")
    
    print(f"\nQuery Costs:")
    print(f"  Queries/Month: {args.queries_per_month:,}")
    print(f"  Embedding Cost: ${monthly_query_cost:.4f}/month")
    
    print("\n" + "="*60)
    print(f"Total Monthly Cost: ${total_monthly:.2f}")
    print(f"Annual Cost: ${annual_cost:.2f}")
    print(f"Cost per 1,000 queries: ${cost_per_1k_queries:.4f}")
    print("="*60)
    
    print(f"\n💡 Note: Voyage-3 is ~10x cheaper than OpenAI embeddings")
    print(f"   at ${estimate_embedding_cost(1_000_000, args.model):.2f} per 1M tokens")

if __name__ == '__main__':
    main()
