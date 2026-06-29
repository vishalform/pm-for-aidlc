# evals/ — self-test for pm-for-aidlc

This skill ships its own eval suite so it can be re-verified after any edit
(TDD-for-skills: a skill you didn't test is a skill you don't know works).

## Run

```bash
python evals/run_evals.py            # from the skill root
python evals/run_evals.py --verbose  # show each script's actual output
```

Exit code is non-zero if any auto-verified assertion fails, so this can run in CI.

The runner reports **AUTO-VERIFIED: N/N passed** for gate + routing + stats only.
`trigger_scenarios` are listed at the end for manual/subagent checks and are **not**
included in that count.

## What's tested

`evals.json` has four kinds of scenario (3 auto-verified + 1 manual):

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
- **trigger_scenarios** (manual / subagent): should-fire and should-NOT-fire prompts
  (near-misses like SaaS pricing, plain funnels, signup dashboards). Triggering depends on the
  model reading the `description`, so the runner prints these for a with/without-skill A/B.

## Extending

Add a scenario to the right array in `evals.json`. Gate: give `task_id` (or `axes`) +
`expect_mode`/`expect_mode_not` + `expect_controls_include`/`_exclude` (+ `expect_blast`/
`expect_gate_metric`). Routing: `prompt` + `expect_task_ids_any` + `expect_cluster_contains`
(+ `top`, `expect_weak_match`). Stats: `cmd` (use `FIXTURES/...`) + `expect_exit` (+
`expect_json`). Re-run; keep it green.

For full TDD-style pressure testing (does a fresh agent comply under time/authority
pressure), run a with-skill vs without-skill subagent on the trigger prompts and grade
against the gate/routing expectations here.
