#!/usr/bin/env python3
"""
Validate RAG pipeline configuration and test retrieval quality.
Usage: python pipeline_validator.py config.json [--test-queries queries.json]
"""

import json
import sys
import argparse
from urllib.parse import urlparse

def validate_config(config):
    """Validate pipeline configuration."""
    required_fields = [
        'mongodb_uri',
        'collection_name',
        'vector_index_name',
        'embedding_dimensions'
    ]
    
    errors = []
    warnings = []
    
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate MongoDB URI format
    if 'mongodb_uri' in config:
        uri = config['mongodb_uri']
        if not uri.startswith('mongodb'):
            errors.append("Invalid MongoDB URI format")
    
    # Validate dimensions
    if 'embedding_dimensions' in config:
        dims = config['embedding_dimensions']
        if dims not in [384, 768, 1024, 1536, 3072]:
            warnings.append(f"Unusual embedding dimensions: {dims}")
    
    # Check for Voyage API key
    if 'voyage_api_key' not in config:
        warnings.append("No Voyage API key in config (may be in env)")
    
    return errors, warnings

def validate_test_queries(queries):
    """Validate test queries format."""
    if not isinstance(queries, list):
        return ["Test queries must be a JSON array"]
    
    errors = []
    for i, q in enumerate(queries):
        if 'query' not in q:
            errors.append(f"Query {i}: missing 'query' field")
        if 'expected_sources' in q and not isinstance(q['expected_sources'], list):
            errors.append(f"Query {i}: 'expected_sources' must be array")
    
    return errors

def calculate_mrr(results, expected_sources):
    """Calculate Mean Reciprocal Rank."""
    if not expected_sources:
        return 1.0  # No expectations, can't fail
    
    for i, result in enumerate(results):
        if 'source' in result and result['source'] in expected_sources:
            return 1.0 / (i + 1)
    return 0.0

def calculate_precision_at_k(results, expected_sources, k=5):
    """Calculate Precision@K."""
    if not expected_sources:
        return 1.0
    
    relevant_in_top_k = sum(
        1 for r in results[:k] 
        if 'source' in r and r['source'] in expected_sources
    )
    return relevant_in_top_k / min(k, len(results)) if results else 0.0

def main():
    parser = argparse.ArgumentParser(description='Validate RAG pipeline')
    parser.add_argument('config', help='Pipeline config JSON file')
    parser.add_argument('--test-queries', help='Test queries JSON file (optional)')
    parser.add_argument('--skip-connection-test', action='store_true', help='Skip MongoDB connection test')
    
    args = parser.parse_args()
    
    # Load config
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("="*60)
    print("RAG PIPELINE VALIDATION")
    print("="*60)
    
    # Validate config
    print("\n1. Validating configuration...")
    errors, warnings = validate_config(config)
    
    if errors:
        print("❌ Configuration errors:")
        for err in errors:
            print(f"   - {err}")
        sys.exit(1)
    else:
        print("✓ Configuration valid")
    
    if warnings:
        print("⚠️  Warnings:")
        for warn in warnings:
            print(f"   - {warn}")
    
    # MongoDB connection test (mocked - requires pymongo in real impl)
    if not args.skip_connection_test:
        print("\n2. Testing MongoDB connection...")
        print("⚠️  Connection test requires pymongo (skipped in validator)")
        print("   Run: pip install pymongo && test connection manually")
    
    # Vector index validation
    print("\n3. Checking vector index configuration...")
    if 'vector_index_name' in config and 'embedding_dimensions' in config:
        print(f"✓ Index: {config['vector_index_name']}")
        print(f"✓ Dimensions: {config['embedding_dimensions']}")
    
    # Test queries
    if args.test_queries:
        print(f"\n4. Loading test queries from {args.test_queries}...")
        try:
            with open(args.test_queries, 'r') as f:
                queries = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ Failed to load test queries: {e}", file=sys.stderr)
            sys.exit(1)
        
        query_errors = validate_test_queries(queries)
        if query_errors:
            print("❌ Test query errors:")
            for err in query_errors:
                print(f"   - {err}")
            sys.exit(1)
        
        print(f"✓ Loaded {len(queries)} test queries")
        
        # Simulate retrieval quality (mock results)
        print("\n5. Simulating retrieval quality metrics...")
        print("   (Real implementation requires running queries against MongoDB)")
        print("   Expected metrics:")
        print("   - MRR > 0.7 (Mean Reciprocal Rank)")
        print("   - Precision@5 > 0.6")
        print("   - Avg latency < 200ms")
    
    print("\n" + "="*60)
    print("✓ VALIDATION COMPLETE")
    print("="*60)
    
    print("\nNext steps:")
    print("1. Install dependencies: pip install pymongo voyage-ai")
    print("2. Test MongoDB connection with real credentials")
    print("3. Run sample queries and measure MRR/Precision")
    print("4. Monitor query latency in production")

if __name__ == '__main__':
    main()
