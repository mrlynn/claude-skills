# AI Agent Skills by Michael Lynn

Production-ready skill packages for AI coding agents. Built from real-world applications.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 17](https://img.shields.io/badge/Skills-17-brightgreen.svg)](#skill-collections)
[![Python Tools: 37](https://img.shields.io/badge/Python_Tools-37-blue.svg)](#skill-collections)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-purple.svg)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
[![OpenAI Codex](https://img.shields.io/badge/Codex-Compatible-green.svg)](https://openai.com/codex)

---

## What This Is

A curated collection of **AI agent skill packages** — structured knowledge bundles that give coding assistants deep expertise in specific domains. Each skill contains battle-tested patterns, CLI tools, and reference documentation extracted from production applications and 10+ years of field experience.

Skills follow the open `SKILL.md` specification: YAML frontmatter for metadata, markdown for instructions, and optional Python tools for automation. This format is natively supported by Claude Code and adaptable to any AI agent platform.

## Skill Collections

### [MongoDB DevRel Skills](mongodb-skills/) (8 skills)

Skills for building Next.js + MongoDB applications following MongoDB Developer Relations conventions.

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

**Origin:** Extracted from the [MongoDB Hackathon Platform](https://github.com/mrlynn/mongohacks).

### Professional Skills Collection (9 skills)

General-purpose skills for technical work, developer relations, and professional development.

| Skill | Purpose | Tools |
|-------|---------|-------|
| **[rag-pipeline-builder](rag-pipeline-builder/)** | Build RAG systems with Voyage AI embeddings | `chunking_strategy_analyzer.py`, `cost_estimator.py`, `ingestion_test_harness.py` |
| **[resume-tailorer](resume-tailorer/)** | ATS-optimize resumes for job postings | `job_analyzer.py`, `resume_matcher.py`, `ats_optimizer.py` |
| **[developer-day-curriculum](developer-day-curriculum/)** | Design workshop agendas and exercises | `audience_analyzer.py`, `agenda_generator.py`, `exercise_scaffolder.py` |
| **[mcp-server-scaffold](mcp-server-scaffold/)** | Generate MCP tool servers from OpenAPI specs | `openapi_parser.py`, `mcp_generator.py`, `server_tester.py` |
| **[document-model-advisor](document-model-advisor/)** | MongoDB schema design (embed vs reference) | `relationship_analyzer.py`, `schema_optimizer.py`, `migration_planner.py` |
| **[conference-talk-builder](conference-talk-builder/)** | Create CFPs and talk outlines | `cfp_generator.py`, `outline_builder.py`, `slide_estimator.py` |
| **[queryable-encryption-workshop](queryable-encryption-workshop/)** | Industry-specific QE demos with compliance mapping | `vertical_analyzer.py`, `demo_generator.py`, `compliance_mapper.py` |
| **[technical-comparison-generator](technical-comparison-generator/)** | Fair MongoDB vs competitor comparisons | `feature_analyzer.py`, `comparison_generator.py`, `use_case_matcher.py` |
| **[hackathon-judge-assistant](hackathon-judge-assistant/)** | Scoring rubrics and constructive feedback | `rubric_generator.py`, `submission_scorer.py`, `feedback_generator.py` |

**Origin:** Patterns from 10+ years MongoDB field work, 50+ workshops, 100+ schema reviews, hackathon judging.

## Quick Start

### Claude Code

```bash
# Install individual skill
claude skill add /path/to/rag-pipeline-builder

# Or reference in .claude/settings.local.json
```

### Other AI Agents

Each skill is self-contained with a `SKILL.md` entry point. Point your agent at any skill directory:

```
rag-pipeline-builder/SKILL.md
document-model-advisor/SKILL.md
...
```

Pre-packaged ZIP files available in `dist/` (see below).

## Skill Anatomy

Every skill follows a consistent structure:

```
<skill-name>/
├── SKILL.md              # Entry point: YAML frontmatter + instructions
├── README.md             # Quick start guide
├── scripts/              # Python CLI tools (standard library only)
│   ├── tool1.py
│   ├── tool2.py
│   └── tool3.py
├── references/           # Detailed knowledge base documents
│   ├── patterns.md
│   └── best-practices.md
└── assets/               # Templates, sample data, starter files
    ├── template1.json
    └── template2.md
```

**Design principles:**

- **Real code, not pseudocode** — patterns extracted from production
- **Architecture decisions documented** — explains WHY, not just WHAT
- **Zero external dependencies** — Python tools use standard library only
- **Self-contained** — each skill works independently
- **Deterministic tools** — no LLM/API calls; pure local computation

## Distribution

### Individual Skills (ZIP)

Each skill is packaged as a standalone ZIP in `dist/`:

```
dist/
├── rag-pipeline-builder.zip
├── resume-tailorer.zip
├── developer-day-curriculum.zip
├── mcp-server-scaffold.zip
├── document-model-advisor.zip
├── conference-talk-builder.zip
├── queryable-encryption-workshop.zip
├── technical-comparison-generator.zip
└── hackathon-judge-assistant.zip
```

### Collections (ZIP)

```
dist/
├── mongodb-skills-all.zip           # All 8 MongoDB skills
└── professional-skills-all.zip      # All 9 professional skills
```

## Agent Compatibility

| Platform | Status | Install Method |
|----------|--------|----------------|
| Claude Code | ✅ Native | `claude skill add` or `.claude/settings.local.json` |
| OpenAI Codex | ✅ Compatible | Copy `SKILL.md` to `.codex/skills/` |
| Cursor | ✅ Compatible | Reference in rules or context |
| Windsurf | ✅ Compatible | Reference in rules or context |
| Aider | ✅ Compatible | Load as context files |
| Custom agents | ✅ Compatible | Load `SKILL.md` as system context |

The `SKILL.md` format is plain markdown with YAML frontmatter. Any agent that accepts markdown context can use these skills.

## Skill Statistics

| Metric | MongoDB Skills | Professional Skills | Total |
|--------|----------------|---------------------|-------|
| **Skills** | 8 | 9 | **17** |
| **Python Tools** | 10 | 27 | **37** |
| **Reference Docs** | 13 | 18 | **31** |
| **Asset Templates** | varies | 21 | **21+** |
| **Total Files** | varies | 90 | **90+** |

## Use Cases

### For AI Agents
- Deep domain expertise on demand
- Battle-tested patterns and architectures
- Consistent structure for reliable outputs
- Zero external dependencies (all local)

### For Developers
- Reference implementations
- CLI tools for automation
- Architecture decision documentation
- Copy-paste ready templates

### For Teams
- Shared knowledge base
- Consistent conventions
- Onboarding materials
- Code review checklists

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new skills, improving existing ones, or reporting issues.

## Security

See [SECURITY.md](SECURITY.md) for our vulnerability reporting policy and security best practices.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

**Michael Lynn** — Principal Staff Developer Advocate, MongoDB

- 10+ years MongoDB field experience
- 50+ workshops delivered (MongoDB World, AWS re:Invent, customer developer days)
- 100+ schema design reviews
- MongoDB Podcast co-host
- GitHub: [@mrlynn](https://github.com/mrlynn)
- Twitter: [@mlynn](https://twitter.com/mlynn)

---

**Built with real-world experience. Tested in production. Ready for your AI agent.**
