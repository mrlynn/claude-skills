#!/usr/bin/env python3
"""
Generate conference proposal (CFP) from topic definition.
Usage: python cfp_generator.py topic.json --output cfp.md
"""

import json
import argparse

def generate_cfp(topic_data):
    """Generate CFP markdown from topic definition."""
    topic = topic_data.get('topic', 'Untitled')
    problem = topic_data.get('problem', '')
    solution = topic_data.get('solution', '')
    audience = topic_data.get('audience', 'Developers')
    takeaways = topic_data.get('takeaways', [])
    proof = topic_data.get('proof', '')
    
    # Generate hook (first 2 sentences)
    hook = f"{problem.split('.')[0]}.\n\n{solution}."
    
    cfp = f"# {topic}\n\n"
    cfp += f"## Abstract\n\n"
    cfp += f"{hook}\n\n"
    cfp += f"**Problem:** {problem}\n\n"
    cfp += f"**Solution:** {solution}\n\n"
    cfp += f"**You'll learn:**\n"
    for takeaway in takeaways:
        cfp += f"- {takeaway}\n"
    cfp += f"\n**Target audience:** {audience}\n\n"
    cfp += f"**Speaker experience:** {proof}\n"
    
    return cfp

def main():
    parser = argparse.ArgumentParser(description='Generate CFP')
    parser.add_argument('topic', help='Topic definition JSON')
    parser.add_argument('--output', default='cfp.md')
    
    args = parser.parse_args()
    
    with open(args.topic, 'r') as f:
        topic_data = json.load(f)
    
    cfp = generate_cfp(topic_data)
    
    with open(args.output, 'w') as f:
        f.write(cfp)
    
    print(f"✅ Generated CFP: {len(cfp.split())} words")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
