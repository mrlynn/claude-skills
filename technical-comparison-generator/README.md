# Technical Comparison Generator

I spent years doing competitive positioning at MongoDB, and the hardest part isn't knowing your product — it's being fair about the other guy's. Nothing kills credibility faster than a comparison that reads like a hit piece. This skill generates honest, balanced technical comparisons. Yes, it was built with MongoDB in mind, but the framework works for any "us vs them" analysis.

## Quick Start

```bash
# 1. Analyze features
python scripts/feature_analyzer.py --competitor postgres --output features.json

# 2. Generate comparison
python scripts/comparison_generator.py features.json --output comparison.md

# 3. Analyze use case fit
python scripts/use_case_matcher.py --use-case "real-time analytics" --output fit.md
```

## Python Tools

- `feature_analyzer.py` - Compare MongoDB vs competitor features
- `comparison_generator.py` - Generate markdown comparison matrix
- `use_case_matcher.py` - Analyze database fit for use cases

## Competitors Supported

- PostgreSQL
- DynamoDB
- Cassandra

## Principles

1. **Be fair** - Acknowledge competitor strengths
2. **Focus on use case** - Not "better/worse"
3. **Be specific** - Avoid vague claims

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)
