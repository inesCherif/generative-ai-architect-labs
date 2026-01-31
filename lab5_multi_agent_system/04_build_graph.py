"""
============================================================================
LAB 5 — SCRIPT 04 : Build & Run the LangGraph  (the full pipeline)
============================================================================
OBJECTIVE
---------
Wire the three agent functions into a real LangGraph StateGraph, compile
it, and invoke it with example queries.  This is the script where
everything comes together.

WHAT YOU WILL LEARN
-------------------
1.  How to define a typed State class that LangGraph validates.
2.  How to register nodes and edges in a StateGraph.
3.  What .compile() does and why you need it.
4.  How .invoke() runs the whole pipeline from start to END.
5.  How to add a CONDITIONAL edge (bonus — "if search failed, retry").

ARCHITECTURE
------------
        ┌──────────┐     ┌───────────┐     ┌─────────────┐
  IN ──▶│  Planner │────▶│ Retriever │────▶│ Summariser  │──▶ OUT
        └──────────┘     └───────────┘     └─────────────┘

  Entry point: "planner"
  Edges:       planner → retrieve → summarize → END
"""

import os
import json
from dotenv import load_dotenv
from datetime import datetime

# ============================================================================
# BOOTSTRAP — same as previous scripts
# ============================================================================

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HAS_KEY = bool(OPENAI_API_KEY) and OPENAI_API_KEY != "your_openai_api_key_here"

llm = None
search = None
memory = None

if HAS_KEY:
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
    except Exception:
        HAS_KEY = False

try:
    from langchain_community.tools import DuckDuckGoSearchRun
    search = DuckDuckGoSearchRun()
except Exception:
    pass

try:
    from langchain.memory import ConversationBufferMemory
    memory = ConversationBufferMemory(return_messages=True)
except Exception:
    pass

print(f"\n  Mode: {'LIVE' if HAS_KEY else 'DEMO'}  |  "
      f"LLM: {'✅' if llm else '🔧'}  |  "
      f"Search: {'✅' if search else '🔧'}  |  "
      f"Memory: {'✅' if memory else '🔧'}")


# ============================================================================
# COPY the agent functions (identical to Script 03)
# ============================================================================
# In a production project you would import them from a shared module.
# We duplicate them here so this single script is self-contained and
# you can read everything in one place.
# ============================================================================

def call_llm(prompt_text: str, demo_fallback: str) -> str:
    if llm:
        try:
            from langchain.schema import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt_text)])
            return response.content
        except Exception as e:
            print(f"       ⚠️  LLM error: {e}")
            return demo_fallback
    return demo_fallback


def log_agent(name: str, action: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  [{ts}] 🤖 {name:>12} │ {action}")


PLANNER_PROMPT = """You are a Planner agent.  Your ONLY job is to take a user's
question and rewrite it into a clear, concise search query that will
return useful web results.

User's question: {input}

Write a single, focused search query.  Do NOT answer the question —
only produce the query.  Output ONLY the query text, nothing else."""

SUMMARISER_PROMPT = """You are a Summariser agent.  The user asked a question and a
Retriever agent fetched raw search results.  Your job is to synthesise
those results into a clear, concise, well-organised answer.

Original question: {input}

Raw search results:
{retrieved_info}

Write a clear answer (3-5 sentences) that directly addresses the user's
question.  If the search results are empty or unhelpful, say so politely."""


def planner_node(state: dict) -> dict:
    log_agent("PLANNER", f"input: \"{state['input'][:55]}…\"")
    plan = call_llm(
        PLANNER_PROMPT.format(input=state["input"]),
        demo_fallback="Mars exploration latest news 2025"
    )
    log_agent("PLANNER", f"query: \"{plan[:70]}\"")
    if memory:
        memory.save_context({"input": state["input"]},
                            {"output": f"[Planner] {plan}"})
    return {"planner_output": plan, "step": "retrieve"}


def retriever_node(state: dict) -> dict:
    query = state["planner_output"]
    log_agent("RETRIEVER", f"searching: \"{query[:55]}\"")
    if search:
        try:
            results = search.run(query)
            log_agent("RETRIEVER", f"got {len(results)} chars")
        except Exception as e:
            results = f"[Search error: {e}]"
            log_agent("RETRIEVER", f"error: {e}")
    else:
        results = (
            "[DEMO] NASA announced a new Mars rover mission for 2026 that will "
            "carry advanced instruments to search for biosignatures. SpaceX plans "
            "a crewed mission by 2028. The European Space Agency is also developing "
            "a Mars sample-return mission in partnership with NASA."
        )
        log_agent("RETRIEVER", "returned demo results")
    if memory:
        memory.save_context({"input": f"[Retriever] query: {query}"},
                            {"output": f"[Retriever] {results[:100]}…"})
    return {"retrieved_info": results, "step": "summarize"}


def summariser_node(state: dict) -> dict:
    log_agent("SUMMARISER", "synthesising …")
    answer = call_llm(
        SUMMARISER_PROMPT.format(input=state["input"],
                                 retrieved_info=state["retrieved_info"]),
        demo_fallback=(
            "Based on recent reports, NASA is preparing a new Mars rover mission "
            "for 2026 that will search for signs of past life on Mars. SpaceX has "
            "also announced ambitious plans for a crewed Mars mission by 2028. "
            "Additionally, the European Space Agency is working on a sample-return "
            "mission. These efforts represent a major new era in Mars exploration."
        )
    )
    log_agent("SUMMARISER", f"answer ready ({len(answer)} chars)")
    if memory:
        memory.save_context({"input": "[Summariser] synthesising"},
                            {"output": f"[Summariser] {answer[:100]}…"})
    return {"final_output": answer, "step": "end"}


# ============================================================================
# STEP 1 — Define the State type
# ============================================================================
# LangGraph uses typed dictionaries (TypedDict) to know which keys are
# valid in the state and what type each value should be.
#
# If you try to return a key that is NOT in the State class, LangGraph
# will raise an error.  This catches bugs early.
# ============================================================================

try:
    from typing import TypedDict

    class AgentState(TypedDict, total=False):
        """
        The shared state dictionary that flows through every node.

        Keys
        ----
        input           : The user's original question.
        planner_output  : The search query produced by the Planner.
        retrieved_info  : Raw search results from the Retriever.
        final_output    : The polished answer from the Summariser.
        step            : Informational — which step just finished.
        """
        input:            str
        planner_output:   str
        retrieved_info:   str
        final_output:     str
        step:             str

    print("  ✅  AgentState defined with keys:")
    for key in AgentState.__annotations__:
        print(f"       • {key}: {AgentState.__annotations__[key].__name__}")

except ImportError:
    print("  ⚠️   TypedDict not available — using plain dict.")
    AgentState = dict


# ============================================================================
# STEP 2 — Build the Graph
# ============================================================================
# StateGraph(State) creates an empty graph that knows about our State type.
# .add_node(name, fn)  registers a function as a node.
# .add_edge(src, dst)  draws an arrow from src to dst.
# .set_entry_point(n)  says "start here".
#
# The special constant END (imported from langgraph) means "stop".
# ============================================================================

USE_LANGGRAPH = False   # will be True if import succeeds

try:
    from langgraph.graph import StateGraph, END

    # --- Create the graph ---
    graph = StateGraph(AgentState)

    # --- Register nodes ---
    graph.add_node("planner",   planner_node)
    graph.add_node("retrieve",  retriever_node)
    graph.add_node("summarize", summariser_node)

    print("  ✅  Nodes added:")
    print("       • planner   → planner_node()")
    print("       • retrieve  → retriever_node()")
    print("       • summarize → summariser_node()")

    # --- Set the entry point ---
    graph.set_entry_point("planner")
    print("\n  ✅  Entry point: 'planner'")

    # --- Draw edges ---
    graph.add_edge("planner",   "retrieve")    # Planner  → Retriever
    graph.add_edge("retrieve",  "summarize")   # Retriever→ Summariser
    graph.add_edge("summarize", END)           # Summariser→ done!

    print("  ✅  Edges:")
    print("       planner  ──▶  retrieve")
    print("       retrieve ──▶  summarize")
    print("       summarize──▶  END")

    USE_LANGGRAPH = True

except ImportError as e:
    print(f"  ⚠️   LangGraph not installed: {e}")
    print("       Install with:  pip install langgraph")
    print("       Falling back to manual graph execution …")


# ============================================================================
# STEP 3 — Compile
# ============================================================================
# .compile() validates the graph (no missing nodes, no dangling edges)
# and returns a Runnable — an object with .invoke() and .stream().
#
# Think of compile as "press the green button to lock in the blueprint."
# After compilation the graph is immutable.
# ============================================================================

app = None

if USE_LANGGRAPH:
    try:
        app = graph.compile()
        print("  ✅  Graph compiled successfully!")
        print(f"       Type: {type(app)}")
        print("       The graph is now locked and ready to run.")
    except Exception as e:
        print(f"  ❌  Compile error: {e}")
        USE_LANGGRAPH = False

if not USE_LANGGRAPH:
    print("  🔧  [FALLBACK] Using manual sequential execution.")


# ============================================================================
# MANUAL FALLBACK — if LangGraph is not installed
# ============================================================================
# This is literally what LangGraph does under the hood for a linear graph.
# It proves you already understand the concept!
# ============================================================================

def run_manual(input_text: str) -> dict:
    """Run planner → retriever → summariser manually (no LangGraph needed)."""
    state = {"input": input_text}
    state = {**state, **planner_node(state)}
    state = {**state, **retriever_node(state)}
    state = {**state, **summariser_node(state)}
    return state


# ============================================================================
# STEP 4 — INVOKE  (run the pipeline!)
# ============================================================================

EXAMPLE_QUERIES = [
    "Tell me what's new about Mars exploration this month.",
    "What are the latest developments in renewable energy in 2025?"
]

for i, query in enumerate(EXAMPLE_QUERIES, 1):

    print("\n" + "━" * 70)
    print(f"  QUERY {i} :  \"{query}\"")
    print("━" * 70)

    # Reset memory for each query
    if memory:
        memory.clear()

    # --- Run via LangGraph OR manual fallback ---
    if app:
        try:
            result = app.invoke({"input": query})
        except Exception as e:
            print(f"\n  ❌  LangGraph invoke error: {e}")
            print("      Falling back to manual execution …")
            result = run_manual(query)
    else:
        result = run_manual(query)

    # --- Print the final answer ---
    print("\n  " + "─" * 66)
    print("  ✅  FINAL ANSWER")
    print("  " + "─" * 66)
    print(f"\n  {result.get('final_output', '[no output]')}\n")

    # --- Show memory trace ---
    if memory and len(memory.chat_history) > 0:
        print("  📝  Agent memory trace:")
        for msg in memory.chat_history:
            label = "Human" if msg.type == "human" else "AI   "
            print(f"       [{label}] {msg.content[:90]}")


# ============================================================================
# RECAP
# ============================================================================

print("\n" + "=" * 70)
print("  RECAP — what happened inside the graph")
print("=" * 70)
print("""
  1. .invoke({"input": "…"})  pushed the initial state into the graph.
  2. The graph started at the entry point: "planner".
  3. planner_node() ran → returned {"planner_output": …}
  4. The edge planner → retrieve fired.
  5. retriever_node() ran → returned {"retrieved_info": …}
  6. The edge retrieve → summarize fired.
  7. summariser_node() ran → returned {"final_output": …}
  8. The edge summarize → END fired → pipeline stopped.
  9. .invoke() returned the final state dictionary.

  Every step was deterministic, logged, and traceable.  That is the
  power of LangGraph over a single monolithic prompt.
""")

print("  Next script:   05_conditional_edge.py")
print("      → Add a decision node: \"if search failed, retry with")
print("        a different query.\"  This turns our linear graph into")
print("        a real control-flow system.")
print("=" * 70)