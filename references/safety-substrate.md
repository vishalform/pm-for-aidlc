# Safety, Red-teaming & Guardrails — substrate playbook

*Cross-cutting substrate A · 6 tasks (`AT-63`–`AT-68`) · all `now`. Not a phase you pass through — a lens laid over every cluster.*

Safety sits as a **substrate**, not a step, because it overlays Discovery, System Design, Delivery, and Measurement alike. It is the cluster with the **heaviest safety exposure** (every task is `safety:high`) and the **least SaaS precedent** — the nearest classic analog is incident response (`T-060`), and it covers only a fraction of the ground. Safety here is a **measurable, regressable, gated** property: jailbreak resistance and over-refusal both get evaluated and gated, and they **trade off**.

## When this applies

- The surface is **public-facing, regulated, or takes irreversible/financial actions** (the Chevy-$1, Air Canada, Cursor-policy class of incident).
- You need to find the jailbreak **before users do** (`AT-63`) and keep a regressable **abuse corpus** (`AT-64`).
- You must define **what the system must never do** and enforce it with filters (`AT-65`).
- The system **over-refuses** valid requests, or **under-refuses** harmful ones (`AT-66`).
- A **harmful output reached prod** and you must contain + capture it (`AT-67`).
- A release needs a **safety gate** before it ships (`AT-68`).

## The tasks

| id | task | autonomy | eval | blast | safety | flywheel | status |
|---|---|---|---|---|---|---|---|
| AT-63 | Design a red-team campaign | human-led | partial | med | high | producer | now |
| AT-64 | Build and maintain a jailbreak and abuse eval corpus | copilot | gated | low | high | producer | now |
| AT-65 | Spec guardrail policy and content filters | human-led | gated | high | high | none | now |
| AT-66 | Calibrate refusal and over-refusal rate | copilot | gated | med | high | none | now |
| AT-67 | Triage a safety incident or harmful output | human-led | partial | high | high | producer | now |
| AT-68 | Run a pre-release safety eval gate | human-led | gated | high | high | none | now |

Per-task steps + full 6-axis read: [`task-catalog.md`](task-catalog.md). Note the autonomy: the *judgment* tasks (`AT-63`/`AT-65`/`AT-67`/`AT-68`) are **human-led**; AI generates attacks and runs suites but never owns the threat model, the policy, or the containment call.

## The method (make safety a gate, not a checklist)

```text
AT-63 red-team campaign against a threat model  →  log breaks
  → AT-64 categorize breaks into a versioned jailbreak/abuse corpus → score resistance
  → AT-65 guardrail policy + input/output filters (block/redact/escalate)
  → AT-66 calibrate refusal vs over-refusal on paired benign/harmful sets
  → AT-68 pre-release safety eval gate (jailbreak + abuse + PII suites vs the floor)
  → AT-67 if a harmful output ships: CONTAIN first → comms → postmortem → AT-17 regression case
```

- **Red-team to find it first** (`AT-63`): start from a threat model, generate attacks, run the campaign, log breaks, and **fix + regress** them — absence of a campaign is not absence of vulnerability.
- **Resistance is regressable** (`AT-64`): a versioned, categorized corpus turns jailbreak resistance into a score that can silently regress if you don't watch it — so put it in an eval.
- **Guardrails are policy made executable** (`AT-65`): define disallowed behaviors, choose filters, set actions (block/redact/escalate), and **test against the real abuse corpus** — an untested filter is decorative.
- **Over-refusal is a real product failure** (`AT-66`): safety and helpfulness trade off; measure *both* rates on paired benign/harmful sets and own the balance as a product call.
- **Contain before you diagnose** (`AT-67`): a harmful output in prod is reversible only *forward* (filter or rollback); contain, communicate, postmortem, then turn the incident into a permanent regression case (`AT-17`).
- **Safety is a release gate** (`AT-68`): a failed safety floor is a hard no-go; the suites run, but the decision stays human.

## Tools

- **Red-team / attacks:** garak, PyRIT, HarmBench, manual probing.
- **Guardrails / filters:** Llama Guard, NeMo Guardrails, OpenAI moderation, Guardrails AI; Lakera for jailbreak/abuse detection.
- **Scoring:** the eval suite + Braintrust / Arize Phoenix for refusal/over-refusal rates.

## Pitfalls

- No threat model; one-off probing; **breaks logged but never fixed**.
- Stale corpus; no categorization; treating safety as a one-time launch checklist.
- Policy with no enforcement; **untested filters**; over-blocking valid use (over-refusal).
- Optimizing harm-blocking only, ignoring over-refusal; no benign test set.
- Slow containment; no comms; **no regression case from the incident**.
- Treating safety as advisory; no PII check; overriding a failed safety floor.

## Execution heuristics

- *You red-team so you find the jailbreak before users do.*
- *Jailbreak resistance is a measurable, regressable property* — if it's not in an eval, it will silently regress.
- *Guardrails are policy made executable;* a filter not tested against real attacks is decorative.
- *Over-refusal is a real product failure;* safety and helpfulness trade off and the balance is a product call.
- *Contain before you diagnose.*
- *Safety is a release gate, not a launch-day checklist.*

## Hand-offs

The pre-release gate (`AT-68`) is part of **Delivery** go/no-go ([`delivery-playbook.md`](delivery-playbook.md), `AT-54`). Incidents become regression cases in **Eval & Spec** ([`eval-spec-playbook.md`](eval-spec-playbook.md), `AT-17`). PII/data-use posture sits with [`inference-economics.md`](inference-economics.md) (`AT-72`) and consent/disclosure with [`commercial-playbook.md`](commercial-playbook.md) (`AT-85`). MCP-server safety is enforced in [`system-agent-playbook.md`](system-agent-playbook.md) (`AT-26`).

**Stressed hardest by** UC-15 (the trust & safety layer itself), UC-12 (legal), UC-13 (clinical), UC-01/UC-02 (public-facing conversational). See [`usecase-playbooks.md`](usecase-playbooks.md).
