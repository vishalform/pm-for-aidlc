# Worked example — shipping a support-agent change, end to end

A concrete pass through the skill: route → gate → loop → stats → ship gate → monitor.
Scenario: **our support agent sometimes refuses valid requests and sometimes invents a
refund policy. We want to fix it and ship safely.** All commands are stdlib-only and run
from the skill root.

## 1. Route the request

```bash
$ python scripts/select_task.py "our agent hallucinated a refund policy in production" --top 3
```
Routes to the trace/feedback-mining and groundedness tasks (Discovery + Measurement). The
agent reads only the matching playbook (`references/discovery-playbook.md`).

## 2. Grow the eval from real traces (don't author it upfront)

Run the **eval spine**: instrument → smart-sample failure-biased traces → open-code by hand
(human) → axial-code into a taxonomy → quantify → stop at saturation (~20 traces, no new
failure mode). Two modes emerge: *over-refusal* and *hallucinated policy*. Each becomes a
graded case. The rubric is the PM's to own:

```bash
$ python scripts/autonomy_gate.py --id AT-08      # "write the eval rubric"
MODE:     human_led
controls: canary_or_shadow, eval_gate, provenance_log, safety_gate
```
The eval is the PRD here — only the PM knows what "good" means, so the gate keeps it human.

## 3. Validate the LLM judge before trusting it

The "hallucinated policy" check is subjective, so it needs a judge — and the judge is
untrusted until it agrees with humans. Collect binary labels and validate:

```bash
$ python scripts/judge_validation.py --labels labels.csv
VERDICT: NOT VALIDATED
  -> UNDER-POWERED: the point estimate meets the bar but the CI lower bound does not.
     Collect ~70 balanced labels (a perfect judge needs that many to certify) ...
```
Collect more, re-run, and only ship the judge when it reads `TRUSTED` on the full-set CI
lower bound. (A confidently-wrong judge is worse than no judge.)

## 4. Change the prompt behind a gate

A prompt edit is a distribution change — version it and gate it like code:

```bash
$ python scripts/autonomy_gate.py --id AT-20      # "prompt regression CI"
MODE:     run_unattended
controls: eval_gate, safety_gate
```
The prompt-regression CI is autonomous *because* it is gated and read-only-checkable.

## 5. Is the candidate actually better? (paired, not vibes)

Score the **same frozen eval set** under the baseline prompt (A) and the candidate (B):

```bash
$ python scripts/eval_stats.py compare --a base_scores.txt --b cand_scores.txt
A: n=200 mean=0.7500    B: n=200 mean=0.8100   [PAIRED]
delta (B-A) = +0.0600
paired bootstrap 95% CI of mean delta: [+0.0300, +0.0950]
McNemar exact p (two-sided) = 0.0005  (discordant: B-fixed=12, B-broke=0; alpha=0.05)
verdict: SIGNIFICANT — ship-eligible on this metric.
```
The paired test catches a real win the unpaired test would miss (`--unpaired` → p=0.18, "not
significant"). Same logic guards regressions.

## 6. Ship gate (pre-registered bar)

Gate the release on the bar you locked *before* seeing results — CI lower bound, worst slice,
and a paired regression check vs the last-good baseline:

```bash
$ python scripts/eval_gate.py --results cand.jsonl --bar bar.json --baseline base.jsonl
  [PASS] groundedness [guardrail]: ci_lower 0.94 >= 0.92
  [PASS] refusal_calibration: ci_lower 0.88 >= 0.85
VERDICT: GO
```
If the candidate had quietly dropped the hard cases it fails, the gate would catch the
**coverage gap** and return NO-GO — a subset can't game its way to a pass.

## 7. Monitor online (the one safe unattended carve-out)

Groundedness is the trust metric. A read-only, judge-validated monitor is the *only*
`safety:high` task that runs unattended:

```bash
$ python scripts/autonomy_gate.py --id AT-56
MODE:     run_unattended
controls: eval_gate, safety_gate     # actuation=read-only (asserted in the bundle)
```
Alert on the CI **lower** bound, not the point estimate. When a regression appears, RCA it
(eliminate the judge first), add the case to the dataset, and the loop closes back to step 2.

---

**The thread:** every step is graded before it is trusted, every number comes from a script,
and the autonomy of each step is decided by what you can grade — not by how reversible it looks.
