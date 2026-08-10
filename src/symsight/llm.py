# Copyright (c) 2026 PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""xAI / SpaceXAI client helpers."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from symsight.config import DEFAULT_BASE_URL


def make_client(*, api_key: str, base_url: str = DEFAULT_BASE_URL) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=base_url)


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
    client: OpenAI,
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
    response = client.responses.create(**kwargs)
    return response_text(response)
