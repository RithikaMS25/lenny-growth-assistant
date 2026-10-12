
from app.services.retrieval import extract_requested_speaker


def test_extracts_molly_graham():
    query = (
        "According to Molly Graham, "
        "what work should people avoid outsourcing to AI?"
    )
    assert extract_requested_speaker(query) == "Molly Graham"


def test_extracts_adam_mosseri():
    query = "According to Adam Mosseri, what is AI changing?"
    assert extract_requested_speaker(query) == "Adam Mosseri"


def test_returns_none_without_speaker_phrase():
    query = "What work should people avoid outsourcing to AI?"
    assert extract_requested_speaker(query) is None


def test_returns_none_for_empty_query():
    assert extract_requested_speaker("") is None
