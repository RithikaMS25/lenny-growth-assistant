import pytest

from app.services.ollama_provider import generate_answer
from app.services.chat import ChatServiceError, _generate_anthropic_agent, _generate_cloud, _select_provider
from app.services.pi_provider import PiProviderError, generate_answer as generate_with_pi
from app.schemas.chat import ChatRequest


@pytest.mark.asyncio
async def test_ollama_requires_grounded_evidence():
    with pytest.raises(ValueError, match="Evidence"):
        await generate_answer(question="What works?", evidence=[])


@pytest.mark.asyncio
async def test_ollama_rejects_empty_question():
    with pytest.raises(ValueError, match="Question"):
        await generate_answer(question="  ", evidence=[{"source_title": "x", "source_url": None, "content": "evidence"}])


def test_chat_contract_rejects_unknown_provider():
    with pytest.raises(Exception):
        ChatRequest(question="What is supported?", provider="fake")


@pytest.mark.asyncio
async def test_cloud_provider_reports_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ChatServiceError, match="OPENAI_API_KEY is not configured"):
        await _generate_cloud("openai", "question", [{"source_title": "source", "source_url": None, "content": "evidence"}])


@pytest.mark.asyncio
async def test_pi_provider_returns_print_output(monkeypatch):
    class Process:
        returncode = 0
        async def communicate(self): return b"A grounded answer.", b""

    async def spawn(*args, **kwargs): return Process()
    monkeypatch.setattr("app.services.pi_provider.asyncio.create_subprocess_exec", spawn)
    result = await generate_with_pi(question="A question", evidence=[{"source_title": "source", "source_url": None, "content": "evidence"}])
    assert result == "A grounded answer."


@pytest.mark.asyncio
async def test_pi_provider_surfaces_nonzero_exit(monkeypatch):
    class Process:
        returncode = 2
        async def communicate(self): return b"", b"provider unavailable"

    async def spawn(*args, **kwargs): return Process()
    monkeypatch.setattr("app.services.pi_provider.asyncio.create_subprocess_exec", spawn)
    with pytest.raises(PiProviderError, match="provider unavailable"):
        await generate_with_pi(question="A question", evidence=[{"source_title": "source", "source_url": None, "content": "evidence"}])


@pytest.mark.asyncio
async def test_claude_agent_sdk_is_tools_disabled_and_returns_text(monkeypatch):
    import sys
    from types import SimpleNamespace
    options_seen = []

    class TextBlock:
        def __init__(self, text): self.text = text
    class AssistantMessage:
        def __init__(self, content): self.content = content
    class ResultMessage:
        is_error = False
    class Options:
        def __init__(self, **kwargs): options_seen.append(kwargs)
    async def query(*, prompt, options):
        assert "evidence" in prompt
        yield AssistantMessage([TextBlock("A grounded SDK answer.")])
        yield ResultMessage()

    monkeypatch.setitem(sys.modules, "claude_agent_sdk", SimpleNamespace(
        AssistantMessage=AssistantMessage, ClaudeAgentOptions=Options,
        ResultMessage=ResultMessage, TextBlock=TextBlock, query=query,
    ))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-only-placeholder")
    answer = await _generate_anthropic_agent("source evidence")
    assert answer == "A grounded SDK answer."
    assert options_seen[0]["tools"] == []
    assert options_seen[0]["max_turns"] == 1


def test_pi_is_disabled_by_default_after_live_quality_failure(monkeypatch):
    monkeypatch.delenv("ENABLE_PI_PROVIDER", raising=False)
    with pytest.raises(ChatServiceError, match="Pi is disabled"):
        _select_provider("pi")
