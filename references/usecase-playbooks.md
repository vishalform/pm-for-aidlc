# Use-Case Playbooks — specialize the loop by what you're shipping

*16 use cases (`UC-01`–`UC-16`) in 8 families. Same AIDLC loop everywhere — what changes is **which failure mode dominates**, **which metric defines "good"**, and therefore **which task clusters get stressed hardest**.*

> How to use this file: identify the use case you're working on → read its dominant failure mode + success metric → that tells you which cluster playbook to open and which `AT-`/`EVL-` tasks are load-bearing. Task IDs resolve in [`task-catalog.md`](task-catalog.md). All vendor/benchmark figures are **vendor-reported or point-in-time — *verify current*** (sourced in `Research/aidlc-usecases.md`).

## The shared spine (every use case runs this)

Before specializing, note the tasks that recur in *almost every* row — the universal AIDLC loop:
- **Observe:** `EVL-01` verify instrumentation · `AT-48` wire the flywheel.
- **Define "good":** `AT-08` rubric (the eval is the PRD) · `AT-09`/`EVL-11` golden + adversarial datasets · `EVL-03`–`EVL-05` open-code → taxonomy → quantify.
- **Grade:** `AT-10`/`EVL-07` code scorers · `AT-11`/`EVL-08` LLM-judge + `AT-12`/`EVL-09` calibration.
- **Gate:** `AT-16` quality bar · `AT-49`/`EVL-12` eval-gated CI · `AT-54` go/no-go.
- **Ship:** `AT-50` pin bundle · `AT-51`/`EVL-16` canary/shadow · `AT-53` rollback.
- **Monitor:** `AT-55`/`EVL-13` online scoring + drift · `AT-58` cluster failures · `AT-61`/`EVL-14` RCA · `AT-59` cost/latency/quality.
- **Economics & comms:** `AT-70` cost-per-task · `AT-74` pricing · `AT-84` acceptance · `AT-81` exec update.

The sections below highlight what is *distinctive* per use case, not the whole spine.

## Inverse index — which use cases stress each cluster hardest

If you're strengthening a cluster, these are its richest proving grounds:

| Cluster → playbook | Stressed hardest by |
|---|---|
| Discovery → [`discovery-playbook.md`](discovery-playbook.md) | UC-01, UC-02, UC-03, UC-09 (high trace volume) |
| Eval & Spec → [`eval-spec-playbook.md`](eval-spec-playbook.md) | **All** (universal spine) |
| System & Agent → [`system-agent-playbook.md`](system-agent-playbook.md) | UC-03, UC-04, UC-05, UC-09, UC-11 |
| Training Flywheel → [`training-flywheel-playbook.md`](training-flywheel-playbook.md) | UC-03, UC-10, UC-14 (most app-PMs only `AT-46/47/48`) |
| Delivery → [`delivery-playbook.md`](delivery-playbook.md) | **All**, esp. UC-09, UC-13, UC-14 |
| Measurement → [`measurement-playbook.md`](measurement-playbook.md) | UC-09 (`EVL-15`), UC-10/UC-11 (online A/B), UC-01/02/05 |
| Safety → [`safety-substrate.md`](safety-substrate.md) | UC-15, UC-12, UC-13, UC-01, UC-02 |
| Inference Econ → [`inference-economics.md`](inference-economics.md) | UC-01, UC-02, UC-10, UC-11 |
| Commercial → [`commercial-playbook.md`](commercial-playbook.md) | UC-01 (outcome pricing), UC-07, UC-08, UC-12 |

---

## A. Conversational service agents

### UC-01 · Customer-support agent (chat / deflection)
- **What:** LLM agent resolves inbound support conversations end-to-end (answers, refunds, lookups) and escalates the rest.
- **Dominant failure mode:** **confident wrong / hallucinated policy** carrying the company's authority (Air Canada, Cursor "Sam"); jailbreak/prompt injection (Chevy-$1).
- **Success metric:** **resolution/deflection rate with a *pinned* definition**, groundedness, CSAT parity, escalation precision/recall, over-refusal, cost-per-resolution.
- **Eval focus:** judge tone/faithfulness + calibration; groundedness monitor; refusal calibration; conversation transition-failure localization.
- **Distinctive tasks:** `AT-11`/`AT-12`, `AT-56`, `AT-65`/`AT-66`, `AT-67`, `EVL-15`, `AT-74` (outcome pricing), `AT-84`. Inherits `T-005`, `T-006`, `T-052`, `T-062`, `T-088`.

### UC-02 · Voice agent (telephony)
- **What:** Real-time STT→LLM→TTS agent over telephony: support, booking, intake, qualification.
- **Dominant failure mode:** **latency / turn-taking** failure + mid-call task failure; STT errors compounding; spoken hallucinations are un-reviewable.
- **Success metric:** end-to-end + per-hop latency (p50/95/99) — bar is **sub-~800ms (*verify current*)** — barge-in time, containment, escalation accuracy, cost-per-call.
- **Eval focus:** everything in UC-01 plus latency/SLO and in-call tool-call accuracy.
- **Distinctive tasks:** `AT-59` (latency a primary axis), `AT-24`/`AT-25`, `AT-27`/`AT-28`, `EVL-15`; inherits `T-117` (SLO/SLI), `T-060`.

## B. Builder & analyst copilots

### UC-03 · Coding agent / copilot
- **What:** Generates, edits, lands code from NL intent — autocomplete → IDE agent → autonomous issue→PR.
- **Dominant failure mode:** **plausible-but-wrong diffs**; compounding multi-file edits; **benchmark contamination** inflating scores; perceived ≠ measured productivity (METR RCT, *verify current*).
- **Success metric:** execution/test-pass on **contamination-controlled private sets**, acceptance/retention, *measured* cycle-time, cost-per-task.
- **Eval focus:** execution/assertion graders (code is checkable); RL-env/sandbox/verifier; contamination check is the defining hazard.
- **Distinctive tasks:** `AT-02`/`AT-05`/`AT-86` (fast frontier → constant probes), `AT-10`/`EVL-07`, `AT-43`/`AT-44`/`AT-45`, `AT-47`, `AT-49`/`EVL-12`. Overlays `O-PLG-001`/`O-PLG-002`/`O-PLG-014`, `T-116`.

### UC-04 · Data-analyst / text-to-SQL / BI agent
- **What:** Turns NL questions into governed warehouse queries + trustworthy answers (a grounded data-analyst agent spec).
- **Dominant failure mode:** **semantically-wrong SQL that runs cleanly**; wrong join grain / row explosion; null/dedup errors; schema > context window.
- **Success metric:** **execution accuracy vs golden SQL (result-set match)**, schema-linking precision, groundedness (numbers trace to a query), % auto-answered.
- **Eval focus:** deterministic execution/result-match scorer; schema retrieval/linking + retrieval-quality eval; plan→validate→repair loop.
- **Distinctive tasks:** `AT-10`/`EVL-07`, `AT-22`/`AT-23`, `AT-24`, `AT-27`, `AT-56`, `EVL-06`/`EVL-11`. Inherits `T-122`, `T-123`, `T-124`, `T-081`, `T-085`.

## C. Knowledge & document AI

### UC-05 · RAG / enterprise search assistant
- **What:** QA grounded in a permissioned corpus, returning cited, permission-aware answers.
- **Dominant failure mode:** **retrieval miss → ungrounded answer**; cross-source contradiction hidden behind a citation; permission leakage.
- **Success metric:** **recall@k and groundedness measured *separately* from generation**, citation correctness, faithfulness, permission-correctness (zero tolerance), freshness.
- **Eval focus:** RAG pipeline design + retrieval-quality eval; groundedness monitor; connector/MCP governance; permission posture.
- **Distinctive tasks:** `AT-22`/`AT-23`, `AT-21`, `AT-56`, `AT-26`, `AT-72`, `EVL-08`; inherits `T-048` (entitlements), `T-085`/`T-121`, `O-B2B-002`.

### UC-06 · Document extraction & processing (IDP)
- **What:** Extracts structured fields from invoices, contracts, forms, IDs, KYC packets with confidence-based human review.
- **Dominant failure mode:** **silent field errors at scale**; mis-calibrated confidence; missing line-items; layout/vendor drift.
- **Success metric:** field-level F1, **straight-through-processing rate**, confidence calibration, exception rate by doc type.
- **Eval focus:** deterministic schema/field scorers; slice-by-doc-type evals; confidence-routing as human-in-loop design; bounding-box grounding.
- **Distinctive tasks:** `AT-10`/`EVL-07`, `AT-14`, `AT-56`, `AT-60` (corrections → flywheel); inherits `T-054`, `T-064`, `T-032`, `O-FIN-001`/`O-FIN-006`/`O-FIN-011`, `O-B2B-002`.

## D. GTM & content

### UC-07 · Sales copilot / AI SDR
- **What:** Researches, enriches, personalizes, and runs outbound/CS motions.
- **Dominant failure mode:** **generic "obviously-AI" personalization**; **domain-reputation/deliverability damage at scale**; over-automation; compliance (CAN-SPAM/GDPR).
- **Success metric:** reply/positive-reply rate, meetings booked, bounce rate, inbox-placement/domain-health, personalization quality.
- **Eval focus:** personalization judge + calibration; the deliverability/"don't send junk" guardrail (a spam-floor analog).
- **Distinctive tasks:** `AT-11`/`AT-12`, `AT-65`/`AT-66`, `AT-79`, `AT-60`; inherits `T-099`, `T-129`, `O-B2B-003`/`O-B2B-006`/`O-PLG-005`, `O-CON-003`/`O-CON-010`.

### UC-08 · Enterprise content generation
- **What:** Drafts brand-consistent (and in regulated settings, compliant) content at scale.
- **Dominant failure mode:** **off-brand voice**; **fabricated facts/claims** in published content; "AI slop"; data-use concerns.
- **Success metric:** brand-voice adherence (judge + human), factuality/groundedness vs source-of-truth, edit/acceptance rate, compliance pass-rate.
- **Eval focus:** LLM-judge for tone/brand-voice + calibration (the core eval); grounding + Knowledge-Graph RAG; brand-safety guardrails; data-rights/consent.
- **Distinctive tasks:** `AT-11`/`AT-12`, `AT-56`, `AT-65`/`AT-66`, `AT-22`, `AT-72`/`AT-85`; inherits `T-045`, `T-057`, `T-009`.

### UC-16 · Meeting / conversation intelligence
- **What:** Captures calls/meetings → transcripts, faithful summaries, action items, revenue signals.
- **Dominant failure mode:** **unfaithful summary (invented commitments)**; diarization/attribution errors; recording-consent/privacy.
- **Success metric:** summary faithfulness + coverage (judge + human), action-item precision/recall, transcription WER + diarization, CRM-field accuracy, consent-compliance.
- **Eval focus:** faithfulness/coverage judge + calibration; groundedness to transcript; privacy + recording-consent/disclosure.
- **Distinctive tasks:** `AT-11`/`AT-12`, `AT-56`, `AT-60`, `AT-72`/`AT-85`, `EVL-08`; inherits `T-002`, `T-145`, `T-099`/`O-B2B-009`.

## E. Orchestration

### UC-09 · Agentic workflow automation
- **What:** Multi-step, tool-using agent executes a business process via plan-act-observe loops.
- **Dominant failure mode:** **compounding/cascading error** (0.95^20 ≈ 36%, *verify current*); tool misuse; unbounded loops; meltdown; irreversible wrong actions. **Reliability ≠ accuracy.**
- **Success metric:** **pass^k / consistency** (not just pass@1), end-to-end task completion (state match), per-transition success, tool-call accuracy, cost/steps.
- **Eval focus:** harness/loop + budget design; tool schema + tool-call accuracy + tool-reliability mining; MCP governance; transition-failure matrix; safe rollout/rollback for autonomous actions.
- **Distinctive tasks:** `AT-27`/`AT-28`, `AT-24`/`AT-25`/`AT-07`, `AT-26`, `AT-30`/`AT-32`, `EVL-15`, `AT-58`, `AT-43`/`AT-45`, `AT-51`/`AT-53`/`EVL-16`; inherits `T-060`, `T-067`.

## F. Ranking & personalization

### UC-10 · Recommendation system (generative / ML)
- **What:** Predicts or generates the next-best item (feed, product, video, music); incl. generative recsys via Semantic IDs.
- **Dominant failure mode:** **engagement-bait vs long-term retention**; cold-start/long-tail; the **online↔offline gap**; serving cost/latency at scale.
- **Success metric:** **online engagement/retention A/B lifts** (the arbiter); offline recall/NDCG (proxy); segment effects; serving cost/latency.
- **Eval focus:** leans on **classic experimentation** over LLM-judges; slice/cold-start evals; bake-off; online A/B of model change; drift + serving economics.
- **Distinctive tasks:** `AT-14`, `AT-29`, `AT-52`, `AT-57`, `AT-59`/`AT-70`, `AT-46`/`AT-47`, `EVL-13`; inherits `T-037`/`T-038`/`T-069`/`T-078`/`T-079`/`T-137`, `T-013`/`T-014`/`T-112`, `O-CON-005`/`O-CON-008`/`O-CON-013`.

### UC-11 · Search ranking & relevance
- **What:** Orders results/supply to maximize a downstream outcome (web/site/e-comm/marketplace; the retrieval layer inside RAG).
- **Dominant failure mode:** **optimizing clicks not outcomes**; relevance vs coverage/long-tail; a ranking change that cuts liquidity without an A/B catching it.
- **Success metric:** recall@k/NDCG (offline); search-to-fill or answer-success (online); per-query-type performance; A/B outcome lift with guardrails.
- **Eval focus:** bridges RAG retrieval eval and online-experiment ranking; slice by query type.
- **Distinctive tasks:** `AT-22`/`AT-23`, `AT-29`, `AT-52`, `AT-14`, `AT-57`, `EVL-13`; inherits `T-037`/`T-038`/`T-069`/`T-079`, `T-011`, `O-MKT-003`/`O-MKT-011`.

## G. Vertical copilots

### UC-12 · Legal vertical copilot
- **What:** Research, drafting, contract review/redlining, document Q&A, chronology over legal corpora.
- **Dominant failure mode:** **citation hallucination (sanctionable)**; retrieving tangential law → wrong rule; overconfidence in a high-stakes domain; refusals.
- **Success metric:** hallucination rate (and conditional-on-responding), accuracy vs expert baseline, citation correctness/groundedness, responsiveness vs refusal. *(Stanford RegLab / Vals VLAIR figures — verify current.)*
- **Eval focus:** legal-research retrieval + retrieval-quality eval; groundedness/citation monitor (the cardinal metric); judge calibrated against lawyers; adversarial bar-exam sets; red-team + pre-release gate; buyer trust narrative.
- **Distinctive tasks:** `AT-22`/`AT-23`, `AT-56`, `AT-11`/`AT-12`, `AT-09`/`EVL-11`, `AT-63`/`AT-68`, `AT-86`, `AT-82`/`AT-83`, `AT-72`; inherits `T-054`, `O-B2B-001`/`O-B2B-002`, `O-FIN-013`.

### UC-13 · Clinical documentation / health copilot
- **What:** Ambient AI drafts the visit note for clinician review; clinical summarization.
- **Dominant failure mode:** **hallucinated OR omitted clinical facts**; side-conversation capture; accent/specialty degradation; PHI handling; over-reliance.
- **Success metric:** note accuracy incl. **omissions** vs clinician edits, edit/acceptance rate, time-saved + after-hours-EHR-time, specialty-sliced accuracy, PHI-safety.
- **Eval focus:** groundedness incl. omission detection; judge calibrated to clinicians + specialty slices; clinician sign-off is human-in-loop **by construction**; clinician edits → flywheel; PHI privacy + consent.
- **Distinctive tasks:** `AT-56`, `AT-11`/`AT-12`, `AT-14`, `AT-60`, `AT-66`, `AT-67`, `AT-72`/`AT-85`, `AT-84`; inherits `T-048`, `T-054`/`T-055`, `T-117`. *(No `O-HLTH-*` overlay exists yet — flagged.)*

### UC-14 · Fraud & AML detection (fintech)
- **What:** Scores transactions/onboarding for fraud + financial crime in real time; ML core + LLM-assisted investigation.
- **Dominant failure mode:** **false negatives (regulatory/loss)** vs false-positive overload; drift as tactics evolve; unexplainable alerts failing audit.
- **Success metric:** precision/recall (TPR vs FPR), alert volume vs review capacity, fraud-loss vs approval-rate trade-off, detection latency, drift, **explainability/audit-readiness**.
- **Eval focus:** **most overlay-heavy use case** — `O-FIN-*` is its native taxonomy; datasets + slice by risk tier; drift; quantify failure rates.
- **Distinctive tasks:** `AT-09`, `AT-14`, `AT-57`, `AT-16`, `EVL-05`, LLM-assist via `AT-08`/`AT-11`/`AT-56`; overlays `O-FIN-014`/`O-FIN-004`/`O-FIN-005`/`O-FIN-001`/`O-FIN-011`/`O-FIN-006`/`O-FIN-002`; inherits `T-033`, `T-070`/`T-071`, `T-031`.

## H. Cross-cutting

### UC-15 · Trust & safety / guardrail layer
- **What:** The policy/guardrail surface every other use case ships — define-what-it-must-never-do, filters, jailbreak/prompt-injection defense, PII, refusal calibration.
- **Dominant failure mode:** **jailbreak / prompt injection**; over-refusal (blocks valid use); under-refusal (allows harm); PII leakage; silent safety regressions.
- **Success metric:** jailbreak/abuse-resistance vs versioned corpus, refusal vs over-refusal on paired benign/harmful sets, PII-leak rate, prompt-injection resistance, time-to-contain — **all as release gates**.
- **Eval focus:** the entire [`safety-substrate.md`](safety-substrate.md) cluster.
- **Distinctive tasks:** `AT-63`/`AT-64`, `AT-65`/`AT-66`, `AT-67`, `AT-68`, `AT-17`, `EVL-11`, `AT-72`/`AT-85`; inherits `T-033`/`T-048`, `T-060`/`T-067`, `O-FIN-010`, `O-MKT-008`.

---

*Coverage: 16 use cases linked to a curated, high-signal subset of the 324 tasks (not "everything touches everything"). Source: `Research/aidlc-usecases.csv` + `aidlc-usecases.md`. Vendor/benchmark numbers are point-in-time — **verify current** before citing.*
