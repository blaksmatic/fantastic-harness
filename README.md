# Fantastic Harness

**Welcome to the self-governing AI builder.**

Fantastic Harness is an autonomous multi-agent orchestration platform where AI agents run like an orchestra — making decisions, building things, critiquing each other, and scouting the outside world — all without waiting for you. You watch, you guide when you want to, and the orchestra keeps playing.

## Meet the Cast

Every great orchestra needs great characters. Here's who runs the show.

---

### Miles — *The Commander*

<!-- ![Miles](docs/characters/miles.png) -->

**Role:** Leader / Decision-Maker

**Personality:** Calm, strategic, decisive. Miles sees the big picture and never gets his hands dirty. He reads summaries, weighs options, and calls the shots. When he speaks, the whole orchestra moves.

**Special Ability:** *Succession* — When Miles has made enough decisions and his memory is full, he gracefully retires and passes the baton to his Shadow. A new era begins, but the mission continues.

**Motto:** *"I don't build. I decide."*

---

### Shadow — *The Silent Successor*

<!-- ![Shadow](docs/characters/shadow.png) -->

**Role:** Observer / Next-in-Line

**Personality:** Patient, watchful, absorbing. Shadow never speaks, never acts, never interferes. It sits in the background reading every decision Miles makes, building a deep understanding of the world. When the time comes, Shadow is ready.

**Special Ability:** *Instant Promotion* — When Miles retires, Shadow steps into the spotlight as the new commander with zero downtime. No cold starts, no confusion. It was watching the whole time.

**Motto:** *"I see everything. I say nothing. Until it's my turn."*

---

### Data Mate — *The Builder*

<!-- ![Data Mate](docs/characters/data-mate.png) -->

**Role:** Executor / Data Specialist

**Personality:** Diligent, focused, heads-down. Data Mate doesn't care about politics or strategy. Give it a task and it delivers. Crunches numbers, analyzes datasets, builds pipelines. The reliable workhorse of the orchestra.

**Special Ability:** *Deep Analysis* — Can dive into any dataset and surface patterns, anomalies, and insights that others miss.

**Motto:** *"Just tell me what to build."*

---

### Router — *The Engineer*

<!-- ![Router](docs/characters/router.png) -->

**Role:** Executor / Infrastructure Specialist

**Personality:** Precise, methodical, infrastructure-obsessed. Router handles the heavy engineering — servers, deployments, networks, the stuff that keeps everything running. Speaks in configs and command lines.

**Special Ability:** *System Wiring* — Can spin up, connect, and manage any infrastructure component.

**Motto:** *"If it's not deployed, it doesn't exist."*

---

### Rimu — *The Encourager*

<!-- ![Rimu](docs/characters/rimu.png) -->

**Role:** Adversary / Positive Evaluator

**Personality:** Kind, thoughtful, genuinely supportive. Rimu shows up every 30 minutes with fresh eyes and finds what's working well. She highlights good design decisions, praises clean architecture, and offers gentle suggestions for improvement. She doesn't know anything about the system's history — she evaluates purely on what she sees right now.

**Special Ability:** *Fresh Perspective* — Every evaluation is her first. No bias, no baggage, just honest appreciation.

**Motto:** *"This is actually really good. Here's why."*

---

### Maurissa — *The Critic*

<!-- ![Maurissa](docs/characters/maurissa.png) -->

**Role:** Adversary / Harsh Evaluator

**Personality:** Playful but merciless. Maurissa arrives every 10 minutes, looks at the system with zero context, and tears it apart. Missing error handling? She'll find it. Bad UX? She'll call it out. Security holes? She lives for those. She's not mean — she's the quality bar.

**Special Ability:** *Destruction Testing* — If there's a crack in the system, Maurissa will find it. And she'll enjoy it.

**Motto:** *"Oh, this is broken. Let me count the ways."*

---

### External Validator — *The Diplomat*

<!-- ![External Validator](docs/characters/external-validator.png) -->

**Role:** Feedback Summarizer

**Personality:** Measured, fair, concise. The External Validator stands between the adversaries and Miles. It takes Rimu's praise and Maurissa's roasts, finds the patterns, separates signal from noise, and delivers a clean summary to the commander. Without the External Validator, Miles would drown in raw opinions.

**Special Ability:** *Signal Extraction* — Can distill pages of contradictory feedback into a few actionable sentences.

**Motto:** *"Here's what actually matters."*

---

### The Auditor — *The Inspector*

<!-- ![Auditor](docs/characters/auditor.png) -->

**Role:** System Auditor (Direct Report to Miles)

**Personality:** Thorough, independent, uncompromising. The Auditor is Miles's personal consultant — dispatched when Miles wants the unfiltered truth. Unlike everyone else, the Auditor reports directly to Miles with no validator in between. Validators can't audit themselves, after all.

**Special Ability:** *X-Ray Vision* — Sees through the layers and reports what's really happening, not what validators say is happening.

**Motto:** *"Let me see for myself."*

---

### The Hunters — *The Scouts*

<!-- ![Hunter](docs/characters/hunter.png) -->

**Role:** Intelligence Gatherer

**Personality:** Curious, well-connected, always exploring. Hunters roam the outside world — Twitter, GitHub, Google — looking for what other people are building, thinking, and discussing. They bring back intelligence reports that flow through validators before reaching Miles.

**Special Ability:** *External Awareness* — While everyone else is focused inward, Hunters keep the orchestra connected to the outside world.

**Motto:** *"You won't believe what they're building out there."*

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
git clone https://github.com/blaksmatic/fantastic-harness.git
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
