#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Test MCP server tools and validate responses.
  Usage: python server_tester.py mcp-server/ --test-all
"""

import json
import argparse
from pathlib import Path

def validate_tool_schema(tool_file):
    """Validate tool has required fields."""
    with open(tool_file, 'r') as f:
        content = f.read()
    
    required = ['name:', 'description:', 'inputSchema:', 'execute(']
    results = {field: field in content for field in required}
    
    return all(results.values()), results

def test_all_tools(server_dir):
    """Test all tools in server directory."""
    server_path = Path(server_dir)
    tools_dir = server_path / 'src' / 'tools'
    
    if not tools_dir.exists():
        print(f"❌ Tools directory not found: {tools_dir}")
        return
    
    tool_files = list(tools_dir.glob('*.ts')) + list(tools_dir.glob('*.py'))
    
    results = {
        'total_tools': len(tool_files),
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    for tool_file in tool_files:
        valid, checks = validate_tool_schema(tool_file)
        
        result = {
            'tool': tool_file.stem,
            'valid': valid,
            'checks': checks
        }
        
        results['details'].append(result)
        
        if valid:
            results['passed'] += 1
            print(f"✓ {tool_file.stem}")
        else:
            results['failed'] += 1
            print(f"✗ {tool_file.stem}")
            for field, passed in checks.items():
                if not passed:
                    print(f"  Missing: {field}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Test MCP server')
    parser.add_argument('server_dir', help='MCP server directory')
    parser.add_argument('--test-all', action='store_true', help='Test all tools')
    parser.add_argument('--output', help='Output JSON report', default=None)
    
    args = parser.parse_args()
    
    print(f"Testing MCP server: {args.server_dir}\n")
    
    results = test_all_tools(args.server_dir)
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Total Tools: {results['total_tools']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Report saved to {args.output}")

if __name__ == '__main__':
    main()
