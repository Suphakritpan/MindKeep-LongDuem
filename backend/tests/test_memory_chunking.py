"""Chunking tests (pure, no deps) — Batch F Work Memory."""
from app.modules.memory.chunking import chunk_text


def test_empty_text_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n ") == []


def test_short_text_kept_as_single_chunk():
    # Below the min-size threshold inside the loop, but real content is never
    # silently dropped — the whole text is returned as one chunk.
    assert chunk_text("ราคา มะพร้าว 12 บาท") == ["ราคา มะพร้าว 12 บาท"]


def test_long_text_splits_with_overlap():
    words = [f"w{i}" for i in range(40)]
    chunks = chunk_text(" ".join(words), chunk_size_tokens=10, overlap_tokens=2, min_tokens=1)

    assert len(chunks) > 1
    joined = " ".join(chunks)
    for w in words:  # nothing lost across the split
        assert w in joined
    # consecutive windows overlap: the last word of chunk 0 reappears in chunk 1
    assert chunks[0].split()[-1] in chunks[1].split()
