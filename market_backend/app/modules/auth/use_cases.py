from datetime import datetime, timedelta, timezone

import bcrypt

from fastapi import HTTPException, status
from jose import jwt

from app.config import settings
from app.modules.auth.repos import UserRepo


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


class RegisterUser:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def execute(self, email: str, password: str) -> str:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        hashed = hash_password(password)
        user = await self.repo.create(email=email, hashed_password=hashed)
        return create_access_token(str(user.id), user.role)


class LoginUser:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def execute(self, email: str, password: str) -> str:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return create_access_token(str(user.id), user.role)
