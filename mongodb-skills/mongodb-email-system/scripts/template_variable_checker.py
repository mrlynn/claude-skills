#!/usr/bin/env python3
"""Parse email template files and report on template variable usage.

Scans HTML and TypeScript files for {{variable}} and {{#if variable}}
patterns. Reports variables found per template and flags potential
issues such as variables referenced in conditional blocks but never
defined elsewhere.
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Set, Tuple

# Patterns for Handlebars-style template variables
VAR_RE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_.]*)\s*\}\}")
IF_RE = re.compile(r"\{\{\s*#if\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*\}\}")
EACH_RE = re.compile(r"\{\{\s*#each\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*\}\}")
HELPER_RE = re.compile(r"\{\{\s*([a-zA-Z_]+)\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*\}\}")

TEMPLATE_EXTENSIONS = {".html", ".ts", ".tsx", ".hbs", ".mjml"}


def scan_template(filepath: str) -> Dict[str, Set[str]]:
    """Scan a template file for variable references.

    Returns dict with keys: variables, conditionals, iterators.
    """
    variables: Set[str] = set()
    conditionals: Set[str] = set()
    iterators: Set[str] = set()

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
    except OSError as exc:
        print(f"Warning: could not read {filepath}: {exc}", file=sys.stderr)
        return {"variables": set(), "conditionals": set(), "iterators": set()}

    for match in VAR_RE.finditer(content):
        variables.add(match.group(1))

    for match in IF_RE.finditer(content):
        conditionals.add(match.group(1))

    for match in EACH_RE.finditer(content):
        iterators.add(match.group(1))

    for match in HELPER_RE.finditer(content):
        helper = match.group(1)
        if helper not in ("if", "each", "unless", "with", "else"):
            variables.add(match.group(2))

    return {
        "variables": variables,
        "conditionals": conditionals,
        "iterators": iterators,
    }


def find_issues(
    variables: Set[str],
    conditionals: Set[str],
    iterators: Set[str],
) -> List[str]:
    """Identify potential issues with template variables."""
    issues: List[str] = []

    # Conditionals referencing vars not used elsewhere
    for cond in sorted(conditionals):
        if cond not in variables:
            issues.append(
                f"Variable '{cond}' used in #if block but never rendered directly"
            )

    # Iterators referencing vars not used elsewhere
    for it in sorted(iterators):
        if it not in variables:
            issues.append(
                f"Variable '{it}' used in #each block but never rendered directly"
            )

    return issues


def collect_templates(directory: str) -> List[str]:
    """Recursively collect template files from a directory."""
    templates: List[str] = []
    for root, _dirs, files in os.walk(directory):
        for fname in sorted(files):
            if os.path.splitext(fname)[1] in TEMPLATE_EXTENSIONS:
                templates.append(os.path.join(root, fname))
    return templates


def format_text(results: List[Dict], directory: str) -> str:
    """Format results as human-readable text."""
    lines: List[str] = []
    lines.append("Email Template Variable Report")
    lines.append("=" * 40)
    lines.append(f"Directory: {directory}")
    lines.append(f"Templates scanned: {len(results)}")
    lines.append("")

    total_vars = 0
    total_issues = 0

    for r in results:
        lines.append(f"--- {r['file']} ---")
        all_vars = sorted(r["variables"])
        conds = sorted(r["conditionals"])
        iters = sorted(r["iterators"])
        total_vars += len(all_vars)

        if all_vars:
            lines.append(f"  Variables ({len(all_vars)}): {', '.join(all_vars)}")
        if conds:
            lines.append(f"  Conditionals ({len(conds)}): {', '.join(conds)}")
        if iters:
            lines.append(f"  Iterators ({len(iters)}): {', '.join(iters)}")

        if r["issues"]:
            total_issues += len(r["issues"])
            for issue in r["issues"]:
                lines.append(f"  WARNING: {issue}")

        if not all_vars and not conds and not iters:
            lines.append("  No template variables found.")
        lines.append("")

    lines.append(f"Total unique variables: {total_vars}")
    lines.append(f"Total issues: {total_issues}")

    return "\n".join(lines)


def format_json(results: List[Dict], directory: str) -> str:
    """Format results as JSON."""
    total_issues = sum(len(r["issues"]) for r in results)
    return json.dumps({
        "tool": "template_variable_checker",
        "directory": directory,
        "templates_scanned": len(results),
        "total_issues": total_issues,
        "templates": results,
    }, indent=2)


def main() -> int:
    """Entry point for template variable checker."""
    parser = argparse.ArgumentParser(
        description="Scan email templates for variable usage and potential issues.",
    )
    parser.add_argument(
        "directory",
        help="Directory containing email template files",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: directory not found: {args.directory}", file=sys.stderr)
        return 2

    templates = collect_templates(args.directory)
    if not templates:
        print(f"No template files found in {args.directory}", file=sys.stderr)
        return 0

    results: List[Dict] = []
    for tpl in templates:
        scan = scan_template(tpl)
        issues = find_issues(scan["variables"], scan["conditionals"], scan["iterators"])
        results.append({
            "file": tpl,
            "variables": sorted(scan["variables"]),
            "conditionals": sorted(scan["conditionals"]),
            "iterators": sorted(scan["iterators"]),
            "issues": issues,
        })

    if args.format == "json":
        print(format_json(results, args.directory))
    else:
        print(format_text(results, args.directory))

    total_issues = sum(len(r["issues"]) for r in results)
    return 1 if total_issues > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
