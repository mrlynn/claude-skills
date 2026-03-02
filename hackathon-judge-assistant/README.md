# Hackathon Judge Assistant

Generate scoring rubrics and constructive feedback for hackathon submissions.

## Quick Start

```bash
# 1. Generate rubric
python scripts/rubric_generator.py --type corporate --output rubric.md

# 2. Score submission
python scripts/submission_scorer.py submission.json rubric.md --output scores.json

# 3. Generate feedback
python scripts/feedback_generator.py scores.json --output feedback.md
```

## Python Tools

- `rubric_generator.py` - Create rubrics (corporate, student, MLH)
- `submission_scorer.py` - Score submissions against rubric
- `feedback_generator.py` - Generate constructive feedback

## Hackathon Types

- **Corporate** - Problem fit focused
- **Student** - Innovation & learning focused
- **MLH** - Technical execution focused

## Principles

1. **Fair:** Consistent criteria for all
2. **Constructive:** Actionable feedback
3. **Encouraging:** Celebrate effort

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)
