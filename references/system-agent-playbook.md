# System & Agent Design — playbook

*Cluster 3 · 14 tasks (`AT-19`–`AT-32`) · all `now`. The closest cluster to the old Definition work, and the most expanded.*

This is where the AI PM specs the machine itself — the **prompts, context, retrieval, tools and MCP servers, the loop, the routing, the memory**. Where Part II wrote one spec, the AI PM tends a dozen interacting surfaces, each of which can regress the others. The through-line: **almost everything here carries high regression risk** — a quiet edit anywhere changes the output distribution everywhere — so almost everything here is **gated by an eval before it ships**. (Look at the table: `regr` is `high` for 10 of 14.)

## When this applies

- You are **changing a prompt, context budget, retrieval pipeline, tool schema, loop, or routing** — anything that shapes behavior.
- Hallucination is actually a **retrieval** problem (`AT-22`/`AT-23`) or a **tool-call** problem (`AT-24`/`AT-25`), not a "smarter model" problem.
- You're standing up or bounding an **agent** (loop, stop conditions, step/token budgets) (`AT-27`/`AT-28`).
- You're **choosing or routing** models for cost/quality (`AT-29`/`AT-30`).
- You're wiring in a **third-party tool / MCP server** (`AT-26`) — see the governance gate below.

## The tasks

| id | task | autonomy | eval | blast | regr | safety | status |
|---|---|---|---|---|---|---|---|
| AT-19 | Author and version a prompt in the registry | copilot | gated | low | high | med | now |
| AT-20 | Prompt regression test before merge | autonomous | gated | low | high | med | now |
| AT-21 | Context-window budget design | copilot | partial | low | med | none | now |
| AT-22 | Design or iterate a RAG retrieval pipeline | copilot | partial | med | high | med | now |
| AT-23 | Eval retrieval quality (recall@k + groundedness) | copilot | gated | low | high | med | now |
| AT-24 | Design a tool or function schema | copilot | partial | med | high | med | now |
| AT-25 | Eval tool-call accuracy | copilot | gated | low | high | med | now |
| AT-26 | Select or evaluate an MCP server (governance + reliability) | copilot | partial | med | med | **high** | now |
| AT-27 | Design the agent loop or harness | copilot | partial | high | high | **high** | now |
| AT-28 | Set the agent step, tool-call, and token budget | copilot | partial | med | med | med | now |
| AT-29 | Run a model bake-off on your eval set | copilot | gated | med | high | med | now |
| AT-30 | Design a model routing policy | copilot | gated | med | high | med | now |
| AT-31 | Run a prompt-optimization pass (DSPy/GEPA) | autonomous | gated | low | high | med | now |
| AT-32 | Design agent memory | copilot | partial | med | med | **high** | now |

Per-task steps + full 6-axis read: [`task-catalog.md`](task-catalog.md).

## The method (design surfaces, each eval-gated)

The cluster is a set of interacting surfaces. Treat each as *code under an eval*:

- **Prompts are code** (`AT-19`/`AT-20`): draft → diff vs current → tag a version → link the governing eval → register; **never edit a prod prompt in place**, and gate the merge on a regression test (`AT-20`, which runs unattended as CI).
- **Retrieval caps answers** (`AT-22`/`AT-23`): chunk by meaning, pick an embedding model, add a reranker, wire context to the prompt — then **eval retrieval separately from generation** (recall@k + groundedness), or you'll tune the wrong half. A wrong chunk is a confident wrong answer.
- **Context is a paid, scarce resource** (`AT-21`): rank sources by value-per-token, set a budget, test truncation/eviction. More tokens is not more quality past the dilution point.
- **Tools are a contract** (`AT-24`/`AT-25`): the description *is a prompt* — design for the model's job, make errors part of the contract, then score tool *selection* and *argument* accuracy (including should-not-call cases).
- **The harness is the product** (`AT-27`/`AT-28`): define plan-act-observe, **termination conditions**, max steps/tool-calls/tokens, a per-run cost cap, and error/retry handling. An agent with no stop condition fails unsafely and burns money.
- **Routing is the cost-quality lever** (`AT-29`/`AT-30`): pick on *your* eval (cheapest model that clears your bar wins), define a fallback chain, and eval routed-vs-single. Most traffic is easy — don't pay frontier prices for it.
- **Memory is state with risk** (`AT-32`): scope it, set read/write + eviction policy, address privacy of stored memory (hence `safety:high`). Stale or leaked memory is worse than none.
- **Optimize against the eval, not vibes** (`AT-31`): an optimizer that overfits the dev set is a regression in disguise — validate the gain on a holdout.

## MCP server selection — governance gate (AT-26)

`AT-26` carries **`safety:high`** because an MCP server is third-party code inside your agent loop. It MUST honor the workspace **MCP-governance rule (always-applied): Runlayer-managed servers only.**

1. **Provenance first:** if a server is not Runlayer-managed (no `runlayer.com`, not `runlayer run <uuid>`), it is a **shadow MCP** — flag it and stop. Shadow servers bypass org security policy, audit logging, and access controls.
2. **Then reliability:** test schema quality + tool-call success rate (reuse `AT-07` tool-log mining and `AT-25` tool-call accuracy).
3. **Then permission surface:** review the scope it requests; least privilege.
4. **Approve or reject** — security/PM own the governance call, not just the reliability number.

## Tools

- **Prompts:** Braintrust prompts, LangSmith Hub, PromptLayer.
- **RAG:** LlamaIndex, LangChain, pgvector / Pinecone / Weaviate, Cohere rerank; eval with Ragas, Arize Phoenix RAG metrics.
- **Tools/agents:** JSON Schema, OpenAI/Anthropic tool specs, MCP (Runlayer-managed); harness via LangGraph, OpenAI Agents SDK, or a custom loop; BFCL-/τ-bench-style scenarios for tool-call eval.
- **Routing/optimization:** LiteLLM, OpenRouter, NotDiamond/RouteLLM, Martian; DSPy, GEPA.

## Pitfalls

- Editing prod prompts untracked; no eval link; prompt sprawl; shipping a prompt edit ungated.
- Chunking by bytes not meaning; no reranker; **only evaluating the final answer** (ignoring retrieval recall).
- Human-centric tool naming; undefined error semantics; scoring only the final answer (ignoring argument errors / should-not-call cases).
- **No termination condition; unbounded tool-calls; silent infinite loops; no per-run cost cap.**
- Routing without an eval; no fallback; a routing signal that misclassifies hard tasks as easy.
- Installing **shadow/unmanaged MCP servers**; trusting marketing over testing; ignoring permission scope.
- Unbounded memory growth; stale memory poisoning answers; storing PII without controls.
- Overfitting the optimizer to the dev set with no holdout validation.

## Execution heuristics

- *Prompts are code* — version them, link them to an eval, never edit prod in place.
- *Retrieval quality caps answer quality;* a wrong chunk is a confident wrong answer.
- *Separate retrieval failures from generation failures, or you tune the wrong half.*
- *The tool description is a prompt;* make errors part of the contract.
- *The harness is the product;* an agent with no stop condition fails unsafely.
- *Routing is the cost-quality lever* — the cheapest model that clears your bar wins.
- *Memory is state with privacy and staleness risk.*
- *An MCP server is third-party code in your agent loop* — managed-only, vet before wiring.

## Hand-offs

Gated by **Eval & Spec** ([`eval-spec-playbook.md`](eval-spec-playbook.md)). Routing/portfolio choices connect to [`inference-economics.md`](inference-economics.md) (`AT-69`/`AT-70`). The harness + reward structure prefigures training (`AT-43` RL environment = dataset + harness + scoring) in [`training-flywheel-playbook.md`](training-flywheel-playbook.md). Ship changes through [`delivery-playbook.md`](delivery-playbook.md).

**Stressed hardest by** UC-03 (coding), UC-04 (text-to-SQL), UC-05 (RAG), UC-09 (agentic automation), UC-11 (search/ranking) — see [`usecase-playbooks.md`](usecase-playbooks.md).
