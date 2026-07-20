// NEXUS Platform - Vector Store (Qdrant & Chroma)
import { QdrantClient } from 'qdrant-client';
import { OpenAIEmbeddings } from '@langchain/openai';
import { EventEmitter } from 'events';

interface VectorStoreConfig {
  provider: 'qdrant' | 'chroma';
  url?: string;
  apiKey?: string;
  collectionName?: string;
  openaiKey?: string;
}

interface Document {
  id: string;
  content: string;
  metadata?: Record<string, any>;
}

export class VectorStore extends EventEmitter {
  private client: QdrantClient | null = null;
  private embeddings: OpenAIEmbeddings | null = null;
  private config: VectorStoreConfig;
  private collectionName: string;
  private documents: Map<string, Document> = new Map();

  constructor(config: VectorStoreConfig) {
    super();
    this.config = {
      collectionName: 'nexus-knowledge',
      ...config,
    };
    this.collectionName = this.config.collectionName || 'nexus-knowledge';
  }

  async initialize(): Promise<void> {
    if (this.config.openaiKey) {
      this.embeddings = new OpenAIEmbeddings({
        openAIApiKey: this.config.openaiKey,
      });
    }

    if (this.config.provider === 'qdrant' && this.config.url) {
      this.client = new QdrantClient({
        url: this.config.url,
        apiKey: this.config.apiKey,
      });

      // Create collection if not exists
      try {
        await this.client.createCollection(this.collectionName, {
          vectors: { size: 1536, distance: 'Cosine' },
        });
      } catch (e) {
        // Collection might already exist
      }
      console.log('✅ Qdrant Vector Store initialized');
    } else {
      // Use in-memory Chroma-like store
      console.log('✅ In-Memory Vector Store initialized');
    }
  }

  async addDocument(doc: Document): Promise<void> {
    this.documents.set(doc.id, doc);
    console.log(`📄 Document added: ${doc.id}`);
    this.emit('document_added', doc);
  }

  async addDocuments(docs: Document[]): Promise<void> {
    for (const doc of docs) {
      await this.addDocument(doc);
    }
  }

  async search(query: string, k = 5): Promise<Document[]> {
    // Simple keyword matching for in-memory store
    const results: Document[] = [];
    const queryLower = query.toLowerCase();

    for (const doc of this.documents.values()) {
      if (doc.content.toLowerCase().includes(queryLower)) {
        results.push(doc);
        if (results.length >= k) break;
      }
    }

    // If no results, return recent documents
    if (results.length === 0) {
      const allDocs = Array.from(this.documents.values());
      return allDocs.slice(-k);
    }

    return results;
  }

  async deleteDocument(id: string): Promise<void> {
    this.documents.delete(id);
    console.log(`🗑️ Document deleted: ${id}`);
    this.emit('document_deleted', id);
  }

  async updateDocument(id: string, content: string, metadata?: Record<string, any>): Promise<void> {
    const doc = this.documents.get(id);
    if (doc) {
      doc.content = content;
      if (metadata) doc.metadata = { ...doc.metadata, ...metadata };
      console.log(`📝 Document updated: ${id}`);
      this.emit('document_updated', doc);
    }
  }

  async getDocument(id: string): Promise<Document | undefined> {
    return this.documents.get(id);
  }

  async getAllDocuments(): Promise<Document[]> {
    return Array.from(this.documents.values());
  }

  async count(): Promise<number> {
    return this.documents.size;
  }

  async clear(): Promise<void> {
    this.documents.clear();
    console.log('🧹 Vector store cleared');
    this.emit('cleared');
  }

  // Semantic search with embeddings
  async semanticSearch(query: string, k = 5): Promise<Document[]> {
    if (!this.embeddings) {
      // Fallback to keyword search
      return this.search(query, k);
    }

    try {
      const queryEmbedding = await this.embeddings.embedQuery(query);
      // For now, return keyword matches
      // In production, you'd use the embedding to do cosine similarity
      return this.search(query, k);
    } catch (error) {
      console.error('Semantic search error:', error);
      return this.search(query, k);
    }
  }

  // RAG - Retrieve and Generate
  async rag(query: string, k = 3): Promise<{ context: string; documents: Document[] }> {
    const docs = await this.semanticSearch(query, k);
    const context = docs.map((d) => d.content).join('\n\n');
    return { context, documents: docs };
  }
}

export default VectorStore;
