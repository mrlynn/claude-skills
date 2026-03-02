---
name: hackathon-judge-assistant
description: Generate scoring rubrics and constructive feedback for hackathon submissions with fair evaluation frameworks and actionable improvement suggestions
license: MIT
metadata:
  version: 1.0.0
  author: MongoDB Developer Relations
  category: events
  domain: hackathon-judging
  updated: 2026-03-01
  python-tools: rubric_generator.py, submission_scorer.py, feedback_generator.py
  tech-stack: python, markdown
---

# hackathon-judge-assistant

## Trigger

Use this skill when judging hackathons, creating scoring rubrics, or providing submission feedback.

**Trigger phrases:**
- "Create hackathon rubric"
- "Score hackathon submission"
- "Generate judge feedback"
- "Hackathon evaluation criteria"

## Overview

Good hackathon judging is:
- **Fair:** Consistent criteria applied to all teams
- **Constructive:** Feedback that helps teams improve
- **Balanced:** Technical + presentation + innovation
- **Encouraging:** Celebrate effort, even if incomplete

This skill generates rubrics, scores submissions, and provides actionable feedback that motivates rather than discourages.

## How to Use

### Quick Start

1. **Generate rubric:**
   ```bash
   python scripts/rubric_generator.py --type corporate --output rubric.md
   ```

2. **Score submission:**
   ```bash
   python scripts/submission_scorer.py submission.json rubric.md --output scores.json
   ```

3. **Generate feedback:**
   ```bash
   python scripts/feedback_generator.py scores.json --output feedback.md
   ```

### Python Tools
- `scripts/rubric_generator.py` — Create scoring rubrics
- `scripts/submission_scorer.py` — Score submissions against rubric
- `scripts/feedback_generator.py` — Generate constructive feedback

### Reference Docs
- `references/judging-best-practices.md` — Fair evaluation principles
- `references/feedback-templates.md` — Constructive feedback patterns

### Templates & Assets
- `assets/rubric-template.md` — Scoring criteria structure
- `assets/submission-template.json` — Submission data format

## Scoring Rubric

### Standard Categories (5 points each = 25 total)

**1. Innovation (5 points)**
- 5: Novel approach, creative problem-solving
- 4: Fresh take on existing idea
- 3: Solid implementation of known pattern
- 2: Derivative but functional
- 1: Copy of existing solution

**2. Technical Execution (5 points)**
- 5: Clean code, well-architected, production-ready
- 4: Good structure, minor rough edges
- 3: Works but needs refactoring
- 2: Barely functional, significant issues
- 1: Broken or incomplete

**3. Presentation (5 points)**
- 5: Clear, engaging, well-rehearsed demo
- 4: Good demo, minor stumbles
- 3: Functional demo, needs polish
- 2: Confusing or incomplete demo
- 1: No demo or unusable

**4. Problem Fit (5 points)**
- 5: Perfectly addresses stated problem
- 4: Good fit with minor gaps
- 3: Partially solves problem
- 2: Tangentially related
- 1: Misses the problem

**5. Completeness (5 points)**
- 5: Fully working end-to-end
- 4: Core features complete, minor gaps
- 3: Partial implementation
- 2: Proof-of-concept only
- 1: Minimal functionality

### Weighted Rubric (Alternative)

For different hackathon types, adjust weights:

**Student Hackathon** (learning-focused):
- Innovation: 30%
- Presentation: 25%
- Technical: 20%
- Completeness: 15%
- Problem fit: 10%

**Corporate Hackathon** (product-focused):
- Problem fit: 30%
- Technical: 25%
- Completeness: 25%
- Innovation: 15%
- Presentation: 5%

**Open Hackathon** (creativity-focused):
- Innovation: 40%
- Technical: 25%
- Presentation: 20%
- Completeness: 10%
- Problem fit: 5%

## Judging Best Practices

### DO:

✅ **Score against rubric, not each other**
> Don't compare teams. Score each submission independently against criteria.

✅ **Celebrate effort**
> "You built a working prototype in 24 hours - impressive execution under time pressure!"

✅ **Give actionable feedback**
> "Consider adding error handling for edge cases (null inputs, network failures)."

✅ **Acknowledge constraints**
> "Given the time limit, your prioritization of core features was smart."

✅ **Be specific**
> "The MongoDB aggregation pipeline for real-time analytics was well-designed."

### DON'T:

❌ **Harsh criticism**
> "This code is terrible." → "Consider refactoring for better separation of concerns."

❌ **Vague feedback**
> "Needs improvement." → "Add input validation on the form fields."

❌ **Compare to professional work**
> "This wouldn't pass code review." → (It's a hackathon, not production!)

❌ **Focus only on negatives**
> Always start with what worked well.

## Feedback Template

### Structure

**1. Strengths (3-5 bullets)**
- What impressed you
- Technical highlights
- Creative elements

**2. Areas for Improvement (2-3 bullets)**
- Specific, actionable suggestions
- Prioritized by impact
- Framed positively

**3. Next Steps (1-2 bullets)**
- Concrete actions to continue project
- Learning resources (if relevant)

### Example Feedback

**Project:** Real-time IoT dashboard with MongoDB time series

**Strengths:**
- ✅ Excellent use of MongoDB time series collections for sensor data
- ✅ Clean React UI with real-time updates via Socket.io
- ✅ Well-structured demo showing key features
- ✅ Good documentation in README

**Areas for Improvement:**
- Consider adding authentication (currently open endpoint)
- MongoDB aggregation pipeline could be optimized (reduce network roundtrips)
- Error handling for disconnected sensors missing

**Next Steps:**
- Deploy to MongoDB Atlas (free tier) for live demo
- Add data retention policy (TTL indexes on old sensor data)
- Check out MongoDB Change Streams for more efficient real-time updates

**Score:** 21/25 (Innovation: 4, Technical: 4, Presentation: 5, Problem Fit: 4, Completeness: 4)

## Common Hackathon Types

### 1. Corporate Internal Hackathon

**Focus:** Business value, feasibility

**Rubric emphasis:**
- Problem fit (30%)
- Technical execution (25%)
- Completeness (25%)

**Feedback style:**
- Align to company roadmap
- Production readiness considerations
- Team fit and resources needed

### 2. Student Hackathon

**Focus:** Learning, creativity

**Rubric emphasis:**
- Innovation (30%)
- Presentation (25%)
- Effort and learning (implicit)

**Feedback style:**
- Encouraging tone
- Learning resources
- Career development tips

### 3. Major League Hacking (MLH)

**Focus:** Technical skill, polish

**Rubric emphasis:**
- Technical execution (30%)
- Innovation (25%)
- Completeness (25%)

**Feedback style:**
- Detailed technical review
- Industry best practices
- Open source contribution paths

### 4. Themed Hackathon (e.g., AI, Climate, FinTech)

**Focus:** Theme alignment, impact

**Rubric emphasis:**
- Problem fit (35%)
- Innovation (30%)
- Impact potential (implicit)

**Feedback style:**
- Domain-specific insights
- Real-world application paths
- Industry connections

## Python Tool Details

### 1. Rubric Generator

**Input:** Hackathon type

**Output:** Markdown rubric with weighted criteria

```markdown
# Hackathon Judging Rubric: Corporate

## Scoring Criteria (25 points total)

### Problem Fit (30% - 7.5 points)
[Detailed scoring guide]

### Technical Execution (25% - 6.25 points)
[Detailed scoring guide]
...
```

### 2. Submission Scorer

**Input:** Submission data + rubric

**Output:** Scores per category + total

```json
{
  "team": "Team MongoDB",
  "project": "Real-time IoT Dashboard",
  "scores": {
    "innovation": 4,
    "technical": 4,
    "presentation": 5,
    "problem_fit": 4,
    "completeness": 4
  },
  "total": 21,
  "percentage": 84
}
```

### 3. Feedback Generator

**Input:** Scores + submission details

**Output:** Constructive feedback (strengths, improvements, next steps)

## Edge Cases

### Incomplete Submissions

**Don't penalize harshly:**
> "While the backend wasn't fully integrated, your MongoDB schema design shows solid understanding of document modeling."

**Focus on what's there:**
> "The prototype demonstrates the core concept well. With more time, adding the API layer would complete the vision."

### Over-Scoped Projects

**Acknowledge ambition:**
> "You tackled a complex problem. Scoping a smaller MVP might have allowed more polish on core features."

**Highlight wins:**
> "The authentication system you built is production-ready - great prioritization given the time."

### Technical Debt

**Frame constructively:**
> "Given the 24-hour constraint, hardcoding config was a smart time trade-off. For next steps, consider environment variables."

## Tie-Breaking

When scores are identical:

1. **Innovation** - Novel approaches win
2. **Completeness** - Working beats polished concepts
3. **Presentation** - Clear communication matters
4. **Technical quality** - Clean code over hacky

## Anti-Patterns

### ❌ Scoring Drift

**Problem:** Later submissions scored harsher than early ones

**Solution:** Review first few submissions after 5-10 to recalibrate

### ❌ The "Almost Perfect" Trap

**Problem:** No 5-point scores ("nothing is perfect")

**Solution:** If criteria met, award full points. 5/5 should be achievable.

### ❌ Personal Preference Bias

**Problem:** Favoring familiar tech stacks

**Solution:** Judge execution quality, not technology choices

### ❌ Recency Bias

**Problem:** Last demo feels most impressive

**Solution:** Take notes, review all scores before finalizing

## Quality Checklist

Before submitting scores:
- [ ] All categories scored (no blanks)
- [ ] Scores justified with notes
- [ ] Feedback includes strengths
- [ ] Suggestions are actionable
- [ ] Tone is encouraging
- [ ] No harsh language
- [ ] Specific examples cited

## When to Use vs. Other Tools

| Use `hackathon-judge-assistant` | Use other tools |
|---------------------------------|-----------------|
| Creating rubrics | Event planning |
| Scoring submissions | Prize selection |
| Writing feedback | Team formation |
| Fair evaluation | Logistics management |

## References

- Judging Best Practices: `references/judging-best-practices.md`
- Feedback Templates: `references/feedback-templates.md`
- MLH Judging Guide: https://mlh.io/judging

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)

---

**Golden Rule:** Your feedback might be the difference between a team continuing their project or abandoning it. Make it count.
