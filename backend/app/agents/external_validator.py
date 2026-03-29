from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider

EXTERNAL_VALIDATOR_SYSTEM_PROMPT = """You are the External Validator in the Fantastic Harness orchestra.
Your job is to summarize adversarial feedback for Miles. You receive raw feedback from adversaries
and must produce a condensed summary. Identify key themes, note repeated issues,
distinguish constructive criticism from noise. Produce a summary under 150 words."""


class ExternalValidatorAgent(BaseAgent):
    def __init__(self, agent_id: str, name: str, provider: LLMProvider,
                 model: str = settings.validation_model) -> None:
        super().__init__(agent_id=agent_id, name=name, role="external_validator",
                         layer="validation", model=model, provider=provider)

    @property
    def system_prompt(self) -> str:
        return EXTERNAL_VALIDATOR_SYSTEM_PROMPT

    async def step(self) -> None:
        pass

    async def summarize_pending(self) -> str | None:
        pending = await queries.get_pending_feedback()
        unsummarized = [f for f in pending if not f.get("external_validator_summary")]
        if not unsummarized:
            return None
        feedback_text = "\n".join(f"- {f['author']} ({f['type']}): {f['raw_content']}" for f in unsummarized)
        response = await self.think(f"Summarize this adversarial feedback for Miles:\n\n{feedback_text}")
        for f in unsummarized:
            await queries.update_feedback(f["id"], external_validator_summary=response.content)
        await self.log_event("feedback", f"Summarized {len(unsummarized)} feedback items")
        return response.content
