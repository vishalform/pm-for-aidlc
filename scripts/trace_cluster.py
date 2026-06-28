#!/usr/bin/env python3
"""trace_cluster.py — cluster failure traces/notes into ranked failure modes (AT-01/58, EVL-04).

Turns raw failure notes into named, ranked clusters so you fix patterns, not
one-offs. Uses TF-IDF cosine + deterministic greedy leader clustering (stdlib
only; no sklearn). Ranks clusters by frequency x mean-severity, names each by its
top distinctive terms, and surfaces a representative exemplar. The LLM should
then VALIDATE/rename the clusters (axial coding is human-owned).

CAVEAT (short notes): lexical TF-IDF can over-split paraphrases ("hallucinated a refund
policy" vs "hallucinated a discount we never offered") or merge superficially similar
ones. This is an ADVISORY first pass — never quote `rank_score` as a measured failure
rate; confirm counts by labeling against the validated taxonomy (EVL-05). For short,
noisy notes, lower --threshold and lean on the human validation step.

Inputs: plain text (one note per line) or CSV with --text-col (+ optional
--id-col, --severity-col where severity is a number; default weight 1).

  python trace_cluster.py --input notes.txt
  python trace_cluster.py --input traces.csv --text-col note --severity-col sev
  python trace_cluster.py --input notes.txt --threshold 0.3 --max-clusters 10 --json

Tuning: --threshold (cosine to join a cluster, default 0.30; higher = tighter).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402


def _load(path: str, text_col, id_col, sev_col):
    if path.lower().endswith(".csv") or text_col:
        rows = _common.load_csv(path)
        if not rows:
            return []
        tcol = text_col or list(rows[0].keys())[0]
        items = []
        for i, r in enumerate(rows):
            txt = (r.get(tcol) or "").strip()
            if not txt:
                continue
            sev = 1.0
            if sev_col and r.get(sev_col):
                try:
                    sev = float(r[sev_col])
                except ValueError:
                    sev = 1.0
            ident = r.get(id_col) if id_col else None
            items.append({"id": ident or f"row{i}", "text": txt, "sev": sev})
        return items
    with open(path, encoding="utf-8") as fh:
        return [{"id": f"line{i}", "text": ln.strip(), "sev": 1.0}
                for i, ln in enumerate(fh) if ln.strip()]


def _tfidf(items):
    docs_tokens = [_common.tokenize(it["text"]) for it in items]
    n = len(items)
    df = {}
    for toks in docs_tokens:
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log((1 + n) / (1 + d)) + 1.0 for t, d in df.items()}
    vecs = []
    for toks in docs_tokens:
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        vec = {t: (c / len(toks)) * idf[t] for t, c in tf.items()} if toks else {}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        vecs.append({t: v / norm for t, v in vec.items()})
    return vecs, idf


def _cosine(a: dict, b: dict) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(t, 0.0) for t, v in a.items())


def _centroid(vecs, idxs):
    acc = {}
    for i in idxs:
        for t, v in vecs[i].items():
            acc[t] = acc.get(t, 0.0) + v
    norm = math.sqrt(sum(v * v for v in acc.values())) or 1.0
    return {t: v / norm for t, v in acc.items()}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True, help="txt (one note/line) or csv")
    p.add_argument("--text-col"); p.add_argument("--id-col"); p.add_argument("--severity-col")
    p.add_argument("--threshold", type=float, default=0.30, help="cosine to join a cluster (default 0.30)")
    p.add_argument("--max-clusters", type=int, default=12, help="max clusters to report")
    p.add_argument("--top-terms", type=int, default=5)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    items = _load(args.input, args.text_col, args.id_col, args.severity_col)
    if not items:
        raise SystemExit("no non-empty notes found")
    vecs, _ = _tfidf(items)

    # deterministic greedy leader clustering (input order)
    clusters = []  # each: {"members": [idx], "centroid": vec}
    for i in range(len(items)):
        best_sim, best_c = 0.0, None
        for c in clusters:
            sim = _cosine(vecs[i], c["centroid"])
            if sim > best_sim:
                best_sim, best_c = sim, c
        if best_c is not None and best_sim >= args.threshold:
            best_c["members"].append(i)
            best_c["centroid"] = _centroid(vecs, best_c["members"])
        else:
            clusters.append({"members": [i], "centroid": dict(vecs[i])})

    summaries = []
    for c in clusters:
        idxs = c["members"]
        size = len(idxs)
        mean_sev = sum(items[i]["sev"] for i in idxs) / size
        rank_score = size * mean_sev
        top_terms = [t for t, _ in sorted(c["centroid"].items(), key=lambda kv: -kv[1])][: args.top_terms]
        rep = max(idxs, key=lambda i: _cosine(vecs[i], c["centroid"]))
        summaries.append({
            "size": size,
            "mean_severity": round(mean_sev, 3),
            "rank_score": round(rank_score, 3),
            "suggested_name": " / ".join(top_terms) if top_terms else "(empty)",
            "exemplar_id": items[rep]["id"],
            "exemplar": items[rep]["text"][:160],
            "member_ids": [items[i]["id"] for i in idxs],
        })
    summaries.sort(key=lambda s: (-s["rank_score"], -s["size"]))
    summaries = summaries[: args.max_clusters]

    if args.json:
        print(json.dumps({"n_items": len(items), "n_clusters": len(clusters),
                          "clusters": summaries}, indent=2, ensure_ascii=False))
        return 0

    print(f"{len(items)} notes -> {len(clusters)} clusters "
          f"(threshold={args.threshold}); top {len(summaries)} by frequency x severity:\n")
    for rank, s in enumerate(summaries, 1):
        print(f"#{rank}  [{s['rank_score']:>6}]  n={s['size']}  mean_sev={s['mean_severity']}")
        print(f"     theme: {s['suggested_name']}")
        print(f"     exemplar ({s['exemplar_id']}): {s['exemplar']!r}")
    print("\nnext: VALIDATE/rename these (axial coding is human-owned); "
          "file novel modes to the eval dataset.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
