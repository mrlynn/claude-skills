#!/usr/bin/env python3
"""
Analyze database fit for specific use case.
Usage: python use_case_matcher.py --use-case "real-time analytics" --output fit.md
"""

import argparse

USE_CASES = {
    "real-time analytics": {
        "mongodb_score": 9,
        "postgres_score": 6,
        "reasoning": "MongoDB's aggregation framework and time series collections excel at real-time analytics"
    },
    "complex joins": {
        "mongodb_score": 5,
        "postgres_score": 10,
        "reasoning": "PostgreSQL's optimized join engine handles complex relational queries better"
    },
    "iot time series": {
        "mongodb_score": 10,
        "postgres_score": 5,
        "reasoning": "MongoDB's time series collections are purpose-built for IoT sensor data"
    }
}

def analyze_fit(use_case):
    """Analyze database fit for use case."""
    if use_case not in USE_CASES:
        return f"# Use Case: {use_case}\n\nNo predefined analysis available."
    
    data = USE_CASES[use_case]
    
    md = f"# Use Case: {use_case.title()}\n\n"
    md += f"## Database Fit Scores\n\n"
    md += f"- **MongoDB:** {data['mongodb_score']}/10\n"
    md += f"- **PostgreSQL:** {data['postgres_score']}/10\n\n"
    md += f"## Analysis\n\n{data['reasoning']}\n"
    
    if data['mongodb_score'] > data['postgres_score']:
        md += f"\n**Recommendation:** MongoDB is better suited for this use case.\n"
    else:
        md += f"\n**Recommendation:** PostgreSQL is better suited for this use case.\n"
    
    return md

def main():
    parser = argparse.ArgumentParser(description='Analyze use case fit')
    parser.add_argument('--use-case', required=True)
    parser.add_argument('--output', default='fit.md')
    
    args = parser.parse_args()
    
    fit = analyze_fit(args.use_case.lower())
    
    with open(args.output, 'w') as f:
        f.write(fit)
    
    print(f"✅ Analyzed use case: {args.use_case}")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
