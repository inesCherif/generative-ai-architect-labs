"""
============================================================================
LAB 5 — SCRIPT 02 : Setup — LLM, Tool, and Memory  (real LangChain objects)
============================================================================
OBJECTIVE
---------
Turn the concepts from Script 01 into REAL LangChain objects that you can
touch, inspect, and print.  Every object is tested so you see exactly what
it does before we wire agents together.

WHAT YOU WILL LEARN
-------------------
1.  How to load your API key safely with python-dotenv.
2.  How to create a ChatOpenAI LLM instance.
3.  How to wrap DuckDuckGo search into a LangChain Tool.
4.  How to create and use ConversationBufferMemory.
5.  How to call the LLM manually and see the raw response.

GRACEFUL FALLBACK
-----------------
If your OpenAI key is missing or invalid this script still runs.
Every real API call is wrapped in a try/except that prints a clear
message and substitutes a demo value so the rest of the script keeps
teaching you.
"""

import os
from dotenv import load_dotenv

print("=" * 70)
print("  LAB 5 — SCRIPT 02 :  SETUP  (LLM · Tool · Memory)")
print("=" * 70)


# ============================================================================
# STEP A — Load the API key
# ============================================================================

load_dotenv()                             
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  

if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
    print("  ✅  OPENAI_API_KEY loaded  (first 8 chars: " +
          OPENAI_API_KEY[:8] + "…)")
    HAS_KEY = True
else:
    print("  ⚠️   OPENAI_API_KEY not found — running in DEMO mode.")
    print("       To enable live calls, copy .env.template → .env")
    print("       and paste your key from https://platform.openai.com/api-keys")
    HAS_KEY = False


# ============================================================================
# STEP B — Create the LLM instance
# ============================================================================
# ChatOpenAI is LangChain's wrapper around OpenAI's chat models.
#
#   model       – which model to use (gpt-4, gpt-4o-mini …)
#   temperature – 0 = deterministic, 1 = creative.
#                 We use 0 so answers are repeatable while learning.
#   api_key     – passed explicitly (or it reads OPENAI_API_KEY env var)
#
# The object does NOT make a network call here — it only connects when
# you actually .invoke() it.
# ============================================================================

llm = None # default if no key

if HAS_KEY:
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model="gpt-4o-mini",        # cheaper & faster than gpt-4; great for learning
            temperature=0,              # deterministic answers
            api_key=OPENAI_API_KEY
        )
        print("  ✅  LLM created:  ChatOpenAI(model='gpt-4o-mini', temperature=0)")
        print(f"       Type: {type(llm)}")
    except Exception as e:
        print(f"  Could not create LLM: {e}")
        HAS_KEY = False

if not HAS_KEY:
    print("  🔧  [DEMO] LLM object is None — API calls will be simulated.")


# ============================================================================
# STEP C — Create the Search Tool
# ============================================================================
# DuckDuckGoSearchRun wraps the duckduckgo-search library.
# It is FREE — no API key required.
#
# We then wrap it in LangChain's Tool class so it has:
#   name        – identifier the LLM / agent will reference
#   func        – the callable (search.run)
#   description – plain English so an LLM knows when to use it
#
# IMPORTANT: In this lab the Retriever agent calls the tool DIRECTLY
# (search.run(query)).  The Tool wrapper is shown here for completeness
# and because you will use it in more advanced setups.
# ============================================================================

search = None
search_tool = None

try:
    from langchain_community.tools import DuckDuckGoSearchRun
    from langchain.agents import Tool

    search = DuckDuckGoSearchRun()

    search_tool = Tool(
        name="WebSearch",
        func=search.run,
        description=(
            "Useful for searching the web to answer current-events "
            "questions or general knowledge queries."
        )
    )

    print("  ✅  Search tool created:")
    print(f"       name        = \"{search_tool.name}\"")
    print(f"       description = \"{search_tool.description[:60]}…\"")
    print(f"       func        = {search_tool.func}")

except ImportError as e:
    print(f"  ⚠️   Could not import search tool: {e}")
    print("       Install with:  pip install duckduckgo-search")
    print("       Continuing without search …")
except Exception as e:
    print(f"  ⚠️   Search tool error: {e}")
    print("       Continuing without search …")


# ============================================================================
# STEP D — Create Shared Memory
# ============================================================================
# ConversationBufferMemory keeps a list of every (Human / AI) message.
# Because we pass return_messages=True it returns them as a list of
# message objects — exactly the format ChatOpenAI expects.
#
# In our multi-agent graph we will store the memory object inside the
# STATE dictionary so every agent can read the same history.
# ============================================================================

try:
    from langchain.memory import ConversationBufferMemory

    memory = ConversationBufferMemory(return_messages=True)

    print("  ✅  Memory created:  ConversationBufferMemory(return_messages=True)")
    print(f"       Type: {type(memory)}")
    print(f"       Messages so far: {len(memory.chat_history)}  (empty — as expected)")

    # --- Demo: manually add a turn so you can SEE what memory looks like ---
    memory.save_context(
        {"input": "Hello, what can you do?"},
        {"output": "I can plan, search, and summarise!"}
    )

    print("\n       After saving one exchange:")
    for msg in memory.chat_history:
        label = "Human" if msg.type == "human" else "AI   "
        print(f"         [{label}] {msg.content}")

    # Reset for the real run
    memory.clear()
    print("\n       Memory cleared — ready for the real run.")

except ImportError as e:
    print(f"  ⚠️   Could not import memory: {e}")
    memory = None


# ============================================================================
# STEP E — Quick live LLM test  (only if key is valid)
# ============================================================================
# This is a single .invoke() call — the bare minimum to prove the
# connection works before we build agents on top of it.
# ============================================================================

print("\n" + "─" * 70)
print("  STEP E :  Quick LLM smoke-test")
print("─" * 70)

if llm:
    try:
        from langchain.schema import HumanMessage

        test_response = llm.invoke([HumanMessage(content="Say 'LLM is alive' and nothing else.")])
        print(f"  ✅  LLM responded:  \"{test_response.content}\"")
    except Exception as e:
        print(f"  ❌  LLM call failed: {e}")
        print("       Check your API key and internet connection.")
else:
    print("  🔧  [DEMO] Skipped — no valid API key.")


# ============================================================================
# STEP F — Quick search test
# ============================================================================

print("\n" + "─" * 70)
print("  STEP F :  Quick Search smoke-test")
print("─" * 70)

if search:
    try:
        test_query = "Mars exploration 2025"
        print(f"  🔍  Searching for: \"{test_query}\"")
        snippet = search.run(test_query)
        # Print only first 200 chars so output stays readable
        print(f"  ✅  Search returned ({len(snippet)} chars):")
        print(f"       \"{snippet[:200]}…\"")
    except Exception as e:
        print(f"  ⚠️   Search failed: {e}")
        print("       Some networks block DuckDuckGo.  The agents will still")
        print("       work — they will just get an error message as 'retrieved info'.")
else:
    print("  🔧  [DEMO] Skipped — search tool not available.")


# ============================================================================
# SUMMARY — what we have ready for the next scripts
# ============================================================================

print("\n" + "=" * 70)
print("  SUMMARY — objects ready for the agent scripts")
print("=" * 70)
print(f"  LLM (ChatOpenAI)              : {'✅  ready' if llm    else '🔧  demo mode'}")
print(f"  Search Tool (DuckDuckGo)      : {'✅  ready' if search else '🔧  not available'}")
print(f"  Memory (ConversationBuffer)   : {'✅  ready' if memory else '🔧  not available'}")
print("""
  Next script:   03_define_agents.py
      → We write the Planner, Retriever, and Summariser agent functions
        and attach them to a LangGraph StateGraph.
""")
print("=" * 70)