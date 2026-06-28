"""Local embedding client (Ollama) for Work Memory vectors.

Mirrors OllamaClient (urllib, local-first — ADR-004/005) but for embeddings.
Unlike summarization there is no deterministic fallback for a vector: if the
model is unavailable the embed job raises and the worker retries it later
(ADR-012), rather than storing a meaningless zero vector.
"""
import json
import urllib.request

from app.core.config import settings

_TIMEOUT_SECONDS = 60


class EmbeddingClient:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.embedding_model

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        body = json.dumps({"model": self.model, "input": texts}).encode("utf-8")
        req = urllib.request.Request(
            f"{settings.ollama_base_url}/api/embed",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        embeddings = payload.get("embeddings")
        if not embeddings or len(embeddings) != len(texts):
            raise ValueError("embedding service returned no/mismatched vectors")
        return embeddings
