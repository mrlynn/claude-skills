#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Analyze job posting and extract structured requirements.
  Usage: python job_analyzer.py job-posting.txt --output analysis.json
"""

import re
import json
import argparse
from pathlib import Path

# Common tech skills patterns
TECH_SKILLS = [
    'python', 'javascript', 'java', 'c\\+\\+', 'c#', 'ruby', 'go', 'rust', 'swift',
    'react', 'vue', 'angular', 'node\\.js', 'django', 'flask', 'spring',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
    'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
    'git', 'ci/cd', 'jenkins', 'github actions',
    'machine learning', 'deep learning', 'nlp', 'computer vision',
    'rag', 'vector search', 'embeddings', 'llm', 'langchain'
]

def extract_skills(text):
    """Extract technical skills from text."""
    text_lower = text.lower()
    found_skills = []
    
    for skill in TECH_SKILLS:
        if re.search(rf'\b{skill}\b', text_lower):
            # Normalize case
            match = re.search(rf'\b({skill})\b', text_lower)
            if match:
                found_skills.append(match.group(0))
    
    return list(set(found_skills))

def extract_experience_years(text):
    """Extract required years of experience."""
    patterns = [
        r'(\d+)\+?\s*years?',
        r'(\d+)\s*to\s*(\d+)\s*years?',
        r'minimum\s*(\d+)\s*years?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

def extract_education(text):
    """Extract education requirements."""
    patterns = [
        r'bachelor\'?s?\s*degree',
        r'master\'?s?\s*degree',
        r'phd',
        r'degree.*computer science',
        r'degree.*engineering'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

def split_sections(text):
    """Split job posting into sections."""
    sections = {
        'required': '',
        'preferred': '',
        'responsibilities': ''
    }
    
    # Find required/preferred sections
    required_match = re.search(
        r'(required|must have|requirements):(.*?)(?=preferred|nice to have|responsibilities|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if required_match:
        sections['required'] = required_match.group(2)
    
    preferred_match = re.search(
        r'(preferred|nice to have|bonus):(.*?)(?=responsibilities|required|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if preferred_match:
        sections['preferred'] = preferred_match.group(2)
    
    resp_match = re.search(
        r'(responsibilities|what you\'ll do|duties):(.*?)(?=required|preferred|qualifications|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if resp_match:
        sections['responsibilities'] = resp_match.group(2)
    
    return sections

def extract_responsibilities(text):
    """Extract bullet points from responsibilities section."""
    # Find bullet points (lines starting with -, *, •, or numbers)
    bullets = re.findall(r'^[\s]*[•\-\*\d\.]+\s*(.+)$', text, re.MULTILINE)
    return [b.strip() for b in bullets if len(b.strip()) > 10]

def extract_keywords(text):
    """Extract important keywords (nouns, key phrases)."""
    # Remove common filler words
    text_lower = text.lower()
    
    # Find 2-3 word phrases that appear multiple times
    words = re.findall(r'\b[a-z]{4,}\b', text_lower)
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Keywords are words appearing 2+ times
    keywords = [w for w, count in word_freq.items() if count >= 2]
    
    # Add technical skills
    keywords.extend(extract_skills(text))
    
    return list(set(keywords))[:30]  # Top 30 keywords

def analyze_job_posting(filepath):
    """Analyze job posting and return structured data."""
    with open(filepath, 'r') as f:
        text = f.read()
    
    # Extract title and company (first few lines usually)
    lines = text.split('\n')
    title = lines[0].strip() if lines else 'Unknown'
    company = lines[1].strip() if len(lines) > 1 else 'Unknown'
    
    # Split into sections
    sections = split_sections(text)
    
    # Extract from sections
    required_skills = extract_skills(sections['required'] or text)
    preferred_skills = extract_skills(sections['preferred'] or '')
    
    # Remove duplicates (preferred that are also required)
    preferred_skills = [s for s in preferred_skills if s not in required_skills]
    
    responsibilities = extract_responsibilities(sections['responsibilities'] or text)
    experience_years = extract_experience_years(text)
    education = extract_education(text)
    keywords = extract_keywords(text)
    
    return {
        'title': title,
        'company': company,
        'required_skills': required_skills,
        'preferred_skills': preferred_skills,
        'keywords': keywords,
        'experience_years': experience_years,
        'education': education,
        'responsibilities': responsibilities
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze job posting')
    parser.add_argument('job_posting', help='Job posting text file')
    parser.add_argument('--output', help='Output JSON file', default=None)
    
    args = parser.parse_args()
    
    print(f"Analyzing job posting: {args.job_posting}")
    
    analysis = analyze_job_posting(args.job_posting)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n✅ Analysis saved to {args.output}")
    else:
        print("\n" + "="*60)
        print("JOB ANALYSIS")
        print("="*60)
        print(f"\nTitle: {analysis['title']}")
        print(f"Company: {analysis['company']}")
        print(f"\nRequired Skills ({len(analysis['required_skills'])}):")
        for skill in analysis['required_skills']:
            print(f"  - {skill}")
        print(f"\nPreferred Skills ({len(analysis['preferred_skills'])}):")
        for skill in analysis['preferred_skills']:
            print(f"  - {skill}")
        print(f"\nExperience: {analysis['experience_years'] or 'Not specified'}")
        print(f"Education: {analysis['education'] or 'Not specified'}")
        print(f"\nTop Keywords ({len(analysis['keywords'])}):")
        print(f"  {', '.join(analysis['keywords'][:15])}")
        print(f"\nResponsibilities ({len(analysis['responsibilities'])}):")
        for resp in analysis['responsibilities'][:5]:
            print(f"  - {resp}")

if __name__ == '__main__':
    main()
