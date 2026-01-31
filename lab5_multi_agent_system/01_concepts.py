"""

OBJECTIVE
---------
Before writing a single "real" line, you need a mental model for the THREE
big ideas this lab is built on.  This script walks you through each one
with tiny, runnable examples that need nothing but Python.

WHAT YOU WILL LEARN
-------------------
1.  What a "chain" is and why LangChain exists.
2.  What a "graph" is and why LangGraph exists ON TOP of LangChain.
3.  What a "multi-agent system" is and why it is better than one big prompt.
"""

# ============================================================================
# 0.  THE VERY FIRST QUESTION:  "What problem are we solving?"
# ============================================================================
#
#  Imagine you ask GPT-4:
#      "What is the latest news about Mars exploration?"
#
#  GPT-4 can only answer from its TRAINING DATA (frozen in time).
#  It cannot browse the web.  It cannot run code.  It cannot remember
#  your previous conversations.
#
#  LangChain + LangGraph solve exactly that gap by giving LLMs:
#      • Tools   (web search, calculators, databases …)
#      • Memory  (remember past turns)
#      • Structure (decide WHICH tool to call, in WHAT order)
#
# ============================================================================

print("=" * 70)
print("  LAB 5 — SCRIPT 01 :  CORE CONCEPTS")
print("=" * 70)


# ============================================================================
# 1.  WHAT IS A "CHAIN"?  (LangChain's core idea)
# ============================================================================
#
#  A Chain = Input  →  [some processing]  →  Output
#
#  The simplest chain:
#      user_question  →  LLM  →  answer
#
#  A more useful chain:
#      user_question  →  format_prompt  →  LLM  →  parse_output  →  answer
#
#  LangChain gives you pre-built "links" you can snap together:
#      PromptTemplate   –  formats your prompt with variables
#      ChatOpenAI       –  calls GPT-4 (or any LLM)
#      ConversationBufferMemory  –  stores past messages
#      Tool             –  wraps any function (search, calc …)
#      LLMChain         –  PromptTemplate + LLM glued together
#
#  Think of LangChain as a LEGO set for LLM apps.
# ============================================================================

print("\n" + "─" * 70)
print("  CONCEPT 1 :  THE CHAIN  (LangChain's building block)")
print("─" * 70)

# --- Simulate what LangChain's PromptTemplate does ---
# (no import needed — this IS what it does under the hood)

def simple_prompt_template(template: str, **kwargs) -> str:
    """Fill placeholders {like_this} in a template string."""
    return template.format(**kwargs)


# --- Simulate what LangChain's LLMChain does ---

def simulate_llm(prompt: str) -> str:
    """Pretend we called GPT-4.  Returns a canned answer."""
    # In real code this would be:
    #   llm = ChatOpenAI(model="gpt-4")
    #   return llm.invoke(prompt).content
    return f"[LLM received: \"{prompt[:60]}…\" → generated an answer]"


def simple_chain(user_input: str) -> str:
    """
    Simulates a one-step LangChain LLMChain:
        user_input  →  PromptTemplate  →  LLM  →  output
    """
    # Step A: format the prompt
    prompt = simple_prompt_template(
        "You are a helpful assistant. Answer this question:\n{question}",
        question=user_input
    )
    # Step B: send to LLM
    output = simulate_llm(prompt)
    return output


print("""
  A Chain is just:   Input  →  Format Prompt  →  Send to LLM  →  Output

  Example (simulated — no API key):
""")

result = simple_chain("What is the speed of light?")
print(f"    Input   : 'What is the speed of light?'")
print(f"    Output  : {result}")

print("""
  In real LangChain code this is three lines:
      llm   = ChatOpenAI(model="gpt-4")
      chain = LLMChain(llm=llm, prompt=my_prompt_template)
      answer = chain.run("What is the speed of light?")

  WHY does this helper library exist?
      • Prompt templates keep your prompts tidy and reusable.
      • You can swap GPT-4 for Mistral or Claude — same code.
      • Memory, tools, and parsing can be plugged in later.
""")


# ============================================================================
# 2.  WHAT IS A "GRAPH"?  (LangGraph's core idea)
# ============================================================================
#
#  A Chain is LINEAR:   A → B → C  (no branching, no loops)
#
#  A Graph is a NETWORK of nodes with edges that can branch & loop:
#
#        ┌──────────┐     ┌───────────┐
#        │  Planner │────▶│ Retriever │
#        └──────────┘     └─────┬─────┘
#                               │
#                    ┌──────────▼──────────┐
#                    │     Summariser      │
#                    └─────────────────────┘
#
#  Each NODE is a function (or a chain).
#  Each EDGE says "when node A finishes, run node B next."
#  You can add CONDITIONAL edges: "if the result says 'need more info',
#  loop back to Retriever."
#
#  LangGraph builds on LangChain.  It uses the same LLM, tools, memory —
#  but adds the ability to ORCHESTRATE multiple steps in a structured way.
#
#  WHY NOT just chain everything?
#      Because real tasks need DECISIONS.  "Did the search return useful
#      results?  If not, try a different query."  Chains can't do that.
#      Graphs can.
# ============================================================================

print("\n" + "─" * 70)
print("  CONCEPT 2 :  THE GRAPH  (LangGraph's building block)")
print("─" * 70)

# --- Simulate a tiny LangGraph StateGraph ---
# This is EXACTLY what LangGraph does, stripped to its essence.

class TinyStateGraph:
    """Simulates LangGraph's StateGraph with nodes and edges."""

    def __init__(self):
        self.nodes = {}          # name → function
        self.edges = {}          # name → next_name
        self.entry = None        # where to start

    def add_node(self, name, fn):
        self.nodes[name] = fn

    def add_edge(self, src, dst):
        self.edges[src] = dst

    def set_entry_point(self, name):
        self.entry = name

    def compile(self):
        """Returns a callable that walks the graph."""
        def run(state):
            current = self.entry
            while current and current != "end":
                print(f"    → Running node: [{current}]")
                state = {**state, **self.nodes[current](state)}
                current = self.edges.get(current)          # follow the edge
            return state
        return run


# --- Define three tiny node-functions (agents) ---

def planner_node(state):
    print(f"       Planner sees input: \"{state['input'][:50]}…\"")
    return {"planner_output": "Step 1: search the web.  Step 2: summarise."}


def retriever_node(state):
    print(f"       Retriever sees plan: \"{state['planner_output'][:50]}…\"")
    return {"retrieved_info": "… (pretend we searched the web) …"}


def summarizer_node(state):
    print(f"       Summariser sees info: \"{state['retrieved_info'][:50]}…\"")
    return {"final_output": "Here is your summary of the topic."}


# --- Wire them up ---

graph = TinyStateGraph()
graph.add_node("planner",   planner_node)
graph.add_node("retrieve",  retriever_node)
graph.add_node("summarize", summarizer_node)
graph.set_entry_point("planner")
graph.add_edge("planner",   "retrieve")
graph.add_edge("retrieve",  "summarize")
graph.add_edge("summarize", "end")       # "end" stops the loop

app = graph.compile()

print("""
  A Graph connects Nodes with Edges.  Each Node is a function.
  The graph walks from the entry point to "end", step by step.

  Running our tiny 3-node graph:
""")

final_state = app({"input": "Tell me about Mars exploration this month."})
print(f"\n    Final output: \"{final_state['final_output']}\"")

print("""
  In real LangGraph code this looks almost identical:
      graph = StateGraph(MyState)
      graph.add_node("planner",   planner_node)
      graph.add_node("retrieve",  retriever_node)
      graph.add_node("summarize", summarizer_node)
      graph.set_entry_point("planner")
      graph.add_edge("planner",   "retrieve")
      graph.add_edge("retrieve",  "summarize")
      graph.add_edge("summarize", END)
      app = graph.compile()
      result = app.invoke({"input": "…"})
""")


# ============================================================================
# 3.  WHAT IS A "MULTI-AGENT SYSTEM"?
# ============================================================================
#
#  Single agent (one big prompt to GPT-4):
#      "Search the web for X, summarise it, and answer my question."
#      → Works sometimes.  Fails on complex tasks.  Hard to debug.
#
#  Multi-agent (several specialised agents):
#      Planner  : "Break the task into steps."
#      Retriever: "Search the web for step 1."
#      Summariser: "Take the raw results and make them readable."
#
#  WHY is this better?
#      • Each agent has ONE job  →  easier to debug & improve.
#      • You can swap one agent without touching the others.
#      • You can add NEW agents (e.g., a Calculator) without rewriting.
#      • Each agent gets a FOCUSED prompt → better answers.
# ============================================================================

print("\n" + "─" * 70)
print("  CONCEPT 3 :  MULTI-AGENT  vs  SINGLE-AGENT")
print("─" * 70)

print("""
  ┌─────────────────────────────────────────────────────────────┐
  │  SINGLE AGENT (one big prompt)                              │
  │                                                             │
  │  User ──▶ GPT-4 ("search, summarise, answer me") ──▶ Done  │
  │                                                             │
  │  Problems:                                                  │
  │    • If search fails, everything fails.                     │
  │    • Hard to see WHERE it went wrong.                       │
  │    • Prompt gets very long and confusing.                   │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  MULTI-AGENT (specialised agents)                           │
  │                                                             │
  │  User ──▶ Planner ──▶ Retriever ──▶ Summariser ──▶ Done   │
  │                                                             │
  │  Benefits:                                                  │
  │    • Each agent has a short, focused prompt.                │
  │    • You can log & debug each step individually.            │
  │    • Add a Calculator agent later — nothing else changes.   │
  │    • Agents can run in parallel in advanced setups.         │
  └─────────────────────────────────────────────────────────────┘
""")


# ============================================================================
# 4.  "OKAY, SO WHEN DO I USE WHAT?"  — the quick reference
# ============================================================================

print("\n" + "─" * 70)
print("  QUICK REFERENCE :  LangChain vs LangGraph vs OpenAI SDK")
print("─" * 70)

print("""
  ┌──────────────────┬──────────────────────────────────────────────┐
  │  Tool            │  Use it when …                               │
  ├──────────────────┼──────────────────────────────────────────────┤
  │  OpenAI SDK      │  You just want to call GPT-4 directly.       │
  │  (openai)        │  Simplest possible LLM call.                 │
  │                  │  No agents, no tools, no memory.             │
  ├──────────────────┼──────────────────────────────────────────────┤
  │  LangChain       │  You want reusable prompt templates,         │
  │                  │  memory across turns, tool wrappers,         │
  │                  │  or to swap LLM providers easily.            │
  │                  │  Great for a SINGLE chain of steps.          │
  ├──────────────────┼──────────────────────────────────────────────┤
  │  LangGraph       │  You want MULTIPLE agents that hand off      │
  │                  │  work to each other, with branching /        │
  │                  │  looping logic.  Built on top of LangChain.  │
  │                  │  This is what we use in this lab.            │
  └──────────────────┴──────────────────────────────────────────────┘

  Hierarchy:   OpenAI SDK  ⊂  LangChain  ⊂  LangGraph
               (smallest)                   (most powerful)
""")


# ============================================================================
# 5.  WHAT DOES "STATE" MEAN?
# ============================================================================
#
#  Every node in LangGraph receives a STATE dictionary and returns
#  updated key-value pairs that get merged back into the state.
#
#  Think of STATE as the "clipboard" that agents share.
#
#      state = { "input": "…",
#                "planner_output": "…",     ← written by Planner
#                "retrieved_info": "…",     ← written by Retriever
#                "final_output": "…" }      ← written by Summariser
#
#  Each agent reads what it needs and writes what it produces.
# ============================================================================

print("─" * 70)
print("  CONCEPT 4 :  SHARED STATE  (the agents' clipboard)")
print("─" * 70)

print("""
  State flows through every node like a baton in a relay race:

      ┌────────┐  input  ┌───────────┐  planner_output  ┌───────────┐
      │  User  │────────▶│  Planner  │─────────────────▶│ Retriever │
      └────────┘         └───────────┘                  └─────┬─────┘
                                                              │ retrieved_info
                                                              ▼
                                                       ┌─────────────┐
                                                       │ Summariser  │
                                                       └──────┬──────┘
                                                              │ final_output
                                                              ▼
                                                          User sees it!

  Each arrow IS a key in the state dictionary.
  Agents do NOT talk to each other directly — they read & write STATE.
""")


# ============================================================================
# 6.  WHAT IS A "TOOL"?
# ============================================================================
#
#  A Tool = any Python function wrapped so an LLM can call it.
#
#  In this lab we use DuckDuckGoSearchRun — a free web search.
#  But a Tool can be anything: a calculator, a database query, a
#  Python code executor, a file reader …
#
#  LangChain's Tool class just needs:
#      name        – what the LLM calls it ("WebSearch")
#      func        – the actual Python function
#      description – plain-English explanation so the LLM knows WHEN to use it
# ============================================================================

print("─" * 70)
print("  CONCEPT 5 :  TOOLS  (giving the LLM superpowers)")
print("─" * 70)

# Simulate a Tool

def fake_web_search(query: str) -> str:
    return f"[Search results for \"{query}\": …article 1… …article 2…]"


print("""
  A Tool wraps a Python function so an LLM can use it:

      Tool(
          name        = "WebSearch",
          func        = fake_web_search,        # ← any Python function
          description = "Searches the web"      # ← LLM reads this
      )

  Demo call:
""")
print(f"    fake_web_search('Mars 2025')  →  {fake_web_search('Mars 2025')}")

print("""
  In our lab the Retriever agent calls search.run(query) directly.
  The LLM doesn't "choose" the tool here — the graph structure decides
  which agent (and therefore which tool) runs at each step.
""")


# ============================================================================
# 7.  WHAT IS "MEMORY"?
# ============================================================================
#
#  LLMs are stateless by default — they forget everything between calls.
#  Memory solves that.
#
#  ConversationBufferMemory stores every message sent to / from the LLM.
#  You can attach it to a chain or pass it along in the state so every
#  agent can see the full conversation history.
# ============================================================================

print("─" * 70)
print("  CONCEPT 6 :  MEMORY  (making the LLM remember)")
print("─" * 70)

# Simulate memory

class FakeMemory:
    def __init__(self):
        self.messages = []

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})

    def show(self):
        for m in self.messages:
            print(f"      [{m['role']:>9}] {m['content'][:60]}")


mem = FakeMemory()
mem.add("user",      "What is the weather today?")
mem.add("assistant", "I don't have access to real-time data…")
mem.add("user",      "Okay, what about Mars exploration?")

print("""
  Memory stores the conversation so far:
""")
mem.show()

print("""
  In real LangChain:
      memory = ConversationBufferMemory(return_messages=True)
  It automatically appends each exchange.  Agents can read it to
  maintain context across the whole multi-agent workflow.
""")


# ============================================================================
# RECAP
# ============================================================================

print("\n" + "=" * 70)
print("  RECAP — everything we covered")
print("=" * 70)
print("""
  ✅  Chain     = Input → Prompt → LLM → Output          (LangChain)
  ✅  Graph     = Network of Nodes + Edges               (LangGraph)
  ✅  Multi-Agent = Several specialised agents in a graph
  ✅  State     = Shared dictionary agents read/write
  ✅  Tool      = Python function the LLM can call
  ✅  Memory    = Stored conversation history

  Next script:   02_setup_tools_and_memory.py
      → We install real LangChain objects and test them live.
""")
print("=" * 70)