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
