# Lab 5 — Multi-Agent System with LangGraph

A hands-on lab that teaches you to build a **multi-agent AI system** from
the ground up — from first principles to a live interactive chat.

## What You Build

Three specialised AI agents that work together:

| Agent          | Job                                             | Uses       |
| -------------- | ----------------------------------------------- | ---------- |
| **Planner**    | Turns your question into a focused search query | LLM        |
| **Retriever**  | Searches the web for information                | DuckDuckGo |
| **Summariser** | Turns raw results into a clean answer           | LLM        |

A **Router** watches the Retriever's output and retries automatically if
the search fails — this is called a _conditional edge_ and it is what
makes a graph more powerful than a simple chain.

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (Mac: source venv/bin/activate)
pip install langgraph langchain openai faiss-cpu duckduckgo-search
cp .env.template .env          # add your OpenAI key inside
```

Then run scripts **in order**:

```bash
python 01_concepts.py
python 02_setup_tools_and_memory.py
python 03_define_agents.py
python 04_build_graph.py
python 05_conditional_edge.py
python 06_full_interactive.py   # ← interactive chat (type 'quit' to exit)
```

For detailed guidance read **QUICK_START.md**. For visual diagrams read
**VISUAL_GUIDE.md**.

## Technologies

| Library             | Role                                    |
| ------------------- | --------------------------------------- |
| `langgraph`         | Orchestrates the multi-agent graph      |
| `langchain`         | Prompt templates, memory, tool wrappers |
| `langchain-openai`  | LangChain's OpenAI integration          |
| `openai`            | The GPT-4 API                           |
| `duckduckgo-search` | Free web search (no key needed)         |

## Project Layout

```
lab5_multi_agent_system/
├── README.md                       ← this file
├── QUICK_START.md                  ← step-by-step setup guide
├── VISUAL_GUIDE.md                 ← architecture diagrams
├── requirements.txt                ← Python packages
├── .env.template                   ← copy → .env, add key
├── 01_concepts.py                  ← core ideas (no API needed)
├── 02_setup_tools_and_memory.py    ← LLM + Search + Memory
├── 03_define_agents.py             ← write the three agents
├── 04_build_graph.py               ← wire into LangGraph
├── 05_conditional_edge.py          ← add retry logic
└── 06_full_interactive.py          ← the finished interactive system
```
