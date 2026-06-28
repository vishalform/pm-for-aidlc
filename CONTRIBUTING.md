# Contributing to pm-for-aidlc

Thanks for improving the skill. It is a working artifact for coding agents, so the bar is:
**no behavior change ships without a self-test that would catch its revert.** This is the
same discipline the skill teaches ("you can only safely automate what you can grade"),
applied to itself.

## Ground rules

- **Python standard library only.** No numpy/scipy/sklearn. Scripts must run on Python 3.8+
  with no install step (CI does not `pip install`).
- **Scripts are executed, not read as logic.** Keep them deterministic, `--json`-friendly,
  and self-explaining (`--help`). Every threshold is a documented flag, never a magic number.
- **Progressive disclosure.** `SKILL.md` stays a lean router; heavy material lives in
  `references/` (one level deep). Don't inline a playbook into the router.
- **No fabricated data.** Tasks, axes, tools, and citations must trace to the catalog or a
  real source. Mark concept tags as `concept:…`, not as fake URLs.

## Run the self-tests before and after any change

```bash
python evals/run_evals.py            # 49/49 auto-verified (gate + routing + stats)
python scripts/eval_stats.py selftest
python scripts/cost_calc.py selftest
python scripts/build_axes.py --check  # axis bundle is consistent with the catalog + CSV
```

CI runs all four on every push (`.github/workflows/ci.yml`). A red suite blocks the change.

## Adding or editing an `AT-`/`EVL-` task

1. Edit the task definition in `data/aidlc_microtasks.csv` (the 5 CSV-backed axes:
   `ai_leverage, eval_coverage, regression_risk, safety_exposure, flywheel_linkage`) and the
   matching entry in `references/task-catalog.md` (which also carries `blast`).
2. Regenerate the 6-axis bundle the gate reads:
   ```bash
   python scripts/build_axes.py        # writes data/aidlc_axes.csv (cross-checks; fails on drift)
   ```
   `build_axes.py` fails if the catalog and CSV disagree on any of the 5 shared axes — fix the
   mismatch, don't override it.
3. If the task is a genuine **read-only, autonomous, `safety:high` monitor** (today only
   AT-56), add its id to `READ_ONLY_TASKS` in `build_axes.py` so its read-only actuation is
   *asserted*, never inferred.
4. Re-run the self-tests.

## Changing autonomy-gate logic

`scripts/autonomy_gate.py` implements `references/schema-and-autonomy.md` exactly. If you
change a rule:
- Update the reference doc and the worked-examples table together.
- Add a **negative guard** to `evals/evals.json` `gate_scenarios` that asserts the *invariant*
  (e.g. `expect_mode_not: run_unattended`), not the current output — so a future revert fails
  the suite. Confirm it would by temporarily reverting your change and watching it go red.

## Changing a statistic or the router

- Stats: add a golden-value case to the relevant `selftest` and a `stats_scenario` to the
  suite. Prefer paired tests for same-eval-set A/B.
- Router (`select_task.py`): add both a positive and a **held-out** negative routing scenario
  (use phrasing that is *not* the literal trigger string, so you test the capability, not the
  lookup table).

## Pull requests

Keep PRs focused. In the description, state the behavior change, the guard that now protects
it, and paste the `run_evals.py` summary line. Surgical diffs only — match the existing style.
