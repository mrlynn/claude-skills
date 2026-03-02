#!/usr/bin/env python3
"""
Build detailed talk outline from CFP.
Usage: python outline_builder.py cfp.md --duration 45 --output outline.md
"""

import argparse

def build_outline(cfp_text, duration):
    """Build time-blocked outline."""
    # Simple structure for demo
    sections = [
        {"title": "Introduction", "duration": 5, "slides": 5},
        {"title": "Main Content Part 1", "duration": duration // 3, "slides": duration // 3},
        {"title": "Main Content Part 2", "duration": duration // 3, "slides": duration // 3},
        {"title": "Demo", "duration": duration // 6, "slides": 3},
        {"title": "Wrap-up", "duration": 5, "slides": 2},
    ]
    
    outline = f"# Talk Outline ({duration} min)\n\n"
    
    for section in sections:
        outline += f"## {section['title']} ({section['duration']} min) - {section['slides']} slides\n\n"
        outline += f"- [Content placeholder]\n"
        outline += f"- [Content placeholder]\n\n"
    
    return outline

def main():
    parser = argparse.ArgumentParser(description='Build talk outline')
    parser.add_argument('cfp', help='CFP markdown file')
    parser.add_argument('--duration', type=int, default=45, help='Talk duration in minutes')
    parser.add_argument('--output', default='outline.md')
    
    args = parser.parse_args()
    
    with open(args.cfp, 'r') as f:
        cfp_text = f.read()
    
    outline = build_outline(cfp_text, args.duration)
    
    with open(args.output, 'w') as f:
        f.write(outline)
    
    print(f"✅ Generated outline for {args.duration}-minute talk")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
