---
name: pm-for-aidlc
version: 1.0.0
license: MIT
description: >-
  Use when doing AI product management on an AI system itself — writing or
  debugging evals, prompts, agent/RAG/tool design, model selection and routing,
  the data flywheel, eval-gated shipping, online quality/groundedness/drift
  monitoring, safety/red-teaming, or inference cost and unit economics. Triggers:
  AI PM, AIDLC, eval-driven development, "the eval is the PRD", write or calibrate
  an LLM-as-judge, trace/failure-mode mining, prompt regression in CI, canary or
  rollback a model/prompt, hallucination/groundedness, pass@k vs pass^k,
  cost-per-task, model bake-off, RLHF/preference data/reward models, RL
  environments, jailbreak/guardrails, or executing AT-/EVL- AIDLC micro-tasks.
  Use even when the user describes this work without naming "eval" or "AIDLC". NOT for
  classic SaaS PM (seat pricing, signup funnels, sprint hygiene), AWS's "AI-DLC" (using
  AI to ship ordinary software faster), or model-agnostic product analytics.
---

# PM for AIDLC

The operator skill for an **AI product manager** whose product *is* the AI system
(model, agent loop, context/RAG, tools/MCP, routing, inference). It turns the AIDLC
micro-task library (`AT-01..AT-86` + `EVL-01..EVL-16`) into executable behavior:
**route to the right playbook, read the task's risk schema to decide how autonomously
to run it, run the eval-driven loop, and do all stats through scripts.**

Core principle: **the eval is the new PRD — but it is grown from looking at real
traces, not authored upfront. You can only safely automate what you can grade.**

## When to use
- Writing/curating an eval, dataset, rubric, scorer, or LLM-judge (and validating it).
- Mining traces/feedback into failure modes; investigating a quality/eval-score regression.
- Designing or changing a prompt, RAG pipeline, tool/MCP, agent loop, or routing policy.
- Shipping a model/prompt change (CI gate, canary/shadow, rollback) or monitoring it online.
- Safety/red-team/guardrail work; inference cost/unit-economics; AI roadmap and commercial calls.
- Any request that maps to an `AT-`/`EVL-` task, even phrased in plain language.

## When NOT to use
- Classic SaaS PM work with no AI-system component (pricing a seat, generic funnels, sprint hygiene) → use the classic task library, not this skill.
- "Use AI to build ordinary software faster" (AWS's *AI-DLC*) — that's a different acronym/problem.
- Pure data analysis with no model-quality angle.

## How to use it (execution-time orchestration)

```
request
  │
  ├─(1) ROUTE:   match to a cluster → read that references/*-playbook.md
  │              (find candidate task ids: scripts/select_task.py)
  │
  ├─(2) GATE:    read the 6-axis schema → scripts/autonomy_gate.py
  │              → run_unattended | draft_then_confirm | human_led (+ controls)
  │
  ├─(3) OVERLAY: compose modality × risk-tier → set how hard the gates are
  │
  ├─(4) LOOP:    run the cluster's loop (eval spine / judge-validation / ship /
  │              failure-recovery) with explicit stopping rules
  │
  ├─(5) STATS:   every number via scripts/ (CIs, pass^k, judge TPR/TNR, power)
  │
  └─(6) TOOLS:   pick by fit+cost; MCP only through the governance gate
```

If the request fits no task: **compose the closest invariant + overlay and say so**
(see step 7) — do not force a bad fit.

### Examples (focused walkthroughs)

| Walkthrough | When to read it |
|---|---|
| [`examples/worked-example.md`](examples/worked-example.md) | Full end-to-end pass (support-agent change) |
| [`examples/judge-validation-walkthrough.md`](examples/judge-validation-walkthrough.md) | AT-11/AT-12 judge design + calibration → `TRUSTED` |
| [`examples/ship-behind-gate-walkthrough.md`](examples/ship-behind-gate-walkthrough.md) | AT-16 bar + AT-20 CI + `eval_gate.py` GO/NO-GO |

### (1) Route by cluster → playbook

Match the work to a cluster, then read **only** that playbook (progressive disclosure).
Use `scripts/select_task.py "<request>"` to get candidate task ids first.

| If the work is about… | Cluster (`aidlc_phase`) | Read this reference |
|---|---|---|
| Trace/feedback mining, capability probes, eval-gap maps | Discovery & Capability Mapping | `references/discovery-playbook.md` |
| Writing evals, datasets, scorers, judges, thresholds (the hub) | Eval & Spec Definition | `references/eval-spec-playbook.md` |
| Prompts, context/RAG, tools/MCP, agent loop, model bake-off/routing | System & Agent Design | `references/system-agent-playbook.md` |
| RLHF, preference data, reward models, RL envs, SFT, synthetic data | Data & Training Flywheel | `references/training-flywheel-playbook.md` |
| Eval-gated CI, release bundles, canary/shadow, go/no-go, rollback | Delivery & Release | `references/delivery-playbook.md` |
| Online scoring, groundedness, drift, RCA, cost/latency/quality | Measurement & Monitoring | `references/measurement-playbook.md` |
| Red-team, jailbreak corpus, guardrails, refusal calibration, incidents | Safety (substrate A) | `references/safety-substrate.md` |
| Cost-per-task, model portfolio, eval/capability roadmap, data rights | Inference Economics (substrate B) | `references/inference-economics.md` |
| Pricing, GTM, enablement, win-loss, exec/board updates, trust narrative | Commercial & Stakeholder | `references/commercial-playbook.md` |
| Per-task detail (steps, tools, pitfalls, axes) for any `AT-`/`EVL-` id | (all clusters) | `references/task-catalog.md` |
| Mapping a whole use case (support agent, text-to-SQL, RAG, coding…) | 16 use cases | `references/usecase-playbooks.md` |

Output templates (eval-spec, experiment readout, trace-coding sheet, autonomy-gate
decision record, use-case eval plan) live in `assets/`.

**Safety routing (do not mis-send incidents):** incident language routes to the Safety
substrate even without the word "safety" — *prompt injection* / "ignore your
instructions" / *jailbreak* / *leaking PII* / *harmful output* → `references/safety-substrate.md`
(AT-63/64/65/66/67/68), **not** a model bake-off or a Delivery A/B. `select_task.py` encodes
this concept prior; trust it over surface keywords (and "guardrails" + jailbreak/abuse ⇒ AT-65,
not the business-guardrails A/B AT-52).

### (2) Gate by the 6-axis schema (the autonomy decision)

Every task carries `leverage · blast · eval · regr · safety · fly` (+ an `actuation`
read). **Do not eyeball the autonomy call — run the script:**

```bash
python scripts/autonomy_gate.py --id AT-56                   # all 6 axes incl. blast from the bundle
python scripts/autonomy_gate.py --id AT-65 --actuation irreversible
python scripts/autonomy_gate.py --leverage autonomous --blast low --eval gated \
    --regr high --safety high --fly consumer --actuation read-only   # fully explicit
```

It returns one **mode** + required **controls** + reasons. The rules it encodes
(full table in `references/schema-and-autonomy.md`):

- **Ungraded autonomous output never runs unattended** — `eval ∈ {none,partial}` → `draft_then_confirm`. (The key inversion.)
- **`regr=high` → eval-gate** (+ canary/shadow if `blast ≥ med`); if `eval=none`, `build_eval_first` (you cannot pass an absent gate).
- **`safety=med` → safety gate** (run the safety suite; no human downgrade). **`safety=high` actuating → human confirm + safety gate** — *the decision stays human*. The ONLY carve-out that runs unattended is a **read-only, gated monitor** whose read-only is *asserted* (bundle / `--actuation`, e.g. AT-56) — never inferred from low blast.
- **`fly=producer` → provenance log** (+ human confirm unless `eval=gated` catches the compounding error).
- **`blast=high` → human confirm**; **`blast=unknown` → never unattended** (supply `--blast`).

`blast` lives in the bundled `data/aidlc_axes.csv` (regenerate with `scripts/build_axes.py`).
`--id` resolves it precisely; an unknown blast refuses to authorize an unattended run.

### (3) Apply the modality × risk-tier overlay

Compose the invariant task with **modality** (single-turn-rag · tool-using · coding ·
multi-agent · voice · image-gen · extraction) × **risk-tier** (internal ·
external-low-stakes · external-high-stakes). This is **executable** — pass `--modality`
and `--risk-tier` to `autonomy_gate.py` and it recomputes on tightened axes (high-stakes →
bump `safety`/`blast`, add canary + safety gate, set `gate_metric = pass^k`). The overlay
only ever *tightens*. Details in `references/schema-and-autonomy.md` §8.

```bash
python scripts/autonomy_gate.py --id AT-30 --modality multi-agent --risk-tier external-high-stakes
```

### (4) Run the loop (with stopping rules)

AIDLC work is loops, not one-shots. Run the loop for the phase; **stop only on the
stated rule.**

- **The eval spine (default backbone, `EVL-01..16`):** instrument → smart-sample failure-biased traces → open-code (human) → axial-code into a taxonomy (LLM proposes, human validates) → quantify → build from-prod dataset → write graders (code first, validated judge second) → gate in CI → ship behind gate → score online → RCA → feed back. **Stop error-analysis at saturation** (~20 traces with no new failure mode). Deep dive in `references/eval-spec-playbook.md` and `references/measurement-playbook.md`.
- **Judge-validation loop:** draft judge (allow `Unknown`) → collect human labels → `scripts/judge_validation.py` (certifies on the **full-set CI lower bound**; prints the exact N needed, ~70+ for a strong judge) → if below bar, refine the prompt on dev and re-measure → recalibrate on a cadence. **Refuse to trust an unvalidated judge.**
- **Ship loop:** pin the bundle (model+prompt+tools+config) → shadow → canary → gate on online scores → advance or **one-click rollback**. See `references/delivery-playbook.md`.
- **Failure-recovery loop:** after **3 failed fixes, stop and question the architecture** (is it a specification gulf or a generalization gulf? — `references/reasoning-heuristics.md` §10). Don't thrash.

### (5) Do stats only through scripts

Never let the model do the arithmetic. Route every quantitative claim:

| Need | Command |
|---|---|
| Mean + CI; alert on the **lower bound** | `scripts/eval_stats.py ci --data scores.txt` |
| Is B better than A (**paired** by default: McNemar / paired bootstrap) | `scripts/eval_stats.py compare --a base.txt --b cand.txt` |
| Capability vs **reliability** (`pass@k` / `pass^k`) | `scripts/eval_stats.py passk --data runs.tsv --k 1,5,8` |
| Sample size / power / MDE | `scripts/eval_stats.py power --p0 0.8 --mde 0.05` |
| Judge alignment (gates on the **CI lower bound**, not the point estimate) | `scripts/judge_validation.py --labels labels.csv` |
| Train/eval contamination & near-dupes | `scripts/contamination_check.py --train t.txt --eval e.txt` |
| Cluster failure traces into ranked modes | `scripts/trace_cluster.py --input notes.txt` |
| Run a pre-registered eval gate (CI lower bound + worst slice + **paired** regression) | `scripts/eval_gate.py --results r.jsonl --bar bar.json` |
| Inference unit economics (cost/task, margin, frontier, tail) | `scripts/cost_calc.py per-task ...` |

See `scripts/README.md` for full interfaces. Report estimates as "X ± Y (n=…, p=…)",
never "it went up". A `run_unattended` verdict assumes `eval=gated` is a **judge-validated**
grader (TRUSTED) — confirm that before trusting the gate.

### (6) Tool selection + MCP governance gate

Pick by **fit and cost**, prefer the cheapest tool/model that clears the eval bar,
and route most traffic to a cheap model — frontier only for the hard call (mirror the
`copilot`/`human-led` split). Landscape moves fast — **verify current** before committing.

| Job | Common options (verify current) |
|---|---|
| Eval / dataset / CI | Braintrust, Promptfoo, OpenAI Evals, DeepEval, Ragas |
| Tracing / observability | Langfuse, Arize Phoenix, Helicone, Datadog LLM Obs, LangSmith |
| Routing / gateway | LiteLLM, OpenRouter, NotDiamond/RouteLLM, Martian |
| Safety / red-team | garak, PyRIT, Lakera, Llama Guard, NeMo Guardrails |
| Instrumentation schema | OpenTelemetry GenAI (`gen_ai.*`) — don't invent a schema |

**MCP governance gate (always-applied, load-bearing):** selecting/evaluating an MCP
server (AT-26) is `safety_exposure:high`. Use **Runlayer-managed servers only**; never
install/enable an unmanaged ("shadow") server; flag any config not managed by Runlayer.
Governance approval is human-owned even when reliability testing is automated.

### (7) Out-of-the-box requests (the escape hatch)

For a novel request with no catalog match:
1. `scripts/select_task.py "<request>"` → nearest invariant(s).
2. Name the composition explicitly: "closest to AT-XX, specialized for `<modality>` at `<risk-tier>`."
3. Reason from `references/reasoning-heuristics.md` (spine §0 + the cluster's heuristics) — they generalize past the literal catalog.
4. Still run `autonomy_gate.py` on your estimated axes (supply `--blast`).
5. **Escape hatch:** if the fit is poor (e.g. `select_task.py` reports a weak match below the floor), or `safety`/`blast` is high and you're unsure, say so and ask the human. A confident-but-wrong plan on a high-stakes task is the failure to avoid.

**Dispatch subagents for the hard, subjective calls.** For rubric design (AT-08), taxonomy
validation (EVL-04), go/no-go (AT-54), or model choice (AT-29/30): use **blind A/B** (hide
which output is which) for model/prompt picks, **best-of-N** for drafting a rubric, **panel**
for taxonomy boundaries. See skill: `dispatching-parallel-agents`. Default to a single pass
for mechanical tasks.

## Discipline: rationalizations → reality

"You can only safely automate what you can grade" is a discipline. Under pressure you (or
the user) will reach for these — don't:

| Rationalization | Reality |
|---|---|
| "It's a one-line prompt edit, just ship it." | A prompt edit *is* a distribution change — version and gate it like code (AT-19/20). |
| "The judge looks right." | An unvalidated judge is worse than none. Run `judge_validation.py`; trust only `TRUSTED`. |
| "Blast is low, so it's safe to run unattended." | Reversibility ≠ safety; the dominant risk is *undetectable wrongness*. A safety:high actuator stays human even at low blast. |
| "Offline scores are green, ship it." | Offline ≠ prod. Score online; alert on the CI **lower** bound (AT-55/56). |
| "Aggregate pass, we're good." | An aggregate pass hides a broken slice — gate the worst slice too (AT-14). |
| "Emergency — override the safety gate." | A failed safety floor is a hard no-go; the gate decision stays human (AT-68). |

**Red flags — STOP:** editing a prod prompt in place · quoting a number the *model* computed instead of a script · `run_unattended` on `eval ∈ {none,partial}` · trusting a judge you didn't validate · reaching for `--gate-on point` to "just get TRUSTED" · pasting a metric with no CI.

## Self-test

This skill ships its own eval suite. After any edit, run it:

```bash
python evals/run_evals.py
```

It checks routing, autonomy-gate decisions (incl. **negative** guards that must catch an
unsafe-combo regression), and stats self-checks against expected outcomes. See
`evals/README.md`.

## Reference map (one level deep)

- Core: `references/schema-and-autonomy.md`, `references/reasoning-heuristics.md`; `scripts/` (`select_task`, `autonomy_gate`, `eval_stats`, `judge_validation`, `contamination_check`, `trace_cluster`, `eval_gate`, `cost_calc`, `build_axes` + `scripts/README.md`); `data/` (vendored CSVs + generated `aidlc_axes.csv`); `evals/`.
- Cluster playbooks & catalog: `references/task-catalog.md`, `references/discovery-playbook.md`, `references/eval-spec-playbook.md`, `references/system-agent-playbook.md`, `references/training-flywheel-playbook.md`, `references/delivery-playbook.md`, `references/measurement-playbook.md`, `references/safety-substrate.md`, `references/inference-economics.md`, `references/commercial-playbook.md`, `references/usecase-playbooks.md`.
- Templates: `assets/`.

> Portability note: the skill `name` and its directory are both `pm-for-aidlc` (hyphens), matching the agentskills.io `^[a-z0-9-]+$` rule for clean cross-tool portability (Claude Code, Codex, Cursor). Keep the frontmatter `name` and the directory name in sync if you ever rename.
