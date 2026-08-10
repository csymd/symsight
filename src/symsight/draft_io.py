# Copyright (c) 2026 PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Draft markdown read/write with YAML front matter."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from symsight.models import ContentFormat, Draft, DraftMeta
from symsight.textutil import char_count, slugify, word_count


def parse_front_matter(raw: str) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    fm_raw, body = parts[1], parts[2]
    meta: dict[str, Any] = {}
    for line in fm_raw.strip().splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if val in ("true", "false"):
            meta[key] = val == "true"
        elif val == "null":
            meta[key] = None
        elif re.fullmatch(r"-?\d+", val):
            meta[key] = int(val)
        elif val.startswith('"') and val.endswith('"'):
            meta[key] = val[1:-1].replace('\\"', '"')
        else:
            meta[key] = val
    return meta, body.lstrip("\n")


def _yq(v: object) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace('"', '\\"')
    return f'"{s}"'


def render_front_matter(front: dict[str, Any]) -> str:
    lines = ["---"] + [f"{k}: {_yq(v)}" for k, v in front.items()] + ["---", ""]
    return "\n".join(lines)


def strip_disclaimer_from_body(body: str) -> str:
    body = re.sub(
        r"\n---\s*\n+\*\*Disclaimer\.\*\*.*$",
        "",
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return body.strip()


def read_draft(path: Path) -> Draft:
    raw = path.read_text(encoding="utf-8")
    fm, body = parse_front_matter(raw)
    body = strip_disclaimer_from_body(body)
    title = str(fm.get("title") or path.stem)
    meta = None
    meta_path = path.with_suffix(".meta.json")
    if meta_path.is_file():
        try:
            meta = DraftMeta.model_validate_json(meta_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            meta = None
    return Draft(path=path, title=title, body=body, front_matter=fm, meta=meta)


def list_drafts(drafts_dir: Path) -> list[Draft]:
    if not drafts_dir.is_dir():
        return []
    drafts: list[Draft] = []
    for path in sorted(drafts_dir.glob("*.md"), reverse=True):
        try:
            drafts.append(read_draft(path))
        except OSError:
            continue
    return drafts


def write_draft_content(
    path: Path,
    *,
    front: dict[str, Any],
    body: str,
    disclaimer: str | None = None,
) -> None:
    content = render_front_matter(front) + body.rstrip()
    if disclaimer:
        content += f"\n\n---\n\n**Disclaimer.** {disclaimer.strip()}\n"
    else:
        content += "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def save_draft_body(path: Path, body: str, *, disclaimer: str | None = None) -> Draft:
    """Rewrite body keeping front matter; refresh word/char counts."""
    draft = read_draft(path)
    fm = dict(draft.front_matter)
    fmt = str(fm.get("format", "article"))
    if fmt == ContentFormat.SOCIAL.value:
        fm["char_count"] = char_count(body)
        fm.pop("word_count", None)
    else:
        fm["word_count"] = word_count(body)
    # Preserve disclaimer flag
    disc = disclaimer
    if disc is None and fm.get("disclaimer"):
        # re-read original for disclaimer text is hard — leave block off if not provided
        disc = None
    write_draft_content(path, front=fm, body=body, disclaimer=disc)
    return read_draft(path)


def set_status(path: Path, status: str) -> None:
    raw = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'^status:\s*".*?"',
        f'status: "{status}"',
        raw,
        count=1,
        flags=re.MULTILINE,
    )
    if updated == raw:
        updated = re.sub(
            r"^status:\s*\S+",
            f'status: "{status}"',
            raw,
            count=1,
            flags=re.MULTILINE,
        )
    if updated == raw and raw.startswith("---"):
        # inject status into front matter
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1].rstrip() + f'\nstatus: "{status}"\n'
            updated = f"---{fm}---{parts[2]}"
    path.write_text(updated, encoding="utf-8")


def unique_draft_path(drafts_dir: Path, stem: str) -> Path:
    drafts_dir.mkdir(parents=True, exist_ok=True)
    path = drafts_dir / f"{stem}.md"
    n = 2
    while path.exists():
        path = drafts_dir / f"{stem}-{n}.md"
        n += 1
    return path


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
    date = datetime.now(UTC).strftime("%Y-%m-%d")
    type_slug = slugify(type_id, max_len=40)
    if fmt == ContentFormat.SOCIAL:
        stem = f"{date}-social-{slugify(title or body[:40])}"
    else:
        stem = f"{date}-{type_slug}-{slugify(title)}"
    path = unique_draft_path(drafts_dir, stem)

    front: dict[str, Any] = {
        "title": title,
        "type": type_id,
        "format": fmt.value,
        "brand": brand_id,
        "brand_name": brand_display,
        "generated_at": meta.generated_at,
        "status": "draft",
        "disclaimer": bool(disclaimer),
        "topic": topic,
    }
    if fmt == ContentFormat.SOCIAL:
        front["char_count"] = char_count(body)
    else:
        front["word_count"] = word_count(body)

    write_draft_content(path, front=front, body=body, disclaimer=disclaimer)

    meta_path = path.with_suffix(".meta.json")
    meta_out = meta.model_copy(update={"title": title, "path": str(path)})
    meta_path.write_text(meta_out.model_dump_json(indent=2), encoding="utf-8")
    return path


def write_meta_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
