# Team overrides (example)

Optional defaults for your org. Copy to `CONFIG.md` (gitignored locally) or encode in your
agent's project rules. Upstream skill defaults are conservative; override only with intent.

These keys map to script flags and governance policy — not all are wired to a loader yet;
treat this as the canonical contract for team customization.

## Routing (`select_task.py`)

| Key | Default | Maps to | Notes |
|---|---|---|---|
| `select_task_floor` | `9.0` | `--floor` | Below this top score, print the §7 escape-hatch (weak match). |
| `default_top_n` | `8` | `--top` | Candidate tasks returned per query. |

## Autonomy gate (`autonomy_gate.py`)

| Key | Default | Maps to | Notes |
|---|---|---|---|
| `blast_default_when_unknown` | `unknown` | (implicit) | When blast is missing from the bundle, gate refuses `run_unattended`. |
| `require_blast_explicit` | `true` | `--blast` required for unattended | Agent must pass `--blast` to authorize unattended when blast is unknown. |

## Judge validation (`judge_validation.py`)

| Key | Default | Maps to | Notes |
|---|---|---|---|
| `judge_min_ci_lower` | `0.9` | `--threshold` with `--gate-on ci_lower` | TPR & TNR CI lower bound for `TRUSTED`. |
| `judge_min_labels` | `5` | `--min-per-class` | Minimum labels per class before validation is trusted. |
| `gate_on` | `ci_lower` | `--gate-on` | `ci_lower` (recommended) or `point`. Never use `point` to "just get TRUSTED". |

## Eval gate (`eval_gate.py`)

| Key | Default | Maps to | Notes |
|---|---|---|---|
| `alert_on` | `ci_lower` | bar `min_ci_lower` | Gate on the CI **lower** bound, not the point estimate. |
| `paired_regression_required` | `true` | baseline regression | When `--baseline` is supplied, regressions must use paired McNemar/permutation by `case_id`. |

## MCP governance (AT-26)

| Key | Default | Notes |
|---|---|---|
| `mcp_policy` | `org_registry_only` | Only servers from the organization-approved MCP registry. |
| `mcp_allowlist` | `[]` | Optional explicit server IDs/names your org has vetted (empty = follow registry policy). |

## Trigger eval tiers

| Tier | Mechanism | CI | API keys |
|---|---|---|---|
| **Tier 1** (default) | `evals/trigger_classifier.py` — rule-based proxy parsing `SKILL.md` trigger/NOT phrases | Yes — auto-verified by `run_evals.py` | None |
| **Tier 2** (future / optional) | LLM-judge with/without-skill A/B on `trigger_scenarios` | No — manual or custom pipeline | Required |

Tier 1 catches near-miss anti-triggers (SaaS pricing, signup funnels, AWS AI-DLC coding agent) and
positive AI-system signals (eval, hallucination, jailbreak, groundedness, cost/quality dashboards).
It does **not** prove a live model will always fire correctly — run Tier 2 before high-stakes rollout.

### Tier 2 config (optional, not wired in CI)

| Key | Default | Notes |
|---|---|---|
| `trigger_eval_enabled` | `false` | Set true only when running manual/subagent A/B (Tier 2). |
| `trigger_eval_model` | (unset) | Model for with/without-skill A/B on trigger prompts; requires API key. |

## Example (YAML-style)

```yaml
select_task_floor: 9.0
default_top_n: 8

blast_default_when_unknown: unknown
require_blast_explicit: true

judge_min_ci_lower: 0.9
judge_min_labels: 5
gate_on: ci_lower

alert_on: ci_lower
paired_regression_required: true

mcp_policy: org_registry_only
mcp_allowlist: []

trigger_eval_enabled: false   # Tier 2 only
trigger_eval_model: null      # e.g. gpt-4o — requires API key
```
