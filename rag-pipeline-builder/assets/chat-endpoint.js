// RAG Chat Endpoint with Streaming
// Usage: Add to your Next.js API routes (app/api/chat/route.js)

const { search } = require('./retrieval-api');
const OpenAI = require('openai');

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

function assembleContext(results) {
  return results.map((r, i) => 
    `[Source ${i+1}: ${r.source}]\n${r.text}`
  ).join('\n\n---\n\n');
}

async function logUsage(data) {
  // Fire-and-forget logging
  try {
    // Log to database or analytics service
    console.log('Usage logged:', { query: data.query, results: data.results.length });
  } catch (err) {
    console.error('Usage logging failed:', err);
  }
}

export async function POST(req) {
  const { query } = await req.json();
  
  if (!query) {
    return new Response(JSON.stringify({ error: 'Query required' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  try {
    // Retrieve relevant context
    const { results } = await search(query, { limit: 5 });
    const context = assembleContext(results);
    
    // Generate response with streaming
    const stream = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'Answer questions using ONLY the provided context. Cite sources using [Source N]. If the context doesn\'t contain the answer, say "I don\'t have information about that in the documentation."'
        },
        {
          role: 'user',
          content: `Context:\n${context}\n\nQuestion: ${query}\n\nAnswer:`
        }
      ],
      stream: true,
      max_tokens: 500
    });
    
    // Fire-and-forget usage logging
    logUsage({ query, results }).catch(() => {});
    
    // Stream response to client
    const encoder = new TextEncoder();
    const readable = new ReadableStream({
      async start(controller) {
        for await (const chunk of stream) {
          const text = chunk.choices[0]?.delta?.content || '';
          controller.enqueue(encoder.encode(text));
        }
        controller.close();
      }
    });
    
    return new Response(readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      }
    });
    
  } catch (error) {
    console.error('Chat failed:', error);
    return new Response(JSON.stringify({ error: 'Chat failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
