# Team overrides (example)

Optional defaults for your org. Copy to `CONFIG.md` (gitignored locally) or encode in your
agent's project rules. Upstream skill defaults are conservative; override only with intent.

## Trigger eval tiers

| Tier | Mechanism | CI | API keys |
|---|---|---|---|
| **Tier 1** (default) | `evals/trigger_classifier.py` — rule-based proxy parsing `SKILL.md` trigger/NOT phrases | Yes — auto-verified by `run_evals.py` | None |
| **Tier 2** (future / optional) | LLM-judge with/without-skill A/B on `trigger_scenarios` | No — manual or custom pipeline | Required |

Tier 1 catches near-miss anti-triggers (SaaS pricing, signup funnels, AWS AI-DLC coding agent) and
positive AI-system signals (eval, hallucination, jailbreak, groundedness, cost/quality dashboards).
It does **not** prove a live model will always fire correctly — run Tier 2 before high-stakes rollout.

### Tier 2 config (optional, not wired in CI)

```yaml
trigger_eval_enabled: false   # set true only when running manual/subagent A/B
trigger_eval_model: null      # e.g. gpt-4o — requires API key; future runner
```
