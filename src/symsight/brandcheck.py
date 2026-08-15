# Copyright (c) 2026, PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Forbidden-term scanning from active brand config."""

from __future__ import annotations

from pathlib import Path

from symsight.models import Brand

SCAN_EXTENSIONS = {
    ".html",
    ".md",
    ".css",
    ".js",
    ".json",
    ".txt",
    ".svg",
    ".py",
    ".yml",
    ".yaml",
    ".toml",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".grok",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    "target",
    "dist",
}


def find_hits(text: str, forbidden: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in forbidden if term.lower() in lower]


def check_text(text: str, brand: Brand) -> list[str]:
    return find_hits(text, brand.forbidden)


def check_path(path: Path, brand: Brand) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    return check_text(text, brand)


def iter_scan_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        root = root.resolve()
        if root.is_file():
            files.append(root)
            continue
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix.lower() not in SCAN_EXTENSIONS and path.name not in {
                "README",
                "README.md",
            }:
                continue
            files.append(path)
    return sorted(set(files))


def scan_paths(roots: list[Path], brand: Brand) -> list[tuple[Path, list[str]]]:
    problems: list[tuple[Path, list[str]]] = []
    for path in iter_scan_files(roots):
        hits = check_path(path, brand)
        if hits:
            problems.append((path, sorted(set(hits))))
    return problems
