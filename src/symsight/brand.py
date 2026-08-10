# Copyright (c) 2026 PalEm Dynamics LLC
# Licensed under the Apache License, Version 2.0.
"""Load and resolve brand YAML configs."""

from __future__ import annotations

from pathlib import Path

import yaml

from symsight.models import Brand


class BrandError(Exception):
    """Brand load / resolve failure."""


def load_brand_file(path: Path) -> Brand:
    """Load a single brand YAML file."""
    if not path.is_file():
        raise BrandError(f"Brand file not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise BrandError(f"Brand file must be a mapping: {path}")
    # Allow id from filename if missing
    if "id" not in raw:
        raw["id"] = path.stem
    try:
        return Brand.model_validate(raw)
    except Exception as exc:
        raise BrandError(f"Invalid brand file {path}: {exc}") from exc


def list_brand_files(brands_dir: Path) -> list[Path]:
    if not brands_dir.is_dir():
        return []
    return sorted(brands_dir.glob("*.yaml")) + sorted(
        p for p in brands_dir.glob("*.yml") if p not in brands_dir.glob("*.yaml")
    )


def list_brands(brands_dir: Path) -> list[Brand]:
    brands: list[Brand] = []
    for path in list_brand_files(brands_dir):
        try:
            brands.append(load_brand_file(path))
        except BrandError:
            continue
    return brands


def resolve_brand(
    *,
    brands_dir: Path,
    brand_id: str | None = None,
    brand_path: Path | None = None,
) -> Brand:
    """Resolve brand by path or id under brands_dir."""
    if brand_path is not None:
        return load_brand_file(Path(brand_path))

    if not brand_id:
        raise BrandError("No brand specified (set active_brand, --brand, or --brand-file)")

    # Exact file stem match
    for ext in (".yaml", ".yml"):
        candidate = brands_dir / f"{brand_id}{ext}"
        if candidate.is_file():
            return load_brand_file(candidate)

    # Match by id field inside files
    for path in list_brand_files(brands_dir):
        brand = load_brand_file(path)
        if brand.id == brand_id:
            return brand

    known = [p.stem for p in list_brand_files(brands_dir)]
    raise BrandError(
        f"Brand {brand_id!r} not found in {brands_dir}. "
        f"Available: {', '.join(known) or '(none)'}"
    )
