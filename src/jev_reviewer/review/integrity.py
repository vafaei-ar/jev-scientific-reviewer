from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from ..document import ooxml_generator_hints


PATTERNS = {
    "contrastive_negation": re.compile(r"\bnot (?:only|just|merely)\b.{0,80}\bbut\b", re.I | re.S),
    "generic_significance": re.compile(r"\b(?:underscor(?:e|es|ing)|highlight(?:s|ing)|pivotal|transformative|groundbreaking|crucial)\b", re.I),
    "roadmap_language": re.compile(r"\b(?:in this (?:paper|study|section)|the remainder of this|we first|we next|we then|finally, we)\b", re.I),
    "generic_gap": re.compile(r"\b(?:there remains a critical need|little is known|has garnered increasing attention|in recent years)\b", re.I),
}


def style_signals(text: str) -> dict[str, Any]:
    words = re.findall(r"\b\w+\b", text)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    pattern_counts = {name: len(rx.findall(text)) for name, rx in PATTERNS.items()}
    sentence_lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]
    repeated_starts = Counter(" ".join(s.lower().split()[:3]) for s in sentences if len(s.split()) >= 3)
    repeated = {k: v for k, v in repeated_starts.items() if v >= 3}
    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "mean_sentence_words": round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0,
        "sentences_over_35_words": sum(1 for n in sentence_lengths if n > 35),
        "pattern_counts": pattern_counts,
        "repeated_sentence_starts": dict(sorted(repeated.items(), key=lambda kv: -kv[1])[:8]),
    }


def provenance_signals(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"classification": [], "details": {}}
    suffix = path.suffix.lower()
    if suffix == ".docx":
        hints = ooxml_generator_hints(path)
        out["details"]["generator_hints"] = hints
        if any(x in hints for x in ("python-docx", "libreoffice", "pandoc")):
            out["classification"].append("programmatic-generation-indicator")
        if "microsoft word" in hints or "microsoft office" in hints:
            out["classification"].append("normal-office-provenance")
    elif suffix == ".pdf":
        reader = PdfReader(str(path))
        meta = {str(k): str(v) for k, v in dict(reader.metadata or {}).items()}
        out["details"]["pdf_metadata"] = meta
        joined = " ".join(meta.values()).lower()
        generators = [x for x in ("reportlab", "libreoffice", "pandoc", "latex", "microsoft") if x in joined]
        if generators:
            out["details"]["generator_hints"] = generators
        if any(x in generators for x in ("reportlab", "pandoc")):
            out["classification"].append("programmatic-generation-indicator")
        elif generators:
            out["classification"].append("normal-or-ambiguous-provenance")
    else:
        out["classification"].append("provenance-not-applicable")
    if not out["classification"]:
        out["classification"].append("no-obvious-provenance-signal")
    return out
