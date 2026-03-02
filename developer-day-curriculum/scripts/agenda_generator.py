#!/usr/bin/env python3
"""
Generate time-blocked workshop agenda from audience analysis.
Usage: python agenda_generator.py analysis.json --duration 6 --output agenda.md
"""

import json
import argparse
from datetime import datetime, timedelta

def parse_time(time_str):
    """Parse time string like '9:00 AM' to datetime."""
    return datetime.strptime(time_str, '%I:%M %p')

def format_time(dt):
    """Format datetime to '9:00 AM' format."""
    return dt.strftime('%I:%M %p').lstrip('0')

def add_minutes(time_dt, minutes):
    """Add minutes to time."""
    return time_dt + timedelta(minutes=minutes)

def generate_time_blocks(start_time_str, duration_hours, include_lunch=False):
    """Generate time blocks for the day."""
    start_time = parse_time(start_time_str)
    current_time = start_time
    blocks = []
    
    # Calculate total minutes
    total_minutes = duration_hours * 60
    elapsed = 0
    
    # Welcome (15 min)
    blocks.append({
        'type': 'welcome',
        'start': format_time(current_time),
        'duration': 15,
        'title': 'Welcome & Introductions'
    })
    current_time = add_minutes(current_time, 15)
    elapsed += 15
    
    # Determine session structure
    if duration_hours <= 4:
        # Half-day: 1 break
        session_minutes = total_minutes - 15 - 15  # - welcome - break
        blocks.append({
            'type': 'session',
            'start': format_time(current_time),
            'duration': session_minutes // 2,
            'title': 'Morning Session'
        })
        current_time = add_minutes(current_time, session_minutes // 2)
        
        blocks.append({
            'type': 'break',
            'start': format_time(current_time),
            'duration': 15,
            'title': 'Break'
        })
        current_time = add_minutes(current_time, 15)
        
        blocks.append({
            'type': 'session',
            'start': format_time(current_time),
            'duration': session_minutes // 2,
            'title': 'Afternoon Session'
        })
        
    elif duration_hours <= 8:
        # Full-day: morning, lunch, afternoon with breaks
        morning_duration = 180  # 3 hours
        lunch_duration = 60 if include_lunch else 0
        afternoon_duration = total_minutes - 15 - morning_duration - lunch_duration - 30  # - welcome - morning - lunch - breaks
        
        blocks.append({
            'type': 'session',
            'start': format_time(current_time),
            'duration': 90,
            'title': 'Morning Session Part 1'
        })
        current_time = add_minutes(current_time, 90)
        
        blocks.append({
            'type': 'break',
            'start': format_time(current_time),
            'duration': 15,
            'title': 'Break'
        })
        current_time = add_minutes(current_time, 15)
        
        blocks.append({
            'type': 'session',
            'start': format_time(current_time),
            'duration': 90,
            'title': 'Morning Session Part 2'
        })
        current_time = add_minutes(current_time, 90)
        
        if include_lunch:
            blocks.append({
                'type': 'lunch',
                'start': format_time(current_time),
                'duration': 60,
                'title': 'Lunch Break'
            })
            current_time = add_minutes(current_time, 60)
        
        blocks.append({
            'type': 'session',
            'start': format_time(current_time),
            'duration': afternoon_duration // 2,
            'title': 'Afternoon Session Part 1'
        })
        current_time = add_minutes(current_time, afternoon_duration // 2)
        
        blocks.append({
            'type': 'break',
            'start': format_time(current_time),
            'duration': 15,
            'title': 'Break'
        })
        current_time = add_minutes(current_time, 15)
        
        blocks.append({
            'type': 'session',
            'start': format_time(current_time),
            'duration': afternoon_duration // 2,
            'title': 'Afternoon Session Part 2'
        })
    
    return blocks

def fill_sessions_with_topics(blocks, topics, pacing):
    """Fill session blocks with topics and exercises."""
    agenda_items = []
    topic_idx = 0
    
    for block in blocks:
        if block['type'] == 'welcome':
            agenda_items.append({
                'time': block['start'],
                'duration': block['duration'],
                'type': 'intro',
                'title': block['title'],
                'content': [
                    'Icebreaker activity',
                    'Agenda overview',
                    'Learning objectives',
                    'Wi-Fi and logistics'
                ]
            })
        
        elif block['type'] == 'break':
            agenda_items.append({
                'time': block['start'],
                'duration': block['duration'],
                'type': 'break',
                'title': block['title'],
                'content': []
            })
        
        elif block['type'] == 'lunch':
            agenda_items.append({
                'time': block['start'],
                'duration': block['duration'],
                'type': 'lunch',
                'title': block['title'],
                'content': []
            })
        
        elif block['type'] == 'session' and topic_idx < len(topics):
            # Fill session with topic + exercise pattern
            session_time = parse_time(block['start'])
            session_minutes = block['duration']
            
            while session_minutes > 0 and topic_idx < len(topics):
                topic = topics[topic_idx]
                
                # Lecture for this topic (30-45 min)
                lecture_duration = min(topic['duration_min'] // 2, 45, session_minutes)
                if lecture_duration > 0:
                    agenda_items.append({
                        'time': format_time(session_time),
                        'duration': lecture_duration,
                        'type': 'lecture',
                        'title': f"Topic {topic_idx + 1}: {topic['title']}",
                        'content': [
                            f"Learning objective: {topic['description']}",
                            'Key concepts and demonstrations',
                            'Q&A'
                        ]
                    })
                    session_time = add_minutes(session_time, lecture_duration)
                    session_minutes -= lecture_duration
                
                # Exercise for this topic (30-60 min)
                exercise_duration = min(topic['duration_min'] - lecture_duration, 60, session_minutes)
                if exercise_duration > 0:
                    agenda_items.append({
                        'time': format_time(session_time),
                        'duration': exercise_duration,
                        'type': 'exercise',
                        'title': f"Exercise {topic_idx + 1}: {topic['title']}",
                        'content': [
                            f"Hands-on: Build {topic['title'].lower()} example",
                            f"Starter code: exercises/{topic_idx + 1:02d}-{topic['title'].lower().replace(' ', '-')}/",
                            'Success criteria: [To be defined]',
                            'Extension challenges for fast finishers'
                        ]
                    })
                    session_time = add_minutes(session_time, exercise_duration)
                    session_minutes -= exercise_duration
                
                topic_idx += 1
    
    return agenda_items

def generate_agenda_markdown(analysis, agenda_items, start_time, duration_hours):
    """Generate markdown agenda."""
    md = f"# MongoDB Developer Day - {analysis['company']}\n\n"
    md += f"**Date:** [Date] | **Duration:** {duration_hours} hours | **Level:** {analysis['recommended_level'].title()}\n\n"
    
    # Goals
    md += "## Learning Objectives\n\n"
    for topic in analysis['suggested_topics'][:3]:
        md += f"- {topic['description']}\n"
    md += "\n"
    
    # Prerequisites
    md += "## Prerequisites\n\n"
    for prereq in analysis['prerequisites']:
        md += f"- {prereq}\n"
    md += "\n"
    
    # Schedule
    md += "## Schedule\n\n"
    
    current_session = None
    for item in agenda_items:
        # Group by session
        if item['type'] in ['intro', 'lunch', 'break']:
            if current_session:
                md += "\n"
                current_session = None
            
            if item['type'] == 'intro':
                md += f"### {item['time']} - {item['title']} ({item['duration']} min)\n\n"
                for content in item['content']:
                    md += f"- {content}\n"
                md += "\n"
            elif item['type'] == 'lunch':
                md += f"### {item['time']} - 🍽️ {item['title']} ({item['duration']} min)\n\n"
            elif item['type'] == 'break':
                md += f"### {item['time']} - ☕ {item['title']} ({item['duration']} min)\n\n"
        
        elif item['type'] == 'lecture':
            md += f"### {item['time']} - {item['title']} ({item['duration']} min)\n\n"
            for content in item['content']:
                md += f"- {content}\n"
            md += "\n"
        
        elif item['type'] == 'exercise':
            md += f"### {item['time']} - 💻 {item['title']} ({item['duration']} min)\n\n"
            for content in item['content']:
                md += f"- {content}\n"
            md += "\n"
    
    # Follow-up resources
    md += "## Follow-Up Resources\n\n"
    md += "- Slide deck: [To be shared]\n"
    md += "- Exercise repository: [GitHub link]\n"
    md += "- MongoDB documentation: https://docs.mongodb.com\n"
    md += "- MongoDB University (free courses): https://learn.mongodb.com\n"
    md += "- Community support: https://community.mongodb.com\n\n"
    
    # Contact
    md += "## Questions?\n\n"
    md += "- Email: [Your email]\n"
    md += "- Slack: [Your Slack handle]\n"
    md += "- Office hours: [Schedule]\n"
    
    return md

def main():
    parser = argparse.ArgumentParser(description='Generate workshop agenda')
    parser.add_argument('analysis', help='Audience analysis JSON file (from audience_analyzer.py)')
    parser.add_argument('--duration', type=int, help='Duration in hours', default=None)
    parser.add_argument('--start-time', help='Start time (e.g., "9:00 AM")', default='9:00 AM')
    parser.add_argument('--include-lunch', action='store_true', help='Include lunch break')
    parser.add_argument('--output', help='Output Markdown file', default='agenda.md')
    
    args = parser.parse_args()
    
    print(f"Loading analysis: {args.analysis}")
    with open(args.analysis, 'r') as f:
        analysis = json.load(f)
    
    duration = args.duration or analysis['duration_hours']
    
    print(f"\nGenerating {duration}-hour agenda starting at {args.start_time}...")
    
    # Generate time blocks
    blocks = generate_time_blocks(args.start_time, duration, args.include_lunch)
    
    # Fill with topics and exercises
    agenda_items = fill_sessions_with_topics(blocks, analysis['suggested_topics'], analysis['pacing'])
    
    # Generate markdown
    agenda_md = generate_agenda_markdown(analysis, agenda_items, args.start_time, duration)
    
    with open(args.output, 'w') as f:
        f.write(agenda_md)
    
    print(f"✅ Agenda saved to {args.output}")
    
    print("\n" + "="*60)
    print("AGENDA SUMMARY")
    print("="*60)
    print(f"\nDuration: {duration} hours")
    print(f"Topics: {len(analysis['suggested_topics'])}")
    print(f"Exercises: {sum(1 for item in agenda_items if item['type'] == 'exercise')}")
    print(f"Breaks: {sum(1 for item in agenda_items if item['type'] in ['break', 'lunch'])}")
    
    print("\n💡 Next steps:")
    print("1. Review and customize agenda")
    print("2. Run: python scripts/exercise_scaffolder.py agenda.md --output exercises/")
    print("3. Fill in exercise starter code and solutions")

if __name__ == '__main__':
    main()
