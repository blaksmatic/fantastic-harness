from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider

EXECUTOR_SYSTEM_PROMPT = """You are an executor agent in the Fantastic Harness orchestra.
Your job is to complete the task assigned to you. Work thoroughly and report your findings.
Provide a detailed result of your work. Be specific about what you found or built."""


class ExecutorAgent(BaseAgent):
    def __init__(self, agent_id: str, name: str, role: str, provider: LLMProvider,
                 model: str = settings.executor_model) -> None:
        super().__init__(agent_id=agent_id, name=name, role=role,
                         layer="executor", model=model, provider=provider)

    @property
    def system_prompt(self) -> str:
        return EXECUTOR_SYSTEM_PROMPT

    async def step(self) -> None:
        pass

    async def execute_task(self, task_id: str) -> str:
        task = await queries.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        await queries.update_task(task_id, status="running")
        await self.log_event("task", f"Starting: {task['description']}")
        response = await self.think(f"Execute this task:\n\n{task['description']}")
        await queries.update_task(task_id, status="done", result=response.content)
        await self.log_event("task", f"Completed: {task['description']}")
        return response.content
