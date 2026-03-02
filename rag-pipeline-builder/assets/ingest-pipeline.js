// RAG Ingestion Pipeline with Content Hashing
// Usage: node ingest-pipeline.js

const crypto = require('crypto');
const { MongoClient } = require('mongodb');
const { VoyageAIClient } = require('voyageai');

const MONGODB_URI = process.env.MONGODB_URI;
const VOYAGE_API_KEY = process.env.VOYAGE_API_KEY;
const COLLECTION_NAME = process.env.COLLECTION_NAME || 'documents';
const CHUNK_SIZE = parseInt(process.env.CHUNK_SIZE) || 1000;
const CHUNK_OVERLAP = parseInt(process.env.CHUNK_OVERLAP) || 200;

async function hashContent(text) {
  return crypto.createHash('sha256').update(text).digest('hex');
}

async function chunkDocument(text, chunkSize = CHUNK_SIZE, overlap = CHUNK_OVERLAP) {
  const words = text.split(' ');
  const chunks = [];
  
  for (let i = 0; i < words.length; i += (chunkSize - overlap)) {
    const chunk = words.slice(i, i + chunkSize).join(' ');
    if (chunk.trim()) {
      chunks.push(chunk);
    }
  }
  
  return chunks;
}

async function ingestDocument(db, voyageClient, document) {
  const { id, text, category, source } = document;
  
  // Hash content for incremental updates
  const contentHash = await hashContent(text);
  
  // Check if already ingested
  const existing = await db.collection(COLLECTION_NAME).findOne({
    source: id,
    content_hash: contentHash
  });
  
  if (existing) {
    console.log(`⏭️  Skipping unchanged: ${id}`);
    return { status: 'skipped', id };
  }
  
  // Chunk document
  const chunks = await chunkDocument(text);
  console.log(`📝 Processing ${id}: ${chunks.length} chunks`);
  
  // Batch embed (128 at a time)
  const embeddings = [];
  for (let i = 0; i < chunks.length; i += 128) {
    const batch = chunks.slice(i, i + 128);
    const batchEmbeddings = await voyageClient.embed({
      input: batch,
      model: 'voyage-3'
    });
    embeddings.push(...batchEmbeddings.data.map(e => e.embedding));
  }
  
  // Store in MongoDB
  const documents = chunks.map((chunk, i) => ({
    text: chunk,
    embedding: embeddings[i],
    source: id,
    category,
    source_url: source,
    content_hash: contentHash,
    chunk_index: i,
    total_chunks: chunks.length,
    ingested_at: new Date()
  }));
  
  await db.collection(COLLECTION_NAME).insertMany(documents);
  console.log(`✅ Ingested ${id}: ${documents.length} chunks`);
  
  return { status: 'ingested', id, chunks: documents.length };
}

async function main() {
  const mongoClient = new MongoClient(MONGODB_URI);
  const voyageClient = new VoyageAIClient({ apiKey: VOYAGE_API_KEY });
  
  try {
    await mongoClient.connect();
    const db = mongoClient.db();
    
    // Example: ingest documents from a directory or array
    const documents = [
      {
        id: 'doc1',
        text: 'Your document text here...',
        category: 'ui-docs',
        source: 'https://example.com/doc1'
      }
      // Add more documents...
    ];
    
    for (const doc of documents) {
      await ingestDocument(db, voyageClient, doc);
    }
    
    console.log('\n✅ Ingestion complete!');
  } finally {
    await mongoClient.close();
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { ingestDocument, chunkDocument, hashContent };
