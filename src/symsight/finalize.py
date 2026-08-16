# Copyright (c) 2026, PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Promote drafts to the final directory (move or copy markdown only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from symsight._impl import use_rust

if use_rust():
    from symsight._native import FinalizeError
    from symsight._native import finalize_draft as _finalize_draft
    from symsight._native import list_final as _list_final

    def finalize_draft(
        draft_path: Path,
        *,
        final_dir: Path,
        brand: Any | None = None,
        copy: bool = False,
    ) -> Path:
        return Path(_finalize_draft(str(draft_path), str(final_dir), brand, copy))

    def list_final(final_dir: Path) -> list[Path]:
        return [Path(p) for p in _list_final(str(final_dir))]
else:
    from symsight._py import finalize as _py_finalize

    FinalizeError = _py_finalize.FinalizeError
    finalize_draft = _py_finalize.finalize_draft
    list_final = _py_finalize.list_final
