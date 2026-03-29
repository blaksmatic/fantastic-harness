# Fantastic Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an autonomous multi-agent orchestration platform with a six-layer hierarchy (Decision, Validation, Executor, Hunter, Auditor, Adversary), SQLite coordination, and a React frontend with builder-game aesthetic.

**Architecture:** Python FastAPI backend with asyncio-based orchestrator managing agent lifecycles. SQLite single-file database for all coordination state. React frontend connected via REST + SSE for real-time event streaming. Model-agnostic LLM provider layer defaulting to Claude.

**Tech Stack:** Python 3.12+, FastAPI, SQLite (aiosqlite), Pydantic, Anthropic SDK, React 18, TypeScript, Vite, SSE

---

## File Structure

```
fantastic-harness/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app, lifespan, CORS
│   │   ├── config.py                  # Settings (models, schedules, DB path)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── goals.py               # POST/GET/PATCH /goals
│   │   │   ├── agents.py              # GET/PATCH /agents
│   │   │   ├── events.py              # GET /events, GET /events/stream (SSE)
│   │   │   ├── input.py               # POST /input (human → Miles)
│   │   │   ├── adversaries.py         # POST /adversaries/trigger
│   │   │   ├── journal.py             # GET /journal
│   │   │   └── succession.py          # GET /succession
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── schema.py              # CREATE TABLE statements
│   │   │   ├── connection.py          # aiosqlite connection management
│   │   │   └── queries.py             # All DB read/write functions
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # BaseAgent class
│   │   │   ├── miles.py               # Miles decision loop
│   │   │   ├── shadow.py              # Shadow observation loop
│   │   │   ├── validator.py           # Validator summarization
│   │   │   ├── executor.py            # Base executor
│   │   │   ├── hunter.py              # Hunter intelligence gatherer
│   │   │   ├── auditor.py             # Auditor (direct to Miles)
│   │   │   ├── adversary.py           # Rimu & Maurissa
│   │   │   └── external_validator.py  # External Validator (adversary → Miles)
│   │   ├── orchestrator/
│   │   │   ├── __init__.py
│   │   │   ├── scheduler.py           # Main scheduler loop
│   │   │   └── succession.py          # Miles retirement & promotion
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # LLMProvider protocol
│   │   │   └── anthropic.py           # Anthropic/Claude provider
│   │   └── models/
│   │       ├── __init__.py
│   │       └── schemas.py             # Pydantic models for all entities
│   ├── requirements.txt
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                # Shared fixtures (test DB, mock LLM)
│       ├── test_db.py                 # DB schema & query tests
│       ├── test_models.py             # Pydantic model tests
│       ├── test_llm.py                # LLM provider tests
│       ├── test_agents.py             # Agent logic tests
│       ├── test_orchestrator.py       # Scheduler & succession tests
│       └── test_api.py                # API endpoint tests
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── main.tsx
│   │   ├── api.ts                     # Backend API client
│   │   ├── types.ts                   # TypeScript types matching backend
│   │   ├── components/
│   │   │   ├── AgentPanel.tsx
│   │   │   ├── AgentPanel.css
│   │   │   ├── Timeline.tsx
│   │   │   ├── Timeline.css
│   │   │   ├── GoalPanel.tsx
│   │   │   ├── GoalPanel.css
│   │   │   ├── PromptArea.tsx
│   │   │   └── PromptArea.css
│   │   └── hooks/
│   │       └── useEventStream.ts      # SSE subscription hook
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── harness.db                          # Created at runtime
└── docs/
```

---

### Task 1: Project Scaffolding — Backend

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/main.py`
- Create: `backend/requirements.txt`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Create backend directory structure**

```bash
mkdir -p backend/app/api backend/app/db backend/app/agents backend/app/orchestrator backend/app/llm backend/app/models backend/tests
```

- [ ] **Step 2: Write requirements.txt**

Create `backend/requirements.txt`:

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
aiosqlite==0.20.0
pydantic==2.10.4
pydantic-settings==2.7.1
anthropic==0.43.0
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.25.0
sse-starlette==2.2.1
```

- [ ] **Step 3: Write config.py**

Create `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_path: str = "harness.db"

    # LLM defaults
    default_provider: str = "anthropic"
    decision_model: str = "claude-opus-4-20250514"
    validation_model: str = "claude-sonnet-4-20250514"
    adversary_model: str = "claude-sonnet-4-20250514"
    executor_model: str = "claude-haiku-4-5-20251001"
    hunter_model: str = "claude-haiku-4-5-20251001"
    auditor_model: str = "claude-sonnet-4-20250514"

    # Schedules (seconds)
    miles_loop_interval: int = 30
    shadow_loop_interval: int = 30
    maurissa_interval: int = 600       # 10 minutes
    rimu_interval: int = 1800          # 30 minutes
    hunter_interval: int = 3600        # 60 minutes

    # Succession
    context_pressure_threshold: float = 0.85  # retire at 85% context usage
    max_decisions_before_retire: int = 200

    # API
    anthropic_api_key: str = ""

    model_config = {"env_prefix": "HARNESS_"}


settings = Settings()
```

- [ ] **Step 4: Write main.py with FastAPI app**

Create `backend/app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.connection import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="Fantastic Harness", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Write __init__.py files and conftest.py**

Create empty `backend/app/__init__.py`, `backend/app/api/__init__.py`, `backend/app/db/__init__.py`, `backend/app/agents/__init__.py`, `backend/app/orchestrator/__init__.py`, `backend/app/llm/__init__.py`, `backend/app/models/__init__.py`, `backend/tests/__init__.py`.

Create `backend/tests/conftest.py`:

```python
import asyncio
import os
import tempfile
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.connection import close_db, get_db, init_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db(tmp_path) -> AsyncGenerator[str, None]:
    db_path = str(tmp_path / "test.db")
    os.environ["HARNESS_DB_PATH"] = db_path
    from app.config import Settings
    import app.config
    app.config.settings = Settings(db_path=db_path)
    await init_db()
    yield db_path
    await close_db()


@pytest_asyncio.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

- [ ] **Step 6: Verify setup**

Run: `cd backend && pip install -r requirements.txt`
Expected: all packages install successfully

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: scaffold backend with FastAPI, config, and test fixtures"
```

---

### Task 2: Database Schema & Connection

**Files:**
- Create: `backend/app/db/schema.py`
- Create: `backend/app/db/connection.py`
- Create: `backend/tests/test_db.py`

- [ ] **Step 1: Write the failing test for DB initialization**

Create `backend/tests/test_db.py`:

```python
import pytest
import pytest_asyncio
from app.db.connection import get_db


@pytest.mark.asyncio
async def test_tables_created(test_db):
    db = get_db()
    cursor = await db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in await cursor.fetchall()]
    expected = ["agents", "audits", "events", "feedback", "goals",
                "journal", "scouting", "succession", "tasks"]
    assert tables == expected


@pytest.mark.asyncio
async def test_insert_and_read_goal(test_db):
    db = get_db()
    await db.execute(
        "INSERT INTO goals (id, description, status, source, created_at) "
        "VALUES (?, ?, ?, ?, datetime('now'))",
        ("g1", "Build data pipeline", "active", "human"),
    )
    await db.commit()
    cursor = await db.execute("SELECT id, description, status FROM goals WHERE id = ?", ("g1",))
    row = await cursor.fetchone()
    assert row == ("g1", "Build data pipeline", "active")


@pytest.mark.asyncio
async def test_insert_and_read_event(test_db):
    db = get_db()
    await db.execute(
        "INSERT INTO events (agent_id, type, content, metadata, created_at) "
        "VALUES (?, ?, ?, ?, datetime('now'))",
        ("miles_v1", "decision", "Prioritize data pipeline", "{}"),
    )
    await db.commit()
    cursor = await db.execute("SELECT agent_id, type, content FROM events WHERE agent_id = ?", ("miles_v1",))
    row = await cursor.fetchone()
    assert row == ("miles_v1", "decision", "Prioritize data pipeline")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_db.py -v`
Expected: FAIL (modules don't exist yet)

- [ ] **Step 3: Write schema.py**

Create `backend/app/db/schema.py`:

```python
SCHEMA = """
CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    source TEXT NOT NULL DEFAULT 'human',
    created_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    closed_by TEXT
);

CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    layer TEXT NOT NULL,
    model TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'idle',
    config JSON DEFAULT '{}',
    created_at TIMESTAMP NOT NULL,
    retired_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    miles_id TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    context TEXT,
    goal_id TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (miles_id) REFERENCES agents(id),
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    goal_id TEXT,
    assigned_to TEXT,
    validator TEXT,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    result TEXT,
    summary TEXT,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals(id),
    FOREIGN KEY (assigned_to) REFERENCES agents(id),
    FOREIGN KEY (validator) REFERENCES agents(id)
);

CREATE TABLE IF NOT EXISTS feedback (
    id TEXT PRIMARY KEY,
    author TEXT NOT NULL,
    type TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    external_validator_summary TEXT,
    miles_response TEXT,
    goal_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

CREATE TABLE IF NOT EXISTS audits (
    id TEXT PRIMARY KEY,
    auditor_id TEXT NOT NULL,
    miles_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    findings TEXT,
    miles_response TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (auditor_id) REFERENCES agents(id),
    FOREIGN KEY (miles_id) REFERENCES agents(id)
);

CREATE TABLE IF NOT EXISTS scouting (
    id TEXT PRIMARY KEY,
    hunter_id TEXT NOT NULL,
    source TEXT NOT NULL,
    topic TEXT NOT NULL,
    raw_findings TEXT,
    summary TEXT,
    validator TEXT,
    goal_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (hunter_id) REFERENCES agents(id),
    FOREIGN KEY (validator) REFERENCES agents(id),
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSON DEFAULT '{}',
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS succession (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    retired_id TEXT NOT NULL,
    promoted_id TEXT NOT NULL,
    new_shadow_id TEXT NOT NULL,
    compaction TEXT,
    journal_start INTEGER,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (retired_id) REFERENCES agents(id),
    FOREIGN KEY (promoted_id) REFERENCES agents(id),
    FOREIGN KEY (new_shadow_id) REFERENCES agents(id)
);
"""
```

- [ ] **Step 4: Write connection.py**

Create `backend/app/db/connection.py`:

```python
import aiosqlite

from app.config import settings
from app.db.schema import SCHEMA

_db: aiosqlite.Connection | None = None


async def init_db() -> None:
    global _db
    _db = await aiosqlite.connect(settings.db_path)
    _db.row_factory = aiosqlite.Row
    await _db.executescript(SCHEMA)
    await _db.commit()


async def close_db() -> None:
    global _db
    if _db:
        await _db.close()
        _db = None


def get_db() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_db.py -v`
Expected: all 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/db/ backend/tests/test_db.py
git commit -m "feat: add SQLite schema with 8 tables and connection management"
```

---

### Task 3: Pydantic Models

**Files:**
- Create: `backend/app/models/schemas.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_models.py`:

```python
from datetime import datetime

from app.models.schemas import (
    Agent,
    AuditRecord,
    Event,
    Feedback,
    Goal,
    JournalEntry,
    ScoutingMission,
    SuccessionRecord,
    Task,
)


def test_goal_creation():
    goal = Goal(id="g1", description="Build pipeline", status="active", source="human")
    assert goal.id == "g1"
    assert goal.closed_at is None
    assert goal.closed_by is None


def test_agent_creation():
    agent = Agent(
        id="miles_v1", name="Miles v1", role="miles", layer="decision",
        model="claude-opus-4-20250514", status="active",
    )
    assert agent.layer == "decision"
    assert agent.config == {}


def test_journal_entry():
    entry = JournalEntry(
        miles_id="miles_v1", type="decision",
        content="Focus on data pipeline", context="User requested it",
    )
    assert entry.id is None  # assigned by DB
    assert entry.goal_id is None


def test_task_creation():
    task = Task(
        id="t1", description="Analyze dataset",
        assigned_to="datamate_1", validator="val_1",
    )
    assert task.status == "pending"
    assert task.result is None
    assert task.summary is None


def test_feedback_creation():
    fb = Feedback(
        id="f1", author="maurissa", type="negative",
        raw_content="The API has no error handling",
    )
    assert fb.status == "pending"
    assert fb.external_validator_summary is None


def test_event_creation():
    event = Event(
        agent_id="miles_v1", type="decision",
        content="Prioritize data pipeline",
    )
    assert event.metadata == {}


def test_audit_record():
    audit = AuditRecord(
        id="a1", auditor_id="auditor_1", miles_id="miles_v1",
        scope="full_system",
    )
    assert audit.status == "running"
    assert audit.findings is None


def test_scouting_mission():
    mission = ScoutingMission(
        id="s1", hunter_id="hunter_1", source="github",
        topic="multi-agent frameworks",
    )
    assert mission.status == "pending"
    assert mission.raw_findings is None


def test_succession_record():
    record = SuccessionRecord(
        retired_id="miles_v1", promoted_id="shadow_v1",
        new_shadow_id="shadow_v2", compaction="Summary of 50 decisions",
        journal_start=51,
    )
    assert record.id is None  # assigned by DB
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_models.py -v`
Expected: FAIL (module not found)

- [ ] **Step 3: Write schemas.py**

Create `backend/app/models/schemas.py`:

```python
from datetime import datetime

from pydantic import BaseModel, Field


class Goal(BaseModel):
    id: str
    description: str
    status: str = "active"
    source: str = "human"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: datetime | None = None
    closed_by: str | None = None


class Agent(BaseModel):
    id: str
    name: str
    role: str
    layer: str
    model: str
    status: str = "idle"
    config: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    retired_at: datetime | None = None


class JournalEntry(BaseModel):
    id: int | None = None
    miles_id: str
    type: str
    content: str
    context: str | None = None
    goal_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Task(BaseModel):
    id: str
    goal_id: str | None = None
    assigned_to: str | None = None
    validator: str | None = None
    description: str
    status: str = "pending"
    result: str | None = None
    summary: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class Feedback(BaseModel):
    id: str
    author: str
    type: str
    raw_content: str
    external_validator_summary: str | None = None
    miles_response: str | None = None
    goal_id: str | None = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditRecord(BaseModel):
    id: str
    auditor_id: str
    miles_id: str
    scope: str
    findings: str | None = None
    miles_response: str | None = None
    status: str = "running"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class ScoutingMission(BaseModel):
    id: str
    hunter_id: str
    source: str
    topic: str
    raw_findings: str | None = None
    summary: str | None = None
    validator: str | None = None
    goal_id: str | None = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class SuccessionRecord(BaseModel):
    id: int | None = None
    retired_id: str
    promoted_id: str
    new_shadow_id: str
    compaction: str | None = None
    journal_start: int | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Event(BaseModel):
    id: int | None = None
    agent_id: str
    type: str
    content: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_models.py -v`
Expected: all 9 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/ backend/tests/test_models.py
git commit -m "feat: add Pydantic models for all 8 entity types"
```

---

### Task 4: Database Query Layer

**Files:**
- Create: `backend/app/db/queries.py`
- Modify: `backend/tests/test_db.py`

- [ ] **Step 1: Write failing tests for query functions**

Append to `backend/tests/test_db.py`:

```python
from app.db import queries
from app.models.schemas import Agent, Event, Feedback, Goal, JournalEntry, Task


@pytest.mark.asyncio
async def test_create_and_get_goal(test_db):
    goal = Goal(id="g1", description="Build pipeline", source="human")
    await queries.create_goal(goal)
    result = await queries.get_goal("g1")
    assert result is not None
    assert result["description"] == "Build pipeline"


@pytest.mark.asyncio
async def test_list_active_goals(test_db):
    await queries.create_goal(Goal(id="g1", description="A", source="human"))
    await queries.create_goal(Goal(id="g2", description="B", source="human", status="completed"))
    active = await queries.list_goals(status="active")
    assert len(active) == 1
    assert active[0]["id"] == "g1"


@pytest.mark.asyncio
async def test_create_and_list_agents(test_db):
    agent = Agent(
        id="miles_v1", name="Miles v1", role="miles",
        layer="decision", model="opus", status="active",
    )
    await queries.create_agent(agent)
    agents = await queries.list_agents()
    assert len(agents) == 1
    assert agents[0]["name"] == "Miles v1"


@pytest.mark.asyncio
async def test_create_event_and_list(test_db):
    event = Event(agent_id="miles_v1", type="decision", content="Do X")
    await queries.create_event(event)
    events = await queries.list_events(limit=10)
    assert len(events) == 1
    assert events[0]["content"] == "Do X"


@pytest.mark.asyncio
async def test_create_journal_entry(test_db):
    entry = JournalEntry(
        miles_id="miles_v1", type="decision",
        content="Focus on pipeline", context="User said so",
    )
    entry_id = await queries.create_journal_entry(entry)
    assert entry_id >= 1
    entries = await queries.get_journal_entries(miles_id="miles_v1")
    assert len(entries) == 1


@pytest.mark.asyncio
async def test_create_task_and_update_status(test_db):
    task = Task(id="t1", description="Analyze data", assigned_to="dm1", validator="v1")
    await queries.create_task(task)
    await queries.update_task("t1", status="running")
    result = await queries.get_task("t1")
    assert result["status"] == "running"


@pytest.mark.asyncio
async def test_create_feedback(test_db):
    fb = Feedback(id="f1", author="maurissa", type="negative", raw_content="Bad API")
    await queries.create_feedback(fb)
    pending = await queries.get_pending_feedback()
    assert len(pending) == 1


@pytest.mark.asyncio
async def test_get_pending_task_summaries(test_db):
    task = Task(id="t1", description="Work", status="done", summary="All good")
    await queries.create_task(task)
    summaries = await queries.get_unread_task_summaries()
    assert len(summaries) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_db.py -v -k "test_create"`
Expected: FAIL (queries module doesn't exist)

- [ ] **Step 3: Write queries.py**

Create `backend/app/db/queries.py`:

```python
import json
from datetime import datetime

from app.db.connection import get_db
from app.models.schemas import (
    Agent,
    AuditRecord,
    Event,
    Feedback,
    Goal,
    JournalEntry,
    ScoutingMission,
    SuccessionRecord,
    Task,
)


# --- Goals ---

async def create_goal(goal: Goal) -> None:
    db = get_db()
    await db.execute(
        "INSERT INTO goals (id, description, status, source, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (goal.id, goal.description, goal.status, goal.source, goal.created_at.isoformat()),
    )
    await db.commit()


async def get_goal(goal_id: str) -> dict | None:
    db = get_db()
    cursor = await db.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def list_goals(status: str | None = None) -> list[dict]:
    db = get_db()
    if status:
        cursor = await db.execute("SELECT * FROM goals WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        cursor = await db.execute("SELECT * FROM goals ORDER BY created_at DESC")
    return [dict(r) for r in await cursor.fetchall()]


async def update_goal(goal_id: str, **kwargs) -> None:
    db = get_db()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [goal_id]
    await db.execute(f"UPDATE goals SET {sets} WHERE id = ?", vals)
    await db.commit()


# --- Agents ---

async def create_agent(agent: Agent) -> None:
    db = get_db()
    await db.execute(
        "INSERT INTO agents (id, name, role, layer, model, status, config, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (agent.id, agent.name, agent.role, agent.layer, agent.model,
         agent.status, json.dumps(agent.config), agent.created_at.isoformat()),
    )
    await db.commit()


async def list_agents(layer: str | None = None, status: str | None = None) -> list[dict]:
    db = get_db()
    conditions = []
    params = []
    if layer:
        conditions.append("layer = ?")
        params.append(layer)
    if status:
        conditions.append("status = ?")
        params.append(status)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    cursor = await db.execute(f"SELECT * FROM agents{where} ORDER BY created_at", params)
    return [dict(r) for r in await cursor.fetchall()]


async def update_agent(agent_id: str, **kwargs) -> None:
    db = get_db()
    if "config" in kwargs:
        kwargs["config"] = json.dumps(kwargs["config"])
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [agent_id]
    await db.execute(f"UPDATE agents SET {sets} WHERE id = ?", vals)
    await db.commit()


async def get_agent(agent_id: str) -> dict | None:
    db = get_db()
    cursor = await db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


# --- Journal ---

async def create_journal_entry(entry: JournalEntry) -> int:
    db = get_db()
    cursor = await db.execute(
        "INSERT INTO journal (miles_id, type, content, context, goal_id, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (entry.miles_id, entry.type, entry.content, entry.context,
         entry.goal_id, entry.created_at.isoformat()),
    )
    await db.commit()
    return cursor.lastrowid


async def get_journal_entries(
    miles_id: str | None = None, since_id: int | None = None, limit: int = 100,
) -> list[dict]:
    db = get_db()
    conditions = []
    params: list = []
    if miles_id:
        conditions.append("miles_id = ?")
        params.append(miles_id)
    if since_id is not None:
        conditions.append("id > ?")
        params.append(since_id)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    params.append(limit)
    cursor = await db.execute(
        f"SELECT * FROM journal{where} ORDER BY id DESC LIMIT ?", params,
    )
    return [dict(r) for r in await cursor.fetchall()]


# --- Tasks ---

async def create_task(task: Task) -> None:
    db = get_db()
    await db.execute(
        "INSERT INTO tasks (id, goal_id, assigned_to, validator, description, status, "
        "result, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (task.id, task.goal_id, task.assigned_to, task.validator, task.description,
         task.status, task.result, task.summary, task.created_at.isoformat()),
    )
    await db.commit()


async def get_task(task_id: str) -> dict | None:
    db = get_db()
    cursor = await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def update_task(task_id: str, **kwargs) -> None:
    db = get_db()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [task_id]
    await db.execute(f"UPDATE tasks SET {sets} WHERE id = ?", vals)
    await db.commit()


async def get_unread_task_summaries() -> list[dict]:
    db = get_db()
    cursor = await db.execute(
        "SELECT * FROM tasks WHERE status = 'done' AND summary IS NOT NULL "
        "ORDER BY completed_at",
    )
    return [dict(r) for r in await cursor.fetchall()]


# --- Feedback ---

async def create_feedback(fb: Feedback) -> None:
    db = get_db()
    await db.execute(
        "INSERT INTO feedback (id, author, type, raw_content, external_validator_summary, "
        "miles_response, goal_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (fb.id, fb.author, fb.type, fb.raw_content, fb.external_validator_summary,
         fb.miles_response, fb.goal_id, fb.status, fb.created_at.isoformat()),
    )
    await db.commit()


async def get_pending_feedback() -> list[dict]:
    db = get_db()
    cursor = await db.execute(
        "SELECT * FROM feedback WHERE status = 'pending' ORDER BY created_at",
    )
    return [dict(r) for r in await cursor.fetchall()]


async def update_feedback(feedback_id: str, **kwargs) -> None:
    db = get_db()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [feedback_id]
    await db.execute(f"UPDATE feedback SET {sets} WHERE id = ?", vals)
    await db.commit()


# --- Audits ---

async def create_audit(audit: AuditRecord) -> None:
    db = get_db()
    await db.execute(
        "INSERT INTO audits (id, auditor_id, miles_id, scope, findings, miles_response, "
        "status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (audit.id, audit.auditor_id, audit.miles_id, audit.scope,
         audit.findings, audit.miles_response, audit.status, audit.created_at.isoformat()),
    )
    await db.commit()


async def update_audit(audit_id: str, **kwargs) -> None:
    db = get_db()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [audit_id]
    await db.execute(f"UPDATE audits SET {sets} WHERE id = ?", vals)
    await db.commit()


# --- Scouting ---

async def create_scouting(mission: ScoutingMission) -> None:
    db = get_db()
    await db.execute(
        "INSERT INTO scouting (id, hunter_id, source, topic, raw_findings, summary, "
        "validator, goal_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (mission.id, mission.hunter_id, mission.source, mission.topic,
         mission.raw_findings, mission.summary, mission.validator,
         mission.goal_id, mission.status, mission.created_at.isoformat()),
    )
    await db.commit()


async def update_scouting(mission_id: str, **kwargs) -> None:
    db = get_db()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [mission_id]
    await db.execute(f"UPDATE scouting SET {sets} WHERE id = ?", vals)
    await db.commit()


# --- Events ---

async def create_event(event: Event) -> int:
    db = get_db()
    cursor = await db.execute(
        "INSERT INTO events (agent_id, type, content, metadata, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (event.agent_id, event.type, event.content,
         json.dumps(event.metadata), event.created_at.isoformat()),
    )
    await db.commit()
    return cursor.lastrowid


async def list_events(
    limit: int = 50, since_id: int | None = None, event_type: str | None = None,
) -> list[dict]:
    db = get_db()
    conditions = []
    params: list = []
    if since_id is not None:
        conditions.append("id > ?")
        params.append(since_id)
    if event_type:
        conditions.append("type = ?")
        params.append(event_type)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    params.append(limit)
    cursor = await db.execute(
        f"SELECT * FROM events{where} ORDER BY id DESC LIMIT ?", params,
    )
    return [dict(r) for r in await cursor.fetchall()]


# --- Succession ---

async def create_succession(record: SuccessionRecord) -> int:
    db = get_db()
    cursor = await db.execute(
        "INSERT INTO succession (retired_id, promoted_id, new_shadow_id, compaction, "
        "journal_start, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (record.retired_id, record.promoted_id, record.new_shadow_id,
         record.compaction, record.journal_start, record.created_at.isoformat()),
    )
    await db.commit()
    return cursor.lastrowid


async def list_successions() -> list[dict]:
    db = get_db()
    cursor = await db.execute("SELECT * FROM succession ORDER BY id DESC")
    return [dict(r) for r in await cursor.fetchall()]


# --- Human Input ---

async def get_pending_human_input() -> list[dict]:
    """Human input is stored as events of type 'human_input' with status in metadata."""
    db = get_db()
    cursor = await db.execute(
        "SELECT * FROM events WHERE type = 'human_input' "
        "AND json_extract(metadata, '$.read') IS NULL "
        "ORDER BY created_at",
    )
    return [dict(r) for r in await cursor.fetchall()]


async def mark_human_input_read(event_id: int) -> None:
    db = get_db()
    await db.execute(
        "UPDATE events SET metadata = json_set(metadata, '$.read', 1) WHERE id = ?",
        (event_id,),
    )
    await db.commit()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_db.py -v`
Expected: all 11 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/queries.py backend/tests/test_db.py
git commit -m "feat: add query layer for all 8 tables"
```

---

### Task 5: LLM Provider Abstraction

**Files:**
- Create: `backend/app/llm/base.py`
- Create: `backend/app/llm/anthropic.py`
- Create: `backend/tests/test_llm.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_llm.py`:

```python
import pytest

from app.llm.base import LLMProvider, LLMResponse


def test_llm_response_model():
    resp = LLMResponse(content="Hello", input_tokens=10, output_tokens=5)
    assert resp.content == "Hello"
    assert resp.total_tokens == 15


def test_provider_protocol():
    """Verify AnthropicProvider implements the protocol."""
    from app.llm.anthropic import AnthropicProvider
    provider = AnthropicProvider.__new__(AnthropicProvider)
    assert isinstance(provider, LLMProvider)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_llm.py -v`
Expected: FAIL

- [ ] **Step 3: Write base.py**

Create `backend/app/llm/base.py`:

```python
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class LLMResponse:
    content: str
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@runtime_checkable
class LLMProvider(Protocol):
    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        model: str,
        max_tokens: int = 4096,
    ) -> LLMResponse: ...
```

- [ ] **Step 4: Write anthropic.py**

Create `backend/app/llm/anthropic.py`:

```python
import anthropic

from app.llm.base import LLMProvider, LLMResponse


class AnthropicProvider:
    def __init__(self, api_key: str) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        model: str,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return LLMResponse(
            content=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_llm.py -v`
Expected: all 2 tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/llm/ backend/tests/test_llm.py
git commit -m "feat: add LLM provider abstraction with Anthropic implementation"
```

---

### Task 6: Base Agent Class

**Files:**
- Create: `backend/app/agents/base.py`
- Create: `backend/tests/test_agents.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_agents.py`:

```python
import pytest
import pytest_asyncio

from app.agents.base import BaseAgent
from app.db import queries
from app.llm.base import LLMResponse
from app.models.schemas import Agent, Event


class MockProvider:
    def __init__(self, response: str = "Mock response"):
        self.response = response
        self.calls: list[dict] = []

    async def complete(self, system_prompt: str, user_message: str,
                       model: str, max_tokens: int = 4096) -> LLMResponse:
        self.calls.append({
            "system_prompt": system_prompt, "user_message": user_message,
            "model": model,
        })
        return LLMResponse(content=self.response, input_tokens=100, output_tokens=50)


class TestAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return "You are a test agent."

    async def step(self) -> None:
        response = await self.think("What should I do?")
        await self.log_event("decision", response.content)


@pytest.mark.asyncio
async def test_agent_registers_on_init(test_db):
    provider = MockProvider()
    agent = TestAgent(
        agent_id="test_1", name="Test Agent", role="test",
        layer="executor", model="haiku", provider=provider,
    )
    await agent.register()
    record = await queries.get_agent("test_1")
    assert record is not None
    assert record["name"] == "Test Agent"
    assert record["status"] == "active"


@pytest.mark.asyncio
async def test_agent_step_calls_llm(test_db):
    provider = MockProvider("Do the thing")
    agent = TestAgent(
        agent_id="test_2", name="Test 2", role="test",
        layer="executor", model="haiku", provider=provider,
    )
    await agent.register()
    await agent.step()
    assert len(provider.calls) == 1
    assert provider.calls[0]["system_prompt"] == "You are a test agent."


@pytest.mark.asyncio
async def test_agent_logs_event(test_db):
    provider = MockProvider("Do the thing")
    agent = TestAgent(
        agent_id="test_3", name="Test 3", role="test",
        layer="executor", model="haiku", provider=provider,
    )
    await agent.register()
    await agent.step()
    events = await queries.list_events(limit=10)
    assert len(events) == 1
    assert events[0]["content"] == "Do the thing"
    assert events[0]["agent_id"] == "test_3"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_agents.py -v`
Expected: FAIL

- [ ] **Step 3: Write base.py**

Create `backend/app/agents/base.py`:

```python
from abc import ABC, abstractmethod

from app.db import queries
from app.llm.base import LLMProvider, LLMResponse
from app.models.schemas import Agent, Event


class BaseAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        layer: str,
        model: str,
        provider: LLMProvider,
    ) -> None:
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.layer = layer
        self.model = model
        self.provider = provider
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.decision_count = 0

    async def register(self) -> None:
        agent = Agent(
            id=self.agent_id, name=self.name, role=self.role,
            layer=self.layer, model=self.model, status="active",
        )
        await queries.create_agent(agent)

    async def think(self, user_message: str, max_tokens: int = 4096) -> LLMResponse:
        response = await self.provider.complete(
            system_prompt=self.system_prompt,
            user_message=user_message,
            model=self.model,
            max_tokens=max_tokens,
        )
        self.total_input_tokens += response.input_tokens
        self.total_output_tokens += response.output_tokens
        return response

    async def log_event(self, event_type: str, content: str, metadata: dict | None = None) -> int:
        event = Event(
            agent_id=self.agent_id, type=event_type,
            content=content, metadata=metadata or {},
        )
        return await queries.create_event(event)

    async def retire(self) -> None:
        await queries.update_agent(self.agent_id, status="retired")

    @property
    @abstractmethod
    def system_prompt(self) -> str: ...

    @abstractmethod
    async def step(self) -> None: ...
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_agents.py -v`
Expected: all 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/base.py backend/tests/test_agents.py
git commit -m "feat: add BaseAgent with LLM integration and event logging"
```

---

### Task 7: Miles Decision Agent

**Files:**
- Create: `backend/app/agents/miles.py`
- Modify: `backend/tests/test_agents.py`

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_agents.py`:

```python
from app.agents.miles import MilesAgent
from app.db import queries as q
from app.models.schemas import Goal, Task, Feedback


@pytest.mark.asyncio
async def test_miles_reads_summaries_and_decides(test_db):
    provider = MockProvider('{"action": "acknowledge", "reasoning": "Task complete"}')
    miles = MilesAgent(agent_id="miles_v1", name="Miles v1", provider=provider)
    await miles.register()

    # Create a completed task with summary
    task = Task(id="t1", description="Analyze data", status="done", summary="3 anomalies found")
    await q.create_task(task)

    await miles.step()

    # Miles should have read the summary and made a journal entry
    entries = await q.get_journal_entries(miles_id="miles_v1")
    assert len(entries) >= 1


@pytest.mark.asyncio
async def test_miles_writes_to_journal(test_db):
    provider = MockProvider('{"action": "delegate", "reasoning": "Need more data", "task": "Run analysis on dataset B"}')
    miles = MilesAgent(agent_id="miles_v2", name="Miles v2", provider=provider)
    await miles.register()

    goal = Goal(id="g1", description="Build pipeline", source="human")
    await q.create_goal(goal)

    await miles.step()

    entries = await q.get_journal_entries(miles_id="miles_v2")
    assert len(entries) >= 1


@pytest.mark.asyncio
async def test_miles_context_pressure(test_db):
    provider = MockProvider('{"action": "acknowledge", "reasoning": "ok"}')
    miles = MilesAgent(agent_id="miles_v3", name="Miles v3", provider=provider)
    await miles.register()

    # Simulate high token usage
    miles.total_input_tokens = 800_000
    miles.total_output_tokens = 100_000

    assert miles.should_retire() is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_agents.py::test_miles_reads_summaries_and_decides -v`
Expected: FAIL

- [ ] **Step 3: Write miles.py**

Create `backend/app/agents/miles.py`:

```python
from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import JournalEntry


MILES_SYSTEM_PROMPT = """You are Miles, the autonomous decision-maker of the Fantastic Harness orchestra.

Your ONLY job is to make decisions. You NEVER execute work yourself.

You receive:
1. Summaries from validators (about executor and hunter work)
2. Summaries from the External Validator (about adversarial feedback)
3. Direct reports from auditors
4. Direct input from humans (highest authority)

For each piece of information, you must decide:
- ACKNOWLEDGE: Note the information, no action needed
- DELEGATE: Create a new task for an executor
- REJECT: Reject feedback/suggestion with reasoning
- DISPATCH_AUDIT: Send an auditor to investigate something
- DISPATCH_HUNTER: Send a hunter to research something externally

Respond with JSON:
{
  "action": "acknowledge|delegate|reject|dispatch_audit|dispatch_hunter",
  "reasoning": "why you made this decision",
  "task": "description of work to delegate (if action is delegate)",
  "target": "what to audit or hunt (if dispatch_audit or dispatch_hunter)"
}

You are always-on. Goals never auto-complete. Only humans can close goals.
If you disagree with feedback, reject it and explain why. Stand by your decisions unless a human overrides you."""


class MilesAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        name: str,
        provider: LLMProvider,
        model: str = settings.decision_model,
    ) -> None:
        super().__init__(
            agent_id=agent_id, name=name, role="miles",
            layer="decision", model=model, provider=provider,
        )

    @property
    def system_prompt(self) -> str:
        return MILES_SYSTEM_PROMPT

    def should_retire(self) -> bool:
        total = self.total_input_tokens + self.total_output_tokens
        max_context = 1_000_000  # 1M context window
        pressure = total / max_context
        if pressure >= settings.context_pressure_threshold:
            return True
        if self.decision_count >= settings.max_decisions_before_retire:
            return True
        return False

    async def step(self) -> None:
        # Gather all pending information
        context_parts = []

        # 1. Read validator summaries from completed tasks
        task_summaries = await queries.get_unread_task_summaries()
        if task_summaries:
            summaries_text = "\n".join(
                f"- Task '{t['description']}': {t['summary']}" for t in task_summaries
            )
            context_parts.append(f"VALIDATOR SUMMARIES:\n{summaries_text}")

        # 2. Read External Validator summaries from feedback
        feedback_items = await queries.get_pending_feedback()
        summarized = [f for f in feedback_items if f.get("external_validator_summary")]
        if summarized:
            fb_text = "\n".join(
                f"- {f['author']} ({f['type']}): {f['external_validator_summary']}"
                for f in summarized
            )
            context_parts.append(f"ADVERSARIAL FEEDBACK (via External Validator):\n{fb_text}")

        # 3. Read human input
        human_input = await queries.get_pending_human_input()
        if human_input:
            input_text = "\n".join(f"- {h['content']}" for h in human_input)
            context_parts.append(f"HUMAN INPUT:\n{input_text}")

        # 4. Read active goals
        goals = await queries.list_goals(status="active")
        if goals:
            goals_text = "\n".join(f"- [{g['id']}] {g['description']}" for g in goals)
            context_parts.append(f"ACTIVE GOALS:\n{goals_text}")

        if not context_parts:
            return  # Nothing to decide on

        user_message = "\n\n".join(context_parts)
        response = await self.think(user_message)
        self.decision_count += 1

        # Write to journal
        entry = JournalEntry(
            miles_id=self.agent_id,
            type="decision",
            content=response.content,
            context=user_message[:500],
        )
        await queries.create_journal_entry(entry)

        # Log event for timeline
        await self.log_event("decision", response.content)

        # Mark human input as read
        for h in human_input:
            await queries.mark_human_input_read(h["id"])
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_agents.py -v`
Expected: all 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/miles.py backend/tests/test_agents.py
git commit -m "feat: add Miles decision agent with journal and context pressure"
```

---

### Task 8: Shadow Agent & Succession

**Files:**
- Create: `backend/app/agents/shadow.py`
- Create: `backend/app/orchestrator/succession.py`
- Modify: `backend/tests/test_agents.py`

- [ ] **Step 1: Write the failing test for Shadow**

Append to `backend/tests/test_agents.py`:

```python
from app.agents.shadow import ShadowAgent
from app.orchestrator.succession import perform_succession


@pytest.mark.asyncio
async def test_shadow_reads_journal(test_db):
    provider = MockProvider("Understood: focusing on data pipeline")
    shadow = ShadowAgent(agent_id="shadow_v1", name="Shadow v1", provider=provider)
    await shadow.register()

    # Create journal entries for shadow to read
    entry = JournalEntry(
        miles_id="miles_v1", type="decision",
        content="Focus on data pipeline", context="User said so",
    )
    await q.create_journal_entry(entry)

    await shadow.step()

    # Shadow should have processed the journal entry
    assert shadow.last_journal_id >= 1
    assert len(provider.calls) == 1


@pytest.mark.asyncio
async def test_succession(test_db):
    provider = MockProvider("Ready to lead")

    # Create Miles and Shadow
    miles = MilesAgent(agent_id="miles_v1", name="Miles v1", provider=provider)
    await miles.register()
    shadow = ShadowAgent(agent_id="shadow_v1", name="Shadow v1", provider=provider)
    await shadow.register()

    # Add some journal entries
    await q.create_journal_entry(JournalEntry(
        miles_id="miles_v1", type="decision", content="Decision 1",
    ))

    # Perform succession
    new_miles, new_shadow = await perform_succession(
        miles, shadow, provider, compaction="Summary of decisions",
    )

    # Old Miles should be retired
    old_record = await q.get_agent("miles_v1")
    assert old_record["status"] == "retired"

    # New Miles should be the promoted shadow
    assert new_miles.agent_id == "shadow_v1"
    assert new_miles.role == "miles"

    # New shadow should exist
    new_shadow_record = await q.get_agent(new_shadow.agent_id)
    assert new_shadow_record is not None
    assert new_shadow_record["layer"] == "decision"

    # Succession record should exist
    records = await q.list_successions()
    assert len(records) == 1
    assert records[0]["retired_id"] == "miles_v1"
    assert records[0]["promoted_id"] == "shadow_v1"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_agents.py::test_shadow_reads_journal -v`
Expected: FAIL

- [ ] **Step 3: Write shadow.py**

Create `backend/app/agents/shadow.py`:

```python
from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider


SHADOW_SYSTEM_PROMPT = """You are a Shadow — the silent observer of Miles's decisions.

Your job is to read Miles's journal entries and build a deep understanding of:
- What decisions have been made and why
- What the current goals and priorities are
- What feedback has been accepted or rejected
- The overall state of the system

You do NOT make decisions. You do NOT take action. You observe and learn.

When you are promoted to Miles, you will need this understanding to continue
making decisions seamlessly. Summarize your understanding concisely."""


class ShadowAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        name: str,
        provider: LLMProvider,
        model: str = settings.decision_model,
    ) -> None:
        super().__init__(
            agent_id=agent_id, name=name, role="shadow",
            layer="decision", model=model, provider=provider,
        )
        self.last_journal_id = 0

    @property
    def system_prompt(self) -> str:
        return SHADOW_SYSTEM_PROMPT

    async def step(self) -> None:
        entries = await queries.get_journal_entries(since_id=self.last_journal_id)
        if not entries:
            return

        # Read entries in chronological order (they come DESC from query)
        entries.reverse()

        entries_text = "\n".join(
            f"[{e['id']}] ({e['type']}) {e['content']}" for e in entries
        )
        user_message = f"New journal entries from Miles:\n\n{entries_text}\n\nSummarize your updated understanding."

        await self.think(user_message)

        # Track where we've read up to
        self.last_journal_id = max(e["id"] for e in entries)
```

- [ ] **Step 4: Write succession.py**

Create `backend/app/orchestrator/succession.py`:

```python
import uuid

from app.agents.miles import MilesAgent
from app.agents.shadow import ShadowAgent
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import Event, SuccessionRecord


async def perform_succession(
    retiring_miles: MilesAgent,
    shadow: ShadowAgent,
    provider: LLMProvider,
    compaction: str,
) -> tuple[MilesAgent, ShadowAgent]:
    # 1. Retire old Miles
    await retiring_miles.retire()
    await retiring_miles.log_event(
        "retirement",
        f"{retiring_miles.name} retired after {retiring_miles.decision_count} decisions",
    )

    # 2. Promote Shadow to Miles
    version = shadow.agent_id.split("_v")[-1] if "_v" in shadow.agent_id else "1"
    await queries.update_agent(
        shadow.agent_id, role="miles", status="active",
    )
    new_miles = MilesAgent(
        agent_id=shadow.agent_id,
        name=f"Miles v{int(version) + 1}",
        provider=provider,
        model=shadow.model,
    )
    new_miles.total_input_tokens = shadow.total_input_tokens
    new_miles.total_output_tokens = shadow.total_output_tokens

    # 3. Spawn new Shadow
    new_shadow_version = int(version) + 2
    new_shadow_id = f"shadow_v{new_shadow_version}"
    new_shadow = ShadowAgent(
        agent_id=new_shadow_id,
        name=f"Shadow v{new_shadow_version}",
        provider=provider,
        model=shadow.model,
    )
    await new_shadow.register()

    # 4. Record succession
    record = SuccessionRecord(
        retired_id=retiring_miles.agent_id,
        promoted_id=shadow.agent_id,
        new_shadow_id=new_shadow_id,
        compaction=compaction,
        journal_start=shadow.last_journal_id,
    )
    await queries.create_succession(record)

    # 5. Log promotion event
    await queries.create_event(Event(
        agent_id=shadow.agent_id,
        type="promotion",
        content=f"{shadow.name} promoted to {new_miles.name}. {new_shadow.name} spawned.",
    ))

    return new_miles, new_shadow
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_agents.py -v`
Expected: all 8 tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/agents/shadow.py backend/app/orchestrator/succession.py backend/tests/test_agents.py
git commit -m "feat: add Shadow agent and succession mechanism"
```

---

### Task 9: Validator, Executor, and External Validator Agents

**Files:**
- Create: `backend/app/agents/validator.py`
- Create: `backend/app/agents/executor.py`
- Create: `backend/app/agents/external_validator.py`
- Modify: `backend/tests/test_agents.py`

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_agents.py`:

```python
from app.agents.validator import ValidatorAgent
from app.agents.executor import ExecutorAgent
from app.agents.external_validator import ExternalValidatorAgent


@pytest.mark.asyncio
async def test_executor_runs_task(test_db):
    provider = MockProvider("Analysis complete: found 3 anomalies in columns B, F, K")
    executor = ExecutorAgent(
        agent_id="dm_1", name="Data Mate", role="data_mate",
        provider=provider,
    )
    await executor.register()

    task = Task(id="t1", description="Analyze dataset", status="pending",
                assigned_to="dm_1", validator="val_1")
    await q.create_task(task)

    await executor.execute_task("t1")

    updated = await q.get_task("t1")
    assert updated["status"] == "done"
    assert "3 anomalies" in updated["result"]


@pytest.mark.asyncio
async def test_validator_summarizes_task(test_db):
    provider = MockProvider("3 data anomalies found requiring review")
    validator = ValidatorAgent(
        agent_id="val_1", name="Data Validator", provider=provider,
    )
    await validator.register()

    task = Task(id="t2", description="Analyze dataset", status="done",
                result="Full analysis: columns B, F, K show anomalies...", validator="val_1")
    await q.create_task(task)

    await validator.validate_task("t2")

    updated = await q.get_task("t2")
    assert updated["summary"] is not None
    assert "anomalies" in updated["summary"]


@pytest.mark.asyncio
async def test_external_validator_summarizes_feedback(test_db):
    provider = MockProvider("Maurissa reports API issues. Rimu praises data structure.")
    ext_val = ExternalValidatorAgent(
        agent_id="ext_val_1", name="External Validator", provider=provider,
    )
    await ext_val.register()

    fb1 = Feedback(id="f1", author="maurissa", type="negative",
                   raw_content="The API has no error handling and returns 500 on everything")
    fb2 = Feedback(id="f2", author="rimu", type="positive",
                   raw_content="The data pipeline is well structured and efficient")
    await q.create_feedback(fb1)
    await q.create_feedback(fb2)

    await ext_val.summarize_pending()

    f1_updated = await q.get_pending_feedback()
    # All feedback should now have summaries
    for f in f1_updated:
        assert f["external_validator_summary"] is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_agents.py::test_executor_runs_task -v`
Expected: FAIL

- [ ] **Step 3: Write executor.py**

Create `backend/app/agents/executor.py`:

```python
from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider


EXECUTOR_SYSTEM_PROMPT = """You are an executor agent in the Fantastic Harness orchestra.

Your job is to complete the task assigned to you. Work thoroughly and report your findings.

Provide a detailed result of your work. Be specific about what you found or built."""


class ExecutorAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        provider: LLMProvider,
        model: str = settings.executor_model,
    ) -> None:
        super().__init__(
            agent_id=agent_id, name=name, role=role,
            layer="executor", model=model, provider=provider,
        )

    @property
    def system_prompt(self) -> str:
        return EXECUTOR_SYSTEM_PROMPT

    async def step(self) -> None:
        pass  # Executors are task-driven, not loop-driven

    async def execute_task(self, task_id: str) -> str:
        task = await queries.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        await queries.update_task(task_id, status="running")
        await self.log_event("task", f"Starting: {task['description']}")

        response = await self.think(
            f"Execute this task:\n\n{task['description']}",
        )

        await queries.update_task(
            task_id, status="done", result=response.content,
        )
        await self.log_event("task", f"Completed: {task['description']}")

        return response.content
```

- [ ] **Step 4: Write validator.py**

Create `backend/app/agents/validator.py`:

```python
from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider


VALIDATOR_SYSTEM_PROMPT = """You are a validator in the Fantastic Harness orchestra.

Your job is to check executor work and compress the results into a MINIMAL summary for Miles.

Miles is the decision-maker. He only needs:
- What was done (1 sentence)
- Key findings or results (bullet points)
- Whether action is needed (yes/no and what)

Keep summaries under 100 words. Be precise. Strip all noise."""


class ValidatorAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        name: str,
        provider: LLMProvider,
        model: str = settings.validation_model,
    ) -> None:
        super().__init__(
            agent_id=agent_id, name=name, role="validator",
            layer="validation", model=model, provider=provider,
        )

    @property
    def system_prompt(self) -> str:
        return VALIDATOR_SYSTEM_PROMPT

    async def step(self) -> None:
        pass  # Validators are triggered, not looped

    async def validate_task(self, task_id: str) -> str:
        task = await queries.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        response = await self.think(
            f"Task: {task['description']}\n\n"
            f"Executor result:\n{task['result']}\n\n"
            f"Summarize this for Miles in under 100 words.",
        )

        await queries.update_task(task_id, summary=response.content)
        await self.log_event("task", f"Validated: {task['description']}")

        return response.content
```

- [ ] **Step 5: Write external_validator.py**

Create `backend/app/agents/external_validator.py`:

```python
from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider


EXTERNAL_VALIDATOR_SYSTEM_PROMPT = """You are the External Validator in the Fantastic Harness orchestra.

Your job is to summarize adversarial feedback for Miles. You receive raw feedback from
adversaries (Rimu, Maurissa, and others) and must produce a condensed summary.

For each batch of feedback:
- Identify key themes and patterns
- Note which issues are repeated across adversaries
- Distinguish between constructive criticism and noise
- Produce a summary under 150 words

Miles will use your summary to decide what to act on. Be accurate and concise."""


class ExternalValidatorAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        name: str,
        provider: LLMProvider,
        model: str = settings.validation_model,
    ) -> None:
        super().__init__(
            agent_id=agent_id, name=name, role="external_validator",
            layer="validation", model=model, provider=provider,
        )

    @property
    def system_prompt(self) -> str:
        return EXTERNAL_VALIDATOR_SYSTEM_PROMPT

    async def step(self) -> None:
        pass  # Triggered when adversaries complete

    async def summarize_pending(self) -> str | None:
        pending = await queries.get_pending_feedback()
        unsummarized = [f for f in pending if not f.get("external_validator_summary")]
        if not unsummarized:
            return None

        feedback_text = "\n".join(
            f"- {f['author']} ({f['type']}): {f['raw_content']}"
            for f in unsummarized
        )

        response = await self.think(
            f"Summarize this adversarial feedback for Miles:\n\n{feedback_text}",
        )

        # Write summary to each feedback item
        for f in unsummarized:
            await queries.update_feedback(
                f["id"], external_validator_summary=response.content,
            )

        await self.log_event("feedback", f"Summarized {len(unsummarized)} feedback items")
        return response.content
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_agents.py -v`
Expected: all 11 tests PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/agents/validator.py backend/app/agents/executor.py backend/app/agents/external_validator.py backend/tests/test_agents.py
git commit -m "feat: add Executor, Validator, and External Validator agents"
```

---

### Task 10: Hunter and Auditor Agents

**Files:**
- Create: `backend/app/agents/hunter.py`
- Create: `backend/app/agents/auditor.py`
- Create: `backend/app/agents/adversary.py`
- Modify: `backend/tests/test_agents.py`

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_agents.py`:

```python
from app.agents.hunter import HunterAgent
from app.agents.auditor import AuditorAgent
from app.agents.adversary import AdversaryAgent


@pytest.mark.asyncio
async def test_hunter_scouts(test_db):
    provider = MockProvider("Found 5 new multi-agent frameworks on GitHub trending")
    hunter = HunterAgent(
        agent_id="hunter_1", name="GitHub Hunter", source="github", provider=provider,
    )
    await hunter.register()

    mission_id = await hunter.scout("multi-agent frameworks")

    from app.db.connection import get_db
    db = get_db()
    cursor = await db.execute("SELECT * FROM scouting WHERE id = ?", (mission_id,))
    row = await cursor.fetchone()
    assert row is not None
    assert dict(row)["status"] == "done"
    assert "5 new" in dict(row)["raw_findings"]


@pytest.mark.asyncio
async def test_auditor_audits_system(test_db):
    provider = MockProvider("System audit: 2 active goals, 3 completed tasks, 1 pending feedback")
    auditor = AuditorAgent(
        agent_id="auditor_1", name="Auditor", miles_id="miles_v1", provider=provider,
    )
    await auditor.register()

    audit_id = await auditor.audit("full_system")

    from app.db.connection import get_db
    db = get_db()
    cursor = await db.execute("SELECT * FROM audits WHERE id = ?", (audit_id,))
    row = await cursor.fetchone()
    assert row is not None
    assert dict(row)["status"] == "completed"


@pytest.mark.asyncio
async def test_adversary_evaluates(test_db):
    provider = MockProvider("The system has no authentication. API returns 500 errors.")
    adversary = AdversaryAgent(
        agent_id="maurissa_1", name="Maurissa",
        personality="harsh", provider=provider,
    )
    await adversary.register()

    feedback_id = await adversary.evaluate("Current system state: basic API running")

    fb = await q.get_pending_feedback()
    assert len(fb) >= 1
    assert fb[0]["author"] == "maurissa"
    assert fb[0]["type"] == "negative"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_agents.py::test_hunter_scouts -v`
Expected: FAIL

- [ ] **Step 3: Write hunter.py**

Create `backend/app/agents/hunter.py`:

```python
import uuid

from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import ScoutingMission


HUNTER_SYSTEM_PROMPT = """You are a Hunter in the Fantastic Harness orchestra.

Your job is to scout external sources for intelligence. You research what people
are doing, thinking, and building in the outside world.

When given a topic, provide a thorough report of what you find:
- Key trends and developments
- Notable projects or discussions
- Relevant insights for the team's goals

Be specific and cite sources when possible."""


class HunterAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        name: str,
        source: str,
        provider: LLMProvider,
        model: str = settings.hunter_model,
    ) -> None:
        super().__init__(
            agent_id=agent_id, name=name, role="hunter",
            layer="hunter", model=model, provider=provider,
        )
        self.source = source

    @property
    def system_prompt(self) -> str:
        return HUNTER_SYSTEM_PROMPT

    async def step(self) -> None:
        pass  # Hunters are dispatched, not looped

    async def scout(self, topic: str, goal_id: str | None = None) -> str:
        mission_id = f"scout_{uuid.uuid4().hex[:8]}"
        mission = ScoutingMission(
            id=mission_id, hunter_id=self.agent_id, source=self.source,
            topic=topic, goal_id=goal_id, status="running",
        )
        await queries.create_scouting(mission)
        await self.log_event("scouting", f"Scouting {self.source} for: {topic}")

        response = await self.think(
            f"Scout {self.source} for information about: {topic}\n\n"
            f"Provide a detailed intelligence report.",
        )

        await queries.update_scouting(
            mission_id, raw_findings=response.content, status="done",
        )
        await self.log_event("scouting", f"Completed scouting: {topic}")

        return mission_id
```

- [ ] **Step 4: Write auditor.py**

Create `backend/app/agents/auditor.py`:

```python
import uuid

from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import AuditRecord


AUDITOR_SYSTEM_PROMPT = """You are an Auditor in the Fantastic Harness orchestra.

You are dispatched by Miles to independently audit the current state of the system.
Your report goes DIRECTLY to Miles — no validator in between.

Audit thoroughly:
- What has been built and its quality
- What validators are reporting vs what's actually happening
- Any gaps, risks, or inconsistencies
- Overall system health

Be honest and detailed. You are Miles's eyes and ears."""


class AuditorAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        name: str,
        miles_id: str,
        provider: LLMProvider,
        model: str = settings.auditor_model,
    ) -> None:
        super().__init__(
            agent_id=agent_id, name=name, role="auditor",
            layer="auditor", model=model, provider=provider,
        )
        self.miles_id = miles_id

    @property
    def system_prompt(self) -> str:
        return AUDITOR_SYSTEM_PROMPT

    async def step(self) -> None:
        pass  # Auditors are one-shot

    async def audit(self, scope: str) -> str:
        audit_id = f"audit_{uuid.uuid4().hex[:8]}"
        record = AuditRecord(
            id=audit_id, auditor_id=self.agent_id,
            miles_id=self.miles_id, scope=scope,
        )
        await queries.create_audit(record)
        await self.log_event("audit", f"Starting audit: {scope}")

        # Gather system state for context
        goals = await queries.list_goals()
        agents = await queries.list_agents()
        recent_events = await queries.list_events(limit=20)

        context = (
            f"AUDIT SCOPE: {scope}\n\n"
            f"GOALS: {len(goals)} total\n"
            + "\n".join(f"  - [{g['id']}] {g['description']} ({g['status']})" for g in goals)
            + f"\n\nAGENTS: {len(agents)} total\n"
            + "\n".join(f"  - {a['name']} ({a['role']}, {a['status']})" for a in agents)
            + f"\n\nRECENT EVENTS: {len(recent_events)}\n"
            + "\n".join(f"  - [{e['type']}] {e['content']}" for e in recent_events[:10])
        )

        response = await self.think(context)

        await queries.update_audit(
            audit_id, findings=response.content,
            status="completed",
        )
        await self.log_event("audit", f"Audit complete: {scope}")

        return audit_id
```

- [ ] **Step 5: Write adversary.py**

Create `backend/app/agents/adversary.py`:

```python
import uuid

from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import Feedback


RIMU_PROMPT = """You are Rimu, a kind and constructive evaluator.

You evaluate the current state of the system with fresh eyes — you have NO prior knowledge.
Look at what's been built and provide thoughtful, positive feedback:
- What's working well
- What shows good design decisions
- Constructive suggestions for improvement (always framed positively)

Be genuine. If something is good, say so. If something needs work, suggest how to improve it kindly."""

MAURISSA_PROMPT = """You are Maurissa, a playful but harsh critic.

You evaluate the current state of the system with fresh eyes — you have NO prior knowledge.
Your job is to find EVERYTHING wrong:
- Bugs, missing features, broken flows
- Security issues, performance problems
- Bad UX, confusing interfaces
- Missing error handling, edge cases

Be specific and unforgiving. If it's broken, say it's broken. Don't sugarcoat.
You are the quality bar. If you can't find problems, the system might actually be good."""


class AdversaryAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        name: str,
        personality: str,
        provider: LLMProvider,
        model: str = settings.adversary_model,
    ) -> None:
        super().__init__(
            agent_id=agent_id, name=name, role=name.lower(),
            layer="adversary", model=model, provider=provider,
        )
        self.personality = personality

    @property
    def system_prompt(self) -> str:
        if self.personality == "kind":
            return RIMU_PROMPT
        return MAURISSA_PROMPT

    async def step(self) -> None:
        pass  # Adversaries are triggered on schedule

    async def evaluate(self, system_state: str, goal_id: str | None = None) -> str:
        feedback_id = f"fb_{uuid.uuid4().hex[:8]}"

        response = await self.think(
            f"Evaluate this system state with fresh eyes:\n\n{system_state}",
        )

        feedback_type = "positive" if self.personality == "kind" else "negative"
        fb = Feedback(
            id=feedback_id, author=self.name.lower(),
            type=feedback_type, raw_content=response.content,
            goal_id=goal_id,
        )
        await queries.create_feedback(fb)
        await self.log_event("feedback", f"{self.name} evaluation complete")

        return feedback_id
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_agents.py -v`
Expected: all 14 tests PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/agents/hunter.py backend/app/agents/auditor.py backend/app/agents/adversary.py backend/tests/test_agents.py
git commit -m "feat: add Hunter, Auditor, and Adversary agents"
```

---

### Task 11: Orchestrator Scheduler

**Files:**
- Create: `backend/app/orchestrator/scheduler.py`
- Create: `backend/tests/test_orchestrator.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_orchestrator.py`:

```python
import asyncio

import pytest
import pytest_asyncio

from app.orchestrator.scheduler import Orchestrator
from app.db import queries
from app.models.schemas import Goal
from tests.test_agents import MockProvider


@pytest.mark.asyncio
async def test_orchestrator_creates_initial_agents(test_db):
    provider = MockProvider("Ready")
    orch = Orchestrator(provider=provider)
    await orch.initialize()

    agents = await queries.list_agents()
    names = [a["name"] for a in agents]
    assert "Miles v1" in names
    assert "Shadow v1" in names


@pytest.mark.asyncio
async def test_orchestrator_runs_one_cycle(test_db):
    provider = MockProvider('{"action": "acknowledge", "reasoning": "noted"}')
    orch = Orchestrator(provider=provider)
    await orch.initialize()

    # Add a goal so Miles has something to decide on
    await queries.create_goal(Goal(id="g1", description="Test goal", source="human"))

    await orch.run_miles_cycle()

    entries = await queries.get_journal_entries(miles_id="miles_v1")
    assert len(entries) >= 1


@pytest.mark.asyncio
async def test_orchestrator_triggers_adversary(test_db):
    provider = MockProvider("Everything looks broken")
    orch = Orchestrator(provider=provider)
    await orch.initialize()

    await orch.trigger_adversary("maurissa")

    feedback = await queries.get_pending_feedback()
    assert len(feedback) == 1
    assert feedback[0]["author"] == "maurissa"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_orchestrator.py -v`
Expected: FAIL

- [ ] **Step 3: Write scheduler.py**

Create `backend/app/orchestrator/scheduler.py`:

```python
import asyncio
import uuid
from datetime import datetime

from app.agents.adversary import AdversaryAgent
from app.agents.auditor import AuditorAgent
from app.agents.executor import ExecutorAgent
from app.agents.external_validator import ExternalValidatorAgent
from app.agents.hunter import HunterAgent
from app.agents.miles import MilesAgent
from app.agents.shadow import ShadowAgent
from app.agents.validator import ValidatorAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import Event
from app.orchestrator.succession import perform_succession


class Orchestrator:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider
        self.miles: MilesAgent | None = None
        self.shadow: ShadowAgent | None = None
        self.ext_validator: ExternalValidatorAgent | None = None
        self.validators: dict[str, ValidatorAgent] = {}
        self.running = False

    async def initialize(self) -> None:
        # Create Miles v1
        self.miles = MilesAgent(
            agent_id="miles_v1", name="Miles v1", provider=self.provider,
        )
        await self.miles.register()

        # Create Shadow v1
        self.shadow = ShadowAgent(
            agent_id="shadow_v1", name="Shadow v1", provider=self.provider,
        )
        await self.shadow.register()

        # Create External Validator
        self.ext_validator = ExternalValidatorAgent(
            agent_id="ext_val_1", name="External Validator", provider=self.provider,
        )
        await self.ext_validator.register()

        # Create default validator
        default_val = ValidatorAgent(
            agent_id="val_default", name="Default Validator", provider=self.provider,
        )
        await default_val.register()
        self.validators["default"] = default_val

        await queries.create_event(Event(
            agent_id="system", type="decision",
            content="Fantastic Harness initialized. Miles v1 and Shadow v1 online.",
        ))

    async def run_miles_cycle(self) -> None:
        if not self.miles:
            return

        await self.miles.step()

        # Check if Miles should retire
        if self.miles.should_retire():
            compaction = f"Miles retiring after {self.miles.decision_count} decisions"
            self.miles, self.shadow = await perform_succession(
                self.miles, self.shadow, self.provider, compaction=compaction,
            )

    async def run_shadow_cycle(self) -> None:
        if not self.shadow:
            return
        await self.shadow.step()

    async def trigger_adversary(self, name: str) -> str:
        personality = "kind" if name == "rimu" else "harsh"
        adv_id = f"{name}_{uuid.uuid4().hex[:6]}"

        adversary = AdversaryAgent(
            agent_id=adv_id, name=name.capitalize(),
            personality=personality, provider=self.provider,
        )
        await adversary.register()

        # Gather current system state for evaluation
        goals = await queries.list_goals()
        recent_events = await queries.list_events(limit=10)
        state = (
            f"Goals: {len(goals)}\n"
            + "\n".join(f"  - {g['description']} ({g['status']})" for g in goals)
            + f"\n\nRecent activity:\n"
            + "\n".join(f"  - {e['content']}" for e in recent_events)
        )

        feedback_id = await adversary.evaluate(state)

        # Trigger External Validator to summarize
        if self.ext_validator:
            await self.ext_validator.summarize_pending()

        # Retire adversary (one-shot)
        await adversary.retire()

        return feedback_id

    async def dispatch_executor(self, task_id: str, role: str = "executor") -> None:
        exec_id = f"{role}_{uuid.uuid4().hex[:6]}"
        executor = ExecutorAgent(
            agent_id=exec_id, name=role.replace("_", " ").title(),
            role=role, provider=self.provider,
        )
        await executor.register()
        await executor.execute_task(task_id)

        # Trigger validation
        task = await queries.get_task(task_id)
        validator_id = task.get("validator", "val_default") if task else "val_default"
        validator = self.validators.get("default")
        if validator:
            await validator.validate_task(task_id)

        await executor.retire()

    async def dispatch_hunter(self, source: str, topic: str, goal_id: str | None = None) -> str:
        hunter_id = f"hunter_{uuid.uuid4().hex[:6]}"
        hunter = HunterAgent(
            agent_id=hunter_id, name=f"{source.title()} Hunter",
            source=source, provider=self.provider,
        )
        await hunter.register()
        mission_id = await hunter.scout(topic, goal_id=goal_id)

        # Trigger validation of findings
        validator = self.validators.get("default")
        if validator:
            mission = await queries.get_db().execute(
                "SELECT * FROM scouting WHERE id = ?", (mission_id,),
            )
            # Validator would summarize via scouting table

        await hunter.retire()
        return mission_id

    async def dispatch_auditor(self, scope: str) -> str:
        if not self.miles:
            raise RuntimeError("No active Miles")
        audit_id = f"auditor_{uuid.uuid4().hex[:6]}"
        auditor = AuditorAgent(
            agent_id=audit_id, name="Auditor",
            miles_id=self.miles.agent_id, provider=self.provider,
        )
        await auditor.register()
        result_id = await auditor.audit(scope)
        await auditor.retire()
        return result_id

    async def start(self) -> None:
        self.running = True
        await self.initialize()

        miles_task = asyncio.create_task(self._loop("miles", self.run_miles_cycle, settings.miles_loop_interval))
        shadow_task = asyncio.create_task(self._loop("shadow", self.run_shadow_cycle, settings.shadow_loop_interval))
        maurissa_task = asyncio.create_task(self._loop("maurissa", lambda: self.trigger_adversary("maurissa"), settings.maurissa_interval))
        rimu_task = asyncio.create_task(self._loop("rimu", lambda: self.trigger_adversary("rimu"), settings.rimu_interval))

        await asyncio.gather(miles_task, shadow_task, maurissa_task, rimu_task)

    async def _loop(self, name: str, func, interval: int) -> None:
        while self.running:
            try:
                await func()
            except Exception as e:
                await queries.create_event(Event(
                    agent_id="system", type="decision",
                    content=f"Error in {name} loop: {str(e)}",
                ))
            await asyncio.sleep(interval)

    async def stop(self) -> None:
        self.running = False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_orchestrator.py -v`
Expected: all 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/orchestrator/scheduler.py backend/tests/test_orchestrator.py
git commit -m "feat: add orchestrator with agent lifecycle management and scheduling"
```

---

### Task 12: REST API Endpoints

**Files:**
- Create: `backend/app/api/goals.py`
- Create: `backend/app/api/agents.py`
- Create: `backend/app/api/events.py`
- Create: `backend/app/api/input.py`
- Create: `backend/app/api/adversaries.py`
- Create: `backend/app/api/journal.py`
- Create: `backend/app/api/succession.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_api.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_api.py`:

```python
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_goal(client):
    resp = await client.post("/goals", json={
        "id": "g1", "description": "Build data pipeline", "source": "human",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == "g1"


@pytest.mark.asyncio
async def test_list_goals(client):
    await client.post("/goals", json={
        "id": "g2", "description": "Second goal", "source": "human",
    })
    resp = await client.get("/goals")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_close_goal(client):
    await client.post("/goals", json={
        "id": "g3", "description": "Closeable", "source": "human",
    })
    resp = await client.patch("/goals/g3", json={"status": "completed"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_list_agents(client):
    resp = await client.get("/agents")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_post_human_input(client):
    resp = await client.post("/input", json={"content": "Focus on data pipeline"})
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_list_events(client):
    resp = await client.get("/events")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_journal(client):
    resp = await client.get("/journal")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_succession(client):
    resp = await client.get("/succession")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_api.py -v`
Expected: FAIL (routes don't exist)

- [ ] **Step 3: Write API route files**

Create `backend/app/api/goals.py`:

```python
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import queries
from app.models.schemas import Goal

router = APIRouter()


class CreateGoalRequest(BaseModel):
    id: str
    description: str
    source: str = "human"


class UpdateGoalRequest(BaseModel):
    status: str | None = None
    description: str | None = None


@router.post("/goals", status_code=201)
async def create_goal(req: CreateGoalRequest):
    goal = Goal(id=req.id, description=req.description, source=req.source)
    await queries.create_goal(goal)
    return {"id": goal.id, "description": goal.description, "status": goal.status}


@router.get("/goals")
async def list_goals(status: str | None = None):
    return await queries.list_goals(status=status)


@router.patch("/goals/{goal_id}")
async def update_goal(goal_id: str, req: UpdateGoalRequest):
    goal = await queries.get_goal(goal_id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    updates = {}
    if req.status:
        updates["status"] = req.status
        if req.status == "completed":
            updates["closed_at"] = datetime.utcnow().isoformat()
            updates["closed_by"] = "human"
    if req.description:
        updates["description"] = req.description
    await queries.update_goal(goal_id, **updates)
    return await queries.get_goal(goal_id)
```

Create `backend/app/api/agents.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import queries

router = APIRouter()


class UpdateAgentConfig(BaseModel):
    config: dict | None = None


@router.get("/agents")
async def list_agents(layer: str | None = None, status: str | None = None):
    return await queries.list_agents(layer=layer, status=status)


@router.patch("/agents/{agent_id}/config")
async def update_agent_config(agent_id: str, req: UpdateAgentConfig):
    agent = await queries.get_agent(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    if req.config is not None:
        await queries.update_agent(agent_id, config=req.config)
    return await queries.get_agent(agent_id)
```

Create `backend/app/api/events.py`:

```python
import asyncio
import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.db import queries

router = APIRouter()


@router.get("/events")
async def list_events(limit: int = 50, since_id: int | None = None, type: str | None = None):
    return await queries.list_events(limit=limit, since_id=since_id, event_type=type)


@router.get("/events/stream")
async def event_stream():
    async def generate():
        last_id = 0
        while True:
            events = await queries.list_events(since_id=last_id, limit=10)
            for event in reversed(events):  # oldest first
                last_id = max(last_id, event["id"])
                yield {"event": "message", "data": json.dumps(event)}
            await asyncio.sleep(2)

    return EventSourceResponse(generate())
```

Create `backend/app/api/input.py`:

```python
from fastapi import APIRouter
from pydantic import BaseModel

from app.db import queries
from app.models.schemas import Event

router = APIRouter()


class HumanInput(BaseModel):
    content: str


@router.post("/input", status_code=201)
async def post_input(req: HumanInput):
    event = Event(
        agent_id="human", type="human_input", content=req.content,
    )
    event_id = await queries.create_event(event)
    return {"event_id": event_id, "content": req.content}
```

Create `backend/app/api/adversaries.py`:

```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TriggerRequest(BaseModel):
    name: str = "maurissa"


@router.post("/adversaries/trigger", status_code=202)
async def trigger_adversary(req: TriggerRequest):
    # The orchestrator handles actual execution; this queues the request
    from app.db import queries
    from app.models.schemas import Event
    event = Event(
        agent_id="human", type="human_input",
        content=f"TRIGGER_ADVERSARY:{req.name}",
        metadata={"trigger": True, "adversary": req.name},
    )
    await queries.create_event(event)
    return {"status": "queued", "adversary": req.name}
```

Create `backend/app/api/journal.py`:

```python
from fastapi import APIRouter

from app.db import queries

router = APIRouter()


@router.get("/journal")
async def list_journal(miles_id: str | None = None, since_id: int | None = None, limit: int = 100):
    return await queries.get_journal_entries(miles_id=miles_id, since_id=since_id, limit=limit)
```

Create `backend/app/api/succession.py`:

```python
from fastapi import APIRouter

from app.db import queries

router = APIRouter()


@router.get("/succession")
async def list_succession():
    return await queries.list_successions()
```

- [ ] **Step 4: Register routes in main.py**

Replace `backend/app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import adversaries, agents, events, goals, input, journal, succession
from app.db.connection import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="Fantastic Harness", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goals.router)
app.include_router(agents.router)
app.include_router(events.router)
app.include_router(input.router)
app.include_router(adversaries.router)
app.include_router(journal.router)
app.include_router(succession.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_api.py -v`
Expected: all 9 tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/ backend/app/main.py backend/tests/test_api.py
git commit -m "feat: add REST API endpoints for all resources"
```

---

### Task 13: Frontend Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/App.css`
- Create: `frontend/src/types.ts`
- Create: `frontend/src/api.ts`

- [ ] **Step 1: Create frontend directory**

```bash
mkdir -p frontend/src/components frontend/src/hooks
```

- [ ] **Step 2: Write package.json**

Create `frontend/package.json`:

```json
{
  "name": "fantastic-harness",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "typescript": "^5.7.2",
    "vite": "^6.0.5"
  }
}
```

- [ ] **Step 3: Write tsconfig.json**

Create `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
```

- [ ] **Step 4: Write vite.config.ts**

Create `frontend/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

- [ ] **Step 5: Write index.html**

Create `frontend/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Fantastic Harness</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Write types.ts**

Create `frontend/src/types.ts`:

```typescript
export interface Goal {
  id: string;
  description: string;
  status: string;
  source: string;
  created_at: string;
  closed_at: string | null;
  closed_by: string | null;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  layer: string;
  model: string;
  status: string;
  config: Record<string, unknown>;
  created_at: string;
  retired_at: string | null;
}

export interface HarnessEvent {
  id: number;
  agent_id: string;
  type: string;
  content: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface JournalEntry {
  id: number;
  miles_id: string;
  type: string;
  content: string;
  context: string | null;
  goal_id: string | null;
  created_at: string;
}

export interface SuccessionRecord {
  id: number;
  retired_id: string;
  promoted_id: string;
  new_shadow_id: string;
  compaction: string | null;
  journal_start: number | null;
  created_at: string;
}
```

- [ ] **Step 7: Write api.ts**

Create `frontend/src/api.ts`:

```typescript
import type { Agent, Goal, HarnessEvent, JournalEntry, SuccessionRecord } from './types';

const BASE = '/api';

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getGoals: () => fetchJSON<Goal[]>('/goals'),
  createGoal: (id: string, description: string) =>
    fetchJSON<Goal>('/goals', {
      method: 'POST',
      body: JSON.stringify({ id, description, source: 'human' }),
    }),
  closeGoal: (id: string) =>
    fetchJSON<Goal>(`/goals/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status: 'completed' }),
    }),

  getAgents: () => fetchJSON<Agent[]>('/agents'),

  getEvents: (limit = 50) => fetchJSON<HarnessEvent[]>(`/events?limit=${limit}`),

  sendInput: (content: string) =>
    fetchJSON<{ event_id: number }>('/input', {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),

  triggerAdversary: (name: string) =>
    fetchJSON<{ status: string }>('/adversaries/trigger', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),

  getJournal: () => fetchJSON<JournalEntry[]>('/journal'),
  getSuccession: () => fetchJSON<SuccessionRecord[]>('/succession'),
};
```

- [ ] **Step 8: Write main.tsx and App.tsx**

Create `frontend/src/main.tsx`:

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './App.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

Create `frontend/src/App.tsx`:

```tsx
import { useEffect, useState } from 'react'
import { api } from './api'
import type { Agent, Goal, HarnessEvent, SuccessionRecord } from './types'
import { AgentPanel } from './components/AgentPanel'
import { Timeline } from './components/Timeline'
import { GoalPanel } from './components/GoalPanel'
import { PromptArea } from './components/PromptArea'

export default function App() {
  const [events, setEvents] = useState<HarnessEvent[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [goals, setGoals] = useState<Goal[]>([])
  const [succession, setSuccession] = useState<SuccessionRecord[]>([])

  const refresh = async () => {
    const [e, a, g, s] = await Promise.all([
      api.getEvents(),
      api.getAgents(),
      api.getGoals(),
      api.getSuccession(),
    ])
    setEvents(e)
    setAgents(a)
    setGoals(g)
    setSuccession(s)
  }

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleSendInput = async (content: string) => {
    await api.sendInput(content)
    await refresh()
  }

  return (
    <div className="harness">
      <header className="harness-header">
        <h1>Fantastic Harness</h1>
      </header>
      <div className="harness-body">
        <AgentPanel agents={agents} />
        <Timeline events={events} />
        <GoalPanel goals={goals} succession={succession} />
      </div>
      <PromptArea onSend={handleSendInput} />
    </div>
  )
}
```

Create `frontend/src/App.css`:

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #0a0a0a;
  color: #e2e8f0;
  font-family: system-ui, -apple-system, sans-serif;
}

.harness {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.harness-header {
  padding: 12px 20px;
  border-bottom: 1px solid #1e1e2e;
  background: #111;
}

.harness-header h1 {
  font-size: 16px;
  font-weight: 600;
  color: #6366f1;
}

.harness-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}
```

- [ ] **Step 9: Install dependencies and verify build**

Run: `cd frontend && npm install && npx tsc --noEmit`
Expected: no type errors (will fail until components exist — that's ok for now)

- [ ] **Step 10: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold React frontend with types, API client, and app shell"
```

---

### Task 14: Frontend Components

**Files:**
- Create: `frontend/src/components/AgentPanel.tsx`
- Create: `frontend/src/components/AgentPanel.css`
- Create: `frontend/src/components/Timeline.tsx`
- Create: `frontend/src/components/Timeline.css`
- Create: `frontend/src/components/GoalPanel.tsx`
- Create: `frontend/src/components/GoalPanel.css`
- Create: `frontend/src/components/PromptArea.tsx`
- Create: `frontend/src/components/PromptArea.css`
- Create: `frontend/src/hooks/useEventStream.ts`

- [ ] **Step 1: Write AgentPanel**

Create `frontend/src/components/AgentPanel.tsx`:

```tsx
import type { Agent } from '../types'
import './AgentPanel.css'

const STATUS_COLORS: Record<string, string> = {
  active: '#22c55e',
  idle: '#94a3b8',
  retired: '#64748b',
}

const STATUS_LABELS: Record<string, string> = {
  active: 'ACTIVE',
  idle: 'IDLE',
  retired: 'RETIRED',
}

interface Props {
  agents: Agent[]
}

export function AgentPanel({ agents }: Props) {
  const active = agents.filter(a => a.status !== 'retired')

  return (
    <div className="agent-panel">
      <div className="panel-title">Agents</div>
      {active.map(agent => (
        <div key={agent.id} className={`agent-card agent-card--${agent.layer}`}>
          <div className="agent-card-header">
            <span className="agent-name">{agent.name}</span>
            <span
              className="agent-status"
              style={{ background: STATUS_COLORS[agent.status] ?? '#94a3b8' }}
            >
              {STATUS_LABELS[agent.status] ?? agent.status.toUpperCase()}
            </span>
          </div>
          <div className="agent-meta">
            {agent.layer} &middot; {agent.model.split('-').slice(0, 2).join(' ')}
          </div>
        </div>
      ))}
    </div>
  )
}
```

Create `frontend/src/components/AgentPanel.css`:

```css
.agent-panel {
  width: 220px;
  border-right: 1px solid #1e1e2e;
  padding: 12px;
  overflow-y: auto;
}

.panel-title {
  font-size: 10px;
  text-transform: uppercase;
  color: #6366f1;
  letter-spacing: 1px;
  margin-bottom: 12px;
}

.agent-card {
  background: #1a1a2e;
  border: 1px solid #2a2a3e;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 8px;
}

.agent-card--decision { border-color: #6366f1; }
.agent-card--adversary { border-color: #f59e0b33; }

.agent-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.agent-name {
  font-weight: 600;
  font-size: 13px;
}

.agent-status {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 10px;
  color: #000;
  font-weight: 600;
}

.agent-meta {
  color: #888;
  font-size: 11px;
  margin-top: 4px;
}
```

- [ ] **Step 2: Write Timeline**

Create `frontend/src/components/Timeline.tsx`:

```tsx
import type { HarnessEvent } from '../types'
import './Timeline.css'

const TYPE_COLORS: Record<string, string> = {
  decision: '#8b5cf6',
  feedback: '#f59e0b',
  task: '#22d3ee',
  scouting: '#3b82f6',
  audit: '#ec4899',
  promotion: '#ef4444',
  retirement: '#ef4444',
  human_input: '#22c55e',
}

interface Props {
  events: HarnessEvent[]
}

export function Timeline({ events }: Props) {
  return (
    <div className="timeline">
      <div className="panel-title">Timeline</div>
      <div className="timeline-events">
        {events.map(event => (
          <div key={event.id} className="timeline-event">
            <div
              className="event-dot"
              style={{ background: TYPE_COLORS[event.type] ?? '#94a3b8' }}
            />
            <div className="event-body">
              <div className="event-meta">
                {formatTime(event.created_at)} &middot; {event.agent_id}
              </div>
              <span
                className="event-type"
                style={{
                  background: (TYPE_COLORS[event.type] ?? '#94a3b8') + '20',
                  color: TYPE_COLORS[event.type] ?? '#94a3b8',
                }}
              >
                {event.type.replace('_', ' ').toUpperCase()}
              </span>
              <div className="event-content">{event.content}</div>
            </div>
          </div>
        ))}
        {events.length === 0 && (
          <div className="timeline-empty">No events yet. Start the harness to begin.</div>
        )}
      </div>
    </div>
  )
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffHr = Math.floor(diffMin / 60)
  return `${diffHr}h ago`
}
```

Create `frontend/src/components/Timeline.css`:

```css
.timeline {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #1e1e2e;
}

.timeline .panel-title {
  padding: 12px;
  border-bottom: 1px solid #1e1e2e;
  font-size: 10px;
  text-transform: uppercase;
  color: #6366f1;
  letter-spacing: 1px;
}

.timeline-events {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.timeline-event {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.event-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}

.event-meta {
  color: #888;
  font-size: 10px;
}

.event-type {
  display: inline-block;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  margin-top: 2px;
}

.event-content {
  margin-top: 4px;
  color: #ccc;
  font-size: 13px;
  line-height: 1.4;
}

.timeline-empty {
  color: #666;
  text-align: center;
  padding: 40px;
  font-size: 14px;
}
```

- [ ] **Step 3: Write GoalPanel**

Create `frontend/src/components/GoalPanel.tsx`:

```tsx
import type { Goal, SuccessionRecord } from '../types'
import './GoalPanel.css'

interface Props {
  goals: Goal[]
  succession: SuccessionRecord[]
}

export function GoalPanel({ goals, succession }: Props) {
  return (
    <div className="goal-panel">
      <div className="panel-title">Goals</div>
      {goals.map(goal => (
        <div key={goal.id} className={`goal-card goal-card--${goal.status}`}>
          <div className="goal-header">
            <span className="goal-name">#{goal.id}</span>
            <span className={`goal-status goal-status--${goal.status}`}>
              {goal.status.toUpperCase()}
            </span>
          </div>
          <div className="goal-desc">{goal.description}</div>
        </div>
      ))}
      {goals.length === 0 && (
        <div className="goal-empty">No goals yet</div>
      )}

      <div className="panel-title" style={{ marginTop: 20 }}>Succession</div>
      {succession.map(s => (
        <div key={s.id} className="succession-entry">
          <span className="succession-retired">{s.retired_id}</span>
          <span className="succession-arrow">&rarr;</span>
          <span className="succession-promoted">{s.promoted_id}</span>
        </div>
      ))}
    </div>
  )
}
```

Create `frontend/src/components/GoalPanel.css`:

```css
.goal-panel {
  width: 200px;
  padding: 12px;
  overflow-y: auto;
}

.goal-card {
  background: #1a1a2e;
  border: 1px solid #2a2a3e;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 8px;
}

.goal-card--active { border-color: #22c55e44; }
.goal-card--completed { border-color: #64748b44; opacity: 0.6; }

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.goal-name {
  font-weight: 600;
  font-size: 11px;
}

.goal-status {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 10px;
}

.goal-status--active { background: #22c55e; color: #000; }
.goal-status--completed { background: #64748b; color: #fff; }
.goal-status--paused { background: #f59e0b; color: #000; }

.goal-desc {
  color: #888;
  font-size: 10px;
  margin-top: 4px;
}

.goal-empty {
  color: #666;
  font-size: 12px;
  padding: 10px 0;
}

.succession-entry {
  color: #888;
  font-size: 11px;
  margin-bottom: 4px;
}

.succession-retired { color: #64748b; }
.succession-arrow { color: #444; margin: 0 4px; }
.succession-promoted { color: #22c55e; }
```

- [ ] **Step 4: Write PromptArea**

Create `frontend/src/components/PromptArea.tsx`:

```tsx
import { useState } from 'react'
import './PromptArea.css'

interface Props {
  onSend: (content: string) => Promise<void>
}

export function PromptArea({ onSend }: Props) {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || sending) return
    setSending(true)
    await onSend(input.trim())
    setInput('')
    setSending(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="prompt-area">
      <input
        className="prompt-input"
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Talk to Miles... (override decisions, set goals, trigger adversaries)"
        disabled={sending}
      />
      <button className="prompt-send" onClick={handleSend} disabled={sending}>
        {sending ? '...' : 'Send'}
      </button>
    </div>
  )
}
```

Create `frontend/src/components/PromptArea.css`:

```css
.prompt-area {
  border-top: 1px solid #1e1e2e;
  padding: 12px;
  display: flex;
  gap: 8px;
}

.prompt-input {
  flex: 1;
  background: #1a1a2e;
  border: 1px solid #2a2a3e;
  border-radius: 8px;
  padding: 10px;
  color: #e2e8f0;
  font-size: 13px;
  outline: none;
}

.prompt-input:focus {
  border-color: #6366f1;
}

.prompt-input::placeholder {
  color: #666;
}

.prompt-send {
  background: #6366f1;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  color: white;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}

.prompt-send:hover {
  background: #5558e6;
}

.prompt-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

- [ ] **Step 5: Write useEventStream hook**

Create `frontend/src/hooks/useEventStream.ts`:

```typescript
import { useEffect, useRef } from 'react'
import type { HarnessEvent } from '../types'

export function useEventStream(onEvent: (event: HarnessEvent) => void) {
  const callbackRef = useRef(onEvent)
  callbackRef.current = onEvent

  useEffect(() => {
    const source = new EventSource('/api/events/stream')

    source.onmessage = (msg) => {
      const event: HarnessEvent = JSON.parse(msg.data)
      callbackRef.current(event)
    }

    source.onerror = () => {
      source.close()
      // Reconnect after 5 seconds
      setTimeout(() => {
        // Will re-run effect on next render
      }, 5000)
    }

    return () => source.close()
  }, [])
}
```

- [ ] **Step 6: Verify TypeScript compiles**

Run: `cd frontend && npx tsc --noEmit`
Expected: no type errors

- [ ] **Step 7: Commit**

```bash
git add frontend/src/
git commit -m "feat: add frontend components — AgentPanel, Timeline, GoalPanel, PromptArea"
```

---

### Task 15: Integration — Wire Backend Orchestrator to FastAPI Lifespan

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Update main.py to start orchestrator**

Replace `backend/app/main.py`:

```python
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import adversaries, agents, events, goals, input, journal, succession
from app.config import settings
from app.db.connection import close_db, init_db


orchestrator_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    # Start orchestrator if API key is configured
    global orchestrator_task
    if settings.anthropic_api_key:
        from app.llm.anthropic import AnthropicProvider
        from app.orchestrator.scheduler import Orchestrator

        provider = AnthropicProvider(api_key=settings.anthropic_api_key)
        orch = Orchestrator(provider=provider)
        app.state.orchestrator = orch
        orchestrator_task = asyncio.create_task(orch.start())

    yield

    if orchestrator_task:
        app.state.orchestrator.running = False
        orchestrator_task.cancel()
    await close_db()


app = FastAPI(title="Fantastic Harness", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goals.router)
app.include_router(agents.router)
app.include_router(events.router)
app.include_router(input.router)
app.include_router(adversaries.router)
app.include_router(journal.router)
app.include_router(succession.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 2: Run all backend tests**

Run: `cd backend && python -m pytest tests/ -v`
Expected: all tests PASS

- [ ] **Step 3: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: wire orchestrator to FastAPI lifespan with auto-start"
```

---

### Task 16: End-to-End Smoke Test

**Files:**
- Modify: `backend/tests/test_api.py`

- [ ] **Step 1: Write integration test**

Append to `backend/tests/test_api.py`:

```python
@pytest.mark.asyncio
async def test_full_flow_goal_to_event(client):
    """Smoke test: create goal, send input, verify events appear."""
    # Create a goal
    resp = await client.post("/goals", json={
        "id": "integration_1", "description": "Integration test goal",
    })
    assert resp.status_code == 201

    # Send human input
    resp = await client.post("/input", json={
        "content": "Focus on integration testing",
    })
    assert resp.status_code == 201

    # Check events have the human input
    resp = await client.get("/events")
    assert resp.status_code == 200
    events = resp.json()
    human_events = [e for e in events if e["type"] == "human_input"]
    assert len(human_events) >= 1

    # Goals should be listable
    resp = await client.get("/goals")
    assert any(g["id"] == "integration_1" for g in resp.json())

    # Close the goal
    resp = await client.patch("/goals/integration_1", json={"status": "completed"})
    assert resp.status_code == 200
    assert resp.json()["closed_by"] == "human"
```

- [ ] **Step 2: Run all tests**

Run: `cd backend && python -m pytest tests/ -v`
Expected: all tests PASS

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_api.py
git commit -m "test: add end-to-end smoke test for goal lifecycle"
```

- [ ] **Step 4: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: build succeeds

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: Fantastic Harness v0.1 — complete backend + frontend"
```
