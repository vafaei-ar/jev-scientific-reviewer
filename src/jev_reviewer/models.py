from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Document:
    name: str
    path: Path
    text: str
    kind: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class JevAnswer:
    question_id: str
    choice: str | None
    probabilities: dict[str, float]
    confidence: float | None

    @property
    def top_probability(self) -> float | None:
        if not self.probabilities:
            return None
        return max(self.probabilities.values())
