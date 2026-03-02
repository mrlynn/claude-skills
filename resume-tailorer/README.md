# Resume Tailorer

Customize resumes and cover letters for specific job postings with ATS optimization and keyword matching.

## Quick Start

### 1. Set up your master resume

Edit `assets/resume-template.json` with your complete work history:
```bash
cp assets/resume-template.json my-resume.json
# Edit my-resume.json with your experience
```

### 2. Save the job posting

Copy the job description into a text file:
```bash
# Save job posting to job-posting.txt
```

### 3. Analyze the job posting

```bash
python scripts/job_analyzer.py job-posting.txt --output analysis.json
```

**Output:** Extracts required skills, keywords, responsibilities

### 4. Match your experience

```bash
python scripts/resume_matcher.py my-resume.json analysis.json --output matches.json
```

**Output:** Scores your experience by relevance, identifies keyword gaps

### 5. Generate tailored resume

```bash
python scripts/ats_optimizer.py my-resume.json matches.json \
  --output tailored-resume.md \
  --cover-letter \
  --company-name "MongoDB"
```

**Output:**
- `tailored-resume.md` - Markdown resume optimized for this job
- `tailored-resume-cover-letter.md` - Cover letter template

### 6. Convert to PDF

```bash
# Option 1: Using pandoc
pandoc tailored-resume.md -o MichaelLynn-Resume.pdf

# Option 2: Copy markdown into Google Docs and export as PDF
```

## Python Tools

### job_analyzer.py
Extracts structured requirements from job posting text.

**Features:**
- Detects required vs preferred skills
- Extracts keywords and technologies
- Identifies experience/education requirements
- Lists responsibilities

**Example:**
```bash
python scripts/job_analyzer.py mongodb-job.txt --output analysis.json
```

### resume_matcher.py
Matches your experience to job requirements and scores relevance.

**Scoring:**
- Keyword overlap (30%)
- Recency (20%)
- Impact/quantification (30%)
- Role alignment (20%)

**Example:**
```bash
python scripts/resume_matcher.py my-resume.json analysis.json --output matches.json
```

### ats_optimizer.py
Generates ATS-friendly resume with keyword optimization.

**Features:**
- Reorders experience by relevance score
- Integrates keywords naturally
- Prioritizes skills by job requirements
- Generates cover letter template
- ATS-safe formatting (no tables/graphics)

**Example:**
```bash
python scripts/ats_optimizer.py my-resume.json matches.json \
  --output tailored-resume.md \
  --cover-letter
```

## Master Resume Format

Your master resume should be in JSON format (see `assets/resume-template.json`):

```json
{
  "contact": { "name": "...", "email": "...", "phone": "..." },
  "summary": "...",
  "experience": [
    {
      "title": "...",
      "company": "...",
      "dates": "...",
      "achievements": ["...", "..."]
    }
  ],
  "skills": ["...", "..."],
  "education": [...]
}
```

**Why JSON?**
- Programmatic analysis and matching
- Easy reordering by relevance
- Version control friendly
- Flexible for different formats (Markdown, PDF, HTML)

## Reference Documentation

- **`references/tailoring-strategies.md`** - Resume tailoring best practices
  - Mirror job description language
  - Quantify achievements
  - Reorder by relevance
  - STAR method
  - Cover letter personalization

- **`references/ats-best-practices.md`** - ATS optimization techniques
  - ATS-friendly formatting
  - Keyword optimization
  - Common parsing errors
  - Testing your resume
  - Industry-specific quirks

## Workflow Example

**Scenario:** Applying for "Senior Developer Advocate at MongoDB"

```bash
# 1. Analyze job posting
python scripts/job_analyzer.py mongodb-job.txt --output analysis.json
# Output: Required skills (Python, MongoDB, workshops), keywords (vector search, RAG)

# 2. Match experience
python scripts/resume_matcher.py my-resume.json analysis.json --output matches.json
# Output: MongoDB role scored 0.95 relevance, missing "LangChain" skill

# 3. Generate tailored resume
python scripts/ats_optimizer.py my-resume.json matches.json \
  --output mongodb-resume.md \
  --cover-letter \
  --company-name "MongoDB"
# Output: Resume highlighting MongoDB/workshop experience, cover letter template

# 4. Customize cover letter
# Edit mongodb-resume-cover-letter.md with company research

# 5. Convert to PDF
pandoc mongodb-resume.md -o MichaelLynn-MongoDB-Resume.pdf

# 6. Apply!
```

## Quality Checklist

Before submitting:
- [ ] Keywords from job posting appear naturally
- [ ] All achievements quantified (numbers, metrics)
- [ ] Experience reordered by relevance
- [ ] Cover letter addresses hiring manager by name
- [ ] Cover letter references company-specific detail
- [ ] No typos or grammar errors
- [ ] ATS-friendly formatting (no tables/graphics)
- [ ] File named professionally (FirstLast-Resume.pdf)

## Tips

### For Best Results
1. **Keep master resume current** - Update after every achievement
2. **Save tailored versions** - Name as `Company-Role-Date.pdf` to track
3. **Research company** - Spend 15 minutes on LinkedIn/blog before customizing
4. **Proofread 3 times** - Typos in skills section kill keyword matching
5. **Test with ATS checker** - Use Jobscan or Resume Worded

### Time Investment
- **First time:** 2-3 hours (setting up master resume + first tailoring)
- **Subsequent applications:** 30-60 minutes per job

### Success Metrics
- **Generic resume:** 2-5% interview rate
- **Tailored resume:** 30-50% interview rate for relevant roles

**Quality > quantity.** Better to apply to 5 jobs with tailored resumes than 50 with generic.

## Common Pitfalls

❌ **Keyword stuffing**
> "Expert in Python, MongoDB, vector search, RAG, semantic search..."

✅ **Natural integration**
> "Built semantic search using MongoDB Atlas Vector Search with Python"

❌ **Vague achievements**
> "Improved developer experience"

✅ **Quantified results**
> "Improved onboarding, reducing time-to-first-query from 2h to 15min (4.6/5 satisfaction)"

❌ **Chronological order when irrelevant**
> 2023: Engineering Manager (not relevant)  
> 2020: Developer Advocate (highly relevant)

✅ **Relevance order**
> Developer Advocate, 2020 (relevance: 0.95)  
> Engineering Manager, 2023 (relevance: 0.60)

## Dependencies

**Python:** Standard library only (no external packages required)

**Optional (for PDF export):**
- Pandoc: `brew install pandoc`

## References

- ATS Statistics: https://www.jobscan.co/blog/ats-statistics/
- Resume Action Verbs: https://www.themuse.com/advice/185-powerful-verbs
- Cover Letter Guide: https://www.askamanager.org/category/cover-letters

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)

---

**Next steps:** Set up your master resume, analyze your first job posting, and tailor!
