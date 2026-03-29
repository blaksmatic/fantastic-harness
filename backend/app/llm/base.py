from dataclasses import dataclass
from typing import Protocol, runtime_checkable

@dataclass
class LLMResponse:
    content: str
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

@runtime_checkable
class LLMProvider(Protocol):
    async def complete(self, system_prompt: str, user_message: str,
                       model: str, max_tokens: int = 4096) -> LLMResponse: ...
