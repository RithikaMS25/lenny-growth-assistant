
import pytest

from app.services.chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("   ") == []


def test_short_text_returns_one_chunk():
    chunks = chunk_text("Lenny interviews startup founders.")
    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].content == "Lenny interviews startup founders."


def test_chunks_overlap():
    words = [f"word{i}" for i in range(200)]
    chunks = chunk_text(" ".join(words), chunk_size=100, overlap=20)

    assert len(chunks) == 3
    assert chunks[0].content.split()[-20:] == chunks[1].content.split()[:20]
    assert chunks[1].content.split()[-20:] == chunks[2].content.split()[:20]


def test_invalid_chunk_size_is_rejected():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=0)


def test_invalid_overlap_is_rejected():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=10, overlap=10)
