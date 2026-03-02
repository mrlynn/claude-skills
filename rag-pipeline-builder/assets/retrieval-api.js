// RAG Retrieval API with Score Boosting
// Usage: Add to your Express/Next.js API routes

const { MongoClient } = require('mongodb');
const { VoyageAIClient } = require('voyageai');

const MONGODB_URI = process.env.MONGODB_URI;
const VOYAGE_API_KEY = process.env.VOYAGE_API_KEY;
const COLLECTION_NAME = process.env.COLLECTION_NAME || 'documents';
const VECTOR_INDEX_NAME = process.env.VECTOR_INDEX_NAME || 'vector_index';

function boostScores(results, boostConfig = {}) {
  return results.map(r => ({
    ...r,
    original_score: r.score,
    boosted_score: r.score * (boostConfig[r.category] || 1.0)
  })).sort((a, b) => b.boosted_score - a.boosted_score);
}

async function search(query, options = {}) {
  const {
    limit = 5,
    filters = {},
    categoryBoost = { 'ui-docs': 1.5, 'examples': 1.2, 'api-reference': 1.0 }
  } = options;
  
  const mongoClient = new MongoClient(MONGODB_URI);
  const voyageClient = new VoyageAIClient({ apiKey: VOYAGE_API_KEY });
  
  try {
    // Embed query
    const embedding = await voyageClient.embed({
      input: [query],
      model: 'voyage-3'
    });
    const queryVector = embedding.data[0].embedding;
    
    // Connect to MongoDB
    await mongoClient.connect();
    const db = mongoClient.db();
    
    // Vector search with filters
    const pipeline = [
      {
        $vectorSearch: {
          index: VECTOR_INDEX_NAME,
          path: 'embedding',
          queryVector,
          numCandidates: limit * 10,
          limit,
          filter: filters
        }
      },
      {
        $project: {
          text: 1,
          source: 1,
          category: 1,
          source_url: 1,
          score: { $meta: 'vectorSearchScore' }
        }
      }
    ];
    
    const results = await db.collection(COLLECTION_NAME)
      .aggregate(pipeline)
      .toArray();
    
    // Apply score boosting
    const boosted = boostScores(results, categoryBoost);
    
    return {
      results: boosted,
      meta: {
        query,
        total_results: boosted.length,
        filters_applied: Object.keys(filters).length > 0
      }
    };
    
  } finally {
    await mongoClient.close();
  }
}

// Express/Next.js handler example
async function handler(req, res) {
  const { query, limit, category } = req.body;
  
  if (!query) {
    return res.status(400).json({ error: 'Query required' });
  }
  
  const filters = category ? { category } : {};
  
  try {
    const results = await search(query, { limit, filters });
    res.json(results);
  } catch (error) {
    console.error('Search failed:', error);
    res.status(500).json({ error: 'Search failed' });
  }
}

module.exports = { search, handler };
