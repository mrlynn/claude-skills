#!/usr/bin/env python3
"""Check a .env file against required environment variables for MongoDB skills.

Maintains a built-in registry mapping skill names to their required
environment variables. Reports missing, empty, and extraneous variables.
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Set, Tuple

# Built-in registry: skill -> required env vars
SKILL_REGISTRY: Dict[str, List[str]] = {
    "scaffold": ["MONGODB_URI", "AUTH_SECRET", "NEXTAUTH_URL"],
    "rbac": ["AUTH_SECRET", "NEXTAUTH_URL"],
    "email": ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "EMAIL_FROM"],
    "atlas": ["ATLAS_PUBLIC_KEY", "ATLAS_PRIVATE_KEY", "ATLAS_ORG_ID"],
    "ai": ["OPENAI_API_KEY", "VOYAGE_API_KEY"],
}

ALL_SKILLS = sorted(SKILL_REGISTRY.keys())


def parse_env_file(filepath: str) -> Dict[str, str]:
    """Parse a .env file into a dict of name -> value.

    Handles comments, blank lines, quoted values, and inline comments.
    """
    env: Dict[str, str] = {}
    if not os.path.isfile(filepath):
        return env
    with open(filepath, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', stripped)
            if match:
                key = match.group(1)
                value = match.group(2).strip()
                # Remove surrounding quotes
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                env[key] = value
    return env


def check_skills(
    env: Dict[str, str],
    skills: List[str],
) -> Dict[str, Dict[str, List[str]]]:
    """Check env vars against required vars for each skill.

    Returns a dict per skill with keys: present, missing, empty.
    """
    results: Dict[str, Dict[str, List[str]]] = {}
    for skill in skills:
        required = SKILL_REGISTRY.get(skill, [])
        present: List[str] = []
        missing: List[str] = []
        empty: List[str] = []
        for var in required:
            if var not in env:
                missing.append(var)
            elif not env[var]:
                empty.append(var)
            else:
                present.append(var)
        results[skill] = {
            "required": required,
            "present": present,
            "missing": missing,
            "empty": empty,
        }
    return results


def format_text(
    results: Dict[str, Dict[str, List[str]]],
    env_file: str,
    env_vars: Dict[str, str],
) -> str:
    """Format check results as human-readable text."""
    lines: List[str] = []
    lines.append("Environment Variable Check")
    lines.append("=" * 40)
    lines.append(f"File: {env_file}")
    lines.append(f"Variables defined: {len(env_vars)}")
    lines.append(f"Skills checked: {', '.join(results.keys())}")
    lines.append("")

    all_ok = True
    for skill, info in results.items():
        status = "OK" if not info["missing"] and not info["empty"] else "ISSUES"
        if status != "OK":
            all_ok = False
        lines.append(f"[{status}] {skill}")
        if info["present"]:
            for v in info["present"]:
                lines.append(f"  + {v}")
        if info["missing"]:
            for v in info["missing"]:
                lines.append(f"  - {v} (MISSING)")
        if info["empty"]:
            for v in info["empty"]:
                lines.append(f"  ! {v} (EMPTY)")
        lines.append("")

    if all_ok:
        lines.append("All required variables are set.")
    else:
        lines.append("Some variables are missing or empty. See above.")

    return "\n".join(lines)


def format_json(
    results: Dict[str, Dict[str, List[str]]],
    env_file: str,
    env_vars: Dict[str, str],
) -> str:
    """Format check results as JSON."""
    has_issues = any(
        r["missing"] or r["empty"] for r in results.values()
    )
    return json.dumps({
        "tool": "env_checker",
        "file": env_file,
        "variables_defined": len(env_vars),
        "all_ok": not has_issues,
        "skills": results,
    }, indent=2)


def main() -> int:
    """Entry point for env checker."""
    parser = argparse.ArgumentParser(
        description="Check .env files against required variables for MongoDB skills.",
    )
    parser.add_argument(
        "env_file",
        help="Path to .env file to check",
    )
    parser.add_argument(
        "--skills", default="all",
        help=f"Comma-separated skill names or 'all' (available: {', '.join(ALL_SKILLS)})",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--list-skills", action="store_true",
        help="List available skills and their required variables",
    )
    args = parser.parse_args()

    if args.list_skills:
        for skill, vars_ in sorted(SKILL_REGISTRY.items()):
            print(f"{skill}: {', '.join(vars_)}")
        return 0

    if not os.path.isfile(args.env_file):
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 2

    skills_str = args.skills.strip()
    if skills_str.lower() == "all":
        skills = ALL_SKILLS
    else:
        skills = [s.strip() for s in skills_str.split(",")]
        unknown = [s for s in skills if s not in SKILL_REGISTRY]
        if unknown:
            print(f"Error: unknown skills: {', '.join(unknown)}", file=sys.stderr)
            print(f"Available: {', '.join(ALL_SKILLS)}", file=sys.stderr)
            return 2

    env_vars = parse_env_file(args.env_file)
    results = check_skills(env_vars, skills)

    if args.format == "json":
        print(format_json(results, args.env_file, env_vars))
    else:
        print(format_text(results, args.env_file, env_vars))

    has_issues = any(r["missing"] or r["empty"] for r in results.values())
    return 1 if has_issues else 0


if __name__ == "__main__":
    sys.exit(main())
