# Golden vectors

Compatibility contract for `symsight.textutil` and the Rust `symsight-core` port.

`*.json` under this directory (except `front_matter.json` / `write_new_draft/`)
are generated from the current Python implementation:

```bash
uv run python scripts/export_goldens.py
```

`front_matter.json` and `write_new_draft/` lock the hand-rolled draft codec
against `src/symsight/draft_io.py`. Do **not** regenerate textutil goldens
after `textutil.py` becomes a shim unless you intend to change the contract.
