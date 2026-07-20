// NEXUS Platform - Document Parser (PDF & Documents)
import { EventEmitter } from 'events';
import { readFile, writeFile } from 'fs/promises';
import { join } from 'path';
import axios from 'axios';

interface DocumentConfig {
  tempDir?: string;
  openaiKey?: string;
}

interface ParsedDocument {
  id: string;
  filename: string;
  content: string;
  pages?: number;
  metadata: {
    author?: string;
    createdDate?: Date;
    modifiedDate?: Date;
    pageCount?: number;
    fileSize?: number;
  };
  extractedData?: Record<string, any>;
}

interface FormField {
  name: string;
  type: 'text' | 'number' | 'date' | 'email' | 'phone' | 'select';
  value?: string;
  confidence?: number;
  page?: number;
}

interface IntakeForm {
  clientName?: string;
  email?: string;
  phone?: string;
  address?: string;
  dateOfBirth?: string;
  caseType?: string;
  description?: string;
  documents?: string[];
}

export class DocumentParser extends EventEmitter {
  private config: DocumentConfig;
  private tempDir: string;

  constructor(config: DocumentConfig = {}) {
    super();
    this.config = config;
    this.tempDir = config.tempDir || '/tmp/nexus-docs';
  }

  async initialize(): Promise<void> {
    console.log('✅ Document Parser initialized');
  }

  // Parse PDF file
  async parsePDF(filePath: string): Promise<ParsedDocument> {
    const content = await this.extractTextFromPDF(filePath);
    const id = `doc-${Date.now()}`;

    const doc: ParsedDocument = {
      id,
      filename: filePath.split('/').pop() || filePath,
      content,
      metadata: {
        fileSize: 0,
      },
    };

    console.log(`📄 PDF parsed: ${doc.filename}`);
    this.emit('document_parsed', doc);
    return doc;
  }

  // Extract text from PDF
  private async extractTextFromPDF(filePath: string): Promise<string> {
    try {
      // For a real implementation, you'd use pdf-parse or similar
      // This is a simplified version
      const content = await readFile(filePath, 'utf-8').catch(() => '');
      // In production, use pdf-parse: const pdfParse = require('pdf-parse');
      return content.slice(0, 10000); // Placeholder
    } catch (error) {
      console.error('PDF parse error:', error);
      return '';
    }
  }

  // Parse document from URL
  async parseFromURL(url: string): Promise<ParsedDocument> {
    try {
      const response = await axios.get(url, { responseType: 'arraybuffer' });
      const id = `doc-${Date.now()}`;
      const content = response.data.toString('utf-8').slice(0, 10000);

      return {
        id,
        filename: url.split('/').pop() || 'document',
        content,
        metadata: {
          fileSize: response.data.length,
        },
      };
    } catch (error) {
      console.error('URL fetch error:', error);
      throw new Error('Failed to fetch document');
    }
  }

  // Extract form fields from document
  async extractFormFields(document: ParsedDocument): Promise<FormField[]> {
    const fields: FormField[] = [];
    
    // Common patterns for form extraction
    const patterns = {
      email: /[\w.-]+@[\w.-]+\.\w+/gi,
      phone: /(\+?91[\s-]?)?[\d]{10}/g,
      date: /\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}/g,
    };

    // Extract emails
    const emails = document.content.match(patterns.email);
    if (emails) {
      fields.push({
        name: 'email',
        type: 'email',
        value: emails[0],
        confidence: 0.9,
      });
    }

    // Extract phone numbers
    const phones = document.content.match(patterns.phone);
    if (phones) {
      fields.push({
        name: 'phone',
        type: 'phone',
        value: phones[0],
        confidence: 0.85,
      });
    }

    // Extract dates
    const dates = document.content.match(patterns.date);
    if (dates) {
      fields.push({
        name: 'date',
        type: 'date',
        value: dates[0],
        confidence: 0.8,
      });
    }

    console.log(`📋 Extracted ${fields.length} form fields`);
    return fields;
  }

  // Parse intake form for CA/Lawyer
  async parseIntakeForm(document: ParsedDocument): Promise<IntakeForm> {
    const content = document.content.toLowerCase();
    const intake: IntakeForm = {};

    // Extract name (usually first capitalized words)
    const namePattern = /(?:name|client|applicant)[\s:]+([A-Z][a-z]+\s+[A-Z][a-z]+)/i;
    const nameMatch = document.content.match(namePattern);
    if (nameMatch) intake.clientName = nameMatch[1];

    // Extract email
    const emailPattern = /[\w.-]+@[\w.-]+\.\w+/;
    const emailMatch = document.content.match(emailPattern);
    if (emailMatch) intake.email = emailMatch[0];

    // Extract phone
    const phonePattern = /(\+?91[\s-]?)?[\d]{10}/;
    const phoneMatch = document.content.match(phonePattern);
    if (phoneMatch) intake.phone = phoneMatch[0];

    // Extract case type keywords
    const caseTypes = ['tax', 'divorce', 'property', 'criminal', 'corporate', 'civil', 'immigration', 'patent'];
    for (const type of caseTypes) {
      if (content.includes(type)) {
        intake.caseType = type;
        break;
      }
    }

    document.extractedData = intake;
    console.log('📋 Intake form parsed:', intake);
    return intake;
  }

  // Classify document type
  async classifyDocument(document: ParsedDocument): Promise<{
    type: 'invoice' | 'contract' | 'id' | 'receipt' | 'letter' | 'form' | 'unknown';
    confidence: number;
  }> {
    const content = document.content.toLowerCase();
    const scores: Record<string, number> = {
      invoice: 0,
      contract: 0,
      id: 0,
      receipt: 0,
      letter: 0,
      form: 0,
    };

    // Scoring patterns
    if (content.includes('invoice') || content.includes('bill to')) scores.invoice += 0.8;
    if (content.includes('agreement') || content.includes('whereas') || content.includes('hereby')) scores.contract += 0.9;
    if (content.includes('driver') || content.includes('license') || content.includes('passport')) scores.id += 0.85;
    if (content.includes('receipt') || content.includes('paid') || content.includes('total')) scores.receipt += 0.75;
    if (content.includes('dear') || content.includes('sincerely') || content.includes('regards')) scores.letter += 0.7;
    if (content.includes('form') || content.includes('please fill') || content.includes('signature')) scores.form += 0.8;

    let maxType = 'unknown';
    let maxScore = 0;
    for (const [type, score] of Object.entries(scores)) {
      if (score > maxScore) {
        maxScore = score;
        maxType = type;
      }
    }

    return {
      type: maxType as any,
      confidence: maxScore,
    };
  }

  // Summarize document
  async summarizeDocument(document: ParsedDocument, maxLength = 500): Promise<string> {
    // Simple summarization - take first and last paragraphs
    const paragraphs = document.content.split('\n\n').filter((p) => p.trim());
    
    if (paragraphs.length === 0) return '';
    if (paragraphs.length === 1) return paragraphs[0].slice(0, maxLength);

    const summary = paragraphs[0] + '\n\n...' + (paragraphs.length > 2 ? '\n\n' + paragraphs[paragraphs.length - 1] : '');
    return summary.slice(0, maxLength) + (summary.length > maxLength ? '...' : '');
  }

  // Extract key information using AI
  async extractWithAI(document: ParsedDocument, prompt: string): Promise<string> {
    // This would integrate with OpenAI for smart extraction
    // For now, return a placeholder
    console.log(`🤖 AI extraction with prompt: ${prompt}`);
    return `[AI extraction would process: "${prompt}" on document ${document.filename}]`;
  }

  // Save parsed document
  async saveDocument(document: ParsedDocument): Promise<string> {
    const filename = `${document.id}.json`;
    const filepath = join(this.tempDir, filename);
    await writeFile(filepath, JSON.stringify(document, null, 2));
    console.log(`💾 Document saved: ${filepath}`);
    return filepath;
  }

  // Batch process documents
  async batchProcess(filePaths: string[]): Promise<ParsedDocument[]> {
    const results: ParsedDocument[] = [];
    for (const path of filePaths) {
      try {
        const doc = await this.parsePDF(path);
        results.push(doc);
      } catch (error) {
        console.error(`Failed to process ${path}:`, error);
      }
    }
    console.log(`📚 Batch processed ${results.length}/${filePaths.length} documents`);
    return results;
  }
}

export default DocumentParser;
