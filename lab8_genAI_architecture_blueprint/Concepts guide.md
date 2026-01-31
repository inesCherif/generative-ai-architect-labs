# Lab 8: Architecture Concepts Guide

Everything you need to know about designing GenAI systems.

---

## 📚 Part 1: What is System Architecture?

### Simple Definition

**System Architecture** = Blueprint for how software components work together

Think of it like:

- **Building Architecture** → Blueprint shows rooms, plumbing, electrical
- **System Architecture** → Diagram shows services, databases, data flow

### Why Architecture Matters

**Without Architecture:**

```
❌ Components don't fit together
❌ Performance bottlenecks
❌ Security vulnerabilities
❌ Hard to scale
❌ Difficult to maintain
```

**With Architecture:**

```
✅ Clear component responsibilities
✅ Optimized data flow
✅ Security by design
✅ Scalable from day one
✅ Easy to explain and maintain
```

---

## 🏗️ Part 2: GenAI Architecture Components

### Layer 1: User Interface (Frontend)

**What it is:** How users interact with your AI system

**Options:**

- **Web App** - Streamlit, Gradio, React
- **Mobile App** - React Native, Flutter
- **Chat Interface** - Slack bot, Discord bot
- **API Only** - No UI, just endpoints

**When to use what:**

- Internal tool → Streamlit (fast to build)
- Customer-facing → React (professional)
- Team collaboration → Slack/Discord bot
- Integration → API only

**Example:**

```python
# Streamlit chat interface
import streamlit as st

st.title("AI Assistant")
user_input = st.text_input("Ask me anything:")
if user_input:
    response = ai_pipeline(user_input)
    st.write(response)
```

---

### Layer 2: API Gateway

**What it is:** Entry point that routes requests to services

**Why you need it:**

- Authentication (who is this?)
- Rate limiting (prevent abuse)
- Routing (which service handles this?)
- Monitoring (track usage)

**Options:**

- **AWS API Gateway** - Managed, scales automatically
- **Kong** - Open source, flexible
- **FastAPI** - Simple, Python-native (what we used in Lab 7)

**Example Flow:**

```
User Request
    ↓
API Gateway
    ↓ (checks auth token)
    ↓ (checks rate limit)
    ↓ (routes based on path)
    ↓
Backend Service
```

---

### Layer 3: LLM (Large Language Model)

**What it is:** The AI brain that generates responses

**Options:**

**1. OpenAI GPT-4**

- ✅ Most capable
- ✅ Easy API
- ❌ Expensive
- ❌ Data sent to OpenAI

**2. Anthropic Claude**

- ✅ Long context (200K tokens)
- ✅ Strong reasoning
- ❌ Expensive
- ❌ Data sent to Anthropic

**3. Open Source (Llama, Mistral)**

- ✅ Private (your infrastructure)
- ✅ Customizable
- ❌ Need GPU infrastructure
- ❌ More complex to deploy

**4. Azure OpenAI**

- ✅ Enterprise features
- ✅ Data stays in your cloud
- ❌ More expensive
- ❌ Requires Azure setup

**When to use what:**

- Prototype → OpenAI GPT-4 (easiest)
- Production (sensitive data) → Azure OpenAI or self-hosted
- Cost-sensitive → Open source models
- Long documents → Claude

---

### Layer 4: RAG Components

**What it is:** System for retrieving relevant knowledge

**Component 4a: Vector Database**

**What it does:** Stores document embeddings for semantic search

**Options:**

- **Pinecone** - Managed, easy, expensive
- **Weaviate** - Open source, feature-rich
- **Chroma** - Simple, local, free
- **FAISS** - Facebook's library, fast

**When to use:**

- Need semantic similarity search
- Large document corpus
- "Find similar" queries

**Example:**

```python
# Store documents
vectordb.add(documents, embeddings)

# Search
results = vectordb.search("How to treat headaches?", k=5)
```

**Component 4b: Knowledge Graph**

**What it does:** Stores structured relationships (what you did in Lab 7!)

**Options:**

- **Neo4j** - Popular graph database
- **Stardog** - RDF/SPARQL focus
- **Apache Jena Fuseki** - What we used in Lab 7

**When to use:**

- Complex relationships matter
- Need reasoning
- Domain has hierarchies

**Example:**

```sparql
SELECT ?treatment ?mechanism
WHERE {
    ?treatment treats ?disease .
    ?treatment hasMechanism ?mechanism .
}
```

---

### Layer 5: Agent Orchestration (Optional)

**What it is:** Coordinates multiple AI agents to solve complex tasks

**Why you might need it:**

- Multi-step workflows
- Need to use multiple tools
- Complex reasoning required

**Options:**

**1. LangChain**

- ✅ Most popular
- ✅ Lots of integrations
- ❌ Complex API

**2. LangGraph**

- ✅ State management
- ✅ Explicit control flow
- ❌ Newer, fewer examples

**3. CrewAI**

- ✅ Multi-agent focus
- ✅ Role-based agents
- ❌ Less flexible

**4. AutoGen**

- ✅ Microsoft-backed
- ✅ Conversational agents
- ❌ Still evolving

**Example Use Case:**

```
User: "Analyze this contract and schedule a review meeting"

Agent 1 (Analyst): Reads contract, identifies risks
    ↓
Agent 2 (Summarizer): Creates executive summary
    ↓
Agent 3 (Scheduler): Checks calendars, books meeting
    ↓
Final Response: "Found 3 risks. Meeting scheduled for Tuesday."
```

---

### Layer 6: Data Storage

**What it is:** Where you store application data

**Options:**

**Relational DB (PostgreSQL, MySQL)**

- ✅ Structured data
- ✅ Transactions
- ❌ Not for unstructured text

**Document DB (MongoDB)**

- ✅ Flexible schema
- ✅ JSON documents
- ❌ No complex joins

**Object Storage (S3)**

- ✅ Files, images, documents
- ✅ Cheap, scalable
- ❌ No querying

**When to use what:**

```
User accounts, orders     → PostgreSQL
Chat history, logs        → MongoDB
PDFs, images, videos      → S3
Document embeddings       → Vector DB
Knowledge relationships   → Graph DB
```

---

### Layer 7: Deployment & Infrastructure

**What it is:** Where your code runs

**Options:**

**1. Cloud Functions (Serverless)**

- ✅ Auto-scales
- ✅ Pay per use
- ❌ Cold starts
- ❌ Limited by timeout

**2. Containers (Docker + K8s)**

- ✅ Full control
- ✅ No timeouts
- ❌ More complex
- ❌ Need to manage scaling

**3. Managed Services**

- AWS Fargate - Run containers without managing servers
- Azure Container Apps - Similar to Fargate
- Google Cloud Run - Serverless containers

**When to use what:**

- Simple API → Cloud Functions
- Complex workflows → Containers
- Need GPUs → EC2/Compute instances
- Best balance → Fargate/Cloud Run

---

### Layer 8: Monitoring & Observability

**What it is:** Track system health and performance

**What to monitor:**

- **Latency** - How long do requests take?
- **Errors** - What's failing?
- **Token usage** - LLM cost tracking
- **User satisfaction** - Thumbs up/down
- **System resources** - CPU, memory, disk

**Tools:**

- **Prometheus + Grafana** - Open source, flexible
- **CloudWatch (AWS)** - Managed, integrated
- **Datadog** - Premium, powerful
- **LangSmith** - LLM-specific monitoring

**Example Metrics:**

```python
# Track in your code
track_metric("llm_latency", duration_ms)
track_metric("tokens_used", token_count)
track_metric("user_satisfaction", thumbs_up)
```

---

## 🎨 Part 3: Common Architecture Patterns

### Pattern 1: Simple RAG

**Use Case:** Basic Q&A bot

```
User Question
    ↓
Retrieve relevant docs (Vector DB)
    ↓
Add to prompt
    ↓
LLM generates answer
    ↓
Return response
```

**Pros:**

- ✅ Simple to build
- ✅ Easy to understand
- ✅ Fast to iterate

**Cons:**

- ❌ Limited reasoning
- ❌ No multi-step tasks
- ❌ Single knowledge source

---

### Pattern 2: Multi-Source RAG

**Use Case:** Research assistant, comprehensive Q&A

```
User Question
    ↓
Query multiple sources in parallel:
    - Vector DB (semantic search)
    - Graph DB (relationship queries)
    - SQL DB (structured data)
    ↓
Combine & rank results
    ↓
LLM generates answer
```

**Pros:**

- ✅ Comprehensive answers
- ✅ Multiple perspectives
- ✅ Rich context

**Cons:**

- ❌ More complex
- ❌ Slower
- ❌ Need to merge results

---

### Pattern 3: Agentic Workflow

**Use Case:** Complex tasks, multi-step reasoning

```
User Task
    ↓
Planner Agent: Creates execution plan
    ↓
Executor Agents: Each handles a step
    - Retriever: Gets information
    - Analyzer: Processes data
    - Summarizer: Creates output
    ↓
Coordinator: Combines results
    ↓
Final output
```

**Pros:**

- ✅ Handles complex tasks
- ✅ Can use tools
- ✅ Self-correcting

**Cons:**

- ❌ Expensive (many LLM calls)
- ❌ Unpredictable
- ❌ Hard to debug

---

### Pattern 4: Hybrid (Best of All)

**Use Case:** Production systems, enterprise applications

```
User Request
    ↓
API Gateway (auth, routing)
    ↓
Request Classifier: Determines complexity
    ↓
Simple query → Simple RAG (fast, cheap)
Complex query → Multi-source RAG + Agents
    ↓
Response with source citations
    ↓
Monitoring & feedback loop
```

**Pros:**

- ✅ Optimized for each query type
- ✅ Cost-efficient
- ✅ Scalable

**Cons:**

- ❌ Most complex to build
- ❌ More components to maintain

---

## 📊 Part 4: Making Architecture Decisions

### Decision Framework

For each component, ask:

1. **What problem does it solve?**
   - If no clear problem → Don't add it

2. **What are the alternatives?**
   - Compare 2-3 options

3. **What are the trade-offs?**
   - Cost vs. features
   - Complexity vs. control
   - Speed vs. accuracy

4. **What's the simplest solution?**
   - Start simple, add complexity only when needed

### Example Decision Process

**Question:** Should we use a vector database?

**Analysis:**

- Problem: Need to search 10,000 documents for relevant context
- Alternatives:
  1. Keyword search (fast, but misses semantics)
  2. Vector DB (semantic, but costs money)
  3. Read all docs each time (accurate, but way too slow)
- Trade-offs:
  - Vector DB adds cost but needed for quality
- Decision: Yes, use vector DB (Chroma for prototype, Pinecone for production)

---

## 🎯 Part 5: Architecture Best Practices

### 1. Start Simple

**Don't:**

```
❌ Start with 10 microservices
❌ Use every tool and framework
❌ Over-engineer for scale you don't have
```

**Do:**

```
✅ Start with monolith
✅ Add complexity only when needed
✅ Prove value first, scale later
```

---

### 2. Decouple Components

**Bad (Tightly Coupled):**

```python
# UI directly calls LLM
response = openai.chat(user_input)
```

**Good (Decoupled):**

```python
# UI → API → Service → LLM
response = api_client.query(user_input)
```

**Why?**

- Easy to swap LLM providers
- Can add caching layer
- Testable in isolation

---

### 3. Design for Observability

**Build monitoring in from day one:**

```python
@track_metrics
def generate_response(query):
    start = time.time()

    # Retrieve
    docs = retrieve(query)
    log_metric("retrieval_time", time.time() - start)

    # Generate
    response = llm.generate(query, docs)
    log_metric("generation_time", time.time() - start)
    log_metric("tokens_used", response.tokens)

    return response
```

---

### 4. Handle Failures Gracefully

**LLMs can fail!** Design for it:

```python
def generate_with_fallback(query):
    try:
        # Try GPT-4
        return gpt4.generate(query)
    except RateLimitError:
        # Fall back to GPT-3.5
        return gpt35.generate(query)
    except Exception:
        # Return helpful error
        return "I'm having trouble right now. Please try again."
```

---

### 5. Cost Management

**LLM costs add up fast!**

**Strategies:**

1. **Cache responses** - Same question = Same answer
2. **Use cheaper models** - GPT-3.5 for simple tasks
3. **Truncate context** - Only include relevant parts
4. **Batch requests** - Process multiple at once
5. **Monitor usage** - Set alerts on spend

**Example:**

```python
# Check cache first
cached = cache.get(query_hash)
if cached:
    return cached  # Free!

# Only call LLM if not cached
response = llm.generate(query)
cache.set(query_hash, response)
```

---

## 📐 Part 6: How to Draw Architecture Diagrams

### Diagramming Best Practices

**1. Use Standard Symbols**

- Rectangles = Services/Components
- Cylinders = Databases
- Clouds = External services
- Arrows = Data flow

**2. Left-to-Right or Top-to-Bottom Flow**

```
User → Frontend → API → Backend → Database
```

**3. Group Related Components**

```
┌─────────────────────────────┐
│  RAG Layer                  │
│  ┌──────┐  ┌──────┐        │
│  │Vector│  │Graph │        │
│  │  DB  │  │  DB  │        │
│  └──────┘  └──────┘        │
└─────────────────────────────┘
```

**4. Label Everything**

- Component names
- Connection types (REST, gRPC, etc.)
- Technologies used

**5. Include Legends**

```
Solid line   = Synchronous call
Dashed line  = Asynchronous
Red arrow    = Error path
```

---

### Tools for Diagramming

**1. draw.io (Recommended)**

- ✅ Free
- ✅ Works in browser
- ✅ Lots of shapes
- ✅ Export to PNG/PDF

**2. Mermaid (Code-based)**

- ✅ Version control friendly
- ✅ Fast for simple diagrams
- ✅ Renders in GitHub
- ❌ Less flexible

**3. Lucidchart (Premium)**

- ✅ Collaborative
- ✅ Professional templates
- ❌ Costs money

**4. Excalidraw (Sketchy style)**

- ✅ Quick sketches
- ✅ Hand-drawn aesthetic
- ❌ Less professional

---

## 💼 Part 7: Communicating Architecture to Stakeholders

### To Executives (Non-Technical)

**Focus on:**

- Business value
- ROI (return on investment)
- Time to market
- Risk mitigation

**Example:**

```
"This architecture will:
- Reduce customer support costs by 40%
- Answer 80% of questions automatically
- Launch in 6 weeks
- Scale to handle growth"
```

**Use analogies:**

```
❌ "We'll use a graph database with SPARQL"
✅ "Think of it like a smart filing system that understands relationships"
```

---

### To Engineers (Technical)

**Focus on:**

- Technology choices
- Scalability
- Trade-offs
- Implementation details

**Example:**

```
"Architecture decisions:
1. FastAPI for API (async, type-safe)
2. Pinecone for vectors (managed, scales)
3. PostgreSQL for app data (ACID, familiar)
4. Docker + Fargate (containers, serverless)

Trade-offs:
- Pinecone costs more but saves dev time
- Fargate simpler than K8s but less control"
```

---

### To Product Managers

**Focus on:**

- Features enabled
- Timeline
- Resource needs
- Risks and mitigation

**Example:**

```
"Architecture supports:
✅ Feature 1: Smart search (Week 2)
✅ Feature 2: Recommendations (Week 4)
✅ Feature 3: Analytics (Week 6)

Risks:
- LLM cost could exceed budget
  → Mitigation: Caching + cheaper model fallback
```

---

## 🎓 Summary: Key Takeaways

### Architecture is About Trade-offs

Every decision involves trade-offs:

- Simple vs. Powerful
- Fast vs. Accurate
- Cheap vs. Feature-rich
- Flexible vs. Performant

**Good architects:**

- Understand the options
- Know the trade-offs
- Make informed decisions
- Document the reasoning

---

### Start Simple, Then Scale

**Phase 1: Prototype**

- FastAPI + OpenAI + Chroma
- Proves concept quickly

**Phase 2: Production**

- Add auth, monitoring, caching
- Switch to Pinecone for scale

**Phase 3: Enterprise**

- Multi-region deployment
- Advanced security
- Custom models

---

### Understand Your Use Case

Different use cases need different architectures:

**Simple Q&A:**

- Vector DB + LLM = Done

**Complex Analysis:**

- Multi-source RAG + Agents

**Real-time Chat:**

- Streaming responses
- Low latency critical

**Batch Processing:**

- Process millions of docs
- Throughput over latency

---

**You're now ready to design your own GenAI architecture!** 🚀
