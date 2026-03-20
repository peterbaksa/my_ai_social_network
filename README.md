# AI Social Network

A lightweight simulation of a social network where AI agents — each with a unique persona, opinions, and communication style — debate a given topic in real time. Built on top of a local LLM (Ollama), with no cloud dependencies.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![LLM](https://img.shields.io/badge/LLM-Llama_3.1_8B-orange)

---

## How It Works

The core idea is simple: **an AI agent is not a chatbot — it's a persona attached to a single LLM call.**

Each agent is defined by a YAML config file containing their name, age, personality traits, background story, opinion stance, and communication tone. The agents don't "run" as separate processes — they take turns in a sequential loop, and each turn consists of a single call to a local LLM with the agent's full context injected into the prompt.

### The Simulation Loop

```
For each iteration (1 to 50):
    For each agent:
        1. Build a prompt:
           - System: "You are [persona]. Your traits are [X]. Your stance is [Y]."
           - User: "Here is the recent feed: [last 15 messages]. What do you do?"
        2. Send prompt to local LLM (Ollama)
        3. Parse the JSON response → post / comment / like / ignore
        4. Save to database + broadcast to UI via WebSocket
```

The LLM has **no memory between calls**. All context (who the agent is, what happened on the network) is reconstructed from the agent's persona config and a rolling window of recent messages. This keeps the prompt size constant regardless of how many iterations have passed.

### What Makes Agents Different From Each Other

Every agent sees the **same feed** but responds differently because of their unique prompt context:

| Agent Property | What It Does |
|---|---|
| `traits` | Shapes **how** they write (sarcastic, diplomatic, emotional...) |
| `background` | Gives the LLM **reasons** for their opinions |
| `current_focus` | Seeds their **first message** in the simulation |
| `opinion_stance` (-2 to +2) | Creates **disagreement** — agents on opposite ends will clash |
| `sentiment_bias` (-1 to +1) | Controls **tone** — same opinion can be said kindly or aggressively |

### What Emerges

With just 5 agents and 50 iterations, natural group dynamics emerge without any explicit programming:

- **Alliances** — agents with similar stances start supporting each other
- **Conflicts** — opposing stances lead to heated exchanges
- **Mediation** — neutral agents try to bridge the gap
- **Topic drift** — conversations evolve beyond the initial seed post

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  Browser (localhost:8000)                   │
│  Single-page UI with real-time feed         │
└──────────────┬──────────────────────────────┘
               │ WebSocket
┌──────────────▼──────────────────────────────┐
│  FastAPI Server                             │
│  Serves UI + manages WebSocket connections  │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│  Simulation Engine                          │
│  Sequential loop: agent → LLM → action      │
│  Manages feed (rolling window of 15 items)  │
└───────┬──────────────────┬──────────────────┘
        │                  │
┌───────▼───────┐  ┌───────▼───────┐
│  Ollama       │  │  SQLite       │
│  Local LLM    │  │  All actions  │
│  (llama3.1)   │  │  persisted    │
└───────────────┘  └───────────────┘
```

### Tech Stack

| Component | Technology | Why |
|---|---|---|
| LLM | Ollama + Llama 3.1 8B | Runs locally, no API keys, no cost |
| Agents | Custom Python classes | Lightweight — no LangChain overhead |
| Database | SQLAlchemy + SQLite | Zero setup, full history persisted |
| Web UI | FastAPI + WebSocket | Real-time streaming, no frontend build step |
| Config | YAML | Human-readable, easy to add/modify agents |
| Validation | Pydantic | Structured LLM output parsing |

---

## Project Structure

```
config/
├── settings.yaml              # Simulation settings (topic, model, iterations)
└── personas/                  # One YAML file per agent
    ├── marcus_webb.yaml
    ├── elena_novak.yaml
    ├── dr_raj_singh.yaml
    ├── kira_tanaka.yaml
    └── dave_cooper.yaml

src/
├── main.py                    # Entry point
├── agent/
│   ├── agent.py               # Agent class (persona + memory)
│   ├── memory.py              # Rolling memory window
│   └── actions.py             # Action types (post, comment, like, ignore)
├── simulation/
│   ├── engine.py              # Main simulation loop
│   └── feed.py                # Global feed manager
├── llm/
│   └── client.py              # Ollama client + prompt builder
├── database/
│   ├── models.py              # SQLAlchemy models
│   └── repository.py          # Database operations
└── web/
    ├── app.py                 # FastAPI application
    ├── websocket.py           # WebSocket connection manager
    └── static/
        └── index.html         # Single-page UI (dark theme)

data/
└── simulation.db              # SQLite database (auto-created, gitignored)
```

---

## Quick Start

### Prerequisites

- macOS (Apple Silicon recommended) or Linux
- [Conda](https://docs.conda.io/en/latest/miniconda.html) (Miniconda or Miniforge)
- [Ollama](https://ollama.ai) installed and running

### Setup

```bash
# 1. Create conda environment
bash _conda_install_env.sh

# 2. Install Python dependencies
bash _conda_install_python_requirements.sh

# 3. Run the application (downloads LLM model if needed)
bash run_app.sh
```

### Manual Setup

```bash
conda create -n ai-social-network python=3.13 -y
conda activate ai-social-network
pip install -r requirements.txt
ollama pull llama3.1:8b
python -m src.main
```

Then open **http://localhost:8000** in your browser.

### Controls

The UI provides three buttons:

| Button | What It Does |
|---|---|
| **New Simulation** | Starts a fresh session with a new ID. Feed is empty, seed post kicks off the conversation. |
| **Resume Last** | Loads the last session from the database, replays all previous messages in the UI, and continues from where it left off. |
| **Stop** | Stops the simulation at any point. Progress is saved — you can resume later. |

Every simulation run is tagged with a unique `session_id` in the database, so conversations from different runs never mix. You can stop a simulation at iteration 12, close everything, come back later, and click **Resume Last** to continue from iteration 13.

---

## Creating Your Own Agents

Add a new YAML file to `config/personas/`:

```yaml
name: "Your Agent Name"
age: 30
traits: "curious, skeptical, witty"
background: >
  A brief paragraph about who this person is, what they do,
  and why they hold their opinions. The more specific, the
  more interesting the conversations.
current_focus: "What they're thinking about right now — this seeds their first message."
opinion_stance: 1      # -2 (strongly against) to +2 (strongly for)
sentiment_bias: 0.3    # -1.0 (negative tone) to +1.0 (positive tone)
```

### Tips for Interesting Conversations

- **Spread opinion stances across the spectrum** — if everyone agrees, nothing happens
- **Give agents personal stakes** — "lost my job" hits harder than "the economy is bad"
- **Mix ages and backgrounds** — a 19-year-old student and a 52-year-old CEO see the world differently
- **Use `current_focus` wisely** — it drives the first iteration; make it specific and provocative

### Changing the Topic

Edit `config/settings.yaml`:

```yaml
simulation:
  topic: "Your debate topic here — frame it as a question for best results"
  iterations: 50
  model: "llama3.1:8b"
  seed_post:
    agent: "file_name_without_extension"
    content: "A provocative opening post to kick off the discussion."
```

---

## Accessing Conversation History

All messages are stored in `data/simulation.db`. Query with any SQLite client:

```sql
-- Full conversation timeline
SELECT iteration, agent_name, action, target_agent, content
FROM posts
ORDER BY id;

-- Only posts and comments (skip likes and ignores)
SELECT iteration, agent_name, content, target_agent
FROM posts
WHERE action IN ('post', 'comment')
ORDER BY id;

-- What did a specific agent say?
SELECT iteration, action, content
FROM posts
WHERE agent_name = 'Elena Novak'
ORDER BY id;
```

---

## How This Differs From Other Approaches

| Approach | Complexity | Scale | This Project |
|---|---|---|---|
| LangChain agents | Heavy (tools, chains, vector stores) | ~10 agents | No LangChain |
| OASIS / CAMEL-AI | Full framework (23 actions, recommendations) | Up to 1M agents | Custom lightweight |
| Stanford Generative Agents | Research-grade (reflection, planning) | 25 agents | Simplified memory |
| **This project** | **Minimal (persona + 1 LLM call)** | **5-20 agents** | **You are here** |

The goal is not scale — it's **understanding**. Every line of code is readable, every decision is traceable, and you can modify any part without fighting a framework.

---

## Inspired By

- [Stanford Generative Agents](https://arxiv.org/abs/2304.03442) — the original "AI town" paper
- [OASIS (CAMEL-AI)](https://github.com/camel-ai/oasis) — large-scale social simulation engine
- [MiroFish](https://github.com/666ghj/MiroFish) — prediction engine built on OASIS

---

## License

MIT — Peter Baksa, 2026
