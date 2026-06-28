#!/usr/bin/env python3
"""contamination_check.py — detect train/eval overlap and near-duplicates (AT-47).

A contaminated eval flatters you into shipping a worse model. Exact-match checks miss
near-dupes and template leakage, so this runs three complementary channels:
  - exact     overlap on normalized text (whitespace/case-folded)          [HARD gate]
  - near-dup  character k-shingle Jaccard >= --threshold (paraphrase/typo)  [HARD gate]
  - template  TOKEN Jaccard >= --token-threshold — "capital of {France|Spain}"  [WARN]

The template channel is lexical and cannot distinguish a real template leak ("capital of
{France|Spain}") from two genuinely distinct short questions that share function words
("reset my {password|username}", token-Jaccard ~0.71). So by DEFAULT a template-ONLY hit
is a non-blocking WARNING (reported for human review, does not fail the gate); pass
--strict-template to make template hits block too. exact and near-dup are real leakage and
always block. NOTE: lexical proxy; for the embedding near-dup step AT-47 also specifies,
add a vector pass over these candidates (out of scope here — stdlib only). Nothing is fabricated.

Inputs: plain text (one item per line) or CSV with --text-col.
  python contamination_check.py --train train.txt --eval eval.txt
  python contamination_check.py --train t.csv --eval e.csv --text-col prompt --threshold 0.8
  python contamination_check.py --train train.txt --eval eval.txt --token-threshold 0.6 --json
  python contamination_check.py --train t.txt --eval e.txt --strict-template   # template also blocks

Exit code: 2 if a HARD finding (exact/near-dup, or template under --strict-template),
else 0. A clean set or template-only warnings exit 0.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402


def _load_items(path: str, text_col: str | None) -> list:
    if path.lower().endswith(".csv") or text_col:
        rows = _common.load_csv(path)
        if not rows:
            return []
        col = text_col
        if col is None:
            col = list(rows[0].keys())[0]
        if col not in rows[0]:
            raise SystemExit(f"column {col!r} not in {path}; columns={list(rows[0].keys())}")
        items = [(i, (r.get(col) or "").strip()) for i, r in enumerate(rows)]
    else:
        with open(path, encoding="utf-8") as fh:
            items = [(i, line.strip()) for i, line in enumerate(fh)]
    return [(i, t) for (i, t) in items if t]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--train", required=True, help="training items (txt one-per-line or csv)")
    p.add_argument("--eval", dest="eval_path", required=True, help="eval items (txt or csv)")
    p.add_argument("--text-col", help="column name if inputs are CSV")
    p.add_argument("--threshold", type=float, default=0.8, help="char-shingle Jaccard near-dup threshold (default 0.8)")
    p.add_argument("--token-threshold", type=float, default=0.6, help="token Jaccard template-leak threshold (default 0.6)")
    p.add_argument("--ngram", type=int, default=5, help="char shingle size (default 5)")
    p.add_argument("--strict-template", action="store_true",
                   help="make template (token-Jaccard) hits also block (exit 2); default = warn only")
    p.add_argument("--show", type=int, default=20, help="max contaminated rows to print")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    train = _load_items(args.train, args.text_col)
    ev = _load_items(args.eval_path, args.text_col)
    if not train or not ev:
        raise SystemExit("train and eval must both be non-empty")

    # exact index
    train_norm = {}
    for idx, txt in train:
        train_norm.setdefault(_normalize(txt), idx)

    # token blocking: content-token -> list of train indices (cuts pairwise cost)
    train_shingles, train_toks, token_to_train = {}, {}, {}
    for idx, txt in train:
        train_shingles[idx] = _common.char_shingles(txt, args.ngram)
        train_toks[idx] = set(_common.tokenize(txt, drop_stop=False))  # incl. stopwords for templates
        for tok in set(_common.tokenize(txt)):
            token_to_train.setdefault(tok, []).append(idx)

    findings = []
    for e_idx, e_txt in ev:
        norm = _normalize(e_txt)
        if norm in train_norm:
            findings.append({"eval_idx": e_idx, "eval_text": e_txt, "kind": "exact",
                             "similarity": 1.0, "train_idx": train_norm[norm]})
            continue
        e_sh = _common.char_shingles(e_txt, args.ngram)
        e_tok = set(_common.tokenize(e_txt, drop_stop=False))
        cands = set()
        for tok in set(_common.tokenize(e_txt)):
            cands.update(token_to_train.get(tok, ()))
        best_char, best_tok, best_idx, best_kind = 0.0, 0.0, None, None
        for t_idx in cands:
            cs = _common.jaccard(e_sh, train_shingles[t_idx])
            ts = _common.jaccard(e_tok, train_toks[t_idx])
            if cs >= args.threshold and cs > best_char:
                best_char, best_idx, best_kind = cs, t_idx, "near-dup"
            elif ts >= args.token_threshold and ts > best_tok and best_kind != "near-dup":
                best_tok, best_idx, best_kind = ts, t_idx, "template"
        if best_kind:
            sim = best_char if best_kind == "near-dup" else best_tok
            findings.append({"eval_idx": e_idx, "eval_text": e_txt, "kind": best_kind,
                             "similarity": round(sim, 4), "train_idx": best_idx})

    # exact/near-dup are real leakage (HARD). template is lexical and noisy on short text,
    # so it WARNS by default and only blocks under --strict-template (M-4).
    hard = [f for f in findings if f["kind"] in ("exact", "near-dup")]
    warn = [f for f in findings if f["kind"] == "template"]
    blocked = bool(hard) or (bool(warn) and args.strict_template)
    rate = len(findings) / len(ev)
    result = {
        "n_train": len(train), "n_eval": len(ev),
        "contaminated": len(findings), "hard": len(hard), "template_warn": len(warn),
        "contamination_rate": round(rate, 4), "blocked": blocked,
        "strict_template": args.strict_template,
        "threshold": args.threshold, "token_threshold": args.token_threshold, "ngram": args.ngram,
        "quarantine_eval_idx": sorted(f["eval_idx"] for f in (hard if not args.strict_template else findings)),
    }

    if args.json:
        result["findings"] = findings[: args.show]
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"train={len(train)}  eval={len(ev)}  char>={args.threshold}  token>={args.token_threshold}  ngram={args.ngram}")
        print(f"hard (exact/near-dup): {len(hard)}   template-warn: {len(warn)}   "
              f"total: {len(findings)} / {len(ev)} ({rate*100:.2f}%)")
        for f in [x for x in findings if x["kind"] in ("exact", "near-dup")][: args.show]:
            preview = f["eval_text"][:80].replace("\n", " ")
            print(f"  [BLOCK] eval#{f['eval_idx']} [{f['kind']} sim={f['similarity']}] ~ train#{f['train_idx']}: {preview!r}")
        for f in warn[: args.show]:
            preview = f["eval_text"][:80].replace("\n", " ")
            tag = "BLOCK" if args.strict_template else "WARN"
            print(f"  [{tag}] eval#{f['eval_idx']} [template sim={f['similarity']}] ~ train#{f['train_idx']}: {preview!r}")
        if blocked:
            print(f"\nNO-GO: quarantine eval rows {result['quarantine_eval_idx'][:50]}"
                  + (" ..." if len(result['quarantine_eval_idx']) > 50 else ""))
            print("clean separation is non-negotiable; re-split before trusting any score.")
        elif warn:
            print("\nREVIEW (exit 0): template-only matches are advisory — a human should confirm "
                  "whether these are real template leaks or just distinct short items sharing words. "
                  "Use --strict-template to block on them.")
        else:
            print("\nCLEAN: no exact or near-duplicate overlap above threshold.")

    return 2 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
