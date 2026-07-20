// NEXUS Platform - Web Connector (Playwright)
import { chromium, Browser, Page } from 'playwright';
import { EventEmitter } from 'events';
import type { Message } from '../types/index.js';

interface WebConfig {
  headless?: boolean;
  onError?: (error: Error) => void;
}

interface SearchResult {
  url: string;
  title: string;
  snippet: string;
  content?: string;
}

export class WebConnector extends EventEmitter {
  private browser: Browser | null = null;
  private config: WebConfig;
  private isInitialized = false;

  constructor(config: WebConfig = {}) {
    super();
    this.config = {
      headless: true,
      ...config,
    };
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      this.browser = await chromium.launch({
        headless: this.config.headless,
      });
      this.isInitialized = true;
      console.log('Web connector initialized');
    } catch (error) {
      this.config.onError?.(error as Error);
      throw error;
    }
  }

  async scrape(url: string, selector?: string): Promise<string> {
    if (!this.browser) await this.initialize();

    const page = await this.browser!.newPage();
    try {
      await page.goto(url, { waitUntil: 'networkidle' });
      
      if (selector) {
        const element = await page.$(selector);
        return element ? await element.textContent() || '' : '';
      }

      return await page.content();
    } finally {
      await page.close();
    }
  }

  async extractText(url: string, selectors: string[]): Promise<Record<string, string>> {
    if (!this.browser) await this.initialize();

    const page = await this.browser!.newPage();
    try {
      await page.goto(url, { waitUntil: 'networkidle' });

      const result: Record<string, string> = {};
      for (const selector of selectors) {
        const element = await page.$(selector);
        result[selector] = element ? await element.textContent() || '' : '';
      }

      return result;
    } finally {
      await page.close();
    }
  }

  async takeScreenshot(url: string, path: string): Promise<void> {
    if (!this.browser) await this.initialize();

    const page = await this.browser!.newPage();
    try {
      await page.goto(url, { waitUntil: 'networkidle' });
      await page.screenshot({ path, fullPage: true });
    } finally {
      await page.close();
    }
  }

  async fillForm(url: string, formSelector: string, data: Record<string, string>): Promise<void> {
    if (!this.browser) await this.initialize();

    const page = await this.browser!.newPage();
    try {
      await page.goto(url);
      await page.waitForSelector(formSelector);

      for (const [field, value] of Object.entries(data)) {
        await page.fill(field, value);
      }

      await page.click(`${formSelector} button[type="submit"]`);
      await page.waitForNavigation();
    } finally {
      await page.close();
    }
  }

  async research(query: string, maxResults = 5): Promise<SearchResult[]> {
    // For actual search, you'd integrate with Tavily, SerpAPI, etc.
    // This is a simplified version
    console.log(`Researching: ${query}`);
    
    return [
      {
        url: 'https://example.com',
        title: `Results for: ${query}`,
        snippet: `Search results for "${query}" would appear here.`,
      },
    ];
  }

  async clickAndWait(url: string, clickSelector: string, waitForSelector?: string): Promise<string> {
    if (!this.browser) await this.initialize();

    const page = await this.browser!.newPage();
    try {
      await page.goto(url);
      await page.click(clickSelector);
      
      if (waitForSelector) {
        await page.waitForSelector(waitForSelector);
      }

      return await page.content();
    } finally {
      await page.close();
    }
  }

  async getLinks(url: string, filter?: RegExp): Promise<string[]> {
    if (!this.browser) await this.initialize();

    const page = await this.browser!.newPage();
    try {
      await page.goto(url, { waitUntil: 'networkidle' });
      
      const links = await page.$$eval('a', (anchors) => 
        anchors.map((a) => a.href).filter((href) => href.startsWith('http'))
      );

      if (filter) {
        return links.filter((link) => filter.test(link));
      }

      return links;
    } finally {
      await page.close();
    }
  }

  async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      this.isInitialized = false;
    }
  }
}

export default WebConnector;
