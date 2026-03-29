import pytest
import pytest_asyncio
from app.agents.base import BaseAgent
from app.db import queries
from app.llm.base import LLMResponse
from app.models.schemas import Agent, Event, Goal, Task, Feedback, JournalEntry


class MockProvider:
    def __init__(self, response: str = "Mock response"):
        self.response = response
        self.calls: list[dict] = []

    async def complete(self, system_prompt: str, user_message: str,
                       model: str, max_tokens: int = 4096) -> LLMResponse:
        self.calls.append({"system_prompt": system_prompt, "user_message": user_message, "model": model})
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
    agent = TestAgent(agent_id="test_1", name="Test Agent", role="test",
                      layer="executor", model="haiku", provider=provider)
    await agent.register()
    record = await queries.get_agent("test_1")
    assert record is not None
    assert record["name"] == "Test Agent"
    assert record["status"] == "active"

@pytest.mark.asyncio
async def test_agent_step_calls_llm(test_db):
    provider = MockProvider("Do the thing")
    agent = TestAgent(agent_id="test_2", name="Test 2", role="test",
                      layer="executor", model="haiku", provider=provider)
    await agent.register()
    await agent.step()
    assert len(provider.calls) == 1
    assert provider.calls[0]["system_prompt"] == "You are a test agent."

@pytest.mark.asyncio
async def test_agent_logs_event(test_db):
    provider = MockProvider("Do the thing")
    agent = TestAgent(agent_id="test_3", name="Test 3", role="test",
                      layer="executor", model="haiku", provider=provider)
    await agent.register()
    await agent.step()
    events = await queries.list_events(limit=10)
    assert len(events) == 1
    assert events[0]["content"] == "Do the thing"
    assert events[0]["agent_id"] == "test_3"


# Task 7: Miles tests
from app.agents.miles import MilesAgent
from app.db import queries as q

@pytest.mark.asyncio
async def test_miles_reads_summaries_and_decides(test_db):
    provider = MockProvider('{"action": "acknowledge", "reasoning": "Task complete"}')
    miles = MilesAgent(agent_id="miles_v1", name="Miles v1", provider=provider)
    await miles.register()
    task = Task(id="t1", description="Analyze data", status="done", summary="3 anomalies found")
    await q.create_task(task)
    await miles.step()
    entries = await q.get_journal_entries(miles_id="miles_v1")
    assert len(entries) >= 1

@pytest.mark.asyncio
async def test_miles_writes_to_journal(test_db):
    provider = MockProvider('{"action": "delegate", "reasoning": "Need more data"}')
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
    miles.total_input_tokens = 800_000
    miles.total_output_tokens = 100_000
    assert miles.should_retire() is True


# Task 8: Shadow and Succession tests
from app.agents.shadow import ShadowAgent
from app.orchestrator.succession import perform_succession

@pytest.mark.asyncio
async def test_shadow_reads_journal(test_db):
    provider = MockProvider("Understood: focusing on data pipeline")
    shadow = ShadowAgent(agent_id="shadow_v1", name="Shadow v1", provider=provider)
    await shadow.register()
    entry = JournalEntry(miles_id="miles_v1", type="decision",
                         content="Focus on data pipeline", context="User said so")
    await q.create_journal_entry(entry)
    await shadow.step()
    assert shadow.last_journal_id >= 1
    assert len(provider.calls) == 1

@pytest.mark.asyncio
async def test_succession(test_db):
    provider = MockProvider("Ready to lead")
    miles = MilesAgent(agent_id="miles_v1", name="Miles v1", provider=provider)
    await miles.register()
    shadow = ShadowAgent(agent_id="shadow_v1", name="Shadow v1", provider=provider)
    await shadow.register()
    await q.create_journal_entry(JournalEntry(miles_id="miles_v1", type="decision", content="Decision 1"))
    new_miles, new_shadow = await perform_succession(miles, shadow, provider, compaction="Summary of decisions")
    old_record = await q.get_agent("miles_v1")
    assert old_record["status"] == "retired"
    assert new_miles.agent_id == "shadow_v1"
    assert new_miles.role == "miles"
    new_shadow_record = await q.get_agent(new_shadow.agent_id)
    assert new_shadow_record is not None
    assert new_shadow_record["layer"] == "decision"
    records = await q.list_successions()
    assert len(records) == 1
    assert records[0]["retired_id"] == "miles_v1"
    assert records[0]["promoted_id"] == "shadow_v1"


# Task 9: Validator, Executor, External Validator tests
from app.agents.validator import ValidatorAgent
from app.agents.executor import ExecutorAgent
from app.agents.external_validator import ExternalValidatorAgent

@pytest.mark.asyncio
async def test_executor_runs_task(test_db):
    provider = MockProvider("Analysis complete: found 3 anomalies in columns B, F, K")
    executor = ExecutorAgent(agent_id="dm_1", name="Data Mate", role="data_mate", provider=provider)
    await executor.register()
    task = Task(id="t1", description="Analyze dataset", status="pending", assigned_to="dm_1", validator="val_1")
    await q.create_task(task)
    await executor.execute_task("t1")
    updated = await q.get_task("t1")
    assert updated["status"] == "done"
    assert "3 anomalies" in updated["result"]

@pytest.mark.asyncio
async def test_validator_summarizes_task(test_db):
    provider = MockProvider("3 data anomalies found requiring review")
    validator = ValidatorAgent(agent_id="val_1", name="Data Validator", provider=provider)
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
    ext_val = ExternalValidatorAgent(agent_id="ext_val_1", name="External Validator", provider=provider)
    await ext_val.register()
    fb1 = Feedback(id="f1", author="maurissa", type="negative", raw_content="API has no error handling")
    fb2 = Feedback(id="f2", author="rimu", type="positive", raw_content="Data pipeline is well structured")
    await q.create_feedback(fb1)
    await q.create_feedback(fb2)
    await ext_val.summarize_pending()
    pending = await q.get_pending_feedback()
    for f in pending:
        assert f["external_validator_summary"] is not None


# Task 10: Hunter, Auditor, Adversary tests
from app.agents.hunter import HunterAgent
from app.agents.auditor import AuditorAgent
from app.agents.adversary import AdversaryAgent

@pytest.mark.asyncio
async def test_hunter_scouts(test_db):
    provider = MockProvider("Found 5 new multi-agent frameworks on GitHub trending")
    hunter = HunterAgent(agent_id="hunter_1", name="GitHub Hunter", source="github", provider=provider)
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
    provider = MockProvider("System audit: 2 active goals, 3 completed tasks")
    auditor = AuditorAgent(agent_id="auditor_1", name="Auditor", miles_id="miles_v1", provider=provider)
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
    adversary = AdversaryAgent(agent_id="maurissa_1", name="Maurissa", personality="harsh", provider=provider)
    await adversary.register()
    feedback_id = await adversary.evaluate("Current system state: basic API running")
    fb = await q.get_pending_feedback()
    assert len(fb) >= 1
    assert fb[0]["author"] == "maurissa"
    assert fb[0]["type"] == "negative"
