# Task Catalog — every task `pm-for-aidlc` can invoke

> Navigable index of all **324** tasks: **102 AIDLC** tasks (`AT-01`–`AT-86`, `EVL-01`–`EVL-16`) with the full 6-axis read, plus the **222 classic** PM tasks (`T-001`–`T-152` + 70 `O-*` domain overlays) they map back to. Generated faithfully from `Research/aidlc_microtasks.csv` and `Research/pm_microtask_database.csv` — no task, tool, or axis is invented. Benchmark/model figures elsewhere in the skill are marked *verify current*.

This file is **Level-3 reference**: `SKILL.md` routes here to look up a task, then sends you to the matching cluster playbook for the method. To run a task safely, read its 6-axis line, then apply the autonomy gate (see `schema-and-autonomy.md`).

## How to read an entry

Each AIDLC entry carries:
- **Steps** — the method in one line (the cluster playbook expands it).
- **Tools** — `tools_in_practice` from the sheet (representative, not mandatory).
- **Axes** — the 6-axis read that drives the autonomy decision:
  - `autonomy` (how-automatable): `human-led` → `copilot` → `autonomous`.
  - `blast` (reversibility of the action): `low` / `med` / `high`.
  - `eval` (eval-coverage — the new gate): `gated` (a grader exists, can be trusted to run) / `partial` / `none` (a human must look).
  - `regression` (can a quiet change silently shift the output distribution?): `low` / `med` / `high`.
  - `safety` (touches jailbreak, abuse, or PII?): `none` / `med` / `high`.
  - `flywheel` (does it write into the data loop, where one bad label compounds?): `none` / `consumer` / `producer`.
- **Classic** — the `T-`/`O-` task(s) this keeps/modifies/supersedes (look them up in the Classic index below).
- **Core rule** — the one-line reasoning heuristic for the task.

**The autonomy inversion to remember:** an *ungraded* autonomous task is the dangerous quadrant — never run unattended no matter how low its blast radius. `eval` gates `autonomy`, not the other way around.

## Clusters

1. **Discovery & Capability Mapping** (7) → [`discovery-playbook.md`](discovery-playbook.md)  
   <sub>AT-01, AT-02, AT-03, AT-04, AT-05, AT-06, AT-07</sub>
2. **Eval & Spec Definition (hub)** (22) → [`eval-spec-playbook.md`](eval-spec-playbook.md)  
   <sub>AT-08, AT-09, AT-10, AT-11, AT-12, AT-13, AT-14, AT-15, AT-16, AT-17, AT-18, EVL-02, EVL-03, EVL-04, EVL-05, EVL-06, EVL-07, EVL-08, EVL-09, EVL-10, EVL-11, EVL-12</sub>
3. **System & Agent Design** (14) → [`system-agent-playbook.md`](system-agent-playbook.md)  
   <sub>AT-19, AT-20, AT-21, AT-22, AT-23, AT-24, AT-25, AT-26, AT-27, AT-28, AT-29, AT-30, AT-31, AT-32</sub>
4. **Data & Training Flywheel** (16) → [`training-flywheel-playbook.md`](training-flywheel-playbook.md) · *Phase-2 (`later`)*  
   <sub>AT-33, AT-34, AT-35, AT-36, AT-37, AT-38, AT-39, AT-40, AT-41, AT-42, AT-43, AT-44, AT-45, AT-46, AT-47, AT-48</sub>
5. **Delivery & Release** (6) → [`delivery-playbook.md`](delivery-playbook.md)  
   <sub>AT-49, AT-50, AT-51, AT-52, AT-53, AT-54</sub>
6. **Measurement & Monitoring** (13) → [`measurement-playbook.md`](measurement-playbook.md)  
   <sub>AT-55, AT-56, AT-57, AT-58, AT-59, AT-60, AT-61, AT-62, EVL-01, EVL-13, EVL-14, EVL-15, EVL-16</sub>
7. **Safety, Red-teaming & Guardrails** (6) → [`safety-substrate.md`](safety-substrate.md)  
   <sub>AT-63, AT-64, AT-65, AT-66, AT-67, AT-68</sub>
8. **Inference Economics & Model Portfolio** (5) → [`inference-economics.md`](inference-economics.md)  
   <sub>AT-69, AT-70, AT-71, AT-72, AT-73</sub>
9. **Commercial & Stakeholder** (13) → [`commercial-playbook.md`](commercial-playbook.md)  
   <sub>AT-74, AT-75, AT-76, AT-77, AT-78, AT-79, AT-80, AT-81, AT-82, AT-83, AT-84, AT-85, AT-86</sub>

Then: [Classic task index](#classic-task-index-the-t--o-library) · 152 `T-*` invariants + 70 `O-*` overlays.

---

## 1. Discovery & Capability Mapping

*7 tasks · 7 `now` · method → [`discovery-playbook.md`](discovery-playbook.md)*

**AT-01 · Mine production traces into failure-mode clusters** · `now`  
Turn raw production agent runs into ranked, named failure-mode clusters that point to what to fix next.  
- Steps: Sample recent production traces → Group by failure type → Rank clusters by frequency x severity → Link representative exemplars → File novel failures to the eval dataset → Hand off the ranked queue  
- Tools: LangSmith · Langfuse · Arize Phoenix · Braintrust  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `low` · safety `med` · flywheel `consumer`  
- Classic: T-088, T-006 · Core rule: Failing traces are the roadmap; cluster into patterns, never react to one-offs; the production distribution always differs from staging.

**AT-02 · Run a capability-elicitation probe on a new model** · `now`  
Test whether a newly released model unlocks a use case the current model cannot do.  
- Steps: Define candidate task + inputs → Prompt across regimes (zero/few-shot, tools) → Score vs the incumbent model → Note capability + failure deltas → Decide unlock yes/no/needs-work  
- Tools: model playground · Braintrust · OpenAI/Anthropic consoles · OpenRouter  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `low` · safety `none` · flywheel `none`  
- Classic: net-new · Core rule: A new model is an opportunity surface, not just a swap; probe for net-new capability before re-pricing the roadmap.

**AT-03 · Triage a thumbs-down or negative-feedback event** · `now`  
Classify a single user-flagged bad output and route it to a fix or the dataset.  
- Steps: Read the flagged trace → Reproduce with seed/temperature → Classify the failure type → Add to the eval/regression dataset → Route to prompt/retrieval/tool/model owner  
- Tools: Langfuse · LangSmith · Braintrust · Zendesk  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `low` · safety `med` · flywheel `producer`  
- Classic: T-052, T-005 · Core rule: A thumbs-down is a labeled datapoint, not a complaint; reproduce before believing and capture it before it decays.

**AT-04 · Build a use-case to eval-gap map** · `now`  
Map desired product behaviors to existing evals and flag the ungraded ones before they regress.  
- Steps: Enumerate target use cases/behaviors → Map each to an existing eval → Flag behaviors with no coverage → Size the risk of each gap → Prioritize gaps to close  
- Tools: Braintrust · Promptfoo · spreadsheet  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `med` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: Ungraded behavior is unmanaged behavior; coverage gaps are where silent regressions hide.

**AT-05 · Competitive model or agent teardown on your eval set** · `now`  
Run a competitor model or agent through your own rubric to locate capability deltas.  
- Steps: Get competitor access → Run your eval set through it → Score vs your system → Note where it wins/loses → Decide borrow/counter/ignore  
- Tools: Braintrust · Promptfoo · OpenRouter  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `low` · safety `none` · flywheel `none`  
- Classic: T-007 · Core rule: Your eval set is the only fair comparison; public leaderboards measure someone else's task, not yours.

**AT-06 · Cluster negative feedback into quality themes** · `now`  
Cluster thumbs-down, edits, and complaints into ranked quality themes for the roadmap.  
- Steps: Pull the feedback window → Cluster by theme → Rank by frequency x severity → Link exemplars → Tag novel themes  
- Tools: Arize Phoenix · Enterpret · Dovetail · Braintrust  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `low` · safety `med` · flywheel `consumer`  
- Classic: T-005, T-145 · Core rule: The score is noise; the verbatims and edits are the signal about what to fix.

**AT-07 · Mine tool-call logs for unreliable tools** · `now`  
Find tools or MCP servers with high error, timeout, or misuse rates from trace spans.  
- Steps: Pull tool-call spans → Compute error+latency+timeout by tool → Rank the unreliable tools → Flag flaky/abused tools → Hand off for fix or replacement  
- Tools: OpenTelemetry traces · Helicone · Datadog LLM Obs · LangSmith  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `med` · safety `none` · flywheel `consumer`  
- Classic: T-085 · Core rule: A flaky tool quietly caps agent quality; reliability of the tool surface is a product metric, not just an ops one.

---

## 2. Eval & Spec Definition (hub)

*22 tasks · 22 `now` · method → [`eval-spec-playbook.md`](eval-spec-playbook.md)*

**AT-08 · Write the eval rubric or scoring function for a capability** · `now`  
Define what good means for an AI capability as a graded scoring function; the eval is the modern PRD.  
- Steps: Assemble real example inputs → Define the task the system performs → Write explicit one-dimension scoring criteria → Encode graded scores → Calibrate against human judgment → Version the rubric  
- Tools: Braintrust · Promptfoo · LangSmith · OpenAI Evals  
- Axes: autonomy `human-led` · blast `med` · eval `gated` · regression `high` · safety `med` · flywheel `producer`  
- Classic: T-046, T-029 · Core rule: The scoring function is the new PRD; the prompt is temporary, the eval is permanent; score one dimension per scorer or you cannot localize a regression.

**AT-09 · Curate a golden eval dataset from prod traces** · `now`  
Build the versioned dataset of representative and hard cases the eval suite runs against.  
- Steps: Sample representative + hard + adversarial cases → De-dup → Label expected behavior → Check leakage vs training → Version and freeze the split  
- Tools: Braintrust Datasets · Langfuse Datasets · Argilla  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: The dataset is the new user research; a frozen, representative split is what makes scores comparable over time.

**AT-10 · Design a single-dimension code-based scorer** · `now`  
Write a deterministic scorer that checks exactly one quality dimension (format, schema, exact-match).  
- Steps: Pick one dimension → Write the deterministic check → Unit-test the scorer on known cases → Register it in the suite  
- Tools: autoevals · Promptfoo · Python · Braintrust  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `med` · safety `none` · flywheel `producer`  
- Classic: net-new · Core rule: Use code for what code can check; one dimension per scorer keeps optimization trade-offs visible.

**AT-11 · Design an LLM-as-judge scorer and rubric** · `now`  
Build an LLM-judge scorer for nuanced qualities code cannot check (tone, faithfulness, helpfulness).  
- Steps: Write the judge prompt with good/bad examples → Use chain-of-thought scoring → Choose the judge model (often different from task model) → Pin the version  
- Tools: Braintrust · Arize Phoenix Evals · DeepEval  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: A judge prompt is product knowledge, not engineering; vague judge prompts produce vague scores; the judge can itself be wrong.

**AT-12 · Calibrate an LLM judge against human labels** · `now`  
Measure and maintain judge-to-human agreement so eval scores keep reflecting real quality.  
- Steps: Sample judged items → Collect human labels → Compute agreement (e.g., kappa) → Adjust the judge prompt → Re-measure on a holdout → Schedule recurring recalibration  
- Tools: Braintrust · Arize Phoenix · spreadsheet  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: T-124 · Core rule: Without calibration, scoring drift silently inflates or deflates results; the judge is an instrument that needs re-zeroing.

**AT-13 · Run an eval-coverage gap analysis** · `now`  
Find behaviors and slices with no automated grader before they regress in production.  
- Steps: List behaviors + slices → Map to evals → Flag gaps → Size each gap's risk → Recommend new evals  
- Tools: Braintrust · spreadsheet  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `med` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: You can only safely automate what you can grade; coverage is the precondition for autonomy.

**AT-14 · Build slice and segment evals** · `now`  
Score the system by input type, length, language, and user segment to catch localized regressions.  
- Steps: Define slices → Split the dataset → Run per-slice scoring → Flag the worst slices → Track slice trend  
- Tools: Braintrust · Arize Phoenix · warehouse SQL  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `med` · safety `none` · flywheel `none`  
- Classic: T-079 · Core rule: An aggregate pass can hide a broken slice; quality is a distribution, read it by segment.

**AT-15 · Version and changelog an eval suite** · `now`  
Snapshot and changelog the eval suite so score movements are attributable to suite vs system changes.  
- Steps: Snapshot the suite → Diff vs prior version → Note threshold/criteria changes → Tag the release  
- Tools: Braintrust · git  
- Axes: autonomy `autonomous` · blast `low` · eval `gated` · regression `med` · safety `none` · flywheel `none`  
- Classic: T-123 · Core rule: If the ruler changes silently you cannot tell improvement from measurement drift; version the ruler.

**AT-16 · Define the release quality bar (eval thresholds)** · `now`  
Pre-commit the exact eval thresholds that decide ship/hold for any model or prompt change.  
- Steps: Pick the gating metrics → Set pass thresholds + CIs → Set guardrail floors (safety, groundedness) → Lock the bar before the change → Document it  
- Tools: Braintrust · docs  
- Axes: autonomy `human-led` · blast `med` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: T-138, T-031 · Core rule: Pre-register the bar before data exists to prevent motivated reasoning at ship time; the gate is the eval, not a vibe.

**AT-17 · Author adversarial and regression eval cases from an incident** · `now`  
Turn a production failure into a permanent regression test so it never silently returns.  
- Steps: Take the failing trace → Minimize a reliable repro → Encode expected behavior → Add to the regression set → Confirm it fails pre-fix and passes post-fix  
- Tools: Braintrust · Promptfoo  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `high` · safety `med` · flywheel `producer`  
- Classic: T-053 · Core rule: Every incident is a free eval case; a fixed bug without a regression test is a bug waiting to recur.

**AT-18 · Run the weekly eval-score review** · `now`  
Hold a weekly team review of eval-score movement and regressions, not a feature demo.  
- Steps: Pull the week's eval scores → Flag regressions + wins → Tie each move to a change → Assign follow-ups → Update the bar if needed  
- Tools: Braintrust · Slack · spreadsheet  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `med` · safety `none` · flywheel `none`  
- Classic: T-073 · Core rule: The flywheel is the new sprint cycle; demo scores weekly so regressions surface in days, not quarters.

**EVL-02 · Pull a smart trace sample for review** · `now`  
Assemble ~100 high-yield traces for review, biased to failures and outliers, not a random sample.  
- Steps: Choose the window → Bias to negative-feedback + outliers + known clusters → Stratify by segment → Export for review  
- Tools: Langfuse · Arize Phoenix · notebook  
- Axes: autonomy `autonomous` · blast `low` · eval `partial` · regression `low` · safety `med` · flywheel `consumer`  
- Classic: net-new · Core rule: Random sampling wastes review on the boring middle; a stratified, failure-biased sample is where the signal lives.

**EVL-03 · Run an open-coding pass** · `now`  
Read each trace and write a free-text note on the first thing that went wrong, before any categories exist.  
- Steps: Read the full trace → Note the first upstream failure in free text (no categories) → Mark pass/fail → Save the note  
- Tools: custom annotation viewer · notebook  
- Axes: autonomy `human-led` · blast `low` · eval `none` · regression `low` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: Open coding is the irreducible look-at-your-data step; categories imposed too early blind you to the failure you did not expect.

**EVL-04 · Axial-code notes into a failure taxonomy** · `now`  
Cluster the open-coding notes into ~5-10 named, defined failure modes.  
- Steps: Gather all notes → LLM first-pass clustering → Human-validate the clusters → Write a one-line definition per mode  
- Tools: notebook + LLM · spreadsheet  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `med` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: The taxonomy is the vocabulary the team argues in; the LLM proposes clusters, the human owns the names and boundaries.

**EVL-05 · Quantify failure rates and triage each mode** · `now`  
Label all sampled traces against the taxonomy, count each mode, and decide fix vs assertion vs judge vs guardrail.  
- Steps: Label every trace vs the taxonomy → Count the rate per mode → Rank by frequency x severity → Assign each mode to fix / assertion / judge / guardrail  
- Tools: spreadsheet · Braintrust · Langfuse  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `med` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: Counting turns anecdotes into priorities; the triage decision is what routes each mode into the rest of the loop.

**EVL-06 · Build a from-prod failure dataset** · `now`  
Turn confirmed production failures into a labeled, versioned dataset of eval cases.  
- Steps: One-click add failing traces → Attach the note + label → De-dup → Version and freeze the split  
- Tools: Braintrust Datasets · Langfuse Datasets  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: Confirmed failures are the highest-value eval cases; a frozen labeled split is what proves a fix and prevents the regression.

**EVL-07 · Write a code or assertion grader** · `now`  
Write a deterministic check for a code or structured output - schema, exact-match, execution, or tool-argument.  
- Steps: Pick one dimension → Write the check (schema/match/exec/tool-arg) → Unit-test the grader → Register it in the suite  
- Tools: Promptfoo · autoevals · Python  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `med` · safety `none` · flywheel `producer`  
- Classic: net-new · Core rule: Use code for what code can verify; a deterministic assertion is cheaper and more trustworthy than any judge.

**EVL-08 · Build and validate an LLM-judge** · `now`  
Build a single-dimension LLM judge and validate it against human labels before trusting it.  
- Steps: Write the judge prompt + rubric (allow an Unknown verdict) → Collect 50-100 binary human labels → Split 75/25 train/test → Measure TPR/TNR on the held-out labels  
- Tools: Braintrust · Arize Phoenix Evals · DeepEval  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: Who validates the validators? A judge is untrusted until it agrees with humans; allowing Unknown stops it from guessing.

**EVL-09 · Recalibrate a judge against fresh labels** · `now`  
Re-check an in-production judge against fresh human labels to catch judge-human drift.  
- Steps: Sample recent judged items → Re-label a gold subset → Recompute TPR/TNR or kappa → Adjust the judge prompt  
- Tools: Braintrust · Arize Phoenix · spreadsheet  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: A judge drifts as the input distribution moves; an uncalibrated judge silently stops measuring what you think.

**EVL-10 · Generate and validate structured synthetic data** · `now`  
Bootstrap an eval set when no production data exists, then validate realism and leakage.  
- Steps: Define the input dimensions → Hand-write ~20 seed tuples → Two-step generate from the seeds → Validate realism + check leakage vs eval  
- Tools: frontier model · dedup tools  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: Synthetic data unblocks a cold start, but unvalidated it is contamination; hand-write the seeds so the dimensions are real.

**EVL-11 · Curate golden and adversarial sets; version splits** · `now`  
Maintain the stable golden bar plus an adversarial/incident-repro set, with versioned splits.  
- Steps: Sample representative + hard cases → Minimize incident repros into cases → Label the expected behavior → Freeze the versioned split  
- Tools: Braintrust/Langfuse Datasets · Promptfoo  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: The golden set is the stable bar; the adversarial set is the immune memory; both must be frozen to stay comparable.

**EVL-12 · Configure eval-gated CI (assertions then judges)** · `now`  
Block merges that regress the eval suite: assertions first, judges where needed, thresholds, deltas commented on the PR.  
- Steps: Wire the suite to the PR → Run assertions first, judges where needed → Set the thresholds → Fail the build + comment the deltas  
- Tools: Promptfoo · Braintrust GitHub Action  
- Axes: autonomy `autonomous` · blast `med` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: The eval is the unit test for a non-deterministic system; if it is not in CI it is not a gate.

---

## 3. System & Agent Design

*14 tasks · 14 `now` · method → [`system-agent-playbook.md`](system-agent-playbook.md)*

**AT-19 · Author and version a prompt in the registry** · `now`  
Write and version a prompt as a tracked artifact linked to its eval.  
- Steps: Draft the prompt → Diff vs current → Tag a version → Link the governing eval → Register  
- Tools: Braintrust prompts · LangSmith Hub · PromptLayer  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: Prompts are code; version them, link them to an eval, and never edit prod prompts in place.

**AT-20 · Prompt regression test before merge** · `now`  
Run a candidate prompt against the eval set and block the merge on any score regression.  
- Steps: Run candidate vs baseline on the eval set → Compare scores per dimension → Block on regression → Report deltas  
- Tools: Braintrust CI · Promptfoo · GitHub Actions  
- Axes: autonomy `autonomous` · blast `low` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: A one-line prompt edit is a distribution change; gate it like code, because it can silently regress everything.

**AT-21 · Context-window budget design** · `now`  
Decide what enters the context window and at what token cost for a given task.  
- Steps: Inventory context sources → Rank by value per token → Set the token budget → Test truncation/eviction behavior → Eval quality vs budget  
- Tools: tokenizer · tracing · spreadsheet  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `med` · safety `none` · flywheel `none`  
- Classic: net-new · Core rule: Context is a scarce, paid resource; more tokens is not more quality past the point of dilution.

**AT-22 · Design or iterate a RAG retrieval pipeline** · `now`  
Design chunking, embeddings, and reranking for retrieval-augmented generation.  
- Steps: Choose chunking strategy → Pick the embedding model → Add a reranker → Wire retrieved context to the prompt → Eval end-to-end  
- Tools: LlamaIndex · LangChain · pgvector/Pinecone/Weaviate · Cohere rerank  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: Retrieval quality caps answer quality; a wrong chunk is a confident wrong answer.

**AT-23 · Eval retrieval quality** · `now`  
Measure recall@k and the groundedness of retrieved context independently of the generator.  
- Steps: Build a retrieval eval set → Measure recall@k → Measure answer groundedness on retrieved context → Flag low-recall queries  
- Tools: Arize Phoenix (RAG metrics) · Ragas · Braintrust  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: Separate retrieval failures from generation failures, or you will tune the wrong half.

**AT-24 · Design a tool or function schema** · `now`  
Specify the tool contract the model calls: inputs, outputs, errors, and model-legible descriptions.  
- Steps: Define inputs/outputs → Specify error semantics → Write a description the model can act on → Test with the model → Version the schema  
- Tools: JSON Schema · OpenAI/Anthropic tool specs · MCP  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `none`  
- Classic: T-039 · Core rule: The tool description is a prompt; design for the model's job, and make errors part of the contract.

**AT-25 · Eval tool-call accuracy** · `now`  
Measure whether the model selects the right tool with the right arguments.  
- Steps: Build a tool-use eval set → Score tool selection → Score argument accuracy → Flag systematic misuse  
- Tools: BFCL-style harness · Braintrust · tau-bench-style scenarios  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: Tool-use is a distinct capability with its own benchmark; an agent that calls the wrong tool well is still wrong.

**AT-26 · Select or evaluate an MCP server (governance + reliability)** · `now`  
Evaluate and approve an MCP server for reliability, schema quality, and security before wiring it in.  
- Steps: Check provenance + governance (managed vs shadow) → Test schema + reliability → Eval tool-call success rate → Review security/permission surface → Approve or reject  
- Tools: MCP registry · Runlayer-managed servers · Promptfoo · trace logs  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `med` · safety `high` · flywheel `none`  
- Classic: T-119, T-026 · Core rule: An MCP server is third-party code in your agent loop; unvetted servers bypass security and audit controls.

**AT-27 · Design the agent loop or harness** · `now`  
Define the plan-act-observe loop, termination conditions, and tool-call ceilings for the agent.  
- Steps: Define the loop structure → Set stop/termination conditions → Set max steps + token ceiling → Handle tool errors + retries → Spec memory hooks  
- Tools: LangGraph · OpenAI Agents SDK · custom harness  
- Axes: autonomy `copilot` · blast `high` · eval `partial` · regression `high` · safety `high` · flywheel `none`  
- Classic: net-new · Core rule: The harness is the product; unbounded loops burn money and an agent with no stop condition fails unsafely.

**AT-28 · Set the agent step, tool-call, and token budget** · `now`  
Bound cost and loops per run with explicit step, tool-call, and token ceilings.  
- Steps: Set max tool-calls → Set max tokens per run → Set a per-run cost cap → Add a loop-guard → Alert on cap hits  
- Tools: AI service config · model gateway · Helicone  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `med` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: Every run has a cost ceiling or it has none; the budget is a safety and an economics control at once.

**AT-29 · Run a model bake-off on your eval set** · `now`  
Select a model by running candidates through your own rubric, not public leaderboards.  
- Steps: Pick candidate models → Run your eval suite on each → Compare quality/cost/latency → Note slice differences → Recommend the model  
- Tools: OpenRouter · Braintrust · LiteLLM  
- Axes: autonomy `copilot` · blast `med` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: T-025, T-119 · Core rule: Choose on your task, not someone else's benchmark; the cheapest model that clears your bar wins.

**AT-30 · Design a model routing policy** · `now`  
Route easy tasks to a cheap model and hard tasks to a strong one, with a fallback chain.  
- Steps: Define the routing signal → Set thresholds → Define the fallback chain → Eval routed vs single-model → Monitor route mix  
- Tools: LiteLLM · OpenRouter · NotDiamond/RouteLLM · Martian  
- Axes: autonomy `copilot` · blast `med` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: Routing is the cost-quality lever; most traffic is easy, so do not pay frontier prices for it.

**AT-31 · Run a prompt-optimization pass (DSPy/GEPA)** · `now`  
Auto-optimize a prompt against the eval metric and validate the gain on a holdout.  
- Steps: Define the optimization metric → Run the optimizer → Validate on held-out data → Diff vs the hand-written prompt → Promote or discard  
- Tools: DSPy · GEPA · OpenAI prompt optimizer  
- Axes: autonomy `autonomous` · blast `low` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: Optimize against the eval, not vibes; an optimizer that overfits the dev set is a regression in disguise.

**AT-32 · Design agent memory** · `now`  
Decide what persists across turns/runs, how it is retrieved, and how it is bounded and protected.  
- Steps: Define memory scope → Set write/read policy → Define staleness/eviction → Address privacy of stored memory → Eval retrieval relevance  
- Tools: vector store · agent framework · pgvector  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `med` · safety `high` · flywheel `none`  
- Classic: net-new · Core rule: Memory is state with privacy and staleness risk; stale or leaked memory is worse than none.

---

## 4. Data & Training Flywheel

*16 tasks · 4 `now` / 12 `later` · method → [`training-flywheel-playbook.md`](training-flywheel-playbook.md)*

**AT-33 · Design a preference-data collection task** · `later`  
Define the comparison units (prompts, response pairs, ranking rules) that feed RLHF/DPO.  
- Steps: Define the prompt distribution → Choose a pairing strategy → Source candidate responses → Define the comparison schema → Pilot with a small batch  
- Tools: Surge AI · Mercor · Labelbox · Argilla  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: Preference data is the product spec encoded as comparisons; garbage pairs train a garbage reward.

**AT-34 · Write annotation and rater guidelines** · `later`  
Author the rubric humans (and AI judges) follow when labeling preferences or quality.  
- Steps: Define criteria → Give good/bad examples → Write tie-break rules → Cover edge cases → Version the guideline  
- Tools: docs · Label Studio · Argilla  
- Axes: autonomy `human-led` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: Inconsistent raters train a noisy reward; the guideline is the calibration source for both humans and AI judges.

**AT-35 · Recruit and calibrate raters; measure inter-rater agreement** · `later`  
Recruit, qualify, and calibrate human raters and track inter-rater agreement.  
- Steps: Recruit/qualify raters → Run a calibration set → Compute inter-rater agreement → Re-train low-agreement raters → Manage the vendor  
- Tools: Surge AI · Mercor · Labelbox  
- Axes: autonomy `human-led` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: T-021 · Core rule: If raters disagree the reward learns noise; agreement is the quality floor of the whole training loop.

**AT-36 · Audit preference-data quality** · `later`  
Catch noisy, biased, or gamed labels before they train the reward model.  
- Steps: Sample labels → Re-label a gold subset → Flag drift/bias → Quarantine bad batches → Report quality  
- Tools: Argilla · Snorkel · spreadsheet  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: A bad label compounds through the reward into the policy; audit before you train, not after.

**AT-37 · Spec a reward-model train and eval** · `later`  
Define what the reward model should reward and how its quality is independently tested.  
- Steps: Define the reward target → Pick the training data → Spec a held-out RM eval → Set acceptance criteria → Plan portability for online RL/eval  
- Tools: TRL · OpenRLHF · Braintrust  
- Axes: autonomy `human-led` · blast `high` · eval `gated` · regression `high` · safety `high` · flywheel `producer`  
- Classic: net-new · Core rule: A reward model is a portable scorer; spec its eval as rigorously as the policy's, or it will reward the wrong thing.

**AT-38 · Detect reward hacking and reward-model gaming** · `later`  
Find where the policy exploits the reward to get high scores with low real quality.  
- Steps: Inspect high-reward/low-quality samples → Probe known exploits → Quantify the gap → Patch the reward/verifier → Re-test  
- Tools: eval suite · manual review · Braintrust  
- Axes: autonomy `copilot` · blast `high` · eval `partial` · regression `high` · safety `high` · flywheel `producer`  
- Classic: net-new · Core rule: Any reward will be gamed; the question is whether you find the exploit before your users do.

**AT-39 · Design an RLAIF or Constitutional preference pipeline** · `later`  
Use an AI judge to label routine preferences and route only ambiguous or high-stakes cases to humans.  
- Steps: Write the constitution/judge rubric → Generate AI preference labels → Route ambiguous cases to humans → Validate AI labels vs human on a sample → Monitor label quality  
- Tools: Constitutional-AI-style judge · Surge/Mercor (hard cases) · Argilla  
- Axes: autonomy `copilot` · blast `high` · eval `partial` · regression `high` · safety `high` · flywheel `producer`  
- Classic: net-new · Core rule: AI labels are far cheaper than human pairs and comparable on clear cases; reserve humans for the hard, high-stakes ones.

**AT-40 · Curate an SFT dataset** · `later`  
Assemble supervised fine-tuning examples from prod traces and expert demonstrations.  
- Steps: Select demonstrations → Clean and format → De-dup vs the eval set → Label quality → Version  
- Tools: warehouse · Argilla · TRL  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: SFT data quality sets the ceiling; a few hundred excellent examples beat a noisy pile.

**AT-41 · Plan a distillation run and eval gate** · `later`  
Plan distilling a strong teacher into a cheaper student, gated on an eval acceptance bar.  
- Steps: Pick teacher + student → Generate the distillation set → Set eval acceptance → Run + eval the student → Gate the ship  
- Tools: TRL · vLLM · Braintrust  
- Axes: autonomy `copilot` · blast `high` · eval `gated` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: Distillation trades quality for cost; gate on the eval or you ship a quietly worse model to save money.

**AT-42 · Decide fine-tune vs prompt vs RAG** · `now`  
Make the build-method call for a capability gap: prompt, retrieve, or train.  
- Steps: Frame the capability gap → Estimate cost/latency/quality of each path → Check data availability → Weigh maintenance burden → Recommend and document  
- Tools: decision doc · eval data · spreadsheet  
- Axes: autonomy `human-led` · blast `med` · eval `partial` · regression `med` · safety `none` · flywheel `none`  
- Classic: net-new · Core rule: Fine-tuning is the last resort, not the first; for an orchestrator the answer is usually prompt/RAG until evals prove otherwise.

**AT-43 · Author an RL environment (dataset + harness + reward)** · `later`  
Author a verifiable environment for training/eval; an environment and an agent eval are the same object.  
- Steps: Define task inputs (dataset) → Spec the harness/sandbox + tools → Write the reward/rubric → Version as a module → Publish to the env registry  
- Tools: Prime Intellect verifiers · Environments Hub · prime-rl  
- Axes: autonomy `human-led` · blast `high` · eval `gated` · regression `high` · safety `high` · flywheel `producer`  
- Classic: net-new · Core rule: An RL environment and an agent eval are the same thing - dataset + harness + scoring rules; build it once, use it for both.

**AT-44 · Design a sandbox or tool emulator for an environment** · `later`  
Build deterministic, isolated stand-ins for real tools so the environment is safe and reproducible.  
- Steps: Enumerate the real tools → Build deterministic mocks → Seed environment state → Verify isolation → Validate fidelity vs real tools  
- Tools: Modal · E2B · Daytona · Docker  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `med` · safety `high` · flywheel `none`  
- Classic: net-new · Core rule: Training/eval needs determinism and isolation; a sandbox that drifts from reality teaches the wrong lesson.

**AT-45 · Design and anti-game a reward or verifier function** · `later`  
Make high reward actually mean good by red-teaming the reward against exploits.  
- Steps: Define a verifiable signal → List likely exploits → Add anti-gaming checks → Red-team the reward → Lock and version  
- Tools: verifiers · custom checks · eval suite  
- Axes: autonomy `human-led` · blast `high` · eval `gated` · regression `high` · safety `high` · flywheel `producer`  
- Classic: net-new · Core rule: Verifiable rewards (RLVR) are powerful and brittle; the reward is a spec the policy will attack relentlessly.

**AT-46 · Generate and validate synthetic data** · `now`  
Generate synthetic cases and prove they are useful and not contamination.  
- Steps: Define the generation recipe → Generate cases → Validate quality + diversity → Check leakage vs the eval set → Accept or discard  
- Tools: frontier model · dedup/embedding tools · Argilla  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: Unvalidated synthetic data is contamination wearing a costume; validate diversity and leakage before use.

**AT-47 · Run a train/eval contamination and leakage check** · `now`  
Detect overlap between training data and the eval set so scores are not inflated.  
- Steps: Hash/embed both sets → Compute overlap/near-dupes → Flag contaminated cases → Quarantine → Re-split clean  
- Tools: dedup/embedding tools · spreadsheet  
- Axes: autonomy `autonomous` · blast `med` · eval `gated` · regression `high` · safety `none` · flywheel `producer`  
- Classic: net-new · Core rule: A contaminated eval flatters you into shipping a worse model; clean separation is non-negotiable.

**AT-48 · Wire the data flywheel (prod trace to dataset/eval/train)** · `now`  
Stand up the standing pipeline that turns production traces into eval/training data.  
- Steps: Define capture-to-dataset rules → Set a sampling policy → Scrub PII/consent → Route to eval (now) and train (later) → Set the cadence  
- Tools: tracing (LangSmith/Langfuse) · Datasets · cron/pg_cron  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `high` · flywheel `producer`  
- Classic: net-new · Core rule: Production traces are the next dataset; the flywheel is the compounding asset, and its leak is PII.

---

## 5. Delivery & Release

*6 tasks · 6 `now` · method → [`delivery-playbook.md`](delivery-playbook.md)*

**AT-49 · Configure eval-gated CI** · `now`  
Block merges that drop eval scores below threshold via a CI gate.  
- Steps: Wire the eval suite to PRs → Set the thresholds → Fail the build on regression → Report which cases regressed → Require override sign-off  
- Tools: Braintrust GitHub Action · Promptfoo CI · GitHub Actions  
- Axes: autonomy `autonomous` · blast `med` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: The eval is the unit test for non-deterministic systems; if it is not in CI, it is not a gate.

**AT-50 · Pin and version a model+prompt release bundle** · `now`  
Snapshot model id, prompt, tools, and config as one pinned, eval-scored release bundle.  
- Steps: Snapshot model id + prompt + tools + config → Record the eval scores → Tag the bundle → Link the rollback target  
- Tools: git · prompt registry · model gateway  
- Axes: autonomy `copilot` · blast `med` · eval `gated` · regression `high` · safety `none` · flywheel `none`  
- Classic: T-118 · Core rule: A model release is a bundle, not a model id; pin everything that affects behavior so you can roll back cleanly.

**AT-51 · Plan a canary or shadow deployment for a model change** · `now`  
Plan a canary or shadow rollout for a model/prompt change with online scoring gates.  
- Steps: Choose shadow vs canary → Set traffic % → Wire online scorers → Define advance/hold/rollback criteria → Assign a monitor  
- Tools: LaunchDarkly/Statsig · model gateway · online evals  
- Axes: autonomy `copilot` · blast `high` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: T-040 · Core rule: A model change is a prod change; ramp it behind online evals, because offline scores never fully predict prod.

**AT-52 · Online A/B a model or prompt change with quality and business guardrails** · `now`  
Run an online experiment on a model/prompt change against quality and business guardrails.  
- Steps: State the hypothesis → Define the online quality metric + guardrails → Compute power/sample size → Pre-set the ship rule → Read out vs criteria  
- Tools: Statsig · Braintrust online · warehouse SQL  
- Axes: autonomy `copilot` · blast `high` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: T-037, T-069 · Core rule: Offline eval is necessary but not sufficient; the prod distribution decides, so confirm online before full rollout.

**AT-53 · Execute a model or prompt rollback on quality regression** · `now`  
Revert to the last-good bundle when online quality regresses.  
- Steps: Confirm the regression vs baseline → Select the last-good bundle → Revert → Verify recovery → Log + open a regression case  
- Tools: model gateway · flags · traces  
- Axes: autonomy `human-led` · blast `high` · eval `gated` · regression `high` · safety `high` · flywheel `none`  
- Classic: T-067 · Core rule: Reversible mitigation first; a clean pinned bundle makes rollback a one-click decision under pressure.

**AT-54 · Release-readiness go/no-go on eval and safety gates** · `now`  
Make the ship call against eval, safety, cost, and rollback-readiness gates.  
- Steps: Confirm eval pass vs the bar → Confirm safety/red-team pass → Confirm rollback is ready → Confirm cost in budget → Record go/no-go  
- Tools: checklist · Braintrust · red-team report  
- Axes: autonomy `human-led` · blast `high` · eval `gated` · regression `high` · safety `high` · flywheel `none`  
- Classic: T-055 · Core rule: Ship only when the eval, the safety gate, and the rollback all hold; one unchecked critical gate is a no-go.

---

## 6. Measurement & Monitoring

*13 tasks · 13 `now` · method → [`measurement-playbook.md`](measurement-playbook.md)*

**AT-55 · Wire online scoring on production traffic** · `now`  
Run scorers on a sample of live traffic to monitor quality continuously.  
- Steps: Pick online scorers → Set the sampling rate → Build dashboards → Set alert thresholds → Route low scores to triage  
- Tools: Braintrust online · Arize Phoenix · Langfuse  
- Axes: autonomy `copilot` · blast `med` · eval `gated` · regression `med` · safety `med` · flywheel `consumer`  
- Classic: net-new · Core rule: Offline evals catch known failures; online scoring catches the distribution shift you did not anticipate.

**AT-56 · Monitor hallucination and groundedness rate** · `now`  
Continuously measure whether outputs are grounded in sources (e.g., every number traces to a tool).  
- Steps: Define the groundedness check → Score a prod sample → Trend the rate → Alert on a rise → Route ungrounded cases to triage  
- Tools: Arize Phoenix Evals · Ragas · custom grounding checks  
- Axes: autonomy `autonomous` · blast `low` · eval `gated` · regression `high` · safety `high` · flywheel `consumer`  
- Classic: net-new · Core rule: Groundedness is the trust metric; for a grounded product, an ungrounded claim is a sev incident, not a quirk.

**AT-57 · Detect quality or behavior drift vs baseline** · `now`  
Flag when the system's behavior distribution drifts from its baseline.  
- Steps: Set the baseline → Score a rolling window → Flag drift → Segment where it concentrates → Open an RCA  
- Tools: Arize Phoenix · Langfuse · warehouse SQL  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `consumer`  
- Classic: T-070, T-071 · Core rule: Models drift even when you change nothing (provider updates, input shift); watch the distribution, not a point.

**AT-58 · Cluster online failures into a triage queue** · `now`  
Auto-score prod outputs, cluster the failures, and prioritize the queue.  
- Steps: Auto-score prod outputs → Sort by low score → Cluster failures → Prioritize by frequency x severity → Feed novel ones to the dataset  
- Tools: Braintrust · LangSmith · Arize Phoenix  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `med` · safety `med` · flywheel `producer`  
- Classic: T-088 · Core rule: Failing prod outputs are the roadmap; cluster into patterns and grow the dataset from them.

**AT-59 · Build a cost/latency/quality dashboard and per-task cost** · `now`  
Track tokens, cost, latency, and quality per task/run in one view.  
- Steps: Define the unit (per task/run) → Pull tokens+cost+latency+score → Trend them together → Set alerts → Tie spikes to changes  
- Tools: Helicone · Datadog LLM Obs · Langfuse  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `low` · safety `none` · flywheel `none`  
- Classic: T-072 · Core rule: The three axes trade off; you cannot manage quality without seeing its cost and latency beside it.

**AT-60 · Wire human feedback (thumbs/edits) into the flywheel** · `now`  
Capture in-product thumbs and edits and route them to the dataset and triage.  
- Steps: Capture the feedback signal → Map it to traces → Route to the dataset → Close the loop to the user → Monitor signal volume  
- Tools: in-app feedback · Datasets · tracing  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `med` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: Human feedback is the cheapest label source; capture the edit, not just the thumbs, because the edit shows the fix.

**AT-61 · Investigate an eval-score regression (RCA)** · `now`  
Root-cause a drop in eval score: is it the model, the judge, the data, or a real regression?  
- Steps: Confirm it is real not judge-noise → Diff the changed component (prompt/model/retrieval/tool) → Timestamp-match to changes → Rank hypotheses → Write the verdict  
- Tools: Braintrust diff · traces · git log  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `none`  
- Classic: T-070 · Core rule: A score drop has four suspects - model, judge, data, system; eliminate the judge first, because it is cheapest to be wrong.

**AT-62 · Reconcile the offline-eval vs online-quality gap** · `now`  
Explain why offline eval scores and online quality disagree and fix the eval set.  
- Steps: Compare offline scores to online outcomes → Find the distribution shift → Identify missing cases → Add them to the eval set → Re-validate  
- Tools: Braintrust · warehouse SQL · tracing  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `producer`  
- Classic: T-081 · Core rule: When offline says good and prod says bad, the eval set is unrepresentative; the gap is a dataset bug, not a model bug.

**EVL-01 · Verify trace instrumentation** · `now`  
Confirm every run logs the fields needed to replay and score it: inputs, full output, tool calls, context, versions, and cost.  
- Steps: Audit a sample run → Check inputs + full output + tool calls + context + versions + cost are logged → Map fields to the gen_ai.* OTel convention → File instrumentation gaps  
- Tools: OpenTelemetry GenAI · Arize Phoenix · Langfuse  
- Axes: autonomy `autonomous` · blast `low` · eval `partial` · regression `low` · safety `med` · flywheel `producer`  
- Classic: net-new · Core rule: You cannot evaluate what you did not capture; a run that cannot be replayed and re-scored is invisible to the eval loop.

**EVL-13 · Wire online scoring and drift alerts** · `now`  
Score a sample of production traffic with reference-free scorers and alert when the lower-bound CI breaches a floor.  
- Steps: Pick reference-free scorers → Set the sampling rate → Build dashboards → Alert on the lower-bound CI breaching the floor  
- Tools: Braintrust online · Arize Phoenix · HoneyHive  
- Axes: autonomy `copilot` · blast `med` · eval `gated` · regression `med` · safety `med` · flywheel `consumer`  
- Classic: net-new · Core rule: Production has no reference answer, so score reference-free; alert on the CI lower bound, not the point estimate, to avoid noise.

**EVL-14 · Investigate an eval-score regression (RCA)** · `now`  
Root-cause an eval-score drop: distinguish judge variance from a real regression, then localize the component.  
- Steps: Confirm it is real, not judge variance → Diff the changed component (prompt/model/retrieval/tool) → Timestamp-match to deploys → Write the verdict  
- Tools: Braintrust diff · traces · git log  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: A score drop has four suspects - model, judge, data, system; eliminate judge noise first because it is the cheapest way to be fooled.

**EVL-15 · Build the agent transition-failure matrix** · `now`  
Localize where multi-step agent runs break by tallying last-success against first-failure states.  
- Steps: Define the agent states → Tally last-success x first-failure across runs → Rank the transition hotspots → Link exemplar traces  
- Tools: traces · notebook  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `med` · safety `none` · flywheel `consumer`  
- Classic: net-new · Core rule: A drop-off in an agent is a transition failure, not a funnel step; the matrix shows which hand-off actually breaks.

**EVL-16 · Plan eval-gated canary/shadow and rollback** · `now`  
Graduate a model or prompt change safely: pin the bundle, shadow then canary, gate on online scores, define the rollback rule.  
- Steps: Pin the bundle (model + prompt + tools) → Shadow, then canary a traffic % → Wire online scorers → Set the advance / rollback rule  
- Tools: model gateway · feature flags · online evals  
- Axes: autonomy `copilot` · blast `high` · eval `gated` · regression `high` · safety `med` · flywheel `none`  
- Classic: net-new · Core rule: A model change is a prod change gated on online quality; ungraded autonomous rollout is the dangerous quadrant - pin so rollback is one click.

---

## 7. Safety, Red-teaming & Guardrails

*6 tasks · 6 `now` · method → [`safety-substrate.md`](safety-substrate.md)*

**AT-63 · Design a red-team campaign** · `now`  
Plan structured adversarial probing of the system against a threat model.  
- Steps: Define the threat model → Generate attack prompts → Run the campaign → Log breaks → Prioritize fixes + regression cases  
- Tools: garak · PyRIT · HarmBench · manual  
- Axes: autonomy `human-led` · blast `med` · eval `partial` · regression `med` · safety `high` · flywheel `producer`  
- Classic: net-new · Core rule: You red-team so you find the jailbreak before users do; absence of a campaign is not absence of vulnerability.

**AT-64 · Build and maintain a jailbreak and abuse eval corpus** · `now`  
Maintain a versioned corpus of jailbreaks and abuse cases to score model resistance.  
- Steps: Collect known jailbreaks → Categorize by attack type → Score model resistance → Add new attacks → Version  
- Tools: garak · internal corpus · Lakera  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `high` · safety `high` · flywheel `producer`  
- Classic: net-new · Core rule: Jailbreak resistance is a measurable, regressable property; if it is not in an eval, it will silently regress.

**AT-65 · Spec guardrail policy and content filters** · `now`  
Define what the system must never do and the input/output filters that enforce it.  
- Steps: Define disallowed behaviors → Choose input/output filters → Set actions (block/redact/escalate) → Test against the abuse corpus → Document  
- Tools: Llama Guard · NeMo Guardrails · OpenAI moderation · Guardrails AI  
- Axes: autonomy `human-led` · blast `high` · eval `gated` · regression `high` · safety `high` · flywheel `none`  
- Classic: T-033 · Core rule: Guardrails are policy made executable; the filter that is not tested against real attacks is decorative.

**AT-66 · Calibrate refusal and over-refusal rate** · `now`  
Tune the system to block harmful requests without refusing valid ones.  
- Steps: Build a benign + harmful test set → Measure refuse rates on each → Tune the policy/prompt → Re-measure → Lock the trade-off  
- Tools: eval suite · Braintrust · Llama Guard  
- Axes: autonomy `copilot` · blast `med` · eval `gated` · regression `high` · safety `high` · flywheel `none`  
- Classic: net-new · Core rule: Over-refusal is a real product failure; safety and helpfulness trade off and the balance is a product call.

**AT-67 · Triage a safety incident or harmful output** · `now`  
Run the PM side of a live safety incident: contain, communicate, and capture a regression.  
- Steps: Confirm scope + severity → Contain (filter/rollback) → Communicate to stakeholders → Postmortem → Add a regression case  
- Tools: incident tooling · flags · traces  
- Axes: autonomy `human-led` · blast `high` · eval `partial` · regression `high` · safety `high` · flywheel `producer`  
- Classic: T-060 · Core rule: Contain before you diagnose; a harmful output in prod is reversible only forward, via filter or rollback.

**AT-68 · Run a pre-release safety eval gate** · `now`  
Block release on jailbreak, abuse, and PII-leak eval suites failing their floor.  
- Steps: Run jailbreak + abuse + PII suites → Compare to the safety floor → Block on fail → Require sign-off → Log  
- Tools: garak · Lakera · Braintrust  
- Axes: autonomy `human-led` · blast `high` · eval `gated` · regression `high` · safety `high` · flywheel `none`  
- Classic: net-new · Core rule: Safety is a release gate, not a launch-day checklist; a failed safety floor is a hard no-go.

---

## 8. Inference Economics & Model Portfolio

*5 tasks · 5 `now` · method → [`inference-economics.md`](inference-economics.md)*

**AT-69 · Model portfolio build-vs-buy review** · `now`  
Decide which capabilities use which models - API, open-weight, or fine-tuned - with lock-in and data-rights weighed.  
- Steps: Map needs to models → Compare API vs open vs fine-tune → Assess lock-in + data rights → Estimate switching cost → Recommend the portfolio  
- Tools: vendor docs · eval data · spreadsheet  
- Axes: autonomy `human-led` · blast `med` · eval `partial` · regression `med` · safety `med` · flywheel `none`  
- Classic: T-119, T-093 · Core rule: Model choice is a portfolio decision with lock-in risk; do not single-source a capability you cannot switch.

**AT-70 · Inference cost-per-task budget and unit economics** · `now`  
Model the unit economics of an AI feature: cost per task, margin, and the cost-quality frontier.  
- Steps: Define the task unit → Measure tokens x price + tool/infra cost → Model margin per task → Map the cost-quality frontier → Set the budget  
- Tools: Helicone · model gateway · spreadsheet  
- Axes: autonomy `copilot` · blast `med` · eval `partial` · regression `med` · safety `none` · flywheel `none`  
- Classic: T-093, T-016 · Core rule: For an AI product, inference is COGS; a feature that is loved and unprofitable per call is a problem, not a win.

**AT-71 · Eval roadmap tied to capability and eval gaps** · `now`  
Sequence which evals to build next, ranked by risk and use-case value.  
- Steps: Inventory eval gaps → Rank by risk x use-case value → Sequence the eval builds → Tie to capability bets → Publish  
- Tools: Braintrust · roadmap tool  
- Axes: autonomy `human-led` · blast `med` · eval `partial` · regression `med` · safety `med` · flywheel `none`  
- Classic: T-090 · Core rule: The eval roadmap is the product roadmap for an AI system; you can only build what you can grade.

**AT-72 · Data-rights, licensing, and privacy posture for training and traces** · `now`  
Set the policy for what data may be used for training/evals, with consent, licensing, and PII handled.  
- Steps: Inventory data sources → Check rights/consent/licensing → Classify PII → Set retention + access → Publish the policy  
- Tools: DPA/legal · data catalog · consent records  
- Axes: autonomy `human-led` · blast `high` · eval `none` · regression `low` · safety `high` · flywheel `producer`  
- Classic: T-048 · Core rule: The flywheel's fuel is user data; using it without rights is a legal and trust failure that compounds.

**AT-73 · Capability roadmap tied to eval gaps** · `now`  
Set the AI capability strategy: which bets to make, anchored to eval targets and capability deltas.  
- Steps: Synthesize eval gaps + capability deltas → Pick the bets → Tie each to an eval target → Sequence → Write the narrative  
- Tools: strategy doc · eval data  
- Axes: autonomy `human-led` · blast `med` · eval `partial` · regression `med` · safety `med` · flywheel `none`  
- Classic: T-092, T-090 · Core rule: Strategy for an AI product is choosing which capabilities to grade-and-grow next; the insight stays human.

---

## 9. Commercial & Stakeholder

*13 tasks · 13 `now` · method → [`commercial-playbook.md`](commercial-playbook.md)*

**AT-74 · Design usage or token-based pricing for an AI product** · `now`  
Price an AI product so revenue tracks the inference cost it incurs.  
- Steps: Pick the value-aligned usage unit → Map unit to inference cost → Set price + included tier → Define overage + caps → Model margin + bill-shock risk  
- Tools: Stripe · Metronome · spreadsheet  
- Axes: autonomy `copilot` · blast `low` · eval `none` · regression `low` · safety `none` · flywheel `none`  
- Classic: T-041, T-027 · Core rule: Price the unit that tracks both value and cost; flat pricing on metered COGS is how AI products lose money at scale.

**AT-75 · Define AI feature tier-gating and rate limits** · `now`  
Decide which AI capabilities, quotas, and model tiers gate which plan.  
- Steps: List AI capabilities + their cost → Assign to tiers → Set per-tier rate limits/quotas → Gate premium models to higher tiers → Check competitive parity  
- Tools: Stripe · product spec · spreadsheet  
- Axes: autonomy `copilot` · blast `low` · eval `none` · regression `low` · safety `none` · flywheel `none`  
- Classic: T-042 · Core rule: Gate on cost and capability, not just features; rate limits are a margin control, not only a product one.

**AT-76 · Model the gross-margin impact of an AI feature** · `now`  
Project how an AI feature's inference COGS moves gross margin at scale.  
- Steps: Estimate per-use inference cost → Project usage distribution → Model COGS at scale → Run a cost-sensitivity range → Recommend with guardrails  
- Tools: spreadsheet · Helicone · warehouse SQL  
- Axes: autonomy `copilot` · blast `low` · eval `none` · regression `low` · safety `none` · flywheel `none`  
- Classic: T-093, T-136 · Core rule: Inference COGS scales with usage; a feature's margin can invert as it succeeds, so model the tail.

**AT-77 · Write a GTM or launch brief for an AI capability** · `now`  
Position and launch an AI capability around its evaluated capability, trust, and limits.  
- Steps: Set the launch tier → Write positioning around capability + trust → State the limits honestly → Plan enablement → Define launch + quality metrics  
- Tools: Notion · Braintrust (evidence) · marketing tools  
- Axes: autonomy `copilot` · blast `low` · eval `none` · regression `low` · safety `med` · flywheel `none`  
- Classic: T-045 · Core rule: Sell the evaluated capability, not the hype; overclaiming an AI capability is a trust debt you pay in churn.

**AT-78 · Triage sales and CS requests for the AI product** · `now`  
Triage field requests, separating the model cannot from we have not wired it.  
- Steps: Collect requests with context → Dedupe vs known asks → Classify model-limit vs product-gap → Weight by value → Route or decline with reason  
- Tools: Productboard · Salesforce · Slack  
- Axes: autonomy `copilot` · blast `low` · eval `none` · regression `low` · safety `none` · flywheel `consumer`  
- Classic: T-066 · Core rule: For AI products, half of it does not work is a capability limit, not a backlog item; classify before committing.

**AT-79 · Build sales enablement for an AI feature** · `now`  
Equip the field to set accurate expectations about an AI feature's accuracy, limits, and guardrails.  
- Steps: Summarize what the feature does + its limits → Write the accuracy/trust talk track → Add objection handling (hallucination, data use) → Note guardrails → Distribute  
- Tools: Notion · Slack · Gong  
- Axes: autonomy `copilot` · blast `low` · eval `none` · regression `low` · safety `med` · flywheel `none`  
- Classic: T-129, T-151 · Core rule: The field will overpromise unless armed with the limits; expectation-setting is the enablement, not just the value pitch.

**AT-80 · Run AI win-loss analysis** · `now`  
Analyze why deals were won/lost on AI-specific factors: accuracy, trust, hallucination, latency, cost.  
- Steps: Pull won/lost deals → Read notes for AI-specific reasons → Cluster trust/accuracy/latency/cost drivers → Weight by deal size → Tie to eval/roadmap  
- Tools: Gong · Salesforce · Dovetail  
- Axes: autonomy `copilot` · blast `low` · eval `none` · regression `low` · safety `med` · flywheel `consumer`  
- Classic: T-099 · Core rule: AI deals are won and lost on trust and reliability; recurring it hallucinated in the POC is roadmap signal.

**AT-81 · Prepare an exec or board update on AI quality and economics** · `now`  
Brief leadership on eval trend, cost-per-task, safety posture, and the capability roadmap.  
- Steps: Lead with the eval-quality trend → Show cost/run + margin → Surface safety posture + incidents → Tie to the capability roadmap → Pre-empt the hard questions  
- Tools: Slides · Braintrust · spreadsheet  
- Axes: autonomy `human-led` · blast `low` · eval `none` · regression `low` · safety `med` · flywheel `none`  
- Classic: T-095, T-103 · Core rule: For an AI product, the board cares about quality trend, unit economics, and safety exposure; show the eval curve, not feature counts.

**AT-82 · Respond to a why is the AI wrong escalation** · `now`  
Handle a stakeholder escalation about AI reliability by reframing expectations with evidence.  
- Steps: Acknowledge + get the specific case → Reproduce + classify the failure → Frame it vs the eval/groundedness data → Set realistic reliability expectations → Log + route the fix  
- Tools: Slack · traces · Braintrust  
- Axes: autonomy `human-led` · blast `low` · eval `none` · regression `low` · safety `med` · flywheel `none`  
- Classic: T-094, T-131 · Core rule: Reframe from it is broken to here is the measured reliability and the fix path; non-determinism needs expectation-setting, not defensiveness.

**AT-83 · Author the AI trust and transparency narrative for buyers** · `now`  
Write the buyer-facing account of how the system is evaluated, grounded, and kept safe.  
- Steps: Inventory what buyers ask about AI → Describe the eval + grounding approach → Document data use + retention → State safety + human-oversight controls → Keep it current  
- Tools: trust center · Notion · Braintrust  
- Axes: autonomy `human-led` · blast `med` · eval `none` · regression `low` · safety `high` · flywheel `none`  
- Classic: net-new · Core rule: Buyers now diligence AI trust like security; a clear transparency narrative deflects the AI questionnaire and accelerates deals.

**AT-84 · Build an AI adoption and engagement scorecard** · `now`  
Track adoption of the AI feature and the acceptance/edit rate of its outputs.  
- Steps: Define eligible users → Measure adoption + frequency → Measure acceptance/edit/override rate → Trend vs target → Segment by cohort  
- Tools: Amplitude · warehouse SQL · in-app feedback  
- Axes: autonomy `copilot` · blast `low` · eval `partial` · regression `low` · safety `none` · flywheel `consumer`  
- Classic: T-139, T-074 · Core rule: For AI features, the acceptance/edit rate is the truest adoption signal - it shows whether users trust the output.

**AT-85 · Handle AI data-use consent and disclosure in the product** · `now`  
Spec the in-product consent for using user data in the flywheel and disclosure of AI involvement.  
- Steps: Identify data-use + AI-disclosure points → Spec consent capture + storage → Spec AI-involvement disclosure → Cover opt-out → Review with legal  
- Tools: product spec · legal review · consent log  
- Axes: autonomy `human-led` · blast `high` · eval `none` · regression `low` · safety `high` · flywheel `producer`  
- Classic: T-048, O-FIN-010 · Core rule: Consent for the flywheel and disclosure of AI are trust and compliance gates; a silent data-grab or hidden AI is a liability.

**AT-86 · Competitive AI capability and pricing teardown** · `now`  
Compare competitors on both AI capability (via your evals) and pricing/packaging.  
- Steps: List competitors → Run their AI on your eval set → Capture their pricing + limits → Normalize for comparison → Flag capability + pricing gaps  
- Tools: competitor access · Braintrust · spreadsheet  
- Axes: autonomy `copilot` · blast `low` · eval `gated` · regression `low` · safety `none` · flywheel `none`  
- Classic: T-150, T-007 · Core rule: Compare AI capability on your task and pricing on value; a competitor's leaderboard win may not survive your eval.

---

## Classic task index (the `T-` + `O-` library)

The model-agnostic PM tasks the AIDLC tasks **keep, modify, or supersede**. These carry only the two classic axes the sheet defines — `autonomy` (`ai_leverage`) and `blast` (`blast_radius`); the four AI-specific axes apply through their `AT-`/`EVL-` counterpart when the task is done *on an AI product*. Use this index to resolve any **Classic:** reference above.

### Invariant tasks `T-001`–`T-152` (152) — by phase

<details><summary><b>Discovery</b> (34)</summary>

| id | task | autonomy | blast |
|---|---|---|---|
| T-001 | Conduct a customer discovery interview | human-led | low |
| T-002 | Write an interview snapshot | copilot | low |
| T-003 | Synthesize multiple interviews into themes | copilot | low |
| T-004 | Build or update an opportunity solution tree | copilot | low |
| T-005 | Triage inbound customer feedback into themes | copilot | low |
| T-006 | Mine support tickets for top pain themes | copilot | low |
| T-007 | Run a competitive feature teardown | copilot | low |
| T-008 | Monitor competitor releases and changelogs | autonomous | low |
| T-009 | Analyze app-store and review-site sentiment | copilot | low |
| T-010 | Explore an ad-hoc product-data question | copilot | low |
| T-011 | Pull a funnel and find the largest drop-off | copilot | low |
| T-012 | Build a retention curve and find the flattening point | copilot | low |
| T-013 | Identify the activation aha event | copilot | med |
| T-014 | Compare retention across behavioral cohorts | copilot | low |
| T-015 | Run a path analysis on non-converters | copilot | low |
| T-016 | Size a market or opportunity | copilot | med |
| T-017 | Design and analyze a product survey | copilot | low |
| T-018 | Run an assumption test | copilot | med |
| T-019 | Define or refine a persona from evidence | copilot | low |
| T-020 | Draft a discovery research plan | copilot | low |
| T-021 | Recruit and schedule research participants | human-led | low |
| T-022 | Map a customer journey from data and qual | copilot | low |
| T-023 | Analyze churned-user exit reasons | copilot | med |
| T-024 | Watch session replays for a friction point | copilot | low |
| T-025 | Benchmark a metric against category | copilot | low |
| T-026 | Diagnose a technical constraint via system exploration | human-led | low |
| T-027 | Estimate willingness-to-pay via survey | copilot | med |
| T-119 | Assess a third-party vendor or API | copilot | med |
| T-130 | Run a customer advisory session | human-led | med |
| T-134 | Analyze a jobs-to-be-done interview set | copilot | low |
| T-135 | Run a heuristic UX audit | copilot | low |
| T-145 | Synthesize NPS verbatims into themes | copilot | low |
| T-150 | Compile a competitor pricing comparison | copilot | low |
| T-152 | Run a five-whys on a recurring complaint | copilot | low |

</details>

<details><summary><b>Definition</b> (35)</summary>

| id | task | autonomy | blast |
|---|---|---|---|
| T-028 | Write a problem statement one-pager | copilot | med |
| T-029 | Draft a product requirements document | copilot | med |
| T-030 | Write user stories and acceptance criteria | copilot | med |
| T-031 | Define success metrics for a feature | copilot | med |
| T-032 | Write a tracking and instrumentation plan | copilot | med |
| T-033 | Define a guardrail metric set | copilot | med |
| T-034 | Write non-goals and scope boundaries | copilot | med |
| T-035 | Create a solution sketch and design brief | copilot | med |
| T-036 | Specify edge cases and error states | copilot | med |
| T-037 | Design an experiment | copilot | med |
| T-038 | Calculate required sample size and duration | autonomous | low |
| T-039 | Write an API or platform capability spec | copilot | med |
| T-040 | Define a rollout and feature-flag plan | copilot | med |
| T-041 | Write a pricing and packaging proposal | copilot | med |
| T-042 | Define a tier and feature-gating matrix | copilot | med |
| T-043 | Draft an RFC for a technical approach | copilot | med |
| T-044 | Prototype the solution (demos before memos) | copilot | med |
| T-045 | Create a launch and go-to-market brief | copilot | med |
| T-046 | Define an eval rubric for an AI feature | human-led | med |
| T-047 | Write a risk and dependency register | copilot | med |
| T-048 | Define an entitlements and permissions model | copilot | med |
| T-106 | Optimize a high-drop onboarding step | copilot | med |
| T-110 | Define an at-risk churn cohort | copilot | med |
| T-113 | Define and track a habit metric | copilot | low |
| T-116 | Review an API for developer experience | copilot | med |
| T-117 | Define SLOs and SLIs for a service | copilot | med |
| T-118 | Plan a deprecation or migration | human-led | high |
| T-121 | Review a schema or pipeline change impact | copilot | med |
| T-123 | Build a self-serve metric definition | copilot | med |
| T-124 | Validate a metric definition with data team | human-led | med |
| T-125 | Write a data-dictionary entry | copilot | low |
| T-138 | Define experiment ship-criteria | copilot | med |
| T-142 | Map cross-team dependencies | copilot | med |
| T-147 | Define an activation milestone checklist | copilot | med |
| T-148 | Estimate engineering effort with the eng lead | human-led | med |

</details>

<details><summary><b>Delivery</b> (27)</summary>

| id | task | autonomy | blast |
|---|---|---|---|
| T-049 | Run a backlog hygiene grooming pass | copilot | med |
| T-050 | Write a delivery ticket from a story | copilot | med |
| T-051 | Prepare and prioritize the sprint backlog | copilot | med |
| T-052 | Triage an inbound bug report | copilot | med |
| T-053 | Reproduce and document a bug | copilot | med |
| T-054 | Acceptance-review a completed story | copilot | med |
| T-055 | Run a release-readiness go/no-go | human-led | med |
| T-056 | Enable a feature flag to start rollout | human-led | high |
| T-057 | Write release notes and changelog | copilot | low |
| T-058 | Send a stakeholder status update | copilot | low |
| T-059 | Unblock or escalate a delivery blocker | human-led | med |
| T-060 | Triage and communicate a production incident | human-led | high |
| T-061 | Manually QA a flow in staging | copilot | med |
| T-062 | Write a customer-facing help doc | copilot | low |
| T-063 | Coordinate a beta or early-access cohort | human-led | med |
| T-064 | Verify instrumentation fired correctly | copilot | med |
| T-065 | Cut scope to hit a deadline | human-led | med |
| T-066 | Triage sales and CS feature requests | copilot | med |
| T-067 | Make a hotfix or rollback decision | human-led | high |
| T-068 | Update the roadmap board after a change | copilot | low |
| T-127 | Run a design critique | human-led | med |
| T-129 | Write a feature enablement brief | copilot | low |
| T-131 | Triage and route a CS or sales escalation | human-led | med |
| T-133 | Run a pre-launch alignment check | human-led | med |
| T-143 | Audit feature flags for cleanup | copilot | med |
| T-144 | Prepare talking points for a customer call | copilot | low |
| T-151 | Write an internal launch FAQ | copilot | low |

</details>

<details><summary><b>Measurement</b> (37)</summary>

| id | task | autonomy | blast |
|---|---|---|---|
| T-069 | Read out an A/B experiment and recommend ship or kill | copilot | med |
| T-070 | Investigate a metric alert that fired | copilot | med |
| T-071 | Set up an alert or threshold on a key metric | copilot | med |
| T-072 | Build or refresh a metrics dashboard | copilot | low |
| T-073 | Prepare the weekly metrics review | copilot | low |
| T-074 | Measure feature adoption post-launch | copilot | low |
| T-075 | Run a pre/post launch impact analysis | copilot | low |
| T-076 | Decompose a metric change | copilot | low |
| T-077 | Calculate and refresh a north-star KPI | autonomous | low |
| T-078 | Analyze a guardrail regression in an experiment | copilot | med |
| T-079 | Cohort an experiment result by segment | copilot | med |
| T-080 | Monitor a rollout's health metrics | copilot | med |
| T-081 | Reconcile a metric discrepancy between tools | copilot | med |
| T-082 | Write a post-launch retro | copilot | low |
| T-083 | Annotate a release on dashboards | autonomous | low |
| T-084 | Measure funnel conversion lift after a fix | copilot | low |
| T-085 | Audit data quality and detect broken events | copilot | med |
| T-086 | Interpret an experiment non-result | copilot | med |
| T-087 | Build a retention and revenue cohort report | copilot | low |
| T-088 | Run an eval suite on production AI logs | copilot | med |
| T-104 | Diagnose a drop in signups | copilot | med |
| T-105 | Analyze channel attribution for a cohort | copilot | low |
| T-108 | Analyze a referral or virality loop | copilot | low |
| T-109 | Analyze the paywall and upgrade funnel | copilot | low |
| T-111 | Run a resurrection and win-back analysis | copilot | low |
| T-112 | Analyze feature-usage vs retention | copilot | low |
| T-114 | Audit an engagement campaign | copilot | low |
| T-120 | Triage a platform performance regression | copilot | med |
| T-122 | Write a SQL query for a product question | copilot | low |
| T-126 | Backfill or QA a historical metric | copilot | med |
| T-128 | Facilitate a sprint retro | human-led | low |
| T-136 | Analyze pricing elasticity from a test | copilot | med |
| T-137 | Monitor an experiment for SRM and health | autonomous | low |
| T-139 | Build a weekly growth scorecard | copilot | low |
| T-140 | Triage a data-looks-wrong report | copilot | med |
| T-141 | Write a one-page launch recap | copilot | low |
| T-146 | Build a feature adoption funnel | copilot | low |

</details>

<details><summary><b>Strategy/Ops</b> (19)</summary>

| id | task | autonomy | blast |
|---|---|---|---|
| T-089 | Prioritize a feature backlog | copilot | med |
| T-090 | Draft or refresh a quarterly roadmap | copilot | med |
| T-091 | Set or refine team OKRs | human-led | med |
| T-092 | Write a product strategy narrative | human-led | med |
| T-093 | Build a business case and ROI model | copilot | med |
| T-094 | Respond to a stakeholder feature request | human-led | med |
| T-095 | Prepare an executive product update | human-led | med |
| T-096 | Prepare a prioritization workshop | copilot | med |
| T-097 | Maintain a ranked won't-do list | copilot | low |
| T-098 | Allocate capacity for quarterly planning | human-led | med |
| T-099 | Synthesize win-loss for positioning | copilot | med |
| T-100 | Check roadmap-to-OKR alignment | copilot | med |
| T-101 | Refresh the vision one-pager | human-led | med |
| T-102 | Build a monetization roadmap | copilot | med |
| T-103 | Prepare a quarterly business review deck | copilot | med |
| T-107 | Build a growth experiment backlog | copilot | med |
| T-115 | Triage a tech-debt vs feature trade-off | human-led | med |
| T-132 | Write a decision-log entry | copilot | low |
| T-149 | Draft a sunset recommendation | human-led | med |

</details>

### Domain overlays `O-*` (70) — by domain

<details><summary><b>Fintech</b> (14)</summary>

| id | task | phase | autonomy | blast |
|---|---|---|---|---|
| O-FIN-001 | Diagnose KYC verification drop-off by step | Discovery | copilot | med |
| O-FIN-002 | Design a risk-based step-up vs reject flow | Definition | copilot | med |
| O-FIN-003 | Reconcile a transaction ledger discrepancy | Measurement | copilot | high |
| O-FIN-004 | Disposition a suspicious-activity (SAR) alert | Delivery | human-led | high |
| O-FIN-005 | Build a fraud-rate vs approval-rate guardrail readout | Measurement | copilot | med |
| O-FIN-006 | Spec a compliance decision audit trail | Definition | copilot | med |
| O-FIN-007 | Analyze the chargeback and dispute funnel | Measurement | copilot | med |
| O-FIN-008 | Model interchange and fee economics | Strategy/Ops | copilot | med |
| O-FIN-009 | Plan a KYC vendor failover and orchestration A/B | Definition | copilot | med |
| O-FIN-010 | Review a regulated disclosure or consent screen | Delivery | human-led | high |
| O-FIN-011 | Risk-tier the onboarding gate by intended activity | Definition | copilot | med |
| O-FIN-012 | Build a funded-account-rate readout | Measurement | copilot | low |
| O-FIN-013 | Assess a regulation change's product impact | Discovery | copilot | med |
| O-FIN-014 | Define transaction-monitoring alert thresholds | Measurement | copilot | med |

</details>

<details><summary><b>Marketplace</b> (14)</summary>

| id | task | phase | autonomy | blast |
|---|---|---|---|---|
| O-MKT-001 | Diagnose a liquidity drop by geo or category | Measurement | copilot | med |
| O-MKT-002 | Build a supply/demand balance readout | Measurement | copilot | low |
| O-MKT-003 | Analyze match rate and time-to-match | Measurement | copilot | low |
| O-MKT-004 | Model a take-rate change across both sides | Strategy/Ops | copilot | med |
| O-MKT-005 | Plan supply-side seeding for a new market | Definition | copilot | med |
| O-MKT-006 | Detect and analyze disintermediation leakage | Measurement | copilot | med |
| O-MKT-007 | Analyze whale and concentration risk | Discovery | copilot | low |
| O-MKT-008 | Define a trust-and-safety supply gate | Definition | copilot | med |
| O-MKT-009 | Build a sell-through and utilization readout | Measurement | copilot | low |
| O-MKT-010 | Diagnose supplier churn vs demand churn | Discovery | copilot | med |
| O-MKT-011 | Tune search ranking to improve fill rate | Definition | copilot | med |
| O-MKT-012 | Allocate CAC budget across both sides | Strategy/Ops | copilot | med |
| O-MKT-013 | Analyze cross-side network-effect spillover | Discovery | copilot | low |
| O-MKT-014 | Define a liquidity threshold before scaling | Definition | copilot | med |

</details>

<details><summary><b>B2B-Enterprise</b> (14)</summary>

| id | task | phase | autonomy | blast |
|---|---|---|---|---|
| O-B2B-001 | Respond to a security questionnaire | Delivery | copilot | med |
| O-B2B-002 | Maintain a security control evidence map | Definition | copilot | med |
| O-B2B-003 | Triage deal-linked feature requests | Delivery | copilot | med |
| O-B2B-004 | Spec enterprise security and admin gating | Definition | copilot | med |
| O-B2B-005 | Evaluate a DPA or contractual commitment request | Strategy/Ops | human-led | high |
| O-B2B-006 | Build a product-qualified-account signal | Definition | copilot | med |
| O-B2B-007 | Prepare a roadmap commitment for a strategic account | Strategy/Ops | human-led | high |
| O-B2B-008 | Analyze seat and license expansion (NRR) | Measurement | copilot | low |
| O-B2B-009 | Run win-loss synthesis on enterprise deals | Strategy/Ops | copilot | med |
| O-B2B-010 | Plan a self-serve to sales-assist handoff | Definition | copilot | med |
| O-B2B-011 | Assess SOC2 Type I vs II readiness gap | Discovery | copilot | med |
| O-B2B-012 | Define an admin and governance feature for IT buyers | Definition | copilot | med |
| O-B2B-013 | Build a trust-center content set | Delivery | copilot | med |
| O-B2B-014 | Scope a custom enterprise commitment vs roadmap | Delivery | human-led | high |

</details>

<details><summary><b>PLG-DevTools</b> (14)</summary>

| id | task | phase | autonomy | blast |
|---|---|---|---|---|
| O-PLG-001 | Define activation as first successful API call | Discovery | copilot | med |
| O-PLG-002 | Reduce time-to-first-value in the quickstart | Definition | copilot | med |
| O-PLG-003 | Instrument the developer activation funnel | Definition | copilot | med |
| O-PLG-004 | Audit docs as a product surface | Discovery | copilot | low |
| O-PLG-005 | Build a product-qualified-lead signal | Definition | copilot | med |
| O-PLG-006 | Analyze the free-to-paid conversion funnel | Measurement | copilot | low |
| O-PLG-007 | Diagnose SDK empty-state friction | Discovery | copilot | low |
| O-PLG-008 | Define a weekly-active-developer habit metric | Definition | copilot | low |
| O-PLG-009 | Triage GitHub and community feedback | Discovery | copilot | low |
| O-PLG-010 | Spec a self-serve upgrade and billing flow | Definition | copilot | med |
| O-PLG-011 | Benchmark activation rate vs devtool category | Discovery | copilot | low |
| O-PLG-012 | Plan a usage-based pricing meter | Definition | copilot | med |
| O-PLG-013 | Optimize sample-data and template pre-loading | Definition | copilot | med |
| O-PLG-014 | Analyze API error rates as an activation blocker | Measurement | copilot | med |

</details>

<details><summary><b>Consumer</b> (14)</summary>

| id | task | phase | autonomy | blast |
|---|---|---|---|---|
| O-CON-001 | Diagnose the D1/D7 retention cliff | Discovery | copilot | low |
| O-CON-002 | Design a retention loop, not a campaign | Definition | copilot | med |
| O-CON-003 | Audit push-notification CTR against a spam floor | Measurement | copilot | low |
| O-CON-004 | Define a consumer habit metric | Definition | copilot | low |
| O-CON-005 | Analyze the in-app vs off-app engagement shift | Measurement | copilot | low |
| O-CON-006 | Build an early-churn-interception signal | Definition | copilot | med |
| O-CON-007 | Analyze app-store rating drivers | Discovery | copilot | low |
| O-CON-008 | Design a social-graph virality loop | Measurement | copilot | low |
| O-CON-009 | Segment lapsed vs active for cadence tuning | Discovery | copilot | low |
| O-CON-010 | Analyze notification opt-out and uninstall correlation | Measurement | copilot | med |
| O-CON-011 | Plan a streak-recovery win-back mechanic | Definition | copilot | med |
| O-CON-012 | Optimize session-zero for value-first | Definition | copilot | med |
| O-CON-013 | Measure feed and content engagement depth | Measurement | copilot | low |
| O-CON-014 | A/B test notification copy and timing | Measurement | copilot | med |

</details>

---

*Coverage: 102 AIDLC (7 Discovery · 22 Eval&Spec · 14 System&Agent · 16 Training · 6 Delivery · 13 Measurement · 6 Safety · 5 Inference-Econ · 13 Commercial) + 222 classic (152 `T` · 70 `O`). 90 AIDLC tasks are `now`, 12 are `later` (the training cluster).*
