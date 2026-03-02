# Document Model Advisor

"Should I embed or reference?" — if I had a dollar for every time I've answered that question, I wouldn't need a day job. After 100+ schema reviews, the answer is always "it depends" but the *what it depends on* is surprisingly consistent. This skill captures the decision framework I actually use.

## Quick Start

```bash
# 1. Define entities
cp assets/entity-definition-template.json my-entities.json
# Edit with your entities and relationships

# 2. Analyze relationships
python scripts/relationship_analyzer.py my-entities.json --output analysis.json

# 3. Generate schema
python scripts/schema_optimizer.py analysis.json --output schema.json
```

## Python Tools

- `relationship_analyzer.py` - Recommend embed vs reference
- `schema_optimizer.py` - Generate MongoDB schema
- `migration_planner.py` - Plan SQL → MongoDB migration

## References

- `references/embed-vs-reference-guide.md` - The classic question
- `references/schema-patterns.md` - Common patterns

## Examples

See `assets/schema-examples.json` for e-commerce and social network schemas.

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)
