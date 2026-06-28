# Use-Case Eval Plan — `<UC-id · use case name>`

> Specializes the AIDLC loop for one use case: pin the dominant failure mode → the metric that defines "good" → the cluster/task set it stresses. Source the failure mode + metric from `references/usecase-playbooks.md`.

## 1. Frame
- Use case: `<UC-id + name>` · family: `<...>`
- What it does: `<one line>`
- **Dominant failure mode** (design the eval to catch this first): `<e.g., confident wrong policy / semantically-wrong SQL / compounding error / over-refusal>`
- **Success metric** (the pinned definition of "good"): `<e.g., resolution rate (pinned) / execution accuracy vs golden / pass^k / groundedness>`
- Risk tier: `<internal / external-low-stakes / external-high-stakes>` → sets gate strictness.

## 2. Eval focus → tasks (from the use-case's curated set)
| AIDLC need | tasks to run | playbook |
|---|---|---|
| define "good" | `AT-08` (+ `AT-09`/`EVL-11`) | [`eval-spec-playbook.md`](../references/eval-spec-playbook.md) |
| the distinctive grader | `<e.g., AT-23 retrieval / AT-10 exec / AT-56 groundedness / AT-25 tool-call>` | `<...>` |
| `<system/agent need>` | `<AT-22 / AT-27 / AT-30 …>` | [`system-agent-playbook.md`](../references/system-agent-playbook.md) |
| safety (if public/regulated) | `<AT-65/66/68 …>` | [`safety-substrate.md`](../references/safety-substrate.md) |
| monitor | `<AT-55/56/57, EVL-15 …>` | [`measurement-playbook.md`](../references/measurement-playbook.md) |
| commercial | `<AT-74 pricing / AT-84 acceptance …>` | [`commercial-playbook.md`](../references/commercial-playbook.md) |

Distinctive `AT-`/`EVL-` set for this UC: `<paste from usecase-playbooks.md>` · inherited classic `T-`/`O-`: `<...>`.

## 3. Datasets & slices
- Golden: `<...>` · adversarial / incident-repro: `<...>` · slices that matter here: `<segment / doc type / query type / specialty / risk tier>`.

## 4. The bar & gates
- Primary metric floor (pre-registered): `<...>` · guardrail floors: `<groundedness / safety / cost>`.
- CI gate (`AT-49`/`EVL-12`): `<...>` · online scoring (`AT-55`/`EVL-13`): `<...>` · ship via [`delivery-playbook.md`](../references/delivery-playbook.md).

## 5. Use-case-specific watchouts
`<e.g., pin the resolution definition (UC-01); measure recall@k separately from generation (UC-05); pass^k not pass@1 (UC-09); omission detection (UC-13); O-FIN-* overlays (UC-14); deliverability guardrail (UC-07)>`

## Self-check
- [ ] Eval designed around the **dominant** failure mode · [ ] metric definition **pinned** · [ ] distinctive grader present (not just generic quality) · [ ] slices chosen for this use case · [ ] gate strictness matches risk tier.
