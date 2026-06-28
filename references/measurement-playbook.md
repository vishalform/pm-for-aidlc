# Measurement & Monitoring — playbook

*Cluster 6 · 13 tasks (`AT-55`–`AT-62` + `EVL-01`, `EVL-13`–`EVL-16`) · all `now`. Where the loop closes back to Discovery — and restarts.*

The RCA, alerting, dashboards, and drift hunts survive from classic PM, but they now run over **eval scores and a behavior distribution that can shift even when you change nothing** — because a provider updated the model underneath you, or the input mix moved. Offline evals catch *known* failures; online scoring catches the distribution shift you didn't anticipate. Measurement here does not end the lifecycle; it **restarts** it.

## When this applies

- You need to know if prod quality is holding — **score live traffic** (`AT-55`/`EVL-13`).
- For a grounded product, you must watch **hallucination/groundedness** as a trust metric (`AT-56`) — e.g. *"every number traces to a tool"* made measurable.
- Behavior **drifted** vs baseline and you need to localize it (`AT-57`).
- A **multi-step agent** breaks somewhere and you need to find *where* (the transition-failure matrix, `EVL-15`).
- An **eval score dropped** and you must root-cause it (`AT-61`/`EVL-14`).
- **Offline says good, prod says bad** — reconcile the gap (`AT-62`).
- You're not sure the runs are even **captured** correctly (`EVL-01` — the precondition).

## The tasks

| id | task | autonomy | eval | regr | safety | flywheel | status |
|---|---|---|---|---|---|---|---|
| EVL-01 | Verify trace instrumentation (the precondition) | autonomous | partial | low | med | producer | now |
| AT-55 | Wire online scoring on production traffic | copilot | gated | med | med | consumer | now |
| EVL-13 | Wire online scoring and drift alerts (alert on CI lower bound) | copilot | gated | med | med | consumer | now |
| AT-56 | Monitor hallucination and groundedness rate | autonomous | gated | high | high | consumer | now |
| AT-57 | Detect quality or behavior drift vs baseline | copilot | partial | high | med | consumer | now |
| AT-58 | Cluster online failures into a triage queue | copilot | gated | med | med | producer | now |
| EVL-15 | Build the agent transition-failure matrix | copilot | partial | med | none | consumer | now |
| AT-59 | Build a cost/latency/quality dashboard + per-task cost | copilot | partial | low | none | none | now |
| AT-60 | Wire human feedback (thumbs/edits) into the flywheel | copilot | partial | med | med | producer | now |
| AT-61 | Investigate an eval-score regression (RCA) | copilot | partial | high | med | none | now |
| EVL-14 | Investigate an eval-score regression (RCA) | copilot | partial | high | med | none | now |
| AT-62 | Reconcile the offline-eval vs online-quality gap | copilot | partial | high | med | producer | now |
| EVL-16 | Plan eval-gated canary/shadow and rollback | copilot | gated | high | med | none | now |

Per-task steps + full 6-axis read: [`task-catalog.md`](task-catalog.md).

## The method (monitor → triage → restart the loop)

```text
EVL-01 verify instrumentation (replayable: inputs+output+tool calls+context+versions+cost)
  → AT-55/EVL-13 online scoring on a sample; alert on the CI LOWER BOUND, not the point estimate
  → AT-56 groundedness monitor (every claim traces to a source) · AT-57 drift vs baseline
  → AT-58 cluster online failures into a triage queue (→ feeds Discovery/AT-01 & the dataset)
  → EVL-15 transition-failure matrix to localize WHERE a multi-step agent breaks
  → AT-61/EVL-14 RCA a score drop · AT-62 reconcile offline↔online gap
  → AT-59 cost/latency/quality together · AT-60 capture thumbs+edits into the flywheel
```

- **You can't evaluate what you didn't capture** (`EVL-01`): audit a sample of runs against the required-field checklist (map to the `gen_ai.*` OTel convention); a run you can't replay is invisible to the loop.
- **Score reference-free, alert on the lower bound** (`EVL-13`): production has no gold answer, so use reference-free scorers; alert on the CI lower bound to avoid chasing noise.
- **Groundedness is the trust metric** (`AT-56`): for a grounded product, an ungrounded claim is a sev incident, not a quirk — it runs `autonomous` as a monitor with alerts, and carries `safety:high`.
- **Watch the distribution, not a point** (`AT-57`): models drift even when you change nothing; segment where drift concentrates and open an RCA.
- **A drop-off in an agent is a transition failure, not a funnel step** (`EVL-15`): tally last-success × first-failure across runs to find which hand-off actually breaks.
- **A score drop has four suspects — model, judge, data, system** (`AT-61`/`EVL-14`): eliminate the **judge** first (cheapest way to be fooled), then diff the changed component and timestamp-match to deploys.
- **Offline↔online gap is a dataset bug, not a model bug** (`AT-62`): when offline says good and prod says bad, the eval set is unrepresentative — find the missing cases and add them.
- **Three axes trade off** (`AT-59`): you can't manage quality without seeing cost and latency beside it, per task/run.
- **Capture the edit, not just the thumbs** (`AT-60`): the edit shows the fix — route it to the dataset and close the loop to the user.

## Tools

- **Online scoring / obs:** Braintrust online, Arize Phoenix, Langfuse, HoneyHive.
- **Instrumentation:** OpenTelemetry GenAI conventions, Arize Phoenix, Langfuse.
- **Cost/latency:** Helicone, Datadog LLM Observability, Langfuse.
- **RCA:** Braintrust diff, traces, git log.

## Pitfalls

- Logging the answer but not the tool calls; missing prompt/model versions; no cost capture (`EVL-01`).
- **Alerting on the point estimate** (not the CI lower bound); offline-only evaluation; untuned thresholds.
- No groundedness metric; trusting fluent output; ignoring slow drift.
- Reading the aggregate, not the transition (`EVL-15`); ill-defined agent states.
- **Blaming the model when the judge drifted**; correlation-as-cause; stopping at the first hypothesis.
- Trusting offline over online; not updating the eval set after a gap (`AT-62`).
- Tracking cost without quality; capturing thumbs but not edits, or never using the signal.

## Execution heuristics

- *You cannot evaluate what you didn't capture.*
- *Score the CI lower bound, not the point estimate.*
- *Groundedness is the trust metric;* an ungrounded claim is a sev incident.
- *Models drift even when you change nothing* — watch the distribution.
- *A score drop has four suspects — model, judge, data, system; eliminate the judge first.*
- *When offline says good and prod says bad, the eval set is unrepresentative — the gap is a dataset bug.*
- *A drop-off in an agent is a transition failure, not a funnel step.*
- *Capture the edit, not just the thumbs.*

## Hand-offs

Closes the loop back to **Discovery** ([`discovery-playbook.md`](discovery-playbook.md) — `AT-58` ≈ `AT-01`) and grows the **Eval & Spec** dataset ([`eval-spec-playbook.md`](eval-spec-playbook.md) — `EVL-01`→`EVL-06`). `EVL-16` graduates **Delivery** changes ([`delivery-playbook.md`](delivery-playbook.md)). Cost views feed [`inference-economics.md`](inference-economics.md).

**Stressed hardest by** UC-09 (agentic — `EVL-15`), UC-10/UC-11 (online A/B + drift), UC-01/UC-02/UC-05 (online scoring + groundedness). See [`usecase-playbooks.md`](usecase-playbooks.md).
