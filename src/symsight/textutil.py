# Copyright (c) 2026, PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Text helpers: counting, slugify, title/body extraction from model output."""

from __future__ import annotations

from symsight._impl import use_rust

if use_rust():
    from symsight._native import (  # type: ignore[import-not-found]
        char_count,
        clean_body,
        extract_social_text,
        extract_title_body,
        is_plausible_title,
        slugify,
        word_count,
    )
else:
    from symsight._py import textutil as _py_textutil

    char_count = _py_textutil.char_count
    clean_body = _py_textutil.clean_body
    extract_social_text = _py_textutil.extract_social_text
    extract_title_body = _py_textutil.extract_title_body
    is_plausible_title = _py_textutil.is_plausible_title
    slugify = _py_textutil.slugify
    word_count = _py_textutil.word_count

__all__ = [
    "char_count",
    "clean_body",
    "extract_social_text",
    "extract_title_body",
    "is_plausible_title",
    "slugify",
    "word_count",
]
