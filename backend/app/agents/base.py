from abc import ABC, abstractmethod
from app.db import queries
from app.llm.base import LLMProvider, LLMResponse
from app.models.schemas import Agent, Event


class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str, role: str, layer: str,
                 model: str, provider: LLMProvider) -> None:
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.layer = layer
        self.model = model
        self.provider = provider
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.decision_count = 0

    async def register(self) -> None:
        agent = Agent(id=self.agent_id, name=self.name, role=self.role,
                      layer=self.layer, model=self.model, status="active")
        await queries.create_agent(agent)

    async def think(self, user_message: str, max_tokens: int = 4096) -> LLMResponse:
        response = await self.provider.complete(
            system_prompt=self.system_prompt, user_message=user_message,
            model=self.model, max_tokens=max_tokens,
        )
        self.total_input_tokens += response.input_tokens
        self.total_output_tokens += response.output_tokens
        return response

    async def log_event(self, event_type: str, content: str, metadata: dict | None = None) -> int:
        event = Event(agent_id=self.agent_id, type=event_type,
                      content=content, metadata=metadata or {})
        return await queries.create_event(event)

    async def retire(self) -> None:
        await queries.update_agent(self.agent_id, status="retired")

    @property
    @abstractmethod
    def system_prompt(self) -> str: ...

    @abstractmethod
    async def step(self) -> None: ...
