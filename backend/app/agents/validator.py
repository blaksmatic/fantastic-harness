from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider

VALIDATOR_SYSTEM_PROMPT = """You are a validator in the Fantastic Harness orchestra.
Your job is to check executor work and compress the results into a MINIMAL summary for Miles.
Miles only needs: What was done (1 sentence), Key findings (bullet points), Whether action is needed (yes/no).
Keep summaries under 100 words. Be precise. Strip all noise."""


class ValidatorAgent(BaseAgent):
    def __init__(self, agent_id: str, name: str, provider: LLMProvider,
                 model: str = settings.validation_model) -> None:
        super().__init__(agent_id=agent_id, name=name, role="validator",
                         layer="validation", model=model, provider=provider)

    @property
    def system_prompt(self) -> str:
        return VALIDATOR_SYSTEM_PROMPT

    async def step(self) -> None:
        pass

    async def validate_task(self, task_id: str) -> str:
        task = await queries.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        response = await self.think(
            f"Task: {task['description']}\n\nExecutor result:\n{task['result']}\n\nSummarize this for Miles in under 100 words.")
        await queries.update_task(task_id, summary=response.content)
        await self.log_event("task", f"Validated: {task['description']}")
        return response.content
