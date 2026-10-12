
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.database import DATABASE_URL


@pytest.mark.asyncio
async def test_database_connection():
    test_engine = create_async_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )
    try:
        async with test_engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            assert result.scalar_one() == 1
    finally:
        await test_engine.dispose()


@pytest.mark.asyncio
async def test_pgvector_extension_available():
    test_engine = create_async_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )
    try:
        async with test_engine.connect() as connection:
            result = await connection.execute(
                text(
                    "SELECT extname FROM pg_extension "
                    "WHERE extname = 'vector'"
                )
            )
            assert result.scalar_one_or_none() == "vector"
    finally:
        await test_engine.dispose()
