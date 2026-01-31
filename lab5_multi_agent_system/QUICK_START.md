# 🚀 Quick Start — Lab 5 Multi-Agent System

Everything you need to go from zero to a running multi-agent system in
about 20 minutes.

---

## What You Need

| Tool           | Why                                | Where to get it                      |
| -------------- | ---------------------------------- | ------------------------------------ |
| Python 3.9+    | Runs the code                      | https://www.python.org/              |
| VSCode         | Code editor (you already have it!) | —                                    |
| OpenAI API key | Powers the LLM calls               | https://platform.openai.com/api-keys |

> 💰 **Cost**: ~$0.05–$0.20 for the whole lab (GPT-4o-mini is cheap).  
> DuckDuckGo search is **free** — no key needed.

---

## Step 1 — Open the Project

1. Open VSCode.
2. **File → Open Folder → select `lab5_multi_agent_system`**.
3. Open the terminal: **Terminal → New Terminal**.

---

## Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

You will see `(venv)` appear at the start of your terminal prompt. That
means it is active.

---

## Step 3 — Install Packages

```bash
pip install langgraph langchain openai faiss-cpu duckduckgo-search
```

This takes 1–2 minutes. Lots of text scrolls by — that is normal.

---

## Step 4 — Get Your OpenAI Key

1. Go to **https://platform.openai.com/api-keys**.
2. Sign in (or create a free account — you get $5 credit).
3. Click **"Create new secret key"**.
4. Copy the key (starts with `sk-…`). You will never see it again!

---

## Step 5 — Configure the Key

```bash
# Windows
copy .env.template .env

# Mac / Linux
cp .env.template .env
```

Open `.env` in VSCode, delete the placeholder text, and paste your key:

```
OPENAI_API_KEY=sk-proj-abc123…
```

Save the file (Ctrl+S).

> ⚠️ **Never** share `.env` or push it to GitHub.

---

## Step 6 — Run the Lab (in order!)

| #   | Command                               | What it teaches            | Time |
| --- | ------------------------------------- | -------------------------- | ---- |
| 1   | `python 01_concepts.py`               | Core ideas (no API needed) | 10 s |
| 2   | `python 02_setup_tools_and_memory.py` | Real LangChain objects     | 15 s |
| 3   | `python 03_define_agents.py`          | Write & test each agent    | 30 s |
| 4   | `python 04_build_graph.py`            | Wire agents into a graph   | 30 s |
| 5   | `python 05_conditional_edge.py`       | Add retry / branching      | 30 s |
| 6   | `python 06_full_interactive.py`       | **Interactive chat!**      | —    |

Script 6 does not exit on its own — it waits for YOUR input. Type
questions and watch the agents work. Type `quit` to stop.

---

## What to Look For

### Script 1 — no output errors

Everything is pure Python. If this fails, your Python installation has a
problem.

### Script 2 — key confirmation

You should see:

```
✅  OPENAI_API_KEY loaded  (first 8 chars: sk-proj-…)
✅  LLM created:  ChatOpenAI(…)
✅  Search tool created
✅  LLM responded:  "LLM is alive"
```

If you see `⚠️  OPENAI_API_KEY not found` the `.env` file is missing or
the key is still the placeholder text.

### Script 6 — live agents

```
❓  You: What is quantum computing?

  [12:00:01] 🤖     PLANNER │ input: "What is quantum computing?…"
  [12:00:02] 🤖     PLANNER │ query → "quantum computing explained 2025"
  [12:00:02] 🤖   RETRIEVER │ searching: "quantum computing explained 2025"
  [12:00:03] 🤖   RETRIEVER │ got 1842 chars
  [12:00:03] 🤖      ROUTER │ results OK → summarise
  [12:00:03] 🤖  SUMMARISER │ synthesising …
  [12:00:04] 🤖  SUMMARISER │ done (312 chars)

  ✅  ANSWER
  Quantum computing …
```

---

## Troubleshooting

| Error                          | Fix                                                                                |
| ------------------------------ | ---------------------------------------------------------------------------------- |
| `⚠️  OPENAI_API_KEY not found` | Check `.env` exists (not `.env.template`), key is pasted correctly, file is saved. |
| `AuthenticationError`          | Your key is wrong or revoked. Create a new one at platform.openai.com.             |
| `RateLimitError`               | Wait 30 seconds and try again. Free tier has rate limits.                          |
| Search returns nothing         | Some networks block DuckDuckGo. The retry logic handles this — or switch to Wi-Fi. |
| `KeyboardInterrupt` traceback  | Normal if you press Ctrl+C. Just run the script again.                             |

---

## Commands Inside Script 6

| Type this    | What it does                            |
| ------------ | --------------------------------------- |
| Any question | Runs the full 3-agent pipeline          |
| `memory`     | Shows everything the agents have logged |
| `clear`      | Wipes memory — fresh start              |
| `help`       | Shows the command list                  |
| `quit`       | Exits cleanly                           |

---

## Cost Breakdown

| Service                    | What it costs              | Why                                                  |
| -------------------------- | -------------------------- | ---------------------------------------------------- |
| OpenAI (gpt-4o-mini)       | ~$0.15 per 1M input tokens | Planner + Summariser each make one call per question |
| DuckDuckGo                 | Free                       | No API key, no charges                               |
| **Total for 10 questions** | **< $0.05**                | Very cheap!                                          |

---

## After the Lab — What Next?

1. **Try different questions** in Script 6. The agents handle almost anything.
2. **Add a new tool** — e.g., a calculator. See `VISUAL_GUIDE.md` for how.
3. **Add a new agent** — e.g., a Fact-Checker that verifies the Summariser's output.
4. **Connect to Lab 4** — replace DuckDuckGo with your FAISS / Pinecone RAG retriever.
5. **Add parallel execution** — LangGraph supports running agents in parallel.

---

## File Map

```
lab5_multi_agent_system/
├── QUICK_START.md              ← you are here
├── VISUAL_GUIDE.md             ← architecture diagrams
├── README.md                   ← high-level overview
├── requirements.txt            ← pip packages
├── .env.template               ← copy → .env, add your key
│
├── 01_concepts.py              ← What is a chain? A graph? An agent?
├── 02_setup_tools_and_memory.py← Real LangChain objects
├── 03_define_agents.py         ← Write Planner, Retriever, Summariser
├── 04_build_graph.py           ← Wire them into a LangGraph
├── 05_conditional_edge.py      ← Add retry / branching
└── 06_full_interactive.py      ← Interactive chat (the final product)
```
