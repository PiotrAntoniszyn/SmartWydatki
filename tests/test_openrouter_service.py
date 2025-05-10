import asyncio
import json

import httpx
import pytest

from app.openrouter_service import (
    OpenRouterConfigError,
    OpenRouterService,
)


@pytest.mark.asyncio
async def test_chat_completion_success():
    """Service should return parsed JSON when API responds with 200."""

    async def handler(request: httpx.Request) -> httpx.Response:  # noqa: D401
        content = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Hello!",
                    }
                }
            ]
        }
        return httpx.Response(200, json=content)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        service = OpenRouterService(api_key="test", http_client=client)
        resp = await service.chat_completion([{"role": "user", "content": "Hi"}])
        assert resp["choices"][0]["message"]["content"] == "Hello!"


@pytest.mark.asyncio
async def test_retry_on_429_then_success():
    """Service should retry after 429 and succeed."""
    calls = {
        "count": 0,
    }

    async def handler(request: httpx.Request) -> httpx.Response:  # noqa: D401
        calls["count"] += 1
        if calls["count"] == 1:
            # First call rate limited with Retry-After header
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"choices": [{"message": {"content": "done"}}]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        service = OpenRouterService(api_key="test", http_client=client, max_retries=2)
        resp = await service.chat_completion([{"role": "user", "content": "Hey"}])
        assert calls["count"] == 2  # One retry
        assert resp["choices"][0]["message"]["content"] == "done"


def test_missing_api_key():
    """Service should raise config error without API key."""
    with pytest.raises(OpenRouterConfigError):
        OpenRouterService(api_key=None, http_client=httpx.AsyncClient()) 