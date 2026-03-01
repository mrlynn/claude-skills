#!/usr/bin/env python3
"""Generate a role-permission matrix for MongoDB RBAC middleware.

Takes a JSON config file with routes and allowed roles, or uses built-in
defaults. Outputs a markdown table or JSON showing which roles can
access which routes.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Set

# Built-in default route-role configuration
DEFAULT_CONFIG: Dict[str, List[str]] = {
    "/admin/*": ["super_admin", "admin", "organizer", "marketer"],
    "/admin/users": ["super_admin", "admin"],
    "/admin/settings": ["super_admin", "admin"],
    "/judging/*": ["super_admin", "admin", "organizer", "judge"],
    "/partner/*": ["super_admin", "admin", "partner"],
    "/dashboard": [
        "super_admin", "admin", "organizer", "judge",
        "partner", "marketer", "participant",
    ],
}

ALL_ROLES_ORDERED = [
    "super_admin", "admin", "organizer", "judge",
    "partner", "marketer", "participant",
]


def load_config(filepath: str) -> Dict[str, List[str]]:
    """Load route-role config from a JSON file.

    Expected format: { "/route": ["role1", "role2"], ... }
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Config must be a JSON object mapping routes to role arrays")
    for route, roles in data.items():
        if not isinstance(roles, list):
            raise ValueError(f"Roles for route '{route}' must be an array")
    return data


def discover_roles(config: Dict[str, List[str]]) -> List[str]:
    """Discover all roles from config, preserving a canonical order."""
    seen: Set[str] = set()
    ordered: List[str] = []
    # Start with canonical order
    for role in ALL_ROLES_ORDERED:
        for roles in config.values():
            if role in roles and role not in seen:
                seen.add(role)
                ordered.append(role)
    # Add any extras not in canonical list
    for roles in config.values():
        for role in roles:
            if role not in seen:
                seen.add(role)
                ordered.append(role)
    return ordered


def format_markdown(config: Dict[str, List[str]], roles: List[str]) -> str:
    """Format the matrix as a markdown table."""
    lines: List[str] = []
    lines.append("# Role-Permission Matrix")
    lines.append("")

    # Header
    header = "| Route | " + " | ".join(roles) + " |"
    separator = "|" + "---|" * (len(roles) + 1)
    lines.append(header)
    lines.append(separator)

    # Rows
    for route in sorted(config.keys()):
        allowed = set(config[route])
        cells = []
        for role in roles:
            cells.append(" Y " if role in allowed else " - ")
        lines.append(f"| `{route}` | " + " | ".join(cells) + " |")

    lines.append("")
    lines.append(f"**Legend:** Y = allowed, - = denied")
    lines.append(f"**Total routes:** {len(config)}")
    lines.append(f"**Total roles:** {len(roles)}")

    return "\n".join(lines)


def format_text(config: Dict[str, List[str]], roles: List[str]) -> str:
    """Format the matrix as aligned text."""
    lines: List[str] = []
    lines.append("Role-Permission Matrix")
    lines.append("=" * 40)
    lines.append("")

    route_width = max(len(r) for r in config.keys()) + 2
    role_width = max(len(r) for r in roles) + 1

    # Header
    header = "Route".ljust(route_width) + "".join(r.ljust(role_width) for r in roles)
    lines.append(header)
    lines.append("-" * len(header))

    for route in sorted(config.keys()):
        allowed = set(config[route])
        cells = []
        for role in roles:
            mark = "Y" if role in allowed else "-"
            cells.append(mark.ljust(role_width))
        lines.append(route.ljust(route_width) + "".join(cells))

    lines.append("")
    lines.append(f"Total routes: {len(config)}")
    lines.append(f"Total roles: {len(roles)}")

    return "\n".join(lines)


def format_json_output(config: Dict[str, List[str]], roles: List[str]) -> str:
    """Format the matrix as JSON."""
    matrix: Dict[str, Dict[str, bool]] = {}
    for route in sorted(config.keys()):
        allowed = set(config[route])
        matrix[route] = {role: role in allowed for role in roles}

    return json.dumps({
        "tool": "role_matrix_generator",
        "roles": roles,
        "routes": sorted(config.keys()),
        "matrix": matrix,
        "summary": {
            "total_routes": len(config),
            "total_roles": len(roles),
        },
    }, indent=2)


def main() -> int:
    """Entry point for role matrix generator."""
    parser = argparse.ArgumentParser(
        description="Generate a role-permission matrix for RBAC routes.",
    )
    parser.add_argument(
        "--config", default=None,
        help="Path to JSON config file (uses built-in defaults if omitted)",
    )
    parser.add_argument(
        "--format", choices=["text", "json", "markdown"], default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    if args.config:
        if not os.path.isfile(args.config):
            print(f"Error: config file not found: {args.config}", file=sys.stderr)
            return 2
        try:
            config = load_config(args.config)
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"Error: invalid config: {exc}", file=sys.stderr)
            return 2
    else:
        config = DEFAULT_CONFIG

    roles = discover_roles(config)

    if args.format == "json":
        print(format_json_output(config, roles))
    elif args.format == "markdown":
        print(format_markdown(config, roles))
    else:
        print(format_text(config, roles))

    return 0


if __name__ == "__main__":
    sys.exit(main())
