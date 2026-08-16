# AGENTS.md — symsight

Instructions for agentic development tools working in this repository.

All changes must be owned by the human contributor, who reviews and maintains the code.

## Project overview

**symsight** generates brand-voiced articles and social posts via SpaceXAI / xAI. Config lives in YAML brands; output is markdown drafts under `content/`.

| Path | Role |
|------|------|
| `src/symsight/` | Library (CLI, LLM, brands, TUI; shims over `_py/` or `_native`) |
| `config/brands/` | Brand YAML (ship example only) |
| `tests/` | Pytest (mock the LLM for unit tests) |
| `.github/workflows/` | CI + release (SymWorx-compatible cycle) |

## Branch model (do not invent a different one)

Same as SymWorx:

1. Feature work → **`develop`** (day-to-day CI).
2. Promote with FF **`develop` → `stage`** (no day-to-day CI on `stage`).
3. Cut **`release/vX.Y.Z`**, bump `[workspace.package].version` in `Cargo.toml`, add `## [X.Y.Z]` to `CHANGELOG.md`.
4. PR **`release/*` → `main`**; merge when Release checks are green.
5. **Manually** tag `vX.Y.Z` on `main` (no auto-tag job). Tag runs publish (GitHub Release; PyPI paused).

See [DEVELOPMENT.md](DEVELOPMENT.md).

## Working style

- Prefer incremental, working changes.
- Do not commit secrets (`.env`), personal brand files, or real draft content unless the user asks.
- Keep generation tests mocked; do not call the live API in CI.
- Match existing patterns in `src/symsight/` (Pydantic models, brand YAML, thin CLIs).

## Common commands

```bash
uv sync --extra dev
uv run pytest
SYMSIGHT_IMPL=python uv run pytest   # fallback; needs --extra legacy
uv run ruff check src tests
cargo test --workspace
uv run symsight --help
```
