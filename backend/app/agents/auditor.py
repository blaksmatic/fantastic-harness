import uuid
from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import AuditRecord

AUDITOR_SYSTEM_PROMPT = """You are an Auditor in the Fantastic Harness orchestra.
You are dispatched by Miles to independently audit the current state of the system.
Your report goes DIRECTLY to Miles — no validator in between.
Audit thoroughly: what has been built, what validators are reporting vs reality,
gaps, risks, inconsistencies, and overall system health. Be honest and detailed."""


class AuditorAgent(BaseAgent):
    def __init__(self, agent_id: str, name: str, miles_id: str, provider: LLMProvider,
                 model: str = settings.auditor_model) -> None:
        super().__init__(agent_id=agent_id, name=name, role="auditor",
                         layer="auditor", model=model, provider=provider)
        self.miles_id = miles_id

    @property
    def system_prompt(self) -> str:
        return AUDITOR_SYSTEM_PROMPT

    async def step(self) -> None:
        pass

    async def audit(self, scope: str) -> str:
        audit_id = f"audit_{uuid.uuid4().hex[:8]}"
        record = AuditRecord(id=audit_id, auditor_id=self.agent_id, miles_id=self.miles_id, scope=scope)
        await queries.create_audit(record)
        await self.log_event("audit", f"Starting audit: {scope}")
        goals = await queries.list_goals()
        agents = await queries.list_agents()
        recent_events = await queries.list_events(limit=20)
        context = (f"AUDIT SCOPE: {scope}\n\nGOALS: {len(goals)} total\n"
                   + "\n".join(f"  - [{g['id']}] {g['description']} ({g['status']})" for g in goals)
                   + f"\n\nAGENTS: {len(agents)} total\n"
                   + "\n".join(f"  - {a['name']} ({a['role']}, {a['status']})" for a in agents)
                   + f"\n\nRECENT EVENTS: {len(recent_events)}\n"
                   + "\n".join(f"  - [{e['type']}] {e['content']}" for e in recent_events[:10]))
        response = await self.think(context)
        await queries.update_audit(audit_id, findings=response.content, status="completed")
        await self.log_event("audit", f"Audit complete: {scope}")
        return audit_id
