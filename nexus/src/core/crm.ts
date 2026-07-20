// NEXUS Platform - CRM (Twenty Integration)
import { EventEmitter } from 'events';
import axios from 'axios';

interface CRMConfig {
  apiKey?: string;
  baseUrl?: string;
}

interface Contact {
  id?: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  position?: string;
  tags?: string[];
  notes?: string;
  source?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

interface Company {
  id?: string;
  name: string;
  domain?: string;
  industry?: string;
  size?: string;
  location?: string;
  contacts?: Contact[];
}

interface Deal {
  id?: string;
  title: string;
  value?: number;
  currency?: string;
  stage: 'lead' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost';
  probability?: number;
  contactId?: string;
  companyId?: string;
  expectedCloseDate?: Date;
  notes?: string;
}

interface Task {
  id?: string;
  title: string;
  description?: string;
  dueDate?: Date;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in_progress' | 'completed';
  contactId?: string;
  assignedTo?: string;
}

interface Note {
  id?: string;
  content: string;
  contactId?: string;
  dealId?: string;
  createdAt?: Date;
  createdBy?: string;
}

export class CRMConnector extends EventEmitter {
  private apiKey: string | null = null;
  private baseUrl: string;
  private config: CRMConfig;
  
  // In-memory storage (can be replaced with Twenty API)
  private contacts: Map<string, Contact> = new Map();
  private companies: Map<string, Company> = new Map();
  private deals: Map<string, Deal> = new Map();
  private tasks: Map<string, Task> = new Map();
  private notes: Map<string, Note> = new Map();

  constructor(config: CRMConfig = {}) {
    super();
    this.config = {
      baseUrl: 'https://api.twenty.com/v1',
      ...config,
    };
    this.baseUrl = this.config.baseUrl || 'https://api.twenty.com/v1';
  }

  initialize(): void {
    this.apiKey = this.config.apiKey || process.env.TWENTY_API_KEY || null;
    if (this.apiKey) {
      console.log('✅ CRM (Twenty) initialized');
    } else {
      console.log('⚠️ CRM initialized (demo mode - data stored locally)');
    }
  }

  private getHeaders() {
    return {
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
    };
  }

  // ============ CONTACTS ============

  async createContact(contact: Contact): Promise<Contact> {
    const id = contact.id || `contact-${Date.now()}`;
    const newContact: Contact = {
      ...contact,
      id,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.contacts.set(id, newContact);
    console.log(`👤 Contact created: ${newContact.name} (${id})`);
    this.emit('contact_created', newContact);
    return newContact;
  }

  async getContact(id: string): Promise<Contact | undefined> {
    return this.contacts.get(id);
  }

  async updateContact(id: string, updates: Partial<Contact>): Promise<Contact | undefined> {
    const contact = this.contacts.get(id);
    if (contact) {
      const updated = { ...contact, ...updates, updatedAt: new Date() };
      this.contacts.set(id, updated);
      console.log(`👤 Contact updated: ${updated.name}`);
      this.emit('contact_updated', updated);
      return updated;
    }
    return undefined;
  }

  async deleteContact(id: string): Promise<boolean> {
    const result = this.contacts.delete(id);
    if (result) {
      console.log(`👤 Contact deleted: ${id}`);
      this.emit('contact_deleted', id);
    }
    return result;
  }

  async searchContacts(query: string): Promise<Contact[]> {
    const results: Contact[] = [];
    const lower = query.toLowerCase();
    
    for (const contact of this.contacts.values()) {
      if (
        contact.name.toLowerCase().includes(lower) ||
        contact.email?.toLowerCase().includes(lower) ||
        contact.phone?.includes(query) ||
        contact.company?.toLowerCase().includes(lower)
      ) {
        results.push(contact);
      }
    }
    return results;
  }

  async getAllContacts(): Promise<Contact[]> {
    return Array.from(this.contacts.values());
  }

  // ============ COMPANIES ============

  async createCompany(company: Company): Promise<Company> {
    const id = company.id || `company-${Date.now()}`;
    const newCompany: Company = { ...company, id };
    this.companies.set(id, newCompany);
    console.log(`🏢 Company created: ${newCompany.name} (${id})`);
    this.emit('company_created', newCompany);
    return newCompany;
  }

  async getCompany(id: string): Promise<Company | undefined> {
    return this.companies.get(id);
  }

  async getAllCompanies(): Promise<Company[]> {
    return Array.from(this.companies.values());
  }

  // ============ DEALS ============

  async createDeal(deal: Deal): Promise<Deal> {
    const id = deal.id || `deal-${Date.now()}`;
    const newDeal: Deal = { ...deal, id };
    this.deals.set(id, newDeal);
    console.log(`💰 Deal created: ${newDeal.title} (${id})`);
    this.emit('deal_created', newDeal);
    return newDeal;
  }

  async updateDeal(id: string, updates: Partial<Deal>): Promise<Deal | undefined> {
    const deal = this.deals.get(id);
    if (deal) {
      const updated = { ...deal, ...updates };
      this.deals.set(id, updated);
      console.log(`💰 Deal updated: ${updated.title}`);
      this.emit('deal_updated', updated);
      return updated;
    }
    return undefined;
  }

  async getDealsByStage(): Promise<Record<Deal['stage'], Deal[]>> {
    const byStage: Record<string, Deal[]> = {
      lead: [],
      qualified: [],
      proposal: [],
      negotiation: [],
      won: [],
      lost: [],
    };

    for (const deal of this.deals.values()) {
      byStage[deal.stage]?.push(deal);
    }
    return byStage as Record<Deal['stage'], Deal[]>;
  }

  async getTotalPipelineValue(): Promise<number> {
    let total = 0;
    for (const deal of this.deals.values()) {
      if (deal.stage !== 'won' && deal.stage !== 'lost' && deal.value) {
        total += deal.value * (deal.probability || 100) / 100;
      }
    }
    return total;
  }

  // ============ TASKS ============

  async createTask(task: Task): Promise<Task> {
    const id = task.id || `task-${Date.now()}`;
    const newTask: Task = { ...task, id };
    this.tasks.set(id, newTask);
    console.log(`📋 Task created: ${newTask.title}`);
    this.emit('task_created', newTask);
    return newTask;
  }

  async getTasksByContact(contactId: string): Promise<Task[]> {
    return Array.from(this.tasks.values()).filter((t) => t.contactId === contactId);
  }

  async getPendingTasks(): Promise<Task[]> {
    return Array.from(this.tasks.values()).filter((t) => t.status !== 'completed');
  }

  async completeTask(id: string): Promise<boolean> {
    const task = this.tasks.get(id);
    if (task) {
      task.status = 'completed';
      this.tasks.set(id, task);
      console.log(`✅ Task completed: ${task.title}`);
      this.emit('task_completed', task);
      return true;
    }
    return false;
  }

  // ============ NOTES ============

  async addNote(note: Note): Promise<Note> {
    const id = note.id || `note-${Date.now()}`;
    const newNote: Note = { ...note, id, createdAt: new Date() };
    this.notes.set(id, newNote);
    console.log(`📝 Note added`);
    this.emit('note_added', newNote);
    return newNote;
  }

  async getNotesByContact(contactId: string): Promise<Note[]> {
    return Array.from(this.notes.values()).filter((n) => n.contactId === contactId);
  }

  // ============ ANALYTICS ============

  async getCRMStats(): Promise<{
    totalContacts: number;
    totalCompanies: number;
    totalDeals: number;
    openDeals: number;
    wonDeals: number;
    totalValue: number;
    pipelineValue: number;
    pendingTasks: number;
  }> {
    const deals = Array.from(this.deals.values());
    const contacts = Array.from(this.contacts.values());
    const companies = Array.from(this.companies.values());
    const tasks = Array.from(this.tasks.values());

    return {
      totalContacts: contacts.length,
      totalCompanies: companies.length,
      totalDeals: deals.length,
      openDeals: deals.filter((d) => !['won', 'lost'].includes(d.stage)).length,
      wonDeals: deals.filter((d) => d.stage === 'won').length,
      totalValue: deals.filter((d) => d.stage === 'won').reduce((sum, d) => sum + (d.value || 0), 0),
      pipelineValue: await this.getTotalPipelineValue(),
      pendingTasks: tasks.filter((t) => t.status !== 'completed').length,
    };
  }

  // ============ LEAD QUALIFICATION ============

  async qualifyLead(contactId: string, score: number): Promise<{
    status: 'hot' | 'warm' | 'cold';
    recommendation: string;
  }> {
    const contact = this.contacts.get(contactId);
    if (!contact) {
      return { status: 'cold', recommendation: 'Contact not found' };
    }

    let status: 'hot' | 'warm' | 'cold';
    let recommendation: string;

    if (score >= 70) {
      status = 'hot';
      recommendation = 'Priority follow-up, schedule demo call';
    } else if (score >= 40) {
      status = 'warm';
      recommendation = 'Nurture with content, schedule check-in';
    } else {
      status = 'cold';
      recommendation = 'Add to email sequence, periodic check-in';
    }

    // Create task based on status
    await this.createTask({
      title: `Lead follow-up: ${contact.name}`,
      description: recommendation,
      priority: status === 'hot' ? 'high' : status === 'warm' ? 'medium' : 'low',
      status: 'pending',
      contactId,
    });

    return { status, recommendation };
  }
}

export default CRMConnector;
