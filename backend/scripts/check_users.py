
import asyncio

from sqlalchemy import func, select

from app.database import AsyncSessionLocal, engine
from app.models import User


async def main():
    try:
        async with AsyncSessionLocal() as session:
            count = await session.scalar(
                select(func.count()).select_from(User)
            )
            print(f"User count: {count}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
