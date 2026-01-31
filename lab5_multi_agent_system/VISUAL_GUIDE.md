# 🎨 Visual Guide — Lab 5 Multi-Agent System

Every concept in this lab explained with diagrams. Read this BEFORE or
ALONGSIDE the scripts — it will make everything click.

---

## 1. The Big Picture — What Are We Building?

```
  You type a question
         │
         ▼
  ┌─────────────┐
  │   Planner   │   ← "What should I search for?"
  └──────┬──────┘
         │  search query
         ▼
  ┌─────────────┐
  │  Retriever  │   ← "Let me look that up."     (calls DuckDuckGo)
  └──────┬──────┘
         │  raw results
         ▼
  ┌─────────────┐     ┌─────┐
  │   Router    │────▶│ END │   ← "Did that work?"
  └──────┬──────┘     └─────┘     If not → loop back to Planner
         │  (yes, it worked)
         ▼
  ┌─────────────┐
  │ Summariser  │   ← "Let me clean this up for you."
  └──────┬──────┘
         │  polished answer
         ▼
     You read it
```

---

## 2. LangChain vs LangGraph vs OpenAI SDK — When to Use Which

```
  ┌─────────────────────────────────────────────────────────────┐
  │                        OpenAI SDK                           │
  │                                                             │
  │   client.chat.completions.create(…)                         │
  │                                                             │
  │   Use when:  You just want to call GPT-4.                   │
  │              No agents.  No tools.  No memory.              │
  │              The simplest possible LLM call.                │
  └─────────────────────────────────────────────────────────────┘
                              ▲
                              │  LangChain wraps this
                              ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                       LangChain                             │
  │                                                             │
  │   ChatOpenAI(…)           → swappable LLM wrapper           │
  │   PromptTemplate(…)       → reusable prompt with variables  │
  │   LLMChain(…)             → prompt + LLM glued together     │
  │   ConversationBufferMemory → stores conversation history    │
  │   Tool(…)                 → wraps any function for the LLM  │
  │                                                             │
  │   Use when:  You want ONE chain of steps.                   │
  │              You want to swap LLM providers easily.         │
  │              You want memory or tool wrappers.              │
  └─────────────────────────────────────────────────────────────┘
                              ▲
                              │  LangGraph builds on this
                              ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                       LangGraph                             │
  │                                                             │
  │   StateGraph(…)           → the graph container             │
  │   .add_node(name, fn)     → register an agent function      │
  │   .add_edge(a, b)         → "after a, run b"                │
  │   .add_conditional_edge() → "after a, DECIDE what's next"   │
  │   .compile()              → lock and validate the graph     │
  │   .invoke(state)          → run the whole pipeline          │
  │                                                             │
  │   Use when:  You have MULTIPLE agents.                      │
  │              You need branching or looping.                 │
  │              You want structured, debuggable workflows.     │
  │              THIS IS WHAT WE USE IN THIS LAB.               │
  └─────────────────────────────────────────────────────────────┘

  Hierarchy:   OpenAI SDK  ⊂  LangChain  ⊂  LangGraph
               (bare bones)              (full power)
```

---

## 3. What Is a "Chain"? (LangChain's core unit)

```
  INPUT
    │
    ▼
  ┌──────────────┐
  │ PromptTemplate│   "You are a helpful assistant. Answer: {question}"
  │  (fills in    │        ↓ fills {question} with the actual input
  │   variables)  │   "You are a helpful assistant. Answer: What is AI?"
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │   ChatOpenAI │   Sends the prompt to GPT-4 → gets a response
  └──────┬───────┘
         │
         ▼
  OUTPUT (the LLM's answer)

  A Chain is just these two boxes connected.  LLMChain does this for you.
```

---

## 4. What Is a "Graph"? (LangGraph's core unit)

```
  A CHAIN (linear — no decisions):

    A  ──▶  B  ──▶  C  ──▶  END
    (can only go forward)


  A GRAPH (can branch and loop):

              ┌──────┐
    A  ──▶  B  ──▶  C  ──▶  END
              │              ▲
              │ (retry)      │
              └──────────────┘
    (can go backward if B fails!)


  LangGraph is a GRAPH, not a chain.
  That is its entire reason for existing.
```

---

## 5. What Is "State"? (The agents' shared clipboard)

```
  State is a dictionary that flows through every node.
  Each agent reads what it needs and writes what it produces.

  ┌─────────────────────────────────────────────────────┐
  │  state = {                                          │
  │    "input":           "What is Mars exploration?"   │  ← set by user
  │    "planner_output":  "Mars exploration 2025 news"  │  ← set by Planner
  │    "retrieved_info":  "NASA announced …"            │  ← set by Retriever
  │    "final_output":    "Based on reports …"          │  ← set by Summariser
  │    "retries":         0                             │  ← retry counter
  │  }                                                  │
  └─────────────────────────────────────────────────────┘

  Think of it as a baton in a relay race.
  Each runner (agent) grabs it, adds their contribution, passes it on.
```

---

## 6. What Is a "Tool"?

```
  A Tool = a Python function + a name + a description.

  ┌─────────────────────────────────────────────────┐
  │  Tool(                                          │
  │    name        = "WebSearch"                    │  ← identifier
  │    func        = search.run                     │  ← the actual function
  │    description = "Searches the web for info"    │  ← LLM reads THIS
  │  )                                              │     to know when to use it
  └─────────────────────────────────────────────────┘

  In our lab, the Retriever calls search.run(query) directly.
  The Tool wrapper is shown for completeness — in more advanced setups
  the LLM itself decides which tool to call.

  Other tools you could add later:
    • Calculator      → math questions
    • CodeExecutor    → run Python snippets
    • DatabaseQuery   → SQL lookups
    • RAG Retriever   → your own vector database (from Lab 4!)
```

---

## 7. What Is "Memory"?

```
  LLMs forget everything between calls.  Memory fixes that.

  Without memory:
    Call 1: "What is AI?"        → "AI is …"
    Call 2: "Tell me more."      → "I don't know what you mean."  ❌

  With memory:
    Call 1: "What is AI?"        → "AI is …"
           (memory stores both messages)
    Call 2: "Tell me more."      → "Sure!  As I mentioned, AI …"  ✅

  ConversationBufferMemory stores every Human + AI message.
  In our graph, each agent logs its work to memory so the whole
  conversation is traceable at the end.
```

---

## 8. The Conditional Edge — How Retry Works

```
  After the Retriever runs, the Router checks the results:

  ┌──────────────────────────────────────────────────────┐
  │                                                      │
  │   Retriever done                                     │
  │       │                                              │
  │       ▼                                              │
  │   ┌────────────┐                                     │
  │   │   Router   │   checks: are results useful?       │
  │   └─────┬──────┘                                     │
  │         │                                            │
  │    ┌────┴────┐                                       │
  │    │         │                                       │
  │    ▼         ▼                                       │
  │  GOOD      BAD                                       │
  │    │         │                                       │
  │    ▼         ▼                                       │
  │ Summariser  Planner  ← retry with a different query  │
  │    │         │                                       │
  │    ▼         │                                       │
  │   END        └── (loop back, try again)              │
  │                                                      │
  │   After MAX_RETRIES (2) bad results → END with error │
  └──────────────────────────────────────────────────────┘

  The Router is just a function:
      def router(state) -> str:
          if results_are_bad:
              return "planner"    # loop
          else:
              return "summarize"  # continue
```

---

## 9. How Each Agent's Prompt Differs

```
  Each agent gets a FOCUSED prompt — that is why they work well.

  ┌──────────────────────────────────────────────────────────────┐
  │  PLANNER prompt:                                             │
  │  "Your ONLY job is to rewrite the question into a search     │
  │   query.  Do NOT answer — only produce the query."           │
  │                                                              │
  │  Why: Forces the LLM to think about searchability, not       │
  │       to answer directly.                                    │
  └──────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────┐
  │  RETRIEVER:  No LLM prompt needed!                           │
  │  It just calls search.run(query) — a Python function.        │
  │                                                              │
  │  Why: Searching is a mechanical action, not a thinking one.  │
  └──────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────┐
  │  SUMMARISER prompt:                                          │
  │  "Synthesise these raw results into a clear, concise answer  │
  │   (3-5 sentences)."                                          │
  │                                                              │
  │  Why: Forces the LLM to distil and organise — exactly what   │
  │       it is best at.                                         │
  └──────────────────────────────────────────────────────────────┘
```

---

## 10. Demo Mode vs Live Mode

```
  Every script has TWO paths:

  ┌─────────────────────┐     ┌─────────────────────┐
  │     LIVE MODE       │     │     DEMO MODE       │
  │  (API key present)  │     │  (no API key)       │
  ├─────────────────────┤     ├─────────────────────┤
  │ LLM   → real GPT-4  │     │ LLM   → canned text │
  │ Search → DuckDuckGo │     │ Search → fake data  │
  │ Output → real answer│     │ Output → demo text  │
  └─────────────────────┘     └─────────────────────┘

  Demo mode teaches you the STRUCTURE and FLOW.
  Live mode gives you REAL answers.

  Both paths use the exact same graph logic.
```

---

## 11. Lab 4 + Lab 5 = Unstoppable Combo

```
  Lab 4 built a knowledge base:
      Documents → Embeddings → FAISS / Pinecone / RDF

  Lab 5 built an agent system:
      Planner → Retriever → Summariser

  Combined:
      ┌──────────┐     ┌──────────────────────────────┐
      │  Planner │────▶│  Retriever                   │
      └──────────┘     │    ├── DuckDuckGo (web)      │
                       │    ├── FAISS (local vectors) │
                       │    ├── Pinecone (cloud)      │
                       │    └── RDF Graph (structure) │
                       └──────────┬───────────────────┘
                                  │
                       ┌──────────▼───────────┐
                       │     Summariser       │
                       └──────────────────────┘

  The Retriever can call ANY tool.  Swap DuckDuckGo for your Lab 4
  RAG pipeline and you have a hybrid-retrieval multi-agent system!
```

---

## 12. Script-by-Script Summary

| Script                         | What it teaches                          | Key takeaway                      |
| ------------------------------ | ---------------------------------------- | --------------------------------- |
| `01_concepts.py`               | Chain, Graph, Agent, State, Tool, Memory | Mental model                      |
| `02_setup_tools_and_memory.py` | Real LangChain objects                   | LLM + Search + Memory in 10 lines |
| `03_define_agents.py`          | Write agent functions                    | `fn(state) → dict` is the pattern |
| `04_build_graph.py`            | Wire agents into LangGraph               | Nodes + Edges + compile()         |
| `05_conditional_edge.py`       | Branching / retry                        | Router function decides next node |
| `06_full_interactive.py`       | Interactive CLI                          | The finished product              |

---

## 13. Glossary

| Term                 | What it means                                         |
| -------------------- | ----------------------------------------------------- |
| **Agent**            | A function that does one job (Planner, Retriever, …)  |
| **Chain**            | A linear sequence: prompt → LLM → output              |
| **Compile**          | Lock the graph and validate it (no missing nodes)     |
| **Conditional edge** | An edge whose destination is decided at runtime       |
| **Edge**             | An arrow between two nodes ("after A, run B")         |
| **END**              | The special node that stops the graph                 |
| **Entry point**      | The first node the graph runs                         |
| **Invoke**           | Run the compiled graph with an input                  |
| **LLM**              | Large Language Model (GPT-4, etc.)                    |
| **Memory**           | Stored conversation history                           |
| **Node**             | A single agent function in the graph                  |
| **Prompt**           | The text you send to the LLM                          |
| **Router**           | A function that decides which node runs next          |
| **State**            | The shared dictionary flowing through every node      |
| **Tool**             | A wrapped Python function the LLM / agent can call    |
| **TypedDict**        | A Python class that defines which keys state can have |
