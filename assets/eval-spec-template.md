# Eval Spec — `<capability name>`

> The eval **is** the PRD. Fill this instead of (or alongside) a classic PRD for any non-deterministic capability. Backs `AT-08` (rubric), `AT-09`/`EVL-11` (dataset), `AT-16` (bar). One dimension per scorer.

## 1. Task definition (one precise sentence)
The system takes `<input>` and produces `<output>`. "Good" means: `<one-sentence definition of correct>`.

- Use case (if any): `<UC-id + name>` · dominant failure mode to guard: `<...>`
- Owner (PM): `<name>` — the rubric is human-led; do not delegate the definition of "good".

## 2. Dataset (the new user research)
| split | source | # cases | frozen version | leakage-checked? |
|---|---|---|---|---|
| representative | `<prod traces / EVL-06>` | `<n>` | `<v>` | `<y/n>` |
| hard | `<...>` | `<n>` | `<v>` | `<y/n>` |
| adversarial / incident-repro | `<AT-17 / EVL-11>` | `<n>` | `<v>` | `<y/n>` |

- Each case has a labeled **expected behavior**. Splits are **frozen** so scores are comparable over time.

## 3. Scorers (one dimension each)
| # | dimension | type | scorer | pass criterion | validated? |
|---|---|---|---|---|---|
| 1 | `<format/schema/exact-match>` | code (`AT-10`/`EVL-07`) | `<file/check>` | `<deterministic>` | unit-tested |
| 2 | `<groundedness/tone/faithfulness>` | LLM-judge (`AT-11`) | `<judge prompt>` | `<score ≥ x>` | TPR/TNR vs human (`EVL-08`) |

- Prefer **code** wherever code can verify. A judge is **untrusted until calibrated** (see judge-validation below). Allow an **"Unknown"** verdict.

### Judge validation (per LLM-judge)
- Human labels collected: `<N>` (script prints the N needed, ~70+) · **TPR** `<...>` / **TNR** `<...>` (or κ `<...>`).
- Certified by `judge_validation.py` on the **full-set CI lower bound** ≥ `<0.9>` → verdict `<TRUSTED>`; 75/25 split reported as an overfit check.
- Recalibration cadence: `<e.g., monthly / on input-mix shift>` (`EVL-09`).

## 4. Slices (quality is a distribution)
Report per: `<input type / length / language / segment / doc type / risk tier>`. Worst slice must clear `<floor>` — an aggregate pass can hide a broken slice (`AT-14`).

## 5. The release bar (pre-register before seeing results — `AT-16`)
| gating metric | threshold + CI | guardrail floor |
|---|---|---|
| `<primary quality>` | `<≥ x, 95% CI lower bound>` | — |
| groundedness / safety | — | `<hard floor, no-go if breached>` |
| cost-per-task | `<≤ $x>` | — |

- Bar is **locked before the change**; moving it requires a logged sign-off.

## 6. Wiring
- In CI (`AT-49`/`EVL-12`): `<assertions first, judges where needed; fail build on regression>`
- Online scoring (`AT-55`/`EVL-13`): `<reference-free scorers, sample rate, alert on CI lower bound>`
- Version + changelog (`AT-15`): `<suite version id>`

## Pitfalls to self-check
- [ ] No lumped multi-dimension scorers · [ ] real-data examples (not happy-path) · [ ] splits frozen + leakage-checked · [ ] judge calibrated · [ ] bar pre-registered · [ ] worst slice checked.
