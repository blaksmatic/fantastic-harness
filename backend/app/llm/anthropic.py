import anthropic
from app.llm.base import LLMProvider, LLMResponse

class AnthropicProvider:
    def __init__(self, api_key: str) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def complete(self, system_prompt: str, user_message: str,
                       model: str, max_tokens: int = 4096) -> LLMResponse:
        response = await self.client.messages.create(
            model=model, max_tokens=max_tokens, system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return LLMResponse(
            content=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
