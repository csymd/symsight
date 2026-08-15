# Golden vectors

Compatibility contract for `symsight.textutil` and the Rust `symsight-core` port.

Generated from the current Python implementation:

```bash
uv run python scripts/export_goldens.py
```

Do **not** regenerate after `src/symsight/textutil.py` becomes a shim over Rust
unless you are intentionally changing the contract. `cargo test` and
`uv run pytest` both consume these files.
