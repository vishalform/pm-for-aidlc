#!/usr/bin/env python3
"""build_axes.py — generate the bundled 6-axis catalog data/aidlc_axes.csv.

`blast` is the one axis NOT stored in aidlc_microtasks.csv. It is hand-curated in
references/task-catalog.md (and consistent with the task-review B3 tables). This
generator parses all six axes from the catalog, cross-checks the five CSV-backed
axes against aidlc_microtasks.csv, FAILS on any mismatch, and writes the bundle
that autonomy_gate.py / select_task.py read by default. Single-source-of-truth is
preserved because the artifact is generated, not hand-edited.

Run when the catalog or the CSV changes:
  python build_axes.py                 # writes data/aidlc_axes.csv
  python build_axes.py --check         # verify only; non-zero exit on drift
  python build_axes.py --catalog ... --csv ...

Output columns: id,leverage,blast,eval,regr,safety,fly,actuation,phase_status,cluster,name

`actuation` (read-only | reversible) marks the read-only monitor carve-out used by
autonomy_gate.py. It is set from READ_ONLY_TASKS below (curated; everything else is
the safe default `reversible`), because the catalog axes line carries only 6 axes. The
ONLY autonomous safety:high task is AT-56 (the groundedness monitor), so that is the only
id whose read-only flag changes a verdict; add any new autonomous safety:high *monitor*
here so it is asserted, never inferred.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402

_CLUSTER_RE = re.compile(r"^##\s+\d+\.\s+(.+?)\s*$")
_HEADER_RE = re.compile(r"^\*\*(AT-\d+|EVL-\d+)\s*·\s*(.+?)\*\*\s*·\s*`([^`]+)`")
_AXES_RE = re.compile(
    r"autonomy\s+`([^`]+)`.*?blast\s+`([^`]+)`.*?eval\s+`([^`]+)`.*?"
    r"regression\s+`([^`]+)`.*?safety\s+`([^`]+)`.*?flywheel\s+`([^`]+)`"
)

_NORM = {"": "none", "-": "none", "–": "none", "—": "none", "n/a": "none"}

# Read-only, non-actuating tasks (monitors / passive checks). actuation defaults to the
# safe "reversible" for every other id; read-only must be asserted, never inferred (it is
# the safety:high carve-out). AT-56 is the only autonomous safety:high monitor — the only
# id whose read-only flag changes an autonomy verdict.
READ_ONLY_TASKS = {"AT-56"}


def _norm(v: str) -> str:
    v = (v or "").strip().lower()
    return _NORM.get(v, v)


def parse_catalog(path: str) -> dict:
    """Return {id: {leverage,blast,eval,regr,safety,fly,phase_status,cluster,name}}."""
    out = {}
    cluster = ""
    pending = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            mc = _CLUSTER_RE.match(line)
            if mc and "Classic" not in mc.group(1):
                cluster = mc.group(1).strip()
                continue
            mh = _HEADER_RE.match(line.strip())
            if mh:
                pending = {"id": mh.group(1), "name": mh.group(2).strip(),
                           "phase_status": mh.group(3).strip(), "cluster": cluster}
                continue
            if pending and "Axes:" in line:
                ma = _AXES_RE.search(line)
                if not ma:
                    raise SystemExit(f"could not parse axes for {pending['id']}: {line.strip()!r}")
                pending.update({
                    "leverage": _norm(ma.group(1)), "blast": _norm(ma.group(2)),
                    "eval": _norm(ma.group(3)), "regr": _norm(ma.group(4)),
                    "safety": _norm(ma.group(5)), "fly": _norm(ma.group(6)),
                })
                out[pending["id"]] = pending
                pending = None
    return out


def crosscheck(catalog: dict, csv_path: str) -> list:
    """Compare the 5 CSV-backed axes; return list of mismatch strings (empty = ok)."""
    rows = {(r.get("id") or "").strip(): r for r in _common.load_csv(csv_path)}
    pairs = [("leverage", "ai_leverage"), ("eval", "eval_coverage"),
             ("regr", "regression_risk"), ("safety", "safety_exposure"), ("fly", "flywheel_linkage")]
    mismatches = []
    for tid, cat in catalog.items():
        row = rows.get(tid)
        if row is None:
            mismatches.append(f"{tid}: in catalog but not in CSV")
            continue
        for cat_key, csv_key in pairs:
            cv = _norm(row.get(csv_key, ""))
            if cat[cat_key] != cv:
                mismatches.append(f"{tid}.{cat_key}: catalog={cat[cat_key]!r} != csv={cv!r}")
    # ids in CSV but missing from catalog
    for tid in rows:
        if tid and tid not in catalog:
            mismatches.append(f"{tid}: in CSV but not in catalog")
    return mismatches


def _sort_key(tid: str):
    pre, num = tid.split("-")
    return (0 if pre == "AT" else 1, int(num))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--catalog", default=os.path.join(_common.skill_root(), "references", "task-catalog.md"))
    p.add_argument("--csv", help="aidlc_microtasks.csv (default: bundled data/ or Research/)")
    p.add_argument("--out", default=_common.bundled_path(_common.AXES_BUNDLE_NAME))
    p.add_argument("--check", action="store_true", help="verify only; do not write")
    args = p.parse_args(argv)

    if not os.path.isfile(args.catalog):
        raise SystemExit(f"catalog not found: {args.catalog}")
    catalog = parse_catalog(args.catalog)
    if not catalog:
        raise SystemExit("parsed 0 tasks from the catalog — check the format")

    csv_path = None
    try:
        csv_path = _common.resolve_csv(args.csv, _common.AIDLC_CSV_NAME)
    except (_common.DataNotFound, FileNotFoundError):
        pass

    mismatches = crosscheck(catalog, csv_path) if csv_path else ["(no CSV available — skipped cross-check)"]
    hard = [m for m in mismatches if not m.startswith("(")]
    if hard:
        print(f"FAIL: {len(hard)} catalog/CSV mismatch(es):", file=sys.stderr)
        for m in hard:
            print(f"  - {m}", file=sys.stderr)
        return 1

    cols = ["id", "leverage", "blast", "eval", "regr", "safety", "fly", "actuation",
            "phase_status", "cluster", "name"]
    ids = sorted(catalog, key=_sort_key)
    if args.check:
        print(f"OK: {len(ids)} tasks parsed; axes consistent with {csv_path or '(no CSV)'}.")
        return 0

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for tid in ids:
            r = catalog[tid]
            actuation = "read-only" if tid in READ_ONLY_TASKS else "reversible"
            w.writerow([tid, r["leverage"], r["blast"], r["eval"], r["regr"],
                        r["safety"], r["fly"], actuation, r["phase_status"], r["cluster"], r["name"]])
    print(f"wrote {args.out} ({len(ids)} tasks; cross-checked vs {csv_path or '(no CSV)'}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
