"""EmbeddingClient tests — parses Ollama /api/embed, no network (Batch F)."""
import json

import pytest

from app.modules.ai.embeddings import EmbeddingClient


class _FakeResp:
    def __init__(self, payload: dict) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResp":
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def test_embed_batch_parses_vectors(monkeypatch):
    captured: dict = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _FakeResp({"embeddings": [[0.1, 0.2], [0.3, 0.4]]})

    monkeypatch.setattr("app.modules.ai.embeddings.urllib.request.urlopen", fake_urlopen)

    out = EmbeddingClient(model="test-embed").embed_batch(["a", "b"])

    assert out == [[0.1, 0.2], [0.3, 0.4]]
    assert captured["url"].endswith("/api/embed")
    assert captured["body"] == {"model": "test-embed", "input": ["a", "b"]}


def test_embed_empty_returns_empty():
    assert EmbeddingClient().embed_batch([]) == []


def test_embed_batch_raises_on_count_mismatch(monkeypatch):
    def fake_urlopen(req, timeout=None):
        return _FakeResp({"embeddings": [[0.1]]})  # one vector for two inputs

    monkeypatch.setattr("app.modules.ai.embeddings.urllib.request.urlopen", fake_urlopen)

    with pytest.raises(ValueError):
        EmbeddingClient().embed_batch(["a", "b"])
