"""
============================================================================
LAB 5 — SCRIPT 06 : Interactive Multi-Agent Chat  (the final product)
============================================================================
RUN:   python 06_full_interactive.py
============================================================================

OBJECTIVE
---------
Everything from Scripts 01-05 is now assembled into a single interactive
loop.  YOU type questions, the three agents work, and you see every step
in real time.  This is the "finished lab" — the thing you show people.

WHAT YOU WILL LEARN
-------------------
1.  How to structure a complete, production-style agent script.
2.  How to show a live execution trace (what each agent is doing).
3.  How memory accumulates across multiple questions.
4.  How to handle keyboard interrupts and exit cleanly.

FEATURES
--------
• Live agent trace — every node logs what it is doing as it runs.
• Memory display  — after each answer, see the full conversation history.
• Retry logic     — if search fails, the graph retries automatically.
• Demo mode       — works even without an API key (simulated responses).
• Clean exit      — type "quit" or press Ctrl+C at any time.
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# ============================================================================
# BANNER
# ============================================================================

def print_banner():
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "   🤖  MULTI-AGENT SYSTEM  —  Lab 5 (Interactive)".ljust(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" + "   Agents:  Planner  →  Retriever  →  Summariser".ljust(68) + "█")
    print("█" + "   Features: Web Search · Memory · Retry Logic".ljust(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)


# ============================================================================
# BOOTSTRAP
# ============================================================================

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HAS_KEY = bool(OPENAI_API_KEY) and OPENAI_API_KEY != "your_openai_api_key_here"

llm     = None
search  = None
memory  = None

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

MAX_RETRIES = 2


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


# ============================================================================
# AGENT NODE FUNCTIONS
# ============================================================================

def planner_node(state: dict) -> dict:
    retry_hint = state.get("retry_hint", "")
    retries    = state.get("retries", 0)
    log_agent("PLANNER", f"input: \"{state['input'][:50]}…\"  (attempt {retries + 1})")
    if retry_hint:
        log_agent("PLANNER", f"hint: \"{retry_hint[:60]}…\"")

    plan = call_llm(
        PLANNER_PROMPT.format(input=state["input"], retry_hint=retry_hint),
        demo_fallback=(
            "Mars exploration 2025 latest news"
            if retries == 0 else
            "NASA Mars rover mission 2025 details"
        )
    )
    log_agent("PLANNER", f"query → \"{plan[:70]}\"")

    if memory:
        memory.save_context(
            {"input": state["input"]},
            {"output": f"[Planner] search query: {plan}"}
        )
    return {"planner_output": plan, "step": "retrieve", "retries": retries}


def retriever_node(state: dict) -> dict:
    query   = state["planner_output"]
    retries = state.get("retries", 0)
    log_agent("RETRIEVER", f"searching: \"{query[:55]}\"")

    if search:
        try:
            results = search.run(query)
            log_agent("RETRIEVER", f"got {len(results)} chars")
        except Exception as e:
            results = f"[SEARCH_FAILED: {e}]"
            log_agent("RETRIEVER", f"FAILED: {e}")
    else:
        # Demo: simulate failure on first attempt, success on second
        if retries == 0:
            results = "[DEMO] Short unhelpful snippet."
            log_agent("RETRIEVER", "demo: short result → will trigger retry")
        else:
            results = (
                "[DEMO] NASA confirmed a crewed Mars mission target of 2028. "
                "The 2026 rover will carry spectrometers to analyze Martian soil. "
                "SpaceX Starship will serve as the primary launch vehicle. "
                "The European Space Agency is also working on a sample-return mission."
            )
            log_agent("RETRIEVER", "demo: good result → will proceed")

    if memory:
        memory.save_context(
            {"input": f"[Retriever] query: {query}"},
            {"output": f"[Retriever] result: {results[:100]}…"}
        )
    return {"retrieved_info": results, "step": "check"}


def check_results_router(state: dict) -> str:
    results = state.get("retrieved_info", "")
    retries = state.get("retries", 0)
    is_failed = "[SEARCH_FAILED" in results or len(results.strip()) < 80

    if is_failed:
        if retries < MAX_RETRIES:
            state["retries"]    = retries + 1
            state["retry_hint"] = (
                "The previous query did not return useful results. "
                "Try a completely different angle or add more specific keywords."
            )
            log_agent("ROUTER", f"bad results → retry #{retries + 1}")
            return "planner"
        else:
            log_agent("ROUTER", "max retries reached → giving up")
            state["final_output"] = (
                "I'm sorry — I wasn't able to find reliable information after "
                "multiple attempts.  Please try rephrasing your question or "
                "check a search engine directly."
            )
            return "end"
    log_agent("ROUTER", "results OK → summarise")
    return "summarize"


def summariser_node(state: dict) -> dict:
    log_agent("SUMMARISER", "synthesising …")
    answer = call_llm(
        SUMMARISER_PROMPT.format(
            input=state["input"],
            retrieved_info=state["retrieved_info"]
        ),
        demo_fallback=(
            "Based on recent reports, NASA is preparing a new Mars rover "
            "mission for 2026 that will search for signs of past life. "
            "SpaceX plans a crewed mission by 2028, using Starship as the "
            "primary vehicle.  These missions represent a historic push to "
            "explore the red planet."
        )
    )
    log_agent("SUMMARISER", f"done ({len(answer)} chars)")
    if memory:
        memory.save_context(
            {"input": "[Summariser] synthesising"},
            {"output": f"[Summariser] {answer[:100]}…"}
        )
    return {"final_output": answer, "step": "end"}


# ============================================================================
# BUILD THE LANGGRAPH  (or prepare manual fallback)
# ============================================================================

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
    graph.add_node("planner",   planner_node)
    graph.add_node("retrieve",  retriever_node)
    graph.add_node("summarize", summariser_node)
    graph.set_entry_point("planner")
    graph.add_edge("planner", "retrieve")
    graph.add_conditional_edges(
        "retrieve",
        check_results_router,
        {"summarize": "summarize", "planner": "planner", "end": END}
    )
    graph.add_edge("summarize", END)
    app = graph.compile()

except ImportError:
    pass   # will use manual fallback


def run_manual(input_text: str) -> dict:
    state = {"input": input_text, "retries": 0, "retry_hint": ""}
    for _ in range(MAX_RETRIES + 2):
        state = {**state, **planner_node(state)}
        state = {**state, **retriever_node(state)}
        decision = check_results_router(state)
        if decision == "summarize":
            state = {**state, **summariser_node(state)}
            break
        elif decision == "end":
            break
    return state


# ============================================================================
# INTERACTIVE LOOP
# ============================================================================

def run_query(user_input: str) -> dict:
    """Run the full pipeline for one user question."""
    if app:
        try:
            return app.invoke({"input": user_input, "retries": 0, "retry_hint": ""})
        except Exception as e:
            print(f"\n  ❌  LangGraph error: {e}  — using manual fallback")
            return run_manual(user_input)
    return run_manual(user_input)


def show_memory():
    """Pretty-print the memory trace."""
    if not memory or len(memory.chat_history) == 0:
        return
    print("\n  📝  Memory trace (this session):")
    print("  " + "─" * 66)
    for i, msg in enumerate(memory.chat_history):
        label = "You " if msg.type == "human" else "AI  "
        print(f"    {i+1:>2}. [{label}] {msg.content[:90]}")


def main():
    print_banner()

    mode_label = "LIVE (OpenAI + DuckDuckGo)" if HAS_KEY else "DEMO (simulated)"
    graph_label = "LangGraph" if app else "Manual fallback"

    print(f"\n  Mode   : {mode_label}")
    print(f"  Engine : {graph_label}")
    print(f"  Memory : {'✅  enabled' if memory else '🔧  not available'}")
    print(f"  Retries: up to {MAX_RETRIES}")
    print("\n  Type a question and press Enter.  Type 'quit' to exit.\n")

    question_number = 0

    while True:
        # --- Read input ---
        try:
            user_input = input("  ❓  You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  👋  Goodbye!\n")
            break

        # --- Handle special commands ---
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("\n  👋  Goodbye!\n")
            break
        if user_input.lower() in ("memory", "mem", "history"):
            show_memory()
            continue
        if user_input.lower() in ("clear", "reset"):
            if memory:
                memory.clear()
            print("  🗑️   Memory cleared.\n")
            continue
        if user_input.lower() == "help":
            print("""
  Commands:
    <question>   →  Ask anything — the agents will answer.
    memory       →  Show the full conversation memory.
    clear        →  Wipe memory and start fresh.
    help         →  Show this message.
    quit         →  Exit the program.
""")
            continue

        # --- Run the pipeline ---
        question_number += 1
        print(f"\n  {'─' * 66}")
        print(f"  🔄  Question #{question_number} — agents working …")
        print(f"  {'─' * 66}\n")

        result = run_query(user_input)

        # --- Show the answer ---
        print(f"\n  {'═' * 66}")
        print(f"  ✅  ANSWER")
        print(f"  {'═' * 66}")
        print(f"\n  {result.get('final_output', '[no output]')}\n")
        print(f"  (retries used: {result.get('retries', 0)} / {MAX_RETRIES})")

        # --- Show memory if requested ---
        show_memory()
        print()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()