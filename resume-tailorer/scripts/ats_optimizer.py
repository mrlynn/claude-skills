#!/usr/bin/env python3
"""
Generate ATS-optimized resume from master resume and match analysis.
Usage: python ats_optimizer.py master-resume.json matches.json --output tailored-resume.md
"""

import json
import argparse
from datetime import datetime

def generate_summary(resume, job_analysis, matches):
    """Generate customized summary highlighting relevant experience."""
    # Extract top skills
    top_skills = matches['matched_required_skills'][:3]
    
    # Extract years of experience (rough estimate from experience items)
    total_years = len(resume.get('experience', []))  # Rough estimate
    
    summary = f"Experienced professional with {total_years}+ years"
    if top_skills:
        summary += f" in {', '.join(top_skills)}"
    
    # Add top achievement if available
    if matches['experience_matches']:
        top_exp = matches['experience_matches'][0]
        if top_exp['matched_achievements']:
            summary += f". {top_exp['matched_achievements'][0]}"
    
    return summary

def format_experience_item(exp_match, keywords):
    """Format experience item with keyword optimization."""
    md = f"### {exp_match['title']}\n"
    md += f"**{exp_match['company']}** | {exp_match['dates']}\n\n"
    
    for achievement in exp_match['matched_achievements']:
        md += f"- {achievement}\n"
    
    return md + "\n"

def generate_cover_letter(resume, job_analysis, company_name=None):
    """Generate cover letter template."""
    name = resume.get('contact', {}).get('name', '[Your Name]')
    email = resume.get('contact', {}).get('email', '[Your Email]')
    phone = resume.get('contact', {}).get('phone', '[Your Phone]')
    
    company = company_name or job_analysis.get('company', '[Company Name]')
    title = job_analysis.get('title', '[Job Title]')
    
    letter = f"{name}\n"
    letter += f"{email} | {phone}\n"
    letter += f"{datetime.now().strftime('%B %d, %Y')}\n\n"
    letter += f"Dear Hiring Manager,\n\n"
    letter += f"I am writing to express my strong interest in the {title} position at {company}. "
    letter += f"With my background in {', '.join(job_analysis.get('required_skills', [])[:2])}, "
    letter += f"I am excited about the opportunity to contribute to your team.\n\n"
    
    letter += f"[Paragraph 2: Connect your specific experience to their needs. "
    letter += f"Reference 2-3 achievements that align with job responsibilities.]\n\n"
    
    letter += f"[Paragraph 3: Show genuine interest in the company. "
    letter += f"Mention recent news, products, or initiatives that excite you.]\n\n"
    
    letter += f"I would welcome the opportunity to discuss how my experience can contribute to {company}'s success. "
    letter += f"Thank you for your consideration.\n\n"
    
    letter += f"Best regards,\n{name}\n"
    
    return letter

def generate_resume(resume, job_analysis, matches):
    """Generate ATS-optimized resume in Markdown."""
    contact = resume.get('contact', {})
    name = contact.get('name', 'Your Name')
    email = contact.get('email', 'email@example.com')
    phone = contact.get('phone', '(555) 555-5555')
    linkedin = contact.get('linkedin', '')
    portfolio = contact.get('portfolio', '')
    
    md = f"# {name}\n"
    md += f"{email} | {phone}"
    if linkedin:
        md += f" | {linkedin}"
    if portfolio:
        md += f" | {portfolio}"
    md += "\n\n"
    
    # Summary
    md += "## Summary\n\n"
    summary = generate_summary(resume, job_analysis, matches)
    md += f"{summary}\n\n"
    
    # Experience (reordered by relevance)
    md += "## Experience\n\n"
    for exp_match in matches['experience_matches']:
        # Only include if relevance > 0.5
        if exp_match['relevance_score'] >= 0.5:
            md += format_experience_item(exp_match, job_analysis.get('keywords', []))
    
    # Skills (prioritized by job requirements)
    md += "## Skills\n\n"
    skills = []
    # Required skills first
    skills.extend(matches['matched_required_skills'])
    # Then preferred
    skills.extend(matches['matched_preferred_skills'])
    # Then other skills
    other_skills = [
        s for s in resume.get('skills', []) 
        if s.lower() not in [x.lower() for x in skills]
    ]
    skills.extend(other_skills[:10])  # Limit total skills
    
    md += ", ".join(skills) + "\n\n"
    
    # Education
    if resume.get('education'):
        md += "## Education\n\n"
        for edu in resume['education']:
            md += f"**{edu.get('degree', '')}** | {edu.get('school', '')} | {edu.get('year', '')}\n"
        md += "\n"
    
    return md

def main():
    parser = argparse.ArgumentParser(description='Generate ATS-optimized resume')
    parser.add_argument('resume', help='Master resume JSON file')
    parser.add_argument('matches', help='Match analysis JSON file (from resume_matcher.py)')
    parser.add_argument('--output', help='Output Markdown file', default='tailored-resume.md')
    parser.add_argument('--cover-letter', action='store_true', help='Generate cover letter too')
    parser.add_argument('--company-name', help='Company name for cover letter')
    
    args = parser.parse_args()
    
    print(f"Loading resume: {args.resume}")
    with open(args.resume, 'r') as f:
        resume = json.load(f)
    
    print(f"Loading matches: {args.matches}")
    with open(args.matches, 'r') as f:
        matches = json.load(f)
    
    # Need job analysis for keywords
    # Reconstruct minimal job analysis from matches
    job_analysis = {
        'company': '[Company Name]',
        'title': '[Job Title]',
        'required_skills': matches['matched_required_skills'] + matches['missing_required_skills'],
        'keywords': []  # Would need original, using skills as proxy
    }
    
    print("\nGenerating tailored resume...")
    resume_md = generate_resume(resume, job_analysis, matches)
    
    with open(args.output, 'w') as f:
        f.write(resume_md)
    print(f"✅ Resume saved to {args.output}")
    
    if args.cover_letter:
        cover_letter_path = args.output.replace('.md', '-cover-letter.md')
        print("\nGenerating cover letter...")
        cover_letter = generate_cover_letter(resume, job_analysis, args.company_name)
        with open(cover_letter_path, 'w') as f:
            f.write(cover_letter)
        print(f"✅ Cover letter saved to {cover_letter_path}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Review generated resume for natural language flow")
    print("2. Customize cover letter paragraphs 2-3 with specific details")
    print("3. Proofread for typos and accuracy")
    print("4. Convert to PDF (e.g., pandoc -o resume.pdf resume.md)")
    print("5. Save with professional filename (FirstLast-Resume.pdf)")

if __name__ == '__main__':
    main()
