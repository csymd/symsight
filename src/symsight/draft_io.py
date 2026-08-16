# Copyright (c) 2026, PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Draft markdown read/write with YAML front matter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from symsight._impl import use_rust
from symsight.models import ContentFormat, Draft, DraftMeta

if use_rust():
    from symsight._native import list_drafts as _list_drafts
    from symsight._native import parse_front_matter as _parse_front_matter
    from symsight._native import read_draft as _read_draft
    from symsight._native import render_front_matter as _render_front_matter
    from symsight._native import save_draft_body as _save_draft_body
    from symsight._native import set_status as _set_status
    from symsight._native import strip_disclaimer_from_body as _strip_disclaimer
    from symsight._native import unique_draft_path as _unique_draft_path
    from symsight._native import write_draft_content as _write_draft_content
    from symsight._native import write_new_draft as _write_new_draft

    def parse_front_matter(raw: str) -> tuple[dict[str, Any], str]:
        fm, body = _parse_front_matter(raw)
        return dict(fm), str(body)

    def render_front_matter(front: dict[str, Any]) -> str:
        return str(_render_front_matter(front))

    def strip_disclaimer_from_body(body: str) -> str:
        return str(_strip_disclaimer(body))

    def read_draft(path: Path) -> Draft:
        data = _read_draft(str(path))
        meta = None
        if data.get("meta"):
            meta = DraftMeta.model_validate(data["meta"])
        return Draft(
            path=Path(data["path"]) if data.get("path") else path,
            title=data["title"],
            body=data["body"],
            front_matter=dict(data.get("front_matter") or {}),
            meta=meta,
        )

    def list_drafts(drafts_dir: Path) -> list[Draft]:
        return [read_draft(Path(p)) for p in _list_drafts(str(drafts_dir))]

    def write_draft_content(
        path: Path,
        *,
        front: dict[str, Any],
        body: str,
        disclaimer: str | None = None,
    ) -> None:
        _write_draft_content(str(path), front, body, disclaimer)

    def save_draft_body(path: Path, body: str, *, disclaimer: str | None = None) -> Draft:
        _save_draft_body(str(path), body, disclaimer)
        return read_draft(path)

    def set_status(path: Path, status: str) -> None:
        _set_status(str(path), status)

    def unique_draft_path(drafts_dir: Path, stem: str) -> Path:
        return Path(_unique_draft_path(str(drafts_dir), stem))

    def write_new_draft(
        *,
        drafts_dir: Path,
        title: str,
        body: str,
        brand_id: str,
        brand_display: str,
        type_id: str,
        fmt: ContentFormat,
        topic: str | None,
        disclaimer: str | None,
        meta: DraftMeta,
    ) -> Path:
        fmt_val = fmt.value if hasattr(fmt, "value") else str(fmt)
        return Path(
            _write_new_draft(
                str(drafts_dir),
                title,
                body,
                brand_id,
                brand_display,
                type_id,
                fmt_val,
                meta,
                topic,
                disclaimer,
            )
        )
else:
    from symsight._py import draft_io as _py_draft_io

    list_drafts = _py_draft_io.list_drafts
    parse_front_matter = _py_draft_io.parse_front_matter
    read_draft = _py_draft_io.read_draft
    render_front_matter = _py_draft_io.render_front_matter
    save_draft_body = _py_draft_io.save_draft_body
    set_status = _py_draft_io.set_status
    strip_disclaimer_from_body = _py_draft_io.strip_disclaimer_from_body
    unique_draft_path = _py_draft_io.unique_draft_path
    write_draft_content = _py_draft_io.write_draft_content
    write_new_draft = _py_draft_io.write_new_draft
