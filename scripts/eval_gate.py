#!/usr/bin/env python3
"""eval_gate.py — run a pre-registered eval gate (AT-16/AT-49/AT-54/EVL-12).

"The eval is the unit test for a non-deterministic system; if it's not in CI, it's not
a gate." This consumes per-case eval results + a pre-registered bar and returns
pass/fail, gating on the **CI lower bound** (not the point estimate) and on the **worst
slice** (an aggregate pass can hide a broken slice). Optional regression check vs a
baseline. Reuses eval_stats internals (stdlib only — bar is JSON, not YAML).

Inputs:
  --results results.jsonl   one JSON object per line:
                            {"case_id","metric","score"(0/1 or float),"slice"(optional)}
  --bar bar.json            pre-registered thresholds, e.g.
      {
        "groundedness": {"min_ci_lower": 0.95, "guardrail": true},
        "tool_accuracy": {"min_ci_lower": 0.90},
        "cost_per_task": {"max": 0.03},
        "worst_slice":   {"min_ci_lower": 0.85}
      }
  --baseline base.jsonl     (optional) same format; flags significant regressions.

Bar keys per metric: min_ci_lower (gate CI lower bound) | min (gate point mean) |
max (ceiling, e.g. cost) | guardrail (bool: marks a non-negotiable floor — e.g. safety or
groundedness — surfaced first in the output; EVERY failed metric, failed slice, or
significant regression is a NO-GO, guardrail or not).
Special metric "worst_slice": {min_ci_lower|min} applies to every quality metric's slices.
The optional --baseline regression check PAIRS candidate vs baseline by case_id (then by
index), using McNemar (binary) / paired permutation — never an unpaired pooled test.

Exit code: 0 = GO, 1 = NO-GO (drop-in CI gate, mirrors contamination_check's pattern).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402
import eval_stats  # noqa: E402


def _load_jsonl(path: str) -> list:
    out = []
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out


def _ci_lower(scores: list, conf: float, boot: int, seed: int) -> float:
    if not scores:
        return 0.0
    if set(scores) <= {0.0, 1.0}:
        return eval_stats.wilson_interval(int(sum(scores)), len(scores), conf)[0]
    return eval_stats.bootstrap_ci(scores, conf, boot, seed)[0]


def _by_metric(rows: list) -> dict:
    m = {}
    for r in rows:
        m.setdefault(r["metric"], []).append(r)
    return m


def _align(base_rows: list, cand_rows: list):
    """Pair candidate vs baseline by case_id; fall back to index order; else unpaired.

    Returns (base_scores, cand_scores, mode, coverage). Eval A/B is paired by construction
    (same frozen eval set under two systems). Pairing by case_id keeps the power an unpaired
    test discards. `coverage` (when case_ids are present) reports cases the candidate DROPPED
    relative to the baseline and any duplicate ids — a candidate that omits the cases it
    fails would otherwise evade both the bar and the regression check (a silent false GO).
    """
    b_ids = [r.get("case_id") for r in base_rows]
    c_ids = [r.get("case_id") for r in cand_rows]
    if all(i is not None for i in b_ids) and all(i is not None for i in c_ids):
        cov = {"dropped": sorted(set(b_ids) - set(c_ids), key=str),
               "extra": sorted(set(c_ids) - set(b_ids), key=str),
               "dup": len(b_ids) != len(set(b_ids)) or len(c_ids) != len(set(c_ids))}
        b_map = {r["case_id"]: float(r["score"]) for r in base_rows}
        c_map = {r["case_id"]: float(r["score"]) for r in cand_rows}
        common = [cid for cid in b_ids if cid in c_map]  # baseline order, intersection
        if common:
            return [b_map[c] for c in common], [c_map[c] for c in common], "case_id", cov
        return [], [], "disjoint", cov  # never index-pair unrelated cases
    if len(base_rows) == len(cand_rows):
        return ([float(r["score"]) for r in base_rows],
                [float(r["score"]) for r in cand_rows], "index", None)
    return ([float(r["score"]) for r in base_rows],
            [float(r["score"]) for r in cand_rows], "unpaired", None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", required=True)
    p.add_argument("--bar", required=True, help="bar.json (pre-registered thresholds)")
    p.add_argument("--baseline", help="baseline results.jsonl for a regression check")
    p.add_argument("--conf", type=float, default=0.95)
    p.add_argument("--boot", type=int, default=10000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    rows = _load_jsonl(args.results)
    if not rows:
        raise SystemExit("no results rows")
    with open(args.bar, encoding="utf-8") as fh:
        bar = json.load(fh)
    by_metric = _by_metric(rows)
    base_by_metric = _by_metric(_load_jsonl(args.baseline)) if args.baseline else {}

    findings = []
    overall_ok = True

    for metric, spec in bar.items():
        if metric == "worst_slice":
            continue
        scores = [float(r["score"]) for r in by_metric.get(metric, [])]
        if not scores:
            findings.append({"metric": metric, "status": "MISSING", "detail": "no results for this metric"})
            overall_ok = False
            continue
        mean = sum(scores) / len(scores)
        f = {"metric": metric, "n": len(scores), "mean": round(mean, 4),
             "guardrail": bool(spec.get("guardrail"))}
        ok = True
        if "max" in spec:
            ok = mean <= spec["max"]
            f["check"] = f"mean {mean:.4f} <= max {spec['max']}"
        elif "min" in spec:
            ok = mean >= spec["min"]
            f["check"] = f"mean {mean:.4f} >= min {spec['min']}"
        elif "min_ci_lower" in spec:
            lo = _ci_lower(scores, args.conf, args.boot, args.seed)
            f["ci_lower"] = round(lo, 4)
            ok = lo >= spec["min_ci_lower"]
            f["check"] = f"ci_lower {lo:.4f} >= {spec['min_ci_lower']}"
        f["status"] = "PASS" if ok else "FAIL"
        findings.append(f)
        overall_ok = overall_ok and ok

    # worst-slice gate across quality metrics that carry slices
    ws = bar.get("worst_slice")
    if ws:
        floor = ws.get("min_ci_lower", ws.get("min"))
        use_ci = "min_ci_lower" in ws
        for metric, rs in by_metric.items():
            if metric in bar and ("max" in bar[metric]):  # skip cost-type metrics
                continue
            slices = {}
            for r in rs:
                if r.get("slice"):
                    slices.setdefault(r["slice"], []).append(float(r["score"]))
            for sl, sc in slices.items():
                val = _ci_lower(sc, args.conf, args.boot, args.seed) if use_ci else (sum(sc) / len(sc))
                if val < floor:
                    findings.append({"metric": metric, "slice": sl, "status": "FAIL",
                                     "check": f"slice {('ci_lower' if use_ci else 'mean')} {val:.4f} >= {floor}",
                                     "n": len(sc)})
                    overall_ok = False

    # regression vs baseline (PAIRED: same eval set under base vs candidate)
    regressions = []
    for metric, rs in by_metric.items():
        if metric not in base_by_metric:
            continue
        base, cand, mode, cov = _align(base_by_metric[metric], rs)
        # M3-1/M3-5: coverage + integrity. A candidate that drops the cases it fails (or
        # has duplicate/disjoint ids) must not silently pass — that hides a real regression.
        if cov is not None:
            if cov["dup"]:
                findings.append({"metric": metric, "status": "FAIL",
                                 "check": "duplicate case_id in results or baseline — cannot pair reliably"})
                overall_ok = False
            if cov["dropped"]:
                findings.append({"metric": metric, "status": "FAIL",
                                 "check": f"candidate dropped {len(cov['dropped'])} baseline case_id(s) "
                                          f"(coverage gap — cherry-picked/errored cases hide regressions): "
                                          f"{cov['dropped'][:10]}"})
                overall_ok = False
            if mode == "disjoint":
                findings.append({"metric": metric, "status": "FAIL",
                                 "check": "candidate and baseline case_ids are disjoint — cannot compare"})
                overall_ok = False
        if not base or not cand:
            continue
        delta = sum(cand) / len(cand) - sum(base) / len(base)
        binary = set(base) <= {0.0, 1.0} and set(cand) <= {0.0, 1.0}
        if mode == "unpaired":
            pval = eval_stats.permutation_pvalue(base, cand, args.boot, args.seed)
        elif binary:
            n01 = sum(1 for x, y in zip(base, cand) if x == 0.0 and y == 1.0)
            n10 = sum(1 for x, y in zip(base, cand) if x == 1.0 and y == 0.0)
            pval = eval_stats.mcnemar_exact(n01, n10)
        else:
            pval = eval_stats.paired_permutation_pvalue(base, cand, args.boot, args.seed)
        if delta < 0 and pval < (1 - args.conf):
            regressions.append({"metric": metric, "delta": round(delta, 4),
                                "p": round(pval, 4), "pairing": mode})
            overall_ok = False

    verdict = "GO" if overall_ok else "NO-GO"
    result = {"verdict": verdict, "findings": findings, "regressions": regressions}
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for f in findings:
            tag = f["status"]
            extra = f.get("check", f.get("detail", ""))
            slc = f" slice={f['slice']}" if f.get("slice") else ""
            guard = " [guardrail]" if f.get("guardrail") else ""
            print(f"  [{tag}] {f['metric']}{slc}{guard}: {extra}")
        for r in regressions:
            print(f"  [FAIL] {r['metric']}: regression delta={r['delta']} "
                  f"(p={r['p']}, {r.get('pairing', '?')})")
        print(f"\nVERDICT: {verdict}")
        if verdict == "NO-GO":
            print("  -> do not ship: a gated metric, a slice floor, or a regression failed.")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
