#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Analyze entity relationships and recommend embed vs reference.
  Usage: python relationship_analyzer.py entities.json --output analysis.json
"""

import json
import argparse

def analyze_relationship(relationship, from_entity, to_entity):
    """Analyze a single relationship and recommend strategy."""
    score = 0
    reasons = []
    
    # Factor 1: Access pattern
    access = relationship.get('accessPattern', 'together')
    if access == 'together':
        score += 3
        reasons.append("Data accessed together")
    else:
        score -= 2
        reasons.append("Data accessed separately")
    
    # Factor 2: Cardinality
    typical_count = relationship.get('typical_count', 1)
    if isinstance(typical_count, str) and typical_count == 'unbounded':
        score -= 5
        reasons.append("Unbounded relationship (avoid embedding)")
    elif isinstance(typical_count, int) and typical_count <= 10:
        score += 2
        reasons.append(f"Bounded count ({typical_count})")
    
    # Factor 3: Update frequency
    update_freq = relationship.get('update_frequency', 'rare')
    if update_freq == 'frequent':
        score -= 2
        reasons.append("Frequently updated (avoid large embedded docs)")
    else:
        score += 1
        reasons.append("Rarely updated")
    
    # Factor 4: Relationship type
    rel_type = relationship.get('type', 'one-to-many')
    if rel_type == 'one-to-few':
        score += 2
    elif rel_type in ['one-to-many', 'many-to-many']:
        score -= 2
    
    # Decision
    if score >= 3:
        decision = 'embed'
    elif score <= -3:
        decision = 'reference'
    else:
        decision = 'reference_with_denormalization'
    
    confidence = min(abs(score) / 10, 1.0)
    
    return {
        'relationship': f"{from_entity['name']} → {relationship['to']}",
        'decision': decision,
        'reasoning': reasons,
        'score': score,
        'confidence': round(confidence, 2)
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze entity relationships')
    parser.add_argument('entities', help='Entity definitions JSON file')
    parser.add_argument('--output', default='analysis.json')
    
    args = parser.parse_args()
    
    with open(args.entities, 'r') as f:
        data = json.load(f)
    
    recommendations = []
    
    for entity in data.get('entities', []):
        for relationship in entity.get('relationships', []):
            # Find target entity
            to_entity = next((e for e in data['entities'] if e['name'] == relationship['to']), None)
            if to_entity:
                rec = analyze_relationship(relationship, entity, to_entity)
                recommendations.append(rec)
    
    result = {'recommendations': recommendations}
    
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✅ Analyzed {len(recommendations)} relationships")
    print(f"✅ Saved to {args.output}")
    
    for rec in recommendations:
        print(f"\n{rec['relationship']}:")
        print(f"  Decision: {rec['decision']} (confidence: {rec['confidence']})")
        print(f"  Reasons: {', '.join(rec['reasoning'])}")

if __name__ == '__main__':
    main()
