# Discovery & Capability Mapping — playbook

*Cluster 1 of the AIDLC loop · 7 tasks (`AT-01`–`AT-07`) · all `now`. The opening move: the loop starts here and closes back here from Measurement.*

Discovery does not disappear when the product becomes a model — its **substrate** changes. The SaaS PM mined funnels, tickets, and reviews; the AI PM mines **traces** (the recorded runs of the system itself) for the failure modes and latent capabilities that say what to grade and build next. The funnel's "largest absolute drop" logic (`T-011`) is retired here: AI quality regressions are diffuse distribution shifts and failure clusters, not one leaking step.

## When this cluster applies

Reach for it when:
- You have **production traces / logs** and need to know what to fix first ("the agent is worse this week but I can't say how").
- A **new model dropped** and you need to know what it newly unlocks (not just "should we swap?").
- A **thumbs-down, edit, or complaint** arrived and needs to become a labeled datapoint, not an anecdote.
- You suspect a **tool/MCP server is flaky** and quietly capping quality.
- You need to know **what behaviors have no eval** before they regress (the discovery-side mirror of `AT-13`).

## The tasks

| id | task | autonomy | eval | blast | flywheel | status |
|---|---|---|---|---|---|---|
| AT-01 | Mine production traces into failure-mode clusters | copilot | partial | low | consumer | now |
| AT-02 | Run a capability-elicitation probe on a new model | copilot | partial | low | none | now |
| AT-03 | Triage a thumbs-down or negative-feedback event | copilot | partial | low | producer | now |
| AT-04 | Build a use-case to eval-gap map | copilot | partial | low | none | now |
| AT-05 | Competitive model or agent teardown on your eval set | copilot | gated | low | none | now |
| AT-06 | Cluster negative feedback into quality themes | copilot | partial | low | consumer | now |
| AT-07 | Mine tool-call logs for unreliable tools | copilot | partial | low | none | now |

Full per-task steps and the 6-axis read: see [`task-catalog.md`](task-catalog.md). Autonomy gate: [`schema-and-autonomy.md`](schema-and-autonomy.md).

## The method (the trace-mining loop)

```text
sample recent traces  →  cluster by failure TYPE  →  rank by frequency × severity
   →  link representative exemplars  →  file novel cases to the eval dataset (AT-09)
   →  hand off a ranked queue (to Eval & Spec, or the roadmap)
```

The whole cluster is one discipline applied to four signals — **traces** (`AT-01`, `AT-07`), **new-model probes** (`AT-02`), **single failures** (`AT-03`), and **aggregated feedback** (`AT-06`) — plus two maps that make coverage and competition visible (`AT-04`, `AT-05`). Output is always a *ranked, exemplar-linked queue*, never a single anecdote.

- **Cluster, never react.** The unit of work is a *pattern* (named failure mode), ranked by frequency × severity, with exemplars linked. One dramatic trace is not a roadmap line.
- **Reproduce before believing** (`AT-03`): fix the seed/temperature, because reproduction is now probabilistic. A thumbs-down you can't reproduce is not yet a datapoint.
- **Capture before it decays:** every confirmed failure is filed to the eval/regression dataset (`AT-09`, `EVL-06`) — this is where the flywheel begins (`AT-03`/`AT-06` are flywheel `producer`/`consumer`).
- **Probe for capability, not parity** (`AT-02`): a new model is an *opportunity surface*. Ask "what can it now do that the old one couldn't?" before re-pricing the roadmap — and score it on *your* task, never a memorized benchmark.

## Tools

- **Trace / observability:** LangSmith, Langfuse, Arize Phoenix, Braintrust.
- **Tool-call span mining (`AT-07`):** OpenTelemetry GenAI conventions, Helicone, Datadog LLM Observability.
- **New-model probes (`AT-02`/`AT-05`):** a model playground, OpenRouter, the OpenAI/Anthropic consoles, Braintrust.
- **Feedback clustering (`AT-06`):** Arize Phoenix, Enterpret, Dovetail, Zendesk (for the inbound signal).

(Representative `tools_in_practice` from the sheet — pick by fit and the governance rule, not by brand.)

## Pitfalls (distilled across the cluster)

- **Vibe-checking logs** / reacting to one dramatic trace instead of clustering into patterns.
- **Anecdotal one-prompt judgments** on a new model; testing on memorized examples; ignoring its cost/latency.
- **Losing the trace link** or never growing the dataset (a triaged failure that isn't captured is wasted).
- **Trusting public leaderboards** — they measure someone else's task; run competitors through *your* eval set (`AT-05`).
- **Treating tool errors as pure ops** — silent timeouts and mis-calls are a *product* quality cap (`AT-07`).

## Execution heuristics

- *Failing traces are the roadmap.* The production distribution always differs from staging.
- *A thumbs-down is a labeled datapoint, not a complaint.*
- *A new model is an opportunity surface, not just a swap.*
- *Ungraded behavior is unmanaged behavior* — coverage gaps are exactly where silent regressions hide.
- *The score is noise; the verbatims and the edits are the signal* — the edit shows the fix.
- *A flaky tool quietly caps agent quality;* tool-surface reliability is a product metric.

## Hand-offs

Feeds **Eval & Spec** ([`eval-spec-playbook.md`](eval-spec-playbook.md)) — ranked clusters become datasets (`AT-09`) and graders, and the error-analysis loop (`EVL-02`–`EVL-06`) is the deepened version of trace mining. `AT-04`/`AT-05` feed the **eval roadmap** (`AT-71`) and **capability roadmap** (`AT-73`) in [`inference-economics.md`](inference-economics.md).

**Stressed hardest by use cases** with high production traffic: UC-01 (support), UC-02 (voice), UC-03 (coding), UC-09 (agentic automation) — see [`usecase-playbooks.md`](usecase-playbooks.md).
