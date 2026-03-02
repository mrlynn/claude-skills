#!/usr/bin/env python3
"""
Analyze feature differences between MongoDB and competitor.
Usage: python feature_analyzer.py --competitor postgres --output features.json
"""

import json
import argparse

COMPETITORS = {
    "postgres": {
        "data_model": {"mongodb": "Document (flexible)", "competitor": "Relational (strict)"},
        "scaling": {"mongodb": "Horizontal (sharding)", "competitor": "Vertical (larger machines)"},
        "transactions": {"mongodb": "Multi-document ACID", "competitor": "Full ACID"},
        "query_language": {"mongodb": "MQL (JSON-like)", "competitor": "SQL (ANSI)"},
        "joins": {"mongodb": "$lookup (limited)", "competitor": "Full SQL joins"},
        "vector_search": {"mongodb": "Native (Atlas)", "competitor": "pgvector extension"}
    },
    "dynamodb": {
        "data_model": {"mongodb": "Document", "competitor": "Key-value"},
        "scaling": {"mongodb": "Horizontal (sharding)", "competitor": "Serverless (auto)"},
        "query_language": {"mongodb": "MQL (rich)", "competitor": "Limited (key-value)"},
        "pricing": {"mongodb": "Compute + storage", "competitor": "Pay-per-request"},
        "vendor_lock": {"mongodb": "Portable", "competitor": "AWS only"}
    },
    "cassandra": {
        "data_model": {"mongodb": "Document", "competitor": "Wide-column"},
        "scaling": {"mongodb": "Horizontal", "competitor": "Horizontal (linear)"},
        "consistency": {"mongodb": "Strong (configurable)", "competitor": "Eventual (tunable)"},
        "operations": {"mongodb": "Simpler", "competitor": "Complex"},
        "write_performance": {"mongodb": "High", "competitor": "Very high"}
    }
}

def analyze_features(competitor):
    """Analyze features for competitor."""
    if competitor not in COMPETITORS:
        raise ValueError(f"Unknown competitor: {competitor}")
    
    return {
        "competitor": competitor,
        "features": COMPETITORS[competitor]
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze database features')
    parser.add_argument('--competitor', required=True, choices=COMPETITORS.keys())
    parser.add_argument('--output', default='features.json')
    
    args = parser.parse_args()
    
    analysis = analyze_features(args.competitor)
    
    with open(args.output, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"✅ Analyzed MongoDB vs {args.competitor}")
    print(f"✅ {len(analysis['features'])} features compared")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
