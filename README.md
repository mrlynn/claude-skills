# AI Agent Skills by Michael Lynn

Production-ready skill packages for AI coding agents. Built from real-world applications.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 8+](https://img.shields.io/badge/Skills-8%2B-brightgreen.svg)](#skill-collections)
[![Python Tools: 10+](https://img.shields.io/badge/Python_Tools-10%2B-blue.svg)](#skill-collections)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-purple.svg)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
[![OpenAI Codex](https://img.shields.io/badge/Codex-Compatible-green.svg)](https://openai.com/codex)

---

## What This Is

A curated collection of **AI agent skill packages** — structured knowledge bundles that give coding assistants deep expertise in specific domains. Each skill contains battle-tested patterns, CLI tools, and reference documentation extracted from production applications.

Skills follow the open `SKILL.md` specification: YAML frontmatter for metadata, markdown for instructions, and optional Python tools for automation. This format is natively supported by Claude Code and adaptable to any AI agent platform.

## Skill Collections

### [MongoDB DevRel Skills](mongodb-skills/)

8 skills for building Next.js + MongoDB applications following MongoDB Developer Relations conventions.

| Skill | Purpose | Tools |
|-------|---------|-------|
| `mongodb-nextjs-scaffold` | Project bootstrap with MongoDB branding | `brand_color_checker.py`, `env_checker.py` |
| `mongodb-rbac-middleware` | NextAuth v5 + 8-role RBAC + edge middleware | `role_matrix_generator.py` |
| `mongodb-email-system` | DB-backed transactional email templates | `template_variable_checker.py` |
| `mongodb-atlas-provisioning` | Self-service Atlas cluster management | `atlas_cost_estimator.py` |
| `mongodb-ai-features` | AI/RAG integration with MongoDB Atlas | `embedding_cost_estimator.py`, `chunk_size_analyzer.py` |
| `mongodb-event-platform` | Event/hackathon lifecycle management | `feedback_form_generator.py` |
| `mongodb-partner-portal` | Partner tiers, contacts, engagement tracking | `tier_report_generator.py` |
| `mongodb-devrel-advisor` | Always-on conventions and architecture advisor | &mdash; |

**Origin:** Extracted from the [MongoDB Hackathon Platform](https://github.com/mrlynn/mongohacks) — a production Next.js 16 app with 26 Mongoose models and 8 user roles.

## Quick Start

### Claude Code

```bash
# Install the full MongoDB skills collection
claude plugin add /path/to/mongodb-skills

# Or reference individual skills in .claude/settings.local.json
```

### Other AI Agents

Each skill is a self-contained directory with a `SKILL.md` entry point. Point your agent's skill loader at any skill directory, or copy the `SKILL.md` into your agent's context:

```
mongodb-skills/mongodb-nextjs-scaffold/SKILL.md
mongodb-skills/mongodb-rbac-middleware/SKILL.md
...
```

Pre-packaged ZIP files for individual skills and the full collection are available in [`mongodb-skills/dist/`](mongodb-skills/dist/).

## Skill Anatomy

Every skill follows a consistent structure:

```
<skill-name>/
├── SKILL.md              # Entry point: YAML frontmatter + instructions
├── scripts/              # Python CLI tools (standard library only)
├── references/           # Detailed knowledge base documents
└── assets/               # Templates, sample data, starter files
```

**Design principles:**

- **Real code, not pseudocode** — patterns extracted from production applications
- **Architecture decisions documented** — explains WHY, not just WHAT
- **Zero external dependencies** — Python tools use standard library only
- **Self-contained** — each skill works independently; dependencies are noted, not required
- **Deterministic tools** — no LLM/API calls in scripts; pure local computation

## Agent Compatibility

| Platform | Status | Install Method |
|----------|--------|----------------|
| Claude Code | Native | `claude plugin add` or `.claude/settings.local.json` |
| OpenAI Codex | Compatible | Copy `SKILL.md` to `.codex/skills/` |
| Cursor | Compatible | Reference in rules or context |
| Windsurf | Compatible | Reference in rules or context |
| Custom agents | Compatible | Load `SKILL.md` as system context |

The `SKILL.md` format is plain markdown with YAML frontmatter. Any agent that accepts markdown context can use these skills.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new skills, improving existing ones, or reporting issues.

## Security

See [SECURITY.md](SECURITY.md) for our vulnerability reporting policy and security best practices.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

**Michael Lynn** — Developer Advocate, MongoDB

- GitHub: [@mrlynn](https://github.com/mrlynn)
- Twitter: [@mlynn](https://twitter.com/mlynn)
