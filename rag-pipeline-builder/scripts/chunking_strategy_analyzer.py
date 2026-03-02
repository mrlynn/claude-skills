#!/usr/bin/env python3
"""
Analyze documents and recommend optimal chunking strategy.
Usage: python chunking_strategy_analyzer.py <docs_dir> [--output report.json]
"""

import os
import sys
import json
import argparse
from pathlib import Path

def detect_file_type(filepath):
    """Detect file type from extension."""
    ext = Path(filepath).suffix.lower()
    type_map = {
        '.md': 'markdown',
        '.txt': 'text',
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml'
    }
    return type_map.get(ext, 'unknown')

def analyze_content_structure(content):
    """Analyze content to determine if it's code, prose, or mixed."""
    lines = content.split('\n')
    total_lines = len(lines)
    
    if total_lines == 0:
        return 'unknown'
    
    code_indicators = 0
    prose_indicators = 0
    
    for line in lines[:min(100, total_lines)]:  # Sample first 100 lines
        stripped = line.strip()
        if not stripped:
            continue
        
        # Code indicators
        if any(char in stripped for char in ['def ', 'function ', 'class ', 'import ', 'const ', 'let ', 'var ']):
            code_indicators += 1
        if stripped.endswith(('{', '}', ';', ':')):
            code_indicators += 1
        
        # Prose indicators
        if len(stripped.split()) > 8 and not stripped.startswith(('#', '//', '/*')):
            prose_indicators += 1
    
    if code_indicators > prose_indicators * 2:
        return 'code'
    elif prose_indicators > code_indicators * 2:
        return 'prose'
    else:
        return 'mixed'

def estimate_tokens(text):
    """Rough token estimate (words * 1.3)."""
    words = len(text.split())
    return int(words * 1.3)

def recommend_strategy(file_type, content_structure):
    """Recommend chunking strategy based on analysis."""
    
    if content_structure == 'code' or file_type in ['python', 'javascript', 'typescript']:
        return {
            'strategy': 'function-boundary',
            'description': 'Split on function/class boundaries to keep code units intact',
            'chunk_size': 'variable',
            'overlap': 0
        }
    
    elif content_structure == 'prose' or file_type == 'markdown':
        return {
            'strategy': 'recursive',
            'description': 'Recursive splitting with paragraph boundaries preserved',
            'chunk_size': 1000,
            'overlap': 200
        }
    
    elif file_type in ['html', 'json', 'yaml']:
        return {
            'strategy': 'structural',
            'description': 'Split on structural boundaries (sections, objects)',
            'chunk_size': 'variable',
            'overlap': 0
        }
    
    else:
        return {
            'strategy': 'recursive',
            'description': 'Default recursive splitting',
            'chunk_size': 1000,
            'overlap': 200
        }

def analyze_directory(docs_dir):
    """Analyze all documents in directory."""
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        print(f"Error: Directory '{docs_dir}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    files_analyzed = []
    file_type_counts = {}
    total_tokens = 0
    
    for filepath in docs_path.rglob('*'):
        if filepath.is_file():
            file_type = detect_file_type(filepath)
            
            if file_type == 'unknown':
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError):
                continue
            
            content_structure = analyze_content_structure(content)
            tokens = estimate_tokens(content)
            strategy = recommend_strategy(file_type, content_structure)
            
            files_analyzed.append({
                'path': str(filepath.relative_to(docs_path)),
                'file_type': file_type,
                'content_structure': content_structure,
                'tokens': tokens,
                'strategy': strategy
            })
            
            file_type_counts[file_type] = file_type_counts.get(file_type, 0) + 1
            total_tokens += tokens
    
    return {
        'total_files': len(files_analyzed),
        'file_types': file_type_counts,
        'files': files_analyzed,
        'total_tokens': total_tokens
    }

def generate_recommendations(analysis):
    """Generate chunking recommendations per file type."""
    recommendations = {}
    
    # Group by file type
    by_type = {}
    for file_info in analysis['files']:
        ft = file_info['file_type']
        if ft not in by_type:
            by_type[ft] = []
        by_type[ft].append(file_info)
    
    # Recommend strategy per type
    for file_type, files in by_type.items():
        # Most common strategy for this file type
        strategies = [f['strategy']['strategy'] for f in files]
        most_common = max(set(strategies), key=strategies.count)
        
        total_tokens = sum(f['tokens'] for f in files)
        
        # Estimate chunks
        if most_common == 'recursive':
            chunk_size = 1000
            overlap = 200
            estimated_chunks = int(total_tokens / (chunk_size - overlap))
        else:
            # Function-boundary or structural (variable size)
            estimated_chunks = len(files) * 2  # Rough estimate
        
        recommendations[file_type] = {
            'strategy': most_common,
            'file_count': len(files),
            'total_tokens': total_tokens,
            'estimated_chunks': estimated_chunks
        }
    
    return recommendations

def estimate_cost(total_tokens):
    """Estimate Voyage AI embedding cost."""
    # Voyage-3: $0.02 per 1M tokens
    cost_per_million = 0.02
    return (total_tokens / 1_000_000) * cost_per_million

def main():
    parser = argparse.ArgumentParser(
        description='Analyze documents and recommend chunking strategy'
    )
    parser.add_argument('docs_dir', help='Directory containing documents')
    parser.add_argument('--output', help='Output JSON file', default=None)
    
    args = parser.parse_args()
    
    print(f"Analyzing documents in '{args.docs_dir}'...")
    
    analysis = analyze_directory(args.docs_dir)
    recommendations = generate_recommendations(analysis)
    
    total_chunks = sum(r['estimated_chunks'] for r in recommendations.values())
    cost = estimate_cost(analysis['total_tokens'])
    
    report = {
        'total_files': analysis['total_files'],
        'file_types': analysis['file_types'],
        'total_tokens': analysis['total_tokens'],
        'recommendations': recommendations,
        'estimated_total_chunks': total_chunks,
        'estimated_embedding_cost': f"${cost:.2f}"
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n✅ Report saved to {args.output}")
    else:
        print("\n" + "="*60)
        print("CHUNKING STRATEGY ANALYSIS")
        print("="*60)
        print(f"\nTotal Files: {report['total_files']}")
        print(f"Total Tokens: {report['total_tokens']:,}")
        print(f"Estimated Chunks: {total_chunks:,}")
        print(f"Estimated Embedding Cost: {report['estimated_embedding_cost']}")
        
        print("\nRecommendations by File Type:")
        print("-" * 60)
        for file_type, rec in recommendations.items():
            print(f"\n{file_type.upper()}:")
            print(f"  Files: {rec['file_count']}")
            print(f"  Strategy: {rec['strategy']}")
            print(f"  Tokens: {rec['total_tokens']:,}")
            print(f"  Est. Chunks: {rec['estimated_chunks']:,}")

if __name__ == '__main__':
    main()
