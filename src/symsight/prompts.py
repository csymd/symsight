# Copyright (c) 2026 PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Build system and user prompts from brand + format."""

from __future__ import annotations

from string import Formatter

from symsight.models import ContentFormat, GenerateRequest


def _safe_format(template: str, **kwargs: object) -> str:
    """Format template allowing missing keys to stay as placeholders."""
    keys = {fname for _, fname, _, _ in Formatter().parse(template) if fname}
    try:
        return template.format(**{k: kwargs.get(k, "{" + k + "}") for k in keys})
    except (KeyError, ValueError):
        return template


def system_prompt(req: GenerateRequest) -> str:
    brand = req.brand
    name = brand.full_name

    if req.format == ContentFormat.SOCIAL:
        max_chars = req.resolved_max_chars()
        return f"""You are a writer for {name}.
Voice: {brand.voice.strip()}

Hard rules:
- When naming the organization or byline, use "{name}" exactly if you name it.
- Do not invent credentials, team bios, or regulatory registrations.
- Output a single social post of at most {max_chars} characters.
- Do NOT narrate your process, planning, tool use, or revisions.
- Do NOT include markdown citation markers or footnotes.
- Do NOT output a TITLE line or preamble. Output ONLY the post text.

Output format — the entire response must be ONLY the post text, nothing else.
"""

    min_w = req.resolved_min_words()
    max_w = req.resolved_max_words()
    return f"""You are a writer for {name}.
Voice: {brand.voice.strip()}

Hard rules:
- Always refer to the organization as "{name}" when naming it. Never misspell or alter the name.
- Educational content only unless the brand voice says otherwise. No personalized recommendations.
- Do not invent credentials, AUM, team bios, or regulatory registrations.
- Body length: {min_w}–{max_w} words (title excluded).
- Prefer accurate information. For time-sensitive topics use search; if data is thin, say so—do not invent figures.
- Do NOT narrate your process, planning, tool use, or revisions. Do NOT include footnotes, citation markers,
  or markdown links like [[1]](url) or [1](url). Weave facts into prose only.
- Do NOT output anything before the TITLE line (no preamble).

Output format — the entire response must be ONLY these three parts, nothing else:

TITLE: <short one-line title, max ~80 characters>
---
<body as markdown paragraphs only; no H1; no second TITLE line; no trailing disclaimer>
"""


def user_prompt(req: GenerateRequest, today: str) -> str:
    type_spec = req.resolved_type()
    topic = req.topic or "a useful topic for the intended audience"
    kwargs = {
        "today": today,
        "topic": topic,
        "min_words": req.resolved_min_words(),
        "max_words": req.resolved_max_words(),
        "max_chars": req.resolved_max_chars(),
        "full_name": req.brand.full_name,
        "short_name": req.brand.short_name,
        "display_name": req.brand.display_name,
    }
    base = _safe_format(type_spec.user_template, **kwargs)

    if (
        req.format == ContentFormat.SOCIAL
        and "character" not in base.lower()
        and "max_chars" not in type_spec.user_template
    ):
        base = (
            f"{base.rstrip()}\n"
            f"Hard limit: at most {req.resolved_max_chars()} characters. "
            "Output ONLY the post text."
        )
    return base


def length_rewrite_prompt(
    req: GenerateRequest,
    *,
    title: str,
    body: str,
    current_count: int,
) -> str:
    if req.format == ContentFormat.SOCIAL:
        max_c = req.resolved_max_chars()
        return (
            f"Rewrite the social post below to at most {max_c} characters. "
            "Output ONLY the post text with no preamble, no quotes, no title.\n\n"
            f"Current character count: {current_count}.\n\n"
            f"{body}"
        )
    min_w = req.resolved_min_words()
    max_w = req.resolved_max_words()
    return (
        f"Rewrite the essay below to {min_w}–{max_w} words. "
        "Output ONLY this format with no preamble, no citations, no process notes:\n"
        "TITLE: <short title>\n---\n<body>\n\n"
        f"Current word count: {current_count}.\n\n"
        f"TITLE: {title}\n---\n{body}"
    )
