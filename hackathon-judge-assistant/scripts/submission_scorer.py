#!/usr/bin/env python3
"""
Score hackathon submission against rubric.
Usage: python submission_scorer.py submission.json rubric.md --output scores.json
"""

import json
import argparse

def score_submission(submission):
    """Score submission (simplified for demo)."""
    scores = {
        "innovation": submission.get("innovation_score", 3),
        "technical": submission.get("technical_score", 3),
        "presentation": submission.get("presentation_score", 3),
        "problem_fit": submission.get("problem_fit_score", 3),
        "completeness": submission.get("completeness_score", 3)
    }
    
    total = sum(scores.values())
    percentage = (total / 25) * 100
    
    return {
        "team": submission.get("team", "Unknown"),
        "project": submission.get("project", "Untitled"),
        "scores": scores,
        "total": total,
        "percentage": round(percentage, 1)
    }

def main():
    parser = argparse.ArgumentParser(description='Score submission')
    parser.add_argument('submission', help='Submission JSON file')
    parser.add_argument('rubric', help='Rubric file (for reference)')
    parser.add_argument('--output', default='scores.json')
    
    args = parser.parse_args()
    
    with open(args.submission, 'r') as f:
        submission = json.load(f)
    
    result = score_submission(submission)
    
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Scored submission: {result['team']}")
    print(f"✅ Total: {result['total']}/25 ({result['percentage']}%)")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
