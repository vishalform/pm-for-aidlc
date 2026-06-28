# Commercial & Stakeholder — playbook

*Cluster 7 (the hybrid PM's other half) · 13 tasks (`AT-74`–`AT-86`) · all `now`. The pricing, packaging, GTM, win-loss, and exec-comms work — re-pointed at an AI product.*

The AI PM in this atlas is a **hybrid**: they own the AI system *and* the commercial product around it. So this work isn't cut — it's re-pointed, because the economics and the trust questions are different. Two twists recur: **inference is a metered cost** (so flat pricing can lose money as a feature succeeds) and **trust is the deal-maker** (a hallucination in the POC is a lost deal). These tasks reframe their classic ancestors rather than replace them — the `maps_to_classic` column points back to the originals.

## When this applies

- You're **pricing/packaging** an AI feature whose COGS scales with usage (`AT-74`/`AT-75`/`AT-76`).
- You're **launching** an AI capability and must position it on evaluated capability + limits, not hype (`AT-77`/`AT-79`).
- The **field** is asking for things — half of "it doesn't work" is a model limit, not a backlog item (`AT-78`).
- A deal turned on **AI trust/accuracy** (win-loss, "why is it wrong", the buyer trust narrative) (`AT-80`/`AT-82`/`AT-83`).
- Leadership needs an **AI quality + economics** update (`AT-81`).
- You must handle **adoption read as acceptance** and **data-use consent/disclosure** (`AT-84`/`AT-85`).
- A **competitor** needs a capability + pricing teardown on *your* evals (`AT-86`).

## The tasks

| id | task | autonomy | eval | safety | maps to classic | status |
|---|---|---|---|---|---|---|
| AT-74 | Design usage or token-based pricing | copilot | none | none | T-041, T-027 | now |
| AT-75 | Define AI feature tier-gating and rate limits | copilot | none | none | T-042 | now |
| AT-76 | Model the gross-margin impact of an AI feature | copilot | none | none | T-093, T-136 | now |
| AT-77 | Write a GTM or launch brief for an AI capability | copilot | none | med | T-045 | now |
| AT-78 | Triage sales and CS requests for the AI product | copilot | none | none | T-066 | now |
| AT-79 | Build sales enablement for an AI feature | copilot | none | med | T-129, T-151 | now |
| AT-80 | Run AI win-loss analysis | copilot | none | med | T-099 | now |
| AT-81 | Prepare an exec or board update on AI quality + economics | human-led | none | med | T-095, T-103 | now |
| AT-82 | Respond to a "why is the AI wrong" escalation | human-led | none | med | T-094, T-131 | now |
| AT-83 | Author the AI trust and transparency narrative for buyers | human-led | none | high | O-B2B-013 | now |
| AT-84 | Build an AI adoption and engagement scorecard | copilot | partial | none | T-139, T-074 | now |
| AT-85 | Handle AI data-use consent and disclosure | human-led | none | high | T-048, O-FIN-010 | now |
| AT-86 | Competitive AI capability and pricing teardown | copilot | gated | none | T-150, T-007 | now |

Per-task steps + full 6-axis read: [`task-catalog.md`](task-catalog.md).

## The method (price the metered cost, sell the evaluated capability)

- **Price the unit that tracks value *and* cost** (`AT-74`/`AT-75`): pick a value-aligned usage unit, map it to inference cost, set price + included tier + overage/caps. Flat pricing on metered COGS is how AI products lose money at scale; rate limits are a margin control, not only a product one. The clearest business-model consequence of agents is **outcome-based pricing** (pay-per-resolution).
- **Model the tail** (`AT-76`): inference COGS scales with usage, so a feature's margin can invert as it succeeds — run a cost-sensitivity range on token growth (uses [`inference-economics.md`](inference-economics.md), `AT-70`).
- **Sell the evaluated capability, not the hype** (`AT-77`/`AT-79`): position around measured capability + trust, state limits honestly, and arm the field with the limits (objection-handling on hallucination/data-use). Overclaiming is a trust debt paid in churn.
- **Classify before committing** (`AT-78`): for AI products, "it doesn't work" splits into *model limit* vs *we haven't wired it* — don't promise capability the model lacks.
- **AI deals turn on trust** (`AT-80`/`AT-82`/`AT-83`): cluster AI-specific win/loss drivers (accuracy, hallucination, latency, cost); reframe "it's broken" to "here's the measured reliability and the fix path" with evidence; write the buyer-facing trust narrative (how it's evaluated, grounded, kept safe) to deflect the AI questionnaire.
- **Lead with the eval curve, not feature counts** (`AT-81`): the board cares about quality trend, unit economics, and safety exposure.
- **Acceptance is the truest adoption signal** (`AT-84`): measure acceptance/edit/override rate, not raw usage — *perceived ≠ measured value*.
- **Consent + disclosure are trust gates** (`AT-85`): spec consent capture for flywheel data use and disclosure of AI involvement, with opt-out — a silent data-grab or hidden AI is a liability (`safety:high`).

## Tools

- **Pricing / billing:** Stripe, Metronome; spreadsheet, warehouse SQL.
- **GTM / enablement:** Notion, Slack, Gong; marketing tools.
- **Win-loss / requests:** Gong, Salesforce, Productboard, Dovetail.
- **Trust / adoption:** a trust center, Notion, Braintrust (evidence), Amplitude.

## Pitfalls

- Flat price on metered cost; bill-shock risk; metering a non-value unit; gating table-stakes capability.
- Ignoring COGS at scale; flat usage assumptions; no sensitivity on token growth.
- Overclaiming capability; hiding limits; no eval evidence behind claims; value-only pitch with no limits.
- Promising capability the model lacks; treating model limits as quick fixes.
- Missing AI-trust loss reasons; anecdote over pattern; defensiveness; over-promising perfection.
- Counting usage not acceptance; ignoring the edit rate; no target.
- Training on data without consent; no AI disclosure; no opt-out; vague/stale trust artifacts.

## Execution heuristics

- *Price the unit that tracks both value and cost;* flat pricing on metered COGS loses money at scale.
- *Gate on cost and capability, not just features.*
- *Inference COGS scales with usage* — a feature's margin can invert as it succeeds.
- *Sell the evaluated capability, not the hype* — overclaiming is a trust debt you pay in churn.
- *Half of "it doesn't work" is a capability limit, not a backlog item.*
- *The acceptance/edit rate is the truest adoption signal.*
- *Reframe "it's broken" to "here is the measured reliability and the fix path."*

## Hand-offs

Pricing/margin uses [`inference-economics.md`](inference-economics.md) (`AT-70`/`AT-76`). Launch claims and trust narratives draw their **evidence** from [`eval-spec-playbook.md`](eval-spec-playbook.md) + [`measurement-playbook.md`](measurement-playbook.md) (eval trend, groundedness). Consent/disclosure pairs with [`safety-substrate.md`](safety-substrate.md) (`AT-85` ↔ `AT-72`).

**Stressed hardest by** UC-01 (outcome pricing), UC-07 (sales/SDR), UC-08 (content), UC-12 (legal trust). See [`usecase-playbooks.md`](usecase-playbooks.md).
