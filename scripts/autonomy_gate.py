#!/usr/bin/env python3
"""autonomy_gate.py — turn a task's 6-axis schema read into an execution verdict.

Verdict = one execution MODE + a set of required CONTROLS + human-readable REASONS.

Modes (least -> most human involvement):
  run_unattended      AI runs the task without a human in the per-run loop.
  draft_then_confirm  AI produces the artifact; a human reviews before it takes effect.
  human_led           AI only preps context; a human performs the task.

Controls (the safety envelope; some may already be satisfied by the task itself):
  eval_gate           must pass the eval suite / CI gate.
  build_eval_first    no grader exists yet for a high-regression change — BUILD it first.
  canary_or_shadow    must shadow then canary with online scoring + rollback.
  human_confirm       explicit human sign-off (stronger than passive review).
  provenance_log      log provenance because output feeds the data flywheel.
  safety_gate         must pass the pre-release safety suite (jailbreak/abuse/PII).
  governance:runlayer_managed_only   MCP selection must use governed servers only.

The 6 axes (see references/schema-and-autonomy.md):
  leverage  : autonomous | copilot | human-led      (build order)
  blast     : low | med | high | unknown            (operational irreversibility)
  eval      : none | partial | gated                 (is the output auto-graded?)
  regr      : low | med | high                       (can it silently degrade the distribution?)
  safety    : none | med | high                      (jailbreak/abuse/harm/PII surface)
  fly       : none | consumer | producer             (data-flywheel linkage)

Plus an `actuation` axis (read-only | reversible | irreversible) that distinguishes a
passive monitor from an actuator. A safety:high task NEVER runs unattended unless it is
a read-only monitor with a working gate (the decision stays human for any actuation).
When omitted, `actuation` defaults to `reversible` (actuating); the read-only carve-out
must be ASSERTED via --actuation or the bundle (it is never inferred from low blast).

`blast` resolution for --id: --blast flag → bundled data/aidlc_axes.csv (blast lives
there, not in aidlc_microtasks.csv) → 'unknown'. An UNKNOWN blast never authorizes an
unattended run — pass --blast to authorize one.

Usage:
  python autonomy_gate.py --id AT-56                         # blast from the bundle
  python autonomy_gate.py --id AT-65 --actuation irreversible
  python autonomy_gate.py --leverage autonomous --blast low --eval gated \\
      --regr high --safety high --fly consumer --actuation read-only
  python autonomy_gate.py --id AT-30 --modality multi-agent --risk-tier external-high-stakes
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402

LEVERAGE = {"autonomous", "copilot", "human-led"}
BLAST = {"low", "med", "high"}
EVAL = {"none", "partial", "gated"}
REGR = {"low", "med", "high"}
SAFETY = {"none", "med", "high"}
FLY = {"none", "consumer", "producer"}
ACTUATION = {"read-only", "reversible", "irreversible"}
MODALITY = {"single-turn-rag", "tool-using", "coding", "multi-agent", "voice", "image-gen", "extraction"}
RISK_TIER = {"internal", "external-low-stakes", "external-high-stakes"}

_NORMALIZE = {"": "none", "-": "none", "–": "none", "—": "none", "n/a": "none", "human": "human-led",
              "read_only": "read-only", "readonly": "read-only"}


def _norm(value: str, allowed: set, axis: str) -> str:
    v = (value or "").strip().lower()
    v = _NORMALIZE.get(v, v)
    if v not in allowed:
        raise ValueError(f"invalid {axis}={value!r}; expected one of {sorted(allowed)}")
    return v


def _norm_blast(value: str) -> str:
    v = (value or "").strip().lower()
    v = _NORMALIZE.get(v, v)
    if v in BLAST:
        return v
    if v in ("unknown", "none", ""):
        return "unknown"
    raise ValueError(f"invalid blast={value!r}; expected low|med|high|unknown")


def _bump(value: str, order: list) -> str:
    if value not in order:
        return value
    i = order.index(value)
    return order[min(i + 1, len(order) - 1)]


def verdict(leverage, blast, eval_cov, regr, safety, fly, actuation=None) -> dict:
    """Apply the documented precedence rules. Most-restrictive outcome wins."""
    leverage = _norm(leverage, LEVERAGE, "leverage")
    eval_cov = _norm(eval_cov, EVAL, "eval")
    regr = _norm(regr, REGR, "regr")
    safety = _norm(safety, SAFETY, "safety")
    fly = _norm(fly, FLY, "fly")
    blast = _norm_blast(blast)
    if actuation:
        actuation = _norm(actuation, ACTUATION, "actuation")
    else:
        # The read-only monitor carve-out must be ASSERTED — an explicit --actuation or the
        # bundled catalog (data/aidlc_axes.csv) — never INFERRED from low blast. Inferring
        # read-only from (autonomous + low blast) re-opened the safety hole: an *actuating*
        # safety:high task at low blast (auto-redact PII, auto-quarantine abuse, auto-revoke
        # a token) would wrongly run unattended. The safe default is actuating.
        actuation = "reversible"
    is_read_only = actuation == "read-only"

    reasons = []
    controls = set()

    # 1) Base mode from the build-order axis.
    if leverage == "human-led":
        mode = "human_led"
        reasons.append("leverage=human-led: AI preps context only; a human performs the task.")
    elif leverage == "autonomous":
        mode = "run_unattended"
        reasons.append("leverage=autonomous: candidate for an unattended run.")
    else:
        mode = "draft_then_confirm"
        reasons.append("leverage=copilot: AI drafts; a human owns the decision.")

    # 2) The key inversion: ungraded autonomous output never runs unattended.
    if mode == "run_unattended" and eval_cov in ("none", "partial"):
        mode = "draft_then_confirm"
        reasons.append(
            f"eval={eval_cov}: ungraded/partly-graded output never runs unattended "
            "(the key inversion) -> draft for human review."
        )
    if eval_cov == "gated":
        controls.add("eval_gate")

    # 3) Regression risk -> a gate (+ canary/shadow for shipping-scale changes).
    if regr == "high":
        if eval_cov == "none":
            controls.add("build_eval_first")  # an absent gate cannot be "passed"
        else:
            controls.add("eval_gate")
        if blast in ("med", "high", "unknown"):
            controls.add("canary_or_shadow")
        reasons.append(
            "regr=high: "
            + ("BUILD the grader first (eval=none cannot be gated); " if eval_cov == "none" else "require an eval-gate; ")
            + ("+ canary/shadow before exposure." if "canary_or_shadow" in controls else "CI gate suffices for a low-blast change.")
        )

    # 4) Compounding risk: a safety surface or a flywheel producer.
    # A med safety surface still runs the pre-release safety suite — it just does not force
    # a human into the loop (only safety=high actuating does). This makes the 3-valued axis
    # behave as documented instead of effectively binary.
    if safety == "med":
        controls.add("safety_gate")
        reasons.append("safety=med: require the pre-release safety_gate (no human downgrade at med).")
    if safety == "high" or fly == "producer":
        which = " + ".join(
            ([f"safety={safety}"] if safety == "high" else [])
            + (["flywheel=producer"] if fly == "producer" else [])
        )
        if fly == "producer":
            controls.add("provenance_log")
        if safety == "high":
            controls.add("safety_gate")
        gated_catches = eval_cov == "gated"
        # The ONLY safety:high carve-out: a read-only monitor whose output is graded
        # (e.g. AT-56). Any actuating safety:high task keeps a human in the loop.
        monitor_ok = safety == "high" and is_read_only and gated_catches
        downgrade, msgs = False, []
        if safety == "high" and not monitor_ok:
            downgrade = True
            msgs.append(f"safety=high actuating (actuation={actuation})")
        if fly == "producer" and not gated_catches:
            downgrade = True
            msgs.append("flywheel=producer ungated")
        if downgrade:
            if mode == "run_unattended":
                mode = "draft_then_confirm"
            controls.add("human_confirm")
            reasons.append(f"{' + '.join(msgs)}: the decision stays human (human_confirm) + provenance/safety logging.")
        else:
            reasons.append(f"{which}: read-only monitor / gated producer -> keep mode; add safety/provenance controls.")

    # 5) Operational irreversibility.
    if blast == "high":
        if mode == "run_unattended":
            mode = "draft_then_confirm"
        controls.add("human_confirm")
        reasons.append("blast=high: irreversible/prod/money/legal -> human confirm mandatory even if the drafting is automatable.")

    # 5b) Unknown blast must never bless an unattended run (the C2 fix).
    if blast == "unknown" and mode == "run_unattended":
        mode = "draft_then_confirm"
        controls.add("human_confirm")
        reasons.append("blast=unknown: pass --blast to authorize an unattended run; defaulting to draft_then_confirm.")

    # 6) Final guard: you can only run unattended what you can grade.
    if mode == "run_unattended" and eval_cov != "gated":
        mode = "draft_then_confirm"
        reasons.append("run_unattended requires eval=gated; downgrading to draft_then_confirm.")

    # M1 reminder: the gate trusts the axes you hand it.
    if mode == "run_unattended" and eval_cov == "gated":
        reasons.append("NB: run_unattended trusts that eval=gated is a JUDGE-VALIDATED grader "
                       "(judge_validation.py -> TRUSTED) and that the axes are honest, not self-reported.")

    return {
        "mode": mode,
        "controls": sorted(controls),
        "reasons": reasons,
        "axes": {"leverage": leverage, "blast": blast, "eval": eval_cov,
                 "regr": regr, "safety": safety, "fly": fly, "actuation": actuation},
    }


def apply_overlay(axes: dict, modality, risk_tier):
    """Tighten (never loosen) the axes for the modality x risk-tier overlay."""
    notes, extra = [], set()
    gate_metric = "pass@k"
    a = dict(axes)
    if risk_tier:
        risk_tier = _norm(risk_tier, RISK_TIER, "risk-tier")
        if risk_tier == "external-high-stakes":
            a["safety"] = _bump(a["safety"], ["none", "med", "high"])
            a["blast"] = _bump("high" if a["blast"] == "unknown" else a["blast"], ["low", "med", "high"])
            extra.update({"canary_or_shadow", "safety_gate"})
            gate_metric = "pass^k"
            notes.append("risk-tier external-high-stakes: bumped safety+blast one notch; gate autonomous deploy on pass^k.")
        else:
            notes.append(f"risk-tier {risk_tier}: standard gates.")
    if modality:
        modality = _norm(modality, MODALITY, "modality")
        if modality in ("tool-using", "coding", "multi-agent"):
            notes.append(f"modality {modality}: add tool-call-accuracy + transition-failure evals; bound steps/tokens (AT-27/28).")
        elif modality == "voice":
            notes.append("modality voice: add a latency-budget gate (p50/p95) alongside quality.")
        elif modality == "single-turn-rag":
            notes.append("modality single-turn-rag: split retrieval recall@k vs groundedness (AT-23).")
        else:
            notes.append(f"modality {modality}: scope the eval to the output type.")
    return a, gate_metric, notes, extra


def _resolve_by_id(task_id: str, csv_path):
    """Return (axes_dict_or_None, meta). Prefer the bundle (has blast); fall back to CSV."""
    wanted = task_id.strip().upper()
    bundle = _common.load_axes_bundle()
    if wanted in bundle:
        r = bundle[wanted]
        axes = {k: r.get(k, "") for k in ("leverage", "blast", "eval", "regr", "safety", "fly")}
        # actuation comes from the bundle (read-only is asserted there, e.g. AT-56); a
        # missing/blank value derives to reversible in verdict() — the safe default.
        axes["actuation"] = r.get("actuation", "")
        meta = {"id": r.get("id"), "name": r.get("name"), "cluster": r.get("cluster"),
                "phase_status": r.get("phase_status"), "blast_source": "catalog"}
        return axes, meta
    # fallback: 5-axis Research CSV (blast unknown)
    path = _common.resolve_csv(csv_path, _common.AIDLC_CSV_NAME)
    for row in _common.load_csv(path):
        if (row.get("id") or "").strip().upper() == wanted:
            axes = {"leverage": row.get("ai_leverage", ""), "blast": "unknown",
                    "eval": row.get("eval_coverage", ""), "regr": row.get("regression_risk", ""),
                    "safety": row.get("safety_exposure", ""), "fly": row.get("flywheel_linkage", ""),
                    "actuation": ""}
            meta = {"id": row.get("id"), "name": row.get("name"), "cluster": row.get("cluster"),
                    "phase_status": row.get("phase_status"),
                    "blast_source": "unknown (not in CSV; generate data/aidlc_axes.csv)"}
            return axes, meta
    raise SystemExit(f"task id {task_id!r} not found in the bundle or CSV")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--id", help="AIDLC task id (e.g. AT-08, EVL-12); reads axes from the bundle")
    p.add_argument("--csv", help="path to aidlc_microtasks.csv (override; default bundled/Research)")
    p.add_argument("--leverage", help="autonomous|copilot|human-led")
    p.add_argument("--blast", help="low|med|high (omit = unknown; unknown never authorizes unattended)")
    p.add_argument("--eval", dest="eval_cov", help="none|partial|gated")
    p.add_argument("--regr", help="low|med|high")
    p.add_argument("--safety", help="none|med|high")
    p.add_argument("--fly", help="none|consumer|producer")
    p.add_argument("--actuation", help="read-only|reversible|irreversible (default: derived)")
    p.add_argument("--modality", help="single-turn-rag|tool-using|coding|multi-agent|voice|image-gen|extraction")
    p.add_argument("--risk-tier", dest="risk_tier", help="internal|external-low-stakes|external-high-stakes")
    p.add_argument("--json", action="store_true", help="emit JSON")
    args = p.parse_args(argv)

    meta = {}
    if args.id:
        axes, meta = _resolve_by_id(args.id, args.csv)
        leverage = args.leverage or axes["leverage"]
        eval_cov = args.eval_cov or axes["eval"]
        regr = args.regr or axes["regr"]
        safety = args.safety or axes["safety"]
        fly = args.fly or axes["fly"]
        actuation = args.actuation or axes.get("actuation") or None
        if args.blast:
            blast = args.blast
            meta["blast_source"] = "flag"
        else:
            blast = axes["blast"] or "unknown"
    else:
        missing = [n for n, v in [("--leverage", args.leverage), ("--eval", args.eval_cov),
                                  ("--regr", args.regr), ("--safety", args.safety), ("--fly", args.fly)] if not v]
        if missing:
            p.error(f"without --id you must pass: {', '.join(missing)}")
        leverage, eval_cov, regr, safety, fly = args.leverage, args.eval_cov, args.regr, args.safety, args.fly
        actuation = args.actuation
        blast = args.blast or "unknown"

    try:
        out = verdict(leverage, blast, eval_cov, regr, safety, fly, actuation)
        base_blast = out["axes"]["blast"]  # pre-overlay, for the meta display
        # P5: modality x risk-tier overlay (recompute on tightened axes).
        if args.modality or args.risk_tier:
            tightened, gate_metric, notes, extra = apply_overlay(out["axes"], args.modality, args.risk_tier)
            out = verdict(tightened["leverage"], tightened["blast"], tightened["eval"],
                          tightened["regr"], tightened["safety"], tightened["fly"], out["axes"]["actuation"])
            out["controls"] = sorted(set(out["controls"]) | extra)
            out["gate_metric"] = gate_metric
            out["overlay_notes"] = notes
            out["overlay"] = {"modality": args.modality, "risk_tier": args.risk_tier}
    except ValueError as exc:
        p.error(str(exc))
        return 2

    # P9: surface deferral + MCP governance at decision time.
    if meta:
        if (meta.get("phase_status") or "").lower() == "later":
            out.setdefault("reasons", []).append(
                "CONFIRM training-phase task (phase_status=later): verify you are actually training, "
                "not just orchestrating, before executing (training-flywheel gate).")
        if (meta.get("id") or "").upper() == "AT-26":
            out["controls"] = sorted(set(out["controls"]) | {"governance:runlayer_managed_only"})
            out.setdefault("reasons", []).append(
                "AT-26 MCP selection: Runlayer-managed servers only; flag shadow servers; approval is human-owned.")
        out["task"] = meta

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        if meta:
            print(f"task:     {meta.get('id')}  {meta.get('name')}")
            print(f"          cluster={meta.get('cluster')}  phase_status={meta.get('phase_status')}")
            tightened = out["axes"]["blast"] != base_blast
            print(f"          blast={base_blast} ({meta.get('blast_source')})"
                  + (f" -> {out['axes']['blast']} (overlay)" if tightened else ""))
        a = out["axes"]
        print(f"axes:     leverage={a['leverage']} blast={a['blast']} eval={a['eval']} "
              f"regr={a['regr']} safety={a['safety']} fly={a['fly']} actuation={a['actuation']}")
        if out.get("overlay_notes"):
            print(f"overlay:  modality={args.modality} risk-tier={args.risk_tier} gate_metric={out.get('gate_metric')}")
        print(f"MODE:     {out['mode']}")
        print(f"controls: {', '.join(out['controls']) if out['controls'] else '(none)'}")
        print("why:")
        for r in out["reasons"]:
            print(f"  - {r}")
        for n in out.get("overlay_notes", []):
            print(f"  + overlay: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
