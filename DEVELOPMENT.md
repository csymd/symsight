# Development

How to build, test, and release **symsight**.

Branch model and release gates mirror [SymWorx](https://github.com/symworx/symworx) so both projects use the same muscle memory.

For agent/tooling guidelines, see [AGENTS.md](AGENTS.md). Contributors own all submitted code.

## Prerequisites

- Python 3.11+ (3.12 recommended; CI matrix is 3.11 + 3.12)
- [uv](https://docs.astral.sh/uv/)
- A SpaceXAI / xAI API key for live generation (`XAI_API_KEY`)
- Rust 1.82+ (stable) with `rustfmt` and `clippy` — required for the Cargo workspace and the Rust CI job. The user-facing CLI is still Python (`uv run symsight`). `rust-toolchain.toml` pins `stable` and the extra components.

## Common commands

```bash
# Install (runtime)
uv sync

# Install with lint/test tools
uv sync --extra dev

# Tests
uv run pytest

# Lint
uv run ruff check src tests

# Optional typecheck
uv run mypy src

# Rust workspace (fmt, clippy, tests)
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace

# Optional native CLI (Python remains the default via uv)
cargo run -p symsight-cli -- brands
cargo run -p symsight-cli -- check
cargo run -p symsight-cli -- tui   # prints a hint; use uv run symsight tui

# CLI / TUI
uv run symsight brands
uv run symsight generate --brand example-writer --type general --topic "deep work"
uv run symsight tui
```

Config:

```bash
cp .env.example .env
# optional: cp config/.symsight.toml.example .symsight.toml
```

## Code style

- Run `uv run ruff check src tests` before committing.
- For Rust changes, also run `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`, and `cargo test --workspace`.
- Keep changes focused; one logical change per PR is preferred.
- Generation tests that hit the network should stay mocked (see `tests/test_generate_mocked.py`).
- Text helpers are locked by `tests/golden/*.json` (consumed by both `cargo test` and pytest). Regenerate only with `uv run python scripts/export_goldens.py` when you intend to change the Python contract — not after `textutil` becomes a Rust shim.

## Project layout

| Path | Role |
|------|------|
| `src/symsight/` | Library (CLI, generate, brands, TUI) |
| `crates/symsight-core/` | Rust domain crate (Python is still the user-facing implementation) |
| `crates/symsight-cli/` | Optional clap binary (`cargo run -p symsight-cli`); flags match `uv run symsight` |
| `config/brands/` | Brand YAML (example only in-repo) |
| `content/drafts/`, `content/final/` | Local drafts (usually not released) |
| `scripts/` | Thin entrypoints wrapping the library |
| `tests/` | Pytest suite |

The Python package version is `[project].version` in `pyproject.toml`. The Cargo workspace version in the root `Cargo.toml` must stay equal to it until the later maturin cutover. Release-meta still reads `pyproject.toml` only.

## Branch model

Same as SymWorx:

```
feature/* ──► develop ──► stage ──► release/vX.Y.Z ──► main ──► tag vX.Y.Z
                 │           │              │             │
              day-to-day   FF only     release prep    publish
                 CI        (no CI)     + validation    on tag
```

1. **Feature development** → merge to `develop`  
   Day-to-day CI (ruff + pytest + Rust fmt/clippy/test) runs on push/PR to `develop` and `main`.

2. **Stage / early access** → fast-forward `develop` → `stage` when you want a promotion point.  
   Day-to-day CI does **not** run on `stage` (avoids double runs on FF). Pre-release tags (e.g. `v0.2.0-beta.1`) may be cut from here if needed.

3. **Release preparation**
   - Create `release/vX.Y.Z` from `stage` (or from `develop` if stage is not updated yet).
   - Bump `version` in `pyproject.toml`.
   - Update `CHANGELOG.md` with a `## [X.Y.Z]` section (required by release metadata).
   - Open a PR from `release/vX.Y.Z` → `main`.

4. **Release**
   - Merge the PR to `main` when **Release** checks are green.
   - **Manually** create and push the annotated tag `vX.Y.Z` on the merge commit (tags are not auto-created in CI).
   - Tag push runs [`.github/workflows/release.yml`](.github/workflows/release.yml): full validation, then **GitHub Release** with sdist + wheel. **PyPI is paused** until `publish-pypi` is re-enabled.

### Example first cut (`v0.1.0`)

```bash
# After the project lands on develop and is promoted:
git checkout stage   # or develop if stage lags
git pull
git checkout -b release/v0.1.0

# Ensure pyproject.toml version is 0.1.0 and CHANGELOG has ## [0.1.0]
# open PR → main, merge when green

git checkout main && git pull
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

### Versioning

- Semantic Versioning (SemVer).
- Pre-releases (e.g. `0.2.0-beta.1`, `0.2.0-rc.1`) may be tagged from `stage` or a release branch; mark them as prerelease in GitHub (`-` in the version).
- Final releases are cut from `release/vX.Y.Z` merged into `main`, then **manually** tagged.

## CI / release automation

| Workflow | Triggers | What it does |
|----------|----------|--------------|
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | push/PR → `develop`, `main` | Ruff + pytest (3.11, 3.12) + Rust fmt/clippy/test |
| [`.github/workflows/release.yml`](.github/workflows/release.yml) | PR → `main`; push `main` / `release/**` / tags `v*`; dispatch | Version + CHANGELOG gates, ruff, pytest, `uv build`; **publish** only on tags |

Release metadata enforces:

- `release/vX.Y.Z` branch name matches `pyproject.toml` version.
- Tag `vX.Y.Z` matches `pyproject.toml` version.
- `CHANGELOG.md` contains `## [X.Y.Z]` for tags and `release/*` branches.

## Bootstrap remote branches (once)

If the remote only has `main` so far:

```bash
git checkout main
git pull
git checkout -b develop
git push -u origin develop
git checkout -b stage
git push -u origin stage
# optional: set default branch to develop in GitHub settings
```

## Related

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
