import pytest
from app.orchestrator.scheduler import Orchestrator
from app.db import queries
from app.models.schemas import Goal
from app.llm.base import LLMResponse


class MockProvider:
    def __init__(self, response: str = "Mock response"):
        self.response = response
        self.calls: list[dict] = []

    async def complete(self, system_prompt: str, user_message: str,
                       model: str, max_tokens: int = 4096) -> LLMResponse:
        self.calls.append({"system_prompt": system_prompt, "user_message": user_message, "model": model})
        return LLMResponse(content=self.response, input_tokens=100, output_tokens=50)


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
