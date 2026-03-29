import json
from datetime import datetime

from app.db.connection import get_db
from app.models.schemas import (
    Agent, AuditRecord, Event, Feedback, Goal,
    JournalEntry, ScoutingMission, SuccessionRecord, Task,
)


# --- Goals ---
async def create_goal(goal: Goal) -> None:
    db = get_db()
    await db.execute(
        "INSERT INTO goals (id, description, status, source, created_at) VALUES (?, ?, ?, ?, ?)",
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
        "INSERT INTO agents (id, name, role, layer, model, status, config, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (agent.id, agent.name, agent.role, agent.layer, agent.model,
         agent.status, json.dumps(agent.config), agent.created_at.isoformat()),
    )
    await db.commit()

async def list_agents(layer: str | None = None, status: str | None = None) -> list[dict]:
    db = get_db()
    conditions, params = [], []
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
        "INSERT INTO journal (miles_id, type, content, context, goal_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (entry.miles_id, entry.type, entry.content, entry.context, entry.goal_id, entry.created_at.isoformat()),
    )
    await db.commit()
    return cursor.lastrowid

async def get_journal_entries(miles_id: str | None = None, since_id: int | None = None, limit: int = 100) -> list[dict]:
    db = get_db()
    conditions, params = [], []
    if miles_id:
        conditions.append("miles_id = ?")
        params.append(miles_id)
    if since_id is not None:
        conditions.append("id > ?")
        params.append(since_id)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    params.append(limit)
    cursor = await db.execute(f"SELECT * FROM journal{where} ORDER BY id DESC LIMIT ?", params)
    return [dict(r) for r in await cursor.fetchall()]

# --- Tasks ---
async def create_task(task: Task) -> None:
    db = get_db()
    await db.execute(
        "INSERT INTO tasks (id, goal_id, assigned_to, validator, description, status, result, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        "SELECT * FROM tasks WHERE status = 'done' AND summary IS NOT NULL ORDER BY completed_at",
    )
    return [dict(r) for r in await cursor.fetchall()]

# --- Feedback ---
async def create_feedback(fb: Feedback) -> None:
    db = get_db()
    await db.execute(
        "INSERT INTO feedback (id, author, type, raw_content, external_validator_summary, miles_response, goal_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (fb.id, fb.author, fb.type, fb.raw_content, fb.external_validator_summary,
         fb.miles_response, fb.goal_id, fb.status, fb.created_at.isoformat()),
    )
    await db.commit()

async def get_pending_feedback() -> list[dict]:
    db = get_db()
    cursor = await db.execute("SELECT * FROM feedback WHERE status = 'pending' ORDER BY created_at")
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
        "INSERT INTO audits (id, auditor_id, miles_id, scope, findings, miles_response, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (audit.id, audit.auditor_id, audit.miles_id, audit.scope, audit.findings, audit.miles_response, audit.status, audit.created_at.isoformat()),
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
        "INSERT INTO scouting (id, hunter_id, source, topic, raw_findings, summary, validator, goal_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (mission.id, mission.hunter_id, mission.source, mission.topic,
         mission.raw_findings, mission.summary, mission.validator, mission.goal_id, mission.status, mission.created_at.isoformat()),
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
        "INSERT INTO events (agent_id, type, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
        (event.agent_id, event.type, event.content, json.dumps(event.metadata), event.created_at.isoformat()),
    )
    await db.commit()
    return cursor.lastrowid

async def list_events(limit: int = 50, since_id: int | None = None, event_type: str | None = None) -> list[dict]:
    db = get_db()
    conditions, params = [], []
    if since_id is not None:
        conditions.append("id > ?")
        params.append(since_id)
    if event_type:
        conditions.append("type = ?")
        params.append(event_type)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    params.append(limit)
    cursor = await db.execute(f"SELECT * FROM events{where} ORDER BY id DESC LIMIT ?", params)
    return [dict(r) for r in await cursor.fetchall()]

# --- Succession ---
async def create_succession(record: SuccessionRecord) -> int:
    db = get_db()
    cursor = await db.execute(
        "INSERT INTO succession (retired_id, promoted_id, new_shadow_id, compaction, journal_start, created_at) VALUES (?, ?, ?, ?, ?, ?)",
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
    db = get_db()
    cursor = await db.execute(
        "SELECT * FROM events WHERE type = 'human_input' AND json_extract(metadata, '$.read') IS NULL ORDER BY created_at",
    )
    return [dict(r) for r in await cursor.fetchall()]

async def mark_human_input_read(event_id: int) -> None:
    db = get_db()
    await db.execute("UPDATE events SET metadata = json_set(metadata, '$.read', 1) WHERE id = ?", (event_id,))
    await db.commit()
