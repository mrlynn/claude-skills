#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Analyze markdown files to recommend RAG chunk sizes.

  For each markdown file in a directory: counts words, characters,
  sections (## headings), and estimates tokens. Recommends chunk_size
  and chunk_overlap based on content density for the RAG ingestion
  pipeline.
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List

HEADING_RE = re.compile(r"^#{1,6}\s+", re.MULTILINE)
H2_RE = re.compile(r"^##\s+", re.MULTILINE)
CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)


def analyze_file(filepath: str) -> Dict[str, object]:
    """Analyze a single markdown file for content metrics."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
        content = fh.read()

    chars = len(content)
    words = len(content.split())
    lines = content.count("\n") + 1
    sections = len(H2_RE.findall(content))
    headings = len(HEADING_RE.findall(content))
    code_blocks = len(CODE_BLOCK_RE.findall(content))
    est_tokens = chars // 4  # rough approximation

    # Content density: words per section (higher = denser)
    avg_words_per_section = words / max(sections, 1)

    return {
        "file": filepath,
        "characters": chars,
        "words": words,
        "lines": lines,
        "sections": sections,
        "headings": headings,
        "code_blocks": code_blocks,
        "estimated_tokens": est_tokens,
        "avg_words_per_section": round(avg_words_per_section, 1),
    }


def recommend_chunk_config(analyses: List[Dict[str, object]]) -> Dict[str, object]:
    """Recommend chunk_size and chunk_overlap based on content analysis."""
    if not analyses:
        return {"chunk_size": 512, "chunk_overlap": 50, "reasoning": "No files analyzed; using defaults."}

    total_docs = len(analyses)
    avg_words = sum(a["words"] for a in analyses) / total_docs
    avg_tokens = sum(a["estimated_tokens"] for a in analyses) / total_docs
    avg_sections = sum(a["sections"] for a in analyses) / total_docs
    avg_words_per_section = sum(a["avg_words_per_section"] for a in analyses) / total_docs
    total_code_blocks = sum(a["code_blocks"] for a in analyses)

    # Recommendation logic
    reasoning_parts: List[str] = []

    if avg_words_per_section > 500:
        chunk_size = 1024
        reasoning_parts.append("Dense sections (>500 words/section) favor larger chunks.")
    elif avg_words_per_section > 200:
        chunk_size = 512
        reasoning_parts.append("Moderate density (200-500 words/section) suits standard chunks.")
    else:
        chunk_size = 256
        reasoning_parts.append("Short sections (<200 words/section) favor smaller chunks.")

    if total_code_blocks / max(total_docs, 1) > 3:
        chunk_size = max(chunk_size, 512)
        reasoning_parts.append("Code-heavy content benefits from larger chunks to preserve context.")

    if avg_tokens < 200:
        chunk_size = min(chunk_size, 256)
        reasoning_parts.append("Small documents suggest smaller chunk sizes.")

    # Overlap: 10-15% of chunk size
    chunk_overlap = max(50, chunk_size // 8)
    reasoning_parts.append(f"Overlap set to ~{chunk_overlap} chars (~{100*chunk_overlap//chunk_size}% of chunk).")

    return {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "strategy": "markdown" if avg_sections > 2 else "recursive",
        "reasoning": " ".join(reasoning_parts),
    }


def format_text(analyses: List[Dict], recommendation: Dict, directory: str) -> str:
    """Format analysis as human-readable text."""
    lines: List[str] = []
    lines.append("Markdown Content Analysis for RAG")
    lines.append("=" * 50)
    lines.append(f"Directory: {directory}")
    lines.append(f"Files analyzed: {len(analyses)}")
    lines.append("")

    if analyses:
        lines.append(f"{'File':<40} {'Words':>7} {'Tokens':>8} {'Sections':>9} {'Code':>5}")
        lines.append("-" * 72)
        for a in analyses:
            fname = os.path.basename(a["file"])
            if len(fname) > 38:
                fname = fname[:35] + "..."
            lines.append(
                f"{fname:<40} {a['words']:>7,} {a['estimated_tokens']:>8,} "
                f"{a['sections']:>9} {a['code_blocks']:>5}"
            )

        total_words = sum(a["words"] for a in analyses)
        total_tokens = sum(a["estimated_tokens"] for a in analyses)
        lines.append("-" * 72)
        lines.append(f"{'TOTAL':<40} {total_words:>7,} {total_tokens:>8,}")
        lines.append("")

        avg_words = total_words / len(analyses)
        avg_tokens = total_tokens / len(analyses)
        lines.append(f"Avg words/doc:    {avg_words:,.0f}")
        lines.append(f"Avg tokens/doc:   {avg_tokens:,.0f}")
        lines.append("")

    lines.append("Recommendation:")
    lines.append(f"  chunk_size:    {recommendation['chunk_size']}")
    lines.append(f"  chunk_overlap: {recommendation['chunk_overlap']}")
    lines.append(f"  strategy:      {recommendation['strategy']}")
    lines.append(f"  reasoning:     {recommendation['reasoning']}")

    return "\n".join(lines)


def format_json(analyses: List[Dict], recommendation: Dict, directory: str) -> str:
    """Format analysis as JSON."""
    total_words = sum(a["words"] for a in analyses) if analyses else 0
    total_tokens = sum(a["estimated_tokens"] for a in analyses) if analyses else 0
    return json.dumps({
        "tool": "chunk_size_analyzer",
        "directory": directory,
        "files_analyzed": len(analyses),
        "summary": {
            "total_words": total_words,
            "total_tokens": total_tokens,
            "avg_words_per_doc": round(total_words / max(len(analyses), 1), 1),
            "avg_tokens_per_doc": round(total_tokens / max(len(analyses), 1), 1),
        },
        "recommendation": recommendation,
        "files": analyses,
    }, indent=2)


def main() -> int:
    """Entry point for chunk size analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze markdown files to recommend RAG chunk sizes.",
    )
    parser.add_argument(
        "directory",
        help="Directory containing markdown files to analyze",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: directory not found: {args.directory}", file=sys.stderr)
        return 2

    # Collect markdown files
    md_files: List[str] = []
    for root, _dirs, files in os.walk(args.directory):
        for fname in sorted(files):
            if fname.endswith((".md", ".mdx")):
                md_files.append(os.path.join(root, fname))

    if not md_files:
        print(f"No markdown files found in {args.directory}", file=sys.stderr)
        return 0

    analyses = [analyze_file(f) for f in md_files]
    recommendation = recommend_chunk_config(analyses)

    if args.format == "json":
        print(format_json(analyses, recommendation, args.directory))
    else:
        print(format_text(analyses, recommendation, args.directory))

    return 0


if __name__ == "__main__":
    sys.exit(main())
