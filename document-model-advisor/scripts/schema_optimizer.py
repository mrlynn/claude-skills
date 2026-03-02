#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Generate optimized MongoDB schema from relationship analysis.
  Usage: python schema_optimizer.py analysis.json --output schema.json
"""

import json
import argparse

def generate_schema(analysis):
    """Generate MongoDB schema from analysis."""
    collections = {}
    denorm_rules = []
    
    for rec in analysis.get('recommendations', []):
        parts = rec['relationship'].split(' → ')
        from_entity = parts[0]
        to_entity = parts[1]
        decision = rec['decision']
        
        # Ensure collections exist
        if from_entity not in collections:
            collections[from_entity] = {
                'name': from_entity.lower() + 's',
                'schema': {'_id': 'ObjectId'},
                'indexes': []
            }
        
        # Add fields based on decision
        if decision == 'reference':
            field_name = to_entity.lower() + 'Id'
            collections[from_entity]['schema'][field_name] = 'ObjectId'
            collections[from_entity]['indexes'].append({'fields': [field_name]})
        
        elif decision == 'reference_with_denormalization':
            # Add reference
            id_field = to_entity.lower() + 'Id'
            collections[from_entity]['schema'][id_field] = 'ObjectId'
            collections[from_entity]['indexes'].append({'fields': [id_field]})
            
            # Add denormalized field
            denorm_field = to_entity.lower() + 'Name'
            collections[from_entity]['schema'][denorm_field] = 'string'
            
            denorm_rules.append({
                'from': f"{to_entity.lower()}s.name",
                'to': f"{collections[from_entity]['name']}.{denorm_field}",
                'sync_strategy': 'on_write'
            })
        
        elif decision == 'embed':
            embed_field = to_entity.lower() + 's'
            collections[from_entity]['schema'][embed_field] = 'array'
    
    return {
        'collections': list(collections.values()),
        'denormalization_rules': denorm_rules
    }

def main():
    parser = argparse.ArgumentParser(description='Generate MongoDB schema')
    parser.add_argument('analysis', help='Analysis JSON from relationship_analyzer.py')
    parser.add_argument('--output', default='schema.json')
    
    args = parser.parse_args()
    
    with open(args.analysis, 'r') as f:
        analysis = json.load(f)
    
    schema = generate_schema(analysis)
    
    with open(args.output, 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"✅ Generated {len(schema['collections'])} collections")
    print(f"✅ {len(schema['denormalization_rules'])} denormalization rules")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
