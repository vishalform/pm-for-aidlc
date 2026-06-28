# data/ — bundled, self-contained skill data

The skill vendors its data here so the scripts work **without** the external `Research/`
directory (portability). Scripts read `data/` first, then fall back to `Research/`, and
always honor an explicit `--csv`/`--aidlc-csv`/etc. override.

| File | What | Source / regeneration |
|---|---|---|
| `aidlc_microtasks.csv` | Frozen copy of the 102 AIDLC tasks (5 axes + text). | Snapshot of `Research/aidlc_microtasks.csv`. Re-copy to refresh. |
| `aidlc-usecases.csv` | Frozen copy of the 16 use-case → task-id index. | Snapshot of `Research/aidlc-usecases.csv`. |
| `aidlc_axes.csv` | **Generated** 6-axis catalog incl. `blast` (the gate's source of truth). | `python scripts/build_axes.py` — parses `references/task-catalog.md`, cross-checks the 5 CSV axes, fails on drift. |

`blast` is the one axis not stored in `aidlc_microtasks.csv`; `aidlc_axes.csv` is how the
autonomy gate resolves a precise `blast` for `--id` (no more silent `med` default).

**To refresh after a source change:** re-copy the two CSVs from `Research/`, then run
`python scripts/build_axes.py` to regenerate `aidlc_axes.csv` (it will fail loudly if the
catalog and CSV disagree). The classic `pm_microtask_database.csv` is intentionally not
vendored (large); `--include-classic` falls back to `Research/` or `--classic-csv`.
