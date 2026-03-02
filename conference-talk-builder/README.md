# Conference Talk Builder

Generate CFPs, outlines, and presentation structures for technical conferences.

## Quick Start

```bash
# 1. Create topic definition
cp assets/topic-template.json my-talk.json
# Edit with your topic

# 2. Generate CFP
python scripts/cfp_generator.py my-talk.json --output cfp.md

# 3. Build outline
python scripts/outline_builder.py cfp.md --duration 45 --output outline.md

# 4. Estimate slides
python scripts/slide_estimator.py outline.md --output estimate.json
```

## Python Tools

- `cfp_generator.py` - Generate conference proposals
- `outline_builder.py` - Create time-blocked outlines
- `slide_estimator.py` - Estimate slide count and pacing

## References

- `references/cfp-best-practices.md` - What gets accepted
- `references/talk-structures.md` - Proven formats

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)
