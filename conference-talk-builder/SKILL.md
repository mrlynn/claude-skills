---
name: conference-talk-builder
description: Generate conference talk proposals (CFPs), abstracts, and presentation outlines with slide structure and timing guidance
license: MIT
metadata:
  version: 1.0.0
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  category: public-speaking
  domain: conference-presentations
  updated: 2026-03-01
  python-tools: cfp_generator.py, outline_builder.py, slide_estimator.py
  tech-stack: python, markdown
---

# conference-talk-builder

## Trigger

Use this skill when submitting to conferences, planning technical talks, or creating presentation outlines.

**Trigger phrases:**
- "Write CFP for [topic]"
- "Generate conference abstract"
- "Build talk outline for [topic]"
- "Plan presentation structure"
- "Estimate slides for [duration]"

## Overview

Conference talk preparation has three phases:
1. **CFP (Call for Proposals)** - Get accepted
2. **Outline** - Structure your content
3. **Slides** - Deliver the talk

This skill helps with phases 1-2. It generates compelling CFPs that get accepted and detailed outlines that make slide creation easy.

## How to Use

### Quick Start
1. **Generate CFP:**
   ```bash
   python scripts/cfp_generator.py topic.json --output cfp.md
   ```

2. **Build outline:**
   ```bash
   python scripts/outline_builder.py cfp.md --duration 45 --output outline.md
   ```

3. **Estimate slides:**
   ```bash
   python scripts/slide_estimator.py outline.md --output slides-estimate.json
   ```

### Python Tools
- `scripts/cfp_generator.py` — Generate conference proposal abstracts
- `scripts/outline_builder.py` — Create detailed talk outlines with timing
- `scripts/slide_estimator.py` — Estimate slide count and content

### Reference Docs
- `references/cfp-best-practices.md` — What makes CFPs get accepted
- `references/talk-structures.md` — Proven presentation structures

### Templates & Assets
- `assets/cfp-template.md` — CFP format and examples
- `assets/outline-template.md` — Talk outline structure

## CFP Best Practices

### The Hook (First 2 Sentences)

**Bad:**
> "This talk will cover MongoDB. We'll discuss various features."

**Good:**
> "Your app is slow. In this talk, you'll learn the 3 schema design patterns that cut query time by 80%."

**Formula:** Problem → Solution with specific outcome

### The Promise (What They'll Learn)

Be specific:

**Vague:**
> "Attendees will learn about vector search."

**Specific:**
> "Attendees will learn to build a semantic search engine using MongoDB Atlas Vector Search, handling 10M documents with <100ms query latency."

### The Proof (Why You're Qualified)

**Bad:**
> "I'm a developer advocate at MongoDB."

**Good:**
> "I've built RAG systems for 5 Fortune 500 companies, processing 50M+ embeddings. I'll share production patterns and gotchas you won't find in docs."

### CFP Structure

1. **Hook** (2 sentences) - Grab attention
2. **Problem** (1 paragraph) - What pain are you solving?
3. **Solution** (1 paragraph) - Your approach
4. **Learning objectives** (3-5 bullets) - Specific takeaways
5. **Target audience** (1 sentence) - Who should attend?
6. **Proof** (1-2 sentences) - Why listen to you?

**Length:** 250-400 words for most conferences

## Talk Structures

### Structure 1: Problem-Solution-Demo (Technical Talks)

**Timeline (45 min):**
- 0-5 min: Hook + problem
- 5-15 min: Existing approaches (and why they fall short)
- 15-25 min: Your solution
- 25-40 min: Live demo
- 40-45 min: Q&A

**Best for:** Technical deep dives, new features, comparisons

### Structure 2: Story-Lesson-Application

**Timeline (45 min):**
- 0-10 min: Tell a story (project that failed/succeeded)
- 10-20 min: Extract lessons
- 20-35 min: Apply to audience's context
- 35-40 min: Action items
- 40-45 min: Q&A

**Best for:** Experience reports, lessons learned, best practices

### Structure 3: Journey (Progressive Complexity)

**Timeline (45 min):**
- 0-5 min: Start simple (basic example)
- 5-15 min: Add complexity (real-world constraints)
- 15-30 min: Handle edge cases
- 30-40 min: Production considerations
- 40-45 min: Q&A

**Best for:** Tutorial-style talks, skill building

### Structure 4: Pattern Showcase

**Timeline (45 min):**
- 0-5 min: Overview (the problem space)
- 5-15 min: Pattern 1 (with example)
- 15-25 min: Pattern 2 (with example)
- 25-35 min: Pattern 3 (with example)
- 35-40 min: When to use each
- 40-45 min: Q&A

**Best for:** Design patterns, best practices, toolkits

## Slide Estimation

**Rule of thumb:** 1 slide per minute for technical talks (includes pauses, transitions)

**45-minute talk:** ~45 slides total
- Title: 1
- Agenda: 1
- Content: ~38
- Demo: ~3 (transition slides)
- Summary: 1
- Q&A: 1

**Exceptions:**
- **Code-heavy slides:** 2-3 min per slide
- **Live demos:** Count transitions only
- **Discussion slides:** 1-2 min per slide

## Python Tool Details

### 1. CFP Generator

**Input:** Topic definition
```json
{
  "topic": "MongoDB Schema Design Patterns",
  "problem": "Developers migrating from SQL struggle with embed vs reference decisions",
  "solution": "Proven decision framework based on access patterns",
  "audience": "Backend developers, DBAs, architects",
  "takeaways": [
    "Embed vs reference decision tree",
    "5 production patterns with examples",
    "Migration strategies from relational"
  ],
  "proof": "10+ years field experience, 100+ schema reviews"
}
```

**Output:** CFP markdown with hook, problem, solution, learning objectives

### 2. Outline Builder

**Input:** CFP + duration

**Output:** Time-blocked outline with sections, subsections, slide estimates

```markdown
# MongoDB Schema Design Patterns (45 min)

## Introduction (5 min) - 5 slides
- Hook: "Your schema is your destiny"
- Common migration failures
- What we'll cover

## Pattern 1: Extended Reference (12 min) - 10 slides
- Problem: Need speed without duplication
- Solution: Reference + denormalized fields
- Example: Blog posts with author info
- Code walkthrough

...
```

### 3. Slide Estimator

**Input:** Outline markdown

**Output:** Slide count by section, timing check, content density warnings

```json
{
  "total_slides": 43,
  "total_duration": 45,
  "pace": "0.95 slides/min",
  "sections": [
    {
      "title": "Introduction",
      "slides": 5,
      "duration": 5,
      "pace": "normal"
    },
    {
      "title": "Pattern 1",
      "slides": 10,
      "duration": 12,
      "pace": "detailed",
      "warning": "Code-heavy section, may run long"
    }
  ]
}
```

## Common Pitfalls

### Pitfall 1: Vague CFPs

**Bad:**
> "We'll talk about MongoDB and AI."

**Good:**
> "Build a RAG chatbot with MongoDB Atlas Vector Search: from embeddings to production in 45 minutes."

### Pitfall 2: Too Broad

**Bad:** "Everything about MongoDB performance" (can't cover in 45 min)

**Good:** "3 Index Strategies That Cut Query Time by 80%" (focused, actionable)

### Pitfall 3: No Demos

Technical talks without live demos are less engaging. **Always include a demo**, even if small.

### Pitfall 4: Overestimating Content

**Common mistake:** Planning 60 slides for 45 minutes.

**Fix:** Cut 25% of planned content. You'll fill time with Q&A, tangents, and audience questions.

## CFP Examples

### Example 1: Technical Deep Dive

**Title:** Building RAG Systems That Don't Hallucinate

**Abstract:**
RAG systems promise accurate AI responses, but 60% of production implementations still hallucinate. Why?

In this talk, you'll learn the 5 patterns that make RAG systems trustworthy: content hashing for incremental updates, category-based score boosting, hybrid search (vector + keyword), and source attribution. We'll build a production RAG system live, handling 10M documents with <200ms query latency using MongoDB Atlas Vector Search and Voyage AI embeddings.

You'll leave with code, deployment configs, and cost optimization strategies tested across 20+ production deployments.

**Audience:** Backend developers building AI-powered applications

**Takeaways:**
- Incremental ingestion pattern (90% cost savings)
- Score boosting for retrieval quality
- Production monitoring and debugging
- Cost optimization (embeddings + storage)

### Example 2: Experience Report

**Title:** We Migrated 500 Microservices to MongoDB: Here's What We Learned

**Abstract:**
"Just use MongoDB" they said. "It'll be easy" they said.

18 months later, we'd migrated 500 microservices from PostgreSQL to MongoDB. Some succeeded. Some failed spectacularly. This is the story of what worked, what didn't, and what we'd do differently.

You'll learn the schema patterns that scaled (and the anti-patterns that didn't), the migration strategies that minimized downtime, and the organizational lessons we learned the hard way.

**Audience:** Architects, engineering leads, DBAs

**Takeaways:**
- 3 schema patterns that scaled to billions of documents
- Migration strategies (big bang vs gradual)
- Team training and knowledge transfer
- When NOT to migrate

## Talk Timing Guide

### 30-Minute Talk
- Introduction: 3 min
- Main content: 22 min (2-3 sections)
- Demo: 3 min
- Wrap-up: 2 min

### 45-Minute Talk (Most Common)
- Introduction: 5 min
- Main content: 30 min (3-4 sections)
- Demo: 7 min
- Wrap-up: 3 min

### 60-Minute Talk
- Introduction: 5 min
- Main content: 40 min (4-5 sections)
- Demo: 10 min
- Wrap-up: 5 min

**Buffer:** Always leave 5-10 min buffer for overruns and Q&A

## Quality Checklist

Before submitting CFP:
- [ ] Hook grabs attention (first 2 sentences)
- [ ] Problem clearly stated
- [ ] Solution specific (not vague)
- [ ] 3-5 concrete takeaways listed
- [ ] Target audience identified
- [ ] Proof of expertise included
- [ ] Length: 250-400 words
- [ ] No typos or grammar errors

Before creating slides:
- [ ] Outline time-blocked
- [ ] Each section has clear objective
- [ ] Demo planned (not just "show code")
- [ ] Slide count estimated
- [ ] Backup content identified (if running short)
- [ ] Cut list ready (if running long)

## When to Use vs. Other Tools

| Use `conference-talk-builder` | Use other tools |
|-------------------------------|-----------------|
| CFP writing | Slide design |
| Talk structure planning | Presentation delivery |
| Outline creation | Speaker coaching |
| Timing estimation | Video editing |

## References

- CFP Best Practices: `references/cfp-best-practices.md`
- Talk Structures: `references/talk-structures.md`
- Speaking tips: https://speaking.io
- CFP examples: https://github.com/stephlocke/lazyCFPs

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)

---

**Next steps after CFP acceptance:**
1. Build detailed outline
2. Create slide deck
3. Practice (3-5 times)
4. Record yourself
5. Iterate based on feedback
