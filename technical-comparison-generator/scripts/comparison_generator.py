#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Generate comparison matrix from feature analysis.
  Usage: python comparison_generator.py features.json --output comparison.md
"""

import json
import argparse

def generate_comparison(features):
    """Generate markdown comparison."""
    competitor = features['competitor']
    
    md = f"# MongoDB vs {competitor.title()}\n\n"
    md += "## Feature Comparison\n\n"
    md += "| Feature | MongoDB | " + competitor.title() + " |\n"
    md += "|---------|---------|" + "-" * (len(competitor) + 2) + "|\n"
    
    for feature, values in features['features'].items():
        feature_name = feature.replace('_', ' ').title()
        md += f"| {feature_name} | {values['mongodb']} | {values['competitor']} |\n"
    
    md += "\n## Use Case Fit\n\n"
    md += f"**Choose MongoDB when:**\n"
    md += "- Flexible schema needed\n"
    md += "- Horizontal scaling required\n"
    md += "- Document model fits data\n\n"
    
    md += f"**Choose {competitor.title()} when:**\n"
    if competitor == 'postgres':
        md += "- Complex joins are central\n"
        md += "- Strict schema required\n"
        md += "- SQL expertise preferred\n"
    elif competitor == 'dynamodb':
        md += "- Simple key-value access\n"
        md += "- AWS-only deployment\n"
        md += "- Serverless preferred\n"
    
    return md

def main():
    parser = argparse.ArgumentParser(description='Generate comparison')
    parser.add_argument('features', help='Feature analysis JSON')
    parser.add_argument('--output', default='comparison.md')
    
    args = parser.parse_args()
    
    with open(args.features, 'r') as f:
        features = json.load(f)
    
    comparison = generate_comparison(features)
    
    with open(args.output, 'w') as f:
        f.write(comparison)
    
    print(f"✅ Generated comparison")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
