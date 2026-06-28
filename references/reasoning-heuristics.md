# Reasoning Heuristics — the non-obvious mental models for AIDLC work

These are the `reasoning_model` one-liners distilled into execution-time heuristics.
They exist so the agent can **improvise correctly** on tasks not literally in the
catalog: compose the closest invariant + overlay, then reason from these. Each is a
sharp, non-obvious claim — not a procedure. Procedures live in the cluster playbooks.

## Contents
- [0. The spine (load-bearing, applies everywhere)](#0-the-spine)
- [1. Discovery & capability mapping](#1-discovery--capability-mapping)
- [2. Eval & spec definition (the hub)](#2-eval--spec-definition)
- [3. System & agent design](#3-system--agent-design)
- [4. Data & training flywheel](#4-data--training-flywheel)
- [5. Delivery & release](#5-delivery--release)
- [6. Measurement & monitoring](#6-measurement--monitoring)
- [7. Safety, red-teaming & guardrails](#7-safety-red-teaming--guardrails)
- [8. Inference economics & portfolio](#8-inference-economics--portfolio)
- [9. Commercial & stakeholder](#9-commercial--stakeholder)
- [10. Diagnostic frames](#10-diagnostic-frames)
- [11. Stats heuristics (always via scripts)](#11-stats-heuristics)
- [12. Improvising on a novel request](#12-improvising-on-a-novel-request)

---

## 0. The spine

- **The eval is the new PRD.** The prompt is temporary; the eval is permanent. The scoring function is the spec, the dataset is the user research, the flywheel is the sprint cycle.
- **But the eval is *grown*, not authored upfront.** Write evaluators for errors you *discover* in real traces, not errors you imagine. Looking at your data is the irreducible step; criteria drift *is* the process — grading is what lets you define the criteria.
- **A passing eval is necessary, not sufficient** — the judge can be confidently wrong. Validate the validator.
- **You can only safely automate what you can grade.** Ungraded autonomous output never runs unattended, regardless of how reversible it looks.
- **Quality is a distribution, not a point.** "It worked when I tried it" is a sample size of one. Read slices and confidence intervals, never just the average.
- **Production is the next dataset.** Measurement is the next Discovery; the lifecycle is a loop, not a pipeline.
- **Reversibility ≠ safety.** A one-line prompt edit is low operational blast and high distributional blast. The dominant risk is *undetectable wrongness*.

## 1. Discovery & capability mapping

- Failing traces are the roadmap; **cluster into patterns, never react to one dramatic trace.** The production distribution always differs from staging.
- A thumbs-down is **a labeled datapoint, not a complaint** — reproduce before believing, capture before it decays.
- A new model is an **opportunity surface, not just a swap** — probe for net-new capability before re-pricing the roadmap.
- **Ungraded behavior is unmanaged behavior;** coverage gaps are where silent regressions hide.
- Your eval set is the only fair comparison — **public leaderboards measure someone else's task.**
- A flaky tool quietly caps agent quality; **tool-surface reliability is a product metric**, not just an ops one.

## 2. Eval & spec definition

- **One dimension per scorer** or you can't localize a regression. Avoid the "God Evaluator" scoring 5–10 things at once.
- **Use code for what code can check** (schema, exact-match, execution, tool-args); reserve the LLM-judge for what needs judgment (tone, faithfulness, helpfulness). Deterministic graders where possible, judges where necessary.
- The dataset is the new user research; a **frozen, representative split** is what makes scores comparable over time.
- A **vague judge prompt produces vague scores;** give the judge examples, chain-of-thought, the full transcript, a pinned version, and **a way out (`Unknown`)** so it doesn't guess.
- Prefer **binary pass/fail over Likert 1–5** — binary forces clearer thinking; decompose progress into multiple binary checks.
- The judge is **an instrument that needs re-zeroing** — calibrate against human labels, then recalibrate on a cadence (drift is silent).
- **Pre-register the quality bar before the data exists** to prevent motivated reasoning at ship time.
- Every incident is a free eval case; **a fixed bug without a regression test is a bug waiting to recur.**
- An aggregate pass can hide a broken slice; don't optimize for 100% — that means the eval is too easy.

## 3. System & agent design

- **Prompts are code** — version them, link each to its governing eval, never edit prod prompts in place.
- A one-line prompt edit **is a distribution change;** gate it like code.
- Context is a scarce, paid resource; **more tokens is not more quality past the point of dilution.**
- Retrieval quality caps answer quality; **a wrong chunk is a confident wrong answer.** Separate retrieval failures (recall@k) from generation failures (groundedness) or you'll tune the wrong half.
- **The tool description is a prompt;** design for the model's job and make errors part of the contract.
- An **MCP server is third-party code in your agent loop** — unvetted servers bypass security and audit controls (governance, not just reliability).
- **The harness is the product;** an agent with no stop condition fails unsafely and unbounded loops burn money.
- Choose the model on **your** task, not a leaderboard; **the cheapest model that clears your bar wins.** Routing is the cost-quality lever — most traffic is easy, so don't pay frontier prices for it.
- An optimizer that overfits the dev set is **a regression in disguise** — always validate the gain on a holdout.
- Memory is state with privacy and staleness risk; **stale or leaked memory is worse than none.**

## 4. Data & training flywheel

> Most of this cluster is `phase_status: later` for an orchestrator. Confirm "are we actually training?" before executing. The parts that pay off now: flywheel-wiring (AT-48), feedback capture (AT-60), synthetic eval data (AT-46/EVL-10), contamination checks (AT-47).

- An **RL environment and an agent eval are the same object** — dataset + harness + scoring. Build once, use for both.
- **Any reward will be gamed;** the question is whether you find the exploit before your users do. Verifiable rewards (RLVR) are powerful and brittle — the reward is a spec the policy attacks relentlessly.
- Preference data is **the product spec encoded as comparisons;** garbage pairs train a garbage reward. Inconsistent raters train a noisy reward — agreement is the quality floor.
- A **bad label compounds** through the reward into the policy into future labels — audit before you train, not after.
- **Unvalidated synthetic data is contamination wearing a costume** — validate diversity and leakage before use.
- A contaminated eval **flatters you into shipping a worse model** — clean separation is non-negotiable.
- Fine-tuning is the **last resort, not the first** — for an orchestrator the answer is usually prompt/RAG until evals prove otherwise.
- SFT data quality sets the ceiling; **a few hundred excellent examples beat a noisy pile.**

## 5. Delivery & release

- **The eval is the unit test for a non-deterministic system** — if it's not in CI, it's not a gate.
- A **model release is a bundle, not a model id** — pin model + prompt + tools + config so rollback is one click.
- A model change is **a prod change** — ramp it behind online evals, because offline scores never fully predict prod.
- **Reversible mitigation first:** a clean pinned bundle makes rollback a one-click decision under pressure.
- Ship only when **the eval, the safety gate, and the rollback all hold** — one unchecked critical gate is a no-go.
- Offline eval is necessary but not sufficient; the **prod distribution decides** — confirm online before full rollout, and don't peek.

## 6. Measurement & monitoring

- Offline evals catch known failures; **online scoring catches the distribution shift you didn't anticipate.** Score reference-free in prod.
- **Groundedness is the trust metric** — for a grounded product, an ungrounded claim is a sev incident, not a quirk ("every number traces to a tool").
- Models drift even when you change nothing (provider updates, input shift) — **watch the distribution, not a point.**
- A score drop has **four suspects — model, judge, data, system** — eliminate the judge first, because it's the cheapest way to be fooled.
- When offline says good and prod says bad, **the eval set is unrepresentative** — the gap is a dataset bug, not a model bug.
- A drop-off in an agent is **a transition failure, not a funnel step** — the transition matrix shows which hand-off actually breaks.
- **Capture the edit, not just the thumbs** — the edit shows the fix. Human feedback is the cheapest label source.
- The three axes (quality, cost, latency) trade off — **you can't manage quality without seeing its cost beside it.**

## 7. Safety, red-teaming & guardrails

- You red-team so you **find the jailbreak before users do;** absence of a campaign is not absence of vulnerability.
- **Jailbreak resistance is a measurable, regressable property** — if it's not in an eval, it will silently regress.
- **Guardrails are policy made executable;** an untested filter is decorative. Guardrails are inline/synchronous/fast/deterministic; evaluators run after and can be heavier — almost never use a slow judge as a synchronous guardrail.
- **Over-refusal is a real product failure** — safety and helpfulness trade off and the balance is a product call (test on paired benign/harmful sets).
- **Contain before you diagnose** — a harmful output in prod is reversible only forward, via filter or rollback.
- Safety is a **release gate, not a launch-day checklist** — a failed safety floor is a hard no-go.

## 8. Inference economics & portfolio

- For an AI product, **inference is COGS** — a feature that's loved and unprofitable per call is a problem, not a win.
- Model choice is **a portfolio decision with lock-in risk** — don't single-source a capability you can't switch.
- The **eval roadmap is the product roadmap** — you can only build what you can grade.
- The flywheel's fuel is user data; **using it without rights is a legal and trust failure that compounds.**

## 9. Commercial & stakeholder

- **Price the unit that tracks both value and cost** — flat pricing on metered COGS is how AI products lose money at scale.
- **Sell the evaluated capability, not the hype** — overclaiming is a trust debt you pay in churn.
- For AI products, **"half of it doesn't work" is a capability limit, not a backlog item** — classify model-limit vs product-gap before committing.
- The board cares about **quality trend, unit economics, and safety exposure** — show the eval curve, not feature counts.
- Reframe escalations from "it's broken" to **"here is the measured reliability and the fix path"** — non-determinism needs expectation-setting, not defensiveness.
- The **acceptance/edit rate is the truest adoption signal** for an AI feature — it shows whether users trust the output.

## 10. Diagnostic frames

- **The Three Gulfs** (where does a failure live?): *Comprehension* (you can't see your data at scale → look at it), *Specification* (intent vs prompt → fix the prompt/context), *Generalization* (good prompt, unreliable across inputs → architectural fix: RAG, decomposition, routing, fine-tune). Spec problems need better prompts; generalization problems need architecture. Don't misdiagnose one as the other.
- **The RAG triad** (localize hallucination): *context relevance* (query→context), *groundedness* (context→answer), *answer relevance* (query→answer). Debug retrieval first (IR metrics), then generation (validated judge).
- **Error-analysis loop**: collect ~100 failure-biased traces → open-code (free-text, first upstream failure, human-owned) → axial-code into ~5–10 named modes (LLM proposes, human validates) → quantify → route each mode to fix / assertion / judge / guardrail → repeat. Stop at saturation (~20 traces, no new mode).
- **Transition-failure matrix** (multi-step agents): rows = last-success state, cols = first-failure state; the hotspot is where to invest.

## 11. Stats heuristics

Route every number through `scripts/` — never the model's arithmetic.

- **Alert on the CI lower bound, not the point estimate** (`eval_stats.py ci`) — it's the difference between a real alert and noise.
- **One run gives ~zero signal** for a stochastic agent — run k times. `pass@k` = capability/coverage (dev, human-in-loop); **`pass^k` = reliability — gate autonomous/high-stakes here** (`eval_stats.py passk`). The gap between them is the production trap.
- **Don't claim a difference that isn't significant** (`eval_stats.py compare`) — "the score went up by X ± Y (n=…, p=…)", not "the score went up".
- **Size the experiment before running it** (`eval_stats.py power`) — an underpowered slice can't catch the regression you care about.
- **A judge is untrusted until its TPR & TNR *CI lower bounds* clear the bar on held-out labels** (`judge_validation.py`) — a perfect point estimate on a tiny test set is still NOT VALIDATED; a confidently-wrong judge is worse than no judge.
- **Exact-match misses near-dupes and template leakage** (`contamination_check.py`) — check char-shingle *and* token-Jaccard overlap, not just hashes.
- **A gate gates on the CI lower bound and the worst slice** (`eval_gate.py`) — an aggregate pass can hide a broken slice; `regr:high + eval:none` means *build the grader first*, not "pass the absent gate".
- **Inference is COGS; model the tail** (`cost_calc.py`) — a flat price on metered cost can invert margin as usage grows.

## 12. Improvising on a novel request

When a request doesn't map cleanly to a catalog task:

1. **Name the closest invariant** (use `select_task.py` to find candidates) and the **modality × risk-tier overlay** (schema-and-autonomy §8).
2. **Compose, don't force-fit.** State explicitly: "this is closest to AT-XX, specialized for `<modality>` at `<risk-tier>`."
3. **Reason from the spine (§0) + the relevant cluster heuristics** above — they generalize past the literal catalog.
4. **Run the 6-axis read through `autonomy_gate.py`** even for a composed task (estimate axes; supply `--blast`).
5. **Escape hatch:** if the composition is a poor fit, or `safety`/`blast` is high and you're unsure, say so and ask the human — don't fabricate a procedure. A wrong-but-confident plan on a high-stakes task is the failure mode to avoid.
