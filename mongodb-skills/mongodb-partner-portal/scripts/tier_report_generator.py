#!/usr/bin/env python3
"""Generate partner engagement reports from partner data JSON.

Groups partners by tier, calculates per-tier statistics (count,
average engagement level, total contribution), identifies top
partners, and flags inactive partners.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Default tier hierarchy and thresholds
TIER_ORDER = ["platinum", "gold", "silver", "bronze"]
DEFAULT_INACTIVE_THRESHOLD = 30  # engagement score below this = inactive


def load_partners(filepath: str) -> List[Dict[str, Any]]:
    """Load partner data from a JSON file.

    Expected format: array of objects with at minimum:
    { "name": str, "tier": str, "engagement_score": number }

    Optional fields: "contribution": number, "active": bool,
    "joined": str, "contact": str
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if isinstance(data, dict) and "partners" in data:
        data = data["partners"]

    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of partner objects (or {partners: [...]})")

    return data


def generate_report(partners: List[Dict[str, Any]], inactive_threshold: int = DEFAULT_INACTIVE_THRESHOLD) -> Dict[str, Any]:
    """Generate a full engagement report from partner data."""
    # Group by tier
    tiers: Dict[str, List[Dict[str, Any]]] = {}
    for p in partners:
        tier = p.get("tier", "unknown").lower()
        tiers.setdefault(tier, []).append(p)

    # Per-tier stats
    tier_stats: List[Dict[str, Any]] = []
    for tier_name in TIER_ORDER + sorted(set(tiers.keys()) - set(TIER_ORDER)):
        members = tiers.get(tier_name, [])
        if not members:
            continue

        scores = [m.get("engagement_score", 0) for m in members]
        contributions = [m.get("contribution", 0) for m in members]

        tier_stats.append({
            "tier": tier_name,
            "count": len(members),
            "avg_engagement": round(sum(scores) / len(scores), 1) if scores else 0,
            "min_engagement": min(scores) if scores else 0,
            "max_engagement": max(scores) if scores else 0,
            "total_contribution": round(sum(contributions), 2),
            "avg_contribution": round(sum(contributions) / len(contributions), 2) if contributions else 0,
        })

    # Top partners (top 5 by engagement_score)
    sorted_partners = sorted(
        partners,
        key=lambda p: p.get("engagement_score", 0),
        reverse=True,
    )
    top_partners = [
        {
            "name": p.get("name", "Unknown"),
            "tier": p.get("tier", "unknown"),
            "engagement_score": p.get("engagement_score", 0),
            "contribution": p.get("contribution", 0),
        }
        for p in sorted_partners[:5]
    ]

    # Inactive partners
    inactive = [
        {
            "name": p.get("name", "Unknown"),
            "tier": p.get("tier", "unknown"),
            "engagement_score": p.get("engagement_score", 0),
        }
        for p in partners
        if p.get("engagement_score", 0) < inactive_threshold
        or p.get("active") is False
    ]

    # Summary
    all_scores = [p.get("engagement_score", 0) for p in partners]
    all_contributions = [p.get("contribution", 0) for p in partners]

    return {
        "total_partners": len(partners),
        "total_tiers": len(tier_stats),
        "overall_avg_engagement": round(sum(all_scores) / max(len(all_scores), 1), 1),
        "total_contribution": round(sum(all_contributions), 2),
        "tier_breakdown": tier_stats,
        "top_partners": top_partners,
        "inactive_partners": inactive,
        "inactive_count": len(inactive),
    }


def format_text(report: Dict[str, Any]) -> str:
    """Format report as human-readable text."""
    lines: List[str] = []
    lines.append("Partner Engagement Report")
    lines.append("=" * 50)
    lines.append(f"Total partners:       {report['total_partners']}")
    lines.append(f"Avg engagement:       {report['overall_avg_engagement']}")
    lines.append(f"Total contribution:   ${report['total_contribution']:,.2f}")
    lines.append(f"Inactive partners:    {report['inactive_count']}")
    lines.append("")

    # Tier breakdown
    lines.append("Tier Breakdown:")
    lines.append(f"{'Tier':<12} {'Count':>6} {'Avg Eng':>8} {'Min':>5} {'Max':>5} {'Total $':>12}")
    lines.append("-" * 52)
    for t in report["tier_breakdown"]:
        lines.append(
            f"{t['tier']:<12} {t['count']:>6} {t['avg_engagement']:>8.1f} "
            f"{t['min_engagement']:>5} {t['max_engagement']:>5} "
            f"${t['total_contribution']:>11,.2f}"
        )
    lines.append("")

    # Top partners
    lines.append("Top Partners:")
    for i, p in enumerate(report["top_partners"], 1):
        lines.append(
            f"  {i}. {p['name']} ({p['tier']}) - "
            f"Score: {p['engagement_score']}, "
            f"Contribution: ${p['contribution']:,.2f}"
        )
    lines.append("")

    # Inactive partners
    if report["inactive_partners"]:
        lines.append(f"Inactive Partners (engagement < {DEFAULT_INACTIVE_THRESHOLD}):")
        for p in report["inactive_partners"]:
            lines.append(f"  - {p['name']} ({p['tier']}) - Score: {p['engagement_score']}")
    else:
        lines.append("No inactive partners found.")

    return "\n".join(lines)


def format_json(report: Dict[str, Any]) -> str:
    """Format report as JSON."""
    return json.dumps({"tool": "tier_report_generator", **report}, indent=2)


def main() -> int:
    """Entry point for tier report generator."""
    parser = argparse.ArgumentParser(
        description="Generate partner engagement reports from partner data JSON.",
    )
    parser.add_argument(
        "data_file",
        help="Path to JSON file containing partner data",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--inactive-threshold", type=int, default=DEFAULT_INACTIVE_THRESHOLD,
        help=f"Engagement score threshold for inactive flag (default: {DEFAULT_INACTIVE_THRESHOLD})",
    )
    parser.add_argument(
        "--top-n", type=int, default=5,
        help="Number of top partners to highlight (default: 5)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.data_file):
        print(f"Error: file not found: {args.data_file}", file=sys.stderr)
        return 2

    try:
        partners = load_partners(args.data_file)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Error: invalid data file: {exc}", file=sys.stderr)
        return 2

    if not partners:
        print("No partner data found.", file=sys.stderr)
        return 0

    report = generate_report(partners, inactive_threshold=args.inactive_threshold)

    # Adjust top_n
    report["top_partners"] = report["top_partners"][:args.top_n]

    if args.format == "json":
        print(format_json(report))
    else:
        print(format_text(report))

    return 0


if __name__ == "__main__":
    sys.exit(main())
