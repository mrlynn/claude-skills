# Developer Day Curriculum Generator

Ok, admittedly, this one will probably not be useful for you, unless you're on the MongoDB DevRel team... we do workshops... and I wrote this to help with generating new agendas, etc... With it you can generate workshop agendas and hands-on curriculum for customer developer days, technical training, and field engagements.

## Quick Start

### 1. Create customer profile

Edit `assets/customer-profile-template.json` with your customer's information:
```bash
cp assets/customer-profile-template.json customer.json
# Edit customer.json with their tech stack, goals, experience level
```

### 2. Analyze audience

```bash
python scripts/audience_analyzer.py customer.json --output analysis.json
```

**Output:** Recommended topics, pacing, and experience level

### 3. Generate agenda

```bash
python scripts/agenda_generator.py analysis.json \
  --duration 6 \
  --start-time "9:00 AM" \
  --include-lunch \
  --output agenda.md
```

**Output:** Time-blocked agenda with lectures and exercises

### 4. Create exercise scaffolding

```bash
python scripts/exercise_scaffolder.py agenda.md --output exercises/
```

**Output:** Exercise directories with starter code, solutions, and extensions

### 5. Customize and deliver

- Fill in starter code with customer-specific examples
- Complete solution code
- Test all exercises on fresh environment
- Deliver workshop!

## Python Tools

### audience_analyzer.py
Analyzes customer profile and recommends workshop approach.

**Features:**
- Determines experience level (beginner/intermediate/advanced)
- Recommends topics based on goals and tech stack
- Calculates optimal pacing (lecture/exercise/break ratios)
- Generates industry-specific focus areas
- Lists prerequisites

**Example:**
```bash
python scripts/audience_analyzer.py fintech-customer.json --output analysis.json
```

### agenda_generator.py
### We won't always have advanced knowledge of the audience, but roll with me here, ok?
Generates time-blocked agenda from audience analysis.

**Features:**
- Time-blocked schedule with topics and breaks
- Lecture + exercise pattern
- Automatic break scheduling
- Lunch break for full-day workshops
- Markdown output

**Options:**
```bash
python scripts/agenda_generator.py analysis.json \
  --duration 6 \           # Hours
  --start-time "9:00 AM" \  # Start time
  --include-lunch \         # Add lunch break
  --output agenda.md
```

### exercise_scaffolder.py
Generates hands-on exercise templates from agenda.

**Features:**
- Creates exercise directory structure
- Generates README with instructions
- Creates starter code with TODOs
- Provides solution placeholders
- Includes extension challenges

**Example:**
```bash
python scripts/exercise_scaffolder.py agenda.md --output exercises/
```

**Output structure:**
```
exercises/
├── 01-schema-design/
│   ├── README.md
│   ├── starter/
│   │   ├── app.js
│   │   ├── package.json
│   │   └── .env.example
│   ├── solution/
│   │   └── app.js
│   └── extension/
│       └── challenges.md
├── 02-aggregation/
│   └── ...
```

## Reference Documentation

### workshop-design-patterns.md
Proven workshop structures and pacing strategies:
- The Golden Ratio (40-50-10)
- Hook-Demo-Practice-Review pattern
- Progressive disclosure
- Scaffolding levels
- Fast finisher strategies
- Common failure modes

### customer-engagement-best-practices.md
Field engagement patterns from 50+ developer days:
- Pre-workshop preparation
- Day-of setup checklist
- Energy management
- Exercise facilitation
- Handling technical issues
- Post-workshop follow-up

## Template Assets

### customer-profile-template.json
Structured customer profile format:
```json
{
  "company": "Acme Corp",
  "industry": "FinTech",
  "audience_size": 20,
  "experience_level": "intermediate",
  "mongodb_experience": "beginner",
  "goals": ["Migration", "Schema design"],
  "constraints": ["6 hours", "Firewall restrictions"]
}
```

### Agenda Templates
- `agenda-template-halfday.md` - 3-4 hour workshop
- `agenda-template-fullday.md` - 6-8 hour workshop

### feedback-survey.md
Post-workshop feedback template:
- Overall rating
- Learning objectives met
- Pace appropriateness
- Most/least valuable topics
- Net Promoter Score
- Follow-up requests

## Workflow Example

**Scenario:** Plan a 6-hour MongoDB developer day for FinTech customer

**Step 1: Create profile**
```json
{
  "company": "FinTech Corp",
  "audience_size": 25,
  "experience_level": "intermediate",
  "mongodb_experience": "beginner",
  "goals": ["PostgreSQL migration", "Schema design", "Transactions"],
  "constraints": ["6 hours", "Atlas firewall blocked"]
}
```

**Step 2: Analyze**
```bash
python scripts/audience_analyzer.py fintech.json --output analysis.json
```

Output: Recommends intermediate level, focus on migration patterns + transactions

**Step 3: Generate agenda**
```bash
python scripts/agenda_generator.py analysis.json \
  --duration 6 \
  --start-time "9:00 AM" \
  --include-lunch \
  --output fintech-agenda.md
```

Output: 6-hour agenda with 4 topics, 4 exercises, lunch, 3 breaks

**Step 4: Create exercises**
```bash
python scripts/exercise_scaffolder.py fintech-agenda.md --output exercises/
```

Output: 4 exercise directories with starter/solution/extension

**Step 5: Customize**
- Fill in PostgreSQL → MongoDB migration examples
- Add FinTech-specific use cases (transactions, compliance)
- Test all exercises

**Step 6: Deliver & follow up**
- Run workshop
- Collect feedback
- Share resources
- Schedule follow-up

## Pacing Guidelines

| Duration | Topics | Exercises | Breaks |
|----------|--------|-----------|--------|
| **Half-day (3-4h)** | 2-3 | 2 | 1 |
| **Full-day (6-8h)** | 4-6 | 4-5 | 3+ |
| **Multi-day** | 8-12 | 8-10 | Lunch + breaks each day |

**Rule of thumb:** 1 topic per hour (30 min lecture, 30 min exercise)

## The Golden Ratio

- **40%** lecture/demonstration
- **50%** hands-on exercises
- **10%** breaks

Adults learn by doing. Maximize hands-on time.

## Quality Checklist

Before delivering:
- [ ] Agenda has clear learning objectives
- [ ] Time blocks add up to total duration
- [ ] Breaks every 60-90 minutes
- [ ] Each exercise has starter code + solution
- [ ] Extension challenges for fast finishers
- [ ] Setup instructions tested
- [ ] Backup plan for connectivity issues
- [ ] Feedback survey prepared
- [ ] Follow-up resources compiled

## Common Patterns

### Hook Opening
Start with a compelling demo, not slides:
> "Watch this." [10-min live demo]
> "That's what you'll build today."

### Progressive Complexity
Layer exercises from simple to complex:
1. Basic CRUD
2. Add indexes
3. Add aggregation
4. Add transactions

### Fast Finisher Extensions
Always have bonus challenges:
- Add validation
- Optimize performance
- Implement caching
- Add monitoring

## Follow-Up Strategy

**Same day:** Share slides + exercise repo
**Next day:** Thank you + resources
**One week:** Check-in on progress
**One month:** "How's it going?" follow-up

## Tips

### For Enterprise Customers
- Use their industry terminology
- Include compliance/security topics
- Formal tone, structured approach

### For Startups
- Move faster, less hand-holding
- Focus on "get it working" quickly
- Include scaling considerations

### For Mixed Audiences
- Morning: Core fundamentals (everyone)
- Afternoon: Breakout tracks (beginner vs advanced)

## Success Metrics

You nailed it if:
- ✅ Participants completed exercises
- ✅ Questions were engaged, not confused
- ✅ Energy stayed high throughout
- ✅ Positive feedback (NPS > 8)
- ✅ Follow-up requests received

## Dependencies

**Python:** Standard library only (no external packages)

## References

- Workshop Design Patterns: `references/workshop-design-patterns.md`
- Customer Engagement Best Practices: `references/customer-engagement-best-practices.md`
- Adult Learning Theory: https://en.wikipedia.org/wiki/Andragogy
- MongoDB Developer Days: [Internal MongoDB resource]

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)

---

**Next steps:** Create your customer profile and start planning!
