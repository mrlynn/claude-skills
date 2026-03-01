# MongoDB DevRel Skills

## Overview

8 production-ready skills extracted from the MongoDB Hackathon Platform. Each skill provides battle-tested patterns for building Next.js + MongoDB applications following MongoDB DevRel conventions.

## Skills Catalog

| Skill | Description | Python Tools |
|-------|-------------|--------------|
| `mongodb-nextjs-scaffold` | Next.js + MongoDB + Auth + MUI project bootstrap | `brand_color_checker.py`, `env_checker.py` |
| `mongodb-rbac-middleware` | NextAuth v5 with 8-role RBAC and edge middleware | `role_matrix_generator.py` |
| `mongodb-email-system` | Templated transactional email with DB-backed templates | `template_variable_checker.py` |
| `mongodb-atlas-provisioning` | Self-service Atlas cluster management via Admin API v2 | `atlas_cost_estimator.py` |
| `mongodb-ai-features` | AI integration: summarization, RAG pipeline, usage tracking | `embedding_cost_estimator.py`, `chunk_size_analyzer.py` |
| `mongodb-event-platform` | Event lifecycle: CRUD, registration, feedback, judging | `feedback_form_generator.py` |
| `mongodb-partner-portal` | Sponsor/partner management with 5-tier system | `tier_report_generator.py` |
| `mongodb-devrel-advisor` | Meta-skill: conventions, branding, architecture decisions | (none) |

## Python Tool Catalog

All tools use Python 3.7+ standard library only. No external dependencies.

### brand_color_checker.py
Validate CSS/theme files against the MongoDB brand palette.
```bash
python mongodb-nextjs-scaffold/scripts/brand_color_checker.py path/to/theme.ts
python mongodb-nextjs-scaffold/scripts/brand_color_checker.py path/to/theme.ts --format json
```

### env_checker.py
Check that a `.env` file has all required variables for selected skills.
```bash
python mongodb-nextjs-scaffold/scripts/env_checker.py .env --skills scaffold,rbac,email
python mongodb-nextjs-scaffold/scripts/env_checker.py .env --skills all --format json
```

### role_matrix_generator.py
Generate a role-to-route permission matrix from an admin-guard configuration file.
```bash
python mongodb-rbac-middleware/scripts/role_matrix_generator.py path/to/admin-guard.ts
python mongodb-rbac-middleware/scripts/role_matrix_generator.py path/to/admin-guard.ts --format json
```

### template_variable_checker.py
Parse email templates and report missing or unused variables.
```bash
python mongodb-email-system/scripts/template_variable_checker.py path/to/templates/
python mongodb-email-system/scripts/template_variable_checker.py path/to/templates/ --format json
```

### atlas_cost_estimator.py
Estimate monthly Atlas cost for a cluster configuration.
```bash
python mongodb-atlas-provisioning/scripts/atlas_cost_estimator.py --tier M10 --provider AWS --region us-east-1
python mongodb-atlas-provisioning/scripts/atlas_cost_estimator.py config.json --format json
```

### embedding_cost_estimator.py
Project Voyage AI and OpenAI embedding costs for a given document count and query volume.
```bash
python mongodb-ai-features/scripts/embedding_cost_estimator.py --docs 1000 --queries-per-month 5000
python mongodb-ai-features/scripts/embedding_cost_estimator.py --docs 1000 --queries-per-month 5000 --format json
```

### chunk_size_analyzer.py
Analyze markdown files and recommend optimal chunk sizes for RAG ingestion.
```bash
python mongodb-ai-features/scripts/chunk_size_analyzer.py path/to/docs/
python mongodb-ai-features/scripts/chunk_size_analyzer.py path/to/docs/ --format json
```

### feedback_form_generator.py
Generate a FeedbackFormConfig JSON document from a simple YAML specification.
```bash
python mongodb-event-platform/scripts/feedback_form_generator.py spec.yaml
python mongodb-event-platform/scripts/feedback_form_generator.py spec.yaml --format json
```

### tier_report_generator.py
Generate a partner engagement summary report from partner data.
```bash
python mongodb-partner-portal/scripts/tier_report_generator.py partners.json
python mongodb-partner-portal/scripts/tier_report_generator.py partners.json --format json
```

## Quality Standards

All skills in this collection meet the following standards:

- **Real code, not pseudocode**: Every code pattern is extracted from a production application
- **Architecture decisions documented**: Each skill explains WHY, not just WHAT
- **Common pitfalls listed**: Known gotchas that save hours of debugging
- **Self-contained**: Each skill can be used independently (dependencies are noted, not required)
- **Python tools are deterministic**: No LLM/API calls — pure local computation
- **Standard library only**: Python scripts have zero external dependencies

## Related Skills

Skills reference each other where patterns overlap:

- `mongodb-nextjs-scaffold` → foundation for all other skills
- `mongodb-rbac-middleware` → depends on scaffold's auth setup
- `mongodb-email-system` → depends on scaffold's DB connection
- `mongodb-atlas-provisioning` → depends on scaffold + RBAC
- `mongodb-ai-features` → depends on scaffold's singleton pattern
- `mongodb-event-platform` → depends on scaffold, RBAC, email
- `mongodb-partner-portal` → depends on scaffold, RBAC, email
- `mongodb-devrel-advisor` → references all other skills
