"""Seed demo users for the hackathon demo."""

import asyncio
from app.database import init_db, async_session
from app.models import User, UserRole
from app.auth import hash_password


DEMO_USERS = [
    {"username": "analyst", "email": "analyst@loanverify.dev", "password": "demo123", "role": UserRole.ANALYST},
    {"username": "reviewer", "email": "reviewer@loanverify.dev", "password": "demo123", "role": UserRole.REVIEWER},
    {"username": "admin", "email": "admin@loanverify.dev", "password": "demo123", "role": UserRole.ADMIN},
]


async def seed():
    await init_db()
    async with async_session() as db:
        from sqlalchemy import select
        for u in DEMO_USERS:
            result = await db.execute(select(User).where(User.username == u["username"]))
            if result.scalar_one_or_none():
                continue
            user = User(
                username=u["username"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(user)
            print(f"  ✓ Created user: {u['username']} ({u['role'].value})")
        await db.commit()
    print("\nSeed complete! Demo accounts:")
    print("  analyst / demo123  (can upload & view)")
    print("  reviewer / demo123 (can resolve exceptions)")
    print("  admin / demo123    (full access)")


if __name__ == "__main__":
    asyncio.run(seed())
