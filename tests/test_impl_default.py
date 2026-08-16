# Copyright (c) 2026, PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Default implementation is Rust unless SYMSIGHT_IMPL overrides it."""

from __future__ import annotations

import os

import pytest

from symsight._impl import impl_name, use_rust


def test_default_impl_is_rust() -> None:
    if os.environ.get("SYMSIGHT_IMPL"):
        pytest.skip("SYMSIGHT_IMPL is set")
    assert impl_name() == "rust"
    assert use_rust() is True


def test_explicit_python_fallback() -> None:
    if os.environ.get("SYMSIGHT_IMPL", "").strip().lower() not in {"python", "py", "legacy"}:
        pytest.skip("not running the Python fallback job")
    assert use_rust() is False
