# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/); this project uses the `version` field in
`SKILL.md` frontmatter.

## [1.0.0] — 2026-06-28

First public release. A complete, self-contained, eval-driven operator skill for AI product
management on the AI system itself (the AIDLC: evals, prompts, RAG, agents, the training
flywheel, delivery, monitoring, safety, inference economics).

### Highlights
- **Router + 6-axis autonomy gate** turning the 102-task `AT-`/`EVL-` library into executable
  behavior (route → gate → overlay → loop → stats → tools).
- **9 stdlib-only scripts**: `select_task`, `autonomy_gate`, `eval_stats`, `judge_validation`,
  `contamination_check`, `trace_cluster`, `eval_gate`, `cost_calc`, `build_axes`.
- **11 cluster playbooks**, the task catalog, 16 use-case playbooks, the schema/autonomy spec,
  and reasoning heuristics under `references/`.
- **49-scenario self-test suite** with negative safety guards, golden-value math checks, and
  CI on every push.

### Hardened before release (adversarial review + LLM-judge loop)
This release shipped only after two rounds of red-teaming and an LLM-as-judge pass:
- **Autonomy safety:** an actuating `safety:high` task can never run unattended — the read-only
  monitor carve-out must be *asserted* (bundle/`--actuation`), never inferred from low blast;
  an unknown blast never authorizes an unattended run.
- **Paired statistics:** `eval_stats compare` and the `eval_gate` regression check are paired by
  default (McNemar / paired bootstrap), and `eval_gate` flags candidate **coverage gaps** so a
  candidate that drops the cases it fails cannot silently flip NO-GO → GO.
- **Judge certification:** `judge_validation` certifies on the full-set CI lower bound and tells
  you the exact label count needed — reachable at the prescribed 50–100 labels for a strong judge.
- **Routing:** incident-language paraphrases route to Safety; homographs ("memory leak",
  "dependency injection") do not.
- **Contamination:** template-leak hits warn (non-blocking) by default; exact/near-dup block.

[1.0.0]: https://github.com/vishalform/pm-for-aidlc/releases/tag/v1.0.0
