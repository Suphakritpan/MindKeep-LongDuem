"""Local LLM client (Ollama) for summarization, with a deterministic fallback.

ADR-005: AI runs on a local model via Ollama. If the runtime is unavailable
(common in dev / first boot), summarize() degrades to a truncated extract so the
pipeline never blocks — never sends company data to an external API (ADR-004).
"""
import json
import urllib.error
import urllib.request

from app.core.config import settings

_FALLBACK_CHARS = 500
_MAX_PROMPT_CHARS = 6_000
_TIMEOUT_SECONDS = 60


class OllamaClient:
    def summarize(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        prompt = (
            "Summarize the following document in 3-5 concise sentences. "
            "Answer in the document's own language.\n\n" + text[:_MAX_PROMPT_CHARS]
        )
        try:
            return self._generate(prompt) or self._fallback(text)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError):
            return self._fallback(text)

    def _generate(self, prompt: str) -> str:
        body = json.dumps(
            {"model": settings.ollama_model, "prompt": prompt, "stream": False}
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{settings.ollama_base_url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return (payload.get("response") or "").strip()

    @staticmethod
    def _fallback(text: str) -> str:
        cleaned = " ".join(text.split())
        suffix = "…" if len(cleaned) > _FALLBACK_CHARS else ""
        return cleaned[:_FALLBACK_CHARS] + suffix
