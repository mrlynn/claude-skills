#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Generate FeedbackFormConfig JSON from a simple YAML-like spec.

  Parses a lightweight spec format into a full FeedbackFormConfig JSON
  document compatible with the MongoDB event platform feedback system.

  Spec format example:
  name: Post-Event Feedback
  slug: post-event-2025
  audience: participant
  ---
  section: Overall Experience
  - How would you rate the event? (rating, required)
  - What did you enjoy most? (long_text)
  ---
  section: Technical
  - Rate the workshop quality (linear_scale, 1-10)
  - Which topics were most useful? (checkbox: React, MongoDB, Node.js)
"""

import argparse
import json
import re
import sys
import uuid
from typing import Any, Dict, List, Optional, Tuple

QUESTION_RE = re.compile(
    r"^-\s+(.+?)\s*"
    r"\("
    r"([a-z_]+)"          # field type
    r"(?:,\s*required)?"  # optional required flag
    r"(?:,\s*(\d+)-(\d+))?"  # optional range (linear_scale)
    r"(?::\s*(.+))?"      # optional options list
    r"\)\s*$"
)

VALID_TYPES = {
    "rating", "long_text", "short_text", "text",
    "linear_scale", "checkbox", "radio", "select",
    "yes_no", "number", "email", "url",
}


def generate_id() -> str:
    """Generate a deterministic short ID from position."""
    # Use a simple counter-based approach for determinism
    if not hasattr(generate_id, "_counter"):
        generate_id._counter = 0
    generate_id._counter += 1
    return f"q{generate_id._counter:03d}"


def parse_spec(content: str) -> Dict[str, Any]:
    """Parse the YAML-like spec into a FeedbackFormConfig dict."""
    # Reset ID counter
    generate_id._counter = 0

    sections_raw = content.split("---")
    if not sections_raw:
        raise ValueError("Spec is empty")

    # Parse header (first block before ---)
    header = sections_raw[0].strip()
    meta: Dict[str, str] = {}
    for line in header.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip()

    name = meta.get("name", "Untitled Form")
    slug = meta.get("slug", name.lower().replace(" ", "-"))
    audience = meta.get("audience", "participant")
    description = meta.get("description", "")

    # Parse sections
    form_sections: List[Dict[str, Any]] = []

    for section_block in sections_raw[1:]:
        section_lines = section_block.strip().splitlines()
        if not section_lines:
            continue

        section_name = "General"
        questions: List[Dict[str, Any]] = []

        for line in section_lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Section header
            if line.lower().startswith("section:"):
                section_name = line.split(":", 1)[1].strip()
                continue

            # Question line
            if line.startswith("-"):
                question = parse_question(line)
                if question:
                    questions.append(question)
                else:
                    print(f"Warning: could not parse question: {line}", file=sys.stderr)

        if questions:
            form_sections.append({
                "id": f"sec_{len(form_sections) + 1:02d}",
                "title": section_name,
                "questions": questions,
            })

    config: Dict[str, Any] = {
        "name": name,
        "slug": slug,
        "audience": audience,
        "status": "draft",
        "sections": form_sections,
    }
    if description:
        config["description"] = description

    return config


def parse_question(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single question line into a question config dict."""
    line = line.strip()
    if not line.startswith("-"):
        return None

    # Remove leading "- "
    text = line[1:].strip()

    # Extract parenthetical spec
    paren_match = re.search(r"\(([^)]+)\)\s*$", text)
    if not paren_match:
        # No type spec, default to short_text
        return {
            "id": generate_id(),
            "text": text,
            "type": "short_text",
            "required": False,
        }

    label = text[:paren_match.start()].strip()
    spec = paren_match.group(1).strip()

    # Parse spec parts
    parts = [p.strip() for p in spec.split(",")]
    field_type_raw = parts[0] if parts else "short_text"

    # Check for options in type (e.g., "checkbox: React, MongoDB")
    options: Optional[List[str]] = None
    if ":" in field_type_raw:
        field_type, _, opts_str = field_type_raw.partition(":")
        field_type = field_type.strip()
        options = [o.strip() for o in opts_str.split(",") if o.strip()]
    else:
        field_type = field_type_raw

    required = "required" in [p.lower() for p in parts[1:]]

    # Parse range (e.g., "1-10")
    min_val: Optional[int] = None
    max_val: Optional[int] = None
    for p in parts[1:]:
        range_match = re.match(r"^(\d+)-(\d+)$", p.strip())
        if range_match:
            min_val = int(range_match.group(1))
            max_val = int(range_match.group(2))

    # Also check remaining parts for options after colon in later parts
    for p in parts[1:]:
        if ":" in p and not re.match(r"^\d+-\d+$", p.strip()):
            extra_key, _, extra_val = p.partition(":")
            # These might be additional options
            pass

    question: Dict[str, Any] = {
        "id": generate_id(),
        "text": label,
        "type": field_type if field_type in VALID_TYPES else "short_text",
        "required": required,
    }

    if options:
        question["options"] = options

    if min_val is not None and max_val is not None:
        question["min"] = min_val
        question["max"] = max_val

    if field_type == "rating" and min_val is None:
        question["min"] = 1
        question["max"] = 5

    return question


def format_text(config: Dict[str, Any]) -> str:
    """Format the config as a readable summary."""
    lines: List[str] = []
    lines.append("Feedback Form Configuration")
    lines.append("=" * 40)
    lines.append(f"Name:     {config['name']}")
    lines.append(f"Slug:     {config['slug']}")
    lines.append(f"Audience: {config['audience']}")
    lines.append(f"Status:   {config['status']}")
    lines.append("")

    total_questions = 0
    for section in config["sections"]:
        lines.append(f"Section: {section['title']}")
        for q in section["questions"]:
            total_questions += 1
            req = " *" if q.get("required") else ""
            extra = ""
            if "options" in q:
                extra = f" [{', '.join(q['options'])}]"
            if "min" in q and "max" in q:
                extra += f" ({q['min']}-{q['max']})"
            lines.append(f"  [{q['type']}]{req} {q['text']}{extra}")
        lines.append("")

    lines.append(f"Total sections: {len(config['sections'])}")
    lines.append(f"Total questions: {total_questions}")
    lines.append("")
    lines.append("JSON output available with --format json")

    return "\n".join(lines)


def format_json(config: Dict[str, Any]) -> str:
    """Format the config as JSON."""
    return json.dumps(config, indent=2)


def main() -> int:
    """Entry point for feedback form generator."""
    parser = argparse.ArgumentParser(
        description="Generate FeedbackFormConfig JSON from a simple spec file.",
    )
    parser.add_argument(
        "spec_file",
        help="Path to the spec file",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Validate the spec and report errors without generating output",
    )
    args = parser.parse_args()

    try:
        with open(args.spec_file, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        print(f"Error: could not read file: {exc}", file=sys.stderr)
        return 2

    try:
        config = parse_spec(content)
    except ValueError as exc:
        print(f"Error: invalid spec: {exc}", file=sys.stderr)
        return 1

    if args.validate:
        total_q = sum(len(s["questions"]) for s in config["sections"])
        print(f"Valid spec: {len(config['sections'])} sections, {total_q} questions")
        return 0

    if args.format == "json":
        print(format_json(config))
    else:
        print(format_text(config))

    return 0


if __name__ == "__main__":
    sys.exit(main())
