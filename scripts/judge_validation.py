#!/usr/bin/env python3
"""judge_validation.py — validate an LLM judge against human labels (EVL-08/09).

"Who validates the validators?" A judge is untrusted until it agrees with humans.
This reads paired human/judge labels and reports TPR/TNR/precision/accuracy/Cohen's
kappa with Wilson CIs, then issues a TRUSTED / NOT VALIDATED / INSUFFICIENT verdict.

Certification is on the FULL labeled set (every label counts toward the agreement
estimate), gating by default on the CI LOWER BOUND — a confidently-wrong judge is worse
than no judge, and a perfect point estimate on too-few labels still has a wide CI. This
is what makes the prescribed 50-100-label loop able to certify a strong judge (it tells
you the exact N needed) while still failing a tiny or noisy set. A dev/test split is
reported as an OVERFIT check. NOTE: full-set gating assumes the judge prompt was not
tuned on these labels; if you iterated the prompt on dev, re-validate on fresh labels.

Label files (--labels): CSV or JSON.
  CSV columns (case-insensitive, first match wins):
    human:  human | human_label | gold | label
    judge:  judge | judge_label | pred | prediction
    id:     id | item_id | trace_id (optional)
  JSON: list of objects with the same keys.

Value mapping (positive class = the thing the judge is trying to flag):
  positive  <- 1, true, pass, yes, good, positive
  negative  <- 0, false, fail, no, bad, negative
  abstain   <- unknown, "", null, abstain   (judge only; humans must commit)

Abstain handling: --abstain exclude (default) drops abstains from TPR/TNR but
reports coverage; --abstain wrong counts a judge abstain as a missed detection.

Usage:
  python judge_validation.py --labels labels.csv
  python judge_validation.py --labels labels.json --threshold 0.9 --seed 0
  python judge_validation.py --labels labels.csv --test-frac 0.25 --abstain wrong --json
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402
import eval_stats  # noqa: E402  (wilson_interval, cohen_kappa)

POS = {"1", "true", "pass", "yes", "good", "positive", "y", "t"}
NEG = {"0", "false", "fail", "no", "bad", "negative", "n", "f"}
ABSTAIN = {"unknown", "", "null", "none", "abstain", "na", "n/a", "?"}

_HUMAN_KEYS = ("human", "human_label", "gold", "label", "truth")
_JUDGE_KEYS = ("judge", "judge_label", "pred", "prediction", "model")
_ID_KEYS = ("id", "item_id", "trace_id", "case_id")


def _pick(d: dict, keys) -> str | None:
    low = { (k or "").strip().lower(): k for k in d.keys() }
    for cand in keys:
        if cand in low:
            return d[low[cand]]
    return None


def _to_class(v, allow_abstain: bool):
    s = str(v).strip().lower()
    if s in POS:
        return 1
    if s in NEG:
        return 0
    if allow_abstain and s in ABSTAIN:
        return None
    raise SystemExit(f"unmappable label value: {v!r} (allow_abstain={allow_abstain})")


def _load(path: str) -> list:
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        rows = data if isinstance(data, list) else data.get("rows", [])
    else:
        rows = _common.load_csv(path)
    out = []
    for r in rows:
        hv = _pick(r, _HUMAN_KEYS)
        jv = _pick(r, _JUDGE_KEYS)
        if hv is None or jv is None:
            raise SystemExit(f"row missing human/judge column: {r}")
        out.append({
            "id": _pick(r, _ID_KEYS),
            "human": _to_class(hv, allow_abstain=False),
            "judge_raw": jv,
        })
    if not out:
        raise SystemExit("no labeled rows found")
    return out


def _confusion(rows: list, abstain_mode: str):
    tp = fp = tn = fn = abstain = 0
    for r in rows:
        j = _to_class(r["judge_raw"], allow_abstain=True)
        h = r["human"]
        if j is None:
            abstain += 1
            if abstain_mode == "wrong":
                # abstain treated as failing to make the correct call
                if h == 1:
                    fn += 1
                else:
                    fp += 1
            continue
        if h == 1 and j == 1:
            tp += 1
        elif h == 0 and j == 1:
            fp += 1
        elif h == 0 and j == 0:
            tn += 1
        elif h == 1 and j == 0:
            fn += 1
    return tp, fp, tn, fn, abstain


def _metrics(tp, fp, tn, fn, conf):
    pos = tp + fn
    neg = tn + fp
    tpr = tp / pos if pos else None
    tnr = tn / neg if neg else None
    prec = tp / (tp + fp) if (tp + fp) else None
    n = tp + fp + tn + fn
    acc = (tp + tn) / n if n else None
    kappa = eval_stats.cohen_kappa(tp, fp, tn, fn) if n else None
    tpr_ci = eval_stats.wilson_interval(tp, pos, conf) if pos else None
    tnr_ci = eval_stats.wilson_interval(tn, neg, conf) if neg else None
    return {
        "n": n, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "tpr": tpr, "tnr": tnr, "precision": prec, "accuracy": acc, "kappa": kappa,
        "tpr_ci": tpr_ci, "tnr_ci": tnr_ci,
    }


def _fmt(x):
    return "n/a" if x is None else f"{x:.4f}"


def _required_balanced_n(threshold: float, conf: float):
    """Smallest balanced label count (~half per class) at which a PERFECT judge's Wilson
    lower bound clears `threshold` — the minimum that can possibly certify TRUSTED."""
    for per_class in range(1, 2001):
        if eval_stats.wilson_interval(per_class, per_class, conf)[0] >= threshold:
            return 2 * per_class
    return None


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--labels", required=True, help="CSV or JSON of paired human/judge labels")
    p.add_argument("--test-frac", type=float, default=0.25, help="held-out fraction (default 0.25)")
    p.add_argument("--threshold", type=float, default=0.9, help="TPR & TNR bar for TRUSTED (default 0.9)")
    p.add_argument("--gate-on", choices=("ci_lower", "point"), default="ci_lower",
                   help="gate TRUSTED on the CI lower bound (default) or the point estimate")
    p.add_argument("--min-per-class", type=int, default=5,
                   help="min positives AND negatives in the labeled set, else INSUFFICIENT (default 5)")
    p.add_argument("--abstain", choices=("exclude", "wrong"), default="exclude")
    p.add_argument("--conf", type=float, default=0.95, help="CI confidence (default 0.95)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    rows = _load(args.labels)
    rng = random.Random(args.seed)

    # Certification estimate on the FULL labeled set (every label counts).
    tpA, fpA, tnA, fnA, abA = _confusion(rows, args.abstain)
    full = _metrics(tpA, fpA, tnA, fnA, args.conf)
    full["abstain"] = abA
    full["coverage"] = ((tpA + fpA + tnA + fnA) / len(rows)) if rows else None

    # dev/test split reported only as an overfit check.
    shuffled = list(rows)
    rng.shuffle(shuffled)
    n_test = max(1, round(len(shuffled) * args.test_frac))
    test, dev = shuffled[:n_test], shuffled[n_test:]
    out = {}
    for name, subset in (("dev", dev), ("test", test)):
        tp, fp, tn, fn, ab = _confusion(subset, args.abstain)
        m = _metrics(tp, fp, tn, fn, args.conf)
        m["abstain"] = ab
        m["coverage"] = ((tp + fp + tn + fn) / len(subset)) if subset else None
        out[name] = m

    pos = full["tp"] + full["fn"]
    neg = full["tn"] + full["fp"]
    tpr_lo = full["tpr_ci"][0] if full["tpr_ci"] else None
    tnr_lo = full["tnr_ci"][0] if full["tnr_ci"] else None
    req_n = _required_balanced_n(args.threshold, args.conf)

    warnings = []
    if len(rows) < 50:
        warnings.append(f"only {len(rows)} labels; field practice is 50-100+ for a stable estimate.")
    if pos < args.min_per_class or neg < args.min_per_class:
        warnings.append(f"fewer than {args.min_per_class} positives or negatives in the labeled set.")

    # Gate on the FULL-set CI lower bound by default (a confidently-wrong judge is worse
    # than no judge; a perfect point estimate on too-few labels still has a wide CI).
    if full["tpr"] is None or full["tnr"] is None or pos < args.min_per_class or neg < args.min_per_class:
        verdict = "INSUFFICIENT"
    elif args.gate_on == "point":
        verdict = "TRUSTED" if (full["tpr"] >= args.threshold and full["tnr"] >= args.threshold) else "NOT VALIDATED"
    else:
        ok = (tpr_lo is not None and tnr_lo is not None
              and tpr_lo >= args.threshold and tnr_lo >= args.threshold)
        verdict = "TRUSTED" if ok else "NOT VALIDATED"
    underpowered = (verdict == "NOT VALIDATED" and args.gate_on == "ci_lower"
                    and full["tpr"] is not None and full["tnr"] is not None
                    and full["tpr"] >= args.threshold and full["tnr"] >= args.threshold)
    tm = out["test"]
    overfit = (tm["tpr"] is not None and full["tpr"] is not None
               and (full["tpr"] - tm["tpr"]) > 0.15)

    if args.json:
        print(json.dumps({"verdict": verdict, "threshold": args.threshold, "gate_on": args.gate_on,
                          "underpowered": underpowered, "overfit_warning": overfit,
                          "required_balanced_n": req_n, "full": full, "test": tm, "dev": out["dev"],
                          "warnings": warnings, "n_total": len(rows)}, indent=2, ensure_ascii=False))
        return 0

    def _ci(ci):
        return "n/a" if not ci else f"[{ci[0]:.3f}, {ci[1]:.3f}]"
    print(f"labels: {len(rows)} total  (full-set certification; dev={len(dev)}/test={len(test)} "
          f"split reported as an overfit check; seed={args.seed}, abstain={args.abstain})")
    print("\nFULL-SET metrics (the certification estimate):")
    print(f"  coverage={_fmt(full['coverage'])}  abstain={full['abstain']}  "
          f"(tp={full['tp']} fp={full['fp']} tn={full['tn']} fn={full['fn']})")
    print(f"  TPR={_fmt(full['tpr'])}  CI={_ci(full['tpr_ci'])}")
    print(f"  TNR={_fmt(full['tnr'])}  CI={_ci(full['tnr_ci'])}")
    print(f"  precision={_fmt(full['precision'])}  accuracy={_fmt(full['accuracy'])}  kappa={_fmt(full['kappa'])}")
    print(f"\n(held-out TEST overfit check: TPR={_fmt(tm['tpr'])} TNR={_fmt(tm['tnr'])}"
          + ("  ! test << full: possible tuning-on-dev overfit" if overfit else "") + ")")
    for w in warnings:
        print(f"  ! {w}")
    bar = f"TPR & TNR {'CI lower bound' if args.gate_on == 'ci_lower' else 'point'} >= {args.threshold}"
    print(f"\nVERDICT: {verdict}  (need {bar} on the full labeled set)")
    if verdict == "INSUFFICIENT":
        need = f"~{req_n} balanced labels (>= {args.min_per_class}/class)" if req_n else "more labels"
        print(f"  -> too few to certify at threshold {args.threshold}: collect {need} and re-run.")
    elif underpowered:
        need = f"~{req_n} balanced labels" if req_n else "more labels"
        print(f"  -> UNDER-POWERED: the point estimate meets the bar but the CI lower bound does not. "
              f"Collect {need} (a perfect judge needs that many to certify), or --gate-on point at your own risk.")
    elif verdict == "NOT VALIDATED":
        print("  -> do NOT trust this judge yet: refine the rubric/prompt on dev, re-label, re-measure.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
