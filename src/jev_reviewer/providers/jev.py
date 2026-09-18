from __future__ import annotations

import asyncio
import random
from typing import Any

import httpx

from ..models import JevAnswer


class JevError(RuntimeError):
    pass


class JevClient:
    def __init__(self, api_key: str, endpoint: str, model: str, timeout: float = 45.0):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model
        self.timeout = timeout

    async def evaluate(self, state: dict[str, Any], questions: dict[str, Any]) -> dict[str, JevAnswer]:
        payload = {"model": self.model, "state": state, "questions": questions}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        retryable = {408, 429, 500, 502, 503, 504, 529}
        last_error: Exception | None = None

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(4):
                try:
                    response = await client.post(self.endpoint, headers=headers, json=payload)
                    if response.status_code in retryable and attempt < 3:
                        delay = min(30.0, (2**attempt) + random.random())
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            try:
                                delay = min(30.0, float(retry_after))
                            except ValueError:
                                pass
                        await asyncio.sleep(delay)
                        continue
                    response.raise_for_status()
                    body = response.json()
                    return self._parse(body)
                except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
                    last_error = exc
                    status = getattr(getattr(exc, "response", None), "status_code", None)
                    if attempt >= 3 or (status is not None and status not in retryable):
                        break
                    await asyncio.sleep(min(30.0, (2**attempt) + random.random()))

        raise JevError(f"JEV request failed: {last_error}")

    @staticmethod
    def _parse(body: dict[str, Any]) -> dict[str, JevAnswer]:
        reserved = {"confidence", "probabilities", "usage", "model", "request_id", "id"}
        confidence_map = body.get("confidence") if isinstance(body.get("confidence"), dict) else {}
        probability_map = body.get("probabilities") if isinstance(body.get("probabilities"), dict) else {}

        flat_candidates = {k: v for k, v in body.items() if k not in reserved}
        if flat_candidates and (confidence_map or probability_map):
            parsed: dict[str, JevAnswer] = {}
            for qid, value in flat_candidates.items():
                probs = probability_map.get(qid, {})
                conf = confidence_map.get(qid)
                parsed[qid] = JevAnswer(
                    question_id=qid,
                    choice=str(value) if value is not None else None,
                    probabilities={str(k): float(v) for k, v in probs.items()} if isinstance(probs, dict) else {},
                    confidence=float(conf) if conf is not None else None,
                )
            if parsed:
                return parsed

        raw_answers = body.get("answers") or body.get("output") or body.get("result") or {}
        if isinstance(raw_answers, dict) and "answers" in raw_answers and isinstance(raw_answers["answers"], dict):
            raw_answers = raw_answers["answers"]
        if not isinstance(raw_answers, dict):
            raise JevError(f"Unexpected JEV response shape: {type(raw_answers).__name__}")

        parsed = {}
        for qid, raw in raw_answers.items():
            if not isinstance(raw, dict):
                continue
            probs = raw.get("probabilities") or raw.get("probs") or {}
            if isinstance(probs, list):
                probs = {str(i): float(v) for i, v in enumerate(probs)}
            parsed[qid] = JevAnswer(
                question_id=qid,
                choice=str(raw.get("choice")) if raw.get("choice") is not None else None,
                probabilities={str(k): float(v) for k, v in probs.items()} if isinstance(probs, dict) else {},
                confidence=float(raw["confidence"]) if raw.get("confidence") is not None else None,
            )
        if not parsed:
            raise JevError(f"No answers found in JEV response. Top-level keys: {list(body.keys())}")
        return parsed
