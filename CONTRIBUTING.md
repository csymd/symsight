# Contributing to symsight

Thanks for contributing.

## Philosophy

Symsight keeps generation **brand-driven** (YAML), **reproducible** (`uv`), and **local-first** for drafts. Prefer small, testable changes over large rewrites.

## AI-assisted contributions

AI tools are fine. You remain responsible for the result: explain the change, keep quality high, and own the code after merge.

## Getting started

1. Fork/clone the repository.
2. Set up the environment (see [DEVELOPMENT.md](DEVELOPMENT.md)).
3. Branch from **`develop`** (`git checkout -b feature/your-feature-name`).
4. Make changes; run `uv run pytest` and `uv run ruff check src tests`.
5. Open a PR into **`develop`** (day-to-day work) unless you are preparing a release.

## Pull requests

- Keep PRs focused (one logical change when practical).
- Include tests when adding or changing behavior.
- Update docs / `CHANGELOG.md` under **Unreleased** when user-visible.
- Stay engaged with review comments.

## Release path

Do **not** open feature PRs straight to `main`. Releases follow the same cycle as SymWorx:

`develop` → `stage` (FF) → `release/vX.Y.Z` → PR to `main` → merge → **manual** tag `vX.Y.Z`

Details: [DEVELOPMENT.md](DEVELOPMENT.md#branch-model).

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).  
To report a security issue, see [SECURITY.md](SECURITY.md) (not public issues).
