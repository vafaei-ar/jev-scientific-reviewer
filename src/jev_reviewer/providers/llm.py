from __future__ import annotations

import httpx


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def ask(self, document_text: str, question: str) -> str:
        prompt = (
            "You are reviewing a scientific manuscript or research proposal. Answer only from the supplied document. "
            "Be precise. Distinguish document facts from your interpretation. If evidence is missing, say so.\n\n"
            f"DOCUMENT:\n{document_text}\n\nQUESTION:\n{question}"
        )
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"]
