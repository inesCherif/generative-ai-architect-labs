# 🧠 GenAI-RAG Architecture Lab

## 📚 What is This Project?

This is a complete, beginner-friendly implementation of a **RAG (Retrieval-Augmented Generation)** system. It's an AI that doesn't just guess answers—it looks up facts in your documents first!

### What You'll Learn

✅ How RAG works (concepts + code)
✅ Vector databases and embeddings
✅ Building a Q&A system from scratch
✅ Integrating LLMs (Large Language Models)
✅ Software architecture and documentation

## 🎯 What is RAG?

**RAG = Retrieval-Augmented Generation**

Traditional AI:

```
Question → AI → Answer (might be wrong!)
```

RAG AI:

```
Question → Search Documents → AI reads docs → Accurate Answer!
```

### Why RAG?

- ✅ **Accurate**: Answers based on your documents
- ✅ **Up-to-date**: Add new documents anytime
- ✅ **Transparent**: Can cite sources
- ✅ **Specialized**: Works with your specific domain knowledge

## 🏗️ Architecture

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ Question
       ▼
┌─────────────┐
│  RAG Engine │
└──────┬──────┘
       │
       ├─► 1. Convert question to vector (embedding)
       │
       ├─► 2. Search vector database
       │      ↓
       │   ┌──────────────┐
       │   │ Vector Store │ (FAISS)
       │   │  - doc1      │
       │   │  - doc2      │
       │   │  - doc3      │
       │   └──────────────┘
       │      ↓
       ├─► 3. Get top 3 most relevant docs
       │
       ├─► 4. Send docs + question to LLM
       │      ↓
       │   ┌──────────────┐
       │   │   OpenAI     │
       │   │   GPT-3.5    │
       │   └──────────────┘
       │      ↓
       └─► 5. Get smart answer!
```

## 📁 Project Structure

```
lab9_document_genAI-RAG_architecture/
├── data/                          # Your documents
│   ├── document1_rag.txt
│   ├── document2_vectordb.txt
│   ├── document3_llms.txt
│   └── document4_embeddings.txt
│
├── src/                           # Python code
│   ├── config.py                  # Configuration & settings
│   ├── document_loader.py         # Load & split documents
│   ├── embeddings.py              # Convert text → vectors
│   ├── vector_store.py            # FAISS database
│   ├── llm.py                     # OpenAI integration
│   └── rag_pipeline.py            # Main RAG system
│
├── diagrams/                      # Architecture diagrams
│   ├── architecture.md            # Mermaid diagram
│   └── architecture.html          # Visual diagram
│
├── docs/                          # Documentation
│   └── jira_guide.md              # JIRA setup guide
│
├── requirements.txt               # Python packages
├── .env                           # API keys (SECRET!)
└── README.md                      # This file!
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (get from https://platform.openai.com/api-keys)

### Step 1: Clone or Download

```bash
cd lab9_document_genAI-RAG_architecture
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `langchain`: RAG framework
- `faiss-cpu`: Vector database
- `sentence-transformers`: Create embeddings (LOCAL, FREE!)
- `openai`: GPT integration
- And more!

### Step 4: Set Up API Key

Edit `.env` file:

```
OPENAI_API_KEY=your-actual-api-key-here
```

Get your key from: https://platform.openai.com/api-keys

### Step 5: Run the Pipeline!

```bash
cd src
python rag_pipeline.py
```

Choose option 3: "Build and then start interactive Q&A"

## 💬 Example Usage

```
You: What is RAG?

🔄 Creating question embedding...
🔍 Searching for top 3 relevant documents...
🤖 Generating answer with LLM...

💡 ANSWER:
RAG (Retrieval-Augmented Generation) is an AI framework that
combines large language models with external knowledge retrieval.
Instead of relying only on training data, RAG systems search
through documents to find relevant information, then use that
context to generate accurate, grounded responses.
```

## 📊 Understanding the Components

### 1. Document Loader (`document_loader.py`)

**What it does:**

- Reads .txt files from `data/` folder
- Splits long documents into chunks
- Preserves metadata (filename, chunk number)

**Why split documents?**

- Embeddings work better on focused text
- LLMs have context limits
- More precise retrieval

### 2. Embeddings (`embeddings.py`)

**What it does:**

- Converts text into vectors (lists of numbers)
- Uses `sentence-transformers` (runs locally!)

**Example:**

```python
"dog" → [0.2, 0.8, -0.3, 0.5, ...]
"puppy" → [0.25, 0.82, -0.28, 0.48, ...]  # Similar!
"car" → [-0.6, 0.1, 0.9, -0.2, ...]       # Different!
```

### 3. Vector Store (`vector_store.py`)

**What it does:**

- Stores embeddings in FAISS database
- Finds similar documents FAST
- Saves/loads to disk

**How it works:**

1. Store: `doc_embedding → database`
2. Search: `query_embedding → find similar → return top K`

### 4. LLM (`llm.py`)

**What it does:**

- Talks to OpenAI's GPT models
- Combines retrieved docs + question
- Generates intelligent answers

### 5. RAG Pipeline (`rag_pipeline.py`)

**What it does:**

- Orchestrates everything!
- Build index, query, interactive mode

## 🧪 Testing Individual Components

Each file can run independently for testing:

```bash
# Test embeddings
python embeddings.py

# Test document loader
python document_loader.py

# Test vector store
python vector_store.py

# Test LLM (requires API key)
python llm.py
```

## 🎨 View Architecture Diagram

Open in your browser:

```
diagrams/architecture.html
```

## 📈 Monitoring & Performance

The pipeline shows:

- Documents loaded
- Embeddings created
- Search results with similarity scores
- Response generation time

## 🔧 Configuration

Edit `src/config.py` to change:

- Embedding model
- LLM model (GPT-3.5 vs GPT-4)
- Chunk size
- Number of results (top_k)
- Temperature (creativity)

## 📖 Learning Resources

### Concepts Covered

1. **Embeddings**: Text → numbers that capture meaning
2. **Vector Databases**: Store and search embeddings
3. **Similarity Search**: Find related documents
4. **Prompt Engineering**: Structure LLM inputs
5. **RAG Architecture**: Combine retrieval + generation

### Next Steps

- Add more documents to `data/`
- Experiment with different chunk sizes
- Try different embedding models
- Adjust LLM temperature
- Add PDF support
- Build a web interface

## 🐛 Troubleshooting

### "No module named 'faiss'"

```bash
pip install faiss-cpu
```

### "OpenAI API key not found"

1. Get key from https://platform.openai.com/api-keys
2. Add to `.env` file: `OPENAI_API_KEY=sk-...`
3. Make sure `.env` is in project root

### "No documents found"

- Add .txt files to `data/` folder
- Check file permissions

### Vector database errors

```bash
# Delete and rebuild
rm -rf vector_db/
python rag_pipeline.py
# Choose option 1 to rebuild
```

## 💡 Tips for Best Results

1. **Good documents** = good answers
   - Clear, well-written content
   - Focused topics
   - Avoid very long paragraphs

2. **Chunk size matters**
   - Too small: Loses context
   - Too large: Less precise
   - 300-500 chars is usually good

3. **Ask specific questions**
   - Good: "What is RAG and why is it useful?"
   - Less good: "Tell me about AI"

## 🎓 Lab Deliverables

✅ Architecture diagram (Mermaid + HTML)
✅ Working RAG pipeline code
✅ Sample documents
✅ Documentation
✅ JIRA project guide

## 📝 License

Educational project - free to use and modify!

## 🙋 Support

Having issues? Check:

1. All packages installed? `pip list`
2. API key set? Check `.env`
3. Documents in `data/` folder?
4. Python 3.8+? `python --version`

---
