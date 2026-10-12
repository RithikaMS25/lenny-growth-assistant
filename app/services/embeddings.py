
from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it."""
    return SentenceTransformer(MODEL_NAME, device="cpu")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Convert text into normalized 384-dimensional embeddings."""
    if not texts:
        return []

    if any(not text.strip() for text in texts):
        raise ValueError("Texts must not be empty")

    model = get_embedding_model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    if vectors.shape[1] != EMBEDDING_DIMENSION:
        raise RuntimeError(
            f"Expected {EMBEDDING_DIMENSION} dimensions, "
            f"got {vectors.shape[1]}"
        )

    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    """Embed one search query."""
    if not query.strip():
        raise ValueError("Query must not be empty")

    return embed_texts([query])[0]
