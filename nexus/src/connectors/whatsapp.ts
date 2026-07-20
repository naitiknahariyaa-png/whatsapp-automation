// NEXUS Platform - WhatsApp Connector (Baileys)
import { EventEmitter } from 'events';
import makeWASocket, { useMultiFileAuthState, DisconnectReason, proto } from '@adiwajshing/baileys';
import { Boom } from '@hapi/boom';
import { existsSync, mkdirSync } from 'fs';
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
  private isConnected = false;
  private qrCode: string | null = null;

  constructor(config: WhatsAppConfig) {
    super();
    this.config = config;
    
    // Ensure session directory exists
    if (!existsSync(config.sessionPath)) {
      mkdirSync(config.sessionPath, { recursive: true });
    }
  }

  async connect(): Promise<void> {
    try {
      console.log('📱 WhatsApp: Connecting...');

      const { state, saveCreds } = await useMultiFileAuthState(this.config.sessionPath);

      this.sock = makeWASocket({
        auth: state,
        printQRInTerminal: true,
        logger: console as any,
      });

      // Save credentials when updated
      this.sock.ev.on('creds.update', saveCreds);

      // Handle connection updates
      this.sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        // QR Code received
        if (qr) {
          this.qrCode = qr;
          console.log('📱 QR Code received! Scan with WhatsApp.');
          this.config.onQR?.(qr);
          this.emit('qr', qr);
        }

        // Connected
        if (connection === 'open') {
          const user = this.sock!.user;
          this.device = {
            id: user?.id || 'unknown',
            name: user?.name || user?.pushName || 'WhatsApp',
            phone: user?.id?.split(':')[0] || '',
            status: 'connected',
            lastSeen: new Date(),
          };
          this.isConnected = true;
          this.qrCode = null;
          this.config.onConnected?.(this.device);
          this.emit('connected', this.device);
          console.log('✅ WhatsApp connected!');
        }

        // Disconnected
        if (connection === 'close') {
          const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
          const reasonStr = DisconnectReason[reason as keyof typeof DisconnectReason] || 'Unknown';
          this.isConnected = false;
          this.config.onDisconnected?.(reasonStr);
          this.emit('disconnected', reasonStr);
          console.log('❌ WhatsApp disconnected:', reasonStr);
        }
      });

      // Handle incoming messages
      this.sock.ev.on('messages.upsert', async (m) => {
        for (const msg of m.messages) {
          if (msg.key.fromMe) continue;
          
          const message = this.parseMessage(msg);
          if (message) {
            this.config.onMessage?.(message);
            this.emit('message', message);
          }
        }
      });

    } catch (error) {
      console.error('❌ WhatsApp connection error:', error);
      throw error;
    }
  }

  private parseMessage(msg: proto.IWebMessageInfo): Message | null {
    if (!msg.message) return null;

    const msgContent = msg.message;
    let content = '';

    if (msgContent.conversation) {
      content = msgContent.conversation;
    } else if (msgContent.extendedTextMessage?.text) {
      content = msgContent.extendedTextMessage.text;
    } else if (msgContent.imageMessage?.caption) {
      content = msgContent.imageMessage.caption;
    } else if (msgContent.videoMessage?.caption) {
      content = msgContent.videoMessage.caption;
    }

    return {
      id: msg.key.id || '',
      channel: 'whatsapp',
      from: msg.key.remoteJid || '',
      to: msg.key.remoteJid || '',
      content,
      timestamp: new Date(msg.messageTimestamp ? msg.messageTimestamp * 1000 : Date.now()),
      metadata: {
        pushName: msg.pushName,
        isGroup: msg.key.remoteJid?.includes('@g.us'),
      },
    };
  }

  async sendMessage(jid: string, content: string): Promise<void> {
    if (!this.sock || !this.isConnected) {
      throw new Error('WhatsApp not connected');
    }

    try {
      await this.sock.sendMessage(jid, { text: content });
      console.log('📤 WhatsApp sent:', content.slice(0, 50));
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  }

  async sendImage(jid: string, imageBuffer: Buffer, caption?: string): Promise<void> {
    if (!this.sock || !this.isConnected) {
      throw new Error('WhatsApp not connected');
    }

    await this.sock.sendMessage(jid, {
      image: imageBuffer,
      caption,
    });
  }

  getDevice(): WhatsAppDevice | null {
    return this.device;
  }

  getQR(): string | null {
    return this.qrCode;
  }

  isActive(): boolean {
    return this.isConnected;
  }

  async disconnect(): Promise<void> {
    if (this.sock) {
      this.sock.end(undefined);
      this.sock = null;
    }
    this.isConnected = false;
    this.device = null;
    this.qrCode = null;
    console.log('📱 WhatsApp disconnected');
    this.emit('disconnected');
  }
}

export default WhatsAppConnector;
