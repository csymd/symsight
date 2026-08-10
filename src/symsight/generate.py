# Copyright (c) 2026 PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Generation orchestration: prompt → LLM → validate → write draft."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

from symsight.brandcheck import check_text
from symsight.config import AppConfig
from symsight.draft_io import write_new_draft
from symsight.llm import create_completion, make_client
from symsight.models import ContentFormat, DraftMeta, GenerateRequest
from symsight.prompts import length_rewrite_prompt, system_prompt, user_prompt
from symsight.textutil import (
    char_count,
    extract_social_text,
    extract_title_body,
    is_plausible_title,
    word_count,
)


class GenerateError(Exception):
    """Generation failure."""


def generate_content(
    req: GenerateRequest,
    cfg: AppConfig,
    *,
    client: object | None = None,
) -> tuple[str, str, DraftMeta]:
    """Return (title, body, meta). Does not write files."""
    api_key = cfg.require_api_key()
    model = req.model or cfg.model
    llm = client or make_client(api_key=api_key, base_url=cfg.base_url)
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    use_search = req.resolved_use_search()

    sys_p = system_prompt(req)
    usr_p = user_prompt(req, today)

    raw = create_completion(
        llm,  # type: ignore[arg-type]
        model=model,
        system=sys_p,
        user=usr_p,
        use_search=use_search,
    )
    if not raw.strip():
        raise GenerateError("Empty response from model")

    if req.format == ContentFormat.SOCIAL:
        title, body, meta = _finish_social(req, cfg, llm, model, raw, use_search, today)
    else:
        title, body, meta = _finish_article(req, cfg, llm, model, raw, use_search, today)

    hits = check_text(title + "\n" + body, req.brand)
    if hits:
        raise GenerateError(
            f"Generated text contains forbidden brand variant(s): {hits}. Re-run generation."
        )
    return title, body, meta


def _finish_article(
    req: GenerateRequest,
    cfg: AppConfig,
    llm: object,
    model: str,
    raw: str,
    use_search: bool,
    today: str,
) -> tuple[str, str, DraftMeta]:
    title, body = extract_title_body(raw)
    wc = word_count(body)
    min_w = req.resolved_min_words()
    max_w = req.resolved_max_words()

    if wc < min_w or wc > max_w or not is_plausible_title(title):
        adjust = length_rewrite_prompt(req, title=title, body=body, current_count=wc)
        raw2 = create_completion(
            llm,  # type: ignore[arg-type]
            model=model,
            system=system_prompt(req),
            user=adjust,
            use_search=False,
        )
        if raw2.strip():
            title, body = extract_title_body(raw2)
            wc = word_count(body)

    if not is_plausible_title(title):
        fallback = req.topic or req.type_id.replace("-", " ").title()
        title = fallback.strip().title()[:80]
        print(
            f"Warning: model title looked like process chatter; using fallback: {title!r}",
            file=sys.stderr,
        )

    if wc < min_w or wc > max_w:
        print(
            f"Warning: word count {wc} outside {min_w}–{max_w}. Edit the draft before finalizing.",
            file=sys.stderr,
        )

    meta = DraftMeta(
        model=model,
        type=req.type_id,
        format=ContentFormat.ARTICLE.value,
        topic=req.topic,
        brand_id=req.brand.id,
        used_web_search=use_search,
        word_count=wc,
        generated_at=datetime.now(UTC).isoformat(),
    )
    return title, body, meta


def _finish_social(
    req: GenerateRequest,
    cfg: AppConfig,
    llm: object,
    model: str,
    raw: str,
    use_search: bool,
    today: str,
) -> tuple[str, str, DraftMeta]:
    body = extract_social_text(raw)
    cc = char_count(body)
    max_c = req.resolved_max_chars()

    if cc > max_c:
        adjust = length_rewrite_prompt(req, title="", body=body, current_count=cc)
        raw2 = create_completion(
            llm,  # type: ignore[arg-type]
            model=model,
            system=system_prompt(req),
            user=adjust,
            use_search=False,
        )
        if raw2.strip():
            body = extract_social_text(raw2)
            cc = char_count(body)

    if cc > max_c:
        print(
            f"Warning: character count {cc} exceeds {max_c}. Edit the draft before finalizing.",
            file=sys.stderr,
        )

    # Title for filename / front matter: first ~60 chars of body
    title = body.strip().split("\n")[0][:80] or "social-post"

    meta = DraftMeta(
        model=model,
        type=req.type_id,
        format=ContentFormat.SOCIAL.value,
        topic=req.topic,
        brand_id=req.brand.id,
        used_web_search=use_search,
        char_count=cc,
        generated_at=datetime.now(UTC).isoformat(),
    )
    return title, body, meta


def generate_and_write(
    req: GenerateRequest,
    cfg: AppConfig,
    *,
    drafts_dir: Path | None = None,
    client: object | None = None,
) -> Path:
    title, body, meta = generate_content(req, cfg, client=client)
    out_dir = drafts_dir or cfg.drafts_dir
    disclaimer = req.brand.disclaimer.strip() or None
    path = write_new_draft(
        drafts_dir=out_dir,
        title=title,
        body=body,
        brand_id=req.brand.id,
        brand_display=req.brand.display_name,
        type_id=req.type_id,
        fmt=req.format,
        topic=req.topic,
        disclaimer=disclaimer,
        meta=meta,
    )
    return path
