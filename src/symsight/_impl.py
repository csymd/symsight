# Copyright (c) 2026, PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.

"""Select the Python or Rust domain implementation."""

from __future__ import annotations

import os


def impl_name() -> str:
    return os.environ.get("SYMSIGHT_IMPL", "python").strip().lower()


def use_rust() -> bool:
    return impl_name() in {"rust", "native"}
