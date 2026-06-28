# Eval & Spec Definition — the hub playbook

*Cluster 2, the center of the wheel · 22 tasks (`AT-08`–`AT-18` + the error-analysis loop `EVL-02`–`EVL-12`) · all `now`. Everything upstream feeds it; everything downstream is gated by it.*

If the SaaS PM's defining artifact was the PRD, the AI PM's is the **eval**: the dataset, the scorers, the judge, the bar. **The eval is the new PRD** — a dataset of real inputs + a task definition + a scoring function does the PRD's old job (state what good means, set the acceptance bar, track progress, prevent regression), except it runs on every commit instead of yellowing in a doc. *The prompt is temporary; the eval is permanent.* Get this cluster right and the rest of the loop has a source of truth; get it wrong and you are shipping on vibes with a dashboard for cover.

## Contents
- [When this applies](#when-this-applies)
- [The tasks](#the-tasks)
- [The error-analysis loop (EVL-02→12)](#the-error-analysis-loop-the-spine)
- [The judge-validation loop](#the-judge-validation-loop)
- [Tools](#tools) · [Pitfalls](#pitfalls) · [Heuristics](#execution-heuristics)

## When this applies

- You are **writing the spec** for any AI behavior — the answer is a rubric + dataset, not a PRD (`AT-08`).
- A green check on a happy-path prompt tempts you to ship — that is **a sample size of one**; build the eval instead.
- You have a pile of production failures and need a **defensible, counted** picture of what's wrong (`EVL-02`–`EVL-05`).
- You need to **trust a number**: write code scorers (`AT-10`/`EVL-07`), then a *validated* judge (`AT-11`/`EVL-08`).
- You are about to **gate a release** and need a pre-committed bar (`AT-16`) and CI (`EVL-12`/`AT-49`).

## The tasks

| id | task | autonomy | eval | regr | flywheel | status |
|---|---|---|---|---|---|---|
| AT-08 | Write the eval rubric or scoring function (the keystone; supersedes `T-046`) | human-led | gated | high | producer | now |
| AT-09 | Curate a golden eval dataset from prod traces | copilot | partial | high | producer | now |
| AT-10 | Design a single-dimension code-based scorer | copilot | gated | med | producer | now |
| AT-11 | Design an LLM-as-judge scorer and rubric | copilot | partial | high | producer | now |
| AT-12 | Calibrate an LLM judge against human labels | copilot | partial | high | producer | now |
| AT-13 | Run an eval-coverage gap analysis | copilot | partial | med | none | now |
| AT-14 | Build slice and segment evals | copilot | gated | med | none | now |
| AT-15 | Version and changelog an eval suite | autonomous | gated | med | none | now |
| AT-16 | Define the release quality bar (eval thresholds) | human-led | gated | high | none | now |
| AT-17 | Author adversarial/regression cases from an incident | copilot | gated | high | producer | now |
| AT-18 | Run the weekly eval-score review | copilot | gated | med | none | now |
| EVL-02 | Pull a smart trace sample for review | autonomous | partial | low | consumer | now |
| EVL-03 | Run an open-coding pass (**the human step**) | human-led | none | low | producer | now |
| EVL-04 | Axial-code notes into a failure taxonomy | copilot | partial | med | producer | now |
| EVL-05 | Quantify failure rates and triage each mode | copilot | partial | med | producer | now |
| EVL-06 | Build a from-prod failure dataset | copilot | partial | high | producer | now |
| EVL-07 | Write a code or assertion grader | copilot | gated | med | producer | now |
| EVL-08 | Build and validate an LLM-judge | copilot | partial | high | producer | now |
| EVL-09 | Recalibrate a judge against fresh labels | copilot | partial | high | producer | now |
| EVL-10 | Generate and validate structured synthetic data | copilot | partial | high | producer | now |
| EVL-11 | Curate golden and adversarial sets; version splits | copilot | partial | high | producer | now |
| EVL-12 | Configure eval-gated CI (assertions then judges) | autonomous | gated | high | none | now |

Per-task steps + full 6-axis read: [`task-catalog.md`](task-catalog.md).

## The error-analysis loop (the spine)

This is the backbone of the whole skill — the disciplined path from "look at your data" to a CI gate. `EVL-01` (instrument) lives in [`measurement-playbook.md`](measurement-playbook.md) because it runs on prod traffic, but it is the precondition for everything here.

```text
EVL-01 instrument (capture inputs+output+tool calls+context+versions+cost)
  → EVL-02 smart, failure-biased trace sample (~100, NOT random)
  → EVL-03 open-code: free-text "first thing that went wrong" (HUMAN, no categories yet)
  → EVL-04 axial-code notes into ~5–10 named failure modes (LLM proposes, human names)
  → EVL-05 quantify rate per mode + triage each → fix / assertion / judge / guardrail
  → EVL-06 build the from-prod failure dataset (label, de-dup, freeze the split)
  → AT-10/EVL-07 code & assertion graders first  →  AT-11/EVL-08 validated judge second
  → AT-16 set the bar  →  EVL-12/AT-49 eval-gated CI
  → (ship)  →  back to EVL-01
```

Why each step is non-negotiable:
- **Sample smart, not random** (`EVL-02`): bias to negative feedback, outliers, and known clusters; random sampling wastes review on the boring middle.
- **Open-code before categories** (`EVL-03`): read the full trace, note the *first upstream* failure in free text. This is the irreducible look-at-your-data step — categories imposed too early blind you to the failure you didn't expect. **Do not delegate this to an LLM.**
- **Axial-code into a taxonomy** (`EVL-04`): the LLM proposes clusters; the human owns the names and boundaries (~5–10 modes, each with a one-line definition).
- **Quantify, then triage** (`EVL-05`): counting turns anecdotes into priorities. Each mode routes to *fix*, *assertion* (`EVL-07`), *judge* (`EVL-08`), or *guardrail* (`AT-65`) — not everything is a "fix."
- **Graders: code first, judge second.** Use a deterministic assertion wherever code can verify it (cheaper, trustworthy, `gated`); reserve the LLM-judge for what code cannot reach (tone, faithfulness) — and only after it is validated.

## The judge-validation loop

An LLM-judge is **untrusted until it agrees with humans** — *who validates the validators?* This is why `AT-11`/`EVL-08` are `partial` coverage until calibrated, and why `AT-12`/`EVL-09` exist.

```text
write judge prompt + rubric (allow an "Unknown" verdict so it can't guess)
  → collect human labels  → run scripts/judge_validation.py
  → it CERTIFIES on the full-set CI lower bound (not a tiny holdout) and prints the exact
    N needed (~70+ for a strong judge at 0.9); the 75/25 split is reported as an overfit check
  → if NOT VALIDATED, refine the prompt on dev and re-measure (then re-validate on fresh labels)
  → schedule recurring recalibration (EVL-09) — the judge drifts as inputs move
```

A perfect point estimate on too few labels is **NOT VALIDATED** (wide CI) — collect the N
the script asks for. `--gate-on point` exists but reverts the safeguard; prefer collecting more.

Run the agreement math through a script, never the model's arithmetic (the parent skill bundles `judge_validation.py`). Allowing an **Unknown** verdict stops a judge from guessing on ambiguous cases.

## Tools

- **Eval platforms / datasets:** Braintrust, Promptfoo, LangSmith, OpenAI Evals, Argilla, Langfuse Datasets.
- **Code scorers:** `autoevals`, Promptfoo, plain Python.
- **Judge + calibration:** Braintrust, Arize Phoenix Evals, DeepEval.
- **Annotation / open-coding:** a custom trace viewer or notebook, spreadsheet, Label Studio/Argilla.

## Pitfalls

- **Delegating the rubric to engineers** — only the PM knows what *good* means for the user (`AT-08` is human-led for the same reason strategy is).
- **Lumping multiple dimensions into one scorer** — you can't localize a regression in a single sinking "quality" number. *One dimension per scorer.*
- **Vibe-checking instead of scoring**; no real-data examples in the rubric or judge prompt.
- **Trusting an unvalidated judge**; labeling and testing on the *same* data; a multi-dimension judge.
- **Imposing categories too early** in coding; noting the *last* error not the *first*; skimming instead of reading.
- **Unfrozen / leaky splits**: over-fitting the set to today's prompt, leakage into training, a stale set that drifts from prod.
- **Setting the bar after seeing results** (`AT-16`) — pre-register it to defeat motivated reasoning; never move the goalposts.
- **Unvalidated synthetic data** (`EVL-10`): contamination in a costume — hand-write the seeds and check leakage/realism.

## Execution heuristics

- *The eval is the new PRD; the prompt is temporary, the eval is permanent.*
- *Score one dimension per scorer, or you cannot localize a regression.*
- *The dataset is the new user research;* a frozen, representative split is what makes Tuesday comparable to Friday.
- *Use code for what code can check;* a deterministic assertion beats any judge.
- *Who validates the validators?* A judge is untrusted until it agrees with humans — allow an "Unknown" verdict.
- *Open coding is the irreducible look-at-your-data step.*
- *Every incident is a free eval case* (`AT-17`) — a fixed bug without a regression test is a bug waiting to recur.
- *Pre-register the bar before the data exists.*

## Hand-offs

Fed by **Discovery** ([`discovery-playbook.md`](discovery-playbook.md)). Gates **Delivery** ([`delivery-playbook.md`](delivery-playbook.md), via `AT-49`/`EVL-12`/`AT-16`) and **Measurement** ([`measurement-playbook.md`](measurement-playbook.md)). The dataset/scorer work is *half of training work* — an RL environment is a dataset + harness + scoring rule (see [`training-flywheel-playbook.md`](training-flywheel-playbook.md)).

**Stressed by every use case** — this is the universal spine (see [`usecase-playbooks.md`](usecase-playbooks.md)).
