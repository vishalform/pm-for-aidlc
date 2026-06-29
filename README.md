# pm-for-aidlc

**An operator skill for the AI product manager whose product *is* the AI system** — the model, the agent loop, context/RAG, tools/MCP, routing, and inference. It turns a 102-task AIDLC library (`AT-01..AT-86` + `EVL-01..EVL-16`) into executable behavior for a coding agent: **route** a request to the right playbook, **gate** it through a 6-axis autonomy schema, **run** the eval-driven loop with explicit stopping rules, and **compute every number through scripts** instead of eyeballing it.

[![self-test](https://github.com/vishalform/pm-for-aidlc/actions/workflows/ci.yml/badge.svg)](https://github.com/vishalform/pm-for-aidlc/actions/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.8%2B%20stdlib--only-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![self-tests](https://img.shields.io/badge/script%20self--tests-49%2F49-brightgreen)

> **AIDLC** here means *the lifecycle of building the AI system as the product* (evals, prompts, RAG, agents, the training flywheel, delivery, monitoring, safety, economics). It is **not** AWS's "AI-DLC" (using AI to ship ordinary software faster) — same letters, orthogonal craft.

---

## Why this exists

When the product is a model, the PM's craft inverts:

- **Output is a distribution, not a value.** "Correct" is a graded judgment, not an assertion.
- **The eval is the new PRD** — a dataset + task + scoring function does the PRD's old job and runs on every commit. But it is **grown from looking at real traces, not authored upfront.**
- **The dominant risk is *undetectable wrongness*.** Blast radius is necessary but insufficient; a one-line prompt edit is a distribution change that can regress silently.

The one rule everything hangs on: **you can only safely automate what you can grade.**

## Who it's for

A coding agent (Claude Code, Cursor, Codex, …) acting as — or assisting — an **AI PM / AI engineer**. Load it when the work is writing/validating evals, mining traces into failure modes, designing or changing prompts/RAG/tools/agent-loops/routing, shipping a model or prompt change behind a gate, monitoring quality/groundedness/drift online, safety/red-team work, or inference unit-economics.

## What's inside

| Piece | What it does |
|---|---|
| **`SKILL.md`** | The lean router: route → gate → overlay → loop → stats → tools (+ a rationalizations/red-flags table). |
| **6-axis autonomy gate** (`scripts/autonomy_gate.py`) | A real decision engine: `leverage · blast · eval · regr · safety · fly` (+ `actuation`) → `run_unattended | draft_then_confirm | human_led` + the required controls. |
| **9 stdlib scripts** | Statistics, judge validation, contamination, trace clustering, a CI eval-gate, cost/unit-economics, and the axis-catalog generator. **No numpy/scipy** — Python 3.8+ standard library only. |
| **11 cluster playbooks** (`references/`) | Discovery, Eval & Spec, System & Agent, Training Flywheel, Delivery, Measurement, Safety, Inference Economics, Commercial — plus the task catalog and 16 use-case playbooks. |
| **102-task catalog + axes** (`data/`) | The full `AT-`/`EVL-` library with all six risk axes per task, vendored so the skill is self-contained. |
| **Output templates** (`assets/`) | Eval-spec, experiment readout, trace-coding sheet, autonomy-gate decision record, use-case eval plan. |
| **Self-test suite** (`evals/`) | 49 auto-verified **script** scenarios (gate + routing + stats) — including **negative safety guards** that must go red if a fix is reverted. Trigger routing (`trigger_scenarios`) is manual/subagent only. |

## Quickstart

```bash
git clone https://github.com/vishalform/pm-for-aidlc
cd pm-for-aidlc

# everything is stdlib-only — no install step
python evals/run_evals.py            # 49/49 script self-tests (gate+routing+stats)
python scripts/eval_stats.py selftest
python scripts/cost_calc.py selftest

# route a request to candidate tasks
python scripts/select_task.py "our agent hallucinated a refund policy in production"

# get the autonomy verdict for a task
python scripts/autonomy_gate.py --id AT-56
```

## Install

Drop the skill into your agent's skills directory (the directory name must stay `pm-for-aidlc` to match the frontmatter `name`):

```bash
# Claude Code
git clone https://github.com/vishalform/pm-for-aidlc ~/.claude/skills/pm-for-aidlc

# Cursor (project-local)
git clone https://github.com/vishalform/pm-for-aidlc .cursor/skills/pm-for-aidlc

# Codex
git clone https://github.com/vishalform/pm-for-aidlc ~/.agents/skills/pm-for-aidlc
```

The skill loads from `SKILL.md`'s frontmatter; the agent reads the body and pulls in a single cluster playbook on demand (progressive disclosure). It triggers automatically when the work matches the description — even when the user never says "eval" or "AIDLC".

## How it works

```
request
  ├─(1) ROUTE    match to a cluster → read that references/*-playbook.md   (scripts/select_task.py)
  ├─(2) GATE     read the 6-axis schema → run_unattended | draft_then_confirm | human_led (+controls)
  ├─(3) OVERLAY  compose modality × risk-tier → tighten the gates (never loosen)
  ├─(4) LOOP     run the cluster's loop (eval spine / judge-validation / ship / failure-recovery)
  ├─(5) STATS    every number via scripts/ (CIs, pass^k, judge TPR/TNR, power, cost)
  └─(6) TOOLS    pick by fit+cost; MCP only through the governance gate
```

Full detail in [`SKILL.md`](SKILL.md) and [`references/schema-and-autonomy.md`](references/schema-and-autonomy.md).

### Examples

| Walkthrough | What it covers |
|---|---|
| [`examples/worked-example.md`](examples/worked-example.md) | End-to-end: route → eval spine → judge → prompt gate → stats → ship gate → monitor |
| [`examples/judge-validation-walkthrough.md`](examples/judge-validation-walkthrough.md) | AT-11 → AT-12 → `judge_validation.py` → TRUSTED (under-powered → certified) |
| [`examples/ship-behind-gate-walkthrough.md`](examples/ship-behind-gate-walkthrough.md) | AT-16 → AT-20 → paired compare → `eval_gate.py` GO/NO-GO (regression + coverage gap) |

### The autonomy gate (the key inversion)

`autonomy_gate.py` encodes one load-bearing rule: **ungraded autonomous output never runs unattended**, no matter how low the blast radius looks (`eval ∈ {none, partial}` → `draft_then_confirm`). On top of that: `regr=high` forces an eval-gate (build the grader first if none exists); `fly=producer` adds a provenance log; a `safety=high` **actuator** keeps a human in the loop — *the decision stays human* — and the **only** carve-out that runs unattended is a read-only, judge-validated monitor (and read-only must be *asserted*, never inferred from low blast).

```bash
python scripts/autonomy_gate.py --id AT-56                    # read-only monitor → run_unattended
python scripts/autonomy_gate.py --id AT-65 --actuation irreversible
python scripts/autonomy_gate.py --id AT-30 --modality multi-agent --risk-tier external-high-stakes
```

### Statistics, not vibes

Every quantitative claim routes through a script (report "X ± Y (n=…, p=…)", never "it went up"):

| Need | Command |
|---|---|
| Mean + CI; alert on the **lower bound** | `eval_stats.py ci --data scores.txt` |
| Is B better than A (**paired** by default: McNemar / paired bootstrap) | `eval_stats.py compare --a base.txt --b cand.txt` |
| Capability vs **reliability** (`pass@k` / `pass^k`) | `eval_stats.py passk --data runs.tsv --k 1,5,8` |
| Validate an LLM judge (gates on the full-set **CI lower bound**) | `judge_validation.py --labels labels.csv` |
| Pre-registered CI eval-gate (CI lower bound + worst slice + **paired** regression) | `eval_gate.py --results r.jsonl --bar bar.json` |
| Train/eval contamination & template leakage | `contamination_check.py --train t.txt --eval e.txt` |
| Inference unit economics (cost/task, margin, frontier, tail) | `cost_calc.py per-task ...` |

See [`scripts/README.md`](scripts/README.md) for every interface.

## Repo layout

```
SKILL.md              # the router (start here)
references/           # 11 cluster playbooks + task catalog + use cases + schema spec + heuristics
scripts/              # 9 stdlib tools + shared helpers + README
data/                 # 102-task catalog, 6-axis bundle, use-case index (vendored)
assets/               # output templates
evals/                # run_evals.py + evals.json + fixtures (the self-test suite)
examples/             # end-to-end + focused walkthroughs (judge validation, ship gate)
```

## Self-tests & CI

The suite is a real regression guard for **scripts**, not a description of current behavior.
The **49/49 auto-verified scenarios** cover `gate_scenarios`, `routing_scenarios`, and
`stats_scenarios` only — **`trigger_scenarios` are printed for manual/subagent A/B** and
are not counted in the pass total. It ships **negative guards** (an actuating `safety:high`
task must *not* run unattended; an omitted blast must *not* authorize one; a paired
regression must be NO-GO; a coverage-gap candidate must be NO-GO; homographs like "memory
leak" must *not* route to Safety) plus golden-value math checks. `python evals/run_evals.py`
exits non-zero on any failure and runs in CI on every push (see
[`.github/workflows/ci.yml`](.github/workflows/ci.yml)). Team override keys: [`CONFIG.example.md`](CONFIG.example.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to add an `AT-`/`EVL-` task, regenerate the axis bundle, and keep the evals green. The Iron Law: **no behavior change without a self-test that would catch its revert.**

## Acknowledgements

The eval-driven philosophy draws on the public work of Hamel Husain, Aakash Gupta × Ankur Goyal ("evals are the new PRD"), Shreya Shankar et al. (the Three Gulfs), and the Braintrust eval manifesto. The skill format follows the [agentskills.io](https://agentskills.io/specification) spec and the practices in Anthropic's skill-authoring guidance and [obra/superpowers](https://github.com/obra/superpowers).

## License

MIT © 2026 Vishal Singh — see [LICENSE](LICENSE).
