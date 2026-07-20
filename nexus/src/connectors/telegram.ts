// NEXUS Platform - Telegram Connector
import { Telegraf, Context, Markup, Composer } from 'telegraf';
import { EventEmitter } from 'events';
import type { Message, TelegramChat } from '../types/index.js';

interface TelegramConfig {
  botToken: string;
  onMessage?: (msg: Message) => void;
  onCommand?: (command: string, ctx: Context) => void;
}

export class TelegramConnector extends EventEmitter {
  private bot: Telegraf;
  private config: TelegramConfig;
  private adminChatIds: Set<string> = new Set();
  private chats: Map<string, TelegramChat> = new Map();

  constructor(config: TelegramConfig) {
    super();
    this.config = config;
    this.bot = new Telegraf(config.botToken);
    this.setupHandlers();
  }

  private setupHandlers(): void {
    // Message handler
    this.bot.on('message', (ctx) => {
      const content = (ctx.message as any).text || 
                      (ctx.message as any).caption || 
                      '[Media]';

      const message: Message = {
        id: String(ctx.message.message_id),
        channel: 'telegram',
        from: String(ctx.from?.id),
        to: String(ctx.chat?.id),
        content,
        timestamp: new Date(),
        metadata: {
          username: ctx.from?.username,
          firstName: ctx.from?.first_name,
          chatType: ctx.chat?.type,
        },
      };

      // Track chat
      this.chats.set(String(ctx.chat?.id), {
        id: String(ctx.chat?.id),
        type: ctx.chat?.type as 'private' | 'group' | 'channel',
        title: ctx.chat?.type !== 'private' ? ctx.chat?.title : undefined,
        username: ctx.chat?.username,
      });

      this.config.onMessage?.(message);
      this.emit('message', message);
    });

    // Command handlers
    this.bot.command('start', (ctx) => {
      ctx.reply('🤖 NEXUS Platform Bot\n\nWelcome! Use /help for commands.');
      this.config.onCommand?.('start', ctx);
      this.emit('command', 'start', ctx);
    });

    this.bot.command('help', (ctx) => {
      const helpText = `
📚 NEXUS Commands:

/start - Start the bot
/devices - List WhatsApp devices
/connect - Connect WhatsApp
/disconnect - Disconnect WhatsApp
/status - System status
/stats - Analytics
/github - GitHub actions
/research - Web research
/settings - Configure bot

/admin - Admin panel
      `;
      ctx.reply(helpText);
      this.config.onCommand?.('help', ctx);
      this.emit('command', 'help', ctx);
    });

    this.bot.command('devices', (ctx) => {
      this.emit('command', 'devices', ctx);
      this.config.onCommand?.('devices', ctx);
    });

    this.bot.command('status', (ctx) => {
      ctx.reply('✅ NEXUS is running\n\nWhatsApp: Connected\nTelegram: Active\nGitHub: Monitoring');
      this.config.onCommand?.('status', ctx);
      this.emit('command', 'status', ctx);
    });

    this.bot.command('stats', (ctx) => {
      ctx.reply('📊 Stats:\n\nMessages: 0\nUsers: 0\nAutomations: 0');
      this.config.onCommand?.('stats', ctx);
      this.emit('command', 'stats', ctx);
    });

    this.bot.command('github', (ctx) => {
      ctx.reply('🐙 GitHub Commands:\n\n/github prs - List open PRs\n/github issues - List issues\n/github review - Review PR');
      this.config.onCommand?.('github', ctx);
      this.emit('command', 'github', ctx);
    });

    this.bot.command('research', (ctx) => {
      ctx.reply('🔍 Web Research\n\nSend a topic to research!');
      this.config.onCommand?.('research', ctx);
      this.emit('command', 'research', ctx);
    });

    // Error handler
    this.bot.catch((err, ctx) => {
      console.error('Telegram error:', err);
      ctx.reply('❌ An error occurred');
    });
  }

  async sendMessage(chatId: string, content: string, options?: any): Promise<void> {
    await this.bot.telegram.sendMessage(chatId, content, options);
  }

  async sendPhoto(chatId: string, photoUrl: string, caption?: string): Promise<void> {
    await this.bot.telegram.sendPhoto(chatId, photoUrl, { caption });
  }

  async sendButtons(chatId: string, content: string, buttons: string[][]): Promise<void> {
    const markup = Markup.inlineKeyboard(
      buttons.map(row => row.map(btn => Markup.button.callback(btn, btn)))
    );
    await this.bot.telegram.sendMessage(chatId, content, markup);
  }

  addAdmin(chatId: string): void {
    this.adminChatIds.add(chatId);
  }

  isAdmin(chatId: string): boolean {
    return this.adminChatIds.has(chatId);
  }

  getChats(): TelegramChat[] {
    return Array.from(this.chats.values());
  }

  async start(): Promise<void> {
    await this.bot.launch();
    console.log('Telegram bot started');
  }

  stop(): void {
    this.bot.stop();
  }
}

export default TelegramConnector;
