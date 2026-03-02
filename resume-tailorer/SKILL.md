---
name: resume-tailorer
description: Customize resumes and cover letters for specific job postings with ATS optimization, keyword matching, and experience highlighting
license: MIT
metadata:
  version: 1.0.0
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  category: career-development
  domain: job-applications
  updated: 2026-03-01
  python-tools: job_analyzer.py, resume_matcher.py, ats_optimizer.py
  tech-stack: python, json, markdown
---

# resume-tailorer

## Trigger

Use this skill when applying to jobs, customizing resumes for specific roles, or optimizing applications for Applicant Tracking Systems (ATS).

**Trigger phrases:**
- "Tailor my resume for this job"
- "Customize cover letter"
- "Match my experience to job requirements"
- "Optimize for ATS"
- "Rewrite resume for [role]"

## Overview

Generic resumes get filtered out. Every job application needs a tailored resume that:
1. **Mirrors the job description language** (ATS keyword matching)
2. **Highlights relevant experience** (not all experience is equal)
3. **Quantifies achievements** (numbers > vague claims)
4. **Passes ATS screening** (formatting, keywords, structure)

This skill analyzes job postings, matches your experience to requirements, rewrites sections to highlight relevance, and generates ATS-optimized PDFs.

**Not a resume builder from scratch** - this assumes you have a master resume and tailors it per application.

## How to Use

### Quick Start
1. **Analyze job posting:**
   ```bash
   python scripts/job_analyzer.py job-posting.txt --output analysis.json
   ```

2. **Match your experience:**
   ```bash
   python scripts/resume_matcher.py master-resume.json analysis.json --output matches.json
   ```

3. **Generate tailored resume:**
   ```bash
   python scripts/ats_optimizer.py master-resume.json matches.json --output tailored-resume.md
   ```

### Python Tools
- `scripts/job_analyzer.py` — Extract requirements, skills, keywords from job posting
- `scripts/resume_matcher.py` — Match candidate experience to job requirements
- `scripts/ats_optimizer.py` — Generate ATS-optimized resume and cover letter

### Reference Docs
- `references/tailoring-strategies.md` — Resume tailoring best practices
- `references/ats-best-practices.md` — ATS optimization techniques

### Templates & Assets
- `assets/resume-template.json` — Structured resume format (master resume)
- `assets/cover-letter-template.txt` — Customizable cover letter
- `assets/sample-job-posting.txt` — Example job description

## Architecture Decisions

### Why JSON for Master Resume
A structured format enables:
- Programmatic analysis and matching
- Flexible reordering of experience
- Easy keyword extraction
- Version control friendly

**Format:**
```json
{
  "contact": { "name": "...", "email": "...", "phone": "..." },
  "summary": "...",
  "experience": [
    {
      "title": "Senior Developer Advocate",
      "company": "MongoDB",
      "dates": "2015-Present",
      "achievements": [
        "Led 50+ customer workshops reaching 2,000+ developers",
        "Built RAG demo platform reducing integration time by 60%"
      ]
    }
  ],
  "skills": ["Python", "MongoDB", "Vector Search", "Public Speaking"]
}
```

### Keyword Matching Strategy
ATS systems scan for exact keyword matches. Strategy:
1. Extract keywords from job posting (nouns, skills, technologies)
2. Find synonyms in candidate experience (e.g., "led" → "leadership")
3. Rewrite bullet points to include exact job posting keywords
4. Maintain natural language (not keyword stuffing)

**Example:**
- Job posting: "Experience with **vector databases** and **semantic search**"
- Original resume: "Built search functionality with embeddings"
- Tailored: "Built **semantic search** using **vector databases** with MongoDB Atlas"

### Experience Relevance Scoring
Not all experience is relevant. Score each role/achievement by:
- **Keyword overlap** (30%): How many job keywords appear?
- **Recency** (20%): Recent experience > old experience
- **Impact** (30%): Quantified achievements > vague descriptions
- **Role alignment** (20%): Title similarity to target role

Top 70% of scored experience goes in the tailored resume.

### ATS-Friendly Formatting
ATS parsers struggle with:
- ❌ Tables and columns
- ❌ Headers/footers
- ❌ Graphics and images
- ❌ Non-standard fonts
- ❌ Text boxes

**Safe formatting:**
- ✅ Plain text or simple Markdown
- ✅ Standard section headers (Experience, Education, Skills)
- ✅ Bullet points with • or -
- ✅ Dates in consistent format (MM/YYYY)
- ✅ PDF generated from clean HTML/Markdown

### Cover Letter Personalization
Generic cover letters are obvious. Personalize by:
1. **Address hiring manager by name** (research on LinkedIn)
2. **Reference specific company initiatives** (recent news, product launches)
3. **Connect your experience to their needs** (not just "I'm great")
4. **Show genuine interest** (why this company, not just any company)

## Generated Output Structure

### Tailored Resume (Markdown)
```markdown
# [Your Name]
[Email] | [Phone] | [LinkedIn] | [Portfolio]

## Summary
[Customized 2-3 sentence summary highlighting relevant experience]

## Experience

### [Most Relevant Role]
**[Title]** | [Company] | [Dates]
- [Achievement with job posting keywords]
- [Quantified result relevant to target role]
- [Technical skills matching job requirements]

### [Second Most Relevant Role]
...

## Skills
[Prioritized skills matching job requirements]

## Education
[Degree] | [School] | [Year]
```

### Cover Letter
```
[Your Name]
[Contact Info]
[Date]

[Hiring Manager Name]
[Company]

Dear [Name],

[Opening: Why this role excites you + company-specific detail]

[Body: 2-3 paragraphs connecting your experience to their needs]

[Closing: Call to action + appreciation]

Best regards,
[Your Name]
```

## Python Tool Details

### 1. Job Analyzer

**Purpose:** Extract structured requirements from job posting text.

**Usage:**
```bash
python scripts/job_analyzer.py job-posting.txt --output analysis.json
```

**Output:**
```json
{
  "title": "Senior Developer Advocate",
  "company": "MongoDB",
  "required_skills": ["Python", "Public Speaking", "MongoDB", "Vector Search"],
  "preferred_skills": ["RAG", "LangChain", "Customer Workshops"],
  "keywords": ["developer", "advocate", "workshops", "demos", "vector", "search"],
  "experience_years": "5+",
  "education": "Bachelor's degree or equivalent",
  "responsibilities": [
    "Lead customer workshops",
    "Build demo applications",
    "Present at conferences"
  ]
}
```

**How it works:**
1. Parse job posting text
2. Extract skills (regex patterns for common tech/tools)
3. Identify required vs preferred (section headers, "must have" vs "nice to have")
4. Extract experience requirements (regex for "X+ years")
5. List responsibilities (bulleted sections)

### 2. Resume Matcher

**Purpose:** Match candidate experience to job requirements and score relevance.

**Usage:**
```bash
python scripts/resume_matcher.py master-resume.json analysis.json --output matches.json
```

**Output:**
```json
{
  "overall_match": 0.82,
  "matched_skills": ["Python", "MongoDB", "Vector Search", "Public Speaking"],
  "missing_skills": ["LangChain"],
  "experience_matches": [
    {
      "title": "Principal Developer Advocate",
      "company": "MongoDB",
      "relevance_score": 0.95,
      "keyword_overlap": 0.87,
      "matched_achievements": [
        "Led 50+ customer workshops reaching 2,000+ developers",
        "Built RAG demo platform reducing integration time by 60%"
      ],
      "rewrite_suggestions": [
        "Add 'vector search' to RAG demo achievement",
        "Quantify workshop impact with developer metrics"
      ]
    }
  ],
  "tailoring_priority": [
    "Emphasize workshop leadership (matches 'Lead customer workshops')",
    "Highlight RAG/vector search projects",
    "Add specific MongoDB features you've demoed"
  ]
}
```

### 3. ATS Optimizer

**Purpose:** Generate ATS-friendly resume with keyword optimization.

**Usage:**
```bash
python scripts/ats_optimizer.py master-resume.json matches.json --output tailored-resume.md
```

**Options:**
- `--cover-letter` - Generate cover letter too
- `--format pdf` - Output PDF (requires pandoc)
- `--highlight-keywords` - Bold keywords matching job posting

**Output:** Markdown resume with:
- Keywords from job posting naturally integrated
- Experience reordered by relevance score
- Achievements rewritten to highlight job-specific value
- Skills section prioritized by job requirements
- ATS-safe formatting

## Workflow Example

**Scenario:** Applying for "Senior Developer Advocate at MongoDB"

**Step 1: Analyze job posting**
```bash
python scripts/job_analyzer.py mongodb-job.txt --output analysis.json
```

Output: Extracts required skills (Python, MongoDB, workshops), keywords (developer advocate, RAG, vector search)

**Step 2: Match your experience**
```bash
python scripts/resume_matcher.py my-resume.json analysis.json --output matches.json
```

Output: Scores your MongoDB work at 0.95 relevance, identifies missing "LangChain" skill

**Step 3: Generate tailored resume**
```bash
python scripts/ats_optimizer.py my-resume.json matches.json \
  --output mongodb-resume.md \
  --cover-letter \
  --format pdf
```

Output:
- `mongodb-resume.md` - Tailored resume highlighting MongoDB/workshop experience
- `mongodb-cover-letter.md` - Personalized cover letter
- `mongodb-resume.pdf` - ATS-optimized PDF

**Step 4: Review and refine**
- Check keyword integration sounds natural
- Verify quantified achievements are accurate
- Customize cover letter opening (research hiring manager)
- Proofread for typos

**Step 5: Apply**
Upload `mongodb-resume.pdf` and submit cover letter text.

## Common Patterns

### Pattern 1: Keyword Integration Without Stuffing

**Bad (keyword stuffing):**
> "Expert in Python, MongoDB, vector search, RAG, semantic search, embeddings, LangChain, OpenAI"

**Good (natural integration):**
> "Built semantic search platform using MongoDB Atlas Vector Search with Python, integrating RAG patterns via LangChain and OpenAI embeddings"

### Pattern 2: Quantify Everything

**Before:**
> "Led customer workshops and improved developer satisfaction"

**After:**
> "Led 50+ customer workshops reaching 2,000+ developers, achieving 4.8/5 satisfaction score and 40% increase in trial conversions"

### Pattern 3: Action Verbs Matching Job Description

If job posting says "Drive adoption", use "Drove" (not "Led" or "Managed"). Mirror their language.

### Pattern 4: Reorder Experience by Relevance

**Master resume order:** Chronological (newest first)

**Tailored resume order:** Relevance score (most relevant first), even if older

Example: Applying to DevRel role? Put your 2020 developer advocacy job before your 2023 engineering management role.

## Quality Checklist

Before submitting:
- [ ] Keywords from job posting appear naturally in resume
- [ ] All achievements are quantified (numbers, percentages, scale)
- [ ] Experience is reordered by relevance (not just chronological)
- [ ] Cover letter addresses hiring manager by name
- [ ] Cover letter references company-specific detail
- [ ] Resume passes ATS check (no tables, graphics, weird fonts)
- [ ] Dates are consistent format (MM/YYYY)
- [ ] No typos or grammar errors
- [ ] PDF is clean and parseable
- [ ] File name is professional (FirstLast-Resume.pdf, not resume-final-v3.pdf)

## When to Use vs. Generic Resume

| Use tailored resume | Use generic resume |
|---------------------|-------------------|
| Applying to specific role | Networking/informational interviews |
| Job posting with clear requirements | Career fairs (exploratory) |
| Competitive position | Internal referrals (already have context) |
| ATS-screened application | Direct email to hiring manager |

**Rule of thumb:** If you're uploading to an ATS, tailor it.

## Tools Integration

**Export to LinkedIn:**
After tailoring, update your LinkedIn profile to mirror the keywords/achievements for that industry.

**Track applications:**
Save each tailored resume as `Company-Role-YYYY-MM-DD.pdf` to track what you sent where.

**A/B testing:**
If applying to similar roles, try different keyword emphasis and track response rates.

## References

- ATS Optimization: `references/ats-best-practices.md`
- Tailoring Strategies: `references/tailoring-strategies.md`
- Resume Action Verbs: https://www.themuse.com/advice/185-powerful-verbs-that-will-make-your-resume-awesome
- Cover Letter Guide: https://www.askamanager.org/category/cover-letters

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)

---

**Next steps after generating tailored resume:**
1. Proofread for natural language flow
2. Customize cover letter opening with company research
3. Save as PDF with professional filename
4. Track application in spreadsheet
5. Follow up 1 week after applying
