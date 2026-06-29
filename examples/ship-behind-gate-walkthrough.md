# Worked example — shipping a prompt change behind a pre-registered gate

A focused pass through the ship loop: pre-register the bar (AT-16) → gate the CI check
(AT-20) → paired significance → eval gate → GO/NO-GO. Scenario: **we tightened the
support-agent prompt to reduce over-refusal; the candidate wins on aggregate but we
won't merge until the pre-registered bar and regression checks pass.** All commands are
stdlib-only and run from the skill root.

## 1. Pre-register the release bar (AT-16)

Lock thresholds *before* running the candidate — motivated reasoning at ship time is the
enemy:

```bash
$ python scripts/autonomy_gate.py --id AT-16
task:     AT-16  Define the release quality bar (eval thresholds)
          cluster=Eval & Spec Definition (hub)  phase_status=now
          blast=med (catalog)
axes:     leverage=human-led blast=med eval=gated regr=high safety=med fly=none actuation=reversible
MODE:     human_led
controls: canary_or_shadow, eval_gate, safety_gate
why:
  - leverage=human-led: AI preps context only; a human performs the task.
  - regr=high: require an eval-gate; + canary/shadow before exposure.
```
The PM owns and locks the bar (see `assets/eval-spec-template.md` §5). The bundled
fixture bar is minimal:

```json
{"groundedness": {"min_ci_lower": 0.6, "guardrail": true}}
```

**Stopping rule (AT-16):** stop when the bar is written, versioned, and committed before
any candidate scores exist. No moving goalposts after seeing results.

## 2. Gate the prompt-regression CI (AT-20)

A one-line prompt edit is a distribution change — gate it like code:

```bash
$ python scripts/autonomy_gate.py --id AT-20
task:     AT-20  Prompt regression test before merge
          cluster=System & Agent Design  phase_status=now
          blast=low (catalog)
axes:     leverage=autonomous blast=low eval=gated regr=high safety=med fly=none actuation=reversible
MODE:     run_unattended
controls: eval_gate, safety_gate
why:
  - leverage=autonomous: candidate for an unattended run.
  - regr=high: require an eval-gate; CI gate suffices for a low-blast change.
  - NB: run_unattended trusts that eval=gated is a JUDGE-VALIDATED grader (judge_validation.py -> TRUSTED) ...
```
Prompt regression CI runs unattended *because* it is gated and read-only-checkable —
but only if the underlying judge is `TRUSTED` (see
[`judge-validation-walkthrough.md`](judge-validation-walkthrough.md)).

## 3. Is the candidate actually better? (paired, not vibes)

Score the **same frozen eval set** under baseline (A) and candidate (B):

```bash
$ python scripts/eval_stats.py compare --a evals/fixtures/cmp_base.txt --b evals/fixtures/cmp_win.txt
A: n=200 mean=0.7500    B: n=200 mean=0.8100   [PAIRED]
delta (B-A) = +0.0600
paired bootstrap 95% CI of mean delta: [+0.0300, +0.0950]
McNemar exact p (two-sided) = 0.0005  (discordant: B-fixed=12, B-broke=0; alpha=0.05)
verdict: SIGNIFICANT — ship-eligible on this metric.
```
Paired by construction (same cases, two systems). An unpaired test on the same data
(`--unpaired` → p≈0.18) would miss a real win — always pair eval A/B.

**Stopping rule:** report "X ± Y (n=…, p=…)" from the script; never eyeball a delta.

## 4. Ship gate — GO (bar passes, no regression)

Run the pre-registered gate against candidate results, baseline, and bar:

```bash
$ python scripts/eval_gate.py \
    --results evals/fixtures/gate_base.jsonl \
    --bar evals/fixtures/gate_bar.json \
    --baseline evals/fixtures/gate_base.jsonl
  [PASS] groundedness [guardrail]: ci_lower 0.6857 >= 0.6

VERDICT: GO
```
Exit code 0 — merge-eligible on this gate. Guardrail metrics surface first; the gate uses
the **CI lower bound**, not the point estimate.

## 5. Ship gate — NO-GO (paired regression)

The bundled candidate fixture (`gate_cand.jsonl`) improves nothing meaningful but
**breaks 12 cases** that baseline passed — the gate catches it even though aggregate
CI might look fine:

```bash
$ python scripts/eval_gate.py \
    --results evals/fixtures/gate_cand.jsonl \
    --bar evals/fixtures/gate_bar.json \
    --baseline evals/fixtures/gate_base.jsonl
  [PASS] groundedness [guardrail]: ci_lower 0.6228 >= 0.6
  [FAIL] groundedness: regression delta=-0.06 (p=0.0005, case_id)

VERDICT: NO-GO
  -> do not ship: a gated metric, a slice floor, or a regression failed.
```
A win on the bar is not enough — significant paired regression vs baseline is an
automatic NO-GO.

## 6. Ship gate — NO-GO (coverage gap)

A candidate that **drops the hard cases** it fails cannot game its way to GO:

```bash
$ python scripts/eval_gate.py \
    --results evals/fixtures/gate_subset.jsonl \
    --bar evals/fixtures/gate_bar.json \
    --baseline evals/fixtures/gate_base.jsonl
  [PASS] groundedness [guardrail]: ci_lower 0.7348 >= 0.6
  [FAIL] groundedness: candidate dropped 12 baseline case_id(s) (coverage gap — cherry-picked/errored cases hide regressions): [188, 189, 190, ...]

VERDICT: NO-GO
  -> do not ship: a gated metric, a slice floor, or a regression failed.
```
Subset cherry-picking is a silent false GO without the coverage check.

---

**The thread:** AT-16 locks the bar before data exists; AT-20 runs the check unattended
in CI; `eval_stats.py compare` proves significance; `eval_gate.py` is the final GO/NO-GO
on CI lower bound + worst slice + paired regression + coverage. Every number comes from a
script — never a vibe.
