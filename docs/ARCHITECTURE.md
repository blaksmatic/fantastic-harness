# Architecture

Fantastic Harness is a six-layer autonomous agent orchestration platform. This document covers every layer, how they connect, and why things are the way they are.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                         │
│   AgentPanel │ Timeline Feed │ GoalPanel │ PromptArea       │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST + SSE
┌──────────────────────┴──────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  Orchestrator                         │  │
│  │  Manages all agent lifecycles, schedules, succession  │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────┴───────────────────────────────────┐  │
│  │                  Agent Layer                           │  │
│  │  Miles │ Shadow │ Validators │ Executors │ Hunters     │  │
│  │  Auditor │ Adversaries │ External Validator            │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────┴───────────────────────────────────┐  │
│  │               SQLite Database                          │  │
│  │  goals │ agents │ journal │ tasks │ feedback           │  │
│  │  audits │ scouting │ events │ succession               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            LLM Provider Layer                          │  │
│  │  Anthropic (default) │ OpenAI │ Local models           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## The Six Layers

### 1. Decision Layer — Miles + Shadow (Opus)

Miles is the leader. He reads summarized information, makes decisions, and delegates work. He never executes anything himself.

Shadow silently reads Miles's journal entries, building context over time. When Miles retires (due to context pressure, decision count, or his own judgment), Shadow is promoted to the new Miles and a fresh Shadow is spawned. There are always exactly two.

**Why two?** The shadow solves the cold-start problem. Traditional agent handoffs require serializing state into a handoff document, which loses nuance. Shadow has been watching the whole time — when promoted, it already understands the decisions and their reasoning.

**Succession flow:**
```
Miles v1 (active) + Shadow v1 (watching)
  → Miles v1 retires, writes compaction summary
  → Shadow v1 promoted to Miles v2
  → Shadow v2 spawned
  → Miles v2 continues decision loop
```

**Files:** `agents/miles.py`, `agents/shadow.py`, `orchestrator/succession.py`

### 2. Validation Layer — Validators + External Validator (Sonnet)

Validators sit between workers and Miles. Their only job is to compress raw results into minimal summaries. This is the gatekeeping principle: nothing unsummarized reaches Miles (except human input and auditor reports).

There are two kinds:
- **Validators** summarize executor and hunter work
- **External Validator** summarizes adversarial feedback

**Why separate the External Validator?** Adversarial feedback has a different structure (positive/negative evaluations) than task results. The External Validator specializes in identifying patterns across multiple adversary evaluations and distilling them into actionable summaries.

**Files:** `agents/validator.py`, `agents/external_validator.py`

### 3. Executor Layer (Haiku)

Executors do the actual work — data analysis, infrastructure tasks, custom building. They are ephemeral: spawned for a task, execute it, report the raw result, and retire.

Executors never communicate directly with Miles. Their results go to a validator, who summarizes them.

**Files:** `agents/executor.py`

### 4. Hunter Layer (Haiku)

Hunters scout external sources (Twitter, GitHub, Google) on a configurable schedule. They can also be dispatched on-demand by Miles.

Like executors, their raw findings go through validators before reaching Miles. Hunters are distinct from executors: executors build things, hunters scout the outside world.

**Files:** `agents/hunter.py`

### 5. Auditor Layer (Sonnet)

The auditor is Miles's personal consultant. Dispatched directly by Miles to independently audit the system — what executors have built, what validators are reporting, overall health.

**The auditor is the only non-human role that bypasses the validation layer.** This is intentional: validators cannot audit themselves. The auditor reports directly to Miles with unfiltered findings.

Auditors are one-shot: spawned, audit, report, destroyed.

**Files:** `agents/auditor.py`

### 6. Adversary Layer (Sonnet)

Adversaries evaluate the system on a configurable schedule with zero prior context. Each instance spawns fresh, evaluates, and is destroyed.

- **Rimu** — kind, constructive feedback (default: every 30 minutes)
- **Maurissa** — harsh, finds everything wrong (default: every 10 minutes)

Their raw feedback goes to the External Validator, who summarizes it for Miles. Humans can trigger adversaries manually and configure schedules.

**Why spawn fresh each time?** If adversaries accumulated memory, they'd develop blind spots — accepting things they've already seen as "normal." Fresh evaluation ensures genuine outsider perspective every time.

**Files:** `agents/adversary.py`

## Information Flow

```
Executor work ──► Validator ──► summary ──► Miles
Hunter intel  ──► Validator ──► summary ──► Miles
Adversary     ──► External Validator ──► summary ──► Miles
Auditor       ──────────────────────────► Miles (direct)
Human         ──────────────────────────► Miles (direct)
```

Only two channels bypass summarization: auditor reports and human input. Everything else is compressed before reaching the decision layer. This keeps Miles's context clean and extends his lifetime before retirement.

## Database Schema

SQLite with 9 tables. All agent coordination happens through the database — no message queues, no shared memory.

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `goals` | What the system is working toward | `id`, `description`, `status`, `closed_by` |
| `agents` | Registry of all agents | `id`, `name`, `role`, `layer`, `model`, `status` |
| `journal` | Miles's decision log (succession backbone) | `miles_id`, `type`, `content`, `context` |
| `tasks` | Work delegated to executors | `result` (raw), `summary` (for Miles) |
| `feedback` | Adversarial evaluations | `raw_content`, `external_validator_summary` |
| `audits` | Auditor reports (direct to Miles) | `auditor_id`, `miles_id`, `findings` |
| `scouting` | Hunter intelligence missions | `source`, `topic`, `raw_findings`, `summary` |
| `events` | Timeline feed for frontend | `agent_id`, `type`, `content`, `metadata` |
| `succession` | Miles → Shadow promotion history | `retired_id`, `promoted_id`, `compaction` |

### Key Design Decisions

**`tasks` has both `result` and `summary`:** The executor writes raw output to `result`. The validator reads it and writes a compressed version to `summary`. Miles only reads `summary`.

**`feedback` has both `raw_content` and `external_validator_summary`:** Same pattern. Adversaries write raw feedback. External Validator compresses it.

**`journal` is the succession backbone:** Shadow reads journal entries to build context. When promoted, the new Miles can reconstruct the decision history from the journal. The `succession` table records where each new Miles should start reading.

**`events` is the frontend's data source:** Every meaningful action in the system creates an event. The frontend polls this table (and can subscribe via SSE) for real-time updates.

## Orchestrator

The orchestrator (`orchestrator/scheduler.py`) is an asyncio-based scheduler that manages:

- **Miles's decision loop** — continuous, configurable interval (default: 30s)
- **Shadow's observation loop** — continuous, reads new journal entries
- **Adversary schedules** — Maurissa every 10 min, Rimu every 30 min
- **Executor lifecycle** — spawn per task, retire after completion
- **Hunter schedules** — configurable per source
- **Validator invocations** — triggered when executors or hunters complete
- **External Validator** — triggered when adversaries complete
- **Succession** — automatic when Miles's context pressure exceeds threshold

The orchestrator starts when the FastAPI app boots (if an API key is configured) and runs until shutdown.

## REST API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/goals` | Create a new goal |
| `GET` | `/goals` | List all goals (filterable by status) |
| `PATCH` | `/goals/{id}` | Update/close a goal |
| `GET` | `/agents` | List agents (filterable by layer, status) |
| `PATCH` | `/agents/{id}/config` | Update agent configuration |
| `GET` | `/events` | List events (paginated, filterable) |
| `GET` | `/events/stream` | SSE stream for real-time events |
| `POST` | `/input` | Send human input to Miles |
| `POST` | `/adversaries/trigger` | Manually trigger an adversary |
| `GET` | `/journal` | Read Miles's decision journal |
| `GET` | `/succession` | View succession history |

## Frontend

React + TypeScript + Vite. Builder-game aesthetic with dark theme.

### Components

| Component | Panel | Purpose |
|-----------|-------|---------|
| `AgentPanel` | Left | Agent cards with status, layer, model info |
| `Timeline` | Center | Chronological event feed, color-coded by type |
| `GoalPanel` | Right | Active goals + succession chain |
| `PromptArea` | Bottom | Text input → POST `/input` → Miles |

### Color Coding

| Event Type | Color |
|------------|-------|
| Decision | Purple `#8b5cf6` |
| Feedback | Orange `#f59e0b` |
| Task | Cyan `#22d3ee` |
| Scouting | Blue `#3b82f6` |
| Audit | Pink `#ec4899` |
| Succession | Red `#ef4444` |
| Human Input | Green `#22c55e` |

### Data Flow

The frontend polls the backend every 3 seconds for events, agents, goals, and succession data. An SSE hook (`useEventStream`) is available for real-time streaming as an alternative.

## LLM Provider Layer

Model-agnostic abstraction with a `LLMProvider` protocol:

```python
class LLMProvider(Protocol):
    async def complete(self, system_prompt: str, user_message: str,
                       model: str, max_tokens: int = 4096) -> LLMResponse: ...
```

Default implementation wraps the Anthropic SDK. Adding a new provider means implementing one method.

### Default Model Assignment

| Layer | Model | Why |
|-------|-------|-----|
| Decision (Miles, Shadow) | Claude Opus | Best reasoning for decisions |
| Validation, Adversary, Auditor | Claude Sonnet | Good judgment, lower cost |
| Executor, Hunter | Claude Haiku | Fast and cheap for task execution |

## Context Management and Succession

Miles tracks his token usage across all `think()` calls. When usage exceeds the threshold (default: 85% of 1M context), or when decision count exceeds the limit (default: 200), Miles retires.

The succession mechanism:

1. Miles writes a final compaction summary to the journal
2. A `succession` record is created with `journal_start` pointing to where the new Miles should begin reading
3. Shadow is promoted: its DB record is updated from role `shadow` to `miles`
4. A new Shadow is spawned and registered
5. The new Miles inherits Shadow's token counts (it's been reading the journal, so it already has context)
6. The decision loop continues without interruption

The Shadow's `last_journal_id` cursor means it only reads new entries — no re-reading the entire history on each cycle.
