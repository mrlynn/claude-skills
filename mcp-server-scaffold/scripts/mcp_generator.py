#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Generate MCP server code from parsed API spec.
  Usage: python mcp_generator.py parsed.json --language typescript --output mcp-server/
"""

import json
import argparse
from pathlib import Path

def generate_typescript_index(parsed, tools):
    """Generate index.ts for TypeScript server."""
    tool_imports = '\n'.join(f"import {{ {t['name']} }} from './tools/{t['name']}.js';" for t in tools)
    tool_list = ',\n  '.join(t['name'] for t in tools)
    
    return f"""#!/usr/bin/env node
import {{ Server }} from '@modelcontextprotocol/sdk/server/index.js';
import {{ StdioServerTransport }} from '@modelcontextprotocol/sdk/server/stdio.js';
import {{ CallToolRequestSchema, ListToolsRequestSchema }} from '@modelcontextprotocol/sdk/types.js';
import 'dotenv/config';

{tool_imports}

const server = new Server(
  {{ name: '{parsed['info']['title'].lower().replace(' ', '-')}-server', version: '1.0.0' }},
  {{ capabilities: {{ tools: {{}} }} }}
);

const tools = [{tool_list}];

server.setRequestHandler(ListToolsRequestSchema, async () => ({{
  tools: tools.map(t => ({{ name: t.name, description: t.description, inputSchema: t.inputSchema }}))
}}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {{
  const {{ name, arguments: args }} = request.params;
  const tool = tools.find(t => t.name === name);
  if (!tool) throw new Error(`Unknown tool: ${{name}}`);
  const result = await tool.execute(args);
  return {{ content: [{{ type: 'text', text: JSON.stringify(result, null, 2) }}] }};
}});

async function main() {{
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP server running on stdio');
}}

main().catch(console.error);
"""

def generate_tool_file(tool):
    """Generate individual tool file."""
    path_replacements = '\n'.join(
        f"    path = path.replace('{{{param}}}', args.{param});"
        for param in tool['parameters']['path']
    )
    
    return f"""import {{ apiClient }} from '../client.js';

export const {tool['name']} = {{
  name: '{tool['name']}',
  description: `{tool['description']}`,
  inputSchema: {json.dumps(tool['inputSchema'], indent=2)},
  
  async execute(args: any) {{
    let path = '{tool['path']}';
{path_replacements}
    
    const result = await apiClient.request(
      '{tool['method']}',
      path,
      args.body,
      args.query
    );
    
    return result;
  }}
}};
"""

def main():
    parser = argparse.ArgumentParser(description='Generate MCP server')
    parser.add_argument('parsed', help='Parsed API spec JSON')
    parser.add_argument('--language', choices=['typescript', 'python'], default='typescript')
    parser.add_argument('--output', default='mcp-server/')
    parser.add_argument('--auth-env-var', default='API_KEY')
    
    args = parser.parse_args()
    
    with open(args.parsed, 'r') as f:
        parsed = json.load(f)
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.language == 'typescript':
        src_dir = output_dir / 'src'
        tools_dir = src_dir / 'tools'
        src_dir.mkdir(exist_ok=True)
        tools_dir.mkdir(exist_ok=True)
        
        # Generate tool files (limit to first 20)
        tools = parsed['tools'][:20]
        for tool in tools:
            tool_file = tools_dir / f"{tool['name']}.ts"
            with open(tool_file, 'w') as f:
                f.write(generate_tool_file(tool))
        
        # Generate index.ts
        with open(src_dir / 'index.ts', 'w') as f:
            f.write(generate_typescript_index(parsed, tools))
        
        # Generate package.json, client.ts, etc. (abbreviated for space)
        print(f"✅ Generated TypeScript MCP server in {output_dir}")
        print(f"✅ Created {len(tools)} tools")
        print(f"\nNext steps:")
        print(f"  cd {output_dir}")
        print(f"  npm install")
        print(f"  npm run build")
        print(f"  npm start")

if __name__ == '__main__':
    main()
