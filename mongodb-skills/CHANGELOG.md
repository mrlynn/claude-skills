# Changelog

All notable changes to the MongoDB DevRel Skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-01

### Added - Initial Release

**8 Production-Ready Skills:**

- `mongodb-nextjs-scaffold` - Next.js + MongoDB + Auth + MUI project bootstrap with MongoDB branding
- `mongodb-rbac-middleware` - NextAuth v5 with 8-role RBAC and edge middleware
- `mongodb-email-system` - Templated transactional email with DB-backed templates
- `mongodb-atlas-provisioning` - Self-service Atlas cluster management via Admin API v2
- `mongodb-ai-features` - AI integration: summarization, RAG pipeline, usage tracking
- `mongodb-event-platform` - Event lifecycle: CRUD, registration, feedback, judging
- `mongodb-partner-portal` - Sponsor/partner management with 5-tier system
- `mongodb-devrel-advisor` - Meta-skill: conventions, branding, architecture decisions

**10 Python CLI Tools (standard library only):**

- `brand_color_checker.py` - Validate CSS/theme files against MongoDB brand palette
- `env_checker.py` - Check .env files for required variables
- `role_matrix_generator.py` - Generate role-to-route permission matrix
- `template_variable_checker.py` - Parse email templates for missing/unused variables
- `atlas_cost_estimator.py` - Estimate monthly Atlas cluster costs
- `embedding_cost_estimator.py` - Project embedding costs for RAG pipelines
- `chunk_size_analyzer.py` - Recommend optimal chunk sizes for document ingestion
- `feedback_form_generator.py` - Generate FeedbackFormConfig from YAML specs
- `tier_report_generator.py` - Generate partner engagement summary reports

**Documentation:**

- README.md with full skills catalog and usage guide
- CLAUDE.md development guide
- Per-skill SKILL.md with YAML frontmatter
- Reference documentation for each skill
- `dist/` directory with prebuilt combined skill files

### Origin

All skills extracted from the [MongoDB Hackathon Platform](https://github.com/mrlynn/mongohacks) - a production Next.js 16 application with 26 Mongoose models, 8 user roles, and comprehensive admin tooling.

---

## Version History Summary

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.0.0 | 2026-03-01 | Initial release - 8 skills, 10 Python tools |

---

## Upcoming Releases

### v1.1.0 (Planned)

- Additional Python automation tools
- Enhanced reference documentation
- Community-contributed skill improvements

### v2.0.0 (Planned)

- New skills: MongoDB Change Streams, MongoDB Charts integration
- Multi-framework support (beyond Next.js)
- Interactive skill installer

---

## Notes

**Semantic Versioning:**

- **Major (x.0.0):** Breaking changes, new skill domains
- **Minor (1.x.0):** New skills, significant enhancements
- **Patch (1.0.x):** Bug fixes, documentation updates, minor improvements

**Contributors:**
All contributors will be credited in release notes for their specific contributions.
