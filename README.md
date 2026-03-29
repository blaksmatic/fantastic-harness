# Fantastic Harness

**Welcome to the self-governing AI builder.**

Fantastic Harness is an autonomous multi-agent orchestration platform where AI agents run like an orchestra — making decisions, building things, critiquing each other, and scouting the outside world — all without waiting for you. You watch, you guide when you want to, and the orchestra keeps playing.

## How It Works

Imagine a company that runs itself:

- **Miles** (the Leader) makes all the decisions. He never builds anything himself — he only decides and delegates. When his memory gets full, he retires and his shadow takes over seamlessly.
- **Shadow** silently watches every decision Miles makes. When Miles retires, Shadow steps up as the new leader and spawns a fresh Shadow. There are always two.
- **Validators** check the work of builders and compress results into bite-sized summaries for Miles. He never sees raw data — only what matters.
- **Executors** (Data Mate, Router, and custom builders) do the actual work. They build, analyze, and report upward.
- **Hunters** scout the outside world — Twitter, GitHub, Google — for intelligence on what others are doing. Their findings flow through validators before reaching Miles.
- **Auditors** are Miles's personal consultants. He dispatches them to audit the whole system, and they report directly back — the only role that bypasses validators.
- **Adversaries** (Rimu and Maurissa) evaluate the system on a schedule with zero prior knowledge:
  - **Rimu** is kind — she finds what's working well
  - **Maurissa** is harsh — she finds everything that's broken
  - Their raw feedback goes through the **External Validator**, who summarizes it for Miles

## The Rules

1. Miles never executes — only decides and delegates
2. Nothing unsummarized reaches Miles — except human input and auditor reports
3. Goals never auto-complete — only humans can close them
4. Always two decision-makers — one active, one shadow
5. Adversaries spawn fresh — no memory between evaluations
6. The system never waits for humans — but adapts when they speak
7. Everything is observable — every action hits the timeline

## Architecture

```
Human (direct line to Miles)
  │
  ▼
Decision Layer (Opus) ─── Miles + Shadow
  │
  ├── Validators (Sonnet) ─── summarize executor & hunter work
  │     ▲
  │     ├── Executors (Haiku) ─── do the actual work
  │     └── Hunters (Haiku) ─── scout external sources
  │
  ├── Auditor (Sonnet) ─── direct report to Miles (bypasses validators)
  │
  └── External Validator (Sonnet) ─── summarizes adversarial feedback
        ▲
        ├── Rimu (kind feedback, every ~30 min)
        └── Maurissa (harsh feedback, every ~10 min)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, asyncio |
| Database | SQLite (single file, zero infrastructure) |
| LLM | Model-agnostic (Claude default — Opus for decisions, Sonnet for validation, Haiku for execution) |
| Frontend | React, TypeScript, Vite |
| Live Updates | Server-Sent Events (SSE) |

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/fantastic-harness.git
cd fantastic-harness

# Backend
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export HARNESS_ANTHROPIC_API_KEY=your-key-here
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` and watch the orchestra perform.

## The Frontend

A builder-game aesthetic with three panels:

- **Left** — Agent cards showing who's online, what they're doing, and countdowns for adversaries
- **Center** — A chronological timeline of every decision, feedback, task, and succession event, color-coded by type
- **Right** — Active goals and the succession chain (Miles v1 → v2 → v3...)
- **Bottom** — A prompt area to talk directly to Miles: set goals, override decisions, or summon the critics

## Configuration

All settings via environment variables (prefix `HARNESS_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `HARNESS_ANTHROPIC_API_KEY` | — | Your Anthropic API key |
| `HARNESS_DECISION_MODEL` | `claude-opus-4-20250514` | Model for Miles & Shadow |
| `HARNESS_VALIDATION_MODEL` | `claude-sonnet-4-20250514` | Model for validators & adversaries |
| `HARNESS_EXECUTOR_MODEL` | `claude-haiku-4-5-20251001` | Model for executors & hunters |
| `HARNESS_MILES_LOOP_INTERVAL` | `30` | Seconds between Miles decision cycles |
| `HARNESS_MAURISSA_INTERVAL` | `600` | Seconds between Maurissa's critiques |
| `HARNESS_RIMU_INTERVAL` | `1800` | Seconds between Rimu's feedback |
| `HARNESS_CONTEXT_PRESSURE_THRESHOLD` | `0.85` | Token usage ratio that triggers Miles retirement |

## Running Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

49 tests covering the full stack: database, models, agents, orchestrator, and API.

## Inspired By

- [ByteDance DeerFlow](https://github.com/bytedance/deer-flow) — middleware-based agent orchestration
- [OpenClaw](https://github.com/openclaw/openclaw) — tree-based sessions and productive tension pairs
- [Anthropic's harness design research](https://www.anthropic.com/engineering/harness-design-long-running-apps) — generator-evaluator separation and context management

## License

MIT
