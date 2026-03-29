import pytest
import pytest_asyncio
from app.db.connection import get_db
from app.db import queries
from app.models.schemas import Agent, Event, Feedback, Goal, JournalEntry, Task


@pytest.mark.asyncio
async def test_tables_created(test_db):
    db = get_db()
    cursor = await db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in await cursor.fetchall()]
    # Filter out sqlite_sequence (created by AUTOINCREMENT)
    tables = [t for t in tables if t != "sqlite_sequence"]
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
    assert tuple(row) == ("g1", "Build data pipeline", "active")


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
    assert tuple(row) == ("miles_v1", "decision", "Prioritize data pipeline")


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
    agent = Agent(id="miles_v1", name="Miles v1", role="miles", layer="decision", model="opus", status="active")
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
    entry = JournalEntry(miles_id="miles_v1", type="decision", content="Focus on pipeline", context="User said so")
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
