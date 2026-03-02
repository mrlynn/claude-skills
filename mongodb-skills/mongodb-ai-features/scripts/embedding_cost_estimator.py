#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Estimate embedding costs for Voyage AI and OpenAI models.

  Calculates one-time ingestion cost, monthly query cost, and annual
  totals based on document count, average token size, and query volume.
"""

import argparse
import json
import sys
from typing import Dict, List

# Pricing per 1 million tokens (USD)
MODEL_PRICING: Dict[str, Dict[str, object]] = {
    "voyage-4-large": {
        "provider": "Voyage AI",
        "price_per_million": 0.12,
        "max_tokens": 16000,
        "dimensions": 1024,
    },
    "voyage-4": {
        "provider": "Voyage AI",
        "price_per_million": 0.10,
        "max_tokens": 16000,
        "dimensions": 1024,
    },
    "voyage-4-lite": {
        "provider": "Voyage AI",
        "price_per_million": 0.05,
        "max_tokens": 16000,
        "dimensions": 512,
    },
    "text-embedding-3-small": {
        "provider": "OpenAI",
        "price_per_million": 0.02,
        "max_tokens": 8191,
        "dimensions": 1536,
    },
    "text-embedding-3-large": {
        "provider": "OpenAI",
        "price_per_million": 0.13,
        "max_tokens": 8191,
        "dimensions": 3072,
    },
}

VALID_MODELS = sorted(MODEL_PRICING.keys())


def estimate_costs(
    docs: int,
    avg_tokens: int,
    queries_per_month: int,
    model: str,
) -> Dict[str, object]:
    """Calculate embedding costs.

    Args:
        docs: Number of documents to embed.
        avg_tokens: Average tokens per document.
        queries_per_month: Monthly query volume.
        model: Embedding model name.

    Returns:
        Dict with cost breakdown.
    """
    info = MODEL_PRICING[model]
    price_per_token = info["price_per_million"] / 1_000_000

    # Ingestion: embed all documents (one-time)
    ingestion_tokens = docs * avg_tokens
    ingestion_cost = ingestion_tokens * price_per_token

    # Queries: embed each query (assume avg query is ~50 tokens)
    query_tokens_per_month = queries_per_month * 50
    monthly_query_cost = query_tokens_per_month * price_per_token

    # Annual: ingestion (one-time) + 12 months of queries
    annual_total = ingestion_cost + (monthly_query_cost * 12)

    return {
        "model": model,
        "provider": info["provider"],
        "dimensions": info["dimensions"],
        "price_per_million_tokens": info["price_per_million"],
        "documents": docs,
        "avg_tokens_per_doc": avg_tokens,
        "queries_per_month": queries_per_month,
        "ingestion": {
            "total_tokens": ingestion_tokens,
            "cost": round(ingestion_cost, 4),
        },
        "monthly_queries": {
            "total_tokens": query_tokens_per_month,
            "cost": round(monthly_query_cost, 4),
        },
        "annual_total": round(annual_total, 4),
    }


def format_text(result: Dict[str, object]) -> str:
    """Format cost estimate as human-readable text."""
    lines: List[str] = []
    lines.append("Embedding Cost Estimate")
    lines.append("=" * 40)
    lines.append(f"Model:    {result['model']} ({result['provider']})")
    lines.append(f"Dims:     {result['dimensions']}")
    lines.append(f"Price:    ${result['price_per_million_tokens']}/M tokens")
    lines.append("")
    lines.append("Input Parameters:")
    lines.append(f"  Documents:         {result['documents']:>12,}")
    lines.append(f"  Avg tokens/doc:    {result['avg_tokens_per_doc']:>12,}")
    lines.append(f"  Queries/month:     {result['queries_per_month']:>12,}")
    lines.append("")
    lines.append("Cost Breakdown:")
    ing = result["ingestion"]
    lines.append(f"  Ingestion (one-time):")
    lines.append(f"    Tokens:          {ing['total_tokens']:>12,}")
    lines.append(f"    Cost:            ${ing['cost']:>11,.4f}")
    mq = result["monthly_queries"]
    lines.append(f"  Monthly queries:")
    lines.append(f"    Tokens/month:    {mq['total_tokens']:>12,}")
    lines.append(f"    Cost/month:      ${mq['cost']:>11,.4f}")
    lines.append("")
    lines.append(f"  Annual total:      ${result['annual_total']:>11,.4f}")
    lines.append(f"    (ingestion + 12 months of queries)")

    return "\n".join(lines)


def format_json(result: Dict[str, object]) -> str:
    """Format cost estimate as JSON."""
    return json.dumps({"tool": "embedding_cost_estimator", **result}, indent=2)


def main() -> int:
    """Entry point for embedding cost estimator."""
    parser = argparse.ArgumentParser(
        description="Estimate embedding costs for Voyage AI and OpenAI models.",
    )
    parser.add_argument(
        "--docs", type=int, required=True,
        help="Number of documents to embed",
    )
    parser.add_argument(
        "--avg-tokens", type=int, default=500,
        help="Average tokens per document (default: 500)",
    )
    parser.add_argument(
        "--queries-per-month", type=int, default=10000,
        help="Monthly query volume (default: 10000)",
    )
    parser.add_argument(
        "--model", default="voyage-4-large", choices=VALID_MODELS,
        help="Embedding model (default: voyage-4-large)",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--compare", action="store_true",
        help="Compare costs across all models",
    )
    args = parser.parse_args()

    if args.docs < 1:
        print("Error: --docs must be at least 1", file=sys.stderr)
        return 2

    if args.compare:
        results = []
        for model in VALID_MODELS:
            results.append(estimate_costs(args.docs, args.avg_tokens, args.queries_per_month, model))
        if args.format == "json":
            print(json.dumps({"tool": "embedding_cost_estimator", "comparison": results}, indent=2))
        else:
            print("Embedding Cost Comparison")
            print("=" * 70)
            print(f"{'Model':<28} {'$/M tokens':>10} {'Ingest':>10} {'Monthly':>10} {'Annual':>10}")
            print("-" * 70)
            for r in results:
                print(
                    f"{r['model']:<28} "
                    f"${r['price_per_million_tokens']:>9.2f} "
                    f"${r['ingestion']['cost']:>9.4f} "
                    f"${r['monthly_queries']['cost']:>9.4f} "
                    f"${r['annual_total']:>9.4f}"
                )
        return 0

    result = estimate_costs(args.docs, args.avg_tokens, args.queries_per_month, args.model)

    if args.format == "json":
        print(format_json(result))
    else:
        print(format_text(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
