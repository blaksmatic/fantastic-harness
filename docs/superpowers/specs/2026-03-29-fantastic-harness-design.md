# Fantastic Harness — Design Spec

An autonomous multi-agent orchestration platform modeled as an orchestra. Agents operate continuously without waiting for humans. Humans observe and can override, but never block progress.

## Core Concepts

### The Orchestra Metaphor

The system is a corporate hierarchy where information flows upward through summarization layers. Only minimal, processed information reaches the decision-maker.

### Always-On Design

Goals never auto-complete. Miles stays online indefinitely, waiting for new work or adversarial feedback. Only humans can close a goal. This is the opposite of most agent frameworks that race to "done."

## Architecture

### Stack

- **Backend:** Python (FastAPI)
- **Frontend:** React
- **Coordination:** SQLite (single file, no infrastructure dependencies)
- **LLM:** Model-agnostic with smart defaults (Claude Opus for decision layer, Sonnet for validation/adversary, Haiku for executors)

### Four Layers

#### 1. Decision Layer (Opus)

**Miles** (active leader) and **Shadow** (passive observer).

- Miles only makes decisions — never executes work
- Miles reads only summarized information from validators and Dark Horn
- Shadow silently reads Miles's journal, building context
- When Miles retires, Shadow is promoted and spawns a new Shadow
- There are always exactly two: one active, one shadow

The only unsummarized input Miles receives is from humans.

#### 2. Validation Layer (Sonnet)

Validators sit between executors and Miles. One validator per domain.

- Check executor work for correctness
- Compress raw results into minimal summaries
- Only the summary reaches Miles
- Extensible — users add validators as needed

#### 3. Executor Layer (Haiku)

Workers that do the actual work: Data Mate (data tasks), Router (infrastructure), Hunter (exploration), and user-defined builders.

- Spawned and killed by Miles's decisions
- Report raw results upward to their assigned validator
- Never communicate directly with Miles

#### 4. Adversary Layer (Sonnet, independent)

Adversaries evaluate the system on a configurable schedule.

- **Rimu** — kind, positive feedback. Less frequent (~30 min default)
- **Maurissa** — harsh, critical feedback. More frequent (~10 min default)
- Each adversary spawns fresh with NO prior context — evaluates from scratch
- Raw feedback goes to **Dark Horn**, who summarizes and passes to Miles
- Dark Horn is the adversary-side equivalent of a validator
- Humans can trigger adversaries manually and configure schedules

### Information Flow Rule

Nothing reaches Miles unsummarized except human input:

- Executor work → Validator → summary → Miles
- Adversarial feedback → Dark Horn → summary → Miles
- Human input → Miles directly

This keeps Miles's context clean and extends his lifetime before retirement.

## Startup Flow

1. System boots, spawns Miles v1 + Shadow v1
2. Miles asks user onboarding questions
3. User provides a goal OR selects "self-explore"
   - If goal: Miles writes to goals table, starts delegating tasks
   - If self-explore: Miles spawns Hunter agents to explore and report back

## Miles's Decision Loop

Runs continuously:

1. Read new validator summaries from tasks table
2. Read new Dark Horn summaries from feedback table
3. Read any human input
4. Make decisions — write to journal
5. Delegate new work — create tasks for executors
6. Respond to feedback — accept or reject
7. Check context pressure — retire if threshold reached
8. Loop

## Shadow's Observation Loop

Runs passively:

1. Read Miles's new journal entries
2. Build internal understanding of decisions made
3. Wait for promotion signal
4. Loop

## Succession (Miles → Shadow Promotion)

Triggered by context pressure (token usage approaching limits), decision count thresholds, or Miles's own judgment.

When Miles retires:

1. Miles writes a final journal entry (compaction summary)
2. A succession record is created
3. Shadow is promoted to active Miles
4. A new Shadow is spawned
5. New Miles reads the compaction summary + recent journal entries
6. Decision loop continues seamlessly

The Shadow already has context from observing, so the transition has no cold-start problem.

## Adversary Schedule

- Maurissa fires more frequently (~10 min default) with harsh/critical evaluations
- Rimu fires less frequently (~30 min default) with kind/constructive feedback
- Each adversary instance spawns fresh — no memory of previous evaluations
- Dark Horn collects all raw feedback, summarizes patterns, and passes condensed reports to Miles
- All timings are configurable by humans via the frontend

## Data Model (SQLite)

### goals

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PK | Unique goal identifier |
| description | TEXT | What the user wants |
| status | TEXT | active / paused / completed |
| source | TEXT | "human" or "self_explore" |
| created_at | TIMESTAMP | When created |
| closed_at | TIMESTAMP | When closed (only by humans) |
| closed_by | TEXT | Always "human" when set |

### agents

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PK | Unique agent identifier |
| name | TEXT | Display name (e.g., "miles_v3") |
| role | TEXT | Specific role name |
| layer | TEXT | decision / validation / executor / adversary |
| model | TEXT | LLM model to use |
| status | TEXT | active / idle / retired |
| config | JSON | Schedule, personality, custom settings |
| created_at | TIMESTAMP | When spawned |
| retired_at | TIMESTAMP | When retired (if applicable) |

### journal

Miles's decision log — the backbone of succession.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing sequence |
| miles_id | TEXT | Which Miles wrote this entry |
| type | TEXT | decision / delegation / rejection / observation |
| content | TEXT | The actual decision or thought |
| context | TEXT | What information prompted this |
| goal_id | TEXT | Related goal (nullable) |
| created_at | TIMESTAMP | When written |

### tasks

Work delegated by Miles to executors.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PK | Unique task identifier |
| goal_id | TEXT | Parent goal |
| assigned_to | TEXT | Executor agent id |
| validator | TEXT | Validator agent id |
| description | TEXT | What to do |
| status | TEXT | pending / running / done / failed |
| result | TEXT | Raw executor output |
| summary | TEXT | Validator's summary for Miles |
| created_at | TIMESTAMP | When created |
| completed_at | TIMESTAMP | When completed |

### feedback

Adversarial evaluations.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PK | Unique feedback identifier |
| author | TEXT | "rimu", "maurissa", or "human" |
| type | TEXT | positive / negative |
| raw_content | TEXT | Full adversarial feedback |
| darkhorn_summary | TEXT | Dark Horn's condensed version |
| miles_response | TEXT | What Miles decided about it |
| goal_id | TEXT | Related goal (nullable) |
| status | TEXT | pending / reviewed / rejected |
| created_at | TIMESTAMP | When submitted |

### events

Timeline feed for the frontend.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing sequence |
| agent_id | TEXT | Who generated this event |
| type | TEXT | decision / feedback / task / promotion / retirement / human_input |
| content | TEXT | Display text |
| metadata | JSON | Extra data for rendering |
| created_at | TIMESTAMP | When it happened |

### succession

Miles → Shadow promotion history.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing sequence |
| retired_id | TEXT | Miles who retired |
| promoted_id | TEXT | Shadow who became Miles |
| new_shadow_id | TEXT | Newly spawned Shadow |
| compaction | TEXT | Compressed state summary |
| journal_start | INTEGER | Journal id where new Miles should start reading |
| created_at | TIMESTAMP | When succession occurred |

## Frontend

Builder-game aesthetic with three panels:

### Left Panel — Agent Cards

Each agent displayed as a card showing:
- Name and version (e.g., "Miles v3")
- Status badge (ACTIVE / WORKING / WATCHING / IDLE)
- Layer and model info
- Current activity or countdown to next action (for adversaries)

### Center — Timeline Feed

Chronological feed of all system activity, color-coded by type:
- Purple: Miles decisions
- Orange: Adversarial feedback (Dark Horn summaries)
- Cyan: Task completions (validator summaries)
- Green: Human input
- Red: Succession events

### Right Panel — Goals & Succession

- Active and queued goals with task counts
- Succession history (Miles v1 → v2 → v3...)

### Bottom — Prompt Area

Text input that sends messages directly to Miles. Used to:
- Override decisions
- Set or modify goals
- Trigger adversaries manually
- Provide guidance

### Live Updates

Backend pushes events to the frontend via SSE (Server-Sent Events). The frontend subscribes to the event stream and renders new entries in real-time.

## Backend API (FastAPI)

### REST Endpoints

- `POST /goals` — create a new goal
- `GET /goals` — list all goals
- `PATCH /goals/{id}` — update/close a goal
- `GET /events` — list events (paginated)
- `GET /events/stream` — SSE stream for live updates
- `GET /agents` — list all agents with status
- `PATCH /agents/{id}/config` — update agent config (schedules, etc.)
- `POST /input` — send human input to Miles
- `POST /adversaries/trigger` — manually trigger an adversary run
- `GET /journal` — read Miles's decision journal
- `GET /succession` — succession history

### Orchestrator

Python scheduler (asyncio-based) that manages:
- Miles's decision loop (continuous)
- Shadow's observation loop (continuous)
- Adversary schedules (configurable intervals)
- Executor lifecycle (spawn/monitor/cleanup)
- Validator invocations (triggered when executors complete)
- Dark Horn summarization (triggered when adversaries complete)

## LLM Provider Layer

Model-agnostic abstraction supporting multiple providers:

- **Default provider:** Anthropic (Claude)
- **Default models:**
  - Decision layer: Claude Opus
  - Validation layer: Claude Sonnet
  - Adversary layer: Claude Sonnet
  - Executor layer: Claude Haiku
- Configurable per agent via the agents table
- Provider interface supports: Anthropic, OpenAI, and local models

## Project Structure

```
fantastic-harness/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── api/                  # REST endpoints
│   │   ├── db/                   # SQLite schema, migrations, queries
│   │   ├── orchestrator/         # Scheduler, agent loops
│   │   ├── agents/               # Agent definitions and prompts
│   │   │   ├── miles.py          # Miles decision loop
│   │   │   ├── shadow.py         # Shadow observation loop
│   │   │   ├── validator.py      # Validator logic
│   │   │   ├── executor.py       # Base executor
│   │   │   ├── adversary.py      # Adversary base (Rimu, Maurissa)
│   │   │   └── darkhorn.py       # Dark Horn summarizer
│   │   ├── llm/                  # LLM provider abstraction
│   │   │   ├── base.py           # Provider interface
│   │   │   ├── anthropic.py      # Claude provider
│   │   │   ├── openai.py         # OpenAI provider
│   │   │   └── local.py          # Local model provider
│   │   └── models/               # Pydantic models
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentPanel.tsx     # Left panel agent cards
│   │   │   ├── Timeline.tsx       # Center timeline feed
│   │   │   ├── GoalPanel.tsx      # Right panel goals
│   │   │   ├── PromptArea.tsx     # Bottom input area
│   │   │   └── SuccessionBadge.tsx
│   │   ├── hooks/
│   │   │   └── useEventStream.ts  # SSE subscription
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── tsconfig.json
├── harness.db                     # SQLite database (created at runtime)
└── docs/
```

## Design Invariants

1. **Miles never executes** — only decides and delegates
2. **Nothing unsummarized reaches Miles** — except human input
3. **Goals never auto-complete** — only humans close goals
4. **Always two decision-makers** — one active, one shadow
5. **Adversaries spawn fresh** — no memory between evaluations
6. **The system never waits for humans** — but adapts when humans provide input
7. **All activity is observable** — every action logged to the events table
