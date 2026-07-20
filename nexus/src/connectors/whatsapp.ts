// NEXUS Platform - WhatsApp Connector (Baileys)
import { 
  makeWASocket, 
  useMultiFileAuthState, 
  DisconnectReason,
  AnyMessageContent,
  baileysVersion 
} from '@adiwajshing/baileys';
import { Boom } from '@hapi/boom';
import { EventEmitter } from 'events';
import { writeFileSync } from 'fs';
import { join } from 'path';
import type { Message, WhatsAppDevice } from '../types/index.js';

interface WhatsAppConfig {
  sessionPath: string;
  onMessage?: (msg: Message) => void;
  onQR?: (qr: string) => void;
  onConnected?: (device: WhatsAppDevice) => void;
  onDisconnected?: (reason: string) => void;
}

export class WhatsAppConnector extends EventEmitter {
  private sock: ReturnType<typeof makeWASocket> | null = null;
  private config: WhatsAppConfig;
  private device: WhatsAppDevice | null = null;

  constructor(config: WhatsAppConfig) {
    super();
    this.config = config;
  }

  async connect(): Promise<void> {
    try {
      const { state, saveCreds更新 } = await useMultiFileAuthState(this.config.sessionPath);

      this.sock = makeWASocket({
        version: baileysVersion,
        auth: state,
        printQRInTerminal: true,
        logger: console,
      });

      this.sock.ev.on('creds.update', saveCreds更新);

      this.sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr && this.config.onQR) {
          this.config.onQR(qr);
          this.emit('qr', qr);
        }

        if (connection === 'open') {
          this.device = {
            id: this.sock!.user?.id || 'unknown',
            name: this.sock!.user?.name || 'Unknown Device',
            phone: this.sock!.user?.id.split(':')[0] || '',
            status: 'connected',
            lastSeen: new Date(),
          };
          this.config.onConnected?.(this.device);
          this.emit('connected', this.device);
        }

        if (connection === 'close') {
          const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
          const reasonStr = DisconnectReason[reason as keyof typeof DisconnectReason] || 'Unknown';
          this.config.onDisconnected?.(reasonStr);
          this.emit('disconnected', reasonStr);
        }
      });

      this.sock.ev.on('messages.upsert', async (m) => {
        for (const msg of m.messages) {
          if (!msg.key.fromMe && msg.message) {
            const message: Message = {
              id: msg.key.id || '',
              channel: 'whatsapp',
              from: msg.key.remoteJid || '',
              to: msg.key.remoteJid || '',
              content: msg.message?.conversation || 
                       msg.message?.extendedTextMessage?.text || 
                       '',
              timestamp: new Date(msg.messageTimestamp ? msg.messageTimestamp * 1000 : Date.now()),
              metadata: {
                pushName: msg.pushName,
                isGroup: msg.key.remoteJid?.includes('@g.us'),
              },
            };
            this.config.onMessage?.(message);
            this.emit('message', message);
          }
        }
      });

    } catch (error) {
      console.error('WhatsApp connection error:', error);
      throw error;
    }
  }

  async sendMessage(jid: string, content: string): Promise<void> {
    if (!this.sock) throw new Error('WhatsApp not connected');

    const message: AnyMessageContent = { text: content };
    await this.sock.sendMessage(jid, message);
  }

  async sendImage(jid: string, imageUrl: string, caption?: string): Promise<void> {
    if (!this.sock) throw new Error('WhatsApp not connected');
    
    // Note: In production, you'd download the image first
    // For now, we'll use URL-based sending
    await this.sock.sendMessage(jid, {
      image: { url: imageUrl },
      caption,
    });
  }

  getDevice(): WhatsAppDevice | null {
    return this.device;
  }

  async disconnect(): Promise<void> {
    if (this.sock) {
      this.sock.end(null);
      this.sock = null;
      this.device = null;
    }
  }
}

export default WhatsAppConnector;
