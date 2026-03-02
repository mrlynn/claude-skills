#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Estimate monthly MongoDB Atlas costs by cluster tier and provider.

  Provides approximate pricing for Atlas dedicated and shared clusters
  across AWS, GCP, and Azure. Supports multiple clusters and outputs
  monthly and annual cost estimates.
"""

import argparse
import json
import sys
from typing import Dict, Optional, Tuple

# Approximate monthly pricing (USD) by tier and provider
# Format: { tier: { provider: price } }
PRICING: Dict[str, Dict[str, float]] = {
    "M0":  {"AWS": 0.0,   "GCP": 0.0,   "AZURE": 0.0},
    "M2":  {"AWS": 9.0,   "GCP": 9.0,   "AZURE": 9.0},
    "M5":  {"AWS": 25.0,  "GCP": 25.0,  "AZURE": 25.0},
    "M10": {"AWS": 57.0,  "GCP": 49.0,  "AZURE": 57.0},
    "M20": {"AWS": 140.0, "GCP": 140.0, "AZURE": 140.0},
    "M30": {"AWS": 430.0, "GCP": 430.0, "AZURE": 430.0},
    "M40": {"AWS": 890.0, "GCP": 890.0, "AZURE": 890.0},
    "M50": {"AWS": 1560.0,"GCP": 1560.0,"AZURE": 1560.0},
}

TIER_SPECS: Dict[str, Dict[str, str]] = {
    "M0":  {"ram": "Shared", "storage": "512 MB", "vcpus": "Shared", "category": "Free"},
    "M2":  {"ram": "Shared", "storage": "2 GB",   "vcpus": "Shared", "category": "Shared"},
    "M5":  {"ram": "Shared", "storage": "5 GB",   "vcpus": "Shared", "category": "Shared"},
    "M10": {"ram": "2 GB",   "storage": "10 GB",  "vcpus": "2",      "category": "Dedicated"},
    "M20": {"ram": "4 GB",   "storage": "20 GB",  "vcpus": "2",      "category": "Dedicated"},
    "M30": {"ram": "8 GB",   "storage": "40 GB",  "vcpus": "2",      "category": "Dedicated"},
    "M40": {"ram": "16 GB",  "storage": "80 GB",  "vcpus": "4",      "category": "Dedicated"},
    "M50": {"ram": "32 GB",  "storage": "160 GB", "vcpus": "8",      "category": "Dedicated"},
}

VALID_TIERS = sorted(PRICING.keys(), key=lambda t: int(t[1:]))
VALID_PROVIDERS = ["AWS", "GCP", "AZURE"]


def estimate_cost(
    tier: str,
    provider: str,
    clusters: int = 1,
) -> Dict[str, object]:
    """Calculate monthly and annual cost estimates."""
    monthly_per_cluster = PRICING[tier][provider]
    monthly_total = monthly_per_cluster * clusters
    annual_total = monthly_total * 12
    specs = TIER_SPECS[tier]

    return {
        "tier": tier,
        "provider": provider,
        "clusters": clusters,
        "category": specs["category"],
        "specs": specs,
        "monthly_per_cluster": monthly_per_cluster,
        "monthly_total": monthly_total,
        "annual_total": annual_total,
    }


def format_text(result: Dict[str, object]) -> str:
    """Format cost estimate as human-readable text."""
    lines = []
    lines.append("MongoDB Atlas Cost Estimate")
    lines.append("=" * 40)
    lines.append(f"Tier:     {result['tier']} ({result['category']})")
    lines.append(f"Provider: {result['provider']}")
    lines.append(f"Clusters: {result['clusters']}")
    lines.append("")
    lines.append("Cluster Specs:")
    specs = result["specs"]
    lines.append(f"  RAM:     {specs['ram']}")
    lines.append(f"  Storage: {specs['storage']}")
    lines.append(f"  vCPUs:   {specs['vcpus']}")
    lines.append("")
    lines.append("Cost Breakdown:")
    lines.append(f"  Per cluster/month: ${result['monthly_per_cluster']:>10,.2f}")
    if result["clusters"] > 1:
        lines.append(f"  x {result['clusters']} clusters:       ${result['monthly_total']:>10,.2f}/mo")
    lines.append(f"  Monthly total:     ${result['monthly_total']:>10,.2f}")
    lines.append(f"  Annual total:      ${result['annual_total']:>10,.2f}")
    lines.append("")
    if result["tier"] == "M0":
        lines.append("Note: M0 is the free tier with limited features.")
        lines.append("      Max 1 free cluster per project.")
    elif result["category"] == "Shared":
        lines.append("Note: Shared tiers have limited configuration options.")
    else:
        lines.append("Note: Prices are approximate and may vary by region.")
        lines.append("      Backup, data transfer, and BI Connector cost extra.")
    return "\n".join(lines)


def format_json(result: Dict[str, object]) -> str:
    """Format cost estimate as JSON."""
    return json.dumps({
        "tool": "atlas_cost_estimator",
        **result,
    }, indent=2)


def main() -> int:
    """Entry point for Atlas cost estimator."""
    parser = argparse.ArgumentParser(
        description="Estimate monthly MongoDB Atlas cluster costs.",
    )
    parser.add_argument(
        "--tier", required=True, choices=VALID_TIERS,
        help=f"Cluster tier ({', '.join(VALID_TIERS)})",
    )
    parser.add_argument(
        "--provider", default="AWS", choices=VALID_PROVIDERS,
        help="Cloud provider (default: AWS)",
    )
    parser.add_argument(
        "--region", default=None,
        help="Cloud region (informational only, does not affect pricing)",
    )
    parser.add_argument(
        "--clusters", type=int, default=1,
        help="Number of clusters (default: 1)",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    if args.clusters < 1:
        print("Error: --clusters must be at least 1", file=sys.stderr)
        return 2

    result = estimate_cost(args.tier, args.provider, args.clusters)
    if args.region:
        result["region"] = args.region

    if args.format == "json":
        print(format_json(result))
    else:
        print(format_text(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
