"""Shared helpers for the pm-for-aidlc scripts (stdlib-only).

Provides:
  - research_dir / csv path resolution (walks up the tree to find Research/)
  - load_csv: csv -> list[dict]
  - tokenize / shingles: light text utilities used by the text scripts

No third-party dependencies. Python 3.8+.
"""
from __future__ import annotations

import csv
import os
import re
import sys
from typing import Dict, List, Optional

class DataNotFound(SystemExit):
    """Raised when a required CSV cannot be resolved. Subclasses SystemExit so an
    uncaught instance prints its message and exits cleanly (no traceback), while callers
    that legitimately tolerate missing data can still catch it explicitly."""


# Canonical source CSVs. The skill vendors frozen copies under data/ so it is
# self-contained (portable); it falls back to Research/ when present (fresher).
AIDLC_CSV_NAME = "aidlc_microtasks.csv"
CLASSIC_CSV_NAME = "pm_microtask_database.csv"
USECASE_CSV_NAME = "aidlc-usecases.csv"
# Generated 6-axis catalog (incl. blast); lives only in data/ (build_axes.py emits it).
AXES_BUNDLE_NAME = "aidlc_axes.csv"


def skill_root() -> str:
    """The pm-for-aidlc/ directory (parent of scripts/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bundled_path(name: str) -> str:
    """Path to a vendored file under the skill's data/ directory."""
    return os.path.join(skill_root(), "data", name)


def _candidate_starts(start: Optional[str]) -> List[str]:
    starts = []
    if start:
        starts.append(os.path.abspath(start))
    # the directory this file lives in (scripts/)
    starts.append(os.path.dirname(os.path.abspath(__file__)))
    # current working directory
    starts.append(os.getcwd())
    return starts


def find_research_dir(start: Optional[str] = None) -> Optional[str]:
    """Walk upward from plausible roots to find a dir containing Research/<aidlc csv>.

    Returns the absolute path to the Research/ directory, or None if not found.
    """
    seen = set()
    for base in _candidate_starts(start):
        cur = base
        while cur and cur not in seen:
            seen.add(cur)
            candidate = os.path.join(cur, "Research", AIDLC_CSV_NAME)
            if os.path.isfile(candidate):
                return os.path.join(cur, "Research")
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
    return None


def resolve_csv(explicit: Optional[str], default_name: str) -> str:
    """Resolve a CSV path: --csv override → bundled data/ → Research/ fallback.

    Preferring the vendored data/ copy makes the skill portable (it no longer
    FileNotFound-errors when Research/ is not an ancestor dir).
    """
    if explicit:
        if not os.path.isfile(explicit):
            raise DataNotFound(f"CSV not found at the path you passed: {explicit}")
        return explicit
    bundled = bundled_path(default_name)
    if os.path.isfile(bundled):
        return bundled
    research = find_research_dir()
    if research is not None:
        path = os.path.join(research, default_name)
        if os.path.isfile(path):
            return path
    raise DataNotFound(
        f"Could not find {default_name} in the bundled data/ directory or a Research/ "
        f"ancestor. The skill ships its data under data/; if you copied scripts/ alone, "
        f"copy data/ too, or pass an explicit path (e.g. --csv / --aidlc-csv)."
    )


def load_csv(path: str) -> List[Dict[str, str]]:
    """Load a CSV into a list of dict rows (utf-8, handles quoted multiline fields)."""
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_axes_bundle() -> Dict[str, Dict[str, str]]:
    """Load the generated 6-axis catalog (data/aidlc_axes.csv) keyed by upper-case id.

    Returns {} if the bundle has not been generated yet (callers fall back to the
    5-axis Research CSV, leaving blast unknown).
    """
    path = bundled_path(AXES_BUNDLE_NAME)
    if not os.path.isfile(path):
        return {}
    return {(r.get("id") or "").strip().upper(): r for r in load_csv(path)}


_WORD_RE = re.compile(r"[a-z0-9]+")

# Small stoplist so keyword scoring/clustering focuses on signal words.
STOPWORDS = frozenset(
    """a an the of to and or for in on with without into from by as is are be this that
    it its at vs your you our we their how what when which who whom run build write make
    set design new use using used into per not no""".split()
)


def tokenize(text: str, drop_stop: bool = True) -> List[str]:
    """Lowercase word tokens; optionally drop common stopwords."""
    toks = _WORD_RE.findall((text or "").lower())
    if drop_stop:
        toks = [t for t in toks if t not in STOPWORDS and len(t) > 1]
    return toks


def char_shingles(text: str, k: int = 5) -> set:
    """Character k-shingles of normalized text (for near-dup / Jaccard)."""
    norm = re.sub(r"\s+", " ", (text or "").lower().strip())
    if len(norm) <= k:
        return {norm} if norm else set()
    return {norm[i : i + k] for i in range(len(norm) - k + 1)}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def eprint(*args, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)
