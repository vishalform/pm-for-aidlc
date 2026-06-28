# scripts/ — runnable tools for pm-for-aidlc

Deterministic work (task lookup, autonomy gating, statistics, judge validation,
contamination, clustering, eval-gating, cost) lives here so it's correct and
token-free — only stdout returns to the agent. **The agent should EXECUTE these, not
read them as logic.**

- **Dependencies:** Python 3.8+ standard library only (no numpy/scipy/sklearn).
- **Data inputs:** scripts read the **bundled `data/` copy first** (`aidlc_microtasks.csv`,
  `aidlc-usecases.csv`, generated `aidlc_axes.csv`), then fall back to `Research/`. This
  makes the skill self-contained/portable. Override with `--csv` / `--aidlc-csv` /
  `--classic-csv` / `--usecase-csv`. (`--include-classic` still needs the classic CSV in
  `data/` or `Research/`, or pass `--classic-csv`.)
- **No fabrication:** every script reads only the files/flags you pass; nothing is invented.
- `_common.py` is a shared helper (path discovery, bundle load, tokenize/shingle). Not a CLI.

Run any script with `--help` for the full flag list.

---

## build_axes.py — generate the bundled 6-axis catalog (maintenance)
`blast` is the only axis not in `aidlc_microtasks.csv`; it is curated in
`references/task-catalog.md`. This parses all six axes from the catalog, **cross-checks
the five CSV axes and fails on any drift**, and writes `data/aidlc_axes.csv` (what the
gate reads). Run after editing the catalog or the CSV.
```bash
python build_axes.py            # writes data/aidlc_axes.csv (102 tasks)
python build_axes.py --check    # verify only; non-zero exit on drift
```

## select_task.py — request → candidate task ids
Keyword scoring **+ a curated concept prior** (incident language → Safety; "every number"
→ groundedness AT-56; "PRD" → eval hub AT-08). Returns ranked candidates with their
6-axis read incl. **blast** (from the bundle). A weak top score (< `--floor`, default 9)
prints the §7 escape-hatch.
```bash
python select_task.py "someone tricked the bot into ignoring its instructions"
python select_task.py "the eval score dropped, find the root cause" --top 5
python select_task.py --usecase UC-04     # AIDLC (gate-ready) vs classic ids, split
```
Filters: `--phase --cluster --leverage --status(now|later) --top --floor --json`.

## autonomy_gate.py — schema read → execution verdict
Turns the 6 axes (+ `actuation`) into `run_unattended | draft_then_confirm | human_led`
+ controls. Implements `references/schema-and-autonomy.md` exactly.
```bash
python autonomy_gate.py --id AT-56                       # all 6 axes incl. blast from the bundle
python autonomy_gate.py --id AT-65 --actuation irreversible
python autonomy_gate.py --id AT-30 --modality multi-agent --risk-tier external-high-stakes
python autonomy_gate.py --leverage autonomous --blast low --eval gated \
    --regr high --safety high --fly consumer --actuation read-only --json
```
Key behavior: **`blast` comes from the bundle on `--id`**; if genuinely unknown the gate
**refuses to authorize an unattended run** (pass `--blast`). A `safety:high` **actuator**
never runs unattended — only a read-only gated monitor does, and **read-only must be
asserted** (the bundle marks AT-56; or pass `--actuation read-only`). When `--actuation`
is omitted it defaults to **`reversible`**, so a low-blast safety actuator is held for a
human (never inferred read-only). `safety=med` adds a `safety_gate` (no human downgrade).
`--modality`/`--risk-tier` recompute on tightened axes and set `gate_metric` (`pass^k` for high-stakes).

## eval_stats.py — statistics (stdlib only)
```bash
python eval_stats.py ci --scores 1,0,1,1,0,1,1,1,0,1      # mean + bootstrap/Wilson CI
python eval_stats.py compare --a base.txt --b cand.txt    # PAIRED by default (McNemar/paired bootstrap)
python eval_stats.py compare --a x.txt --b y.txt --unpaired   # only for independent samples
python eval_stats.py passk --n 8 --c 5 --k 1,8            # pass@k vs pass^k (guards 0<=c<=n)
python eval_stats.py power --p0 0.80 --mde 0.05           # required n per group (pooled SE)
python eval_stats.py judge --tp 40 --fp 6 --tn 44 --fn 10 # confusion → TPR/TNR/κ
python eval_stats.py selftest                             # golden-value regression checks
```
`compare` is **paired by default** (same frozen eval set under A vs B): McNemar's exact test
for binary, paired bootstrap of per-item deltas — an unpaired test pools the two and loses
power (and misses real paired regressions). `selftest` exits non-zero if the math drifts
(incl. the `pass^k(c>n)` guard and the paired/McNemar checks).

## judge_validation.py — align an LLM judge vs human labels
```bash
python judge_validation.py --labels labels.csv                 # gates on the CI LOWER bound
python judge_validation.py --labels labels.json --gate-on point --json
```
Certifies on the **full labeled set's CI lower bound** by default (every label counts; the
dev/test split is reported only as an overfit check). Verdict `TRUSTED` / `NOT VALIDATED` /
`INSUFFICIENT`; a perfect point estimate on too-few labels is NOT VALIDATED and the tool
prints the **exact N** needed (e.g. ~70 to certify a perfect judge at 0.9). This makes the
50-100-label loop able to certify a strong judge. `--gate-on point` / `--min-per-class` (default 5).

## contamination_check.py — train/eval overlap
```bash
python contamination_check.py --train train.txt --eval eval.txt
python contamination_check.py --train t.csv --eval e.csv --text-col prompt --token-threshold 0.6 --json
```
Three channels: exact + char-shingle near-dup (`--threshold`) are **HARD** (real leakage →
**exit 2**); token-Jaccard **template-leak** (`--token-threshold`) is lexical and noisy on
short text, so it **WARNs (exit 0)** by default — pass `--strict-template` to make it block
too. Lexical proxy; add an embedding pass for production.

## trace_cluster.py — cluster failure traces into ranked modes
```bash
python trace_cluster.py --input notes.txt
python trace_cluster.py --input traces.csv --text-col note --severity-col sev --threshold 0.25
```
Advisory TF-IDF clustering. Never quote `rank_score` as a measured rate — confirm counts by
labeling against the validated taxonomy (EVL-05); the human validates/renames.

## eval_gate.py — run a pre-registered eval gate (CI)
```bash
python eval_gate.py --results results.jsonl --bar bar.json [--baseline base.jsonl]
```
`results.jsonl`: `{"case_id","metric","score","slice"}` per line. `bar.json`: per-metric
`min_ci_lower` / `min` / `max` / `guardrail`, plus `worst_slice`. Gates on the **CI lower
bound** and the **worst slice**. The optional `--baseline` regression check is **paired by
case_id** (McNemar/paired permutation) — so it catches a candidate that regresses on a
subset of cases even when the aggregate bar still passes. **Exit 0 GO / 1 NO-GO.**

## cost_calc.py — inference unit economics
```bash
python cost_calc.py per-task --in-tok 1800 --out-tok 350 --in-price 3.0 --out-price 15.0 --calls 4 --price 0.25
python cost_calc.py margin --price 0.25 --cost 0.04
python cost_calc.py frontier --data models.tsv --quality-floor 0.8   # cols: model quality cost
python cost_calc.py tail --cost-per-task 0.04 --tasks-per-user 30 --users 50000 --price-per-user 20 --growth 30
python cost_calc.py selftest                          # golden cost-math checks (incl. margin inversion)
```
Prices user-supplied (per 1M tokens unless `--per-1k`). Surfaces negative/inverting margins.
`selftest` exits non-zero if the cost math drifts.
