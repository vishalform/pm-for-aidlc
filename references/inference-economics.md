# Inference Economics & Model Portfolio — substrate playbook

*Cross-cutting substrate B · 5 tasks (`AT-69`–`AT-73`) · all `now`. The other lens over everything: what the intelligence costs, where it comes from, and which capabilities to grow next.*

This is the AI PM's strategy-and-operations work (classic `T-090`–`T-093`), re-pointed at an AI product. Its defining new fact: **inference is COGS** — a feature can be loved and unprofitable on the same day. The portfolio carries lock-in risk; the roadmap is bounded by what you can grade. These are mostly **human-led** judgment tasks — AI assembles the comparison/model, the differentiating call stays with the PM.

## When this applies

- You're choosing **which capability runs on which model** — API vs open-weight vs fine-tuned — with lock-in and data-rights in view (`AT-69`).
- You need the **unit economics** of a feature: cost per task, margin, the cost-quality frontier (`AT-70`).
- You're sequencing **which evals to build next**, ranked by risk × use-case value (`AT-71`).
- You must set the **data-rights / licensing / privacy posture** for training and trace reuse (`AT-72`).
- You're setting the **capability strategy** — which bets, anchored to eval targets (`AT-73`).

## The tasks

| id | task | autonomy | eval | blast | safety | flywheel | status |
|---|---|---|---|---|---|---|---|
| AT-69 | Model portfolio build-vs-buy review | human-led | partial | med | med | none | now |
| AT-70 | Inference cost-per-task budget and unit economics | copilot | partial | med | none | none | now |
| AT-71 | Eval roadmap tied to capability and eval gaps | human-led | partial | med | med | none | now |
| AT-72 | Data-rights, licensing, and privacy posture for training and traces | human-led | none | high | high | producer | now |
| AT-73 | Capability roadmap tied to eval gaps | human-led | partial | med | med | none | now |

Per-task steps + full 6-axis read: [`task-catalog.md`](task-catalog.md).

## The method (cost, portfolio, and the eval-anchored roadmap)

- **Inference is COGS** (`AT-70`): define the task unit, measure tokens × price + tool/infra cost, model margin per task, map the cost-quality frontier, set a budget. A feature loved-and-unprofitable per call is a problem, not a win — and margin can *invert* as usage grows (model the tail, with `AT-76`).
- **Model choice is a portfolio decision with lock-in risk** (`AT-69`): map needs → models, compare API vs open vs fine-tune, assess lock-in + data rights, estimate switching cost. Don't single-source a capability you can't switch. (Pairs with routing in [`system-agent-playbook.md`](system-agent-playbook.md), `AT-29`/`AT-30`.)
- **The eval roadmap is the product roadmap** (`AT-71`/`AT-73`): you can only build what you can grade. Rank eval gaps by risk × use-case value, sequence the eval builds, tie each capability bet to an eval target. Capability bets with no eval target are how you chase benchmarks instead of use cases.
- **The flywheel's fuel is user data** (`AT-72`): inventory sources, check rights/consent/licensing, classify PII, set retention + access. Using data without rights is a legal and trust failure that compounds — hence `safety:high` and `eval:none` (it's a posture, not a graded behavior). This is the policy backstop for `AT-48` (wire the flywheel) and `AT-85` (consent/disclosure).

## Tools

- **Cost / unit economics:** Helicone, a model gateway, spreadsheet, warehouse SQL.
- **Portfolio:** vendor docs, eval data, spreadsheet.
- **Roadmap:** Braintrust (the gap map), a roadmap/strategy doc.
- **Data-rights:** the DPA/legal review, a data catalog, consent records.

## Pitfalls

- Ignoring per-task cost; no margin model; optimizing quality with no cost ceiling (`AT-70`).
- Single-vendor lock-in; ignoring data rights; choosing on hype (`AT-69`).
- Building features ahead of their evals; no risk ranking; orphan evals (`AT-71`).
- Capability bets with no eval target; chasing benchmarks not use cases; template strategy (`AT-73`).
- **Training on data without rights**; no consent for trace reuse; PII in datasets (`AT-72`).

## Execution heuristics

- *For an AI product, inference is COGS* — a feature can be loved and unprofitable on the same day.
- *Model choice is a portfolio decision with lock-in risk* — don't single-source what you can't switch.
- *The eval roadmap is the product roadmap;* you can only build what you can grade.
- *The flywheel's fuel is user data;* using it without rights is a trust failure that compounds.
- *Strategy is choosing which capabilities to grade-and-grow next* — the differentiating bet stays human.

## Hand-offs

Cost data comes from **Measurement** ([`measurement-playbook.md`](measurement-playbook.md), `AT-59`). The eval/capability roadmaps are fed by **Discovery** gap maps ([`discovery-playbook.md`](discovery-playbook.md), `AT-04`) and **Eval & Spec** ([`eval-spec-playbook.md`](eval-spec-playbook.md)). Routing/portfolio overlaps [`system-agent-playbook.md`](system-agent-playbook.md). Data-rights underpins [`training-flywheel-playbook.md`](training-flywheel-playbook.md) and pricing in [`commercial-playbook.md`](commercial-playbook.md).

**Stressed hardest by** the highest-volume / lowest-margin-tolerance workloads — UC-01 (support), UC-02 (voice), UC-10 (recsys), UC-11 (search). See [`usecase-playbooks.md`](usecase-playbooks.md).
