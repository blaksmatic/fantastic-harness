from app.llm.base import LLMProvider, LLMResponse

def test_llm_response_model():
    resp = LLMResponse(content="Hello", input_tokens=10, output_tokens=5)
    assert resp.content == "Hello"
    assert resp.total_tokens == 15

def test_provider_protocol():
    from app.llm.anthropic import AnthropicProvider
    provider = AnthropicProvider.__new__(AnthropicProvider)
    assert isinstance(provider, LLMProvider)
