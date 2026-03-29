import uuid
from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import ScoutingMission

HUNTER_SYSTEM_PROMPT = """You are a Hunter in the Fantastic Harness orchestra.
Your job is to scout external sources for intelligence. Research what people
are doing, thinking, and building. Provide a thorough report with key trends,
notable projects, and relevant insights. Be specific and cite sources when possible."""


class HunterAgent(BaseAgent):
    def __init__(self, agent_id: str, name: str, source: str, provider: LLMProvider,
                 model: str = settings.hunter_model) -> None:
        super().__init__(agent_id=agent_id, name=name, role="hunter",
                         layer="hunter", model=model, provider=provider)
        self.source = source

    @property
    def system_prompt(self) -> str:
        return HUNTER_SYSTEM_PROMPT

    async def step(self) -> None:
        pass

    async def scout(self, topic: str, goal_id: str | None = None) -> str:
        mission_id = f"scout_{uuid.uuid4().hex[:8]}"
        mission = ScoutingMission(id=mission_id, hunter_id=self.agent_id, source=self.source,
                                  topic=topic, goal_id=goal_id, status="running")
        await queries.create_scouting(mission)
        await self.log_event("scouting", f"Scouting {self.source} for: {topic}")
        response = await self.think(f"Scout {self.source} for information about: {topic}\n\nProvide a detailed intelligence report.")
        await queries.update_scouting(mission_id, raw_findings=response.content, status="done")
        await self.log_event("scouting", f"Completed scouting: {topic}")
        return mission_id
