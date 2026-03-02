# Conference Talk Builder

I've submitted more CFPs than I can count — some accepted, plenty rejected, and a few I'm still embarrassed about. After a while I noticed I was giving the same advice over and over: lead with the audience takeaway, not your credentials. Structure the abstract like a story arc. Time your slides so you're not racing through the last 10. So I turned all of that into this.

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
