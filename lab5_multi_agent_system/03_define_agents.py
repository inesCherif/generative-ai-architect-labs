"""
============================================================================
LAB 5 — SCRIPT 03 : Define the Three Agents  (Planner · Retriever · Summariser)
============================================================================

OBJECTIVE
---------
Write the three agent functions that will become nodes in our LangGraph.
Each function receives the shared STATE, does its work (via an LLM call),
and returns updated state keys.

WHAT YOU WILL LEARN
-------------------
1.  How to write a PromptTemplate for each agent's specialised role.
2.  How each agent node function reads from STATE and writes back.
3.  How the Retriever calls a real tool (DuckDuckGo search).
4.  How logging lets you see what every agent is doing in real time.
5.  The exact signature LangGraph expects:  fn(state) → dict

KEY INSIGHT
-----------
Each agent function is just:
    def agent_name(state):
        # 1. Read what I need from state
        # 2. Do my work (usually an LLM call)
        # 3. Return a dict of new state keys

That's it.  LangGraph handles the rest.
"""

import os
import json
from dotenv import load_dotenv
from datetime import datetime

# ============================================================================
# SETUP — same bootstrap as Script 02
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

status = "LIVE" if HAS_KEY else "DEMO"
print(f"\n  Mode: {status}  |  LLM: {'✅' if llm else '🔧'}  |  "
      f"Search: {'✅' if search else '🔧'}  |  Memory: {'✅' if memory else '🔧'}")


# ============================================================================
# HELPER — a unified "call LLM or return demo text" function
# ============================================================================
# We factor this out so every agent can use it with one line.
# ============================================================================

def call_llm(prompt_text: str, demo_fallback: str) -> str:
    """
    If we have a live LLM, invoke it with a plain string prompt.
    Otherwise return the demo fallback so the script keeps teaching.
    """
    if llm:
        try:
            from langchain.schema import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt_text)])
            return response.content
        except Exception as e:
            print(f"       ⚠️  LLM error: {e}")
            return demo_fallback
    else:
        return demo_fallback


# ============================================================================
# HELPER — pretty log banner
# ============================================================================

def log_agent(name: str, action: str):
    """Print a consistent log line so you can follow execution."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n  [{ts}] 🤖 {name:>12} │ {action}")


# ============================================================================
# CONCEPT RECAP — PromptTemplate
# ============================================================================

print("\n" + "─" * 70)
print("  CONCEPT RECAP :  PromptTemplate")
print("─" * 70)
print("""
  A PromptTemplate is a reusable string with {placeholders}.
  LangChain's version validates the variables and formats them for you.
  In this script we write the templates as plain f-strings so you can
  see EXACTLY what text goes to the LLM — no magic.

  Example:
      template = "You are a planner.  Break down this task: {input}"
      prompt   = template.format(input="Tell me about Mars.")
      # → "You are a planner.  Break down this task: Tell me about Mars."
""")


# ============================================================================
# AGENT 1 — THE PLANNER
# ============================================================================
#
#  Role:   Receives the raw user question and turns it into a clear,
#          ordered plan that the Retriever can act on.
#
#  Reads:  state["input"]           – the user's original question
#  Writes: state["planner_output"]  – the plan (string)
#          state["step"]            – signals which node runs next
#
#  Why a separate Planner?
#      If you dump a complex question straight into a search engine you
#      get noisy results.  A Planner first reformulates the question into
#      a focused, searchable query.
# ============================================================================

print("\n" + "─" * 70)
print("  AGENT 1 :  PLANNER")
print("─" * 70)
print("""
  Job  : Take the user's question → produce a clear search plan.
  Reads: state["input"]
  Writes: state["planner_output"], state["step"]
""")

# --- The prompt template ---
# This is what the LLM actually sees.  Read it carefully!

PLANNER_PROMPT_TEMPLATE = """You are a Planner agent.  Your ONLY job is to take a user's
question and rewrite it into a clear, concise search query that will
return useful web results.

User's question: {input}

Write a single, focused search query.  Do NOT answer the question —
only produce the query.  Output ONLY the query text, nothing else."""


def planner_node(state: dict) -> dict:
    """
    The Planner agent node.

    Parameters
    ----------
    state : dict
        Must contain "input" (the user's original question).

    Returns
    -------
    dict
        Keys: "planner_output" (the reformulated search query),
              "step" (always "retrieve" — tells the graph what's next).
    """
    user_input = state["input"]

    log_agent("PLANNER", f"received input: \"{user_input[:60]}…\"")

    # Format the prompt with the actual user input
    prompt = PLANNER_PROMPT_TEMPLATE.format(input=user_input)

    log_agent("PLANNER", "calling LLM to generate search query …")

    # Call the LLM (or get a demo fallback)
    plan = call_llm(
        prompt,
        demo_fallback=f"Mars exploration news 2025"  # sensible demo query
    )

    log_agent("PLANNER", f"produced plan: \"{plan[:80]}\"")

    # Save to memory if available
    if memory:
        memory.save_context(
            {"input": user_input},
            {"output": f"[Planner] {plan}"}
        )

    # Return new state keys.  "step" is informational — we use explicit
    # edges in the graph, but it's nice for logging.
    return {
        "planner_output": plan,
        "step": "retrieve"
    }


# ============================================================================
# AGENT 2 — THE RETRIEVER
# ============================================================================
#
#  Role:   Takes the Planner's search query and actually searches the web.
#
#  Reads:  state["planner_output"]   – the search query from Planner
#  Writes: state["retrieved_info"]   – raw search results (string)
#          state["step"]             – "summarize"
#
#  Why a separate Retriever?
#      Searching is a distinct action with its own failure mode.  If the
#      search times out or returns garbage, only this agent is affected.
#      The Summariser still gets called — it just gets an error message
#      as its input and can say "I couldn't find information."
# ============================================================================

print("\n" + "─" * 70)
print("  AGENT 2 :  RETRIEVER")
print("─" * 70)
print("""
  Job  : Run a web search using the Planner's query.
  Reads: state["planner_output"]
  Writes: state["retrieved_info"], state["step"]

  Note: This agent calls a TOOL (DuckDuckGo), not the LLM.
        The LLM is not needed here — we just need raw search results.
""")


def retriever_node(state: dict) -> dict:
    """
    The Retriever agent node.

    Parameters
    ----------
    state : dict
        Must contain "planner_output" (search query from Planner).

    Returns
    -------
    dict
        Keys: "retrieved_info" (raw search snippet),
              "step" ("summarize").
    """
    query = state["planner_output"]

    log_agent("RETRIEVER", f"searching for: \"{query[:60]}\"")

    # --- Call the real search tool, or fall back to a demo string ---
    if search:
        try:
            results = search.run(query)
            log_agent("RETRIEVER", f"got {len(results)} chars of results")
        except Exception as e:
            results = (
                f"[Search failed: {e}. "
                "The Summariser will note that no information was retrieved.]"
            )
            log_agent("RETRIEVER", f"search error: {e}")
    else:
        results = (
            "[DEMO] Simulated search results: "
            "NASA announced a new Mars rover mission scheduled for 2026. "
            "The rover will carry instruments to search for signs of past life. "
            "SpaceX is also planning a crewed mission to Mars by 2028."
        )
        log_agent("RETRIEVER", "returned demo search results")

    # Save to memory
    if memory:
        memory.save_context(
            {"input": f"[Retriever] searching: {query}"},
            {"output": f"[Retriever] found: {results[:120]}…"}
        )

    return {
        "retrieved_info": results,
        "step": "summarize"
    }


# ============================================================================
# AGENT 3 — THE SUMMARISER
# ============================================================================
#
#  Role:   Takes raw search results and turns them into a clean,
#          well-structured answer for the user.
#
#  Reads:  state["retrieved_info"]   – raw results from Retriever
#          state["input"]            – original question (for context)
#  Writes: state["final_output"]     – polished answer
#          state["step"]             – "end"
#
#  Why a separate Summariser?
#      Raw search snippets are noisy, repetitive, and unstructured.
#      The Summariser's focused prompt tells the LLM to distil and
#      organise — something a single "do everything" prompt does poorly.
# ============================================================================

print("\n" + "─" * 70)
print("  AGENT 3 :  SUMMARISER")
print("─" * 70)
print("""
  Job  : Turn raw search results into a clean answer.
  Reads: state["retrieved_info"], state["input"]
  Writes: state["final_output"], state["step"]
""")

SUMMARISER_PROMPT_TEMPLATE = """You are a Summariser agent.  The user asked a question and a
Retriever agent fetched raw search results.  Your job is to synthesise
those results into a clear, concise, well-organised answer.

Original question: {input}

Raw search results:
{retrieved_info}

Write a clear answer (3-5 sentences) that directly addresses the user's
question.  If the search results are empty or unhelpful, say so politely."""


def summariser_node(state: dict) -> dict:
    """
    The Summariser agent node.

    Parameters
    ----------
    state : dict
        Must contain "retrieved_info" and "input".

    Returns
    -------
    dict
        Keys: "final_output" (polished answer),
              "step" ("end").
    """
    raw_info = state["retrieved_info"]
    original_q = state["input"]

    log_agent("SUMMARISER", "received search results — synthesising …")

    prompt = SUMMARISER_PROMPT_TEMPLATE.format(
        input=original_q,
        retrieved_info=raw_info
    )

    answer = call_llm(
        prompt,
        demo_fallback=(
            "Based on recent reports, NASA is preparing a new Mars rover "
            "mission for 2026 that will search for signs of past life. "
            "SpaceX has also announced plans for a crewed Mars mission by 2028. "
            "These developments mark an exciting new chapter in Mars exploration."
        )
    )

    log_agent("SUMMARISER", f"produced answer ({len(answer)} chars)")

    # Save to memory
    if memory:
        memory.save_context(
            {"input": f"[Summariser] synthesising …"},
            {"output": f"[Summariser] {answer[:120]}…"}
        )

    return {
        "final_output": answer,
        "step": "end"
    }


# ============================================================================
# TEST — run each agent function in isolation
# ============================================================================
# This is the KEY learning moment.  Before we wire them into a graph,
# let's call each function BY HAND and watch the state evolve.
# ============================================================================

print("\n" + "=" * 70)
print("  TEST :  Running each agent individually (no graph yet)")
print("=" * 70)

# --- Simulate the state as it flows through the pipeline ---

state = {"input": "Tell me what's new about Mars exploration this month."}
print(f"\n  Initial state:\n    {json.dumps(state, indent=4)}")

# Agent 1
print("\n  ── Calling Planner ──")
state = {**state, **planner_node(state)}
print(f"\n  State after Planner:\n    {json.dumps(state, indent=4)}")

# Agent 2
print("\n  ── Calling Retriever ──")
state = {**state, **retriever_node(state)}
print(f"\n  State after Retriever:\n    {json.dumps({k: v[:80] + '…' if len(str(v)) > 80 else v for k, v in state.items()}, indent=4)}")

# Agent 3
print("\n  ── Calling Summariser ──")
state = {**state, **summariser_node(state)}
print(f"\n  State after Summariser:\n    {json.dumps({k: v[:80] + '…' if len(str(v)) > 80 else v for k, v in state.items()}, indent=4)}")


# ============================================================================
# SHOW MEMORY
# ============================================================================

if memory and len(memory.chat_history) > 0:
    print("\n" + "─" * 70)
    print("  MEMORY CONTENTS  (everything the agents logged)")
    print("─" * 70)
    for i, msg in enumerate(memory.chat_history):
        label = "Human" if msg.type == "human" else "AI   "
        print(f"    {i}. [{label}] {msg.content[:100]}")


# ============================================================================
# RECAP
# ============================================================================

print("\n" + "=" * 70)
print("  RECAP")
print("=" * 70)
print("""
  ✅  Planner    – turns a question into a focused search query  (LLM)
  ✅  Retriever  – runs the search query against DuckDuckGo      (Tool)
  ✅  Summariser – synthesises raw results into a clean answer   (LLM)

  Each function:
      • Reads keys it needs from state
      • Does its one job
      • Returns a dict of NEW keys to merge into state

  Next script:   04_build_graph.py
      → We wire these three functions into a LangGraph StateGraph and
        run the full pipeline end-to-end.
""")
print("=" * 70)