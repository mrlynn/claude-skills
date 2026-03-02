#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Generate constructive feedback from scores.
  Usage: python feedback_generator.py scores.json --output feedback.md
"""

import json
import argparse

def generate_feedback(scores):
    """Generate constructive feedback."""
    team = scores['team']
    project = scores['project']
    score_data = scores['scores']
    
    md = f"# Feedback: {team} - {project}\n\n"
    
    # Strengths
    md += "## Strengths\n\n"
    high_scores = [k for k, v in score_data.items() if v >= 4]
    if high_scores:
        for category in high_scores:
            md += f"- ✅ Strong {category.replace('_', ' ')}\n"
    else:
        md += "- Good effort across all categories\n"
    
    # Areas for improvement
    md += "\n## Areas for Improvement\n\n"
    low_scores = [k for k, v in score_data.items() if v <= 2]
    if low_scores:
        for category in low_scores:
            md += f"- Consider improving {category.replace('_', ' ')}\n"
    else:
        md += "- Continue polishing all aspects\n"
    
    # Next steps
    md += "\n## Next Steps\n\n"
    md += "- Deploy to production environment\n"
    md += "- Add comprehensive documentation\n"
    md += "- Consider open sourcing the project\n"
    
    md += f"\n**Score:** {scores['total']}/25 ({scores['percentage']}%)\n"
    
    return md

def main():
    parser = argparse.ArgumentParser(description='Generate feedback')
    parser.add_argument('scores', help='Scores JSON file')
    parser.add_argument('--output', default='feedback.md')
    
    args = parser.parse_args()
    
    with open(args.scores, 'r') as f:
        scores = json.load(f)
    
    feedback = generate_feedback(scores)
    
    with open(args.output, 'w') as f:
        f.write(feedback)
    
    print(f"✅ Generated feedback for {scores['team']}")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
