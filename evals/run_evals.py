#!/usr/bin/env python3
"""run_evals.py — self-test the pm-for-aidlc skill (now a real regression guard).

Auto-verifies, against the REAL scripts:
  - gate_scenarios     6-axis read (by --id or explicit axes, +actuation/overlay) ->
                       expected autonomy_gate mode / controls / blast / gate_metric.
                       Includes NEGATIVE guards that MUST catch C1/C2/M3 if reverted.
  - routing_scenarios  free-text -> expected candidate ids / cluster (and weak-match floor).
  - stats_scenarios    shells eval_stats/judge_validation/contamination and checks exit
                       codes + JSON fields (catches the pass^k / judge-CI bug classes).
  - trigger_scenarios  rule-based proxy via trigger_classifier.py (Tier 1, no API keys).
                       Tier 2 LLM-judge A/B is optional/future (see CONFIG.example.md).

Exit non-zero if any auto-verified assertion fails -> usable as a CI gate.

Usage:
  python evals/run_evals.py
  python evals/run_evals.py --verbose
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.normpath(os.path.join(HERE, "..", "scripts"))
FIXTURES = os.path.join(HERE, "fixtures")

_trigger_mod = None


def _trigger():
    global _trigger_mod
    if _trigger_mod is None:
        sys.path.insert(0, HERE)
        import trigger_classifier as tc  # noqa: E402
        _trigger_mod = tc
    return _trigger_mod


def _run(script: str, args: list, want_json: bool):
    cmd = [sys.executable, os.path.join(SCRIPTS, script)] + args + (["--json"] if want_json else [])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc


def _run_json(script: str, args: list) -> dict:
    proc = _run(script, args, True)
    if not proc.stdout.strip():
        raise RuntimeError(f"{script} produced no stdout (rc={proc.returncode}): {proc.stderr.strip()}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"{script} did not emit JSON. stderr: {proc.stderr.strip()}\nstdout: {proc.stdout[:400]}")


def _gate_args(sc: dict) -> list:
    args = []
    if "task_id" in sc:
        args += ["--id", sc["task_id"]]
    if "axes" in sc:
        a = sc["axes"]
        for flag, key in (("--leverage", "leverage"), ("--eval", "eval"), ("--regr", "regr"),
                          ("--safety", "safety"), ("--fly", "fly")):
            if a.get(key) is not None:
                args += [flag, a[key]]
        if a.get("blast") is not None:
            args += ["--blast", a["blast"]]
    if sc.get("actuation"):
        args += ["--actuation", sc["actuation"]]
    if sc.get("modality"):
        args += ["--modality", sc["modality"]]
    if sc.get("risk_tier"):
        args += ["--risk-tier", sc["risk_tier"]]
    return args


def check_gate(sc: dict, verbose: bool):
    out = _run_json("autonomy_gate.py", _gate_args(sc))
    fails = []
    if "expect_mode" in sc and out["mode"] != sc["expect_mode"]:
        fails.append(f"mode={out['mode']} expected {sc['expect_mode']}")
    if "expect_mode_not" in sc and out["mode"] == sc["expect_mode_not"]:
        fails.append(f"mode={out['mode']} must NOT equal {sc['expect_mode_not']}")
    controls = set(out["controls"])
    for c in sc.get("expect_controls_include", []):
        if c not in controls:
            fails.append(f"missing control {c}")
    for c in sc.get("expect_controls_exclude", []):
        if c in controls:
            fails.append(f"unexpected control {c}")
    if "expect_blast" in sc and out["axes"]["blast"] != sc["expect_blast"]:
        fails.append(f"blast={out['axes']['blast']} expected {sc['expect_blast']}")
    if "expect_gate_metric" in sc and out.get("gate_metric") != sc["expect_gate_metric"]:
        fails.append(f"gate_metric={out.get('gate_metric')} expected {sc['expect_gate_metric']}")
    if verbose:
        print(f"    -> mode={out['mode']} controls={out['controls']} "
              f"blast={out['axes']['blast']} gate_metric={out.get('gate_metric')}")
    return (not fails, fails)


def check_route(sc: dict, default_top: int, verbose: bool):
    top = sc.get("top", default_top)
    out = _run_json("select_task.py", [sc["prompt"], "--top", str(top)])
    ids = [r["id"] for r in out["results"]]
    clusters = [r.get("cluster") or "" for r in out["results"]]
    fails = []
    if "expect_weak_match" in sc and out.get("weak_match") != sc["expect_weak_match"]:
        fails.append(f"weak_match={out.get('weak_match')} expected {sc['expect_weak_match']}")
    wanted = sc.get("expect_task_ids_any", [])
    if wanted and not any(w in ids for w in wanted):
        fails.append(f"none of {wanted} in top-{top} {ids}")
    cc = sc.get("expect_cluster_contains")
    if cc and not any(cc.lower() in c.lower() for c in clusters):
        fails.append(f"no cluster contains {cc!r} in {clusters}")
    ce = sc.get("expect_cluster_excludes")
    if ce and any(ce.lower() in c.lower() for c in clusters):
        fails.append(f"cluster {ce!r} must be ABSENT from top-{top} {clusters}")
    if verbose:
        print(f"    -> top ids={ids} weak={out.get('weak_match')}")
    return (not fails, fails)


def check_trigger(sc: dict, skill_path: str, verbose: bool):
    tc = _trigger()
    tc.load_skill_patterns(skill_path)
    ok, fails = tc.check_scenario(sc)
    if verbose:
        pred = tc.should_trigger(sc["prompt"])
        print(f"    -> predicted should_trigger={pred}")
    return ok, fails


def check_stat(sc: dict, verbose: bool):
    parts = [p.replace("FIXTURES", FIXTURES) for p in sc["cmd"]]
    script, rest = parts[0], parts[1:]
    want_json = "expect_json" in sc
    proc = _run(script, rest, want_json)
    fails = []
    if "expect_exit" in sc and proc.returncode != sc["expect_exit"]:
        fails.append(f"exit={proc.returncode} expected {sc['expect_exit']}")
    if want_json:
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            data = {}
            fails.append("no JSON output")
        for k, v in sc["expect_json"].items():
            if data.get(k) != v:
                fails.append(f"{k}={data.get(k)!r} expected {v!r}")
    if verbose:
        print(f"    -> exit={proc.returncode}")
    return (not fails, fails)


def _run_section(title, scenarios, fn, verbose):
    print(f"\n== {title} ==")
    passed = failed = 0
    for sc in scenarios:
        ok, fails = fn(sc)
        print(f"  [{'PASS' if ok else 'FAIL'}] {sc['id']}")
        for f in fails:
            print(f"        - {f}")
        passed += ok
        failed += (not ok)
    return passed, failed


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--evals", default=os.path.join(HERE, "evals.json"))
    p.add_argument("--skill", default=os.path.normpath(os.path.join(HERE, "..", "SKILL.md")))
    p.add_argument("--top", type=int, default=8, help="default top-N for routing hits")
    p.add_argument("--skip-triggers", action="store_true",
                   help="skip Tier-1 trigger_scenarios auto-verification")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    with open(args.evals, encoding="utf-8") as fh:
        suite = json.load(fh)

    total_pass = total_fail = 0
    pa, fa = _run_section("GATE scenarios", suite.get("gate_scenarios", []),
                          lambda sc: check_gate(sc, args.verbose), args.verbose)
    total_pass += pa; total_fail += fa
    pa, fa = _run_section("ROUTING scenarios", suite.get("routing_scenarios", []),
                          lambda sc: check_route(sc, args.top, args.verbose), args.verbose)
    total_pass += pa; total_fail += fa
    pa, fa = _run_section("STATS scenarios", suite.get("stats_scenarios", []),
                          lambda sc: check_stat(sc, args.verbose), args.verbose)
    total_pass += pa; total_fail += fa

    trig = suite.get("trigger_scenarios", [])
    if trig and not args.skip_triggers:
        pa, fa = _run_section(
            "TRIGGER scenarios (Tier-1 rule proxy)",
            trig,
            lambda sc: check_trigger(sc, args.skill, args.verbose),
            args.verbose,
        )
        total_pass += pa; total_fail += fa
    elif trig and args.skip_triggers:
        print("\n== TRIGGER scenarios (skipped — use trigger_classifier.py or drop --skip-triggers) ==")

    total = total_pass + total_fail
    print(f"\nAUTO-VERIFIED: {total_pass}/{total} passed, {total_fail} failed.")
    return 1 if total_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
