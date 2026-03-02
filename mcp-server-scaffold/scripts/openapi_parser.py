#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Parse OpenAPI/Swagger specs and extract MCP tool definitions.
  Usage: python openapi_parser.py api-spec.yaml --output parsed.json
"""

import json
import yaml
import argparse
from pathlib import Path

def to_snake_case(text):
    """Convert text to snake_case."""
    import re
    text = re.sub(r'[^a-zA-Z0-9]', '_', text)
    text = re.sub(r'_+', '_', text)
    return text.lower().strip('_')

def extract_tool_name(method, path):
    """Generate tool name from HTTP method and path."""
    # Remove version prefixes like /api/v1
    path = path.replace('/api', '').replace('/v1', '').replace('/v2', '')
    
    # Extract path segments
    segments = [s for s in path.split('/') if s and not s.startswith('{')]
    
    # Combine method + segments
    tool_name = f"{method.lower()}_{'_'.join(segments)}"
    return to_snake_case(tool_name)

def extract_parameters(parameters, requestBody=None):
    """Extract parameters from OpenAPI spec."""
    result = {
        'path': [],
        'query': [],
        'header': [],
        'body': None
    }
    
    if parameters:
        for param in parameters:
            param_in = param.get('in', 'query')
            param_name = param.get('name')
            
            if param_in == 'path':
                result['path'].append(param_name)
            elif param_in == 'query':
                result['query'].append(param_name)
            elif param_in == 'header':
                result['header'].append(param_name)
    
    if requestBody:
        content = requestBody.get('content', {})
        if 'application/json' in content:
            result['body'] = content['application/json'].get('schema', {})
    
    return result

def build_input_schema(parameters_info, operation):
    """Build JSON schema for tool input."""
    properties = {}
    required = []
    
    # Path parameters (always required)
    for param_name in parameters_info['path']:
        properties[param_name] = {
            'type': 'string',
            'description': f'Path parameter: {param_name}'
        }
        required.append(param_name)
    
    # Query parameters
    params_list = operation.get('parameters', [])
    for param in params_list:
        if param.get('in') == 'query':
            param_name = param.get('name')
            param_schema = param.get('schema', {'type': 'string'})
            properties[param_name] = {
                'type': param_schema.get('type', 'string'),
                'description': param.get('description', '')
            }
            if param.get('required'):
                required.append(param_name)
    
    # Body parameters
    if parameters_info['body']:
        body_schema = parameters_info['body']
        if 'properties' in body_schema:
            properties.update(body_schema['properties'])
            if 'required' in body_schema:
                required.extend(body_schema['required'])
    
    return {
        'type': 'object',
        'properties': properties,
        'required': required if required else []
    }

def parse_openapi_spec(spec_path, filter_tags=None):
    """Parse OpenAPI spec and extract tool definitions."""
    # Load spec
    with open(spec_path, 'r') as f:
        if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)
    
    # Extract info
    info = {
        'title': spec.get('info', {}).get('title', 'API'),
        'version': spec.get('info', {}).get('version', '1.0.0'),
        'description': spec.get('info', {}).get('description', ''),
        'baseUrl': spec.get('servers', [{}])[0].get('url', 'https://api.example.com')
    }
    
    # Extract auth
    security_schemes = spec.get('components', {}).get('securitySchemes', {})
    auth = None
    if security_schemes:
        first_scheme = list(security_schemes.values())[0]
        auth = {
            'type': first_scheme.get('type', 'apiKey'),
            'in': first_scheme.get('in', 'header'),
            'name': first_scheme.get('name', 'Authorization')
        }
    
    # Extract tools from paths
    tools = []
    paths = spec.get('paths', {})
    
    for path, path_item in paths.items():
        for method in ['get', 'post', 'put', 'delete', 'patch']:
            if method not in path_item:
                continue
            
            operation = path_item[method]
            
            # Filter by tags if specified
            if filter_tags:
                operation_tags = operation.get('tags', [])
                if not any(tag in filter_tags for tag in operation_tags):
                    continue
            
            # Generate tool
            tool_name = extract_tool_name(method, path)
            description = operation.get('summary') or operation.get('description', f'{method.upper()} {path}')
            
            parameters_info = extract_parameters(
                operation.get('parameters'),
                operation.get('requestBody')
            )
            
            input_schema = build_input_schema(parameters_info, operation)
            
            # Extract response schema
            responses = operation.get('responses', {})
            success_response = responses.get('200') or responses.get('201') or {}
            response_content = success_response.get('content', {})
            response_schema = response_content.get('application/json', {}).get('schema', {})
            
            tools.append({
                'name': tool_name,
                'description': description,
                'method': method.upper(),
                'path': path,
                'parameters': parameters_info,
                'inputSchema': input_schema,
                'responseSchema': response_schema
            })
    
    return {
        'info': info,
        'auth': auth,
        'tools': tools
    }

def main():
    parser = argparse.ArgumentParser(description='Parse OpenAPI spec for MCP tools')
    parser.add_argument('spec', help='OpenAPI spec file (YAML or JSON)')
    parser.add_argument('--output', help='Output JSON file', default='parsed.json')
    parser.add_argument('--filter', help='Filter by tags (comma-separated)', default=None)
    
    args = parser.parse_args()
    
    filter_tags = args.filter.split(',') if args.filter else None
    
    print(f"Parsing OpenAPI spec: {args.spec}")
    if filter_tags:
        print(f"Filtering by tags: {filter_tags}")
    
    result = parse_openapi_spec(args.spec, filter_tags)
    
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Parsed {len(result['tools'])} tools")
    print(f"✅ Saved to {args.output}")
    
    print("\nTools extracted:")
    for tool in result['tools'][:10]:  # Show first 10
        print(f"  - {tool['name']}: {tool['description'][:60]}...")
    
    if len(result['tools']) > 10:
        print(f"  ... and {len(result['tools']) - 10} more")

if __name__ == '__main__':
    main()
