#!/usr/bin/env python3
"""
Generate QE demo code from vertical analysis.
Usage: python demo_generator.py analysis.json --output demo/
"""

import json
import argparse
import os

def generate_demo(analysis, output_dir):
    """Generate demo files."""
    os.makedirs(output_dir, exist_ok=True)
    
    vertical = analysis['vertical']
    
    # Generate setup.js
    setup_js = f"""// Setup Queryable Encryption for {vertical}
const {{ MongoClient }} = require('mongodb');
const {{ ClientEncryption }} = require('mongodb-client-encryption');

async function setup() {{
  const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017';
  const client = new MongoClient(uri);
  
  // Create data encryption key
  const encryption = new ClientEncryption(client, {{
    keyVaultNamespace: 'encryption.__keyVault',
    kmsProviders: {{ local: {{ key: Buffer.alloc(96) }} }}
  }});
  
  const keyId = await encryption.createDataKey('local');
  console.log('Created DEK:', keyId);
  
  await client.close();
}}

setup().catch(console.error);
"""
    
    with open(os.path.join(output_dir, 'setup.js'), 'w') as f:
        f.write(setup_js)
    
    # Generate README
    readme = f"""# {vertical.title()} QE Demo

## Setup
1. Start MongoDB: `mongod`
2. Create keys: `node setup.js`
3. Insert data: `node insert.js`
4. Query data: `node query.js`

## Sensitive Fields
"""
    for field in analysis['sensitive_fields']:
        readme += f"- **{field['name']}** ({field['type']}): {field['reason']}\n"
    
    readme += f"\n## Compliance: {', '.join(analysis['compliance_frameworks'])}\n"
    
    with open(os.path.join(output_dir, 'README.md'), 'w') as f:
        f.write(readme)
    
    return ['setup.js', 'README.md']

def main():
    parser = argparse.ArgumentParser(description='Generate QE demo')
    parser.add_argument('analysis', help='Vertical analysis JSON')
    parser.add_argument('--output', default='demo/', help='Output directory')
    
    args = parser.parse_args()
    
    with open(args.analysis, 'r') as f:
        analysis = json.load(f)
    
    files = generate_demo(analysis, args.output)
    
    print(f"✅ Generated {len(files)} demo files")
    print(f"✅ Saved to {args.output}")
    for f in files:
        print(f"   - {f}")

if __name__ == '__main__':
    main()
