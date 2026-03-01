# MongoDB DevRel Skills for Claude Code

Reusable Claude Code skills extracted from battle-tested patterns in the MongoDB Hackathon Platform. Each skill follows Claude Code best practices: `SKILL.md` with YAML frontmatter, Python CLI tools, reference documentation, and sample assets.

## Quick Install

As a Claude Code plugin:
```bash
# From your project directory
claude plugin add /path/to/mongodb-skills
```

Or add individual skills to your project's `.claude/settings.local.json`:
```json
{
  "skills": [
    {
      "name": "mongodb-nextjs-scaffold",
      "description": "Bootstrap a Next.js + MongoDB + Auth + MUI project with MongoDB branding",
      "path": "/Users/michael.lynn/code/claude-skills/mongodb-skills/mongodb-nextjs-scaffold/SKILL.md"
    }
  ]
}
```

## Skills Catalog

| Skill | Purpose | Python Tools | Use When... |
|-------|---------|--------------|-------------|
| `mongodb-nextjs-scaffold` | Project bootstrap | `brand_color_checker.py`, `env_checker.py` | Starting a new Next.js + MongoDB project |
| `mongodb-rbac-middleware` | Auth & access control | `role_matrix_generator.py` | Adding authentication and role-based protection |
| `mongodb-email-system` | Templated email | `template_variable_checker.py` | Adding transactional email to any app |
| `mongodb-atlas-provisioning` | Self-service Atlas | `atlas_cost_estimator.py` | Building programmatic Atlas cluster management |
| `mongodb-ai-features` | AI integration + RAG | `embedding_cost_estimator.py`, `chunk_size_analyzer.py` | Adding summarization, generation, or RAG pipelines |
| `mongodb-event-platform` | Event lifecycle | `feedback_form_generator.py` | Building event/hackathon/workshop management |
| `mongodb-partner-portal` | Partner management | `tier_report_generator.py` | Adding partner tiers, contacts, engagement tracking |
| `mongodb-devrel-advisor` | Conventions advisor | — | Always-on guidance for MongoDB DevRel patterns |

## Skill Structure

Each skill follows Claude Code best practices:

```
mongodb-<skill-name>/
├── SKILL.md              # Main skill (YAML frontmatter + instructions)
├── scripts/              # Python CLI tools (standard library only)
├── references/           # Detailed knowledge base documents
└── assets/               # Templates, sample data, starter files
```

## Python Tools

All tools use Python 3.7+ standard library only. No external dependencies.

```bash
# Validate theme colors against MongoDB brand palette
python mongodb-nextjs-scaffold/scripts/brand_color_checker.py src/styles/theme.ts

# Check .env has all required variables
python mongodb-nextjs-scaffold/scripts/env_checker.py .env --skills scaffold,email,ai

# Generate role-permission matrix
python mongodb-rbac-middleware/scripts/role_matrix_generator.py --format markdown

# Estimate Atlas cluster costs
python mongodb-atlas-provisioning/scripts/atlas_cost_estimator.py --tier M10 --provider AWS --clusters 50

# Estimate embedding costs for RAG pipeline
python mongodb-ai-features/scripts/embedding_cost_estimator.py --docs 1000 --queries-per-month 5000

# Analyze docs for optimal chunk sizing
python mongodb-ai-features/scripts/chunk_size_analyzer.py docs/

# Generate feedback form from YAML spec
python mongodb-event-platform/scripts/feedback_form_generator.py spec.yaml --format json

# Generate partner engagement report
python mongodb-partner-portal/scripts/tier_report_generator.py partners.json
```

## Dependencies Between Skills

Skills are designed to be composable. Later skills build on patterns from earlier ones:

```
mongodb-nextjs-scaffold (foundation)
  ├── mongodb-rbac-middleware (adds auth layer)
  ├── mongodb-email-system (adds email)
  ├── mongodb-ai-features (adds AI/RAG)
  └── mongodb-atlas-provisioning (adds Atlas API)
        │
mongodb-event-platform (combines scaffold + RBAC + email + optionally AI/Atlas)
mongodb-partner-portal (combines scaffold + RBAC + email)
mongodb-devrel-advisor (references all skills)
```

## Origin

Extracted from the [MongoDB Hackathon Platform](https://github.com/mongohacks/hackathon-platform) — a production Next.js 16 application with 26 Mongoose models, 8 user roles, and comprehensive admin tooling.
