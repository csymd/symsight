# Copyright (c) 2026, PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Promote drafts to the final directory (move or copy markdown only)."""

from __future__ import annotations

import shutil
from pathlib import Path

from symsight.brandcheck import check_text
from symsight.draft_io import set_status
from symsight.models import Brand


class FinalizeError(Exception):
    """Finalize failure."""


def finalize_draft(
    draft_path: Path,
    *,
    final_dir: Path,
    brand: Brand | None = None,
    copy: bool = False,
) -> Path:
    """Move or copy draft markdown (+ meta.json) into final_dir; set status final."""
    draft_path = draft_path.resolve()
    if not draft_path.is_file():
        raise FinalizeError(f"Draft not found: {draft_path}")

    raw = draft_path.read_text(encoding="utf-8")
    if brand is not None:
        hits = check_text(raw, brand)
        if hits:
            raise FinalizeError(
                f"Brand check failed on draft ({', '.join(hits)}). Fix before finalizing."
            )

    final_dir.mkdir(parents=True, exist_ok=True)
    dest = final_dir / draft_path.name
    if dest.exists() and dest.resolve() != draft_path.resolve():
        raise FinalizeError(f"Destination already exists: {dest}")

    set_status(draft_path, "final")

    meta_src = draft_path.with_suffix(".meta.json")
    meta_dest = dest.with_suffix(".meta.json")

    if copy:
        shutil.copy2(draft_path, dest)
        if meta_src.is_file():
            shutil.copy2(meta_src, meta_dest)
        # leave original as final status too (already set)
    else:
        if dest.resolve() == draft_path.resolve():
            # already in final dir
            return dest
        shutil.move(str(draft_path), str(dest))
        if meta_src.is_file():
            shutil.move(str(meta_src), str(meta_dest))

    return dest.resolve()


def list_final(final_dir: Path) -> list[Path]:
    if not final_dir.is_dir():
        return []
    return sorted(final_dir.glob("*.md"), reverse=True)
