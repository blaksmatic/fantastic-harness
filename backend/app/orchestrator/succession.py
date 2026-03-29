from app.agents.miles import MilesAgent
from app.agents.shadow import ShadowAgent
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import Event, SuccessionRecord


async def perform_succession(retiring_miles: MilesAgent, shadow: ShadowAgent,
                              provider: LLMProvider, compaction: str) -> tuple[MilesAgent, ShadowAgent]:
    # 1. Retire old Miles
    await retiring_miles.retire()
    await retiring_miles.log_event("retirement",
        f"{retiring_miles.name} retired after {retiring_miles.decision_count} decisions")

    # 2. Promote Shadow to Miles
    version = shadow.agent_id.split("_v")[-1] if "_v" in shadow.agent_id else "1"
    await queries.update_agent(shadow.agent_id, role="miles", status="active")
    new_miles = MilesAgent(agent_id=shadow.agent_id, name=f"Miles v{int(version) + 1}",
                           provider=provider, model=shadow.model)
    new_miles.total_input_tokens = shadow.total_input_tokens
    new_miles.total_output_tokens = shadow.total_output_tokens

    # 3. Spawn new Shadow
    new_shadow_version = int(version) + 2
    new_shadow_id = f"shadow_v{new_shadow_version}"
    new_shadow = ShadowAgent(agent_id=new_shadow_id, name=f"Shadow v{new_shadow_version}",
                             provider=provider, model=shadow.model)
    await new_shadow.register()

    # 4. Record succession
    record = SuccessionRecord(retired_id=retiring_miles.agent_id, promoted_id=shadow.agent_id,
                              new_shadow_id=new_shadow_id, compaction=compaction,
                              journal_start=shadow.last_journal_id)
    await queries.create_succession(record)

    # 5. Log promotion event
    await queries.create_event(Event(agent_id=shadow.agent_id, type="promotion",
        content=f"{shadow.name} promoted to {new_miles.name}. {new_shadow.name} spawned."))

    return new_miles, new_shadow
