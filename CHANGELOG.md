# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

## [0.1.0] - 2026-08-16

### Added

- Initial release of **symsight**: brand-driven articles and social posts from YAML brand files
- CLI (`generate`, `finalize`, `check`, `brands`, `tui`) and Textual TUI
- Rust domain core (`symsight-core`) with Python bindings (`symsight._native` via PyO3 / maturin)
- Native clap binary (`cargo run -p symsight-cli`); GitHub Release also ships `symsight-v*-x86_64-unknown-linux-gnu`
- GitHub Release artifacts: manylinux wheel + sdist (PyPI publish remains paused)
- Example brand, mini-project workspace, `SECURITY.md`, `CODE_OF_CONDUCT.md`, and `NOTICE.md`

### Changed

- Default implementation is Rust; `SYMSIGHT_IMPL=python` is a one-release fallback (`uv sync --extra legacy`)
- Package version is sourced from the Cargo workspace (`pyproject.toml` is `dynamic = ["version"]`)
- Brandcheck skip dirs include `target` and `dist` so Cargo / pack artifacts are not scanned

### Notes

- `SymSight` remains in active development under a beta tag until the API is deemed stable.
- Generation tests stay mocked; CI does not call the live xAI API.

---

## Version Links

[Unreleased]: https://github.com/csymd/symsight/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/csymd/symsight/releases/tag/v0.1.0
