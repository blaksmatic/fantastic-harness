from app.agents.base import BaseAgent
from app.config import settings
from app.db import queries
from app.llm.base import LLMProvider
from app.models.schemas import JournalEntry

MILES_SYSTEM_PROMPT = """You are Miles, the autonomous decision-maker of the Fantastic Harness orchestra.

Your ONLY job is to make decisions. You NEVER execute work yourself.

You receive:
1. Summaries from validators (about executor and hunter work)
2. Summaries from the External Validator (about adversarial feedback)
3. Direct reports from auditors
4. Direct input from humans (highest authority)

For each piece of information, you must decide:
- ACKNOWLEDGE: Note the information, no action needed
- DELEGATE: Create a new task for an executor
- REJECT: Reject feedback/suggestion with reasoning
- DISPATCH_AUDIT: Send an auditor to investigate something
- DISPATCH_HUNTER: Send a hunter to research something externally

Respond with JSON:
{
  "action": "acknowledge|delegate|reject|dispatch_audit|dispatch_hunter",
  "reasoning": "why you made this decision",
  "task": "description of work to delegate (if action is delegate)",
  "target": "what to audit or hunt (if dispatch_audit or dispatch_hunter)"
}

You are always-on. Goals never auto-complete. Only humans can close goals.
If you disagree with feedback, reject it and explain why. Stand by your decisions unless a human overrides you."""


class MilesAgent(BaseAgent):
    def __init__(self, agent_id: str, name: str, provider: LLMProvider,
                 model: str = settings.decision_model) -> None:
        super().__init__(agent_id=agent_id, name=name, role="miles",
                         layer="decision", model=model, provider=provider)

    @property
    def system_prompt(self) -> str:
        return MILES_SYSTEM_PROMPT

    def should_retire(self) -> bool:
        total = self.total_input_tokens + self.total_output_tokens
        max_context = 1_000_000
        pressure = total / max_context
        if pressure >= settings.context_pressure_threshold:
            return True
        if self.decision_count >= settings.max_decisions_before_retire:
            return True
        return False

    async def step(self) -> None:
        context_parts = []

        # 1. Read validator summaries from completed tasks
        task_summaries = await queries.get_unread_task_summaries()
        if task_summaries:
            summaries_text = "\n".join(f"- Task '{t['description']}': {t['summary']}" for t in task_summaries)
            context_parts.append(f"VALIDATOR SUMMARIES:\n{summaries_text}")

        # 2. Read External Validator summaries from feedback
        feedback_items = await queries.get_pending_feedback()
        summarized = [f for f in feedback_items if f.get("external_validator_summary")]
        if summarized:
            fb_text = "\n".join(f"- {f['author']} ({f['type']}): {f['external_validator_summary']}" for f in summarized)
            context_parts.append(f"ADVERSARIAL FEEDBACK (via External Validator):\n{fb_text}")

        # 3. Read human input
        human_input = await queries.get_pending_human_input()
        if human_input:
            input_text = "\n".join(f"- {h['content']}" for h in human_input)
            context_parts.append(f"HUMAN INPUT:\n{input_text}")

        # 4. Read active goals
        goals = await queries.list_goals(status="active")
        if goals:
            goals_text = "\n".join(f"- [{g['id']}] {g['description']}" for g in goals)
            context_parts.append(f"ACTIVE GOALS:\n{goals_text}")

        if not context_parts:
            return

        user_message = "\n\n".join(context_parts)
        response = await self.think(user_message)
        self.decision_count += 1

        entry = JournalEntry(miles_id=self.agent_id, type="decision",
                             content=response.content, context=user_message[:500])
        await queries.create_journal_entry(entry)
        await self.log_event("decision", response.content)

        for h in human_input:
            await queries.mark_human_input_read(h["id"])
