#!/usr/bin/env python3
"""select_task.py — map a free-text request to candidate AIDLC task ids.

Keyword-scores a query against the task library (name, description, cluster,
reasoning_model, tools, pitfalls) AND applies a small curated concept prior so that
incident-language paraphrases route correctly — prompt-injection / "ignore your
instructions" / jailbreak / PII-leak / harmful-output → Safety tasks, not a model
bake-off; "every number traces to a tool" → groundedness (AT-56); "PRD" → the eval
spec hub (AT-08). Returns the top matches with their 6-axis read (incl. blast from
the bundle) so you can hand an id straight to autonomy_gate.py. No fabricated data.

Sources (bundled data/ first, then Research/, or pass --aidlc-csv / --classic-csv):
  aidlc_microtasks.csv     AT-/EVL- AIDLC tasks (primary)
  data/aidlc_axes.csv      6-axis catalog incl. blast (for the displayed axes)
  pm_microtask_database.csv  classic T-/O- tasks (with --include-classic)
  aidlc-usecases.csv       use-case -> task-id index (with --usecase UC-XX)

Usage:
  python select_task.py "someone tricked the bot into ignoring its instructions"
  python select_task.py "the eval score dropped, find the root cause" --top 5
  python select_task.py "ground every number in a tool" --include-classic
  python select_task.py --usecase UC-04            # list a use case's task ids
  python select_task.py "write a judge" --json

Filters: --phase, --cluster, --leverage, --status (now|later). --top N (default 8).
A weak top score (< --floor) prints the §7 escape-hatch (compose, don't force-fit).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402

# Field weights: a hit in the title counts more than a hit in a pitfall list.
FIELD_WEIGHTS = {
    "name": 6.0, "cluster": 2.0, "description": 3.0, "reasoning_model": 2.5,
    "tools_in_practice": 1.5, "common_pitfalls": 1.5, "ai_opportunity": 1.0,
    "general_steps": 1.0, "why_specific": 1.0, "pain_points_ai": 1.0,
}

# Curated concept prior: (trigger phrases/tokens) -> (task-id boosts, cluster boosts).
# Multi-word entries are matched as substrings of the query; single words as tokens.
# This fixes incident-language paraphrases that pure keyword scoring mis-routes (H2).
# Unambiguous safety triggers (multi-word phrases or single tokens with no benign sense).
# Homograph tokens ("leak", "injection") are NOT here — they route to Safety only with a
# confirming context (see _AMBIGUOUS below), so "memory leak" / "dependency injection" stay
# out of the Safety substrate.
CONCEPT_PRIOR = [
    (("jailbreak", "jailbroken", "jailbreaks", "prompt injection",
      "ignore instructions", "ignoring instructions", "ignoring its instructions",
      "ignore its instructions", "tricked the bot", "tricked into", "bypass the guardrail",
      "ignore the system prompt", "ignore previous", "reveal its system prompt",
      "reveal the system prompt", "hidden system prompt", "extract the system prompt",
      "leak the system prompt", "system prompt extraction", "expose the system prompt"),
     {"AT-63": 12, "AT-64": 12, "AT-65": 11, "AT-68": 10}, {"safety": 6}),
    (("pii", "exfiltration", "exfiltrate", "exfiltrating", "personal data", "data leak",
      "leaking pii", "leaks pii", "leaked pii", "leaking personal", "pii leak"),
     {"AT-68": 14, "AT-72": 12, "AT-65": 9}, {"safety": 5}),
    (("harmful", "abuse", "abusive", "toxic", "toxicity", "unsafe", "nsfw",
      "malicious", "harmful output", "offensive", "slur", "slurs", "hateful", "racist",
      "insulting", "say offensive", "saying offensive"),
     {"AT-63": 8, "AT-65": 8, "AT-66": 8, "AT-67": 8, "AT-68": 8}, {"safety": 4}),
    (("groundedness", "grounded", "grounding", "ungrounded", "citation", "citations",
      "hallucination", "hallucinate", "hallucinated", "every number",
      "traces to a tool", "number traces", "comes from a tool",
      "making things up", "made things up", "fabricating", "fabricated facts",
      "invented", "inventing", "not in the retrieved", "isn't in the docs",
      "made up", "confabulating", "confabulation"),
     {"AT-56": 24, "AT-23": 8}, {}),
    (("metrics tanked", "quality dropped", "quality metrics tanked", "scores fell",
      "score dropped", "figure out why"),
     {"AT-61": 14, "EVL-14": 13}, {"measurement": 4}),
    (("automated grader", "grader agree", "grader agrees", "judge agree",
      "judge agrees", "agree with human", "agree with human raters",
      "human raters", "human labels", "judge against human", "judge vs human"),
     {"AT-12": 9, "EVL-08": 7, "EVL-09": 6}, {"eval": 2}),
    (("block merges", "regresses our eval", "prompt regression",
      "regresses our eval suite", "system prompt regresses"),
     {"AT-20": 12, "EVL-12": 10, "AT-49": 10}, {"delivery": 4}),
    (("feel different lately", "didn't ship anything", "behavior changed",
      "responses feel different", "didn't ship anything new"),
     {"AT-57": 14}, {"measurement": 4}),
    (("evals look green but", "evals look green", "customers complaining in prod",
      "customers are complaining in prod", "offline says good", "prod says bad"),
     {"AT-62": 14}, {"measurement": 4}),
    (("roll out to 5%", "roll out the new model to 5%", "roll back if scores dip",
      "roll back if scores", "canary rollout", "shadow deployment"),
     {"AT-51": 10, "EVL-16": 9}, {"delivery": 3}),
    (("prd", "product requirements", "product requirement"),
     {"AT-08": 13}, {"eval & spec": 3}),
]

# Homograph tokens that fire Safety ONLY when a confirming-context token co-occurs.
# (token-trigger set, required-context set, id-boosts, cluster-boost)
_AMBIGUOUS = [
    # 'leak' (homograph: memory/file-descriptor leak) fires Safety only with a STRONG
    # data/secret co-token — NOT generic 'user'/'info'/'system' (those mis-routed benign
    # engineering queries to Safety, M3-2).
    (("leak", "leaks", "leaking", "leaked"),
     ("pii", "data", "personal", "sensitive", "credential", "credentials", "secret",
      "secrets", "ssn", "password", "passwords", "records", "record", "private",
      "confidential", "api", "key", "keys", "token", "tokens", "exfiltrate", "exfiltration"),
     {"AT-68": 12, "AT-72": 10, "AT-65": 8}, ("safety", 5)),
    # 'injection' (homograph: SQL/dependency injection) needs a prompt/instruction co-token.
    (("injection", "inject"),
     ("prompt", "instruction", "instructions"),
     {"AT-63": 12, "AT-64": 11, "AT-65": 10}, ("safety", 5)),
    # 'trick/manipulate' needs an AI-subject co-token (not generic 'system').
    (("manipulate", "manipulated", "manipulating", "coerce", "coerced", "coercing",
      "trick", "tricked", "tricking", "fooled", "fooling"),
     ("model", "agent", "bot", "assistant", "llm", "chatbot", "ai"),
     {"AT-63": 9, "AT-66": 7, "AT-67": 7}, ("safety", 3)),
    # secret/data exfiltration phrased without 'leak' (reveal/print/dump/steal + a secret
    # token) — covers "print its api keys", "revealed confidential records" (M3-6) without
    # re-introducing the M3-2 over-trigger (it requires a concrete secret/data co-token).
    (("reveal", "reveals", "revealed", "revealing", "expose", "exposed", "exposes",
      "exposing", "exfiltrate", "exfiltrated", "exfiltrating", "print", "printed", "prints",
      "dump", "dumped", "steal", "stole", "stolen", "leak"),
     ("key", "keys", "secret", "secrets", "credential", "credentials", "password",
      "passwords", "token", "tokens", "records", "record", "pii", "confidential", "api"),
     {"AT-68": 18, "AT-72": 12, "AT-65": 10}, ("safety", 6)),
]
# guardrails homograph: only treat as Safety when co-occurring with abuse/jailbreak terms.
_GUARDRAIL_SAFETY_CTX = ("jailbreak", "abuse", "block", "blocks", "blocking", "runtime",
                         "filter", "filters", "content", "safety", "harmful", "injection")


def _concept_bonus(query_phrase: str, query_tokens: list):
    q = query_phrase
    qt = set(query_tokens)

    def hit(key: str) -> bool:
        return (key in q) if " " in key else (key in qt)

    id_bonus, cluster_bonus = {}, {}

    def add(ids, cluster=None):
        for i, w in ids.items():
            id_bonus[i] = id_bonus.get(i, 0) + w
        if cluster:
            c, w = cluster
            cluster_bonus[c] = cluster_bonus.get(c, 0) + w

    for triggers, ids, clusters in CONCEPT_PRIOR:
        if any(hit(t) for t in triggers):
            add(ids, None)
            for c, w in clusters.items():
                cluster_bonus[c] = cluster_bonus.get(c, 0) + w

    # Homograph tokens: require a confirming context so "memory leak" / "dependency
    # injection" / "trick the user" do not mis-route to the Safety substrate (M-2/M-3).
    for tokens, ctx, ids, cluster in _AMBIGUOUS:
        if any(t in qt for t in tokens) and any(c in qt for c in ctx):
            add(ids, cluster)

    if ("guardrail" in qt or "guardrails" in qt) and any(hit(t) for t in _GUARDRAIL_SAFETY_CTX):
        add({"AT-65": 10, "AT-66": 8}, ("safety", 4))
    return id_bonus, cluster_bonus


def _score_row(row: dict, query_tokens: list, query_phrase: str) -> float:
    score = 0.0
    qset = set(query_tokens)
    for field, weight in FIELD_WEIGHTS.items():
        text = row.get(field) or ""
        if not text:
            continue
        toks = _common.tokenize(text)
        if not toks:
            continue
        hits = sum(1 for t in toks if t in qset)
        if hits:
            score += weight * min(hits, 5) * 0.4 + weight
        if query_phrase and query_phrase in text.lower():
            score += weight * 1.5
    return score


def _passes_filters(row: dict, args) -> bool:
    if args.phase and args.phase.lower() not in (row.get("aidlc_phase") or "").lower():
        return False
    if args.cluster and args.cluster.lower() not in (row.get("cluster") or "").lower():
        return False
    if args.leverage and (row.get("ai_leverage") or "").lower() != args.leverage.lower():
        return False
    if args.status and (row.get("phase_status") or "").lower() != args.status.lower():
        return False
    return True


def _axes(row: dict, blast: str) -> str:
    return (
        f"{row.get('ai_leverage','?')} · blast:{blast or '?'} · eval:{row.get('eval_coverage','?')} · "
        f"regr:{row.get('regression_risk','?')} · safety:{row.get('safety_exposure','?')} · "
        f"fly:{row.get('flywheel_linkage','?')}"
    )


def _usecase_lookup(uc_id: str, csv_path: str | None) -> dict:
    path = _common.resolve_csv(csv_path, _common.USECASE_CSV_NAME)
    want = uc_id.strip().upper()
    for row in _common.load_csv(path):
        if (row.get("usecase_id") or "").strip().upper() == want:
            ids = [t.strip() for t in (row.get("relevant_task_ids") or "").split(";") if t.strip()]
            aidlc = [i for i in ids if i.upper().startswith(("AT-", "EVL-"))]
            classic = [i for i in ids if not i.upper().startswith(("AT-", "EVL-"))]
            return {"usecase_id": row.get("usecase_id"), "name": row.get("name"),
                    "eval_focus": row.get("eval_focus"),
                    "aidlc_task_ids": aidlc, "classic_task_ids": classic}
    raise SystemExit(f"use case {uc_id!r} not found in {path}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("query", nargs="*", help="free-text description of the work")
    p.add_argument("--aidlc-csv"); p.add_argument("--classic-csv"); p.add_argument("--usecase-csv")
    p.add_argument("--include-classic", action="store_true", help="also search classic T-/O- tasks")
    p.add_argument("--usecase", help="UC-XX: list that use case's relevant task ids and exit")
    p.add_argument("--phase"); p.add_argument("--cluster")
    p.add_argument("--leverage"); p.add_argument("--status", help="now|later")
    p.add_argument("--top", type=int, default=8)
    p.add_argument("--floor", type=float, default=9.0,
                   help="weak-match floor; below it, print the escape-hatch (heuristic; scores unnormalized)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    if args.usecase:
        uc = _usecase_lookup(args.usecase, args.usecase_csv)
        if args.json:
            print(json.dumps(uc, indent=2, ensure_ascii=False))
        else:
            print(f"{uc['usecase_id']}  {uc['name']}")
            print(f"eval_focus: {uc['eval_focus']}")
            print(f"AIDLC ids (gate-ready, {len(uc['aidlc_task_ids'])}): {', '.join(uc['aidlc_task_ids'])}")
            print(f"classic ids (not --id resolvable, {len(uc['classic_task_ids'])}): {', '.join(uc['classic_task_ids'])}")
        return 0

    if not args.query:
        p.error("provide a query, or use --usecase UC-XX")
    query_phrase = " ".join(args.query).strip().lower()
    query_tokens = _common.tokenize(query_phrase)
    if not query_tokens:
        p.error("query has no searchable terms after tokenization")

    rows = _common.load_csv(_common.resolve_csv(args.aidlc_csv, _common.AIDLC_CSV_NAME))
    if args.include_classic:
        rows = rows + _common.load_csv(_common.resolve_csv(args.classic_csv, _common.CLASSIC_CSV_NAME))
    axes_bundle = _common.load_axes_bundle()
    id_bonus, cluster_bonus = _concept_bonus(query_phrase, query_tokens)

    scored = []
    for row in rows:
        if row.get("aidlc_phase") is not None and not _passes_filters(row, args):
            continue
        s = _score_row(row, query_tokens, query_phrase)
        rid = (row.get("id") or "").upper()
        s += id_bonus.get(rid, 0)
        cl = (row.get("cluster") or "").lower()
        for ckey, cw in cluster_bonus.items():
            if ckey in cl:
                s += cw
        if s > 0:
            scored.append((s, row))
    scored.sort(key=lambda x: (-x[0], x[1].get("id", "")))

    results = []
    for s, row in scored[: args.top]:
        rid = (row.get("id") or "").upper()
        blast = (axes_bundle.get(rid) or {}).get("blast", "")
        results.append({
            "id": row.get("id"), "name": row.get("name"), "cluster": row.get("cluster"),
            "phase": row.get("aidlc_phase") or row.get("phase"),
            "phase_status": row.get("phase_status"),
            "axes": _axes(row, blast), "score": round(s, 2),
        })

    top_score = results[0]["score"] if results else 0.0
    weak = top_score < args.floor

    if args.json:
        print(json.dumps({"query": query_phrase, "weak_match": weak, "floor": args.floor,
                          "results": results}, indent=2, ensure_ascii=False))
        return 0

    if not results:
        print("no candidate tasks matched; broaden the query or try --include-classic")
        return 0
    print(f"query: {query_phrase!r}  ->  top {len(results)} candidates\n")
    for r in results:
        print(f"[{r['score']:>5}] {r['id']:<7} {r['name']}")
        print(f"         cluster={r['cluster']}  status={r['phase_status']}")
        print(f"         axes: {r['axes']}")
    if weak:
        print(f"\nWEAK MATCH (top score {top_score} < floor {args.floor}): likely out-of-catalog.")
        print("Use the compose / escape-hatch flow (SKILL.md §7): nearest invariant + overlay, or ask the human.")
    else:
        print("\nnext: pass an id to autonomy_gate.py for the execution verdict (blast comes from the bundle).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
