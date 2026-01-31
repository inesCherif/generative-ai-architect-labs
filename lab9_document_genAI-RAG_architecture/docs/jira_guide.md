# 📋 JIRA Project Guide: GenAI-RAG Support Assistant

## 🎯 Overview

This guide walks you through creating a JIRA project to manage the development of a GenAI-RAG (Retrieval-Augmented Generation) system. We'll set up epics, stories, tasks, sprints, and a roadmap.

## 🚀 Part 1: Create JIRA Project

### Step 1: Access JIRA

1. Go to https://www.atlassian.com/software/jira/free
2. Sign up for a free account (if needed)
3. Or use your organization's JIRA instance

### Step 2: Create New Project

1. Click **"Create Project"** button
2. Select **"Scrum"** template
   - Why Scrum? Supports sprints, backlogs, and roadmaps
3. Name your project: **"GenAI RAG Support Assistant"**
4. Key: **"RAG"** (this becomes your issue prefix, e.g., RAG-1, RAG-2)
5. Click **"Create"**

## 📊 Part 2: Set Up Epics

Epics are high-level features or modules. We'll create 5 epics matching our architecture.

### How to Create an Epic

1. Go to **Backlog** view
2. Click **"Create"** → Select **"Epic"**
3. Fill in the details

### Epic 1: Build RAG Pipeline

```
Epic Name: Build RAG Pipeline
Epic Key: RAG-EPIC-1
Description:
Develop the core RAG pipeline including document loading,
text chunking, embedding creation, and vector storage.

Components:
- Document loader
- Text chunking
- Embedding model integration
- Vector database (FAISS)

Acceptance Criteria:
✅ Can load .txt documents from data folder
✅ Documents split into appropriate chunks
✅ Embeddings created and stored in vector DB
✅ Can search and retrieve relevant documents
```

### Epic 2: Integrate Knowledge Graph (Optional)

```
Epic Name: Integrate Knowledge Graph
Epic Key: RAG-EPIC-2
Description:
Add optional knowledge graph support for structured data
and relationship-based retrieval using SPARQL queries.

Components:
- Knowledge graph database (Neo4j or Stardog)
- SPARQL query templates
- Graph + vector hybrid search

Acceptance Criteria:
✅ Knowledge graph database set up
✅ Can execute SPARQL queries
✅ Hybrid search combines vector + graph results

Priority: LOW (Optional enhancement)
```

### Epic 3: LLM Integration & Prompt Engineering

```
Epic Name: LLM Integration & Prompt Engineering
Epic Key: RAG-EPIC-3
Description:
Integrate Large Language Model (OpenAI GPT) and optimize
prompts for accurate, grounded responses.

Components:
- OpenAI API integration
- Prompt template design
- Context building
- Response formatting

Acceptance Criteria:
✅ OpenAI API successfully integrated
✅ Prompts include retrieved context
✅ Responses cite source documents
✅ Temperature and parameters optimized
```

### Epic 4: Deploy on Cloud (AWS)

```
Epic Name: Cloud Deployment
Epic Key: RAG-EPIC-4
Description:
Deploy the RAG system to AWS using containerization
and serverless/container services.

Components:
- Dockerization
- AWS Fargate / ECS deployment
- API Gateway setup
- Environment configuration

Acceptance Criteria:
✅ Application containerized with Docker
✅ Deployed to AWS Fargate/ECS
✅ API accessible via public endpoint
✅ Environment variables properly configured
```

### Epic 5: Monitoring & Evaluation

```
Epic Name: Monitoring & Evaluation
Epic Key: RAG-EPIC-5
Description:
Implement monitoring, logging, and evaluation metrics
to track system performance and quality.

Components:
- CloudWatch / Prometheus logging
- Performance metrics
- Response quality evaluation
- Cost tracking

Acceptance Criteria:
✅ Logs collected and queryable
✅ Performance metrics tracked (latency, tokens)
✅ Response quality measured
✅ Alerts configured for errors
```

## 📝 Part 3: Create Stories and Tasks

Stories are user-facing features. Tasks are technical work items.

### Example: Epic 1 - Build RAG Pipeline

#### Story RAG-1: Document Loading System

```
Type: Story
Epic: Build RAG Pipeline
Story Points: 3
Priority: High

As a developer
I want to load documents from a data folder
So that they can be processed by the RAG system

Description:
Create a document loader that can read .txt files,
extract content, and preserve metadata.

Acceptance Criteria:
✅ Reads all .txt files from specified directory
✅ Handles errors gracefully
✅ Extracts metadata (filename, size, date)
✅ Returns Document objects with content + metadata

Tasks:
- [ ] Create DocumentLoader class
- [ ] Implement file reading logic
- [ ] Add metadata extraction
- [ ] Write unit tests
- [ ] Create sample test documents
```

#### Story RAG-2: Text Chunking

```
Type: Story
Epic: Build RAG Pipeline
Story Points: 5
Priority: High

As a developer
I want documents split into smaller chunks
So that embeddings are more focused and retrieval is precise

Description:
Implement intelligent text chunking with overlap to
prevent breaking sentences.

Acceptance Criteria:
✅ Splits text into configurable chunk sizes
✅ Maintains overlap between chunks
✅ Breaks at sentence boundaries when possible
✅ Preserves chunk metadata

Tasks:
- [ ] Implement chunking algorithm
- [ ] Add sentence boundary detection
- [ ] Make chunk size configurable
- [ ] Test with various document types
- [ ] Optimize chunk overlap
```

#### Story RAG-3: Embedding Creation

```
Type: Story
Epic: Build RAG Pipeline
Story Points: 5
Priority: High

As a developer
I want to convert text chunks into embeddings
So that semantic similarity search is possible

Description:
Integrate sentence-transformers to create embeddings
from text chunks.

Acceptance Criteria:
✅ Embeddings created using sentence-transformers
✅ Batch processing for efficiency
✅ Consistent vector dimensions
✅ Progress tracking for large datasets

Tasks:
- [ ] Set up sentence-transformers
- [ ] Create EmbeddingModel class
- [ ] Implement batch processing
- [ ] Add progress bars
- [ ] Test embedding quality
```

#### Story RAG-4: Vector Database Setup

```
Type: Story
Epic: Build RAG Pipeline
Story Points: 8
Priority: High

As a developer
I want to store embeddings in a vector database
So that I can quickly find similar documents

Description:
Implement FAISS vector store for embedding storage
and similarity search.

Acceptance Criteria:
✅ FAISS index created and populated
✅ Can add documents to index
✅ Similarity search returns top-k results
✅ Can save/load index from disk

Tasks:
- [ ] Set up FAISS
- [ ] Create VectorStore class
- [ ] Implement add_documents method
- [ ] Implement search method
- [ ] Add save/load functionality
- [ ] Write integration tests
```

### Example: Epic 3 - LLM Integration

#### Story RAG-10: OpenAI Integration

```
Type: Story
Epic: LLM Integration & Prompt Engineering
Story Points: 5
Priority: High

As a developer
I want to integrate OpenAI's GPT models
So that the system can generate intelligent responses

Description:
Set up OpenAI API client and create LLM wrapper class.

Acceptance Criteria:
✅ OpenAI client configured with API key
✅ Can send prompts and receive responses
✅ Error handling for API failures
✅ Configurable temperature and max_tokens

Tasks:
- [ ] Install openai package
- [ ] Create LLM class
- [ ] Implement API call logic
- [ ] Add error handling
- [ ] Create configuration options
- [ ] Test with sample prompts
```

#### Story RAG-11: Prompt Engineering

```
Type: Story
Epic: LLM Integration & Prompt Engineering
Story Points: 5
Priority: High

As a developer
I want well-engineered prompts
So that the LLM generates accurate, grounded responses

Description:
Design prompt templates that effectively combine
retrieved context with user questions.

Acceptance Criteria:
✅ Prompt includes retrieved documents
✅ Instructions encourage source citation
✅ Format optimized for GPT models
✅ Handles cases with no relevant context

Tasks:
- [ ] Research prompt engineering best practices
- [ ] Design prompt template
- [ ] Test various prompt structures
- [ ] Implement context building
- [ ] Validate output quality
```

## 🏃 Part 4: Create Sprints

Sprints are 2-week development cycles.

### How to Create a Sprint

1. Go to **Backlog**
2. Click **"Create Sprint"**
3. Name it: **"Sprint 1: RAG Pipeline Foundation"**
4. Drag stories into the sprint

### Sprint 1: RAG Pipeline Foundation (Week 1-2)

**Goals:**

- Set up project structure
- Implement document loading
- Create embeddings
- Basic vector store

**Stories:**

- RAG-1: Document Loading System
- RAG-2: Text Chunking
- RAG-3: Embedding Creation

**Total Story Points:** 13

### Sprint 2: Vector Search & Testing (Week 3-4)

**Goals:**

- Complete vector database
- Implement search
- Write tests

**Stories:**

- RAG-4: Vector Database Setup
- RAG-5: Search Implementation
- RAG-6: Unit Testing

**Total Story Points:** 15

### Sprint 3: LLM Integration (Week 5-6)

**Goals:**

- OpenAI integration
- Prompt engineering
- End-to-end pipeline

**Stories:**

- RAG-10: OpenAI Integration
- RAG-11: Prompt Engineering
- RAG-12: Complete Pipeline

**Total Story Points:** 13

### Sprint 4: Cloud Deployment (Week 7-8)

**Goals:**

- Dockerize application
- Deploy to AWS
- Set up API

**Stories:**

- RAG-20: Docker Setup
- RAG-21: AWS Deployment
- RAG-22: API Configuration

**Total Story Points:** 18

### Sprint 5: Monitoring & Polish (Week 9-10)

**Goals:**

- Add monitoring
- Optimize performance
- Documentation

**Stories:**

- RAG-30: CloudWatch Integration
- RAG-31: Performance Optimization
- RAG-32: Documentation

**Total Story Points:** 10

## 📅 Part 5: Set Up Roadmap

The roadmap shows timeline and milestones.

### How to Access Roadmap

1. Go to **Roadmap** tab in JIRA
2. Drag epics to timeline
3. Add dependencies

### Milestones

**Week 2: Vector DB Operational**

- ✅ Documents loaded and chunked
- ✅ Embeddings created
- ✅ Vector search working

**Week 4: RAG Pipeline Complete**

- ✅ End-to-end pipeline functional
- ✅ Can query and get retrieved context

**Week 6: LLM Integration Done**

- ✅ OpenAI integrated
- ✅ Generating responses
- ✅ Source citation working

**Week 8: Cloud Deployment**

- ✅ Deployed to AWS
- ✅ API accessible
- ✅ Production ready

**Week 10: Monitoring Active**

- ✅ Logs and metrics collected
- ✅ Performance optimized
- ✅ Documentation complete

## 🎯 Part 6: Configure Board

### Columns

Set up your board with these columns:

1. **Backlog** - Not yet started
2. **To Do** - Ready for sprint
3. **In Progress** - Currently working
4. **Code Review** - Awaiting review
5. **Testing** - In QA
6. **Done** - Completed

### Swim Lanes

Organize by:

- Epic
- Assignee
- Priority

## 📊 Part 7: Track Progress

### Story Points

Estimate complexity:

- **1-2 points**: Simple task (few hours)
- **3-5 points**: Medium task (1-2 days)
- **8-13 points**: Complex task (3-5 days)

### Burndown Chart

1. Go to **Reports**
2. Select **Sprint Burndown**
3. Track remaining story points

### Velocity

After each sprint:

- Record completed story points
- Calculate average velocity
- Use for future planning

## 📋 Sample Board State

```
┌─────────────┬──────────────┬─────────────┬──────────────┬─────┐
│  Backlog    │   To Do      │ In Progress │ Code Review  │ Done│
├─────────────┼──────────────┼─────────────┼──────────────┼─────┤
│ RAG-6       │ RAG-2        │ RAG-1       │ RAG-3        │     │
│ RAG-11      │ RAG-4        │             │              │     │
│ RAG-20      │              │             │              │     │
└─────────────┴──────────────┴─────────────┴──────────────┴─────┘
```

## 🎓 Best Practices

1. **Keep stories small** - 3-5 points ideal
2. **Update daily** - Move cards as you work
3. **Add comments** - Document decisions
4. **Link PRs** - Connect code to stories
5. **Review retrospectives** - Learn and improve

## 📸 Screenshots to Include

When submitting:

1. JIRA board with epics
2. Sprint backlog
3. Roadmap view
4. Burndown chart
5. Completed sprint report

---
