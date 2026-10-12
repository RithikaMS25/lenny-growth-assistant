
import asyncio
import json
import logging
import argparse
import re
from datetime import date
from pathlib import Path

from sqlalchemy import select

from app.database import AsyncSessionLocal, engine
from app.models import Source, SourceChunk
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORPUS_ROOT = (
    PROJECT_ROOT / "data" / "lenny-extracted"
    / "lennys-newsletterpodcastdata-main"
)
INDEX_PATH = CORPUS_ROOT / "index.json"


async def ingest_entry(session, entry, source_type, refresh=False):
    title = entry.get("title", "").strip()
    relative_path = entry.get("filename", "")
    source_url = (entry.get("post_url") or "").strip() or None

    if not title or not relative_path:
        return "invalid: missing title or filename"

    # Resolve paths and reject anything outside the corpus directory.
    file_path = (CORPUS_ROOT / relative_path).resolve()
    if not file_path.is_relative_to(CORPUS_ROOT.resolve()):
        logger.warning("Rejected unsafe path for %s", title)
        return "invalid: unsafe corpus path"

    if not file_path.is_file():
        logger.warning("Missing transcript file: %s", relative_path)
        return "invalid: source file missing"

    existing_source = await session.scalar(select(Source).where(Source.url == source_url)) if source_url else await session.scalar(select(Source).where(Source.url.is_(None), Source.title == title, Source.source_type == source_type))
    existing = existing_source.id if existing_source else None
    if existing:
        if not refresh:
            logger.info("Skipping existing source: %s", title)
            return "skipped"
        await session.delete(existing_source)
        await session.flush()

    content = file_path.read_text(encoding="utf-8-sig", errors="replace").strip()
    # Remove an optional YAML front matter block while preserving the Markdown body.
    content = re.sub(r"\A---\s*\r?\n.*?\r?\n---\s*\r?\n", "", content, count=1, flags=re.DOTALL).strip()
    if not content:
        logger.warning("Empty source: %s", title)
        return "invalid: source file is empty"

    chunks = chunk_text(content, chunk_size=180, overlap=30)
    if not chunks:
        return "invalid: no usable text"

    # Generate embeddings before inserting the source.
    vectors = embed_texts([chunk.content for chunk in chunks])

    source = Source(
        source_type=source_type,
        title=title,
        url=source_url,
        published_date=(
            date.fromisoformat(entry["date"])
            if entry.get("date")
            else None
        ),
        description=entry.get("description"),
    )
    session.add(source)
    await session.flush()

    for chunk, vector in zip(chunks, vectors):
        session.add(
            SourceChunk(
                source_id=source.id,
                chunk_index=chunk.index,
                content=chunk.content,
                embedding=vector.tolist()
                if hasattr(vector, "tolist")
                else list(vector),
            )
        )

    await session.commit()
    logger.info("Ingested %s: %d chunks", title, len(chunks))
    return "ingested"


async def main():
    parser = argparse.ArgumentParser(description="Ingest the local Lenny corpus")
    parser.add_argument("--refresh", action="store_true", help="Re-index sources already present")
    args = parser.parse_args()
    if not INDEX_PATH.is_file():
        raise FileNotFoundError(
            f"Corpus index not found: {INDEX_PATH}"
        )

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    entries = [
        (entry, "podcast")
        for entry in index.get("podcasts", [])
    ] + [
        (entry, "newsletter")
        for entry in index.get("newsletters", [])
    ]

    counts = {"ingested": 0, "skipped": 0, "invalid": 0, "failed": 0}
    reasons = {}

    try:
        async with AsyncSessionLocal() as session:
            for entry, source_type in entries:
                try:
                    result = await ingest_entry(
                        session, entry, source_type, refresh=args.refresh
                    )
                    category, _, reason = result.partition(": ")
                    counts[category] += 1
                    if reason:
                        reasons[reason] = reasons.get(reason, 0) + 1
                except Exception as exc:
                    await session.rollback()
                    counts["failed"] += 1
                    reason = type(exc).__name__
                    reasons[reason] = reasons.get(reason, 0) + 1
                    logger.error("Failed to ingest source title=%r reason=%s", entry.get("title", "unknown source"), reason)

        logger.info("Ingestion summary: %s; reasons: %s", counts, reasons)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
