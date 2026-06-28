# Autonomy-Gate Decision Record — `<task id / change>`

> Captures *how* a task may be executed, from its 6-axis read. The canonical gate rules live in `references/schema-and-autonomy.md`; this record is the artifact you emit per decision. The key inversion: **`eval` gates `autonomy`** — an ungraded autonomous task is the dangerous quadrant.

## 1. The task
- Task: `<AT-/EVL- id + name>` (look up in `references/task-catalog.md`)
- Change being made: `<prompt edit / model swap / dataset update / config / ship>`
- Use case / surface: `<UC-id>` · risk tier: `<internal / external-low-stakes / external-high-stakes>`

## 2. The read (6 axes + actuation; from the catalog, confirm for this instance)
| axis | value | note |
|---|---|---|
| autonomy (how-automatable) | `<human-led / copilot / autonomous>` | |
| blast (reversibility) | `<low / med / high / unknown>` | from `data/aidlc_axes.csv`; unknown never runs unattended |
| eval-coverage | `<gated / partial / none>` | a grader exists & is judge-validated? |
| regression risk | `<low / med / high>` | can a quiet change shift the distribution? |
| safety exposure | `<none / med / high>` | jailbreak / abuse / PII? |
| flywheel linkage | `<none / consumer / producer>` | writes into the data loop? |
| actuation | `<read-only / reversible / irreversible>` | does it observe, or act? |

## 3. Decision (apply the rules)
Reference rules (`schema-and-autonomy.md`), summarized:
- `autonomous + blast:low + eval:gated` → **run unattended** (read-only or no safety/producer risk).
- `autonomous|copilot + eval:none|partial` → **never unattended → draft for human review** (the inversion).
- any `regression:high` → **eval-gate + canary/shadow** (or **build the grader first** if `eval:none`), even if blast looks low.
- `safety:high` **actuating** (reversible/irreversible) → **human confirm + safety gate** — *the decision stays human*. The ONLY carve-out: a **read-only, gated monitor** (e.g. AT-56) may run unattended.
- `flywheel:producer` → **provenance logging**; **+ human confirm** unless a trusted gate (`eval:gated`) catches the compounding error.
- `blast:high` or `blast:unknown` → **human confirm** (unknown: supply the real blast first).

**Execution mode chosen:** `<run unattended | draft-then-confirm | human-led>`
**Required gates before acting:** `<eval bar AT-16 / CI EVL-12 / canary AT-51 / safety gate AT-68 / rollback ready AT-50,AT-53>`
**Rationale (1–2 lines):** `<why this mode, citing the binding axis>`

## 4. Provenance (if flywheel:producer or safety:high)
- What is captured / written: `<dataset, labels, traces>` · consent/PII checked (`AT-72`/`AT-85`): `<y/n>`
- Reviewer / approver: `<name>` · timestamp: `<...>`

## Self-check
- [ ] Did not let low blast override `eval:none` (the inversion) · [ ] high regression routed through a real gate (or `build_eval_first` if ungraded) · [ ] safety:high **actuator** got human confirm (only a read-only gated monitor runs unattended) · [ ] producer got provenance logging · [ ] blast was a real value, not unknown · [ ] rollback path exists for any shipping change.
