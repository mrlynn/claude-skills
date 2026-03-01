# Contributing

Thank you for your interest in contributing to this skills collection. Whether you're fixing a bug, improving documentation, or proposing a new skill, your help is welcome.

## Ways to Contribute

- **New skills** — Add domain expertise from your field
- **Improve existing skills** — Better patterns, more examples, updated references
- **Python tools** — New CLI tools or improvements to existing ones
- **Documentation** — Clearer guides, additional examples, typo fixes
- **Bug reports** — Issues with scripts, broken links, incorrect patterns

## Getting Started

### Prerequisites

- Python 3.7+ (for running/testing tools)
- Git
- Familiarity with the skill domain you're contributing to

### Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/claude-skills.git
cd claude-skills
git checkout -b feature/your-change
```

## Skill Structure

All skills must follow this structure:

```
your-skill-name/
├── SKILL.md              # Required: YAML frontmatter + instructions
├── scripts/              # Optional: Python CLI tools
├── references/           # Optional: Detailed knowledge base
└── assets/               # Optional: Templates, sample data
```

### SKILL.md Requirements

```yaml
---
name: your-skill-name
description: What it does and when to use it.
license: MIT
metadata:
  version: 1.0.0
  author: Your Name
  category: domain-category
  updated: 2026-03-01
---
```

The markdown body should include:
- Overview and purpose
- When to use this skill (trigger conditions)
- Core workflows and patterns
- Code examples from real usage
- Common pitfalls and gotchas

**Target length:** 100-200 lines. Move detailed content to `references/`.

### Python Tool Standards

- **Standard library only** — no external dependencies
- **CLI-first** with `--help` support
- **JSON output option** via `--format json`
- **Production-ready** — not placeholders or stubs
- **Deterministic** — no LLM/API calls; pure local computation

## Contribution Process

### 1. Discuss First (for major changes)

Open an issue describing your idea before investing significant time. This avoids duplicate work and ensures alignment.

### 2. Develop

Follow the structure and standards above. Test your changes locally.

### 3. Test

**For skills:**
- [ ] YAML frontmatter is valid
- [ ] All code examples are correct
- [ ] Links and references work

**For Python tools:**
- [ ] Runs without errors on Python 3.7+
- [ ] `--help` flag works
- [ ] `--format json` produces valid JSON
- [ ] Edge cases handled gracefully

### 4. Submit a Pull Request

```bash
git add .
git commit -m "feat(mongodb): add new-skill-name"
git push origin feature/your-change
```

**PR title format:**
- `feat(domain): add new skill for X`
- `fix(skill-name): correct issue with Y`
- `docs: improve installation guide`

**PR description must include:**
- What changed and why
- How it was tested
- Any documentation updates

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat(domain): description` — new skill or capability
- `fix(skill): description` — bug fix
- `docs: description` — documentation only
- `refactor(skill): description` — code restructuring

## What We Won't Accept

- Generic advice without actionable patterns
- Placeholder or stub scripts
- Skills without clear use cases
- Proprietary or confidential information
- Content that violates licenses

## Code of Conduct

By contributing, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

- **Bug reports:** [Open an issue](../../issues/new?template=bug_report.md)
- **Skill ideas:** [Open a feature request](../../issues/new?template=feature_request.md)
- **General questions:** [Start a discussion](../../discussions)
