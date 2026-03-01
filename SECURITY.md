# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x.x | Yes |
| < 1.0 | No |

## Reporting a Vulnerability

We take security seriously. If you discover a vulnerability in this repository, please report it responsibly.

### Do NOT Open a Public Issue

Please **do not** create a public GitHub issue for security vulnerabilities. This protects users while we work on a fix.

### Contact

Report security vulnerabilities by emailing **michael.lynn@mongodb.com** or via [GitHub Security Advisories](../../security/advisories/new).

**Include:**
- Type of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

### Response Timeline

| Severity | Target Response |
|----------|----------------|
| Critical (RCE, data exposure) | 24-48 hours |
| High (auth bypass, privilege escalation) | 1 week |
| Medium (XSS, misconfigurations) | 2 weeks |
| Low (best practice violations) | 1 month |

- **Initial acknowledgment:** within 48 hours
- **Assessment and fix timeline:** communicated after triage
- **Public disclosure:** after fix is deployed

## Security Best Practices for Users

### Review Scripts Before Running

All Python tools in this repository are open source. Review them before execution:

```bash
# Check what a script does before running it
cat scripts/tool.py

# Look for:
# - External network calls
# - File system modifications outside the working directory
# - Environment variable access
# - Suspicious imports
```

### Run in Sandboxed Environments

For untrusted or newly downloaded skills:

```bash
# Use a virtual environment
python -m venv venv
source venv/bin/activate

# Or use Docker
docker run -it --rm -v $(pwd):/work python:3.11 python /work/scripts/tool.py
```

### Verify SKILL.md Content

Before loading a skill into your AI agent, verify that:
- It doesn't request sensitive information (API keys, credentials)
- Workflows are clearly documented
- YAML frontmatter is valid

## Security in Skill Development

### Do

- Validate all inputs
- Handle errors gracefully
- Limit file system access to necessary directories
- Use type hints
- Keep dependencies to zero (standard library only)

### Don't

- Use `eval()` or `exec()` with user input
- Execute shell commands with unsanitized input
- Store credentials in code
- Make network requests without clear documentation
- Access sensitive system files

## Current Security Measures

- All skills are open source for transparent review
- Python tools use standard library only (minimal attack surface)
- No network calls in any tool
- No credentials or secrets in the repository
- MIT License with clear usage terms

## Recognition

Security researchers who responsibly disclose vulnerabilities will be credited in the CHANGELOG and security advisory (with permission).
