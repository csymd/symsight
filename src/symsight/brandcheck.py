# Copyright (c) 2026, PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Forbidden-term scanning from active brand config."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from symsight._impl import use_rust

if use_rust():
    from symsight._native import check_path as _check_path
    from symsight._native import check_text as _check_text
    from symsight._native import find_hits as _find_hits
    from symsight._native import iter_scan_files as _iter_scan_files
    from symsight._native import scan_paths as _scan_paths

    def find_hits(text: str, forbidden: list[str]) -> list[str]:
        return list(_find_hits(text, list(forbidden)))

    def check_text(text: str, brand: Any) -> list[str]:
        return list(_check_text(text, brand))

    def check_path(path: Path, brand: Any) -> list[str]:
        return list(_check_path(str(path), brand))

    def iter_scan_files(roots: list[Path]) -> list[Path]:
        return [Path(p) for p in _iter_scan_files([str(r) for r in roots])]

    def scan_paths(roots: list[Path], brand: Any) -> list[tuple[Path, list[str]]]:
        out: list[tuple[Path, list[str]]] = []
        for path, hits in _scan_paths([str(r) for r in roots], brand):
            out.append((Path(path), list(hits)))
        return out
else:
    from symsight._py import brandcheck as _py_brandcheck

    SCAN_EXTENSIONS = _py_brandcheck.SCAN_EXTENSIONS
    SKIP_DIRS = _py_brandcheck.SKIP_DIRS
    check_path = _py_brandcheck.check_path
    check_text = _py_brandcheck.check_text
    find_hits = _py_brandcheck.find_hits
    iter_scan_files = _py_brandcheck.iter_scan_files
    scan_paths = _py_brandcheck.scan_paths
