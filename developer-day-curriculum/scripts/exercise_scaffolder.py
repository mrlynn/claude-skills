#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Generate hands-on exercise scaffolding from agenda.
  Usage: python exercise_scaffolder.py agenda.md --output exercises/
"""

import re
import os
import argparse
from pathlib import Path

def extract_exercises_from_agenda(agenda_path):
    """Extract exercise information from agenda markdown."""
    with open(agenda_path, 'r') as f:
        content = f.read()
    
    exercises = []
    
    # Find exercise sections (### TIME - 💻 Exercise N: Title (XX min))
    pattern = r'###\s+[\d:APM\s]+-\s+💻\s+Exercise\s+(\d+):\s+(.+?)\s+\((\d+)\s+min\)'
    matches = re.finditer(pattern, content)
    
    for match in matches:
        exercise_num = int(match.group(1))
        title = match.group(2).strip()
        duration = int(match.group(3))
        
        # Extract content after this heading until next heading
        start_pos = match.end()
        next_heading = re.search(r'\n###', content[start_pos:])
        if next_heading:
            exercise_content = content[start_pos:start_pos + next_heading.start()]
        else:
            exercise_content = content[start_pos:]
        
        exercises.append({
            'number': exercise_num,
            'title': title,
            'duration': duration,
            'content': exercise_content.strip()
        })
    
    return exercises

def generate_exercise_structure(output_dir, exercise):
    """Generate directory structure for an exercise."""
    # Create exercise directory name
    dir_name = f"{exercise['number']:02d}-{exercise['title'].lower().replace(' ', '-').replace(':', '')}"
    exercise_dir = Path(output_dir) / dir_name
    
    # Create directories
    (exercise_dir / 'starter').mkdir(parents=True, exist_ok=True)
    (exercise_dir / 'solution').mkdir(parents=True, exist_ok=True)
    (exercise_dir / 'extension').mkdir(parents=True, exist_ok=True)
    
    return exercise_dir

def generate_readme(exercise_dir, exercise):
    """Generate README.md for exercise."""
    readme_content = f"""# Exercise {exercise['number']}: {exercise['title']}

**Duration:** {exercise['duration']} minutes

## Objective

[Define what participants will build/learn in this exercise]

## Prerequisites

- Completed previous exercises
- MongoDB Atlas cluster running (or local MongoDB)
- [Other prerequisites]

## Instructions

### Part 1: Setup

1. Navigate to the starter code:
   ```bash
   cd starter/
   ```

2. Install dependencies (if needed):
   ```bash
   npm install  # or pip install -r requirements.txt
   ```

3. Configure connection:
   - Copy `.env.example` to `.env`
   - Add your MongoDB connection string

### Part 2: Complete the TODOs

The starter code contains several `TODO` comments marking where you need to add code. Work through them in order:

1. **TODO 1:** [Description]
2. **TODO 2:** [Description]
3. **TODO 3:** [Description]

### Part 3: Test Your Solution

Run the application:
```bash
node app.js  # or python app.py
```

**Success criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Hints

<details>
<summary>Click to reveal hints</summary>

**Hint for TODO 1:**
[Helpful hint without giving away the answer]

**Hint for TODO 2:**
[Another hint]

</details>

## Solution

If you get stuck, check the `solution/` directory for the complete working code.

## Extension Challenges

Done early? Try these bonus challenges in `extension/challenges.md`:

1. [Challenge 1]
2. [Challenge 2]
3. [Challenge 3]

## Troubleshooting

**Problem:** [Common issue]
**Solution:** [How to fix]

**Problem:** [Another issue]
**Solution:** [Fix]

## Resources

- [Relevant MongoDB docs]
- [Related tutorial]
"""
    
    with open(exercise_dir / 'README.md', 'w') as f:
        f.write(readme_content)

def generate_starter_code(exercise_dir, exercise):
    """Generate starter code template."""
    # Generate a basic Node.js example (can be customized)
    starter_code = """const { MongoClient } = require('mongodb');
require('dotenv').config();

const uri = process.env.MONGODB_URI;
const client = new MongoClient(uri);

async function main() {
  try {
    await client.connect();
    console.log('Connected to MongoDB');
    
    const db = client.db('workshop');
    const collection = db.collection('examples');
    
    // TODO 1: Insert a document
    // Hint: Use collection.insertOne({ ... })
    
    
    // TODO 2: Find documents
    // Hint: Use collection.find({ ... }).toArray()
    
    
    // TODO 3: Update a document
    // Hint: Use collection.updateOne({ ... }, { $set: { ... } })
    
    
    console.log('Exercise complete!');
    
  } finally {
    await client.close();
  }
}

main().catch(console.error);
"""
    
    with open(exercise_dir / 'starter' / 'app.js', 'w') as f:
        f.write(starter_code)
    
    # Generate .env.example
    env_example = """MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
"""
    with open(exercise_dir / 'starter' / '.env.example', 'w') as f:
        f.write(env_example)
    
    # Generate package.json
    package_json = """{
  "name": "exercise-%d",
  "version": "1.0.0",
  "description": "%s",
  "main": "app.js",
  "scripts": {
    "start": "node app.js"
  },
  "dependencies": {
    "mongodb": "^6.0.0",
    "dotenv": "^16.0.0"
  }
}
""" % (exercise['number'], exercise['title'])
    
    with open(exercise_dir / 'starter' / 'package.json', 'w') as f:
        f.write(package_json)

def generate_solution(exercise_dir, exercise):
    """Generate solution placeholder."""
    solution_code = """const { MongoClient } = require('mongodb');
require('dotenv').config();

const uri = process.env.MONGODB_URI;
const client = new MongoClient(uri);

async function main() {
  try {
    await client.connect();
    console.log('Connected to MongoDB');
    
    const db = client.db('workshop');
    const collection = db.collection('examples');
    
    // TODO 1: Insert a document
    const insertResult = await collection.insertOne({
      name: 'Example Document',
      timestamp: new Date()
    });
    console.log('Inserted document:', insertResult.insertedId);
    
    // TODO 2: Find documents
    const docs = await collection.find({}).toArray();
    console.log('Found documents:', docs.length);
    
    // TODO 3: Update a document
    const updateResult = await collection.updateOne(
      { _id: insertResult.insertedId },
      { $set: { updated: true } }
    );
    console.log('Updated documents:', updateResult.modifiedCount);
    
    console.log('Exercise complete!');
    
  } finally {
    await client.close();
  }
}

main().catch(console.error);
"""
    
    with open(exercise_dir / 'solution' / 'app.js', 'w') as f:
        f.write(solution_code)

def generate_extensions(exercise_dir, exercise):
    """Generate extension challenges."""
    challenges = f"""# Extension Challenges for Exercise {exercise['number']}

If you've completed the main exercise and want to go further, try these challenges:

## Challenge 1: Add Error Handling

Modify your code to handle errors gracefully:
- Catch connection errors
- Validate input data
- Provide helpful error messages

## Challenge 2: Add Indexes

Create indexes to improve query performance:
- Identify which fields are frequently queried
- Create appropriate indexes
- Verify performance improvement with `.explain()`

## Challenge 3: Implement Transactions

Extend the exercise to use multi-document transactions:
- Wrap operations in a transaction
- Handle rollback on errors
- Test transaction behavior

## Challenge 4: Add Monitoring

Implement logging and monitoring:
- Log all database operations
- Track query execution time
- Alert on errors

## Challenge 5: Optimize for Scale

Consider how your code would perform at scale:
- Use bulk operations where possible
- Implement pagination for large result sets
- Add connection pooling configuration

## Bonus: Production-Ready

Make your code production-ready:
- Add configuration management
- Implement health checks
- Add unit tests
- Document your API
"""
    
    with open(exercise_dir / 'extension' / 'challenges.md', 'w') as f:
        f.write(challenges)

def main():
    parser = argparse.ArgumentParser(description='Generate exercise scaffolding from agenda')
    parser.add_argument('agenda', help='Agenda markdown file (from agenda_generator.py)')
    parser.add_argument('--output', help='Output directory for exercises', default='exercises')
    
    args = parser.parse_args()
    
    print(f"Extracting exercises from: {args.agenda}")
    
    exercises = extract_exercises_from_agenda(args.agenda)
    
    if not exercises:
        print("⚠️  No exercises found in agenda.")
        print("Make sure agenda has sections like: ### TIME - 💻 Exercise N: Title (XX min)")
        return
    
    print(f"\nFound {len(exercises)} exercises")
    
    # Create output directory
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    for exercise in exercises:
        print(f"\nGenerating Exercise {exercise['number']}: {exercise['title']}")
        
        exercise_dir = generate_exercise_structure(args.output, exercise)
        generate_readme(exercise_dir, exercise)
        generate_starter_code(exercise_dir, exercise)
        generate_solution(exercise_dir, exercise)
        generate_extensions(exercise_dir, exercise)
        
        print(f"  ✅ Created {exercise_dir.name}/")
    
    print("\n" + "="*60)
    print(f"✅ Generated {len(exercises)} exercise directories in {args.output}/")
    print("="*60)
    print("\nNext steps:")
    print("1. Review and customize README.md files")
    print("2. Fill in starter code TODOs with specific examples")
    print("3. Complete solution code")
    print("4. Test all exercises on fresh environment")
    print("5. Customize extension challenges for audience level")

if __name__ == '__main__':
    main()
