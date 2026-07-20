// NEXUS Platform - AI Agent Core
import OpenAI from 'openai';
import { EventEmitter } from 'events';
import type { Message, AIMessage } from '../types/index.js';

interface AgentConfig {
  openaiKey?: string;
  model?: string;
  systemPrompt?: string;
  onError?: (error: Error) => void;
}

interface IntentResult {
  intent: string;
  confidence: number;
  entities: Record<string, string>;
}

export class NEXUSAgent extends EventEmitter {
  private client: OpenAI | null = null;
  private config: AgentConfig;
  private conversationHistory: AIMessage[] = [];
  private systemPrompt: string;

  constructor(config: AgentConfig) {
    super();
    this.config = {
      model: 'gpt-4',
      systemPrompt: 'You are NEXUS, an AI assistant that helps with WhatsApp, Telegram, GitHub, and web automation.',
      ...config,
    };
    this.systemPrompt = this.config.systemPrompt || '';
  }

  initialize(): void {
    if (this.config.openaiKey) {
      this.client = new OpenAI({ apiKey: this.config.openaiKey });
    }
  }

  async processMessage(message: Message): Promise<string> {
    const userMessage: AIMessage = {
      role: 'user',
      content: message.content,
      timestamp: new Date(),
    };

    this.conversationHistory.push(userMessage);

    // Intent detection
    const intent = await this.detectIntent(message.content);
    this.emit('intent', intent);

    // Generate response based on intent
    let response: string;

    switch (intent.intent) {
      case 'whatsapp':
        response = await this.handleWhatsAppIntent(intent);
        break;
      case 'telegram':
        response = await this.handleTelegramIntent(intent);
        break;
      case 'github':
        response = await this.handleGitHubIntent(intent);
        break;
      case 'research':
        response = await this.handleResearchIntent(intent);
        break;
      case 'help':
        response = this.getHelpResponse();
        break;
      default:
        response = await this.generateGeneralResponse(message.content);
    }

    const assistantMessage: AIMessage = {
      role: 'assistant',
      content: response,
      timestamp: new Date(),
    };

    this.conversationHistory.push(assistantMessage);
    this.emit('response', response);

    return response;
  }

  async detectIntent(content: string): Promise<IntentResult> {
    const lower = content.toLowerCase();

    // Intent patterns
    if (lower.includes('whatsapp') || lower.includes('wa ') || lower.includes('@wa')) {
      return { intent: 'whatsapp', confidence: 0.9, entities: {} };
    }
    if (lower.includes('telegram') || lower.includes('tg ') || lower.includes('@tg')) {
      return { intent: 'telegram', confidence: 0.9, entities: {} };
    }
    if (lower.includes('github') || lower.includes('pr') || lower.includes('issue') || lower.includes('repo')) {
      return { intent: 'github', confidence: 0.9, entities: {} };
    }
    if (lower.includes('research') || lower.includes('search') || lower.includes('scrape') || lower.includes('web')) {
      return { intent: 'research', confidence: 0.9, entities: {} };
    }
    if (lower.includes('help') || lower.includes('command') || lower.includes('what can you do')) {
      return { intent: 'help', confidence: 0.9, entities: {} };
    }

    return { intent: 'general', confidence: 0.5, entities: {} };
  }

  private async handleWhatsAppIntent(intent: IntentResult): Promise<string> {
    return '🤖 WhatsApp Integration Active\n\nI can help you:\n• Send messages\n• Manage devices\n• Automate replies\n• Broadcast messages\n\nWhat would you like to do?';
  }

  private async handleTelegramIntent(intent: IntentResult): Promise<string> {
    return '📱 Telegram Integration Active\n\nAvailable commands:\n• /devices - List WhatsApp devices\n• /connect - Connect new device\n• /status - System status\n• /stats - View analytics\n\nWhat would you like to do?';
  }

  private async handleGitHubIntent(intent: IntentResult): Promise<string> {
    return '🐙 GitHub Integration Active\n\nI can help you:\n• Review PRs\n• Manage issues\n• Monitor repos\n• Auto-assign tasks\n\nWhat would you like to do?';
  }

  private async handleResearchIntent(intent: IntentResult): Promise<string> {
    return '🔍 Web Research Mode\n\nI can help you:\n• Scrape websites\n• Extract data\n• Research topics\n• Take screenshots\n\nWhat would you like to research?';
  }

  private getHelpResponse(): string {
    return `
🤖 NEXUS Platform - Help

I can help you automate:

📱 WhatsApp
   - Send/receive messages
   - Multi-device support
   - Auto-replies

💬 Telegram
   - Bot commands
   - Admin management
   - Alerts & notifications

🐙 GitHub
   - PR reviews
   - Issue management
   - Repo monitoring

🌐 Web
   - Research & scraping
   - Data extraction
   - Screenshot capture

Just tell me what you need!
`;
  }

  private async generateGeneralResponse(content: string): Promise<string> {
    if (!this.client) {
      return `I'm here to help with WhatsApp, Telegram, GitHub, and Web automation!\n\nTry saying:\n• "Help with WhatsApp"\n• "Show GitHub PRs"\n• "Research this topic"`;
    }

    const messages = [
      { role: 'system' as const, content: this.systemPrompt },
      ...this.conversationHistory.slice(-10),
    ];

    const completion = await this.client.chat.completions.create({
      model: this.config.model || 'gpt-4',
      messages,
      max_tokens: 500,
    });

    return completion.choices[0]?.message?.content || 'I need more information to help you.';
  }

  clearHistory(): void {
    this.conversationHistory = [];
  }

  getHistory(): AIMessage[] {
    return [...this.conversationHistory];
  }
}

export default NEXUSAgent;
