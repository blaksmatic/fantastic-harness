from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider

SHADOW_SYSTEM_PROMPT = """You are a Shadow — the silent observer of Miles's decisions.

Your job is to read Miles's journal entries and build a deep understanding of:
- What decisions have been made and why
- What the current goals and priorities are
- What feedback has been accepted or rejected
- The overall state of the system

You do NOT make decisions. You do NOT take action. You observe and learn.

When you are promoted to Miles, you will need this understanding to continue
making decisions seamlessly. Summarize your understanding concisely."""


class ShadowAgent(BaseAgent):
    def __init__(self, agent_id: str, name: str, provider: LLMProvider,
                 model: str = settings.decision_model) -> None:
        super().__init__(agent_id=agent_id, name=name, role="shadow",
                         layer="decision", model=model, provider=provider)
        self.last_journal_id = 0

    @property
    def system_prompt(self) -> str:
        return SHADOW_SYSTEM_PROMPT

    async def step(self) -> None:
        entries = await queries.get_journal_entries(since_id=self.last_journal_id)
        if not entries:
            return
        entries.reverse()  # chronological order
        entries_text = "\n".join(f"[{e['id']}] ({e['type']}) {e['content']}" for e in entries)
        user_message = f"New journal entries from Miles:\n\n{entries_text}\n\nSummarize your updated understanding."
        await self.think(user_message)
        self.last_journal_id = max(e["id"] for e in entries)
