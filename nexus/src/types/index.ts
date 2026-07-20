// NEXUS Platform - Type Definitions

export interface Message {
  id: string;
  channel: 'whatsapp' | 'telegram' | 'github' | 'web';
  from: string;
  to: string;
  content: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

export interface User {
  id: string;
  name: string;
  phone?: string;
  telegramId?: string;
  githubId?: string;
  createdAt: Date;
}

export interface WhatsAppDevice {
  id: string;
  name: string;
  phone: string;
  status: 'connected' | 'disconnected' | 'connecting';
  lastSeen: Date;
}

export interface TelegramChat {
  id: string;
  type: 'private' | 'group' | 'channel';
  title?: string;
  username?: string;
}

export interface GitHubRepo {
  owner: string;
  repo: string;
  fullName: string;
}

export interface PullRequest {
  number: number;
  title: string;
  state: 'open' | 'closed' | 'merged';
  author: string;
  repository: GitHubRepo;
  createdAt: Date;
  updatedAt: Date;
}

export interface Issue {
  number: number;
  title: string;
  body: string;
  state: 'open' | 'closed';
  author: string;
  labels: string[];
  repository: GitHubRepo;
  createdAt: Date;
}

export interface Automation {
  id: string;
  name: string;
  trigger: 'cron' | 'event' | 'webhook';
  action: string;
  enabled: boolean;
  config: Record<string, unknown>;
}

export interface AIMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface NEXUSConfig {
  port: number;
  databaseUrl: string;
  redisUrl: string;
  telegramToken?: string;
  githubToken?: string;
  openaiKey?: string;
}
