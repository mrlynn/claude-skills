#!/usr/bin/env python3
"""
Match candidate experience to job requirements.
Usage: python resume_matcher.py master-resume.json job-analysis.json --output matches.json
"""

import json
import argparse
from datetime import datetime

def calculate_keyword_overlap(text, keywords):
    """Calculate what % of keywords appear in text."""
    text_lower = text.lower()
    found = sum(1 for kw in keywords if kw.lower() in text_lower)
    return found / len(keywords) if keywords else 0

def calculate_recency_score(dates):
    """Score based on how recent the experience is."""
    # Parse dates like "2020-Present" or "2018-2020"
    if 'present' in dates.lower():
        return 1.0  # Current role = highest score
    
    # Extract end year
    import re
    years = re.findall(r'\d{4}', dates)
    if not years:
        return 0.5  # Can't parse, assume medium
    
    end_year = int(years[-1])
    current_year = datetime.now().year
    years_ago = current_year - end_year
    
    # Score: 1.0 for 0-1 years ago, 0.5 for 5+ years ago
    return max(0.3, 1.0 - (years_ago * 0.1))

def score_achievement(achievement, job_keywords):
    """Score individual achievement by keyword overlap and quantification."""
    # Check for numbers (quantified achievement)
    import re
    has_numbers = bool(re.search(r'\d+', achievement))
    quantification_score = 0.3 if has_numbers else 0
    
    # Keyword overlap
    keyword_score = calculate_keyword_overlap(achievement, job_keywords) * 0.7
    
    return keyword_score + quantification_score

def match_experience(experience_item, job_analysis):
    """Match a single experience item to job requirements."""
    keywords = job_analysis.get('keywords', [])
    required_skills = job_analysis.get('required_skills', [])
    all_keywords = keywords + required_skills
    
    # Calculate component scores
    keyword_overlap = calculate_keyword_overlap(
        f"{experience_item['title']} {' '.join(experience_item.get('achievements', []))}",
        all_keywords
    )
    
    recency = calculate_recency_score(experience_item.get('dates', ''))
    
    # Score achievements
    achievements = experience_item.get('achievements', [])
    achievement_scores = [score_achievement(a, all_keywords) for a in achievements]
    avg_achievement_score = sum(achievement_scores) / len(achievement_scores) if achievement_scores else 0
    
    # Title similarity (simple: does job title contain any keywords?)
    title_overlap = calculate_keyword_overlap(experience_item['title'], all_keywords)
    
    # Overall relevance score (weighted)
    relevance_score = (
        keyword_overlap * 0.3 +
        recency * 0.2 +
        avg_achievement_score * 0.3 +
        title_overlap * 0.2
    )
    
    # Find matched achievements (above threshold)
    matched_achievements = [
        a for a, score in zip(achievements, achievement_scores) if score > 0.3
    ]
    
    return {
        'title': experience_item['title'],
        'company': experience_item.get('company', ''),
        'dates': experience_item.get('dates', ''),
        'relevance_score': round(relevance_score, 2),
        'keyword_overlap': round(keyword_overlap, 2),
        'recency_score': round(recency, 2),
        'matched_achievements': matched_achievements[:5],  # Top 5
        'total_achievements': len(achievements)
    }

def match_resume(resume, job_analysis):
    """Match entire resume to job requirements."""
    # Match skills
    candidate_skills = set([s.lower() for s in resume.get('skills', [])])
    required_skills = set([s.lower() for s in job_analysis.get('required_skills', [])])
    preferred_skills = set([s.lower() for s in job_analysis.get('preferred_skills', [])])
    
    matched_required = list(candidate_skills & required_skills)
    matched_preferred = list(candidate_skills & preferred_skills)
    missing_required = list(required_skills - candidate_skills)
    missing_preferred = list(preferred_skills - candidate_skills)
    
    # Match experience
    experience_matches = []
    for exp in resume.get('experience', []):
        match = match_experience(exp, job_analysis)
        experience_matches.append(match)
    
    # Sort by relevance
    experience_matches.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # Overall match score
    skill_match = len(matched_required) / len(required_skills) if required_skills else 0
    exp_match = experience_matches[0]['relevance_score'] if experience_matches else 0
    overall_match = (skill_match * 0.4 + exp_match * 0.6)
    
    # Generate tailoring suggestions
    suggestions = []
    if missing_required:
        suggestions.append(f"Consider adding these required skills if you have them: {', '.join(missing_required[:3])}")
    if experience_matches:
        top_exp = experience_matches[0]
        suggestions.append(f"Lead with '{top_exp['title']}' (highest relevance: {top_exp['relevance_score']})")
    
    return {
        'overall_match': round(overall_match, 2),
        'skill_match': round(skill_match, 2),
        'matched_required_skills': matched_required,
        'matched_preferred_skills': matched_preferred,
        'missing_required_skills': missing_required,
        'missing_preferred_skills': missing_preferred,
        'experience_matches': experience_matches,
        'tailoring_suggestions': suggestions
    }

def main():
    parser = argparse.ArgumentParser(description='Match resume to job requirements')
    parser.add_argument('resume', help='Master resume JSON file')
    parser.add_argument('job_analysis', help='Job analysis JSON file (from job_analyzer.py)')
    parser.add_argument('--output', help='Output JSON file', default=None)
    
    args = parser.parse_args()
    
    print(f"Loading resume: {args.resume}")
    with open(args.resume, 'r') as f:
        resume = json.load(f)
    
    print(f"Loading job analysis: {args.job_analysis}")
    with open(args.job_analysis, 'r') as f:
        job_analysis = json.load(f)
    
    print("\nMatching resume to job requirements...")
    matches = match_resume(resume, job_analysis)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(matches, f, indent=2)
        print(f"\n✅ Matches saved to {args.output}")
    else:
        print("\n" + "="*60)
        print("RESUME-JOB MATCH ANALYSIS")
        print("="*60)
        print(f"\nOverall Match: {matches['overall_match']*100:.0f}%")
        print(f"Skill Match: {matches['skill_match']*100:.0f}%")
        
        print(f"\n✅ Matched Required Skills ({len(matches['matched_required_skills'])}):")
        for skill in matches['matched_required_skills']:
            print(f"  - {skill}")
        
        print(f"\n❌ Missing Required Skills ({len(matches['missing_required_skills'])}):")
        for skill in matches['missing_required_skills']:
            print(f"  - {skill}")
        
        print(f"\nTop Experience Matches:")
        for exp in matches['experience_matches'][:3]:
            print(f"\n  {exp['title']} ({exp['company']})")
            print(f"  Relevance: {exp['relevance_score']*100:.0f}% | Keywords: {exp['keyword_overlap']*100:.0f}%")
            print(f"  Matched Achievements:")
            for ach in exp['matched_achievements'][:2]:
                print(f"    - {ach[:80]}...")
        
        print(f"\n💡 Tailoring Suggestions:")
        for suggestion in matches['tailoring_suggestions']:
            print(f"  - {suggestion}")

if __name__ == '__main__':
    main()
