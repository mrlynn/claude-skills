#!/usr/bin/env python3
"""Validate CSS/TS/TSX files against the MongoDB brand color palette.

Scans source files for hex color codes and flags any that do not match
the approved MongoDB brand palette. Reports unknown colors with file
paths and line numbers.
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Set, Tuple

# MongoDB brand palette (canonical uppercase hex)
MONGODB_PALETTE: Set[str] = {
    # Primary brand colors
    "#00ED64",  # Spring Green
    "#00684A",  # Forest Green
    "#023430",  # Evergreen
    "#001E2B",  # Slate Blue
    "#006EFF",  # Blue
    "#B45AF2",  # Purple
    "#FFC010",  # Warning Yellow
    "#CF4520",  # Error Red
    # Gray scale
    "#F9FBFA",
    "#E7EEEC",
    "#C1CCC6",
    "#889397",
    "#5C6C75",
    "#3D4F58",
    "#1C2D38",
    "#FFFFFF",
    "#0F2235",
    "#000000",
    # Common shorthand equivalents
    "#FFF",
    "#000",
}

# CSS keywords that are not hex colors but are valid color values
CSS_KEYWORDS: Set[str] = {
    "transparent", "inherit", "initial", "unset", "currentcolor",
    "currentColor", "none", "revert", "revert-layer",
}

# Regex matching 3, 4, 6, or 8 digit hex color codes
HEX_COLOR_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")

VALID_EXTENSIONS = {".css", ".ts", ".tsx", ".scss", ".less"}


def normalize_hex(color: str) -> str:
    """Normalize a hex color to uppercase 6-digit form for comparison."""
    c = color.upper()
    # Strip alpha from 8-digit hex (compare base color only)
    if len(c) == 9:  # #RRGGBBAA
        c = c[:7]
    # Expand 3-digit shorthand
    if len(c) == 4:  # #RGB
        c = "#" + c[1]*2 + c[2]*2 + c[3]*2
    # Strip alpha from 4-digit hex
    if len(c) == 5:  # #RGBA
        c = "#" + c[1]*2 + c[2]*2 + c[3]*2
    return c


def scan_file(filepath: str) -> List[Dict[str, object]]:
    """Scan a single file for non-palette hex colors.

    Returns a list of violation dicts with keys: file, line, column, color, normalized.
    """
    violations: List[Dict[str, object]] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            for lineno, line in enumerate(fh, start=1):
                for match in HEX_COLOR_RE.finditer(line):
                    raw = match.group(0)
                    norm = normalize_hex(raw)
                    if raw.upper() not in MONGODB_PALETTE and norm not in MONGODB_PALETTE:
                        violations.append({
                            "file": filepath,
                            "line": lineno,
                            "column": match.start() + 1,
                            "color": raw,
                            "normalized": norm,
                        })
    except OSError as exc:
        print(f"Warning: could not read {filepath}: {exc}", file=sys.stderr)
    return violations


def collect_files(paths: List[str], extensions: Set[str]) -> List[str]:
    """Recursively collect files with matching extensions from paths."""
    result: List[str] = []
    for p in paths:
        if os.path.isfile(p):
            result.append(p)
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for fname in sorted(files):
                    if os.path.splitext(fname)[1] in extensions:
                        result.append(os.path.join(root, fname))
    return result


def format_text(violations: List[Dict[str, object]], total_files: int) -> str:
    """Format violations as human-readable text."""
    lines: List[str] = []
    lines.append(f"MongoDB Brand Color Check")
    lines.append(f"{'=' * 40}")
    lines.append(f"Files scanned: {total_files}")
    lines.append(f"Violations found: {len(violations)}")
    lines.append("")
    if not violations:
        lines.append("All colors match the MongoDB brand palette.")
    else:
        current_file = ""
        for v in violations:
            if v["file"] != current_file:
                current_file = v["file"]
                lines.append(f"--- {current_file} ---")
            lines.append(
                f"  Line {v['line']:>4}, Col {v['column']:>3}: "
                f"{v['color']} (normalized: {v['normalized']})"
            )
        lines.append("")
        lines.append("Approved palette colors:")
        for c in sorted(MONGODB_PALETTE):
            if len(c) == 7:
                lines.append(f"  {c}")
    return "\n".join(lines)


def format_json(violations: List[Dict[str, object]], total_files: int) -> str:
    """Format violations as JSON."""
    return json.dumps({
        "tool": "brand_color_checker",
        "files_scanned": total_files,
        "violation_count": len(violations),
        "violations": violations,
        "palette": sorted(MONGODB_PALETTE),
    }, indent=2)


def main() -> int:
    """Entry point for brand color checker."""
    parser = argparse.ArgumentParser(
        description="Validate files against the MongoDB brand color palette.",
    )
    parser.add_argument(
        "paths", nargs="+",
        help="Files or directories to scan",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--extensions", default=".css,.ts,.tsx,.scss,.less",
        help="Comma-separated file extensions to scan (default: .css,.ts,.tsx,.scss,.less)",
    )
    args = parser.parse_args()

    extensions = {e.strip() if e.startswith(".") else f".{e.strip()}" for e in args.extensions.split(",")}
    files = collect_files(args.paths, extensions)
    all_violations: List[Dict[str, object]] = []
    for f in files:
        all_violations.extend(scan_file(f))

    if args.format == "json":
        print(format_json(all_violations, len(files)))
    else:
        print(format_text(all_violations, len(files)))

    return 1 if all_violations else 0


if __name__ == "__main__":
    sys.exit(main())
