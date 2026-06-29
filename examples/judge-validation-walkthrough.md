# Worked example — validating an LLM judge before trusting it

A focused pass through the judge-validation loop: route → gate (AT-11) → gate (AT-12) →
`judge_validation.py` → TRUSTED. Scenario: **our groundedness judge scores look fine on
dev, but we won't wire it into CI until it agrees with human labels.** All commands are
stdlib-only and run from the skill root.

## 1. Route the request

```bash
$ python scripts/select_task.py "design an llm-as-judge scorer for groundedness" --top 3
query: 'design an llm-as-judge scorer for groundedness'  ->  top 3 candidates

[ 31.2] AT-11   Design an LLM-as-judge scorer and rubric
         cluster=Eval & Spec Definition (hub)  status=now
         axes: copilot · blast:med · eval:partial · regr:high · safety:med · fly:producer
[ 25.8] AT-56   Monitor hallucination and groundedness rate
         ...
[ 25.2] EVL-08  Build and validate an LLM-judge
         ...
```
AT-11 is the design task; EVL-08 is the deeper eval-spine variant. Read
`references/eval-spec-playbook.md` — the agent pulls only that cluster playbook.

## 2. Gate AT-11 (draft the judge — human owns criteria)

Designing a judge is `eval=partial` until calibrated. The gate keeps it human-led:

```bash
$ python scripts/autonomy_gate.py --id AT-11
task:     AT-11  Design an LLM-as-judge scorer and rubric
          cluster=Eval & Spec Definition (hub)  phase_status=now
          blast=med (catalog)
axes:     leverage=copilot blast=med eval=partial regr=high safety=med fly=producer actuation=reversible
MODE:     draft_then_confirm
controls: canary_or_shadow, eval_gate, human_confirm, provenance_log, safety_gate
why:
  - leverage=copilot: AI drafts; a human owns the decision.
  - regr=high: require an eval-gate; + canary/shadow before exposure.
  - flywheel=producer ungated: the decision stays human (human_confirm) + provenance/safety logging.
```
Draft the judge prompt with good/bad examples and an `Unknown` verdict option. Pin the
version — a judge prompt is product knowledge, not throwaway engineering.

**Stopping rule (AT-11):** stop when you have a pinned one-dimension judge prompt with
rubric examples; do not collect labels or trust scores until AT-12.

## 3. Gate AT-12 (calibrate against human labels)

Once the judge exists, route to calibration:

```bash
$ python scripts/select_task.py "validate our llm judge against human labels" --top 3
[ 32.8] EVL-08  Build and validate an LLM-judge
[ 32.6] AT-12   Calibrate an LLM judge against human labels
         ...

$ python scripts/autonomy_gate.py --id AT-12
task:     AT-12  Calibrate an LLM judge against human labels
          ...
MODE:     draft_then_confirm
controls: canary_or_shadow, eval_gate, human_confirm, provenance_log, safety_gate
```
Collect human labels on a balanced sample (target 50–100 binary labels). The PM owns
ground truth; the agent runs the agreement math.

**Stopping rule (AT-12 loop):** stop only when `judge_validation.py` returns `TRUSTED` on
the **full-set CI lower bound** — not when the point estimate looks good.

## 4. First validation pass — NOT VALIDATED (under-powered)

Run against the bundled under-powered fixture (50 perfect labels — still too few to
certify):

```bash
$ python scripts/judge_validation.py --labels evals/fixtures/judge_underpowered.csv
labels: 50 total  (full-set certification; dev=38/test=12 split reported as an overfit check; seed=0, abstain=exclude)

FULL-SET metrics (the certification estimate):
  coverage=1.0000  abstain=0  (tp=25 fp=0 tn=25 fn=0)
  TPR=1.0000  CI=[0.867, 1.000]
  TNR=1.0000  CI=[0.867, 1.000]
  precision=1.0000  accuracy=1.0000  kappa=1.0000

VERDICT: NOT VALIDATED  (need TPR & TNR CI lower bound >= 0.9 on the full labeled set)
  -> UNDER-POWERED: the point estimate meets the bar but the CI lower bound does not.
     Collect ~70 balanced labels (a perfect judge needs that many to certify), or --gate-on point at your own risk.
```
A perfect-looking judge on 50 labels is **not** trusted — the Wilson CI lower bound
(0.867) sits below the 0.9 bar. Collect more labels; do not `--gate-on point` to force
a pass.

## 5. Second validation pass — TRUSTED

After collecting ~100 balanced labels (use your own CSV with the same `id,human,judge`
columns, or the bundled trusted fixture):

```bash
$ python scripts/judge_validation.py --labels evals/fixtures/judge_trusted.csv
labels: 100 total  (full-set certification; dev=75/test=25 split reported as an overfit check; seed=0, abstain=exclude)

FULL-SET metrics (the certification estimate):
  coverage=1.0000  abstain=0  (tp=50 fp=0 tn=50 fn=0)
  TPR=1.0000  CI=[0.929, 1.000]
  TNR=1.0000  CI=[0.929, 1.000]
  precision=1.0000  accuracy=1.0000  kappa=1.0000

VERDICT: TRUSTED  (need TPR & TNR CI lower bound >= 0.9 on the full labeled set)
```
Now the judge is eligible for CI gating and online monitoring. Schedule recurring
recalibration (`EVL-09` / AT-12) — a judge drifts as the input distribution moves.

---

**Pitfall — tuning on the labels you certify:** if you iterated the judge prompt on the
same items you are certifying, the full-set CI is optimistic. Hold out fresh labels or
re-validate after prompt changes.

**The thread:** AT-11 produces an untrusted instrument; AT-12 certifies it on human
ground truth with explicit stopping at `TRUSTED`. Every `run_unattended` gate downstream
assumes this step happened.
