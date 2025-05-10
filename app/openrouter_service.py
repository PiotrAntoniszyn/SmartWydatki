"""OpenRouter Service
~~~~~~~~~~~~~~~~~~~
A lightweight, stateless wrapper around the OpenRouter.ai Chat Completions
endpoint.  Implementation follows the design documented in
`openrouter-service-implementation-plan.md`.

Only a subset of the full implementation is provided in this commit.  The
remaining functionality (retries, response validation, metrics, etc.) will be
added in subsequent iterations.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, MutableMapping, Protocol, runtime_checkable

import httpx
import backoff
import jsonschema

__all__ = [
    "OpenRouterService",
    # custom errors
    "OpenRouterError",
    "OpenRouterConfigError",
    "OpenRouterSchemaError",
]

logger = logging.getLogger("openrouter_service")

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class OpenRouterError(Exception):
    """Base‐class for all service related errors."""


class OpenRouterConfigError(OpenRouterError):
    """Raised when configuration (e.g. API key) is missing or invalid."""


class OpenRouterSchemaError(OpenRouterError):
    """Raised when the response fails JSON schema validation in strict mode."""


# ---------------------------------------------------------------------------
# Protocols & helper types
# ---------------------------------------------------------------------------


@runtime_checkable
class HTTPClientProtocol(Protocol):
    """Subset of `httpx.AsyncClient` methods required by the service.

    A protocol is used to ease dependency-injection during unit testing.
    """

    async def post(self, url: str, json: Any, headers: MutableMapping[str, str], timeout: float) -> httpx.Response:  # noqa: E501
        ...

    async def get(self, url: str, timeout: float) -> httpx.Response:  # noqa: D401,E501
        ...

    async def aclose(self) -> None:  # noqa: D401
        ...


# ---------------------------------------------------------------------------
# Core service implementation
# ---------------------------------------------------------------------------


class OpenRouterService:
    """Stateless wrapper for the OpenRouter.ai chat completions API."""

    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "openrouter/azure/gpt-4o",
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        default_system_prompt: str | None = None,
        default_response_format: Dict[str, Any] | None = None,
        http_client: HTTPClientProtocol | None = None,
    ) -> None:
        self._api_key: str | None = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self._api_key:
            raise OpenRouterConfigError("OPENROUTER_API_KEY is required but not provided.")

        self.model_name: str = model_name
        self.base_url: str = base_url.rstrip("/")
        self.timeout: float = float(timeout)
        self.max_retries: int = int(max_retries)
        self.backoff_factor: float = float(backoff_factor)
        self.default_system_prompt = default_system_prompt
        self.default_response_format = default_response_format

        # Use provided client or create one.
        self._client: HTTPClientProtocol = (
            http_client
            if http_client is not None
            else httpx.AsyncClient(http2=True, timeout=self.timeout)
        )

        logger.debug(
            "OpenRouterService initialised with model=%s, base_url=%s, timeout=%s, max_retries=%s",  # noqa: E501
            self.model_name,
            self.base_url,
            self.timeout,
            self.max_retries,
        )

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        *,
        model_params: Dict[str, Any] | None = None,
        response_format: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Send a chat completion request.

        Parameters
        ----------
        messages
            Sequence of message dictionaries as expected by OpenRouter
            (role & content).
        model_params
            Extra parameters forwarded to the model (temperature, max_tokens,
            etc.).  Values override those passed in *constructor* if any.
        response_format
            Optional response format following the OpenRouter JSON schema.

        Returns
        -------
        dict
            Parsed JSON response from the API.
        """
        payload = self._build_payload(messages, model_params, response_format)
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "X-Title": "OpenRouterService",
        }

        resp = await self._post_with_retry(endpoint, payload, headers)
        data = resp.json()

        # Validate response under strict mode if defined
        final_response_format = response_format or self.default_response_format
        if final_response_format:
            self._validate_response(data, final_response_format)

        return data

    async def generate_completion(self, prompt: str, **kwargs: Any) -> str:
        """Shortcut for single user prompt, returns assistant content only."""
        messages = [{"role": "user", "content": prompt}]
        full_resp = await self.chat_completion(messages, **kwargs)
        # The OpenRouter response conforms to OpenAI format.
        try:
            return full_resp["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise OpenRouterError("Unexpected response format from OpenRouter API.")

    def health_check(self) -> bool:
        """Sync health-check hitting `/models` endpoint.

        This is intentionally synchronous (blocking) because it is typically
        executed during container start-up where an event-loop might not be
        running yet.
        """
        url = f"{self.base_url}/models"
        try:
            resp = httpx.get(url, headers={"Authorization": f"Bearer {self._api_key}"}, timeout=5.0)
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    # ---------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------

    def _build_payload(
        self,
        messages: List[Dict[str, str]],
        model_params: Dict[str, Any] | None,
        response_format: Dict[str, Any] | None,
    ) -> Dict[str, Any]:
        """Construct JSON payload for chat/completions endpoint."""
        if self.default_system_prompt and (not messages or messages[0].get("role") != "system"):
            # Prepend default system prompt.
            messages = [{"role": "system", "content": self.default_system_prompt}] + list(messages)

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
        }

        if model_params:
            payload.update(model_params)

        if response_format:
            payload["response_format"] = response_format
        elif self.default_response_format:
            payload["response_format"] = self.default_response_format

        return payload

    async def _post_with_retry(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
    ) -> httpx.Response:
        """POST with retry/back-off logic for transient errors."""

        async def _send_request() -> httpx.Response:
            start = time.perf_counter()
            resp = await self._client.post(endpoint, json=payload, headers=headers, timeout=self.timeout)
            duration = time.perf_counter() - start
            logger.info(
                "openrouter.request", extra={"status": resp.status_code, "duration": duration}
            )

            # Handle explicit 429 here to integrate Retry-After without raising
            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", 0))
                await self._handle_rate_limit(retry_after)
                raise httpx.HTTPStatusError("Rate limited", request=resp.request, response=resp)

            if 500 <= resp.status_code < 600:
                # Treat server errors as retryable
                raise httpx.HTTPStatusError("Server error", request=resp.request, response=resp)

            resp.raise_for_status()
            return resp

        # Use backoff library for retries with expo backoff
        @backoff.on_exception(
            backoff.expo,
            (httpx.TimeoutException, httpx.HTTPStatusError),
            factor=self.backoff_factor,
            max_tries=self.max_retries,
            jitter=None,
        )
        async def _wrapped() -> httpx.Response:  # noqa: D401
            return await _send_request()

        return await _wrapped()

    async def _handle_rate_limit(self, retry_after: float) -> None:
        """Sleep coroutine respecting Retry-After header."""
        wait_for = retry_after if retry_after > 0 else self.backoff_factor
        logger.warning("openrouter.rate_limit", extra={"sleep": wait_for})
        await asyncio.sleep(wait_for)

    def _validate_response(
        self,
        resp_json: Dict[str, Any],
        response_format: Dict[str, Any],
    ) -> None:
        """Validate assistant content against provided JSON schema when strict."""
        try:
            if response_format.get("type") != "json_schema":
                return  # Nothing to validate
            j_schema = response_format.get("json_schema", {})
            if not j_schema.get("strict"):
                return
            schema_def = j_schema.get("schema")
            if not schema_def:
                return

            # Extract assistant content
            assistant_content = resp_json["choices"][0]["message"]["content"]
            parsed = json.loads(assistant_content)
            jsonschema.validate(instance=parsed, schema=schema_def)
        except (json.JSONDecodeError, jsonschema.ValidationError) as exc:
            logger.error("openrouter.schema_error", extra={"error": str(exc)})
            raise OpenRouterSchemaError(str(exc))

    # ---------------------------------------------------------------------
    # Utility helpers
    # ---------------------------------------------------------------------

    @staticmethod
    def _mask_secrets(data: str | Dict[str, Any]) -> str | Dict[str, Any]:
        """Mask any occurrences of API key in the provided string/dict."""
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not api_key:
            return data
        replacement = f"{api_key[:4]}…{api_key[-4:]}"  # type: ignore[str-bytes-safe]
        if isinstance(data, str):
            return data.replace(api_key, replacement)
        # naive deep traverse
        text = json.dumps(data)
        text = text.replace(api_key, replacement)
        return json.loads(text)

    # ---------------------------------------------------------------------
    # Async cleanup
    # ---------------------------------------------------------------------

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        if isinstance(self._client, httpx.AsyncClient):
            await self._client.aclose()

    # Provide context-manager helpers
    async def __aenter__(self) -> "OpenRouterService":  # noqa: D401
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.aclose() 