# Delivery & Release — playbook

*Cluster 5 · 6 tasks (`AT-49`–`AT-54`) · all `now`. Closely paired with `EVL-16` (in Measurement). Delivery survives almost intact from classic PM — but every gate swaps its criterion.*

The mechanics are familiar — staged ramps, flags, canaries, rollbacks, the go/no-go — but **the thing being gated is a behavior distribution, not a deterministic build**. Where the SaaS launch checked error rate and latency, the AI launch checks the **eval score and the safety floor**. A one-line prompt or model change is a distribution change; ship it like code, behind gates.

## When this applies

- A **model, prompt, tool, or config change** is ready and you need to ship it without silently regressing the output distribution.
- You need a **CI gate** that blocks merges on eval regression (`AT-49`).
- You're planning a **canary/shadow ramp** or an **online A/B** for a behavior change (`AT-51`/`AT-52`).
- Online quality **regressed** and you need a clean, fast **rollback** (`AT-53`).
- You're making the **ship/hold call** against eval + safety + cost + rollback-readiness (`AT-54`).

## The tasks

| id | task | autonomy | eval | blast | safety | status |
|---|---|---|---|---|---|---|
| AT-49 | Configure eval-gated CI | autonomous | gated | med | med | now |
| AT-50 | Pin and version a model+prompt release bundle | copilot | gated | med | none | now |
| AT-51 | Plan a canary or shadow deployment for a model change | copilot | gated | high | med | now |
| AT-52 | Online A/B a model/prompt change with quality + business guardrails | copilot | gated | high | med | now |
| AT-53 | Execute a model or prompt rollback on quality regression | human-led | gated | high | high | now |
| AT-54 | Release-readiness go/no-go on eval and safety gates | human-led | gated | high | high | now |
| EVL-16 | Plan eval-gated canary/shadow and rollback *(lives in Measurement)* | copilot | gated | high | med | now |

Per-task steps + full 6-axis read: [`task-catalog.md`](task-catalog.md).

## The ship loop

```text
AT-49 eval-gated CI blocks regressions on every PR (autonomous)
  → AT-50 pin the bundle: model id + prompt + tools + config + recorded eval scores + rollback target
  → AT-51/EVL-16 shadow, then canary a traffic % behind ONLINE scorers
  → AT-52 online A/B vs quality AND business guardrails; pre-set the ship rule
  → AT-54 go/no-go: eval pass + safety pass + rollback ready + cost in budget
  → advance  —or—  AT-53 one-click rollback to the last-good pinned bundle
```

- **The eval is the unit test** (`AT-49`/`EVL-12`): if it isn't in CI, it isn't a gate. Fail the build on regression, report which cases regressed, require sign-off to override. This is the single highest-leverage piece of release discipline in the AIDLC, and it runs **autonomous**.
- **A release is a bundle, not a model id** (`AT-50`): pin everything that affects behavior — model id, prompt version, tools, config — and record the eval scores + the rollback target. Pinning is what makes rollback one click.
- **Ramp behind online evals** (`AT-51`/`AT-52`): offline scores never fully predict prod, so shadow → canary → A/B with online scorers and **both** quality and business guardrails; pre-register the ship rule and don't peek.
- **Reversible mitigation first** (`AT-53`): when prod quality regresses, revert to the last-good bundle, verify recovery, *then* diagnose. A clean pinned bundle makes rollback a one-click decision under pressure. (`safety:high` — a human authorizes.)
- **Go/no-go is human and conjunctive** (`AT-54`): ship only when eval, safety, cost, and rollback-readiness *all* hold. One unchecked critical gate is a no-go.

## Tools

- **CI gates:** Braintrust GitHub Action, Promptfoo CI, GitHub Actions.
- **Bundling / rollout:** git, a prompt registry, a model gateway; LaunchDarkly / Statsig flags.
- **Online experiment:** Statsig, Braintrust online, warehouse SQL.

## Pitfalls

- Eval suite **not in CI**; thresholds too loose; silent overrides.
- Pinning only the model id; unversioned prompt/config; no recorded scores; no rollback target.
- **Big-bang model swaps** with no shadow/canary; no online scoring; no rollback trigger.
- Shipping on **offline scores alone**; peeking at an A/B; no business guardrail metrics.
- No pinned last-good bundle → slow rollback; skipping recovery verification.
- Shipping without a safety pass; overriding a failed critical gate.

## Execution heuristics

- *The eval is the unit test for a non-deterministic system; if it's not in CI, it's not a gate.*
- *A model release is a bundle, not a model id* — pin everything that affects behavior.
- *Offline eval is necessary but not sufficient;* the prod distribution decides — confirm online.
- *Reversible mitigation first;* a pinned bundle makes rollback one-click under pressure.
- *Ship only when the eval, the safety gate, and the rollback all hold.*

## Hand-offs

Gated by **Eval & Spec** ([`eval-spec-playbook.md`](eval-spec-playbook.md), `AT-16` bar) and **Safety** ([`safety-substrate.md`](safety-substrate.md), `AT-68` pre-release gate). Online ramp/scoring is read in **Measurement** ([`measurement-playbook.md`](measurement-playbook.md), `AT-55`/`EVL-13`/`EVL-16`). Cost-in-budget check uses [`inference-economics.md`](inference-economics.md) (`AT-70`).

**Stressed hardest by all use cases, especially** the high-stakes/irreversible/regulated ones — UC-09 (agentic automation), UC-13 (clinical), UC-14 (fraud/AML). See [`usecase-playbooks.md`](usecase-playbooks.md).
