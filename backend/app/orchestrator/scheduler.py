import asyncio
import uuid

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
        self.miles = MilesAgent(agent_id="miles_v1", name="Miles v1", provider=self.provider)
        await self.miles.register()
        self.shadow = ShadowAgent(agent_id="shadow_v1", name="Shadow v1", provider=self.provider)
        await self.shadow.register()
        self.ext_validator = ExternalValidatorAgent(agent_id="ext_val_1", name="External Validator", provider=self.provider)
        await self.ext_validator.register()
        default_val = ValidatorAgent(agent_id="val_default", name="Default Validator", provider=self.provider)
        await default_val.register()
        self.validators["default"] = default_val
        await queries.create_event(Event(agent_id="system", type="decision",
            content="Fantastic Harness initialized. Miles v1 and Shadow v1 online."))

    async def run_miles_cycle(self) -> None:
        if not self.miles:
            return
        await self.miles.step()
        if self.miles.should_retire():
            compaction = f"Miles retiring after {self.miles.decision_count} decisions"
            self.miles, self.shadow = await perform_succession(
                self.miles, self.shadow, self.provider, compaction=compaction)

    async def run_shadow_cycle(self) -> None:
        if not self.shadow:
            return
        await self.shadow.step()

    async def trigger_adversary(self, name: str) -> str:
        personality = "kind" if name == "rimu" else "harsh"
        adv_id = f"{name}_{uuid.uuid4().hex[:6]}"
        adversary = AdversaryAgent(agent_id=adv_id, name=name.capitalize(),
                                    personality=personality, provider=self.provider)
        await adversary.register()
        goals = await queries.list_goals()
        recent_events = await queries.list_events(limit=10)
        state = (f"Goals: {len(goals)}\n"
                 + "\n".join(f"  - {g['description']} ({g['status']})" for g in goals)
                 + f"\n\nRecent activity:\n"
                 + "\n".join(f"  - {e['content']}" for e in recent_events))
        feedback_id = await adversary.evaluate(state)
        if self.ext_validator:
            await self.ext_validator.summarize_pending()
        await adversary.retire()
        return feedback_id

    async def dispatch_executor(self, task_id: str, role: str = "executor") -> None:
        exec_id = f"{role}_{uuid.uuid4().hex[:6]}"
        executor = ExecutorAgent(agent_id=exec_id, name=role.replace("_", " ").title(),
                                  role=role, provider=self.provider)
        await executor.register()
        await executor.execute_task(task_id)
        validator = self.validators.get("default")
        if validator:
            await validator.validate_task(task_id)
        await executor.retire()

    async def dispatch_hunter(self, source: str, topic: str, goal_id: str | None = None) -> str:
        hunter_id = f"hunter_{uuid.uuid4().hex[:6]}"
        hunter = HunterAgent(agent_id=hunter_id, name=f"{source.title()} Hunter",
                              source=source, provider=self.provider)
        await hunter.register()
        mission_id = await hunter.scout(topic, goal_id=goal_id)
        await hunter.retire()
        return mission_id

    async def dispatch_auditor(self, scope: str) -> str:
        if not self.miles:
            raise RuntimeError("No active Miles")
        audit_id = f"auditor_{uuid.uuid4().hex[:6]}"
        auditor = AuditorAgent(agent_id=audit_id, name="Auditor",
                                miles_id=self.miles.agent_id, provider=self.provider)
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
                await queries.create_event(Event(agent_id="system", type="decision",
                    content=f"Error in {name} loop: {str(e)}"))
            await asyncio.sleep(interval)

    async def stop(self) -> None:
        self.running = False
