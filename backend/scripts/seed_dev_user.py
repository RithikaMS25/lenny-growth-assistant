
import asyncio
import os
import secrets

from sqlalchemy import select

from app.database import AsyncSessionLocal, engine
from app.models import User
from pwdlib import PasswordHash


async def main():
    email = os.getenv("DEV_USER_EMAIL", "dev@lenny.local")
    password_hash = PasswordHash.recommended().hash(
        secrets.token_urlsafe(32)
    )

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if user is None:
                user = User(
                    email=email,
                    password_hash=password_hash,
                )
                session.add(user)
                await session.commit()
                print(f"Development user created: {email}")
            else:
                print(f"Development user already exists: {email}")

            print(f"User ID: {user.id}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
