# evals/ — self-test for pm-for-aidlc

This skill ships its own eval suite so it can be re-verified after any edit
(TDD-for-skills: a skill you didn't test is a skill you don't know works).

## Run

```bash
python evals/run_evals.py            # from the skill root
python evals/run_evals.py --verbose  # show each script's actual output
python evals/trigger_classifier.py   # trigger scenarios only (Tier 1)
```

Exit code is non-zero if any auto-verified assertion fails, so this can run in CI.
No API keys required — all auto-verified sections use stdlib Python + bundled scripts.

## What's tested

`evals.json` has four kinds of scenario (all four auto-verified in CI):

- **gate_scenarios** (auto-verified): a read (by `task_id` from the bundle, or explicit
  `axes` + `actuation`/`modality`/`risk_tier`) → expected `autonomy_gate.py` mode, controls,
  blast, and gate_metric. These include **negative guards** (`NEG-*`) that assert a *dangerous
  combo is blocked* — they are regression guards for the hardened fixes and MUST fail if the
  fix is reverted (verified: reverting C1/C2/M3 turns the matching `NEG-*` red):
  - `NEG-actuating-safety-high` / `-irreversible` → an actuating safety:high task must **not** be `run_unattended` (C1).
  - `NEG-blast-unknown-not-unattended` → an omitted blast must **not** authorize unattended (C2).
  - `NEG-regr-high-eval-none-build-first` → emits `build_eval_first`, not a phantom `eval_gate` (M3).
- **routing_scenarios** (auto-verified): free-text → expected candidate id(s)/cluster from
  `select_task.py`, including **safety paraphrases** (prompt-injection/PII → Safety) and a
  **weak-match** negative (`expect_weak_match`).
- **stats_scenarios** (auto-verified): shells `eval_stats`/`judge_validation`/`contamination`
  and checks exit codes + JSON. These catch the math/validation bug classes — e.g.
  `eval_stats selftest` and the `passk c>n` guard (pass^k), and the judge under-powered →
  `NOT VALIDATED` fixture (H1). Fixtures live in `evals/fixtures/`.
- **trigger_scenarios** (Tier-1 auto-verified): should-fire and should-NOT-fire prompts
  checked by `trigger_classifier.py`. The classifier parses trigger/NOT phrases from `SKILL.md`
  frontmatter and matches AI-system concepts (eval, safety, groundedness, measurement) vs
  near-miss anti-triggers (SaaS pricing, signup funnels, discovery interviews, AWS AI-DLC).
  **Tier 2** (LLM-judge with/without-skill A/B) is optional/future — see `CONFIG.example.md`.

### trigger_classifier approach

1. Parse `SKILL.md` `description` for the `Triggers:` list and `NOT for` clause.
2. Score each prompt against curated positive patterns (eval, hallucination, jailbreak,
   groundedness, cost/latency/quality for an agent, etc.) and anti-patterns (seat pricing,
   signup funnel, customer discovery interview, AI coding agent to refactor faster).
3. Compare predicted `should_trigger` to each scenario's expected flag.

This is a **proxy** — it guards the skill's documented trigger contract in CI but does not
replace a live model A/B. Use `--skip-triggers` on `run_evals.py` to omit trigger checks.

## Extending

Add a scenario to the right array in `evals.json`. Gate: give `task_id` (or `axes`) +
`expect_mode`/`expect_mode_not` + `expect_controls_include`/`_exclude` (+ `expect_blast`/
`expect_gate_metric`). Routing: `prompt` + `expect_task_ids_any` + `expect_cluster_contains`
(+ `top`, `expect_weak_match`). Stats: `cmd` (use `FIXTURES/...`) + `expect_exit` (+
`expect_json`). Trigger: `prompt` + `should_trigger` + `reason`. Re-run; keep it green.

For full behavioral pressure testing (does a fresh agent comply under time/authority
pressure), run a with-skill vs without-skill subagent on the trigger prompts (Tier 2).
