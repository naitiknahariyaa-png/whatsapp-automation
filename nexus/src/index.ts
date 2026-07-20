// NEXUS Platform - Main Entry Point v3.0
import { config } from 'dotenv';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { NEXUSAgent } from './agents/core.js';
import { WhatsAppConnector, TelegramConnector, GitHubConnector, WebConnector } from './connectors/index.js';
import type { Message, NEXUSConfig } from './types/index.js';

// Load environment variables
config();

class NEXUSPlatform {
  private app: express.Application;
  private agent: NEXUSAgent;
  private whatsapp: WhatsAppConnector | null = null;
  private telegram: TelegramConnector | null = null;
  private github: GitHubConnector | null = null;
  private web: WebConnector | null = null;
  private config: NEXUSConfig;

  constructor() {
    this.config = {
      port: parseInt(process.env.PORT || '3000'),
      databaseUrl: process.env.DATABASE_URL || '',
      redisUrl: process.env.REDIS_URL || '',
      telegramToken: process.env.TELEGRAM_BOT_TOKEN,
      githubToken: process.env.GITHUB_TOKEN,
      openaiKey: process.env.OPENAI_API_KEY,
    };

    this.app = express();
    this.agent = new NEXUSAgent({
      openaiKey: this.config.openaiKey,
      systemPrompt: 'You are NEXUS, a unified AI automation platform connecting WhatsApp, Telegram, GitHub, and Web.',
    });

    this.setupMiddleware();
    this.setupRoutes();
  }

  private setupMiddleware(): void {
    this.app.use(helmet());
    this.app.use(cors());
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'ok',
        platform: 'NEXUS',
        version: '3.0.0',
        uptime: process.uptime(),
      });
    });

    // Status endpoint
    this.app.get('/api/status', (req, res) => {
      res.json({
        platform: 'NEXUS Platform',
        version: '3.0.0',
        whatsapp: this.whatsapp ? 'connected' : 'disconnected',
        telegram: this.telegram ? 'active' : 'inactive',
        github: this.github ? 'monitoring' : 'not configured',
        web: this.web ? 'ready' : 'not initialized',
      });
    });

    // WhatsApp endpoints
    this.app.post('/api/whatsapp/connect', async (req, res) => {
      try {
        if (!this.whatsapp) {
          this.whatsapp = new WhatsAppConnector({
            sessionPath: process.env.WHATSAPP_SESSION_PATH || './sessions/whatsapp',
            onQR: (qr) => {
              console.log('QR Code:', qr);
              this.app.get('/api/whatsapp/qr', (req, res) => res.json({ qr }));
            },
            onConnected: (device) => {
              console.log('WhatsApp connected:', device);
            },
          });
          await this.whatsapp.connect();
        }
        res.json({ success: true, message: 'WhatsApp connecting...' });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.post('/api/whatsapp/send', async (req, res) => {
      try {
        const { jid, message } = req.body;
        if (!this.whatsapp) throw new Error('WhatsApp not connected');
        await this.whatsapp.sendMessage(jid, message);
        res.json({ success: true });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    // GitHub endpoints
    this.app.get('/api/github/prs', async (req, res) => {
      try {
        const { owner, repo } = req.query;
        if (!this.github) throw new Error('GitHub not configured');
        const prs = await this.github.getPullRequests(String(owner), String(repo));
        res.json({ success: true, prs });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.get('/api/github/issues', async (req, res) => {
      try {
        const { owner, repo } = req.query;
        if (!this.github) throw new Error('GitHub not configured');
        const issues = await this.github.getIssues(String(owner), String(repo));
        res.json({ success: true, issues });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    // Web scraping endpoint
    this.app.post('/api/web/scrape', async (req, res) => {
      try {
        const { url, selectors } = req.body;
        if (!this.web) {
          this.web = new WebConnector();
          await this.web.initialize();
        }
        const content = await this.web.extractText(url, selectors || ['body']);
        res.json({ success: true, content });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    // AI Agent endpoint
    this.app.post('/api/chat', async (req, res) => {
      try {
        const { message } = req.body;
        const msg: Message = {
          id: Date.now().toString(),
          channel: 'web',
          from: 'web-user',
          to: 'nexus',
          content: message,
          timestamp: new Date(),
        };
        const response = await this.agent.processMessage(msg);
        res.json({ success: true, response });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    // Message webhook
    this.app.post('/api/webhook', (req, res) => {
      const message = req.body as Message;
      console.log('Webhook received:', message);
      
      // Process message through AI
      this.agent.processMessage(message).then((response) => {
        console.log('AI Response:', response);
      });

      res.json({ received: true });
    });
  }

  async initialize(): Promise<void> {
    console.log('🚀 Initializing NEXUS Platform v3.0...');

    // Initialize AI Agent
    this.agent.initialize();
    console.log('✅ AI Agent initialized');

    // Initialize WhatsApp if configured
    if (process.env.WHATSAPP_SESSION_PATH) {
      console.log('📱 Setting up WhatsApp...');
    }

    // Initialize Telegram if token provided
    if (this.config.telegramToken) {
      console.log('💬 Setting up Telegram...');
      this.telegram = new TelegramConnector({
        botToken: this.config.telegramToken,
        onMessage: (msg) => {
          console.log('Telegram message:', msg);
        },
      });
      await this.telegram.start();
      console.log('✅ Telegram bot started');
    }

    // Initialize GitHub if token provided
    if (this.config.githubToken) {
      console.log('🐙 Setting up GitHub...');
      this.github = new GitHubConnector({
        token: this.config.githubToken,
      });
      console.log('✅ GitHub connector ready');
    }

    // Initialize Web connector
    console.log('🌐 Initializing Web connector...');
    this.web = new WebConnector();
    await this.web.initialize();
    console.log('✅ Web connector ready');

    console.log('🎉 NEXUS Platform initialized successfully!');
  }

  async start(): Promise<void> {
    await this.initialize();

    this.app.listen(this.config.port, () => {
      console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🤖 NEXUS Platform v3.0                                  ║
║   Unified AI Automation Platform                         ║
║                                                           ║
║   🌐 Server running at http://localhost:${this.config.port}              ║
║   📊 Dashboard: http://localhost:${this.config.port}/dashboard          ║
║   📚 API Docs: http://localhost:${this.config.port}/api/status          ║
║                                                           ║
║   Connectors:                                             ║
║   • WhatsApp: ${this.whatsapp ? '✅' : '⚪️'}                                       ║
║   • Telegram: ${this.telegram ? '✅' : '⚪️'}                                       ║
║   • GitHub:   ${this.github ? '✅' : '⚪️'}                                       ║
║   • Web:      ✅                                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
      `);
    });
  }

  async stop(): Promise<void> {
    console.log('🛑 Stopping NEXUS Platform...');
    
    if (this.whatsapp) {
      await this.whatsapp.disconnect();
    }
    
    if (this.telegram) {
      this.telegram.stop();
    }
    
    if (this.web) {
      await this.web.close();
    }
    
    console.log('✅ NEXUS Platform stopped');
  }
}

// Start the platform
const nexus = new NEXUSPlatform();
nexus.start().catch(console.error);

// Handle graceful shutdown
process.on('SIGINT', async () => {
  await nexus.stop();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await nexus.stop();
  process.exit(0);
});

export default NEXUSPlatform;
