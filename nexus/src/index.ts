// NEXUS Platform - Main Entry Point v3.0 - Ultimate Unified AI Automation Platform
import { config } from 'dotenv';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { NEXUSAgent } from './agents/core.js';
import { NEXUSLLMAgent } from './agents/langchain.js';
import { WhatsAppConnector, TelegramConnector, GitHubConnector, WebConnector } from './connectors/index.js';
import { WhatsAppMultiConnector } from './connectors/whatsapp-multi.js';
import { VectorStore } from './core/vector-store.js';
import { JobQueue } from './core/job-queue.js';
import { CalendarConnector } from './core/calendar.js';
import { CRMConnector } from './core/crm.js';
import { DocumentParser } from './core/document-parser.js';
import type { Message, NEXUSConfig } from './types/index.js';

// Load environment variables
config();

class NEXUSPlatform {
  private app: express.Application;
  private agent: NEXUSAgent;
  private llmAgent: NEXUSLLMAgent;
  private whatsapp: WhatsAppConnector | null = null;
  private whatsappMulti: WhatsAppMultiConnector | null = null;
  private telegram: TelegramConnector | null = null;
  private github: GitHubConnector | null = null;
  private web: WebConnector | null = null;
  private vectorStore: VectorStore | null = null;
  private jobQueue: JobQueue | null = null;
  private calendar: CalendarConnector | null = null;
  private crm: CRMConnector | null = null;
  private documentParser: DocumentParser | null = null;
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
    
    // Initialize basic AI Agent
    this.agent = new NEXUSAgent({
      openaiKey: this.config.openaiKey,
      systemPrompt: 'You are NEXUS, a unified AI automation platform.',
    });

    // Initialize LangChain Agent
    this.llmAgent = new NEXUSLLMAgent({
      openaiKey: this.config.openaiKey,
      model: 'gpt-4-turbo',
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

    // ======== VECTOR STORE (Qdrant/Chroma) ========
    this.app.post('/api/vector/add', async (req, res) => {
      try {
        const { id, content, metadata } = req.body;
        if (!this.vectorStore) this.vectorStore = new VectorStore({
          provider: 'chroma',
          openaiKey: this.config.openaiKey,
        });
        await this.vectorStore.addDocument({ id, content, metadata });
        res.json({ success: true });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.get('/api/vector/search', async (req, res) => {
      try {
        const { query, k } = req.query;
        if (!this.vectorStore) throw new Error('Vector store not initialized');
        const results = await this.vectorStore.search(String(query), Number(k) || 5);
        res.json({ success: true, results });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    // ======== JOB QUEUE (BullMQ) ========
    this.app.post('/api/queue/add', async (req, res) => {
      try {
        const { queue, job } = req.body;
        if (!this.jobQueue) {
          this.jobQueue = new JobQueue({ redisUrl: process.env.REDIS_URL });
          await this.jobQueue.initialize();
        }
        const jobId = await this.jobQueue.addJob(queue, job);
        res.json({ success: true, jobId });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.get('/api/queue/stats', async (req, res) => {
      try {
        const { queue } = req.query;
        if (!this.jobQueue) throw new Error('Job queue not initialized');
        const stats = await this.jobQueue.getQueueStats(String(queue));
        res.json({ success: true, stats });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    // ======== CALENDAR (Cal.com) ========
    this.app.post('/api/calendar/booking', async (req, res) => {
      try {
        const booking = req.body;
        if (!this.calendar) {
          this.calendar = new CalendarConnector({ apiKey: process.env.CAL_API_KEY });
          this.calendar.initialize();
        }
        const result = await this.calendar.createBooking(booking);
        res.json(result);
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.get('/api/calendar/events', async (req, res) => {
      try {
        const { limit } = req.query;
        if (!this.calendar) throw new Error('Calendar not initialized');
        const events = await this.calendar.getUpcomingEvents(Number(limit) || 10);
        res.json({ success: true, events });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    // ======== CRM (Twenty) ========
    this.app.post('/api/crm/contact', async (req, res) => {
      try {
        const contact = req.body;
        if (!this.crm) {
          this.crm = new CRMConnector({ apiKey: process.env.TWENTY_API_KEY });
          this.crm.initialize();
        }
        const newContact = await this.crm.createContact(contact);
        res.json({ success: true, contact: newContact });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.get('/api/crm/contacts', async (req, res) => {
      try {
        const { search } = req.query;
        if (!this.crm) throw new Error('CRM not initialized');
        const contacts = search
          ? await this.crm.searchContacts(String(search))
          : await this.crm.getAllContacts();
        res.json({ success: true, contacts });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.post('/api/crm/deal', async (req, res) => {
      try {
        const deal = req.body;
        if (!this.crm) throw new Error('CRM not initialized');
        const newDeal = await this.crm.createDeal(deal);
        res.json({ success: true, deal: newDeal });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.get('/api/crm/stats', async (req, res) => {
      try {
        if (!this.crm) throw new Error('CRM not initialized');
        const stats = await this.crm.getCRMStats();
        res.json({ success: true, stats });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    // ======== DOCUMENT PARSER ========
    this.app.post('/api/document/parse', async (req, res) => {
      try {
        const { url, filePath } = req.body;
        if (!this.documentParser) {
          this.documentParser = new DocumentParser({ openaiKey: this.config.openaiKey });
          await this.documentParser.initialize();
        }
        const doc = url
          ? await this.documentParser.parseFromURL(url)
          : await this.documentParser.parsePDF(filePath);
        res.json({ success: true, document: doc });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.post('/api/document/intake-form', async (req, res) => {
      try {
        const { url, filePath } = req.body;
        if (!this.documentParser) {
          this.documentParser = new DocumentParser();
          await this.documentParser.initialize();
        }
        const doc = url
          ? await this.documentParser.parseFromURL(url)
          : await this.documentParser.parsePDF(filePath);
        const intake = await this.documentParser.parseIntakeForm(doc);
        res.json({ success: true, intake });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    // ======== LANGCHAIN AI AGENT ========
    this.app.post('/api/ai/chat', async (req, res) => {
      try {
        const { message } = req.body;
        const msg: Message = {
          id: Date.now().toString(),
          channel: 'web',
          from: 'web-user',
          to: 'nexus-ai',
          content: message,
          timestamp: new Date(),
        };
        const response = await this.llmAgent.processMessage(msg);
        res.json({ success: true, response });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.post('/api/ai/memory/add', async (req, res) => {
      try {
        const { text, metadata } = req.body;
        await this.llmAgent.addToMemory(text, metadata);
        res.json({ success: true });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    this.app.get('/api/ai/memory/search', async (req, res) => {
      try {
        const { query, k } = req.query;
        const results = await this.llmAgent.searchMemory(String(query), Number(k) || 5);
        res.json({ success: true, results });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });

    // ======== WHATSAPP MULTI ========
    this.app.post('/api/whatsapp/multi/connect', async (req, res) => {
      try {
        const { library } = req.body;
        this.whatsappMulti = new WhatsAppMultiConnector({
          library: library || 'baileys',
          sessionPath: process.env.WHATSAPP_SESSION_PATH,
          onQR: (qr) => console.log('QR:', qr),
        });
        await this.whatsappMulti.connect();
        res.json({ success: true, message: 'WhatsApp connecting...', library });
      } catch (error) {
        res.status(500).json({ success: false, error: String(error) });
      }
    });
  }

  async initialize(): Promise<void> {
    console.log('🚀 Initializing NEXUS Platform v3.0...');
    console.log('   Ultimate Unified AI Automation Platform\n');

    // Initialize AI Agents
    this.agent.initialize();
    console.log('✅ AI Agent (Basic) initialized');
    
    this.llmAgent.initialize();
    console.log('✅ AI Agent (LangChain) initialized');

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

    // Initialize Vector Store (Qdrant/Chroma)
    console.log('🔮 Initializing Vector Store...');
    this.vectorStore = new VectorStore({
      provider: process.env.VECTOR_DB || 'chroma',
      url: process.env.QDRANT_URL,
      openaiKey: this.config.openaiKey,
    });
    await this.vectorStore.initialize();
    console.log('✅ Vector Store ready');

    // Initialize Job Queue (BullMQ)
    if (process.env.REDIS_URL) {
      console.log('⚡ Initializing Job Queue...');
      this.jobQueue = new JobQueue({ redisUrl: process.env.REDIS_URL });
      await this.jobQueue.initialize();
      console.log('✅ Job Queue ready');
    }

    // Initialize Calendar (Cal.com)
    console.log('📅 Initializing Calendar...');
    this.calendar = new CalendarConnector({ apiKey: process.env.CAL_API_KEY });
    this.calendar.initialize();
    console.log('✅ Calendar ready');

    // Initialize CRM (Twenty)
    console.log('👥 Initializing CRM...');
    this.crm = new CRMConnector({ apiKey: process.env.TWENTY_API_KEY });
    this.crm.initialize();
    console.log('✅ CRM ready');

    // Initialize Document Parser
    console.log('📄 Initializing Document Parser...');
    this.documentParser = new DocumentParser({ openaiKey: this.config.openaiKey });
    await this.documentParser.initialize();
    console.log('✅ Document Parser ready');

    console.log('\n🎉 NEXUS Platform initialized successfully!');
  }

  async start(): Promise<void> {
    await this.initialize();

    this.app.listen(this.config.port, () => {
      console.log(`
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   🤖 NEXUS Platform v3.0 - Ultimate Unified AI Automation           ║
║   ══════════════════════════════════════════════════════════════════   ║
║                                                                       ║
║   🌐 Server:     http://localhost:${this.config.port}                              ║
║   📊 Dashboard: http://localhost:${this.config.port}/dashboard                   ║
║   📚 API:       http://localhost:${this.config.port}/api/status                   ║
║                                                                       ║
║   ══════════════════════════════════════════════════════════════════   ║
║   CONNECTORS                                                       ║
║   ══════════════════════════════════════════════════════════════════   ║
║   📱 WhatsApp    Baileys / wweb.js / open-wa                       ║
║   💬 Telegram   Telegraf bot framework                              ║
║   🐙 GitHub     Octokit - PRs, Issues, Repos                       ║
║   🌐 Web        Playwright - Scraping & Research                   ║
║                                                                       ║
║   ══════════════════════════════════════════════════════════════════   ║
║   AI & DATA                                                       ║
║   ══════════════════════════════════════════════════════════════════   ║
║   🤖 AI Agent    LangChain + GPT-4 Turbo                           ║
║   🔮 Vector DB   Qdrant / Chroma - Semantic Search                 ║
║   ⚡ Job Queue   BullMQ - Background Tasks                          ║
║   📄 Documents   PDF Parsing & Intake Forms                        ║
║                                                                       ║
║   ══════════════════════════════════════════════════════════════════   ║
║   BUSINESS                                                        ║
║   ══════════════════════════════════════════════════════════════════   ║
║   📅 Calendar     Cal.com - Bookings & Appointments               ║
║   👥 CRM          Twenty - Contacts, Deals, Tasks                  ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
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
