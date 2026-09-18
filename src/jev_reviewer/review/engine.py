from __future__ import annotations

from typing import Any

from ..models import Document, JevAnswer
from ..providers.jev import JevClient
from .integrity import provenance_signals, style_signals
from .rubrics import INTEGRITY_RUBRIC, PAPER_RUBRIC, PROPOSAL_RUBRIC, build_choice_questions


class ReviewEngine:
    def __init__(self, jev: JevClient, max_chars: int = 90_000):
        self.jev = jev
        self.max_chars = max_chars

    def _state(self, document: Document, mode: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        text = document.text[: self.max_chars]
        state: dict[str, Any] = {
            "task": mode,
            "document_name": document.name,
            "document_type": document.kind,
            "document_text": text,
            "truncated": len(document.text) > len(text),
            "instructions": (
                "Judge only evidence present in the document. Separate writing quality from scientific validity. "
                "Do not infer facts that are absent. Use the full probability distribution when uncertain."
            ),
        }
        if extra:
            state.update(extra)
        return state

    async def paper(self, document: Document) -> dict[str, JevAnswer]:
        return await self.jev.evaluate(self._state(document, "scientific manuscript review"), build_choice_questions(PAPER_RUBRIC))

    async def proposal(self, document: Document) -> dict[str, JevAnswer]:
        return await self.jev.evaluate(self._state(document, "research proposal review"), build_choice_questions(PROPOSAL_RUBRIC))

    async def integrity(self, document: Document) -> tuple[dict[str, JevAnswer], dict[str, Any]]:
        local = {
            "style": style_signals(document.text),
            "provenance": provenance_signals(document.path),
        }
        answers = await self.jev.evaluate(
            self._state(document, "scientific writing integrity audit", extra={"local_style_signals": local["style"]}),
            build_choice_questions(INTEGRITY_RUBRIC),
        )
        return answers, local

    async def check_claim(self, document: Document, claim: str) -> dict[str, JevAnswer]:
        questions = {
            "claim_support": {
                "type": "choice",
                "instructions": f"Does the supplied document support this claim as written? Claim: {claim}",
                "criteria": {
                    "supported": "The document directly supports the claim with adequate evidence.",
                    "partly_supported": "The document supports part of the claim, but the wording overstates or omits important qualification.",
                    "not_supported": "The document does not support the claim as written.",
                    "unclear": "The document is insufficient or ambiguous for this judgment.",
                },
            }
        }
        return await self.jev.evaluate(self._state(document, "claim verification"), questions)
