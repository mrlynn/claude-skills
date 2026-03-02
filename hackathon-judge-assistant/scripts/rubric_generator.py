#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Generate hackathon judging rubric.
  Usage: python rubric_generator.py --type corporate --output rubric.md
"""

import argparse

RUBRICS = {
    "corporate": {
        "problem_fit": 0.30,
        "technical": 0.25,
        "completeness": 0.25,
        "innovation": 0.15,
        "presentation": 0.05
    },
    "student": {
        "innovation": 0.30,
        "presentation": 0.25,
        "technical": 0.20,
        "completeness": 0.15,
        "problem_fit": 0.10
    },
    "mlh": {
        "technical": 0.30,
        "innovation": 0.25,
        "completeness": 0.25,
        "presentation": 0.15,
        "problem_fit": 0.05
    }
}

def generate_rubric(hackathon_type):
    """Generate markdown rubric."""
    if hackathon_type not in RUBRICS:
        raise ValueError(f"Unknown type: {hackathon_type}")
    
    weights = RUBRICS[hackathon_type]
    total_points = 25
    
    md = f"# Hackathon Judging Rubric: {hackathon_type.title()}\n\n"
    md += f"## Scoring (25 points total)\n\n"
    
    for category, weight in sorted(weights.items(), key=lambda x: -x[1]):
        points = weight * total_points
        md += f"### {category.replace('_', ' ').title()} ({weight*100:.0f}% - {points:.1f} points)\n\n"
        md += f"- 5: Excellent\n"
        md += f"- 4: Good\n"
        md += f"- 3: Acceptable\n"
        md += f"- 2: Needs improvement\n"
        md += f"- 1: Poor\n\n"
    
    return md

def main():
    parser = argparse.ArgumentParser(description='Generate judging rubric')
    parser.add_argument('--type', required=True, choices=RUBRICS.keys())
    parser.add_argument('--output', default='rubric.md')
    
    args = parser.parse_args()
    
    rubric = generate_rubric(args.type)
    
    with open(args.output, 'w') as f:
        f.write(rubric)
    
    print(f"✅ Generated {args.type} rubric")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
