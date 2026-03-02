---
name: developer-day-curriculum
description: Generate workshop agendas and hands-on curriculum for customer developer days, technical training sessions, and field engagements
license: MIT
metadata:
  version: 1.0.0
  author: MongoDB Developer Relations
  category: education
  domain: technical-training
  updated: 2026-03-01
  python-tools: audience_analyzer.py, agenda_generator.py, exercise_scaffolder.py
  tech-stack: python, json, markdown
---

# developer-day-curriculum

## Trigger

Use this skill when planning customer developer days, field workshops, technical training sessions, or conference tutorials.

**Trigger phrases:**
- "Plan a developer day for [customer]"
- "Create workshop agenda"
- "Design hands-on training"
- "Build curriculum for [topic]"
- "Generate developer day schedule"

## Overview

Developer days require careful planning: the right topics, appropriate depth, hands-on exercises that work, and perfect pacing. This skill analyzes customer needs, generates time-blocked agendas, creates scaffolded exercises, and produces follow-up materials.

**Not for:** Self-paced courses or recorded content. This is for **live, interactive workshops** with hands-on components.

## How to Use

### Quick Start
1. **Analyze audience:**
   ```bash
   python scripts/audience_analyzer.py customer-profile.json --output analysis.json
   ```

2. **Generate agenda:**
   ```bash
   python scripts/agenda_generator.py analysis.json --duration 6 --output agenda.md
   ```

3. **Create exercises:**
   ```bash
   python scripts/exercise_scaffolder.py agenda.md --output exercises/
   ```

### Python Tools
- `scripts/audience_analyzer.py` — Analyze customer tech stack, experience level, goals
- `scripts/agenda_generator.py` — Generate time-blocked agenda with topics and breaks
- `scripts/exercise_scaffolder.py` — Create hands-on exercise templates and solution code

### Reference Docs
- `references/workshop-design-patterns.md` — Proven workshop structures and pacing
- `references/customer-engagement-best-practices.md` — Field engagement patterns from 50+ developer days

### Templates & Assets
- `assets/agenda-template-halfday.md` — 3-4 hour workshop template
- `assets/agenda-template-fullday.md` — 6-8 hour workshop template
- `assets/exercise-template.md` — Hands-on exercise structure
- `assets/feedback-survey.md` — Post-workshop feedback template

## Architecture Decisions

### Why Audience Analysis First

Different audiences need different approaches:

| Audience Type | Approach | Example Topics |
|---------------|----------|----------------|
| **Beginners** | Guided, step-by-step | "Intro to MongoDB", "Your First Query" |
| **Intermediate** | Problem-solving focused | "Schema Design Workshop", "Aggregation Deep Dive" |
| **Advanced** | Architecture & optimization | "Performance Tuning", "Sharding Strategies" |
| **Mixed** | Layered (core + advanced breakouts) | Morning: Foundations, Afternoon: Tracks |

**Tool:** `audience_analyzer.py` categorizes audience and recommends depth.

### Time-Blocking Strategy

Attention spans are finite. Research shows:
- **10-15 min:** Maximum lecture without interaction
- **45-60 min:** Maximum before needing a break
- **90 min:** Maximum hands-on exercise session

**Agenda structure:**
```
09:00-09:15  Welcome & Introductions (15 min)
09:15-09:45  Topic 1: Lecture (30 min)
09:45-10:30  Exercise 1: Hands-on (45 min)
10:30-10:45  Break (15 min)
10:45-11:15  Topic 2: Lecture (30 min)
...
```

**Pattern:** Lecture → Exercise → Break (repeat)

### Hands-On Exercise Philosophy

**Progressive Disclosure:**
1. **Starter code provided** (80% complete)
2. **Clear TODOs** with hints
3. **Solution available** but not shown upfront
4. **Extension challenges** for fast finishers

**Anti-pattern:** Blank slate ("Build X from scratch"). Most participants fail.

**Good pattern:** Guided scaffolding with specific gaps to fill.

### Pacing Rules

| Duration | Topics | Exercises | Breaks |
|----------|--------|-----------|--------|
| **Half-day (3-4h)** | 2-3 topics | 2 exercises | 1 break |
| **Full-day (6-8h)** | 4-6 topics | 4-5 exercises | 3+ breaks |
| **Multi-day** | 8-12 topics | 8-10 exercises | Lunch + breaks each day |

**Rule of thumb:** 1 topic per hour (30 min lecture, 30 min exercise/discussion).

### Follow-Up Materials

Participants forget 70% within 24 hours without reinforcement. Provide:
- **Slide deck** (PDF, not editable)
- **Exercise repo** (GitHub with solutions)
- **Resource links** (docs, tutorials, videos)
- **Next steps** (suggested learning path)
- **Contact info** (Slack, email, office hours)

## Generated Output Structure

### Agenda (Markdown)
```markdown
# MongoDB Developer Day - [Customer Name]
**Date:** [Date] | **Duration:** 6 hours | **Level:** Intermediate

## Goals
- [Learning objective 1]
- [Learning objective 2]

## Prerequisites
- Basic MongoDB knowledge
- Laptop with [requirements]

## Schedule

### Morning Session (9:00 AM - 12:00 PM)

#### 9:00-9:15 - Welcome & Introductions (15 min)
- Icebreaker
- Agenda overview
- Wi-Fi and logistics

#### 9:15-9:45 - Topic 1: [Title] (30 min)
**Learning objective:** [What participants will learn]
**Key concepts:** [Bullet list]

#### 9:45-10:30 - Exercise 1: [Title] (45 min)
**Goal:** [What participants will build]
**Starter code:** `exercises/01-topic-name/`
**Success criteria:** [How to know you're done]

...

## Follow-Up Resources
- [Links]
```

### Exercise Structure
```
exercises/
├── 01-topic-name/
│   ├── README.md          # Instructions
│   ├── starter/           # Starter code (80% complete)
│   │   └── app.js
│   ├── solution/          # Complete solution
│   │   └── app.js
│   └── extension/         # Bonus challenges
│       └── challenges.md
```

## Python Tool Details

### 1. Audience Analyzer

**Purpose:** Analyze customer profile and recommend topics/depth.

**Input:** Customer profile JSON
```json
{
  "company": "Acme Corp",
  "industry": "FinTech",
  "audience_size": 25,
  "experience_level": "mixed",
  "current_stack": ["PostgreSQL", "Redis", "Python"],
  "mongodb_experience": "beginner",
  "goals": [
    "Migrate from PostgreSQL to MongoDB",
    "Learn schema design patterns"
  ],
  "constraints": [
    "6 hour duration",
    "Must include hands-on exercises"
  ]
}
```

**Output:** Analysis JSON
```json
{
  "recommended_level": "intermediate",
  "suggested_topics": [
    "MongoDB fundamentals (quick refresher)",
    "Relational to document migration patterns",
    "Schema design workshop",
    "Aggregation pipeline deep dive"
  ],
  "pacing": {
    "lecture_ratio": 0.4,
    "exercise_ratio": 0.5,
    "break_ratio": 0.1
  },
  "focus_areas": [
    "Emphasize schema design (coming from relational)",
    "Include PostgreSQL → MongoDB migration example",
    "Address transaction concerns (FinTech requirement)"
  ]
}
```

### 2. Agenda Generator

**Purpose:** Generate time-blocked agenda from analysis.

**Usage:**
```bash
python scripts/agenda_generator.py analysis.json \
  --duration 6 \
  --start-time "9:00 AM" \
  --output agenda.md
```

**Options:**
- `--duration` - Hours (default: 6)
- `--start-time` - Start time (default: 9:00 AM)
- `--include-lunch` - Add lunch break for full-day
- `--format` - Output format (markdown, html, pdf)

**Output:** Markdown agenda with:
- Time-blocked schedule
- Topic descriptions
- Exercise placeholders
- Break timing
- Prerequisites and setup instructions

### 3. Exercise Scaffolder

**Purpose:** Generate hands-on exercise templates from agenda.

**Usage:**
```bash
python scripts/exercise_scaffolder.py agenda.md --output exercises/
```

**Generates:**
- Exercise directory structure
- README with instructions
- Starter code templates
- Solution placeholders
- Extension challenges

**Example output:**
```
exercises/
├── 01-schema-design/
│   ├── README.md
│   ├── starter/
│   │   ├── schema.js        # 80% complete with TODOs
│   │   └── sample-data.json
│   ├── solution/
│   │   └── schema.js        # Complete solution
│   └── extension/
│       └── challenges.md    # Bonus challenges
```

## Workflow Example

**Scenario:** Plan a 6-hour MongoDB developer day for FinTech customer

**Step 1: Create customer profile**
```json
{
  "company": "FinTech Corp",
  "audience_size": 20,
  "experience_level": "intermediate",
  "current_stack": ["PostgreSQL", "Python", "AWS"],
  "mongodb_experience": "beginner",
  "goals": ["Migration from PostgreSQL", "Schema design"],
  "constraints": ["6 hours", "Must include transactions"]
}
```

**Step 2: Analyze audience**
```bash
python scripts/audience_analyzer.py fintech-profile.json --output analysis.json
```

Output: Recommends intermediate level, focus on migration patterns and transactions

**Step 3: Generate agenda**
```bash
python scripts/agenda_generator.py analysis.json \
  --duration 6 \
  --start-time "9:00 AM" \
  --include-lunch \
  --output fintech-agenda.md
```

Output: 6-hour agenda with 4 topics, 4 exercises, lunch, 2 breaks

**Step 4: Create exercises**
```bash
python scripts/exercise_scaffolder.py fintech-agenda.md --output exercises/
```

Output: 4 exercise directories with starter code, solutions, extensions

**Step 5: Customize**
- Fill in starter code with FinTech-specific examples
- Add real PostgreSQL → MongoDB migration example
- Customize transaction exercise for financial use case

**Step 6: Deliver**
- Present agenda
- Walk through exercises
- Collect feedback
- Share follow-up resources

## Common Patterns

### Pattern 1: The "Hook" Opening

Start with a compelling demo, not slides.

**Bad:**
> "Welcome. Today we'll learn about MongoDB. Here are 30 slides..."

**Good:**
> "Let me show you something cool." [Live demo: Build a real-time dashboard in 10 minutes]
> "That's what you'll build today. Let's get started."

### Pattern 2: "You Try" Checkpoints

Every 15 minutes, pause for a quick "you try" moment.

**Example:**
> "I just showed you how to create an index. Open your terminal and try it with your dataset. 2 minutes. Go!"

Prevents passive watching.

### Pattern 3: Progressive Complexity

Start simple, layer on complexity.

**Exercise 1:** Basic CRUD operations
**Exercise 2:** Add indexes for performance
**Exercise 3:** Add aggregation pipeline
**Exercise 4:** Add transactions and error handling

Each builds on the previous.

### Pattern 4: Real-World Context

Use customer's industry for examples.

**Generic (boring):**
> "Here's a user schema..."

**Industry-specific (engaging):**
> "Here's how to model a financial transaction with MongoDB..."

### Pattern 5: Fast Finisher Extensions

Always have bonus challenges ready.

```markdown
## Exercise 1: Basic Schema Design

**Success Criteria:**
- [x] Created schema
- [x] Inserted sample data
- [x] Queried data

**Done early? Try these extensions:**
1. Add validation rules
2. Create compound indexes
3. Add data migration script
```

Keeps advanced participants engaged.

## Timing Anti-Patterns

### ❌ Too Much Content
Cramming 12 topics into 6 hours. Result: Rushed, no hands-on time.

**Fix:** 4-6 topics maximum for 6 hours.

### ❌ No Breaks
Running 3 hours straight without a break.

**Fix:** Break every 60-90 minutes minimum.

### ❌ Long Lectures
45-minute lecture with no interaction.

**Fix:** 15-minute chunks with "you try" checkpoints.

### ❌ Blank Slate Exercises
"Build a complete app from scratch in 45 minutes."

**Fix:** Provide 80% starter code with specific TODOs.

### ❌ Skipping Setup Time
Jumping straight into exercises without verifying everyone's environment works.

**Fix:** 15-minute setup verification at start.

## Quality Checklist

Before delivering:
- [ ] Agenda has clear learning objectives
- [ ] Time blocks total to actual duration
- [ ] Breaks scheduled every 60-90 minutes
- [ ] Each exercise has starter code + solution
- [ ] Extension challenges ready for fast finishers
- [ ] Setup instructions tested on fresh machine
- [ ] Backup plan if live demos fail
- [ ] Feedback survey prepared
- [ ] Follow-up resources compiled
- [ ] Contact info for post-workshop questions

## When to Use Different Formats

| Format | Best For | Example |
|--------|----------|---------|
| **Half-day (3-4h)** | Conference tutorials, intro workshops | "Intro to Vector Search" |
| **Full-day (6-8h)** | Customer developer days, deep dives | "MongoDB Schema Design Workshop" |
| **Multi-day (2-3 days)** | Comprehensive training, bootcamps | "MongoDB Developer Bootcamp" |
| **Workshop series** | Ongoing enablement | Weekly 2-hour sessions over 4 weeks |

## Customization Tips

### For Enterprise Customers
- Use their industry terminology
- Reference their specific use cases
- Include compliance/security topics
- Provide enterprise deployment examples

### For Startups
- Move faster, less hand-holding
- Focus on practical "get it working" approach
- Include scaling considerations
- Share cost optimization tips

### For Mixed Audiences
- Morning: Core fundamentals (everyone)
- Afternoon: Breakout tracks (beginner vs advanced)
- Provide self-paced catch-up materials

## Follow-Up Strategy

**Immediately after (same day):**
- Share slide deck PDF
- Send GitHub repo link with exercises/solutions
- Collect feedback survey

**Next day:**
- Send thank you email
- Share additional resources
- Offer office hours

**One week later:**
- Check in on progress
- Answer questions
- Share related content

**One month later:**
- Follow-up on original goals
- Offer advanced workshop if interest

## References

- Workshop design patterns: `references/workshop-design-patterns.md`
- Field engagement best practices: `references/customer-engagement-best-practices.md`
- Adult learning theory: https://en.wikipedia.org/wiki/Andragogy
- Hands-on exercise design: https://teaching.cornell.edu/resource/active-learning

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)

---

**Next steps after generating curriculum:**
1. Customize exercises with customer-specific examples
2. Test all hands-on exercises on fresh environment
3. Prepare backup demos (in case of connectivity issues)
4. Create feedback survey
5. Compile follow-up resources
