#!/usr/bin/env python3
"""trigger_classifier.py — Tier-1 rule-based proxy for trigger_scenarios.

Parses trigger / NOT phrases from SKILL.md frontmatter and classifies prompts
against AI-system concepts (eval, safety, measurement, agent quality) vs classic
SaaS PM anti-triggers. No API keys — suitable for CI.

Exit 0 if every trigger_scenario in evals.json matches its should_trigger flag.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
DEFAULT_SKILL = os.path.join(ROOT, "SKILL.md")
DEFAULT_EVALS = os.path.join(HERE, "evals.json")

POSITIVE_PATTERNS: list[str | re.Pattern] = [
    r"\beval\b", r"\bevals\b", r"\brubric\b", r"\bscorer\b", r"\bjudge\b",
    r"\bllm\b", r"\brag\b", r"\bprompt regression\b", r"\bmodel bake",
    r"\bgroundedness\b", r"\bgrounded\b", r"\bgrounding\b",
    r"\bhallucinat", r"\bdrift\b", r"\bjailbreak", r"\bjailbroke",
    r"\bguardrail", r"\bred.?team", r"\bcanary\b", r"\brollback\b",
    r"\brefusal", r"\bpass@k\b", r"\bpass\^k\b", r"\brlhf\b",
    r"\breward model", r"\bflywheel\b", r"\bcontamination\b",
    r"\btrace\b.*\bfailure", r"\bfailure.?mode",
    r"\bevery number\b", r"\btraces to\b", r"\bcomes from a query\b",
    r"\bcomes from a tool\b", r"\bsystem prompt\b",
    r"\bcost.?per.?task\b", r"\binference cost\b", r"\binference economics\b",
    r"\bAT-\d+\b", r"\bEVL-\d+\b",
    (r"\b(agent|assistant|model|llm)\b.*"
     r"\b(hallucinat|jailbreak|eval|ground|refusal|quality|latency|cost|monitor|score)\b"),
    (r"\b(hallucinat|jailbreak|eval|ground|refusal|quality|latency|cost|monitor|score)\b.*"
     r"\b(agent|assistant|model|llm)\b"),
    (r"\b(cost|latency|quality)\b.*\b(dashboard|monitor)\b.*\b(agent|inference|model|llm)\b"),
    (r"\b(dashboard|monitor)\b.*\b(agent|inference|model|llm)\b.*\b(cost|latency|quality)\b"),
    r"\bwrite an eval\b", r"\bdebugging evals\b", r"\bcalibrate.*judge\b",
    r"\bmodel selection\b", r"\bmodel routing\b", r"\beval.?gated\b",
    r"\bonline quality\b", r"\bsafety/red", r"\bsafety gate\b",
]

ANTI_PATTERNS: list[str | re.Pattern] = [
    r"\bseat pricing\b", r"\bprice tiers?\b", r"\bpricing tiers?\b",
    r"\bsaas seats?\b", r"\bset the price\b",
    r"\bcustomer discovery interview\b", r"\bdiscovery interview\b",
    r"\bsignup funnel\b", r"\bfunnel drop", r"\bsignup drop",
    r"\bdashboard for signups?\b", r"\bsignups dashboard\b",
    r"\bsprint hygiene\b", r"\bmodel.?agnostic\b",
    r"\bproduct analytics\b(?!.*\b(agent|model|eval|llm)\b)",
    r"\bai coding agent\b",
    r"\buse an ai\b.*\b(refactor|ship|build)\b",
    r"\b(refactor|implement|rewrite)\b.*\b(backend|codebase|faster)\b",
    r"\bship ordinary software\b", r"\bbuild software faster\b",
    r"\baws.?s ai.?dlc\b",
]

_SKILL_TRIGGER_PHRASES: list[str] = []
_SKILL_ANTI_PHRASES: list[str] = []


def _read_skill_description(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        raise ValueError(f"No YAML frontmatter in {path}")
    block = m.group(1)
    dm = re.search(r"^description:\s*(?:>\-?|-)\s*\n((?:  .+\n?)+)", block, re.MULTILINE)
    if not dm:
        raise ValueError(f"No description in frontmatter of {path}")
    lines = [ln.strip() for ln in dm.group(1).splitlines()]
    return " ".join(lines)


def _split_phrase_list(blob: str) -> list[str]:
    out: list[str] = []
    for part in re.split(r",(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)", blob):
        p = part.strip().strip('"').strip("'").strip()
        if p and len(p) > 2:
            out.append(p.lower())
    return out


def parse_skill_triggers(skill_path: str) -> tuple[list[str], list[str]]:
    desc = _read_skill_description(skill_path)
    triggers: list[str] = []
    antis: list[str] = []

    trig_m = re.search(r"\bTriggers:\s*(.+?)(?:\.\s*Use even when|\.\s*NOT for|$)", desc, re.I)
    if trig_m:
        triggers = _split_phrase_list(trig_m.group(1))

    anti_m = re.search(r"\bNOT for\s+(.+?)(?:\.\s*$|$)", desc, re.I)
    if anti_m:
        antis = _split_phrase_list(anti_m.group(1))

    return triggers, antis


def load_skill_patterns(skill_path: str) -> None:
    global _SKILL_TRIGGER_PHRASES, _SKILL_ANTI_PHRASES
    _SKILL_TRIGGER_PHRASES, _SKILL_ANTI_PHRASES = parse_skill_triggers(skill_path)


def _matches_any(text: str, patterns: list[str | re.Pattern]) -> list[str]:
    hits: list[str] = []
    for pat in patterns:
        if isinstance(pat, re.Pattern):
            if pat.search(text):
                hits.append(pat.pattern)
        elif re.search(pat, text):
            hits.append(pat)
        elif pat in text:
            hits.append(pat)
    return hits


def _score_prompt(prompt: str) -> tuple[list[str], list[str]]:
    p = prompt.lower()
    pos = _matches_any(p, POSITIVE_PATTERNS)
    for phrase in _SKILL_TRIGGER_PHRASES:
        if phrase in p:
            pos.append(f"skill:{phrase}")
    anti = _matches_any(p, ANTI_PATTERNS)
    for phrase in _SKILL_ANTI_PHRASES:
        if phrase in p:
            anti.append(f"skill:{phrase}")
    for hint in ("seat pricing", "signup funnels", "sprint hygiene",
                 "ship ordinary software faster", "model-agnostic product analytics"):
        if hint in p:
            anti.append(f"skill:{hint}")
    return pos, anti


def should_trigger(prompt: str) -> bool:
    pos, anti = _score_prompt(prompt)
    if anti and not pos:
        return False
    if pos and not anti:
        return True
    if pos and anti:
        strong = any(
            re.search(s, prompt, re.I)
            for s in (
                r"\beval\b", r"\bhallucinat", r"\bjailbreak", r"\bground",
                r"\bevery number\b", r"\brefusal", r"\bred.?team",
                r"\b(cost|latency|quality).*\b(agent|model|inference)\b",
            )
        )
        return strong
    return False


def check_scenario(sc: dict) -> tuple[bool, list[str]]:
    predicted = should_trigger(sc["prompt"])
    expected = sc["should_trigger"]
    if predicted == expected:
        return True, []
    pos, anti = _score_prompt(sc["prompt"])
    fails = [f"predicted should_trigger={predicted}, expected {expected}"]
    if pos:
        fails.append(f"trigger hits: {pos[:5]}")
    if anti:
        fails.append(f"anti hits: {anti[:5]}")
    return False, fails


def verify_all(evals_path: str, skill_path: str) -> tuple[int, int, list[tuple[str, list[str]]]]:
    load_skill_patterns(skill_path)
    with open(evals_path, encoding="utf-8") as fh:
        scenarios = json.load(fh).get("trigger_scenarios", [])
    passed = failed = 0
    failures: list[tuple[str, list[str]]] = []
    for sc in scenarios:
        ok, errs = check_scenario(sc)
        if ok:
            passed += 1
        else:
            failed += 1
            failures.append((sc["id"], errs))
    return passed, failed, failures


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--evals", default=DEFAULT_EVALS)
    p.add_argument("--skill", default=DEFAULT_SKILL)
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    load_skill_patterns(args.skill)
    if args.verbose:
        print(f"Parsed {len(_SKILL_TRIGGER_PHRASES)} trigger + {len(_SKILL_ANTI_PHRASES)} anti phrases from SKILL.md")

    with open(args.evals, encoding="utf-8") as fh:
        scenarios = json.load(fh).get("trigger_scenarios", [])

    exit_code = 0
    for sc in scenarios:
        ok, errs = check_scenario(sc)
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {sc['id']}")
        for e in errs:
            print(f"        - {e}")
        if not ok:
            exit_code = 1

    passed = sum(1 for sc in scenarios if check_scenario(sc)[0])
    total = len(scenarios)
    print(f"\nTRIGGER classifier: {passed}/{total} passed.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
