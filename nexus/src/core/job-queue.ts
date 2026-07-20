// NEXUS Platform - Job Queue (BullMQ)
import { Queue, Worker, Job, QueueEvents } from 'bullmq';
import IORedis from 'ioredis';
import { EventEmitter } from 'events';

interface JobConfig {
  redisUrl?: string;
  connection?: any;
}

interface NEXUSJob {
  id?: string;
  name: string;
  data: any;
  options?: {
    priority?: number;
    attempts?: number;
    backoff?: {
      type: 'exponential' | 'fixed';
      delay: number;
    };
    removeOnComplete?: boolean;
    removeOnFail?: boolean;
  };
}

export class JobQueue extends EventEmitter {
  private queues: Map<string, Queue> = new Map();
  private workers: Map<string, Worker> = new Map();
  private redis: IORedis | null = null;
  private config: JobConfig;
  private isInitialized = false;

  constructor(config: JobConfig = {}) {
    super();
    this.config = config;
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    const connection = this.config.redisUrl 
      ? { host: 'localhost', port: 6379 } // BullMQ needs connection object
      : undefined;

    if (this.config.redisUrl) {
      this.redis = new IORedis(this.config.redisUrl, {
        maxRetriesPerRequest: null,
      });
    }

    this.isInitialized = true;
    console.log('✅ Job Queue initialized (BullMQ)');
  }

  async createQueue(name: string): Promise<Queue> {
    if (this.queues.has(name)) {
      return this.queues.get(name)!;
    }

    const queue = new Queue(name, {
      connection: this.redis || { host: 'localhost', port: 6379 },
    });

    // Set up event listeners
    queue.on('error', (error) => {
      console.error(`Queue ${name} error:`, error);
      this.emit('error', { queue: name, error });
    });

    this.queues.set(name, queue);
    console.log(`📬 Queue created: ${name}`);
    return queue;
  }

  async addJob(queueName: string, job: NEXUSJob): Promise<string> {
    let queue = this.queues.get(queueName);
    if (!queue) {
      queue = await this.createQueue(queueName);
    }

    const jobId = await queue.add(job.name, job.data, job.options);
    console.log(`📋 Job added to ${queueName}: ${job.name} (${jobId})`);
    this.emit('job_added', { queue: queueName, jobId, job });

    return jobId as string;
  }

  async addBulkJobs(queueName: string, jobs: NEXUSJob[]): Promise<string[]> {
    let queue = this.queues.get(queueName);
    if (!queue) {
      queue = await this.createQueue(queueName);
    }

    const jobsToAdd = jobs.map((j) => ({
      name: j.name,
      data: j.data,
      opts: j.options,
    }));

    const results = await queue.addBulk(jobsToAdd);
    console.log(`📋 ${results.length} jobs added to ${queueName}`);
    
    return results.map((j) => j.id as string);
  }

  async processJobs<T = any>(
    queueName: string,
    processor: (job: Job<T>) => Promise<any>
  ): Promise<Worker> {
    if (this.workers.has(queueName)) {
      return this.workers.get(queueName)!;
    }

    const worker = new Worker(queueName, processor, {
      connection: this.redis || { host: 'localhost', port: 6379 },
      concurrency: 5,
    });

    worker.on('completed', (job) => {
      console.log(`✅ Job ${job.id} completed in ${queueName}`);
      this.emit('job_completed', { queue: queueName, jobId: job.id });
    });

    worker.on('failed', (job, error) => {
      console.error(`❌ Job ${job?.id} failed in ${queueName}:`, error);
      this.emit('job_failed', { queue: queueName, jobId: job?.id, error });
    });

    worker.on('progress', (job, progress) => {
      this.emit('job_progress', { queue: queueName, jobId: job.id, progress });
    });

    this.workers.set(queueName, worker);
    console.log(`⚙️ Worker started for queue: ${queueName}`);
    return worker;
  }

  async getJob(queueName: string, jobId: string): Promise<Job | undefined> {
    const queue = this.queues.get(queueName);
    if (!queue) return undefined;
    return queue.getJob(jobId);
  }

  async getQueueStats(queueName: string): Promise<{
    waiting: number;
    active: number;
    completed: number;
    failed: number;
    delayed: number;
  }> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      return { waiting: 0, active: 0, completed: 0, failed: 0, delayed: 0 };
    }

    const [waiting, active, completed, failed, delayed] = await Promise.all([
      queue.getWaitingCount(),
      queue.getActiveCount(),
      queue.getCompletedCount(),
      queue.getFailedCount(),
      queue.getDelayedCount(),
    ]);

    return { waiting, active, completed, failed, delayed };
  }

  async pauseQueue(queueName: string): Promise<void> {
    const queue = this.queues.get(queueName);
    if (queue) {
      await queue.pause();
      console.log(`⏸️ Queue paused: ${queueName}`);
    }
  }

  async resumeQueue(queueName: string): Promise<void> {
    const queue = this.queues.get(queueName);
    if (queue) {
      await queue.resume();
      console.log(`▶️ Queue resumed: ${queueName}`);
    }
  }

  async clearQueue(queueName: string): Promise<void> {
    const queue = this.queues.get(queueName);
    if (queue) {
      await queue.drain();
      console.log(`🧹 Queue cleared: ${queueName}`);
    }
  }

  async close(): Promise<void> {
    // Close all workers
    for (const worker of this.workers.values()) {
      await worker.close();
    }
    this.workers.clear();

    // Close all queues
    for (const queue of this.queues.values()) {
      await queue.close();
    }
    this.queues.clear();

    // Close Redis
    if (this.redis) {
      await this.redis.quit();
    }

    console.log('👋 Job Queue shutdown complete');
  }

  // Preset job types
  async scheduleWhatsAppMessage(to: string, message: string, delayMs: number): Promise<string> {
    return this.addJob('whatsapp-messages', {
      name: 'send-message',
      data: { to, message },
      options: {
        attempts: 3,
        backoff: { type: 'exponential', delay: 1000 },
      },
    });
  }

  async scheduleTelegramMessage(chatId: string, message: string, delayMs: number): Promise<string> {
    return this.addJob('telegram-messages', {
      name: 'send-message',
      data: { chatId, message },
      options: {
        attempts: 3,
        backoff: { type: 'exponential', delay: 1000 },
      },
    });
  }

  async scheduleGitHubAction(owner: string, repo: string, action: string): Promise<string> {
    return this.addJob('github-actions', {
      name: action,
      data: { owner, repo, action },
    });
  }

  async scheduleReminder(userId: string, message: string, scheduleTime: Date): Promise<string> {
    const delay = scheduleTime.getTime() - Date.now();
    return this.addJob('reminders', {
      name: 'send-reminder',
      data: { userId, message },
      options: {
        delay: Math.max(0, delay),
        removeOnComplete: true,
      },
    });
  }
}

export default JobQueue;
