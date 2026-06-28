# Experiment / Online Readout — `<change name>`

> For canary/shadow → online A/B of a model or prompt change (`AT-51`/`AT-52`/`EVL-16`) and the ship/kill call. Offline eval is necessary but **not sufficient** — the prod distribution decides. Report estimates **with uncertainty**; route the math through a stats script, never model arithmetic.

## 1. Hypothesis & pre-registration (lock before data)
- Change: `<model/prompt/tool/config>` · pinned bundle id (`AT-50`): `<...>`
- Hypothesis: `<the change improves `<metric>` without regressing guardrails>`
- **Ship rule (pre-set):** ship if `<primary ≥ +x with CI lower bound > 0>` **and** no guardrail breached. No peeking.

## 2. Design
- Unit / randomization: `<...>` · split: `<shadow % → canary %>` · power / sample size: `<n for MDE = …>` (`T-038`/`AT-52`).
- Duration: `<...>` · monitor assigned: `<name>`.

## 3. Metrics
| type | metric | direction | baseline | variant | Δ (95% CI) | significant? |
|---|---|---|---|---|---|---|
| primary quality | `<online score / resolution / pass^k>` | ↑ | `<…>` | `<…>` | `<Δ ± …>` | `<y/n>` |
| guardrail (quality) | `<groundedness / safety floor>` | ≥ floor | | | | |
| guardrail (business) | `<CSAT / revenue / latency / cost-per-task>` | ≥ floor | | | | |

- Alert/decide on the **CI lower bound**, not the point estimate (`EVL-13`). Check SRM / health (`T-137`).

## 4. Slice read
Worst slice: `<segment>` Δ `<…>`. Any slice regressed below floor? `<y/n>` (an aggregate win can hide a broken slice).

## 5. Verdict
- **Decision:** `<ship / hold / kill / iterate>` vs the pre-set rule.
- Offline↔online agreement: `<matched / gap>` — if gap, the eval set is unrepresentative → add cases (`AT-62`).
- If ship: go/no-go gates confirmed (`AT-54`: eval ✓ safety ✓ cost ✓ rollback ✓). If regress: rollback plan (`AT-53`) = `<…>`.

## Self-check
- [ ] Ship rule pre-registered · [ ] reported CIs, not bare points · [ ] guardrails (quality **and** business) checked · [ ] slices read · [ ] decision matches the pre-set rule (no goalpost-moving) · [ ] rollback ready.
