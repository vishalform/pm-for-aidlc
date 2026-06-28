# Error-Analysis / Trace-Coding Sheet

> The look-at-your-data loop, `EVL-02`→`EVL-06`. Open-coding (`EVL-03`) is the irreducible **human** step — do not delegate it to an LLM. Categories come *after* reading, not before.

## 0. Sample (EVL-02 — smart, not random)
- Window: `<dates>` · target size: `<~100>` · biased to: negative feedback + outliers + known clusters.
- Stratified by segment: `<...>`. (Random sampling wastes review on the boring middle.)

## 1. Open-coding pass (EVL-03 — human, free-text, no categories yet)
For each trace, read it **fully** and note the **first thing that went wrong** (the first *upstream* failure, not the last symptom).

| # | trace link | pass/fail | first-failure note (free text) | repro settings (seed/temp) |
|---|---|---|---|---|
| 1 | `<link>` | `<P/F>` | `<what went wrong, in plain words>` | `<seed=…, temp=…>` |
| 2 | | | | |
| … | | | | |

## 2. Axial coding (EVL-04 — LLM proposes clusters, human names them)
Cluster the notes into **5–10 named failure modes**, each with a one-line definition. Keep modes non-overlapping.

| mode name | one-line definition |
|---|---|
| `<e.g., over-confident causal claim>` | `<...>` |
| … | |

## 3. Quantify + triage (EVL-05)
Label every sampled trace against the taxonomy; count; rank by frequency × severity; route each mode.

| mode | count | rate % | severity | route → fix / assertion (`EVL-07`) / judge (`EVL-08`) / guardrail (`AT-65`) / monitor |
|---|---|---|---|---|
| `<mode>` | `<n>` | `<%>` | `<hi/med/lo>` | `<route>` |

## 4. From-prod dataset (EVL-06)
- Add confirmed failures (with note + label) to the dataset; de-dup; **freeze** the versioned split: `<id>`.
- Leakage vs training checked? `<y/n>` (`AT-47`).

## 5. Hand-off
- Novel failure modes → roadmap / capability map (`AT-04`). Incident-class failures → regression cases (`AT-17`).
- Multi-step agent? Build the transition-failure matrix to localize *where* it breaks (`EVL-15`).

## Self-check
- [ ] Sample failure-biased, not random · [ ] open-coded the **first** failure, read in full · [ ] ≤10 non-overlapping modes · [ ] counted before acting · [ ] not every mode routed to "fix" · [ ] dataset frozen.
