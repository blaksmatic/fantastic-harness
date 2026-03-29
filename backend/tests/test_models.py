from app.models.schemas import (
    Agent, AuditRecord, Event, Feedback, Goal,
    JournalEntry, ScoutingMission, SuccessionRecord, Task,
)

def test_goal_creation():
    goal = Goal(id="g1", description="Build pipeline", status="active", source="human")
    assert goal.id == "g1"
    assert goal.closed_at is None

def test_agent_creation():
    agent = Agent(id="miles_v1", name="Miles v1", role="miles", layer="decision",
                  model="claude-opus-4-20250514", status="active")
    assert agent.layer == "decision"
    assert agent.config == {}

def test_journal_entry():
    entry = JournalEntry(miles_id="miles_v1", type="decision",
                         content="Focus on data pipeline", context="User requested it")
    assert entry.id is None
    assert entry.goal_id is None

def test_task_creation():
    task = Task(id="t1", description="Analyze dataset", assigned_to="dm1", validator="v1")
    assert task.status == "pending"
    assert task.result is None

def test_feedback_creation():
    fb = Feedback(id="f1", author="maurissa", type="negative", raw_content="Bad API")
    assert fb.status == "pending"
    assert fb.external_validator_summary is None

def test_event_creation():
    event = Event(agent_id="miles_v1", type="decision", content="Prioritize pipeline")
    assert event.metadata == {}

def test_audit_record():
    audit = AuditRecord(id="a1", auditor_id="aud1", miles_id="m1", scope="full_system")
    assert audit.status == "running"

def test_scouting_mission():
    mission = ScoutingMission(id="s1", hunter_id="h1", source="github", topic="agents")
    assert mission.status == "pending"

def test_succession_record():
    record = SuccessionRecord(retired_id="m1", promoted_id="s1",
                              new_shadow_id="s2", compaction="Summary", journal_start=51)
    assert record.id is None
