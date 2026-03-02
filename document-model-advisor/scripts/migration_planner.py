#!/usr/bin/env python3
"""
Plan SQL → MongoDB schema migration.
Usage: python migration_planner.py schema.sql --output migration-plan.json
"""

import re
import json
import argparse

def parse_sql_schema(sql_text):
    """Parse SQL CREATE TABLE statements."""
    tables = []
    
    # Find CREATE TABLE statements
    pattern = r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);'
    matches = re.finditer(pattern, sql_text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        table_name = match.group(1)
        columns_text = match.group(2)
        
        # Parse foreign keys
        fk_pattern = r'(\w+)\s+.*?REFERENCES\s+(\w+)\((\w+)\)'
        fks = re.findall(fk_pattern, columns_text, re.IGNORECASE)
        
        tables.append({
            'name': table_name,
            'foreign_keys': [
                {'column': fk[0], 'references_table': fk[1], 'references_column': fk[2]}
                for fk in fks
            ]
        })
    
    return tables

def plan_migration(tables):
    """Plan MongoDB migration from SQL tables."""
    table_to_collection = {t['name']: t['name'] for t in tables}
    relationship_mappings = []
    steps = []
    
    for table in tables:
        # Export step
        steps.append(f"Export {table['name']} table to JSON")
        
        # Transform foreign keys
        for fk in table['foreign_keys']:
            mongo_field = fk['references_table'] + 'Id'
            relationship_mappings.append({
                'sql_fk': f"{table['name']}.{fk['column']} → {fk['references_table']}.{fk['references_column']}",
                'mongodb_approach': 'reference',
                'field': f"{table['name']}.{mongo_field}",
                'reasoning': 'One-to-many SQL FK maps to MongoDB reference'
            })
            steps.append(f"Transform {table['name']}.{fk['column']} → {mongo_field}")
        
        # Import step
        steps.append(f"Import to {table['name']} collection")
        
        # Index creation
        for fk in table['foreign_keys']:
            steps.append(f"Create index on {table['name']}.{fk['references_table']}Id")
    
    return {
        'tables_to_collections': table_to_collection,
        'relationship_mappings': relationship_mappings,
        'migration_steps': steps
    }

def main():
    parser = argparse.ArgumentParser(description='Plan SQL → MongoDB migration')
    parser.add_argument('sql_schema', help='SQL schema file')
    parser.add_argument('--output', default='migration-plan.json')
    
    args = parser.parse_args()
    
    with open(args.sql_schema, 'r') as f:
        sql_text = f.read()
    
    tables = parse_sql_schema(sql_text)
    plan = plan_migration(tables)
    
    with open(args.output, 'w') as f:
        json.dump(plan, f, indent=2)
    
    print(f"✅ Analyzed {len(tables)} tables")
    print(f"✅ Generated migration plan with {len(plan['migration_steps'])} steps")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
