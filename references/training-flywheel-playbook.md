# Data & Training Flywheel — playbook  *(Phase-2 / `later` — only if you are training, not just orchestrating)*

*Cluster 4 · 16 tasks (`AT-33`–`AT-48`). **12 are flagged `later`; 4 pay off `now`.** This is the cluster that separates a model **builder** from a model **orchestrator**.*

> **Read this gate first.** If your team **orchestrates frontier-model APIs** (gpt-class agent loop + deterministic grounding tools + an eval harness as the regression gate), you are **not training yet**, so RLHF, reward models, RL environments, and fine-tuning are **deferred, not deleted**. Do the 4 `now` tasks below; skip the rest until your evals prove that prompting + retrieval have hit a ceiling. The day they do, this cluster opens. **Do not start preference-data / reward-model / RL-env work just because a task looks relevant — confirm "are we actually training?" first.**

One structural insight governs the whole cluster: **an RL environment and an agent eval are the same object** — a dataset, a harness, and a scoring rule. So the eval work in [`eval-spec-playbook.md`](eval-spec-playbook.md) is already half of the training work here.

## Do these NOW even as an orchestrator

| id | task | autonomy | eval | why it pays off now |
|---|---|---|---|---|
| AT-42 | Decide fine-tune vs prompt vs RAG | human-led | partial | The build-method gate — usually the answer is prompt/RAG until evals prove otherwise. Fine-tuning is the last resort, not the first. |
| AT-46 | Generate and validate synthetic data | copilot | partial | Bootstraps eval scenarios when prod data is thin — *if validated for diversity + leakage*. |
| AT-47 | Run a train/eval contamination and leakage check | autonomous | gated | A contaminated eval flatters you into shipping a worse system; runs as an automated gate. |
| AT-48 | Wire the data flywheel (prod trace → dataset/eval/train) | copilot | partial | The compounding asset: capture-to-dataset rules, sampling policy, PII scrub, route to eval (now) / train (later). |

## The rest — `later` (when training begins)

| id | task | autonomy | eval | safety | flywheel |
|---|---|---|---|---|---|
| AT-33 | Design a preference-data collection task | copilot | partial | med | producer |
| AT-34 | Write annotation and rater guidelines | human-led | partial | med | producer |
| AT-35 | Recruit and calibrate raters; inter-rater agreement | human-led | partial | med | producer |
| AT-36 | Audit preference-data quality | copilot | partial | med | producer |
| AT-37 | Spec a reward-model train and eval | human-led | gated | high | producer |
| AT-38 | Detect reward hacking and reward-model gaming | copilot | partial | high | producer |
| AT-39 | Design an RLAIF or Constitutional preference pipeline | copilot | partial | high | producer |
| AT-40 | Curate an SFT dataset | copilot | partial | med | producer |
| AT-41 | Plan a distillation run and eval gate | copilot | gated | med | producer |
| AT-43 | Author an RL environment (dataset + harness + reward) | human-led | gated | high | producer |
| AT-44 | Design a sandbox or tool emulator for an environment | copilot | partial | high | none |
| AT-45 | Design and anti-game a reward or verifier function | human-led | gated | high | producer |

Per-task steps + full 6-axis read: [`task-catalog.md`](task-catalog.md). Note every `later` task is a flywheel **`producer`** with **high** regression risk — one bad label compounds through a reward model into the policy.

## The method (when you do train)

```text
AT-42 decide the build method (prompt / RAG / fine-tune — evidence, not instinct)
  → data: AT-33 preference task → AT-34 guidelines → AT-35 raters + IRR → AT-36 audit
          (or AT-39 RLAIF: AI labels routine, humans the hard/high-stakes; AT-40 SFT set)
  → reward: AT-37 spec RM train+eval → AT-45 anti-game the reward → AT-38 detect reward hacking
  → environment: AT-43 RL env (= dataset + harness + reward) → AT-44 deterministic sandbox
  → AT-41 distillation gated on eval → AT-46 synthetic data → AT-47 contamination check
  → AT-48 flywheel wires prod traces back into the loop
```

- **Build-method discipline** (`AT-42`): frame the gap, estimate cost/latency/quality of prompt vs RAG vs train, check data availability and maintenance burden, recommend with eval evidence. For an orchestrator the answer is usually prompt/RAG.
- **Data quality sets the ceiling:** garbage pairs train a garbage reward; inconsistent raters train a noisy reward (`AT-35` inter-rater agreement is the quality floor). Audit before you train, not after (`AT-36`).
- **The reward is a spec the policy will attack** (`AT-45`/`AT-38`): any reward will be gamed; the question is whether you find the exploit before your users do. Verifiable rewards (RLVR) are powerful and brittle.
- **Environments = evals** (`AT-43`): build the dataset + harness + scoring rule *once*, use it for grading today and training later. Sandboxes must be deterministic and isolated (`AT-44`) or they teach the wrong lesson.
- **Validate the data you fabricate** (`AT-46`) and **prove clean splits** (`AT-47`): unvalidated synthetic data is contamination in a costume; exact-match-only leakage checks miss near-dupes.

## Tools

- **Preference data / labeling:** Surge AI, Mercor, Labelbox, Argilla, Snorkel, Label Studio.
- **Training / RL:** TRL, OpenRLHF, prime-rl, Prime Intellect verifiers + Environments Hub.
- **Sandboxes:** Modal, E2B, Daytona, Docker.
- **Gates / eval:** Braintrust, vLLM (serving the student), dedup/embedding tools for leakage.

## Pitfalls

- **Starting training prematurely** — fine-tuning before evals prove prompt/RAG hit a ceiling; ignoring data cost; no eval evidence for the build choice (`AT-42`).
- Unrepresentative prompt distributions; ambiguous comparisons; no pilot (`AT-33`); vague rater guidelines with no examples/tie-breaks (`AT-34`).
- No calibration set; ignoring low inter-rater agreement; unmanaged vendor quality variance (`AT-35`).
- No held-out reward-model eval; reward target misaligned with product; trusting the reward number with no adversarial probing (`AT-37`/`AT-38`).
- Easily-gamed reward; reward proxy diverging from quality (`AT-45`); non-deterministic / leaky sandbox (`AT-44`).
- Treating environments and evals as separate objects; leakage into the eval set; mode-collapsed synthetic generations.

## Execution heuristics

- *Fine-tuning is the last resort, not the first.*
- *Preference data is the product spec encoded as comparisons;* garbage pairs train a garbage reward.
- *If raters disagree, the reward learns noise* — agreement is the quality floor of the whole loop.
- *Any reward will be gamed* — the question is whether you find the exploit first.
- *An RL environment and an agent eval are the same object.*
- *Unvalidated synthetic data is contamination in a costume.*
- *A contaminated eval flatters you into shipping a worse model.*

## Hand-offs

Built on top of **Eval & Spec** ([`eval-spec-playbook.md`](eval-spec-playbook.md)) — datasets, scorers, and judges are reused. `AT-48` closes the loop from **Measurement** ([`measurement-playbook.md`](measurement-playbook.md)). Reward/data-rights questions intersect [`inference-economics.md`](inference-economics.md) (`AT-72`) and [`safety-substrate.md`](safety-substrate.md).

**Genuinely relevant to few use cases:** the cases that actually train/distill/RL — UC-03 (coding envs), UC-10 (recsys models), UC-14 (fraud models). **Most application PMs touch only `AT-46`/`AT-47`/`AT-48`** (and `AT-42`). See [`usecase-playbooks.md`](usecase-playbooks.md).
