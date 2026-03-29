# AGENTS.md — Guide for AI Agents Working on Fantastic Harness

Welcome. You're about to work on a self-governing multi-agent orchestration platform. This file tells you everything you need to know to contribute effectively.

## What This Project Is

Fantastic Harness is an autonomous AI orchestra. Multiple AI agents work together in a corporate hierarchy: a leader (Miles) makes decisions, validators filter information, executors do work, hunters scout externally, adversaries critique everything, and a shadow watches silently — ready to take over when the leader retires.

The key insight: **Miles never executes — he only decides.** Everything flows through summarization layers so the decision-maker only sees what matters.

## Project Structure

```
fantastic-harness/
├── backend/                     # Python FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI app with lifespan + orchestrator
│   │   ├── config.py            # Settings (models, schedules, thresholds)
│   │   ├── api/                 # REST endpoints (7 routers)
│   │   ├── db/                  # SQLite schema, connection, queries
│   │   ├── agents/              # All agent implementations
│   │   │   ├── base.py          # BaseAgent ABC
│   │   │   ├── miles.py         # Decision loop + context pressure
│   │   │   ├── shadow.py        # Journal observation loop
│   │   │   ├── validator.py     # Summarizes executor work for Miles
│   │   │   ├── executor.py      # Does assigned tasks
│   │   │   ├── hunter.py        # Scouts external sources
│   │   │   ├── auditor.py       # Direct audit reports to Miles
│   │   │   ├── adversary.py     # Rimu (kind) & Maurissa (harsh)
│   │   │   └── external_validator.py  # Summarizes adversary feedback
│   │   ├── orchestrator/        # Scheduler + succession mechanism
│   │   ├── llm/                 # LLM provider abstraction
│   │   └── models/              # Pydantic schemas
│   ├── tests/                   # pytest suite (49 tests)
│   └── requirements.txt
├── frontend/                    # React + TypeScript + Vite
│   └── src/
│       ├── components/          # AgentPanel, Timeline, GoalPanel, PromptArea
│       ├── hooks/               # useEventStream (SSE)
│       ├── api.ts               # Typed API client
│       └── types.ts             # TypeScript interfaces
└── docs/
    └── superpowers/
        ├── specs/               # Design spec
        └── plans/               # Implementation plan
```

## Architecture Invariants

These are non-negotiable. Do not break them:

1. **Miles never executes** — he delegates via the `tasks` table. If you find Miles doing work, that's a bug.
2. **Nothing unsummarized reaches Miles** — except human input and auditor reports. Validators and External Validator are the gatekeepers.
3. **Goals never auto-complete** — only humans close goals. The `closed_by` field must always be `"human"`.
4. **Always two decision-makers** — one active Miles, one Shadow. Succession creates a new Shadow immediately.
5. **Adversaries spawn fresh** — no memory between evaluations. Each adversary instance is created, evaluates, and is destroyed.
6. **All activity is observable** — every meaningful action must create a row in the `events` table.

## Agent Hierarchy

```
Human → Miles (Opus) + Shadow (Opus)
              │
              ├── Validators (Sonnet) ← Executors (Haiku)
              │                       ← Hunters (Haiku)
              ├── Auditor (Sonnet) [direct to Miles]
              └── External Validator (Sonnet) ← Adversaries (Sonnet)
```

Information flows UP through summarization. Raw data never reaches Miles.

## Database

SQLite with 8 tables + succession. All coordination happens through the DB — no message queues, no in-memory state sharing between agents.

Key tables:
- `journal` — Miles's decision log. The backbone of succession.
- `tasks` — has both `result` (raw executor output) and `summary` (validator's version for Miles)
- `feedback` — has `raw_content` (adversary) and `external_validator_summary` (for Miles)
- `events` — timeline feed for the frontend. Every agent logs here.

## How to Run Tests

```bash
cd backend
source .venv/bin/activate  # or use .venv/bin/python directly
python -m pytest tests/ -v
```

Tests use a temp SQLite DB per test (via `test_db` fixture in `conftest.py`). A `MockProvider` stands in for the LLM — no API calls needed.

## How to Add a New Agent Type

1. Create `backend/app/agents/your_agent.py` subclassing `BaseAgent`
2. Implement `system_prompt` property and `step()` method
3. Decide which layer it belongs to (executor, hunter, validator, adversary)
4. Register it in the orchestrator (`backend/app/orchestrator/scheduler.py`)
5. Add tests in `backend/tests/test_agents.py`
6. The agent should log events via `self.log_event()` for frontend visibility

## How to Add a New API Endpoint

1. Create a router in `backend/app/api/your_endpoint.py`
2. Register it in `backend/app/main.py` via `app.include_router()`
3. Add tests in `backend/tests/test_api.py`

## Conventions

- **Commits:** imperative mood, prefixed with `feat:`, `fix:`, `test:`, `docs:`
- **Agent IDs:** `{role}_{version_or_uuid}` (e.g., `miles_v1`, `hunter_a3f2b1`)
- **No global state beyond the DB** — agents coordinate through SQLite only
- **Each agent is ephemeral** — executors, hunters, auditors, and adversaries are created per-task and retired after
- **Miles and Shadow are persistent** — they run continuously until succession

## Working with Multiple Agents

If you're working alongside other agents on this codebase:
- Focus on your assigned files only
- Don't modify files outside your task scope
- Commit only your changes
- Don't create, apply, or drop git stashes (collision risk)
- Use the `tests/` directory to verify your changes don't break others' work
