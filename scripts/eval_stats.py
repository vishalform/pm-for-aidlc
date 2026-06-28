#!/usr/bin/env python3
"""eval_stats.py — statistics for eval scores (stdlib-only; no numpy/scipy).

Route every quantitative claim through this so the model never eyeballs numbers.
Subcommands:

  ci       mean + bootstrap CI (and Wilson interval for 0/1 data) for one set of scores.
  compare  difference between two sets: bootstrap CI of the delta + permutation p-value.
  passk    pass@k (>=1 of k succeeds) and pass^k (all k succeed) from (n, c) per task.
  power    two-proportion sample size / power / MDE (normal approximation).
  judge    precision/recall/TPR/TNR/accuracy/kappa from confusion counts tp fp tn fn.
  selftest golden-value regression checks (catches the pass^k class of bug); exit 1 on fail.

Inputs are read from flags / files / stdin only — nothing is fabricated.

Examples:
  python eval_stats.py ci --scores 1,0,1,1,0,1,1,1,0,1
  python eval_stats.py ci --data scores.txt --conf 0.95
  python eval_stats.py compare --a base.txt --b cand.txt
  python eval_stats.py passk --data runs.tsv --k 1,5,8     # each line: "n c"
  python eval_stats.py passk --n 8 --c 5 --k 1,8
  python eval_stats.py power --p0 0.80 --mde 0.05 --alpha 0.05 --power 0.8
  python eval_stats.py power --p0 0.80 --n 1500 --alpha 0.05
  python eval_stats.py judge --tp 40 --fp 6 --tn 44 --fn 10
"""
from __future__ import annotations

import argparse
import math
import os
import random
import sys
from statistics import NormalDist

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402

_NORM = NormalDist()


# ---------- input helpers ----------
def _read_numbers(inline: str | None, path: str | None) -> list:
    raw = ""
    if inline:
        raw = inline
    elif path:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    else:
        raise SystemExit("no data: pass --scores, --data FILE, or pipe via stdin")
    out = []
    for tok in raw.replace(",", " ").split():
        try:
            out.append(float(tok))
        except ValueError:
            raise SystemExit(f"not a number: {tok!r}")
    if not out:
        raise SystemExit("no numeric values found")
    return out


def _read_pairs(path: str | None) -> list:
    """Read 'n c' (or 'n,c') per line for passk."""
    if not path:
        raise SystemExit("passk over multiple tasks needs --data FILE with 'n c' per line")
    pairs = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.replace(",", " ").split()
            if len(parts) < 2:
                raise SystemExit(f"bad passk row (need 'n c'): {line!r}")
            n, c = int(float(parts[0])), int(float(parts[1]))
            if c > n or n < 0 or c < 0:
                raise SystemExit(f"bad passk row (need 0<=c<=n): {line!r}")
            pairs.append((n, c))
    if not pairs:
        raise SystemExit("no passk rows found")
    return pairs


# ---------- stats core ----------
def bootstrap_ci(values: list, conf: float, boot: int, seed: int) -> tuple:
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(boot):
        s = 0.0
        for _ in range(n):
            s += values[rng.randrange(n)]
        means.append(s / n)
    means.sort()
    lo_idx = int((1 - conf) / 2 * boot)
    hi_idx = int((1 + conf) / 2 * boot) - 1
    hi_idx = min(max(hi_idx, 0), boot - 1)
    return means[lo_idx], means[hi_idx]


def wilson_interval(c: int, n: int, conf: float) -> tuple:
    if n == 0:
        return (0.0, 1.0)
    z = _NORM.inv_cdf((1 + conf) / 2)
    p = c / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def _check_nck(n: int, c: int, k: int) -> None:
    if n < 0 or c < 0 or c > n:
        raise ValueError(f"need 0<=c<=n, got n={n} c={c}")
    if k < 1:
        raise ValueError(f"k must be >=1, got {k}")
    if k > n:
        raise ValueError(f"k={k} > n={n}")


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased estimator (Codex/HumanEval): P(>=1 of k drawn without replacement passes)."""
    _check_nck(n, c, k)
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """Unbiased estimator: P(all k drawn without replacement pass) — reliability metric."""
    _check_nck(n, c, k)
    if c < k:
        return 0.0
    return comb(c, k) / comb(n, k)


def two_prop_n(p0: float, p1: float, alpha: float, power: float) -> int:
    """Required n PER GROUP to detect p0 vs p1 (two-sided), normal approximation."""
    z_a = _NORM.inv_cdf(1 - alpha / 2)
    z_b = _NORM.inv_cdf(power)
    pbar = (p0 + p1) / 2
    num = (z_a * math.sqrt(2 * pbar * (1 - pbar)) + z_b * math.sqrt(p0 * (1 - p0) + p1 * (1 - p1))) ** 2
    den = (p1 - p0) ** 2
    return max(1, math.ceil(num / den))


def two_prop_power(p0: float, p1: float, alpha: float, n: int) -> float:
    """Achieved power for n per group, p0 vs p1, two-sided.

    Uses the SAME pooled/unpooled SE split as two_prop_n so the two round-trip
    consistently (pooled SE for the null term, unpooled for the alternative term).
    """
    z_a = _NORM.inv_cdf(1 - alpha / 2)
    pbar = (p0 + p1) / 2
    se_pooled = math.sqrt(2 * pbar * (1 - pbar))
    se_alt = math.sqrt(p0 * (1 - p0) + p1 * (1 - p1))
    if se_alt == 0:
        return 1.0
    z_b = (math.sqrt(n) * abs(p1 - p0) - z_a * se_pooled) / se_alt
    return _NORM.cdf(z_b)


def permutation_pvalue(a: list, b: list, reps: int, seed: int) -> float:
    """UNPAIRED two-sample permutation p (pool + shuffle). For independent samples only."""
    rng = random.Random(seed)
    obs = abs(sum(a) / len(a) - sum(b) / len(b))
    pooled = a + b
    na = len(a)
    count = 0
    for _ in range(reps):
        rng.shuffle(pooled)
        ma = sum(pooled[:na]) / na
        mb = sum(pooled[na:]) / (len(pooled) - na)
        if abs(ma - mb) >= obs - 1e-12:
            count += 1
    return (count + 1) / (reps + 1)


def paired_bootstrap_ci(deltas: list, conf: float, boot: int, seed: int) -> tuple:
    """Bootstrap CI of the MEAN per-item delta (resample item indices). Paired design."""
    rng = random.Random(seed)
    n = len(deltas)
    means = []
    for _ in range(boot):
        s = 0.0
        for _ in range(n):
            s += deltas[rng.randrange(n)]
        means.append(s / n)
    means.sort()
    lo = means[int((1 - conf) / 2 * boot)]
    hi = means[min(int((1 + conf) / 2 * boot), boot - 1)]
    return lo, hi


def paired_permutation_pvalue(a: list, b: list, reps: int, seed: int) -> float:
    """PAIRED two-sided permutation p via random sign-flips of per-item deltas.

    The correct test when A and B score the SAME items (the frozen eval set): it
    conditions on the pairing instead of pooling, so it keeps the power an unpaired
    test throws away. Valid for binary and continuous scores.
    """
    rng = random.Random(seed)
    deltas = [bi - ai for ai, bi in zip(a, b)]
    n = len(deltas)
    obs = abs(sum(deltas) / n)
    count = 0
    for _ in range(reps):
        s = sum(d if rng.random() < 0.5 else -d for d in deltas)
        if abs(s / n) >= obs - 1e-12:
            count += 1
    return (count + 1) / (reps + 1)


def mcnemar_exact(n01: int, n10: int) -> float:
    """Two-sided exact McNemar (binomial) p from the two discordant counts.

    n01 = pairs where A=0,B=1 (B fixed); n10 = pairs where A=1,B=0 (B broke / regression).
    Concordant pairs are uninformative. Exact binomial under H0: discordances are 50/50.
    """
    n = n01 + n10
    if n == 0:
        return 1.0
    k = min(n01, n10)
    cdf = sum(comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2.0 * cdf)


def cohen_kappa(tp: int, fp: int, tn: int, fn: int) -> float:
    n = tp + fp + tn + fn
    if n == 0:
        return float("nan")
    po = (tp + tn) / n
    p_yes = ((tp + fn) / n) * ((tp + fp) / n)
    p_no = ((tn + fp) / n) * ((tn + fn) / n)
    pe = p_yes + p_no
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


# ---------- subcommands ----------
def cmd_ci(args) -> int:
    vals = _read_numbers(args.scores, args.data)
    mean = sum(vals) / len(vals)
    lo, hi = bootstrap_ci(vals, args.conf, args.boot, args.seed)
    print(f"n={len(vals)}  mean={mean:.4f}")
    print(f"bootstrap {int(args.conf*100)}% CI: [{lo:.4f}, {hi:.4f}]  (B={args.boot}, seed={args.seed})")
    if set(vals) <= {0.0, 1.0}:
        c = int(sum(vals))
        wlo, whi = wilson_interval(c, len(vals), args.conf)
        print(f"binary: {c}/{len(vals)} pass; Wilson {int(args.conf*100)}% CI: [{wlo:.4f}, {whi:.4f}]")
        print(f"alert on the LOWER bound ({min(lo, wlo):.4f}), not the point estimate.")
    return 0


def cmd_compare(args) -> int:
    a = _read_numbers(args.a_inline, args.a)
    b = _read_numbers(args.b_inline, args.b)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    diff = mb - ma
    binary = set(a) <= {0.0, 1.0} and set(b) <= {0.0, 1.0}

    # Paired is the DEFAULT for equal-length inputs because eval A/B is paired by
    # construction: the same frozen eval set scored under system A and system B. An
    # unpaired test pools the two and discards the pairing, losing power (and missing
    # real paired regressions). Use --unpaired only for genuinely independent samples.
    if args.unpaired:
        paired = False
    elif args.paired:
        if len(a) != len(b):
            raise SystemExit("--paired requires equal-length, index-aligned inputs")
        paired = True
    else:
        paired = (len(a) == len(b))

    n01 = n10 = None
    if paired:
        deltas = [bi - ai for ai, bi in zip(a, b)]
        lo, hi = paired_bootstrap_ci(deltas, args.conf, args.boot, args.seed)
        if binary:
            n01 = sum(1 for ai, bi in zip(a, b) if ai == 0.0 and bi == 1.0)  # B fixed
            n10 = sum(1 for ai, bi in zip(a, b) if ai == 1.0 and bi == 0.0)  # B broke
            pval = mcnemar_exact(n01, n10)
        else:
            pval = paired_permutation_pvalue(a, b, args.boot, args.seed)
    else:
        rng = random.Random(args.seed)
        diffs = []
        for _ in range(args.boot):
            sa = sum(a[rng.randrange(len(a))] for _ in a) / len(a)
            sb = sum(b[rng.randrange(len(b))] for _ in b) / len(b)
            diffs.append(sb - sa)
        diffs.sort()
        lo = diffs[int((1 - args.conf) / 2 * args.boot)]
        hi = diffs[min(int((1 + args.conf) / 2 * args.boot), args.boot - 1)]
        pval = permutation_pvalue(a, b, args.boot, args.seed)
    sig = (lo > 0 or hi < 0) and pval < args.alpha
    verdict = ("ship-eligible on this metric." if sig and diff > 0 else
               "do not claim a difference." if not sig else "significant regression.")

    if args.json:
        import json
        out = {"paired": paired, "binary": binary, "n_a": len(a), "n_b": len(b),
               "mean_a": ma, "mean_b": mb, "delta": diff, "ci_lower": lo, "ci_upper": hi,
               "p": pval, "alpha": args.alpha, "significant": sig, "verdict": verdict}
        if binary and paired:
            out["mcnemar_n01_fixed"], out["mcnemar_n10_broke"] = n01, n10
        print(json.dumps(out, indent=2))
        return 0

    tag = "PAIRED" if paired else "UNPAIRED"
    print(f"A: n={len(a)} mean={ma:.4f}    B: n={len(b)} mean={mb:.4f}   [{tag}]")
    print(f"delta (B-A) = {diff:+.4f}")
    label = "paired bootstrap" if paired else "bootstrap"
    print(f"{label} {int(args.conf*100)}% CI of {'mean delta' if paired else 'delta'}: [{lo:+.4f}, {hi:+.4f}]")
    if paired and binary:
        print(f"McNemar exact p (two-sided) = {pval:.4f}  "
              f"(discordant: B-fixed={n01}, B-broke={n10}; alpha={args.alpha})")
    elif paired:
        print(f"paired permutation p (two-sided) = {pval:.4f}  (alpha={args.alpha})")
    else:
        print(f"permutation p (two-sided) = {pval:.4f}  (alpha={args.alpha})")
    print(f"verdict: {'SIGNIFICANT' if sig else 'NOT significant'} — {verdict}")
    return 0


def cmd_passk(args) -> int:
    ks = [int(x) for x in str(args.k).replace(",", " ").split()]
    if args.n is not None and args.c is not None:
        if args.n < 0 or args.c < 0 or args.c > args.n:  # M2: guard the inline path too
            raise SystemExit(f"need 0<=c<=n, got n={args.n} c={args.c}")
        tasks = [(args.n, args.c)]
    else:
        tasks = _read_pairs(args.data)
    print(f"tasks={len(tasks)}  k={ks}")
    for k in ks:
        at = [pass_at_k(n, c, k) for (n, c) in tasks if n >= k]
        hat = [pass_hat_k(n, c, k) for (n, c) in tasks if n >= k]
        skipped = sum(1 for (n, _) in tasks if n < k)
        if not at:
            print(f"  k={k}: (no task has n>={k})")
            continue
        msg = f"  k={k:<3} pass@k={sum(at)/len(at):.4f}   pass^k={sum(hat)/len(hat):.4f}"
        if skipped:
            msg += f"   ({skipped} task(s) skipped: n<k)"
        print(msg)
    print("read: pass@k = capability/coverage (dev, human-in-loop); "
          "pass^k = reliability (gate autonomous/high-stakes here).")
    return 0


def cmd_power(args) -> int:
    if not 0 < args.p0 < 1:
        raise SystemExit("--p0 must be in (0,1)")
    if args.n is not None:
        if args.mde is not None:
            p1 = args.p0 + (args.p0 * args.mde if args.rel else args.mde)
            pw = two_prop_power(args.p0, min(max(p1, 1e-6), 1 - 1e-6), args.alpha, args.n)
            print(f"p0={args.p0}  p1={p1:.4f}  n/group={args.n}  alpha={args.alpha}")
            print(f"achieved power = {pw:.4f}")
        else:
            # find MDE achievable at the requested power for this n (binary search)
            lo, hi = 1e-5, 1 - args.p0 - 1e-5
            for _ in range(60):
                mid = (lo + hi) / 2
                if two_prop_power(args.p0, args.p0 + mid, args.alpha, args.n) < args.power:
                    lo = mid
                else:
                    hi = mid
            print(f"p0={args.p0}  n/group={args.n}  alpha={args.alpha}  power={args.power}")
            print(f"minimum detectable effect (absolute) = {hi:.4f}  "
                  f"(i.e. detect p1>={args.p0+hi:.4f})")
    else:
        if args.mde is None:
            raise SystemExit("power: provide either --n (compute power/MDE) or --mde (compute n)")
        p1 = args.p0 + (args.p0 * args.mde if args.rel else args.mde)
        if not 0 < p1 < 1:
            raise SystemExit(f"implied p1={p1} out of (0,1)")
        n = two_prop_n(args.p0, p1, args.alpha, args.power)
        print(f"p0={args.p0}  p1={p1:.4f}  alpha={args.alpha}  power={args.power}")
        print(f"required n PER GROUP = {n}   (total = {2*n})")
    return 0


def cmd_judge(args) -> int:
    tp, fp, tn, fn = args.tp, args.fp, args.tn, args.fn
    n = tp + fp + tn + fn
    if n == 0:
        raise SystemExit("counts sum to 0")
    tpr = tp / (tp + fn) if (tp + fn) else float("nan")   # recall / sensitivity
    tnr = tn / (tn + fp) if (tn + fp) else float("nan")   # specificity
    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    acc = (tp + tn) / n
    bal = (tpr + tnr) / 2 if not (math.isnan(tpr) or math.isnan(tnr)) else float("nan")
    kappa = cohen_kappa(tp, fp, tn, fn)
    print(f"n={n}  tp={tp} fp={fp} tn={tn} fn={fn}")
    print(f"TPR(recall)={tpr:.4f}  TNR(specificity)={tnr:.4f}  precision={prec:.4f}")
    print(f"accuracy={acc:.4f}  balanced_acc={bal:.4f}  cohen_kappa={kappa:.4f}")
    print("for a trustworthy judge, target TPR and TNR each >= ~0.9 on held-out labels.")
    return 0


def cmd_selftest(args) -> int:
    """Golden-value regression checks so math bugs (e.g. pass^k=2.0) fail loudly."""
    def approx(a, b, tol=1e-9):
        return abs(a - b) <= tol

    checks = []

    def chk(name, ok):
        checks.append((name, bool(ok)))

    # pass@k / pass^k golden values (hand-verified)
    chk("pass@k(8,5,1)=0.625", approx(pass_at_k(8, 5, 1), 0.625))
    chk("pass^k(8,5,1)=0.625", approx(pass_hat_k(8, 5, 1), 0.625))
    chk("pass^k(8,5,5)=1/56", approx(pass_hat_k(8, 5, 5), 1 / 56))
    chk("pass@k(8,5,5)=1.0", approx(pass_at_k(8, 5, 5), 1.0))
    chk("pass^k(8,5,6)=0.0 (c<k)", pass_hat_k(8, 5, 6) == 0.0)
    # the M2 bug class: c>n must RAISE, never return an impossible probability
    raised = False
    try:
        pass_hat_k(5, 10, 1)
    except ValueError:
        raised = True
    chk("pass^k(5,10,1) raises (c>n)", raised)
    # Wilson interval (8/10): ~[0.490, 0.943]
    lo, hi = wilson_interval(8, 10, 0.95)
    chk("wilson(8,10) ~ [0.49,0.94]", 0.485 < lo < 0.495 and 0.940 < hi < 0.948)
    # Cohen's kappa
    chk("kappa(40,6,44,10)=0.68", approx(cohen_kappa(40, 6, 44, 10), 0.68, 5e-3))
    # power round-trip with two_prop_n
    n = two_prop_n(0.8, 0.85, 0.05, 0.8)
    chk("power round-trips to ~0.80", approx(two_prop_power(0.8, 0.85, 0.05, n), 0.80, 0.03))
    # paired tests (H-A): McNemar exact on discordant counts
    chk("mcnemar(0,12)~0.000488 (strict paired regression)", approx(mcnemar_exact(0, 12), 2 / 4096, 1e-6))
    chk("mcnemar(0,0)=1.0 (no discordance)", mcnemar_exact(0, 0) == 1.0)
    chk("mcnemar(5,5)=1.0 (symmetric)", approx(mcnemar_exact(5, 5), 1.0, 1e-9))
    # paired catches what unpaired misses: 12 strict paired wins, 0 losses
    pa = [1.0] * 150 + [0.0] * 50
    pb = list(pa)
    flipped = 0
    for i in range(len(pb)):
        if pb[i] == 0.0 and flipped < 12:
            pb[i] = 1.0
            flipped += 1
    n01 = sum(1 for x, y in zip(pa, pb) if x == 0.0 and y == 1.0)
    n10 = sum(1 for x, y in zip(pa, pb) if x == 1.0 and y == 0.0)
    chk("paired McNemar flags strict win (p<0.05)", mcnemar_exact(n01, n10) < 0.05)
    chk("unpaired permutation misses it (p>0.05)", permutation_pvalue(pa, pb, 2000, 0) > 0.05)

    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"eval_stats selftest: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("ci", help="mean + bootstrap/Wilson CI")
    c.add_argument("--scores"); c.add_argument("--data")
    c.add_argument("--conf", type=float, default=0.95); c.add_argument("--boot", type=int, default=10000)
    c.add_argument("--seed", type=int, default=0); c.set_defaults(func=cmd_ci)

    cm = sub.add_parser("compare", help="delta CI + significance between two sets (paired by default)")
    cm.add_argument("--a"); cm.add_argument("--b")
    cm.add_argument("--a-inline", dest="a_inline"); cm.add_argument("--b-inline", dest="b_inline")
    cm.add_argument("--conf", type=float, default=0.95); cm.add_argument("--boot", type=int, default=10000)
    cm.add_argument("--alpha", type=float, default=0.05); cm.add_argument("--seed", type=int, default=0)
    cm.add_argument("--paired", action="store_true",
                    help="force the paired test (McNemar for binary); requires equal-length aligned inputs")
    cm.add_argument("--unpaired", action="store_true",
                    help="force the unpaired test (only for genuinely independent samples)")
    cm.add_argument("--json", action="store_true", help="emit JSON (paired, significant, p, delta, CI)")
    cm.set_defaults(func=cmd_compare)

    pk = sub.add_parser("passk", help="pass@k and pass^k")
    pk.add_argument("--data"); pk.add_argument("--n", type=int); pk.add_argument("--c", type=int)
    pk.add_argument("--k", default="1", help="comma list, e.g. 1,5,8"); pk.set_defaults(func=cmd_passk)

    pw = sub.add_parser("power", help="two-proportion sample size / power / MDE")
    pw.add_argument("--p0", type=float, required=True); pw.add_argument("--mde", type=float)
    pw.add_argument("--rel", action="store_true", help="treat --mde as relative (fraction of p0)")
    pw.add_argument("--alpha", type=float, default=0.05); pw.add_argument("--power", type=float, default=0.8)
    pw.add_argument("--n", type=int, help="n per group (compute power/MDE instead of n)")
    pw.set_defaults(func=cmd_power)

    jd = sub.add_parser("judge", help="metrics from confusion counts")
    for f in ("tp", "fp", "tn", "fn"):
        jd.add_argument(f"--{f}", type=int, required=True)
    jd.set_defaults(func=cmd_judge)

    st = sub.add_parser("selftest", help="golden-value regression checks (exit 1 on any failure)")
    st.set_defaults(func=cmd_selftest)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
