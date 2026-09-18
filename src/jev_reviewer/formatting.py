from __future__ import annotations

from typing import Iterable

from .models import JevAnswer


def _pct(x: float) -> str:
    return f"{100*x:.0f}%"


def _bar(x: float, width: int = 10) -> str:
    n = max(0, min(width, round(x * width)))
    return "█" * n + "░" * (width - n)


def render_answers(title: str, answers: dict[str, JevAnswer]) -> str:
    lines = [title, ""]
    for qid, ans in answers.items():
        label = qid.replace("_", " ").title()
        lines.append(f"{label}: {ans.choice or 'n/a'}")
        for choice, prob in sorted(ans.probabilities.items(), key=lambda kv: -kv[1]):
            lines.append(f"  {choice:<18} {_bar(prob)} {_pct(prob)}")
        if ans.confidence is not None:
            lines.append(f"  confidence: {_pct(ans.confidence)}")
        lines.append("")
    return "\n".join(lines).strip()


def render_integrity(answers: dict[str, JevAnswer], local: dict) -> str:
    lines = ["WRITING INTEGRITY AUDIT", "", "JEV pattern judgments:"]
    lines.append(render_answers("", answers))
    style = local["style"]
    lines.extend([
        "",
        "Deterministic text signals:",
        f"  Words: {style['word_count']}",
        f"  Mean sentence length: {style['mean_sentence_words']} words",
        f"  Sentences >35 words: {style['sentences_over_35_words']}",
    ])
    for key, count in style["pattern_counts"].items():
        lines.append(f"  {key.replace('_', ' ')}: {count}")
    if style["repeated_sentence_starts"]:
        lines.append("  Repeated sentence starts:")
        for start, count in style["repeated_sentence_starts"].items():
            lines.append(f"    {start!r}: {count}x")

    prov = local["provenance"]
    lines.extend(["", "File provenance:"])
    for c in prov["classification"]:
        lines.append(f"  - {c}")
    hints = prov.get("details", {}).get("generator_hints") or []
    if hints:
        lines.append("  Generator/application hints: " + ", ".join(hints))
    lines.extend([
        "",
        "Interpretation: these are writing/provenance signals, not proof that AI wrote the document.",
    ])
    return "\n".join(lines)


def split_message(text: str, limit: int = 3800) -> Iterable[str]:
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = limit
        yield text[:cut]
        text = text[cut:].lstrip()
    if text:
        yield text
