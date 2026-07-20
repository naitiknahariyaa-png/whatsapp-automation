// NEXUS Platform - Main Entry Point v3.0
import { config } from 'dotenv';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { WhatsAppConnector } from './connectors/whatsapp.js';
import { TelegramConnector } from './connectors/telegram.js';
import { GitHubConnector } from './connectors/github.js';
import { WebConnector } from './connectors/web.js';
import type { Message } from './types/index.js';

// Load environment variables
config();

interface NEXUSConfig {
  port: number;
  telegramToken?: string;
  githubToken?: string;
  openaiKey?: string;
}

class NEXUSPlatform {
  private app: express.Application;
  private whatsapp: WhatsAppConnector | null = null;
  private telegram: TelegramConnector | null = null;
  private github: GitHubConnector | null = null;
  private web: WebConnector | null = null;
  private config: NEXUSConfig;
  private isInitialized = false;

  constructor() {
    this.config = {
      port: parseInt(process.env.PORT || '3000'),
      telegramToken: process.env.TELEGRAM_BOT_TOKEN,
      githubToken: process.env.GITHUB_TOKEN,
      openaiKey: process.env.OPENAI_API_KEY,
    };

    this.app = express();
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
              console.log('QR Code generated');
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

    // Chat endpoint (simple AI response)
    this.app.post('/api/chat', async (req, res) => {
      try {
        const { message } = req.body;
        
        // Simple response based on message content
        let response = 'Hello! I am NEXUS. Type "help" for commands.';
        
        if (message.toLowerCase().includes('help')) {
          response = `NEXUS Commands:
- /start - Start bot
- /status - Check status
- /connect - Connect WhatsApp
- /github - GitHub actions
- /help - Show this help`;
        } else if (message.toLowerCase().includes('status')) {
          response = `NEXUS Status:
WhatsApp: ${this.whatsapp ? 'Connected' : 'Disconnected'}
Telegram: ${this.telegram ? 'Active' : 'Inactive'}
GitHub: ${this.github ? 'Monitoring' : 'Not configured'}`;
        }
        
        res.json({ success: true, response });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });
  }

  async initialize(): Promise<void> {
    console.log('🚀 Initializing NEXUS Platform v3.0...');

    // Initialize WhatsApp
    if (process.env.WHATSAPP_SESSION_PATH) {
      console.log('📱 Setting up WhatsApp...');
    }

    // Initialize Telegram if token provided
    if (this.config.telegramToken) {
      console.log('💬 Setting up Telegram...');
      this.telegram = new TelegramConnector({
        botToken: this.config.telegramToken,
        onMessage: (msg) => {
          console.log('Telegram message:', msg.content);
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

    this.isInitialized = true;
    console.log('🎉 NEXUS Platform initialized successfully!');
  }

  async start(): Promise<void> {
    await this.initialize();

    this.app.listen(this.config.port, () => {
      console.log(`
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🤖 NEXUS Platform v3.0                                          ║
║   Ultimate Unified AI Automation Platform                          ║
║                                                                   ║
║   🌐 Server running at http://localhost:${this.config.port}                        ║
║   📊 Dashboard: http://localhost:${this.config.port}/dashboard                      ║
║   📚 API Docs: http://localhost:${this.config.port}/api/status                      ║
║                                                                   ║
║   ══════════════════════════════════════════════════════════════════   ║
║   CONNECTORS:                                                      ║
║   📱 WhatsApp:  ${this.whatsapp ? '✅ Connected' : '⚪️ Disconnected'}                                          ║
║   💬 Telegram:  ${this.telegram ? '✅ Active' : '⚪️ Inactive'}                                          ║
║   🐙 GitHub:    ${this.github ? '✅ Monitoring' : '⚪️ Not configured'}                                      ║
║   🌐 Web:      ✅ Ready                                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
      `);
    });
  }

  async stop(): Promise<void> {
    console.log('🛑 Stopping NEXUS Platform...');
    if (this.whatsapp) await this.whatsapp.disconnect();
    if (this.telegram) this.telegram.stop();
    if (this.web) await this.web.close();
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
