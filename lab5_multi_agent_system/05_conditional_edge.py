"""
============================================================================
LAB 5 — SCRIPT 05 : Conditional Edge  (retry if search fails)
============================================================================
RUN:   python 05_conditional_edge.py
============================================================================

OBJECTIVE
---------
Add BRANCHING to the graph.  After the Retriever runs, a decision node
checks whether the search actually returned useful results.
    • If YES → continue to the Summariser as before.
    • If NO  → loop back to the Planner with a hint to try a different query.

This is what separates a Graph from a Chain.  Chains go in one direction.
Graphs can DECIDE.

WHAT YOU WILL LEARN
-------------------
1.  How to write a "router" function that returns a node name.
2.  How add_conditional_edge() works in LangGraph.
3.  How to track retry count so we don't loop forever.
4.  The pattern: check → branch → (loop or continue).

GRAPH SHAPE
-----------
        ┌──────────┐     ┌───────────┐
  IN ──▶│  Planner │────▶│ Retriever │──┐
        └──────────┘     └───────────┘  │
             ▲                          │
             │  (retry — search failed) │
             └──────────────────────────┘ ──▶ ┌─────────────┐
                                               │ Summariser  │──▶ OUT
                                               └─────────────┘
"""

import os
from dotenv import load_dotenv
from datetime import datetime

print("=" * 70)
print("  LAB 5 — SCRIPT 05 :  CONDITIONAL EDGE  (retry on failure)")
print("=" * 70)

# ============================================================================
# BOOTSTRAP
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
      f"Search: {'✅' if search else '🔧'}")


# ============================================================================
# HELPERS
# ============================================================================

def call_llm(prompt_text: str, demo_fallback: str) -> str:
    if llm:
        try:
            from langchain.schema import HumanMessage
            return llm.invoke([HumanMessage(content=prompt_text)]).content
        except Exception as e:
            print(f"       ⚠️  LLM error: {e}")
            return demo_fallback
    return demo_fallback


def log_agent(name: str, action: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  [{ts}] 🤖 {name:>12} │ {action}")


# ============================================================================
# PROMPTS
# ============================================================================

PLANNER_PROMPT = """You are a Planner agent.  Your ONLY job is to take a user's
question and rewrite it into a clear, concise search query.

User's question: {input}
{retry_hint}
Output ONLY the query text, nothing else."""

SUMMARISER_PROMPT = """You are a Summariser agent.  Synthesise these search results
into a clear, concise answer (3-5 sentences).

Original question: {input}

Raw search results:
{retrieved_info}

If the results are empty or unhelpful, say so politely."""

# Maximum number of retry loops before we give up
MAX_RETRIES = 2


# ============================================================================
# AGENT FUNCTIONS  (updated for retry support)
# ============================================================================

def planner_node(state: dict) -> dict:
    """
    Planner — now reads an optional 'retry_hint' from state.
    On the first call retry_hint is empty.  On a retry it says
    "the previous query didn't work, try a different angle."
    """
    retry_hint = state.get("retry_hint", "")
    retries = state.get("retries", 0)

    log_agent("PLANNER", f"input: \"{state['input'][:50]}…\"  "
              f"(attempt {retries + 1})")

    if retry_hint:
        log_agent("PLANNER", f"retry hint: \"{retry_hint}\"")

    plan = call_llm(
        PLANNER_PROMPT.format(input=state["input"], retry_hint=retry_hint),
        demo_fallback=(
            "Mars exploration 2025 latest news"
            if retries == 0 else
            "NASA Mars rover 2025 update"
        )
    )

    log_agent("PLANNER", f"query: \"{plan[:70]}\"")

    return {
        "planner_output": plan,
        "step": "retrieve",
        "retries": retries  # keep the counter unchanged — Retriever updates it
    }


def retriever_node(state: dict) -> dict:
    """
    Retriever — searches the web.  If the result is too short or
    contains an error string, it flags the result so the router can
    detect the failure.
    """
    query = state["planner_output"]
    log_agent("RETRIEVER", f"searching: \"{query[:55]}\"")

    if search:
        try:
            results = search.run(query)
            log_agent("RETRIEVER", f"got {len(results)} chars")
        except Exception as e:
            # Flag the failure explicitly
            results = f"[SEARCH_FAILED: {e}]"
            log_agent("RETRIEVER", f"FAILED: {e}")
    else:
        # DEMO MODE — simulate success on first try, failure on second
        retries = state.get("retries", 0)
        if retries == 0:
            results = (
                "[DEMO] Simulating a SHORT / unhelpful result to trigger retry. "
            )
            log_agent("RETRIEVER", "demo: returning short result (will trigger retry)")
        else:
            results = (
                "[DEMO] NASA confirmed a crewed Mars mission target of 2028. "
                "The rover launching in 2026 will use spectrometers to analyze "
                "Martian soil for biosignatures. SpaceX Starship will serve as "
                "the primary launch vehicle."
            )
            log_agent("RETRIEVER", "demo: returning good result")

    return {
        "retrieved_info": results,
        "step": "check_results"
    }


# ============================================================================
# THE ROUTER  (the decision node)
# ============================================================================
# This function is NOT a regular agent — it does not call an LLM.
# It just LOOKS at the state and returns the NAME of the next node.
#
# LangGraph's add_conditional_edge() calls this function after the
# Retriever finishes.  Whatever string it returns becomes the next node.
#
# This is the core pattern for branching:
#     def router(state) -> str:   # returns a node name
# ============================================================================

print("\n" + "─" * 70)
print("  CONCEPT :  THE ROUTER  (conditional edge function)")
print("─" * 70)
print("""
  A router is a plain function:   def router(state) -> str

  It reads the state and returns the NAME of the next node to run.
  LangGraph uses it like a traffic light:

      After Retriever:
          router(state)  →  "summarize"   (results are good)
          router(state)  →  "planner"     (results are bad — retry)
          router(state)  →  END           (too many retries — give up)
""")


def check_results_router(state: dict) -> str:
    """
    Decides what to do after the Retriever:

    Returns
    -------
    str
        "summarize"  – results look good, proceed.
        "planner"    – results are bad, retry with a new query.
        "end"        – we've retried too many times, bail out.
    """
    results = state.get("retrieved_info", "")
    retries = state.get("retries", 0)

    # --- Failure detection heuristics ---
    is_failed = (
        "[SEARCH_FAILED" in results or          # explicit error tag
        len(results.strip()) < 80               # suspiciously short
    )

    if is_failed:
        if retries < MAX_RETRIES:
            new_retries = retries + 1
            log_agent("ROUTER", f"results too short/failed — retry #{new_retries}")
            # We mutate state here so the Planner sees the updated counter.
            # (In production you'd return this via a separate node, but for
            #  clarity we do it here.)
            state["retries"] = new_retries
            state["retry_hint"] = (
                "The previous search query did not return useful results. "
                "Try a completely different angle or add more specific keywords."
            )
            return "planner"                    # loop back!
        else:
            log_agent("ROUTER", f"max retries ({MAX_RETRIES}) reached — giving up")
            state["final_output"] = (
                "I'm sorry — I wasn't able to find reliable information on "
                "this topic after multiple attempts.  Please try rephrasing "
                "your question or check a search engine directly."
            )
            return "end"                        # bail out
    else:
        log_agent("ROUTER", "results look good — proceeding to summariser")
        return "summarize"                      # happy path


def summariser_node(state: dict) -> dict:
    log_agent("SUMMARISER", "synthesising …")
    answer = call_llm(
        SUMMARISER_PROMPT.format(input=state["input"],
                                 retrieved_info=state["retrieved_info"]),
        demo_fallback=(
            "Based on recent reports, NASA is preparing a new Mars rover "
            "mission for 2026 that will search for signs of past life. "
            "SpaceX plans a crewed mission by 2028, using Starship as the "
            "launch vehicle.  These missions represent a historic push to "
            "explore Mars in the coming decade."
        )
    )
    log_agent("SUMMARISER", f"answer ready ({len(answer)} chars)")
    return {"final_output": answer, "step": "end"}


# ============================================================================
# BUILD THE GRAPH WITH CONDITIONAL EDGE
# ============================================================================

print("\n" + "─" * 70)
print("  BUILDING THE GRAPH  (with conditional edge)")
print("─" * 70)

USE_LANGGRAPH = False
app = None

try:
    from typing import TypedDict
    from langgraph.graph import StateGraph, END

    class AgentState(TypedDict, total=False):
        input:            str
        planner_output:   str
        retrieved_info:   str
        final_output:     str
        step:             str
        retries:          int
        retry_hint:       str

    graph = StateGraph(AgentState)

    # --- Nodes ---
    graph.add_node("planner",   planner_node)
    graph.add_node("retrieve",  retriever_node)
    graph.add_node("summarize", summariser_node)

    # --- Entry ---
    graph.set_entry_point("planner")

    # --- Normal edges ---
    graph.add_edge("planner", "retrieve")      # Planner always → Retriever

    # --- THE CONDITIONAL EDGE ---
    # After "retrieve" finishes, call check_results_router(state).
    # Whatever string it returns becomes the next node.
    #
    # The mapping dict tells LangGraph which strings are valid:
    #   "summarize" → run summariser_node
    #   "planner"   → loop back to planner_node
    #   END         → stop the graph
    #
    # If the router returns a string NOT in the mapping, LangGraph
    # raises an error — a safety net!

    graph.add_conditional_edges(
        "retrieve",                     # after this node …
        check_results_router,           # … call this router function …
        {                               # … and map its output:
            "summarize": "summarize",   #   "summarize" → summariser node
            "planner":   "planner",     #   "planner"   → loop back
            "end":       END            #   "end"       → stop
        }
    )

    # --- Final edge ---
    graph.add_edge("summarize", END)

    print("  ✅  Nodes:  planner, retrieve, summarize")
    print("  ✅  Edges:")
    print("       planner  ──▶  retrieve")
    print("       retrieve ──▶  [CONDITIONAL ROUTER]")
    print("                       ├─ results good  ──▶  summarize  ──▶ END")
    print("                       ├─ results bad   ──▶  planner   (retry loop)")
    print("                       └─ max retries   ──▶  END")

    app = graph.compile()
    print("  ✅  Graph compiled!")
    USE_LANGGRAPH = True

except ImportError as e:
    print(f"  ⚠️   LangGraph not available: {e}")
    print("       Falling back to manual execution with retry logic …")


# ============================================================================
# MANUAL FALLBACK  (with retry loop)
# ============================================================================

def run_manual_with_retry(input_text: str) -> dict:
    """Manual version of the conditional graph — same logic, no LangGraph."""
    state = {"input": input_text, "retries": 0, "retry_hint": ""}

    for attempt in range(MAX_RETRIES + 2):   # +2 = initial + retries + final
        # Planner
        state = {**state, **planner_node(state)}
        # Retriever
        state = {**state, **retriever_node(state)}
        # Router decision
        decision = check_results_router(state)

        if decision == "summarize":
            state = {**state, **summariser_node(state)}
            break
        elif decision == "end":
            # final_output was already set by the router
            break
        # else decision == "planner" → loop continues

    return state


# ============================================================================
# RUN THE PIPELINE
# ============================================================================

print("\n" + "=" * 70)
print("  RUNNING THE PIPELINE  (watch the retry in action)")
print("=" * 70)

query = "Tell me what's new about Mars exploration this month."
print(f"\n  Query: \"{query}\"\n")

if memory:
    memory.clear()

if app:
    try:
        result = app.invoke({"input": query, "retries": 0, "retry_hint": ""})
    except Exception as e:
        print(f"\n  ❌  LangGraph error: {e}")
        print("      Falling back …")
        result = run_manual_with_retry(query)
else:
    result = run_manual_with_retry(query)

print("\n  " + "─" * 66)
print("  ✅  FINAL ANSWER")
print("  " + "─" * 66)
print(f"\n  {result.get('final_output', '[no output]')}\n")

total_retries = result.get("retries", 0)
print(f"  📊  Total retries used: {total_retries} / {MAX_RETRIES}")


# ============================================================================
# RECAP
# ============================================================================

print("\n" + "=" * 70)
print("  RECAP — what's new in this script")
print("=" * 70)
print("""
  ✅  Conditional edge  — the graph can BRANCH after the Retriever.
  ✅  Router function   — a plain fn(state) → str that picks the next node.
  ✅  Retry loop        — if search fails, we loop back to Planner.
  ✅  Max retries       — a safety cap so we never loop forever.
  ✅  Graceful bail-out — after max retries, a polite error message.

  This is the pattern you will use in ANY real multi-agent system:
      1. Do something (Retriever)
      2. Check if it worked (Router)
      3. If not, retry with a different strategy (loop)
      4. If yes, continue (Summariser)

  Next script:   06_full_interactive.py
      → Combine everything into an interactive CLI where YOU type the
        questions and watch the agents work in real time.
""")
print("=" * 70)