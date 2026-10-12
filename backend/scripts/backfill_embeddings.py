
import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal, engine
from app.models import SourceChunk
from app.services.embeddings import embed_texts


async def main() -> None:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.scalars(
                select(SourceChunk)
                .where(SourceChunk.embedding.is_(None))
                .order_by(SourceChunk.source_id, SourceChunk.chunk_index)
            )
            chunks = list(result.all())

            if not chunks:
                print("No chunks need embeddings.")
                return

            batch_size = 32
            updated = 0

            for start in range(0, len(chunks), batch_size):
                batch = chunks[start : start + batch_size]
                vectors = embed_texts([chunk.content for chunk in batch])

                for chunk, vector in zip(batch, vectors):
                    chunk.embedding = vector

                await session.commit()
                updated += len(batch)
                print(f"Embedded {updated}/{len(chunks)} chunks")

            print(f"Backfill complete: {updated} chunks updated.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
