import asyncio
import argparse
import sys

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

sys.path.insert(0, ".")

from app.config import settings
from app.modules.auth.models import User
import app.modules.products.models  # noqa: F401
import app.modules.cart.models      # noqa: F401
import app.modules.orders.models    # noqa: F401


async def create_admin(email: str, password: str):
    engine = create_async_engine(settings.database_url, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"User with email '{email}' already exists (role: {existing.role}).")
            await engine.dispose()
            return

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User(email=email, hashed_password=hashed, role="admin")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"Admin created: {user.email} (id: {user.id})")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("email", help="Admin email")
    parser.add_argument("password", help="Admin password")
    args = parser.parse_args()

    asyncio.run(create_admin(args.email, args.password))
