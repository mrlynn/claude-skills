#!/usr/bin/env python3
"""
Estimate slide count from outline.
Usage: python slide_estimator.py outline.md --output estimate.json
"""

import re
import json
import argparse

def estimate_slides(outline_text):
    """Estimate slides from outline."""
    # Find sections
    pattern = r'## (.+?) \((\d+) min\) - (\d+) slides'
    sections = re.findall(pattern, outline_text)
    
    total_slides = sum(int(s[2]) for s in sections)
    total_duration = sum(int(s[1]) for s in sections)
    
    return {
        'total_slides': total_slides,
        'total_duration': total_duration,
        'pace': f"{total_slides/total_duration:.2f} slides/min",
        'sections': [
            {
                'title': s[0],
                'duration': int(s[1]),
                'slides': int(s[2]),
                'pace': 'normal' if int(s[2])/int(s[1]) < 1.2 else 'detailed'
            }
            for s in sections
        ]
    }

def main():
    parser = argparse.ArgumentParser(description='Estimate slides')
    parser.add_argument('outline', help='Outline markdown file')
    parser.add_argument('--output', default='estimate.json')
    
    args = parser.parse_args()
    
    with open(args.outline, 'r') as f:
        outline_text = f.read()
    
    estimate = estimate_slides(outline_text)
    
    with open(args.output, 'w') as f:
        json.dump(estimate, f, indent=2)
    
    print(f"✅ Estimated {estimate['total_slides']} slides for {estimate['total_duration']} minutes")
    print(f"✅ Pace: {estimate['pace']}")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
