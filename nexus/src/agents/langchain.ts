// NEXUS Platform - AI Agent with LangChain & LangGraph
import { ChatOpenAI } from '@langchain/openai';
import { HumanMessage, SystemMessage, AIMessage } from '@langchain/core/messages';
import { createReactAgent } from '@langchain/langgraph/prebuilt';
import { pullAt } from '@langchain/core/utils/fast';
import { MemoryVectorStore } from 'langchain/vectorstores/memory';
import { OpenAIEmbeddings } from '@langchain/openai';
import { EventEmitter } from 'events';
import type { Message, AIMessage as NEXUSAIMessage } from '../types/index.js';

interface NEXUSLLMConfig {
  openaiKey?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
}

interface Tool {
  name: string;
  description: string;
  handler: (input: any) => Promise<string>;
}

export class NEXUSLLMAgent extends EventEmitter {
  private llm: ChatOpenAI | null = null;
  private embeddings: OpenAIEmbeddings | null = null;
  private vectorStore: MemoryVectorStore | null = null;
  private tools: Map<string, Tool> = new Map();
  private config: NEXUSLLMConfig;
  private conversationHistory: NEXUSAIMessage[] = [];

  constructor(config: NEXUSLLMConfig = {}) {
    super();
    this.config = {
      model: 'gpt-4-turbo',
      temperature: 0.7,
      maxTokens: 2000,
      ...config,
    };
  }

  initialize(): void {
    if (this.config.openaiKey) {
      this.llm = new ChatOpenAI({
        openAIApiKey: this.config.openaiKey,
        model: this.config.model,
        temperature: this.config.temperature,
        maxTokens: this.config.maxTokens,
      });

      this.embeddings = new OpenAIEmbeddings({
        openAIApiKey: this.config.openaiKey,
      });

      this.vectorStore = new MemoryVectorStore(this.embeddings);
      console.log('✅ NEXUS AI Agent initialized with LangChain');
    }
  }

  registerTool(name: string, description: string, handler: (input: any) => Promise<string>): void {
    this.tools.set(name, { name, description, handler });
    console.log(`✅ Tool registered: ${name}`);
  }

  async processMessage(message: Message): Promise<string> {
    if (!this.llm) {
      return 'AI Agent not initialized. Please provide OPENAI_API_KEY.';
    }

    const userMessage: NEXUSAIMessage = {
      role: 'user',
      content: message.content,
      timestamp: new Date(),
    };
    this.conversationHistory.push(userMessage);

    // Detect intent
    const intent = this.detectIntent(message.content);
    this.emit('intent', intent);

    // Find matching tool
    let response: string;
    const tool = this.findTool(intent);

    if (tool) {
      try {
        response = await tool.handler(message.content);
      } catch (error) {
        response = `Error executing ${tool.name}: ${error}`;
      }
    } else {
      // Use LLM for general responses
      const systemPrompt = this.getSystemPrompt(intent);
      const messages = [
        new SystemMessage(systemPrompt),
        ...this.conversationHistory.slice(-10).map(
          (m) => m.role === 'user' ? new HumanMessage(m.content) : new AIMessage(m.content)
        ),
      ];

      const result = await this.llm.invoke(messages);
      response = typeof result === 'string' ? result : result.content as string;
    }

    const assistantMessage: NEXUSAIMessage = {
      role: 'assistant',
      content: response,
      timestamp: new Date(),
    };
    this.conversationHistory.push(assistantMessage);
    this.emit('response', response);

    return response;
  }

  private detectIntent(content: string): string {
    const lower = content.toLowerCase();
    
    if (lower.includes('whatsapp') || lower.includes('wa ')) return 'whatsapp';
    if (lower.includes('telegram') || lower.includes('tg ')) return 'telegram';
    if (lower.includes('github') || lower.includes('pr') || lower.includes('issue')) return 'github';
    if (lower.includes('calendar') || lower.includes('book') || lower.includes('appointment')) return 'calendar';
    if (lower.includes('crm') || lower.includes('customer') || lower.includes('lead')) return 'crm';
    if (lower.includes('document') || lower.includes('pdf') || lower.includes('parse')) return 'document';
    if (lower.includes('search') || lower.includes('find')) return 'search';
    if (lower.includes('schedule') || lower.includes('queue') || lower.includes('job')) return 'queue';
    if (lower.includes('help') || lower.includes('command')) return 'help';
    
    return 'general';
  }

  private findTool(intent: string): Tool | undefined {
    // Map intents to registered tools
    const toolMap: Record<string, string> = {
      whatsapp: 'whatsapp',
      telegram: 'telegram',
      github: 'github',
      calendar: 'calendar',
      crm: 'crm',
      document: 'document',
      search: 'vector_search',
      queue: 'queue',
    };
    
    const toolName = toolMap[intent];
    return toolName ? this.tools.get(toolName) : undefined;
  }

  private getSystemPrompt(intent: string): string {
    const basePrompt = `You are NEXUS, an advanced AI assistant in a unified automation platform.

You have access to:
- WhatsApp messaging and automation
- Telegram bot management
- GitHub repository and PR management
- Calendar/booking system (Cal.com)
- CRM for customer management
- Document parsing and analysis
- Vector search for knowledge retrieval
- Background job processing

Current channel: ${intent === 'general' ? 'multi-channel' : intent}

Be helpful, concise, and actionable.`;
    return basePrompt;
  }

  // Vector Store Operations
  async addToMemory(text: string, metadata?: Record<string, any>): Promise<void> {
    if (!this.vectorStore) return;
    await this.vectorStore.addTextDocuments([text], { metadata });
  }

  async searchMemory(query: string, k = 5): Promise<string[]> {
    if (!this.vectorStore) return [];
    const results = await this.vectorStore.similaritySearch(query, k);
    return results.map((r) => r.pageContent);
  }

  async clearMemory(): Promise<void> {
    if (!this.vectorStore) return;
    // Note: MemoryVectorStore doesn't have a clear method, recreate
    this.vectorStore = new MemoryVectorStore(this.embeddings!);
  }

  clearHistory(): void {
    this.conversationHistory = [];
  }

  getHistory(): NEXUSAIMessage[] {
    return [...this.conversationHistory];
  }
}

export default NEXUSLLMAgent;
