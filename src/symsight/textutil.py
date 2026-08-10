# Copyright (c) 2026 PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Text helpers: counting, slugify, title/body extraction from model output."""

from __future__ import annotations

import re

_BAD_TITLE_HINTS = re.compile(
    r"(?i)\b("
    r"i am revising|i will |i need |let me |here'?s |okay[,.]|sure[,.]|"
    r"verify |searching|tool call|web_search|as an ai|revising the essay|"
    r"preserving the required|format and voice"
    r")\b"
)
_CITATION_MD = re.compile(r"\[\[\d+\]\]\([^)]+\)")
_CITATION_SIMPLE = re.compile(r"\[(\d+)\]\((https?://[^)]+)\)")
_BARE_FOOTNOTE = re.compile(r"\[\[[\d]+\]\]")


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def char_count(text: str) -> int:
    return len(text)


def slugify(text: str, max_len: int = 60) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:max_len] or "insight"


def clean_body(body: str) -> str:
    """Strip citation junk and stray separators from model body text."""
    text = body.strip()
    while text.startswith("---"):
        text = text[3:].lstrip("\n\r- ").lstrip()
    text = _CITATION_MD.sub("", text)
    text = _CITATION_SIMPLE.sub("", text)
    text = _BARE_FOOTNOTE.sub("", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" +\.", ".", text)
    return text.strip()


def is_plausible_title(title: str) -> bool:
    t = title.strip()
    if not t or len(t) > 120:
        return False
    if "http://" in t or "https://" in t or "[[" in t:
        return False
    if _BAD_TITLE_HINTS.search(t):
        return False
    return not (t.count(".") >= 2 and len(t) > 80)


def extract_title_body(raw: str) -> tuple[str, str]:
    """Parse TITLE/body even when the model dumps preamble or multiple TITLE lines."""
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:\w+)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()

    title_hits = list(re.finditer(r"(?im)^TITLE:\s*(.+)$", text))
    if not title_hits:
        title_hits = list(re.finditer(r"(?i)\bTITLE:\s*(.+?)(?=\n|$)", text))

    title: str | None = None
    body_start = 0

    if title_hits:
        chosen = title_hits[-1]
        for hit in reversed(title_hits):
            candidate = hit.group(1).strip()
            if "TITLE:" in candidate.upper():
                parts = re.split(r"(?i)\bTITLE:\s*", candidate)
                candidate = parts[-1].strip()
            if is_plausible_title(candidate):
                chosen = hit
                title = candidate
                break
        if title is None:
            candidate = chosen.group(1).strip()
            if "TITLE:" in candidate.upper():
                candidate = re.split(r"(?i)\bTITLE:\s*", candidate)[-1].strip()
            candidate = re.split(r"\[\[|\s{2,}", candidate)[0].strip()
            title = candidate[:120].strip() or "Untitled insight"
        body_start = chosen.end()

    rest = text[body_start:].lstrip() if title else text
    sep = re.match(r"^-{3,}\s*\n?", rest)
    if sep:
        rest = rest[sep.end() :]
    body = clean_body(rest)

    if not title:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if not lines:
            raise ValueError("Could not parse TITLE/body from model output")
        first = re.sub(r"^#+\s*", "", lines[0]).strip()
        title = first if is_plausible_title(first) else "Untitled insight"
        body = clean_body("\n".join(lines[1:] if is_plausible_title(first) else lines))

    title = re.sub(r"\s+", " ", title).strip().strip('"').strip("'")
    if not body:
        raise ValueError("Parsed empty body from model output")
    return title, body


def extract_social_text(raw: str) -> str:
    """Extract a single social post from model output (strip fences/preamble)."""
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:\w+)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
    # Drop common preambles
    text = re.sub(r"(?is)^(here(?:'s| is).*?:\s*)", "", text)
    text = clean_body(text)
    # Prefer first non-empty paragraph if multi-paragraph dump
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if paras:
        # If first looks like a title line, skip when there is more
        if len(paras) > 1 and paras[0].upper().startswith("TITLE:"):
            return paras[1].strip()
        return paras[0].strip()
    if not text:
        raise ValueError("Empty social text from model output")
    return text
