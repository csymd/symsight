# Copyright (c) 2026, PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""xAI / SpaceXAI client helpers."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from symsight.config import DEFAULT_BASE_URL

HTTP_TIMEOUT_SECS = 120.0

_XAI_KEY = re.compile(r"xai-[A-Za-z0-9_-]+")
_BEARER = re.compile(r"(?i)(bearer\s+)\S+")


def redact_secrets(text: str) -> str:
    """Strip API keys / bearer tokens from error text before it hits logs or stderr."""
    text = _XAI_KEY.sub("xai-[redacted]", text)
    return _BEARER.sub(r"\1[redacted]", text)


def _validate_base_url(base_url: str) -> None:
    parsed = urlparse(base_url.strip())
    host = (parsed.hostname or "").lower()
    if parsed.scheme == "https":
        return
    if parsed.scheme == "http" and host in {"127.0.0.1", "localhost", "::1"}:
        return
    raise ValueError("SYMSIGHT_BASE_URL must be https:// (http is allowed only for localhost)")


def make_client(*, api_key: str, base_url: str = DEFAULT_BASE_URL) -> Any:
    from openai import OpenAI

    _validate_base_url(base_url)
    return OpenAI(api_key=api_key, base_url=base_url, timeout=HTTP_TIMEOUT_SECS)


def response_text(response: object) -> str:
    """Pull final assistant text; skip reasoning/tool chatter when possible."""
    raw = getattr(response, "output_text", None) or ""
    if raw.strip():
        return raw

    parts: list[str] = []
    for item in getattr(response, "output", None) or []:
        item_type = getattr(item, "type", None) or ""
        if (
            item_type
            and item_type not in ("message", "output_text", "")
            and ("reason" in item_type or "tool" in item_type)
        ):
            continue
        for content in getattr(item, "content", None) or []:
            ctype = getattr(content, "type", None)
            if ctype in ("output_text", "text", None):
                text = getattr(content, "text", None)
                if text:
                    parts.append(str(text))
    return "".join(parts)


def create_completion(
    client: Any,
    *,
    model: str,
    system: str,
    user: str,
    use_search: bool = False,
) -> str:
    kwargs: dict[str, Any] = {
        "model": model,
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if use_search:
        kwargs["tools"] = [{"type": "web_search"}]
    try:
        response = client.responses.create(**kwargs)
    except Exception as exc:
        raise RuntimeError(redact_secrets(str(exc))) from exc
    return response_text(response)
