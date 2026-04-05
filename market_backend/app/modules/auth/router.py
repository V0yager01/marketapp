from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.modules.auth.repos import UserRepo
from app.modules.auth.use_cases import LoginUser, RegisterUser

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepo(db)
    token = await RegisterUser(repo).execute(body.email, body.password)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepo(db)
    token = await LoginUser(repo).execute(body.email, body.password)
    return TokenResponse(access_token=token)
