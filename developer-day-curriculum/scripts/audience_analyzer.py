#!/usr/bin/env python3
"""
Analyze customer profile and recommend workshop topics and depth.
Usage: python audience_analyzer.py customer-profile.json --output analysis.json
"""

import json
import argparse

def analyze_experience_level(profile):
    """Determine overall experience level."""
    mongodb_exp = profile.get('mongodb_experience', 'beginner').lower()
    general_exp = profile.get('experience_level', 'intermediate').lower()
    
    # Map to our standard levels
    level_map = {
        'none': 'beginner',
        'beginner': 'beginner',
        'some': 'intermediate',
        'intermediate': 'intermediate',
        'advanced': 'advanced',
        'expert': 'advanced',
        'mixed': 'intermediate'  # Default to intermediate for mixed
    }
    
    mongodb_level = level_map.get(mongodb_exp, 'intermediate')
    
    # If MongoDB experience is low but general experience is high, use intermediate
    if mongodb_level == 'beginner' and general_exp in ['advanced', 'expert']:
        return 'intermediate'
    
    return mongodb_level

def recommend_topics(profile, experience_level):
    """Recommend topics based on profile and experience."""
    goals = profile.get('goals', [])
    current_stack = profile.get('current_stack', [])
    industry = profile.get('industry', '').lower()
    
    topics = []
    
    # Always start with fundamentals if beginner
    if experience_level == 'beginner':
        topics.append({
            'title': 'MongoDB Fundamentals',
            'duration_min': 45,
            'description': 'Introduction to MongoDB, document model, basic CRUD operations'
        })
    
    # Migration topics if coming from relational
    if any(db in str(current_stack).lower() for db in ['postgres', 'mysql', 'sql', 'oracle']):
        topics.append({
            'title': 'Relational to Document Migration',
            'duration_min': 60,
            'description': 'Patterns for migrating from SQL to MongoDB, data modeling differences'
        })
    
    # Schema design (almost always relevant)
    topics.append({
        'title': 'Schema Design Workshop',
        'duration_min': 90,
        'description': 'Embedding vs referencing, schema design patterns for your use case'
    })
    
    # Goal-based topics
    goal_keywords = ' '.join(goals).lower()
    
    if 'performance' in goal_keywords or 'scale' in goal_keywords:
        topics.append({
            'title': 'Performance Optimization',
            'duration_min': 75,
            'description': 'Indexes, explain plans, aggregation optimization'
        })
    
    if 'search' in goal_keywords or 'vector' in goal_keywords or 'ai' in goal_keywords:
        topics.append({
            'title': 'Atlas Vector Search & AI',
            'duration_min': 90,
            'description': 'Building RAG applications with MongoDB Atlas Vector Search'
        })
    
    if 'transaction' in goal_keywords or industry in ['fintech', 'finance', 'banking']:
        topics.append({
            'title': 'Transactions & Data Integrity',
            'duration_min': 60,
            'description': 'Multi-document transactions, consistency guarantees'
        })
    
    if 'aggregation' in goal_keywords or experience_level == 'advanced':
        topics.append({
            'title': 'Aggregation Pipeline Deep Dive',
            'duration_min': 90,
            'description': 'Complex aggregations, optimization techniques, real-world examples'
        })
    
    return topics

def calculate_pacing(duration_hours, experience_level):
    """Calculate recommended time allocation."""
    # Beginners need more explanation, less hands-on
    # Advanced participants need less lecture, more hands-on
    
    pacing_map = {
        'beginner': {
            'lecture_ratio': 0.45,
            'exercise_ratio': 0.45,
            'break_ratio': 0.10
        },
        'intermediate': {
            'lecture_ratio': 0.40,
            'exercise_ratio': 0.50,
            'break_ratio': 0.10
        },
        'advanced': {
            'lecture_ratio': 0.30,
            'exercise_ratio': 0.60,
            'break_ratio': 0.10
        }
    }
    
    pacing = pacing_map.get(experience_level, pacing_map['intermediate'])
    
    # Calculate actual minutes
    total_minutes = duration_hours * 60
    return {
        'lecture_ratio': pacing['lecture_ratio'],
        'exercise_ratio': pacing['exercise_ratio'],
        'break_ratio': pacing['break_ratio'],
        'lecture_minutes': int(total_minutes * pacing['lecture_ratio']),
        'exercise_minutes': int(total_minutes * pacing['exercise_ratio']),
        'break_minutes': int(total_minutes * pacing['break_ratio'])
    }

def generate_focus_areas(profile, topics):
    """Generate specific focus areas and recommendations."""
    focus = []
    current_stack = profile.get('current_stack', [])
    industry = profile.get('industry', '')
    goals = profile.get('goals', [])
    
    # Migration focus
    if any(db in str(current_stack).lower() for db in ['postgres', 'mysql', 'sql']):
        focus.append(f"Emphasize schema design patterns (coming from relational background)")
        focus.append(f"Include specific examples of SQL → MongoDB query translation")
    
    # Industry-specific
    if industry:
        focus.append(f"Use {industry} industry examples throughout exercises")
    
    # Goal-specific
    for goal in goals:
        if 'scale' in goal.lower() or 'performance' in goal.lower():
            focus.append("Include performance tuning and indexing strategies")
        if 'migration' in goal.lower():
            focus.append("Provide migration planning checklist and tooling overview")
        if 'ai' in goal.lower() or 'vector' in goal.lower():
            focus.append("Showcase RAG use cases relevant to their domain")
    
    return focus

def analyze_customer_profile(profile_path):
    """Analyze customer profile and generate recommendations."""
    with open(profile_path, 'r') as f:
        profile = json.load(f)
    
    # Determine experience level
    experience_level = analyze_experience_level(profile)
    
    # Get duration (default to 6 hours)
    duration_hours = 6
    for constraint in profile.get('constraints', []):
        if 'hour' in constraint.lower():
            import re
            match = re.search(r'(\d+)\s*hour', constraint)
            if match:
                duration_hours = int(match.group(1))
    
    # Recommend topics
    topics = recommend_topics(profile, experience_level)
    
    # Calculate pacing
    pacing = calculate_pacing(duration_hours, experience_level)
    
    # Generate focus areas
    focus_areas = generate_focus_areas(profile, topics)
    
    # Determine exercise complexity
    exercise_complexity = {
        'beginner': 'Highly scaffolded with detailed instructions and 90% starter code',
        'intermediate': 'Moderate scaffolding with clear TODOs and 70% starter code',
        'advanced': 'Minimal scaffolding with problem statements and 50% starter code'
    }
    
    return {
        'company': profile.get('company'),
        'industry': profile.get('industry'),
        'audience_size': profile.get('audience_size'),
        'recommended_level': experience_level,
        'duration_hours': duration_hours,
        'suggested_topics': [
            {
                'title': t['title'],
                'duration_min': t['duration_min'],
                'description': t['description']
            }
            for t in topics[:6]  # Max 6 topics
        ],
        'pacing': pacing,
        'exercise_complexity': exercise_complexity[experience_level],
        'focus_areas': focus_areas,
        'prerequisites': [
            'Laptop with admin access',
            'MongoDB Atlas account (or local MongoDB installed)' if experience_level == 'beginner' else 'MongoDB Atlas account',
            'Basic programming knowledge (Python, JavaScript, or similar)' if experience_level == 'beginner' else 'Proficiency in at least one programming language',
            'Text editor or IDE'
        ],
        'recommended_format': 'half-day' if duration_hours <= 4 else 'full-day' if duration_hours <= 8 else 'multi-day'
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze customer profile for workshop planning')
    parser.add_argument('profile', help='Customer profile JSON file')
    parser.add_argument('--output', help='Output JSON file', default=None)
    
    args = parser.parse_args()
    
    print(f"Analyzing customer profile: {args.profile}")
    
    analysis = analyze_customer_profile(args.profile)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n✅ Analysis saved to {args.output}")
    else:
        print("\n" + "="*60)
        print("AUDIENCE ANALYSIS")
        print("="*60)
        print(f"\nCompany: {analysis['company']}")
        print(f"Industry: {analysis['industry']}")
        print(f"Audience Size: {analysis['audience_size']}")
        print(f"Recommended Level: {analysis['recommended_level']}")
        print(f"Duration: {analysis['duration_hours']} hours")
        print(f"Format: {analysis['recommended_format']}")
        
        print(f"\nSuggested Topics ({len(analysis['suggested_topics'])}):")
        for topic in analysis['suggested_topics']:
            print(f"\n  {topic['title']} ({topic['duration_min']} min)")
            print(f"  → {topic['description']}")
        
        print(f"\nPacing Breakdown:")
        print(f"  Lecture: {analysis['pacing']['lecture_minutes']} min ({analysis['pacing']['lecture_ratio']*100:.0f}%)")
        print(f"  Exercises: {analysis['pacing']['exercise_minutes']} min ({analysis['pacing']['exercise_ratio']*100:.0f}%)")
        print(f"  Breaks: {analysis['pacing']['break_minutes']} min ({analysis['pacing']['break_ratio']*100:.0f}%)")
        
        print(f"\n💡 Focus Areas:")
        for focus in analysis['focus_areas']:
            print(f"  - {focus}")
        
        print(f"\nPrerequisites:")
        for prereq in analysis['prerequisites']:
            print(f"  - {prereq}")

if __name__ == '__main__':
    main()
