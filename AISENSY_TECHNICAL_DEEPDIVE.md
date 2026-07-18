# Aisensy - EXACT Technical Architecture Deep Dive

> **Source**: Engineering Blog by Romit Singh Bhau (Engineering Manager), AWS Case Study, GitHub Repos, and public documentation

---

## 🏗️ Infrastructure Evolution Timeline

### The Journey (2020 → Present)

```
2020: Free Heroku Dyno
     ↓
2021: EC2 + Vertical Scaling
     ↓
2022: Microservices + MongoDB (single instance - BOTTLENECK!)
     ↓
2023: Async by Default + AWS Migration
     ↓
2024: CQRS + DocumentDB Migration
     ↓
2025: AI Agents + Bedrock Integration
     ↓
Future: 500M+ API requests/day target
```

---

## ⚙️ EXACT Tech Stack

### Database Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Primary Database** | **Amazon DocumentDB** (MongoDB-compatible) | Main data store - migrated from MongoDB Atlas |
| **Migrated Data** | 120 TB in 3 weeks | Zero downtime migration |
| **Monitoring** | **Amazon CloudWatch** | Centralized logging and monitoring |
| **Event Processing** | **AWS Lambda** + DocumentDB Change Streams | Event-driven data pipelines |

### Key Stats:
- **20% lower database costs** after migration
- **95% faster queries** after optimization
- **12 clusters** running daily on MongoDB Atlas (before migration)
- **Zero downtime** during migration using AWS DMS

### Compute & Serverless

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containers** | Docker containers (per service) | Service isolation |
| **Serverless** | AWS Lambda | Burst handling, event processing |
| **Autoscaling** | Queue-depth based (not CPU-based!) | Proactive scaling |

### Why Queue-Based Autoscaling?
> *"By the time CPU spikes, you've already kept someone waiting."*
> - Autoscaling triggers on queue depth, message arrival rate, consumer lag
> - Pre-warming capacity before scheduled campaigns

---

## 🔄 Message Processing Architecture

### The Core Problem
```
210,000 businesses
     ↓
Different sending schedules
     ↓
Burst traffic (campaign launches)
     ↓
WhatsApp API rate limits per WABA account
     ↓
Must maximize throughput WITHOUT breaching limits
```

### Traffic Shaping Engine (The Unseen Hero)

```python
# Conceptual model of their traffic control system

class TrafficShaper:
    """
    Feedback-driven traffic shaping for WhatsApp API
    Core of their 200M+ daily requests handling
    """
    
    def __init__(self):
        self.per_account_limits = {}  # Track per-WABA limits
        self.dispatch_rate = {}       # Real-time rate tracking
        self.buffer_queues = {}       # Upstream burst buffering
    
    def track_rate_limit(self, waba_id, meta_response):
        """Track rate limits from Meta API responses"""
        self.per_account_limits[waba_id] = {
            'limit': meta_response.headers.get('X-RateLimit-Limit'),
            'remaining': meta_response.headers.get('X-RateLimit-Remaining'),
            'reset': meta_response.headers.get('X-RateLimit-Reset')
        }
    
    def dispatch(self, message, waba_id):
        """Dispatch at maximum compliant throughput"""
        if self._can_send(waba_id):
            return self._send_to_meta(message)
        else:
            self._buffer_message(message, waba_id)
    
    def _can_send(self, waba_id):
        """Check if can send within rate limits"""
        limits = self.per_account_limits.get(waba_id, {})
        return limits.get('remaining', 0) > 0
```

### Key Features of Their Traffic Shaping:

1. **Real-time Rate Limit Tracking** - Uses Meta API response headers
2. **Burst Buffering** - Smooths upstream bursts into permitted downstream traffic
3. **Request Coalescing** - Batches requests to reduce per-message API overhead
4. **Idempotency Keys** - Prevents duplicate delivery on retries
5. **Pipeline Isolation** - Per-message-category isolation (no cross-tenant failures)

### Result:
> *"No platform-induced account suspensions across 210,000 businesses"*

---

## 🗄️ Database Architecture (CQRS Pattern)

### Problem They Faced
```
Single MongoDB instance
     ↓
Analytical queries + Transactional writes
     ↓
Competing workloads
     ↓
Database became 3 AM wake-up call
```

### Solution: CQRS + DocumentDB

```
                    ┌─────────────────────────────────────┐
                    │           WRITE PATH                 │
                    │  (Transactional workloads)          │
                    │                                     │
  Application ────▶│  Amazon DocumentDB                  │
                    │  • Real-time message status         │
                    │  • Contact updates                  │
                    │  • Campaign triggers                │
                    └─────────────────────────────────────┘
                              │
                              │ Change Data Capture (CDC)
                              ▼
                    ┌─────────────────────────────────────┐
                    │           READ PATH                  │
                    │  (Analytical workloads)              │
                    │                                     │
                    │  • Dashboard queries                 │
                    │  • Analytics                        │
                    │  • Reporting                        │
                    └─────────────────────────────────────┘
```

### Optimization Layers (6 Total)

1. **Query Optimization + Index Hygiene**
   - Aligned with write-heavy workload
   - Eliminated N+1 queries
   - Removed redundant indexes

2. **Connection Pooling**
   - Prevents connection exhaustion
   - Multiplexes application threads

3. **CQRS (Command Query Responsibility Segregation)**
   - Separates reads from writes
   - Analytics no longer competes with transactions

4. **Change Data Capture (CDC)**
   - Async event propagation
   - No impact on hot path

5. **Bulk Operations**
   - `insertMany` and `bulkWrite`
   - Reduced DB round-trips by orders of magnitude

6. **Partitioning + Tiered Storage**
   - Hot data → DocumentDB
   - Cold data → S3 (Parquet/columnar formats)

---

## 🔄 Async Processing Architecture

### The Incident That Changed Everything

```
Early 2025: Large customer fires multi-million message campaign
     ↓
Request thread pool backs up (synchronous Meta API calls)
     ↓
Retries amplify original load by 3-4×
     ↓
System begins amplifying its own failure
     ↓
First signal: Support tickets from OTHER customers about delays
```

### Lesson Learned:
> *"A 'safety' mechanism had become the fire."*

### Solution: Async-First Architecture

```python
# After the incident - everything async by default

class MessageProcessor:
    """
    Async message processing pipeline
    """
    
    def __init__(self):
        self.message_queue = Queue()  # Buffered processing
        self.circuit_breaker = CircuitBreaker()
        self.idempotency_store = IdempotencyStore()
    
    async def process_message(self, message):
        """Non-blocking message processing"""
        # Check idempotency first
        if self.idempotency_store.exists(message.id):
            return  # Already processed
        
        try:
            # Use circuit breaker for external calls
            await self.circuit_breaker.call(
                self.send_to_whatsapp, message
            )
        except CircuitOpen:
            # Re-queue with backoff
            await self.message_queue.requeue_with_delay(
                message,
                delay=self.calculate_backoff()
            )
        
        # Mark as processed
        self.idempotency_store.mark(message.id)
```

### Resilience Toolkit

| Technique | Purpose |
|-----------|---------|
| **Exponential Backoff + Jitter** | Prevents thundering-herd on retries |
| **Circuit Breakers** | Stops calling failing dependencies |
| **Idempotency Keys** | Safe retries, no duplicate processing |
| **Retry Budgets** | Caps retry amplification |
| **Dead Letter Queues** | Isolates unprocessable messages |

---

## 📊 Observability Stack

### Problem at Scale
```
Fragmented logs across dozens of services
     ↓
Reconstructing timelines impossible
     ↓
Need to trace single request across entire system
```

### Solution: OpenTelemetry + CloudWatch

```yaml
# Every request gets correlation ID
# Example: trace message from campaign → WhatsApp → delivery

correlation_id: "req_abc123"
  ├── campaign_service: ✅ sent
  ├── queue_processor: ✅ queued  
  ├── rate_limiter: ✅ throttled
  ├── whatsapp_api: ✅ delivered
  └── webhook_handler: ✅ acknowledged
```

### Monitoring Setup

| Component | Tool | Purpose |
|-----------|------|---------|
| **Distributed Tracing** | OpenTelemetry | Full request path visibility |
| **Metrics & Logs** | Amazon CloudWatch | Centralized observability |
| **Alerting** | CloudWatch Alarms | Proactive notifications |
| **Correlation IDs** | Custom implementation | Single log line → full path |

---

## 🏢 Multi-Tenant Isolation Strategy

### The Noisy Neighbor Problem

```
210,000 businesses
     ↓
Different campaign schedules
     ↓
One business fires 1M message campaign
     ↓
Can it degrade performance for others?
```

### Isolation Layers

| Layer | Strategy |
|-------|----------|
| **Rate Limiting** | Per-tenant message limits |
| **Data Isolation** | Logical separation at data layer |
| **Access Control** | Strict enforcement at every service boundary |
| **Pipeline Isolation** | No shared mutable state between tenant workflows |

### Result:
> *"A business firing a 1-million-message campaign does not degrade delivery performance for the 209,999 businesses running alongside it."*

---

## 🔧 Code Stack (From GitHub Analysis)

### Main Repository: `onehashai/aisensy`

```
Language Distribution:
├── JavaScript: 86.4%  (Primary - likely Node.js backend)
└── Python: 13.6%       (Secondary - ML/AI, scripts)
```

### Additional Repositories

| Repo | Technology | Purpose |
|------|------------|---------|
| `techyaisensy/n8n-nodes-aisensy` | Node.js (npm) | Official n8n integration node |
| Node ecosystem | npm packages | API clients, connectors |

### n8n Node Structure

```javascript
// From their n8n node implementation
// npm package: @techyaisensy/n8n-nodes-aisensy

// Core operations:
// 1. Send Campaign Message
// 2. Trigger Project Message  
// 3. Receive Webhook (inbound)
// 4. Manage Templates

// Example usage:
const node = new AisensyNode();
node.execute([
    { operation: 'send', phone: '+91...', message: 'Hello' }
]);
```

---

## 🌐 CDN & Network Optimization

### Network Costs at Scale

```
200M requests/day
     ↓
Hundreds of millions of messages
     ↓
LOTS of bytes moving
     ↓
Network bandwidth became real constraint
     (Often BEFORE CPU!)
```

### Optimizations Applied

| Technique | Impact |
|-----------|--------|
| **HTTP Keep-Alive** | TLS handshake: hundreds of ms → near-zero |
| **DNS Caching** | Eliminated repeated resolution overhead |
| **In-memory LRU Cache** | Microsecond cache hits vs millisecond DB queries |
| **GZIP Compression** | Smaller payloads, less latency |
| **CDN** | Global static asset delivery, reduced origin load |

### Principle:
> *"Always eliminate work that doesn't need to happen before optimizing the work that does."*

---

## 🤖 AI Architecture (Planned)

### Current State: AI Agents with Knowledge Base

```
User Message
     ↓
Intent Detection (NLP)
     ↓
Knowledge Base Lookup
     ↓
AI Orchestrator
     ↓
Response Generation
     ↓
WhatsApp Delivery
```

### Future: Amazon Bedrock Integration

From AWS Case Study:
> *"For its generative AI use cases, AiSensy plans to deploy foundation models using Amazon Bedrock"*

### AI Components (From Tutorials)

1. **Knowledge Base** - Product info, FAQs, policies
2. **AI Orchestrator** - Routes conversations, manages context
3. **Agentic Flows** - Multi-step task completion

---

## 🚀 Autoscaling Strategy

### The Problem with CPU-Based Scaling

```
WhatsApp campaigns = near-instantaneous traffic surges
     ↓
No gradual ramp
     ↓
CPU spike → threshold → scale-out → warm-up
     ↓
Burst already caused degradation!
     ↓
Scaling in REACTION to damage, not in ANTICIPATION
```

### Solution: Event-Driven Sidecar Pattern

```yaml
# Sidecar agent alongside each service
Service:
  - Monitors: queue_depth, message_arrival_rate, consumer_lag
  - Triggers: scale-out when queue_depth climbing (BEFORE CPU spike)
  - Pre-warms: capacity before scheduled campaigns fire
```

### Container Strategy

```
Not one-size-fits-all containers:

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Stateless       │  │ Message         │  │ CPU-Intensive   │
│ Webhook Handler │  │ Formatter       │  │ Analytics       │
│ (lightweight)   │  │ (memory-bound)  │  │ (compute-bound) │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 🐛 Scale-Specific Failures They Encountered

### 1. Garbage Collection Storms

```python
# Problem: High concurrent message volume
#         → GC pressure during bursts
#         → Pause storms
#         → Latency spikes
#         → Cascades into upstream timeouts

# Solution:
- Profiling heap allocation patterns
- Tuned GC parameters
- Concurrency limits per worker
- Evaluating lower-level runtimes (Rust/Go)
```

### 2. Network Bandwidth Saturation

```
Problem: Bytes moving = real constraint
         Often BEFORE CPU!
         
Solution:
- Client-side rate limiting
- Backpressure instead of hard wall
- Alerting tuned for actionable warnings
```

### 3. Distributed Debugging

```
Problem: Logs across dozens of services
         Impossible to reconstruct timelines
         
Solution:
- OpenTelemetry traces everywhere
- CloudWatch alarms below hard limits
- Correlation IDs on every request
```

---

## 📈 Performance Results Summary

| Metric | Before | After |
|--------|--------|-------|
| **Database Queries** | Baseline | **95% faster** |
| **Database Costs** | Baseline | **20% lower** |
| **Migration Time** | - | **3 weeks** |
| **Downtime** | Occasional | **Zero** |
| **Daily API Requests** | - | **200M+** |
| **Annual Messages** | - | **6.5B+** |
| **Businesses Served** | 20-30 | **210,000** |
| **Countries** | - | **68+** |

---

## 🎯 Key Engineering Principles

From their CTO (extracted from blog):

### 1. Design for Failure
> Assume dependencies will be slow, unavailable, or wrong

### 2. Async by Default
> If user doesn't need result in HTTP response → queue it

### 3. Single-Responsibility Pipelines
> One job each, no shared mutable state
> Failures stay localized

### 4. Idempotency Everywhere
> Any operation that can be retried must be safe to retry

### 5. Feedback-Driven Systems
> Rate control, autoscaling, retries use real-time signals
> Not fixed thresholds

### 6. Right Tool for the Job
```
MongoDB → Transactional workloads
Columnar → Analytics
Lambda → Burst processing  
S3/Parquet → Archival (cold data)
```

---

## 🔮 Future Roadmap

| Target | Current |
|--------|---------|
| **API Requests/Day** | 200M → **500M** |
| **AI Features** | Basic → **Agentic AI** |
| **Channels** | WhatsApp → **Multi-channel** |
| **Media** | Text/Images → **Video support** |

---

## 🛠️ How to Build This System

### Phase 1: Foundation (Week 1-4)
```
Tech Stack:
├── Node.js/Express for API
├── MongoDB/DocumentDB for data
├── Bull/Redis for job queues
└── Simple EC2 deployment
```

### Phase 2: Scale Readiness (Week 5-8)
```
Add:
├── Connection pooling
├── CQRS pattern
├── Circuit breakers
├── Rate limiting
└── Basic observability
```

### Phase 3: Production Scale (Week 9-12)
```
Upgrade:
├── Migrate to DocumentDB (if AWS)
├── Queue-depth autoscaling
├── Change Data Capture
├── OpenTelemetry tracing
└── CDN for static assets
```

### Phase 4: AI Features (Ongoing)
```
Integrate:
├── Amazon Bedrock / OpenAI
├── Knowledge base
├── Intent detection
├── AI orchestrator
└── Human handoff logic
```

---

## 📚 Reference Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                                  │
│  React Dashboard │ Flow Builder │ Campaign Manager │ Analytics          │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ REST/GraphQL
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                                     │
│  Rate Limiting │ Authentication │ Tenant Isolation │ Load Balancing     │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│   Campaign    │      │   Message     │      │    AI         │
│   Service     │      │   Processor   │      │   Service     │
│  (Orchestra- │      │  (Executor)   │      │  (Orchestra- │
│   tion)       │      │               │      │   tor)        │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │
        │    Async Queue        │                      │
        └──────────────────────┼──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Redis/Bull      │
                    │   (Job Queue)      │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│   WhatsApp     │      │  Traffic      │      │    Webhook    │
│   Sender       │◀────▶│  Shaper       │      │   Handler     │
│  (Rate Limit   │      │               │      │               │
│   Aware)       │      │               │      │               │
└───────┬───────┘      └───────────────┘      └───────┬───────┘
        │                                               │
        └───────────────────────┬───────────────────────┘
                                │
                    ┌──────────▼──────────┐
                    │  Meta WhatsApp API   │
                    └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                      │
│                                                                         │
│  ┌─────────────────────┐         ┌─────────────────────┐                │
│  │   Amazon DocumentDB  │◀──CDC──│   Analytics DB      │                │
│  │   (Primary/Write)    │         │   (Read/Replicas)   │                │
│  └─────────────────────┘         └─────────────────────┘                │
│                                                                         │
│  ┌─────────────────────┐         ┌─────────────────────┐                │
│  │   Amazon S3          │         │   CloudWatch        │                │
│  │   (Cold Storage)     │         │   (Observability)   │                │
│  └─────────────────────┘         └─────────────────────┘                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📖 Key Resources

| Resource | Link |
|----------|------|
| Engineering Blog | https://m.aisensy.com/blog/engineering/how-aisensy-handles-200m-api-requests-everyday |
| AWS Case Study | https://aws.amazon.com/solutions/case-studies/aisensy |
| GitHub (OneHash) | https://github.com/onehashai/aisensy |
| n8n Integration | https://github.com/techyaisensy/n8n-nodes-aisensy |
| API Docs | https://wiki.aisensy.com/en/articles/11501889-api-reference-docs |

---

*Analysis compiled from public sources including engineering blog posts, AWS case studies, and GitHub repositories.*
