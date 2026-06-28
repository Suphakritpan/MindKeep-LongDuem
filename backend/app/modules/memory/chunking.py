"""Word-boundary chunking for Work Memory.

Ported from the LongRian ingestion pipeline (ADR-001 — proven logic re-implemented,
not copied wholesale). ~4 chars ≈ 1 token; chunks overlap so context is preserved
across splits. Deviation from the original: non-empty text always yields at least
one chunk, so short approved notes are never silently dropped.
"""

CHUNK_SIZE_TOKENS = 400
CHUNK_OVERLAP_TOKENS = 40
CHUNK_MIN_TOKENS = 20


def chunk_text(
    text: str,
    *,
    chunk_size_tokens: int = CHUNK_SIZE_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS,
    min_tokens: int = CHUNK_MIN_TOKENS,
) -> list[str]:
    char_limit = chunk_size_tokens * 4
    char_min = min_tokens * 4

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    i = 0
    while i < len(words):
        j = i
        chars = 0
        while j < len(words) and chars < char_limit:
            chars += len(words[j]) + 1
            j += 1
        chunk = " ".join(words[i:j])
        if len(chunk) >= char_min:
            chunks.append(chunk)
        if j >= len(words):
            break
        i += max(1, j - i - overlap_tokens)

    # Never drop real content: if every slice fell below min_size, keep the whole text.
    if not chunks:
        return [" ".join(words)]
    return chunks
