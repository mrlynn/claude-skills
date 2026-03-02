# Queryable Encryption Workshop

Queryable Encryption is one of MongoDB's most impressive features and also one of the hardest to demo convincingly. "Look, the data is encrypted!" doesn't land unless you tie it to something the audience cares about — like HIPAA, PCI-DSS, or FedRAMP. I built this to generate vertical-specific demos that make the compliance connection obvious.

## Quick Start

```bash
# 1. Analyze vertical
python scripts/vertical_analyzer.py --vertical healthcare --output analysis.json

# 2. Generate demo
python scripts/demo_generator.py analysis.json --output demo/

# 3. Map compliance
python scripts/compliance_mapper.py --vertical healthcare --framework HIPAA --output compliance.md
```

## Python Tools

- `vertical_analyzer.py` - Analyze industry data sensitivity
- `demo_generator.py` - Generate QE demo code
- `compliance_mapper.py` - Map to HIPAA/PCI-DSS/FISMA

## Verticals Supported

- **Healthcare** (HIPAA, HITECH)
- **Finance** (PCI-DSS, SOX)
- **Government** (FISMA, FedRAMP)

## References

- `references/qe-compliance-guide.md` - QE → compliance mapping
- `references/industry-patterns.md` - Common schema patterns

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)
