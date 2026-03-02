# ATS (Applicant Tracking System) Best Practices

## What is an ATS?

An Applicant Tracking System scans resumes for keywords and filters out candidates before a human ever sees the application. **75% of resumes are rejected by ATS before reaching a recruiter.**

## How ATS Works

1. **Parse resume** into structured fields (name, experience, skills)
2. **Extract keywords** from job posting
3. **Match keywords** in resume to job requirements
4. **Score candidates** based on match percentage
5. **Filter out** candidates below threshold (typically <70% match)

## ATS-Friendly Formatting

### ✅ DO

- **Use standard section headers:**
  - Experience (not "Professional Journey")
  - Skills (not "Core Competencies")
  - Education (not "Academic Background")

- **Use standard fonts:**
  - Arial, Calibri, Times New Roman, Helvetica
  - 10-12pt font size

- **Use standard bullet points:**
  - • or - (not custom symbols)

- **Use consistent date formats:**
  - MM/YYYY or Month YYYY
  - "2020-2023" or "Jan 2020 - Dec 2023"

- **Save as .docx or .pdf:**
  - PDF preferred (better formatting preservation)
  - .docx if explicitly requested

### ❌ DON'T

- **Avoid tables and columns**
  - ATS reads left-to-right, tables confuse it
  - Multi-column layouts get scrambled

- **Avoid headers/footers**
  - Content in headers often ignored
  - Page numbers OK, but no contact info

- **Avoid graphics and images**
  - Charts, graphs, headshots
  - Logos or icons
  - Text boxes

- **Avoid creative formatting**
  - Fancy fonts or colors
  - Unusual section names
  - Vertical text

- **Avoid acronyms without spelled-out version**
  - First use: "Search Engine Optimization (SEO)"
  - Subsequent: "SEO"

## Keyword Optimization

### Exact Keyword Matching

ATS looks for **exact matches**. Variations don't count.

**Example:**
- Job posting: "project management"
- Your resume: "managed projects" ❌ (no match)
- Your resume: "project management" ✅ (match)

**Solution:** Use exact phrasing from job posting.

### Keyword Density

**Too few:** Won't rank high enough
**Too many:** Flagged as keyword stuffing

**Sweet spot:** 
- Mention each key skill 2-3 times
- Naturally integrated in achievements

### Keyword Placement

ATS prioritizes keywords in certain sections:

1. **Skills section** (highest weight)
2. **Experience section** (medium weight)
3. **Summary section** (lower weight)

**Strategy:** Put required skills in Skills section, then integrate in Experience achievements.

## File Naming

**Bad:**
- resume.pdf
- resume-final-v3.pdf
- JohnDoe_Resume_2023_FINAL.pdf

**Good:**
- JohnDoe-Resume.pdf
- JohnDoe-SeniorEngineer-Resume.pdf

## Common ATS Parsing Errors

### Problem 1: Date Parsing

**ATS-friendly:**
```
Senior Developer | MongoDB | 01/2020 - Present
```

**ATS-unfriendly:**
```
Senior Developer @ MongoDB (Jan '20 - now)
```

### Problem 2: Contact Info

**ATS-friendly:**
```
John Doe
john.doe@email.com | (555) 555-5555 | linkedin.com/in/johndoe
```

**ATS-unfriendly:**
```
[Image of business card]
```

### Problem 3: Skills Section

**ATS-friendly:**
```
Skills: Python, MongoDB, Docker, AWS, React
```

**ATS-unfriendly:**
```
[Chart showing skill proficiency levels]
```

## Testing Your Resume

### Free ATS Checkers

- **Jobscan** (jobscan.co): Compares your resume to job posting
- **Resume Worded** (resumeworded.com): Free ATS scoring
- **TopResume** (topresume.com): Free resume review

### Manual Check

1. **Copy/paste test:**
   - Copy your resume text
   - Paste into plain text editor
   - If it's readable, ATS can parse it

2. **Keyword search:**
   - Open job posting
   - Highlight required skills
   - Search for each in your resume
   - Aim for 80%+ match

## ATS Score Improvement

### From 40% to 80% Match

**Before (40% match):**
```
Experience:
- Built web applications
- Managed team projects
- Improved system reliability
```

**After (80% match):**
```
Experience:
- Built full-stack web applications using React and Node.js
- Managed Agile team projects with Jira and Confluence
- Improved system reliability through Docker containerization and AWS deployment
```

**Changes:**
- Added specific technologies (React, Node.js, Docker, AWS)
- Added methodologies (Agile, Jira)
- Used exact phrasing from job posting

## Industry-Specific ATS Quirks

### Tech Industry
- Prioritizes technical skills heavily
- Expects GitHub/portfolio links
- Values recent technologies over old

### Enterprise/Corporate
- Prioritizes education and certifications
- Expects formal job titles
- Values stability (long tenures)

### Startups
- Prioritizes versatility ("full-stack", "generalist")
- Expects fast-paced keywords ("pivot", "iterate")
- Values impact over tenure

## Beyond ATS: Human Readers

**Remember:** Even if you pass ATS, a human still reads your resume.

**Balance:**
- ATS optimization (keywords, formatting)
- Human appeal (achievements, impact, storytelling)

**Don't sacrifice readability for ATS gaming.**

## Red Flags ATS Looks For

- **Employment gaps** (unexplained >6 months)
- **Frequent job hopping** (<1 year tenure)
- **Inconsistent dates** (overlapping jobs, math errors)
- **Spelling errors** (especially in skills)
- **Irrelevant experience** (no keyword matches)

## ATS Bypass Strategies

If ATS is blocking you:

1. **Network directly:** Referrals often bypass ATS
2. **Email hiring manager:** Direct contact > ATS submission
3. **Apply via company site:** Sometimes different ATS settings
4. **Attend recruiting events:** In-person submission bypasses ATS

## Myths vs. Reality

### Myth: "ATS rejects keywords in wrong section"
**Reality:** ATS scans entire document, but prioritizes certain sections

### Myth: "PDFs don't work with ATS"
**Reality:** Modern ATS handles PDFs fine (older systems struggled)

### Myth: "Creative resumes stand out"
**Reality:** Creative formatting gets rejected by ATS before humans see it

### Myth: "More pages = more keywords = better score"
**Reality:** Concise, relevant resumes score higher (1-2 pages ideal)

## Action Items

1. **Audit your resume** against ATS best practices
2. **Test with ATS checker** (Jobscan or similar)
3. **Reformat if needed** (remove tables, graphics, fancy fonts)
4. **Extract keywords** from job posting
5. **Integrate keywords** naturally in your resume
6. **Proofread** for spelling errors (critical for keyword matching)
7. **Save as PDF** with professional filename

---

**Bottom line:** ATS is a gatekeeper, not an enemy. Optimize for it without sacrificing human readability.
