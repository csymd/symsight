# Copyright (c) 2026, PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""xAI / SpaceXAI client helpers."""

from __future__ import annotations

from typing import Any

from symsight._impl import use_rust

if use_rust():
    from symsight._native import make_client as _make_client
    from symsight._native import response_text as _response_text

    def make_client(*, api_key: str, base_url: str | None = None) -> Any:
        return _make_client(api_key, base_url)

    def response_text(response: object) -> str:
        return str(_response_text(response))

    def create_completion(*args: Any, **kwargs: Any) -> str:
        raise RuntimeError(
            "create_completion is not used on the Rust path; generate() talks to LlmClient directly"
        )
else:
    from symsight._py import llm as _py_llm

    create_completion = _py_llm.create_completion
    make_client = _py_llm.make_client
    response_text = _py_llm.response_text
