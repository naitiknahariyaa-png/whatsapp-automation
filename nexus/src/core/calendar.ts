// NEXUS Platform - Calendar (Cal.com Integration)
import { EventEmitter } from 'events';
import axios from 'axios';

interface CalConfig {
  apiKey?: string;
  baseUrl?: string;
}

interface CalendarEvent {
  id?: string;
  title: string;
  description?: string;
  startTime: Date;
  endTime: Date;
  attendees: string[];
  timezone?: string;
  location?: string;
  conferenceData?: {
    provider?: string;
    meetingUrl?: string;
  };
}

interface BookingRequest {
  eventTypeSlug: string;
  startTime: string;
  endTime?: string;
  name: string;
  email: string;
  notes?: string;
  responses?: Record<string, string>;
}

interface AvailabilitySlot {
  start: string;
  end: string;
}

export class CalendarConnector extends EventEmitter {
  private apiKey: string | null = null;
  private baseUrl: string;
  private config: CalConfig;

  constructor(config: CalConfig = {}) {
    super();
    this.config = {
      baseUrl: 'https://api.cal.com/v1',
      ...config,
    };
    this.baseUrl = this.config.baseUrl || 'https://api.cal.com/v1';
  }

  initialize(): void {
    this.apiKey = this.config.apiKey || process.env.CAL_API_KEY || null;
    if (this.apiKey) {
      console.log('✅ Cal.com Calendar initialized');
    } else {
      console.log('⚠️ Cal.com Calendar initialized (no API key - limited mode)');
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

  // Get current user's schedule
  async getSchedule(userId: string): Promise<CalendarEvent[]> {
    if (!this.apiKey) {
      return this.getMockEvents();
    }

    try {
      const response = await axios.get(
        `${this.baseUrl}/schedules`,
        this.getHeaders()
      );
      return response.data.schedules || [];
    } catch (error) {
      console.error('Error fetching schedule:', error);
      return [];
    }
  }

  // Get available slots
  async getAvailableSlots(
    eventTypeSlug: string,
    startDate: string,
    endDate: string
  ): Promise<AvailabilitySlot[]> {
    if (!this.apiKey) {
      return this.getMockSlots();
    }

    try {
      const response = await axios.get(
        `${this.baseUrl}/slots`,
        {
          ...this.getHeaders(),
          params: {
            eventTypeSlug,
            startTime: startDate,
            endTime: endDate,
          },
        }
      );
      return response.data.slots || [];
    } catch (error) {
      console.error('Error fetching slots:', error);
      return [];
    }
  }

  // Create a booking
  async createBooking(booking: BookingRequest): Promise<{
    success: boolean;
    booking?: CalendarEvent;
    error?: string;
  }> {
    if (!this.apiKey) {
      // Mock booking
      const mockBooking: CalendarEvent = {
        id: `mock-${Date.now()}`,
        title: booking.eventTypeSlug,
        description: booking.notes,
        startTime: new Date(booking.startTime),
        endTime: new Date(booking.endTime || booking.startTime),
        attendees: [booking.email],
      };
      console.log('📅 Mock booking created:', mockBooking);
      return { success: true, booking: mockBooking };
    }

    try {
      const response = await axios.post(
        `${this.baseUrl}/bookings`,
        booking,
        this.getHeaders()
      );
      console.log('📅 Booking created:', response.data);
      return { success: true, booking: response.data };
    } catch (error: any) {
      console.error('Booking error:', error);
      return {
        success: false,
        error: error.response?.data?.message || 'Booking failed',
      };
    }
  }

  // Cancel a booking
  async cancelBooking(bookingId: string, reason?: string): Promise<boolean> {
    if (!this.apiKey) {
      console.log(`📅 Mock: Booking ${bookingId} cancelled`);
      return true;
    }

    try {
      await axios.delete(
        `${this.baseUrl}/bookings/${bookingId}`,
        {
          ...this.getHeaders(),
          data: { reason },
        }
      );
      console.log(`📅 Booking ${bookingId} cancelled`);
      return true;
    } catch (error) {
      console.error('Cancel booking error:', error);
      return false;
    }
  }

  // Get upcoming events
  async getUpcomingEvents(limit = 10): Promise<CalendarEvent[]> {
    if (!this.apiKey) {
      return this.getMockEvents();
    }

    try {
      const response = await axios.get(
        `${this.baseUrl}/bookings`,
        {
          ...this.getHeaders(),
          params: { status: 'upcoming', limit },
        }
      );
      return response.data.bookings || [];
    } catch (error) {
      console.error('Error fetching events:', error);
      return [];
    }
  }

  // Reschedule a booking
  async rescheduleBooking(
    bookingId: string,
    newStartTime: string,
    newEndTime?: string
  ): Promise<boolean> {
    if (!this.apiKey) {
      console.log(`📅 Mock: Booking ${bookingId} rescheduled to ${newStartTime}`);
      return true;
    }

    try {
      await axios.patch(
        `${this.baseUrl}/bookings/${bookingId}`,
        {
          startTime: newStartTime,
          endTime: newEndTime,
        },
        this.getHeaders()
      );
      console.log(`📅 Booking ${bookingId} rescheduled`);
      return true;
    } catch (error) {
      console.error('Reschedule error:', error);
      return false;
    }
  }

  // Create event type
  async createEventType(data: {
    title: string;
    slug: string;
    description?: string;
    duration: number;
    schedulingType?: 'ROUND_ROBIN' | 'COLLECTIVE';
  }): Promise<{ success: boolean; id?: string }> {
    if (!this.apiKey) {
      console.log('📅 Mock: Event type created:', data);
      return { success: true, id: `mock-${Date.now()}` };
    }

    try {
      const response = await axios.post(
        `${this.baseUrl}/event-types`,
        data,
        this.getHeaders()
      );
      return { success: true, id: response.data.eventType.id };
    } catch (error) {
      console.error('Create event type error:', error);
      return { success: false };
    }
  }

  // Get event types
  async getEventTypes(): Promise<any[]> {
    if (!this.apiKey) {
      return this.getMockEventTypes();
    }

    try {
      const response = await axios.get(
        `${this.baseUrl}/event-types`,
        this.getHeaders()
      );
      return response.data.event_types || [];
    } catch (error) {
      console.error('Error fetching event types:', error);
      return [];
    }
  }

  // Mock data for testing without API key
  private getMockEvents(): CalendarEvent[] {
    const now = new Date();
    return [
      {
        id: 'mock-1',
        title: 'Sales Call',
        description: 'Follow up with potential client',
        startTime: new Date(now.getTime() + 3600000),
        endTime: new Date(now.getTime() + 7200000),
        attendees: ['client@example.com'],
        location: 'Zoom',
      },
      {
        id: 'mock-2',
        title: 'Team Standup',
        startTime: new Date(now.getTime() + 86400000),
        endTime: new Date(now.getTime() + 86400000 + 1800000),
        attendees: ['team@company.com'],
        location: 'Google Meet',
      },
    ];
  }

  private getMockSlots(): AvailabilitySlot[] {
    const now = new Date();
    const slots: AvailabilitySlot[] = [];
    for (let i = 1; i <= 5; i++) {
      const slotStart = new Date(now.getTime() + i * 86400000);
      slotStart.setHours(9, 0, 0, 0);
      const slotEnd = new Date(slotStart.getTime() + 3600000);
      slots.push({
        start: slotStart.toISOString(),
        end: slotEnd.toISOString(),
      });
    }
    return slots;
  }

  private getMockEventTypes() {
    return [
      {
        id: 'mock-1',
        title: '30 Min Meeting',
        slug: '30min',
        duration: 30,
      },
      {
        id: 'mock-2',
        title: '60 Min Consultation',
        slug: '60min',
        duration: 60,
      },
      {
        id: 'mock-3',
        title: 'Discovery Call',
        slug: 'discovery',
        duration: 15,
      },
    ];
  }
}

export default CalendarConnector;
