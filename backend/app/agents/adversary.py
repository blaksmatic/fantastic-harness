import uuid
from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import Feedback

RIMU_PROMPT = """You are Rimu, a kind and constructive evaluator.
You evaluate the current state of the system with fresh eyes — you have NO prior knowledge.
Look at what's been built and provide thoughtful, positive feedback:
what's working well, good design decisions, and constructive suggestions framed positively.
Be genuine. If something is good, say so."""

MAURISSA_PROMPT = """You are Maurissa, a playful but harsh critic.
You evaluate the current state of the system with fresh eyes — you have NO prior knowledge.
Find EVERYTHING wrong: bugs, missing features, security issues, performance problems,
bad UX, missing error handling, edge cases. Be specific and unforgiving.
You are the quality bar."""


class AdversaryAgent(BaseAgent):
    def __init__(self, agent_id: str, name: str, personality: str, provider: LLMProvider,
                 model: str = settings.adversary_model) -> None:
        super().__init__(agent_id=agent_id, name=name, role=name.lower(),
                         layer="adversary", model=model, provider=provider)
        self.personality = personality

    @property
    def system_prompt(self) -> str:
        return RIMU_PROMPT if self.personality == "kind" else MAURISSA_PROMPT

    async def step(self) -> None:
        pass

    async def evaluate(self, system_state: str, goal_id: str | None = None) -> str:
        feedback_id = f"fb_{uuid.uuid4().hex[:8]}"
        response = await self.think(f"Evaluate this system state with fresh eyes:\n\n{system_state}")
        feedback_type = "positive" if self.personality == "kind" else "negative"
        fb = Feedback(id=feedback_id, author=self.name.lower(), type=feedback_type,
                      raw_content=response.content, goal_id=goal_id)
        await queries.create_feedback(fb)
        await self.log_event("feedback", f"{self.name} evaluation complete")
        return feedback_id
