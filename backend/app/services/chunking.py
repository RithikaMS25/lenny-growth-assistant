
from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    index: int
    content: str


def chunk_text(
    text: str,
    chunk_size: int = 180,
    overlap: int = 30,
) -> list[TextChunk]:
    """Split text into word-based chunks with overlap."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    words = text.split()
    if not words:
        return []

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]
        if not chunk_words:
            break

        chunks.append(
            TextChunk(
                index=len(chunks),
                content=" ".join(chunk_words),
            )
        )

        if start + chunk_size >= len(words):
            break

    return chunks
