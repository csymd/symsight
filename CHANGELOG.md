# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

- Rust `symsight-core` AppConfig merge and prompt builders with Python snapshots
- Rust `symsight-core` draft I/O, finalize, and brandcheck with front-matter goldens
- Rust `symsight-core` textutil port with committed golden vectors shared by pytest
- Rust `symsight-core` Brand models and YAML loader with fixture parity tests
- Cargo workspace scaffold (`crates/symsight-core`) and Rust fmt/clippy/test CI job
- Root `SECURITY.md` and `CODE_OF_CONDUCT.md`
- `examples/` sample business brand, mini-project workspace, and static draft shapes
- `NOTICE.md` with PalEm Dynamics LLC attribution

### Changed

- Brandcheck skip dirs include `target` and `dist` so Cargo / pack artifacts are not scanned
- File headers and `LICENSE` appendix use `Copyright (c) 2026, PalEm Dynamics LLC`

### Fixed

- Package metadata URLs and Apache-2.0 license fields for public GitHub / PyPI

## [0.1.0] - 2026-MM-DD

### Added

- Initial release of **symsight**: brand-driven insight generator for articles and social posts

### Notes

- `SymSight` will remain in active development under a beta tag until the API has been deemed stable. 

---

## Version Links

[Unreleased]: https://github.com/bitterbeta/symsight/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/bitterbeta/symsight/releases/tag/v0.1.0
